"""
scarce_core.py - shared engine of the SCARCE criticality assessment
====================================================================

SCARCE is an approach for assessing critical resource use at a country level.
It rates how *critical* a raw material is for a country by combining:

    SUPPLY RISK                                          how likely is it that supply gets disrupted?
    VULNERABILITY                                        how badly would the country be hurt if it were?
    COMPLIANCE WITH SOCIAL STANDARDS                     hot-spots in the sourcing countries
    COMPLIANCE WITH ENVIRONMENTAL STANDARDS              hot-spots in the sourcing countries

The entry scripts in this folder only choose the COUNTRY and the sources:

    1. mode="import"   sourcing mix = the country's import mix (who really supplies it)
                    -> SCARCE_Japan.py, SCARCE_Germany.py
                    
    2. mode="global"   sourcing mix = world production shares (who produces globally)
                    -> SCARCE_Japan_global.py, SCARCE_Germany_global.py

All of the loading, indicator calculations, scaling, exports, and plotting are located here.

Pipeline (see ''run_assessment'' at the bottom)
-----------------------------------------------
    1. load_inputs()                        read Comtrade / production / reserves / indicator files
    2. build_material_data()                derive the sourcing mix of every material
    3. compute_raw_indicators()             one number per material per indicator
    4. scale_*()                            express indicators relative to targets, then min-max to 0..1
    5. export + plots                       CSV tables, stacked-bar charts and the criticality matrix
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# =============================================================================
# 1. STATIC DEFINITIONS
# =============================================================================

#: The 35 materials of the assessment. Spelling must match the sheet names in the
#: production / reserves workbooks and the "Commodity" column of the other files.
MATERIALS = [
    'Aluminium', 'Antimony', 'Bismuth', 'Cadmium', 'Chromium', 'Coal', 'Cobalt',
    'Copper', 'Crude oils', 'Gold', 'Graphite', 'Indium', 'Iron', 'Lead',
    'Lignite', 'Lithium', 'Magnesium', 'Manganese', 'Molybdenum', 'Natural gas',
    'Nickel', 'Niobium', 'Phosphorus', 'Platinum', 'Rare earths', 'Selenium',
    'Silver', 'Strontium', 'Tantalum', 'Titanium', 'Tungsten', 'Uranium',
    'Vanadium', 'Zinc', 'Zirconium',
]

MINING_CAPACITY = 'Mining capacity'

#: The ten supply-risk indicators in methodology order.
SUPPLY_RISK_INDICATORS = [
    'Concentration of production',
    'Concentration of reserves',
    'Feasibility of exploration projects',
    'Political stability',
    MINING_CAPACITY,
    'Trade barriers',
    'Demand growth',
    'Price fluctuation',
    'Primary material use',
    'Occurrence of co-production',
]

VULNERABILITY_INDICATORS = [
    'Economic importance', 'Domestically required demand', 'Share of global production',
    'Dependency on imports', 'Substitutability', 'Future technologies',
]
SOCIAL_INDICATORS = ['Small scale mining', 'Geopolitical risk', 'Human right abuse']
ENVIRONMENTAL_INDICATORS = ['Water scarcity', 'Climate change', 'Sensitivity of local biodiversity']

#: Raw supply-risk values that are computed in "percent x percent" or "percent x score"
#: units are divided by these factors so that they land in a 0-1 (or 0-100) range
#: comparable with the targets in the "Categories and targets" sheet.
SUPPLY_RISK_UNIT_RESCALING = {
    'Concentration of reserves': 10_000,       # HHI of percent shares (max 100^2) -> 0..1
    'Concentration of production': 10_000,
    'Feasibility of exploration projects': 100,  # percent x score -> score
    'Political stability': 100,
    'Trade barriers': 100,
}

#: Policy Perception Index: the "100 - PPI" gap is taken relative to this maximum.
PPI_REFERENCE_MAX = 99.07

#: After the distance-to-target step, scores below this are treated as "no risk".
#: (score = (value/target)^2, so 0.8 is roughly "value below ~90 % of the target").
DISTANCE_TO_TARGET_FLOOR = 0.8

#: Built-in JAPAN data: share (%) of each material's use by Japanese manufacturing sector.
#: Source: original SCARCE_Japan.py. Sector names must exist in the "Value added" sheet of
#: Indicators.xlsx. A sector may be listed twice (e.g. Antimony) and both entries count.
#: Other countries supply this as a CSV instead (Settings.economic_importance_file).
JAPAN_ECONOMIC_IMPORTANCE_SECTORS = {
    'Aluminium': [('Beverages, tobacco and feed', 11), ('Electrical machinery, equipment and supplies', 16), ('Transportation equipment', 43), ('Production machinery', 2)],
    'Antimony': [('Chemical and allied products', 40), ('Electronic parts, devices and electronic circuits', 32), ('Fabricated metal products', 14), ('Chemical and allied products', 10), ('Non-ferrous metals and products', 4)],
    'Bismuth': [('Chemical and allied products', 62), ('Iron and steel', 10), ('Non-ferrous metals and products', 28)],
    'Cadmium': [('Electrical machinery, equipment and supplies', 99), ('Chemical and allied products', 1)],
    'Chromium': [('Fabricated metal products', 25), ('Business oriented machinery', 25), ('Electronic parts, devices and electronic circuits', 5)],
    'Coal': [('Petroleum and coal products', 100)],
    'Cobalt': [('Electrical machinery, equipment and supplies', 80), ('Iron and steel', 4), ('Ceramic, stone and clay products', 5), ('Rubber products', 4)],
    'Copper': [('Electrical machinery, equipment and supplies', 35), ('Information and communication electronics equipment', 5), ('Transportation equipment', 10)],
    'Crude oils': [('Textile mill products', 15), ('Chemical and allied products', 11), ('Petroleum and coal products', 63)],
    'Gold': [('Electronic parts, devices and electronic circuits', 11), ('Fabricated metal products', 83)],
    'Graphite': [('Fabricated metal products', 38), ('Non-ferrous metals and products', 51), ('Electronic parts, devices and electronic circuits', 6), ('General-purpose machinery', 1)],
    'Indium': [('Electronic parts, devices and electronic circuits', 80), ('Chemical and allied products', 20)],
    'Iron': [('Fabricated metal products', 22), ('Transportation equipment', 30), ('Electrical machinery, equipment and supplies', 8), ('Production machinery', 5)],
    'Lead': [('Electronic parts, devices and electronic circuits', 85), ('Chemical and allied products', 6), ('Fabricated metal products', 9)],
    'Lignite': [('Electrical machinery, equipment and supplies', 86)],
    'Lithium': [('Electrical machinery, equipment and supplies', 71), ('Ceramic, stone and clay products', 14), ('Chemical and allied products', 6)],
    'Magnesium': [('Chemical and allied products', 70), ('Iron and steel', 10)],
    'Manganese': [('Transportation equipment', 14), ('Fabricated metal products', 12), ('General-purpose machinery', 11)],
    'Molybdenum': [('Iron and steel', 90), ('Chemical and allied products', 6), ('Electrical machinery, equipment and supplies', 2)],
    'Natural gas': [('Petroleum and coal products', 100)],
    'Nickel': [('Production machinery', 31), ('Electronic parts, devices and electronic circuits', 33), ('Transportation equipment', 19)],
    'Niobium': [('Fabricated metal products', 29), ('Transportation equipment', 24), ('Chemical and allied products', 5), ('Iron and steel', 10), ('Petroleum and coal products', 24)],
    'Phosphorus': [('Food', 70), ('Chemical and allied products', 18)],
    'Platinum': [('Transportation equipment', 38), ('Chemical and allied products', 13), ('Electronic parts, devices and electronic circuits', 10)],
    'Rare earths': [('Electronic parts, devices and electronic circuits', 45), ('Chemical and allied products', 13), ('Iron and steel', 16)],
    'Selenium': [('Ceramic, stone and clay products', 40), ('Chemical and allied products', 6)],
    'Silver': [('Chemical and allied products', 18), ('Transportation equipment', 13), ('General-purpose machinery', 7), ('Electronic parts, devices and electronic circuits', 13), ('Non-ferrous metals and products', 6)],
    'Strontium': [('Chemical and allied products', 1), ('Electronic parts, devices and electronic circuits', 75), ('Fabricated metal products', 0.2)],
    'Tantalum': [('Electronic parts, devices and electronic circuits', 48), ('General-purpose machinery', 11), ('Chemical and allied products', 16)],
    'Titanium': [('Chemical and allied products', 72)],
    'Tungsten': [('Production machinery', 74), ('Chemical and allied products', 7), ('Electronic parts, devices and electronic circuits', 6), ('Fabricated metal products', 7)],
    'Uranium': [('General-purpose machinery', 50)],
    'Vanadium': [('Iron and steel', 98), ('Chemical and allied products', 2)],
    'Zinc': [('Fabricated metal products', 85), ('Chemical and allied products', 5), ('Electronic parts, devices and electronic circuits', 10)],
    'Zirconium': [('Non-ferrous metals and products', 36), ('Chemical and allied products', 35), ('Ceramic, stone and clay products', 15)],
}


# =============================================================================
# 2. SETTINGS AND FILE HANDLING
# =============================================================================

@dataclass
class Settings:
    """User-defined settings:

    country           country assessed, spelled as in the Comtrade file / production sheets (e.g. "Japan", "Germany")
    mode              "import" -> sourcing mix = the country's import mix, all four categories
                      "global" -> sourcing mix = world production shares, no vulnerability
    data_dir          folder with the supporting files
    results_dir       folder where CSVs and figures are written (created automatically if missing)
    refine_code       False (default) calculates the data as the original Japan/Japan Global scripts
                          True add refinements listed below:
                                (1.) !!!!
                                (2.) !!!!
                          Also, corrects some data/logic problems found within the original scripts:
                                (a) Reserves.xlsx has country names with trailing spaces
                                    (e.g. "China ") that never match the other tables, so most
                                    reserve countries were silently ignored in the
                                    feasibility indicator.
                                (b) global mode squared the 'Total' row (100 %) into the
                                    "Concentration of production" sum, adding +1.0.
                                (c) the co-production sheet spells "Natural Gas" / "Rare Earths"
                                    with capitals, so the original found no entry and used 0
                                    but Rare earths should be 0.67.
    show_plots      open the criticality-matrix window at the end

    Country-specific inputs:
    imports_file                            UN Comtrade import file of THE COUNTRY (all materials)
    value_added_file                        CSV 'Industry' and 'Value added' of the country's industries,
                                                      last row = total.  None = 'Value added' sheet of Indicators.xlsx
    economic_importance_file                CSV 'Material','Industry' and 'Share'
                                                     share (%) of each material's use by industry
                                                     industries must exist in the value-added table.  None = built-in Japan table.
    """
    country: str = 'Germany'
    mode: str = 'import'
    data_dir: Path = Path('Supporting files')
    results_dir: Path = Path('Results')
    refine_code: bool = False
    show_plots: bool = True
    imports_file: str | None = None          # default: Comtrade_all_2020.csv (Japan) / Comtrade_all_<year>.csv
    value_added_file: str | None = None
    economic_importance_file: str | None = None
    production_file: str = 'Production_All.xlsx'
    reserves_file: str = 'Reserves.xlsx'
    indicators_file: str = 'Indicators.xlsx'
    matrix_input_file: str | None = None

    def __post_init__(self):
        if self.mode not in ('import', 'global'):
            raise ValueError("mode must be 'import' or 'global'")
        self.data_dir = _resolve_dir(Path(self.data_dir))
        self.results_dir = Path(self.results_dir)
        if self.imports_file is None:
            self.imports_file = ('Comtrade_all_2020.csv' if self.country == 'Japan'
                                 else f'Comtrade_{self.country}_2020.csv')
        if self.matrix_input_file is None:      # the hot-spot classification is country-specific in import mode
            country_specific = self.mode == 'import' and self.country != 'Japan'
            self.matrix_input_file = (f'Result_total_{self.country}.csv' if country_specific
                                      else f'Result_total{self.suffix}.csv')

    @property
    def suffix(self) -> str:
        """'' for import mode, '_global' for global mode (appended to output names)."""
        return '' if self.mode == 'import' else '_global'

    @property
    def includes_vulnerability(self) -> bool:
        """The global variant does not assess vulnerability (method still to be updated)."""
        return self.mode == 'import'


def _resolve_dir(path: Path) -> Path:
    """Use 'path' as given, else look next to this file."""
    if path.is_absolute() or path.exists():
        return path
    return Path(__file__).resolve().parent / path


def _find_file(name: str, *directories: Path) -> Path:
    """Locate a supporting file. Accepts 'My file.xlsx' or 'My_file.xlsx' spellings."""
    for directory in directories:
        for candidate in (name, name.replace(' ', '_')):
            if (directory / candidate).exists():
                return directory / candidate
    searched = ', '.join(str(d) for d in directories)
    raise FileNotFoundError(f"Could not find '{name}' (searched: {searched}). Put the file there "
                            f"or change the file name / DATA_DIR in the settings block of the script.")


# =============================================================================
# 3. LOADING AND PREPARING THE INPUT DATA
# =============================================================================

@dataclass
class Inputs:
    """All raw inputs, prepared once. Dictionaries are keyed by material name."""
    imports: dict[str, pd.DataFrame]      # the country's imports per partner (tonnes, % of total); {} in global mode
    production: dict[str, pd.DataFrame]   # world mine production by country and year + 'Percent'
    reserves: dict[str, pd.DataFrame]     # world reserves by country + 'Percent'
    by_country: pd.DataFrame              # country indicators (PPI, WGI, GI, ETI, GPI, HRA, WDI, biodiversity)
    by_material: pd.DataFrame             # material indicators (volatility, primary use, substitutability, ...)
    coproduction: pd.Series               # occurrence of co-production (0 = main product ... 1 = companion only)
    ssm: pd.DataFrame                     # small-scale-mining share by material (rows) and country (columns)
    value_added: pd.Series                # value added per industry of the country; last row = total ({} in global mode)
    sector_shares: dict[str, list]        # material -> [(industry, share %), ...]     ({} in global mode)
    targets: pd.Series                    # target value per supply-risk indicator


def load_imports(path: Path, country: str) -> dict[str, pd.DataFrame]:
    """Read the UN Comtrade imports of 'country' and return one table per material.

    Safety check: if the file names its reporting country ('ReporterDesc') it must be
    'country' - otherwise it would silently run on another country's imports.

    Columns: Country, PartnerISO, 'Netweight (t)', Percentage.
    * kg are converted to tonnes
    * rows of the same partner are summed
    * Percentage = partner's share of the material's *World* total (the 'World' row
      itself is 100 %).  The World row is later used as "total imports".
    """
    columns = ['Commodity', 'PartnerDesc', 'PartnerISO', 'NetWgt']
    has_reporter = 'ReporterDesc' in pd.read_csv(path, nrows=0).columns
    raw = pd.read_csv(path, usecols=columns + (['ReporterDesc'] if has_reporter else []))
    if has_reporter:
        reporters = set(raw['ReporterDesc'].dropna().astype(str).str.strip())
        if reporters != {country}:
            raise ValueError(f"'{path.name}' contains imports of {sorted(reporters)}, not of {country}. "
                             f"Provide the Comtrade import file of {country} (see Settings.imports_file).")
    grouped = (raw.groupby(['Commodity', 'PartnerDesc', 'PartnerISO'], sort=False)['NetWgt']
                  .sum().reset_index()
                  .rename(columns={'PartnerDesc': 'Country'}))
    grouped['Netweight (t)'] = grouped['NetWgt'] / 1000
    tables = {}
    for material, table in grouped.groupby('Commodity', sort=False):
        table = table.drop(columns='NetWgt').reset_index(drop=True)
        world = table.loc[table['Country'] == 'World', 'Netweight (t)']
        if world.empty:
            raise ValueError(f"No 'World' total row in the import data of {material}.")
        table['Percentage'] = table['Netweight (t)'] / world.iloc[0] * 100
        tables[material] = table
    return tables


def load_sheets_with_shares(path: Path, strip_names: bool) -> dict[str, pd.DataFrame]:
    """Read a workbook with one sheet per material (production or reserves).

    Each sheet is indexed by Country and its LAST ROW is the world total.  A 'Percent'
    column is added: each country's share (%) of the last data column
    (production: most recent year; reserves: 'Reserves').
    """
    sheets = pd.read_excel(path, sheet_name=None)
    for material, sheet in sheets.items():
        sheet = sheet.set_index('Country')
        if strip_names:
            sheet.index = sheet.index.str.replace('\ufeff', '', regex=False).str.strip()
        latest = sheet.iloc[:, -1]
        sheet['Percent'] = latest / latest.iloc[-1] * 100
        sheets[material] = sheet
    return sheets


def load_inputs(settings: Settings) -> Inputs:
    """Read every supporting file (located in Settings)."""
    d = settings.data_dir
    production = load_sheets_with_shares(_find_file(settings.production_file, d), strip_names=False)
    reserves = load_sheets_with_shares(_find_file(settings.reserves_file, d),
                                       strip_names=settings.refine_code)
    _warn_about_country_names(reserves, settings)

    sheets = pd.read_excel(_find_file(settings.indicators_file, d), sheet_name=None)
    coproduction = sheets['Occurrence of co-production'].set_index('Commodity')['Quantitative indicator']
    if settings.refine_code:            # 'Natural Gas' -> 'Natural gas', 'Rare Earths' -> 'Rare earths'
        canonical = {m.lower(): m for m in MATERIALS}
        coproduction.index = [canonical.get(str(name).strip().lower(), name) for name in coproduction.index]

    if settings.mode == 'import':            # country-specific data are only needed for the import mix / vulnerability
        imports = load_imports(_find_file(settings.imports_file, d), settings.country)
        value_added, sector_shares = load_economic_importance(settings, sheets)
    else:
        imports, value_added, sector_shares = {}, pd.Series(dtype=float), {}
    return Inputs(
        imports=imports, production=production, reserves=reserves,
        by_country=sheets['Indicators by country'].set_index('Country'),
        by_material=sheets['Indicators by materials'].set_index('Commodity'),
        coproduction=coproduction,
        ssm=sheets['SSM'].set_index('Commodity'),
        value_added=value_added, sector_shares=sector_shares,
        targets=sheets['Categories and targets'].set_index('Categories')['Target'],
    )


def load_economic_importance(settings: Settings, sheets: dict[str, pd.DataFrame]) -> tuple[pd.Series, dict[str, list]]:
    """Industry value added and the sector shares per material (economic importance).

    Japan : 'Value added' sheet of Indicators.xlsx + the built-in sector table.
    Germany : 'Value added' sheet of Indicators.xlsx + the built-in sector table.
    Other countries: both must be supplied as CSV files (Settings.value_added_file and
    Settings.economic_importance_file)
        value added file            columns  Industry, Value added
        economic importance         columns  Material, Industry, Share  
    """
    d = settings.data_dir
    
    # Read indicators file
    if settings.value_added_file:
        value_added = pd.read_csv(_find_file(settings.value_added_file, d)).set_index('Industry')['Value added']
    elif settings.country == 'Germany':
        value_added = sheets['Value added'].set_index('Industry')['Value added']
    elif settings.country == 'Japan':
        value_added = sheets['Value added'].set_index('Industry')['Value added']
    else:
        raise ValueError(f"Import mode for {settings.country} needs {settings.country}'s industry data: set "
                         "value_added_file (the 'Value added' sheet in Indicators.xlsx describes Japan).")
    
    # Read economic importance file
    if settings.economic_importance_file:
        table = pd.read_csv(_find_file(settings.economic_importance_file, d))
        shares = {m: list(zip(g['Industry'], g['Share'])) for m, g in table.groupby('Material', sort=False)}
    elif settings.country == 'Germany':
        shares = JAPAN_ECONOMIC_IMPORTANCE_SECTORS
    elif settings.country == 'Japan':
        shares = JAPAN_ECONOMIC_IMPORTANCE_SECTORS
    else:
        raise ValueError(f"Import mode for {settings.country} needs economic_importance_file "
                         "(columns Material, Industry, Share).")
    missing = [m for m in MATERIALS if m not in shares]
    unknown = sorted({industry for rows in shares.values() for industry, _ in rows} - set(value_added.index))
    if missing or unknown:
        raise ValueError(f"Economic-importance data incomplete. Materials without sector shares: {missing}. "
                         f"Industries not found in the value-added table: {unknown}.")
    return value_added, shares


def _warn_about_country_names(reserves: dict[str, pd.DataFrame], settings: Settings) -> None:
    """Tell the user if country names carry stray spaces. They would fail to match."""
    if settings.refine_code:
        return
    dirty = sum(int((idx != idx.str.strip()).sum()) for idx in (r.index.astype(str) for r in reserves.values()))
    if dirty:
        warnings.warn(
            f"{dirty} country names in the reserves workbook have leading/trailing spaces "
            "and will not match the other tables (original behaviour kept). "
            "Set refine_code=True to correct this.", stacklevel=2)


# =============================================================================
# 4. THE SOURCING MIX OF ONE MATERIAL
# =============================================================================

@dataclass
class MaterialData:
    """Everything the indicator functions need to know about ONE material."""
    name: str
    imports: pd.DataFrame | None    # None in global mode
    production: pd.DataFrame
    reserves: pd.DataFrame
    mix: pd.Series          # sourcing mix in % per producing country (see build_mix)

    @property
    def year_columns(self) -> list:
        """Production years (all columns except the derived 'Percent'), oldest first."""
        return [c for c in self.production.columns if c != 'Percent']

    @property
    def latest_production(self) -> pd.Series:
        """Most recent production year per country (last row = world total)."""
        return self.production[self.year_columns[-1]]

    @property
    def total_imports_t(self) -> float:
        """The country's total imports of the material in tonnes (the 'World' row)."""
        return float(self.imports.loc[self.imports['Country'] == 'World', 'Netweight (t)'].iloc[0])


def build_mix(mode: str, imports: pd.DataFrame, production: pd.DataFrame) -> pd.Series:
    """Sourcing mix: which countries does the supply of this material come from? (in %)

    global mode:  simply each country's share of world production.

    import mode:  the country's import mix.
        * Imports from a country that also mines the material count for that country.
        * Imports from countries that do NOT appear in the production table (traders,
          re-exporters, "other Asia" ...) are re-allocated to the real producers in
          proportion to their production share, because the material originally
          came from mines somewhere.

    Significance: every country-based indicator (governance, conflict, water stress ...)
    is weighted by this mix, so it decides whose risks are attributed to the material.
    """
    producers = production.index[:-1]                       # last row is the world total
    if mode == 'global':
        return production['Percent'].loc[producers]

    import_share = imports.set_index('Country')['Percentage']
    from_producers = import_share.reindex(production.index).fillna(0)
    non_producers = import_share.drop(index='World').loc[lambda s: ~s.index.isin(production.index)]
    reallocated = production['Percent'] * non_producers.sum() / 100
    return (reallocated + from_producers).loc[producers]


def build_material_data(inputs: Inputs, settings: Settings) -> dict[str, MaterialData]:
    """Bundle inputs and sourcing mix for every material."""
    imports = (lambda material: inputs.imports[material]) if settings.mode == 'import' else (lambda material: None)
    return {m: MaterialData(m, imports(m), inputs.production[m], inputs.reserves[m],
                            build_mix(settings.mode, imports(m), inputs.production[m]))
            for m in MATERIALS}


# =============================================================================
# 5. INDICATOR FUNCTIONS  (one number per material)
# =============================================================================
# Helpers ----------------------------------------------------------------------

def weighted_country_score(mix: pd.Series, indicator: pd.Series, power: int = 1) -> float:
    """sum over countries of  mix[country] * indicator[country] ** power.

    The main factor of all country-based indicators.  Countries without an indicator
    value are skipped.  power=2 is used by indicators that are squared in the method
    so that especially bad countries weigh disproportionately.
    """
    return float((mix * indicator.reindex(mix.index) ** power).sum())


def lookup_material_value(table: pd.DataFrame | pd.Series, material: str, column: str | None = None) -> float:
    """Read a material-level indicator from a table indexed by material name.

    A missing entry counts as 0 (as in the original scripts) but is reported, because a
    silent 0 would hide a spelling mismatch between the input files.
    """
    if material not in table.index:
        warnings.warn(f"No entry for '{material}' in a material-indicator table - using 0 "
                      "(original behaviour). Check the spelling or set refine_code=True.",
                      stacklevel=2)
        return 0.0
    values = table.loc[[material]] if column is None else table.loc[[material], column]
    return float(values.sum())


def herfindahl(shares: pd.Series) -> float:
    """Concentration = sum of squared percentage shares (Herfindahl-Hirschman index)."""
    return float((shares ** 2).sum())


# Supply risk -------------------------------------------------------------------

def concentration_of_reserves(md: MaterialData) -> float:
    """HHI of world reserves.  Few countries holding the reserves -> higher risk."""
    return herfindahl(md.reserves['Percent'].iloc[:-1])


def concentration_of_production(md: MaterialData, settings: Settings) -> float:
    """HHI of the sourcing mix.  Few suppliers -> higher risk."""
    shares = md.mix
    if settings.mode == 'global' and not settings.refine_code:
        shares = md.production['Percent']          # original behaviour: includes 'Total' (=100 %) -> +1.0
    return herfindahl(shares)


def feasibility_of_exploration(md: MaterialData, inputs: Inputs, settings: Settings) -> float:
    """Political/societal hurdles to opening new mines in countries that hold reserves.

    For each country with reserves AND a place in the sourcing mix:
    mix share x (PPI_REFERENCE_MAX - Policy Perception Index).  
    A high PPI means the investment climate for mining is poor, so large value = risky.
    A country is only counted if its production data are complete (import mode: latest year,
    global mode: all years) - as in the original.
    """
    gap = PPI_REFERENCE_MAX - inputs.by_country['PPI 2020']
    required = md.year_columns if settings.mode == 'global' else md.year_columns[-1:]
    complete = (md.production[required].assign(share=md.mix)
                .reindex(md.reserves.index).dropna())
    return float((gap.reindex(complete.index) * complete['share']).sum())


def political_stability(md: MaterialData, inputs: Inputs) -> float:
    """Mix-weighted Worldwide Governance Indicator (WGI): governance instability in the
    sourcing countries can interrupt production and cause supply restrictions."""
    return weighted_country_score(md.mix, inputs.by_country['WGI 2020'])


def mining_capacity(md: MaterialData) -> float:
    """Mix-weighted reserves-to-production ratio (years of extraction left) for countries
    holding reserves.  Short remaining lifetimes -> supply restrictions may occur.
    Countries with zero production get 0 (ratio undefined)."""
    reserves = md.reserves['Reserves'].iloc[:-1].astype(int)
    ratio = reserves / md.latest_production.astype(int)
    per_country = (md.mix * ratio / 100).reindex(reserves.index)
    return float(per_country.replace(np.inf, 0).sum())


def trade_barriers(md: MaterialData, inputs: Inputs) -> float:
    """Mix-weighted Enabling Trade Index (ETI): barriers to trade in the sourcing countries."""
    return weighted_country_score(md.mix, inputs.by_country['ETI 2016'])


def demand_growth(md: MaterialData) -> float:
    """Average growth of the world production total over the last 4 year-on-year steps
    (as a fraction, negative growth counts as 0).

    If demand grows faster than production can follow, shortages may occur.
    NOTE (original method kept): each change is divided by the newer year's total.
    """
    totals = md.production[md.year_columns].iloc[-1].astype(int).iloc[-5:]   # Total row, 5 latest years
    newest_first = totals.iloc[::-1].to_numpy(dtype=float)
    with np.errstate(divide='ignore', invalid='ignore'):
        yoy_percent = (newest_first[:-1] - newest_first[1:]) / newest_first[:-1] * 100
    growth = pd.Series(yoy_percent).mean() / 100
    return float(growth) if growth > 0 else 0.0


def price_fluctuation(md: MaterialData, inputs: Inputs) -> float:
    """Price volatility (%): unexpected price jumps can make a resource unaffordable."""
    return lookup_material_value(inputs.by_material, md.name, 'Volatility index (%) 2020')


def primary_material_use(md: MaterialData, inputs: Inputs) -> float:
    """Share (%) of the supply that is primary and not recycled material."""
    return lookup_material_value(inputs.by_material, md.name, 'Primary material use (%)')


def occurrence_of_coproduction(md: MaterialData, inputs: Inputs) -> float:
    """0 = mined as main product and 1 = only as by-product
    by-products cannot react to their own demand because output follows the host metal."""
    return lookup_material_value(inputs.coproduction, md.name)


# Vulnerability (import mode) ---------------------------------------------------

def economic_importance(md: MaterialData, inputs: Inputs) -> float:
    """sum(sector share x sector value added) / total value added of the country's industry.
    How much of the country's manufacturing depends on the material."""
    sectors = inputs.sector_shares[md.name]
    weighted = sum(share * inputs.value_added.loc[sector] for sector, share in sectors)
    return float(weighted / inputs.value_added.iloc[-1])


def domestically_required_demand(md: MaterialData) -> float:
    """Total imported quantity in tonnes (proxy for the country's demand)."""
    return md.total_imports_t


def share_of_global_production(md: MaterialData) -> float:
    """The country's imports relative to world production: high = it competes with other buyers."""
    return md.total_imports_t / float(md.latest_production.iloc[-1])


def dependency_on_imports(md: MaterialData, country: str) -> float:
    """1 - domestic production / imports.  1 means fully import dependent.
    Domestic production = the country's row in the production sheet; if there is none
    (e.g. Nickel in Japan) it is taken as 0.
    NOTE: values can be negative when domestic production exceeds imports (e.g. Cadmium in Japan)."""
    own = md.latest_production[md.production.index.str.startswith(country)]
    domestic = float(own.iloc[0]) if len(own) else 0.0
    return 1 - domestic / md.total_imports_t


def substitutability(md: MaterialData, inputs: Inputs) -> float:
    """Score for how hard the material is to replace."""
    return lookup_material_value(inputs.by_material, md.name, 'Substitutability')


def future_technologies(md: MaterialData, inputs: Inputs) -> float:
    """Importance of the material for future technologies."""
    return lookup_material_value(inputs.by_material, md.name, 'Future technologies')


# Social standards --------------------------------------------------------------

def small_scale_mining(md: MaterialData, inputs: Inputs) -> float:
    """Mix-weighted share of small-scale (often informal) mining in the sourcing countries."""
    shares = inputs.ssm.loc[md.name].dropna()
    return float((md.mix.reindex(shares.index) * shares).sum())


def geopolitical_risk(md: MaterialData, inputs: Inputs) -> float:
    """Mix x (GI + GPI)^2: probability of armed conflict / lack of peace in the sourcing countries."""
    c = inputs.by_country
    return weighted_country_score(md.mix, c['GPI 2020'] + c['GI 2020'], power=2)


def human_right_abuse(md: MaterialData, inputs: Inputs) -> float:
    """Mix x (forced labour, child labour, torture score)^2 of the sourcing countries."""
    return weighted_country_score(md.mix, inputs.by_country['Human right abuse scaled'], power=2)


# Environmental standards -------------------------------------------------------

def water_scarcity(md: MaterialData, inputs: Inputs) -> float:
    """Mix x (Water Depletion Index)^2: mining where water is scarce harms people and ecosystems."""
    return weighted_country_score(md.mix, inputs.by_country['WDI'], power=2)


def climate_change(md: MaterialData, inputs: Inputs) -> float:
    """Climate-change impact of mining the material (ReCiPe endpoint; same for all origins)."""
    return lookup_material_value(inputs.by_material, md.name, 'Climate change')


def sensitivity_of_local_biodiversity(md: MaterialData, inputs: Inputs) -> float:
    """Mix x (biodiversity sensitivity)^2 of the sourcing countries (ecoregion scarcity,
    conservation status, endemic species)."""
    return weighted_country_score(md.mix, inputs.by_country['Biodiversity'], power=2)


# =============================================================================
# 6. ASSEMBLE THE RAW INDICATOR TABLES
# =============================================================================

def compute_raw_indicators(materials: dict[str, MaterialData], inputs: Inputs, settings: Settings) -> dict[str, pd.DataFrame]:
    """Evaluate every indicator for every material.  Returns tables with materials as rows.

    keys: 'supply_risk', 'social', 'environmental' and (import mode) 'vulnerability'.
    Values are still in their natural units - they are only comparable after scaling.
    """
    def table(columns, functions):
        return pd.DataFrame({name: [fn(md) for md in materials.values()]
                             for name, fn in zip(columns, functions)},
                            index=list(materials))

    tables = {
        'supply_risk': table(SUPPLY_RISK_INDICATORS, [
            lambda md: concentration_of_production(md, settings),
            concentration_of_reserves,
            lambda md: feasibility_of_exploration(md, inputs, settings),
            lambda md: political_stability(md, inputs),
            mining_capacity,
            lambda md: trade_barriers(md, inputs),
            demand_growth,
            lambda md: price_fluctuation(md, inputs),
            lambda md: primary_material_use(md, inputs),
            lambda md: occurrence_of_coproduction(md, inputs),
        ]),
        'social': table(SOCIAL_INDICATORS, [
            lambda md: small_scale_mining(md, inputs),
            lambda md: geopolitical_risk(md, inputs),
            lambda md: human_right_abuse(md, inputs),
        ]),
        'environmental': table(ENVIRONMENTAL_INDICATORS, [
            lambda md: water_scarcity(md, inputs),
            lambda md: climate_change(md, inputs),
            lambda md: sensitivity_of_local_biodiversity(md, inputs),
        ]),
    }
    if settings.includes_vulnerability:
        tables['vulnerability'] = table(VULNERABILITY_INDICATORS, [
            lambda md: economic_importance(md, inputs),
            domestically_required_demand,
            share_of_global_production,
            lambda md: dependency_on_imports(md, settings.country),
            lambda md: substitutability(md, inputs),
            lambda md: future_technologies(md, inputs),
        ])
    return tables


# =============================================================================
# 7. SCALING
# =============================================================================

def distance_to_target(raw_supply_risk: pd.DataFrame, targets: pd.Series) -> pd.DataFrame:
    """Supply risk only: express each indicator relative to its target.

    1. bring indicators to the unit of the targets (SUPPLY_RISK_UNIT_RESCALING)
    2. score = (value / target)^2  - the further above the target, the higher the risk
       Mining capacity is inverted, (target / value)^2, because MORE remaining years
       means LESS risk (value 0 -> score 0, as in the original)
    3. scores below DISTANCE_TO_TARGET_FLOOR are set to 0 ("target met, no risk").
    Columns are ordered alphabetically with Mining capacity last (as in the original CSVs).
    """
    values = raw_supply_risk.copy()
    for column, divisor in SUPPLY_RISK_UNIT_RESCALING.items():
        values[column] = values[column] / divisor

    others = [c for c in SUPPLY_RISK_INDICATORS if c != MINING_CAPACITY]
    score = (values[others] / targets[others]) ** 2
    score[MINING_CAPACITY] = ((targets[MINING_CAPACITY] / values[MINING_CAPACITY]) ** 2
                              ).astype(float).replace(np.inf, 0)
    score = score[sorted(others) + [MINING_CAPACITY]]
    return score.mask(score < DISTANCE_TO_TARGET_FLOOR, 0)


def min_max(table: pd.DataFrame) -> pd.DataFrame:
    """Rescale every column to 0..1 (lowest material = 0, highest = 1)."""
    return (table - table.min()) / (table.max() - table.min())


def add_totals(scaled: pd.DataFrame) -> pd.DataFrame:
    """Append 'Total' (sum of indicators) and 'Scaled total' (Total rescaled to 0..1).
    'Scaled total' is the category score that feeds the criticality matrix."""
    result = scaled.copy()
    result['Total'] = scaled.sum(axis=1)
    result['Scaled total'] = (result['Total'] - result['Total'].min()) / (result['Total'].max() - result['Total'].min())
    return result


# =============================================================================
# 8. EXPORTS AND PLOTS
# =============================================================================

@dataclass(frozen=True)
class Category:
    key: str          # key in the tables dictionary
    label: str        # y-axis label of the chart
    folder: str       # sub-folder of the results directory
    csv_name: str     # file name of the 0..1 indicator table (without extension)
    total_name: str   # file name of the table with Total / Scaled total columns
    png_name: str     # file name of the chart


CATEGORIES = [
    Category('supply_risk', 'Supply risk', 'Supply risk',
             'Supply risk scaled', 'Supply risk total', 'Supply risk'),
    Category('vulnerability', 'Vulnerability', 'Vulnerability',
             'Vulnerability', 'Vulnerability total', 'Vulnerability'),
    Category('social', 'Compliance with social standards', 'Social standards',
             'Compliance with social standards', 'Compliance with social standards total', 'Social standard'),
    Category('environmental', 'Compliance with environmental standards', 'Environmental standards',
             'Compliance with environmental standards', 'Compliance with environmental standards total',
             'Environmental standard'),
]


def export_tables(category: Category, scaled: pd.DataFrame, totals: pd.DataFrame, settings: Settings) -> None:
    """Write the indicator table (0..1) and the table with Total / Scaled total columns."""
    folder = settings.results_dir / category.folder
    folder.mkdir(parents=True, exist_ok=True)
    scaled.to_csv(folder / f'{category.csv_name}{settings.suffix}.csv')
    totals.to_csv(folder / f'{category.total_name}{settings.suffix}.csv')


def plot_stacked_bars(totals: pd.DataFrame, category: Category, settings: Settings) -> None:
    """Stacked bar chart: materials sorted by total score, one colour per indicator."""
    data = totals.sort_values('Total', ascending=False).drop(columns=['Total', 'Scaled total'])
    ax = data.plot(kind='bar', stacked=True, figsize=(16, 10), grid=True, zorder=10)
    ax.set_xlabel('Resources', fontsize=12)
    ax.set_ylabel(category.label, fontsize=12)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    ax.legend(fontsize=12)
    settings.results_dir.mkdir(parents=True, exist_ok=True)
    ax.get_figure().savefig(settings.results_dir / f'{category.png_name}{settings.suffix}.png',
                            dpi=300, bbox_inches='tight', pad_inches=0.0)
    plt.close(ax.get_figure())


def export_scaled_totals(final: dict[str, pd.DataFrame], settings: Settings) -> None:
    """Write one table with the 'Scaled total' of every category (one row per material).

    Column names match 'Result_total.csv', so these numbers can be copied straight into
    the matrix input file (which otherwise has to be kept in sync by hand).
    """
    names = {'supply_risk': 'Supply Risk', 'vulnerability': 'Vulnerability',
             'social': 'Social Standards Compliance', 'environmental': 'Environmental Standards Compliance'}
    table = pd.DataFrame({names[key]: df['Scaled total'] for key, df in final.items()})
    settings.results_dir.mkdir(parents=True, exist_ok=True)
    table.to_csv(settings.results_dir / f'Scaled totals{settings.suffix}.csv', index_label='Material')


#: Marker style per hotspot class in the criticality matrix.
HOTSPOT_STYLES = {
    'neither':       dict(c='black', marker='.', s=70, label='Neither an environmental nor a social hotspot'),
    'social':        dict(c='red', marker='s', s=30, label='Social hotspot'),
    'environmental': dict(c='green', marker='^', s=40, label='Environmental hotspot'),
    'both':          dict(c='black', marker='^', s=40, label='Social and environmental hotspot'),
}
#: Criticality iso-lines: supply risk = k / vulnerability. (k, colour, line width)
CRITICALITY_LINES = [(0.2, '#cccccc', 1.5), (0.4, '#969696', 1), (0.6, '#525252', 1), (0.8, '#252525', 1)]
#: Position of the criticality zone numbers 1-5 printed along the top of the matrix.
ZONE_LABEL_X = [0.1, 0.3, 0.5, 0.7, 0.95]


def hotspot_class(label: str) -> str:
    """Map the free-text 'Hot Spots' label of the matrix input to a style key"""
    text = label.lower()
    if 'neither' in text:
        return 'neither'
    if 'social' in text and 'environmental' in text:
        return 'both'
    return 'social' if 'social' in text else 'environmental'


def plot_criticality_matrix(settings: Settings) -> None:
    """Criticality matrix: vulnerability (x) against supply risk (y) with iso-criticality lines.

    Input is the hand-maintained 'Result_total[_global].csv' with columns Material (label),
    Supply Risk, Vulnerability and Hot Spots.  Supply Risk / Vulnerability are the
    'Scaled total' columns exported by this script.
    """
    try:
        path = _find_file(settings.matrix_input_file, settings.data_dir, settings.results_dir)
    except FileNotFoundError:
        print(f"  Criticality matrix skipped: '{settings.matrix_input_file}' not found. Create it from "
              f"'Scaled totals{settings.suffix}.csv' (add a 'Material' label and a 'Hot Spots' column).")
        return
    results = pd.read_csv(path)
    results['style'] = results['Hot Spots'].map(hotspot_class)
    figsize, label_offset, label_align = ((14, 10), 0.01, 'center') if settings.mode == 'import' else ((10, 10), 0.02, 'right')

    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(0.01, 2.0, 0.01)
    for k, colour, width in CRITICALITY_LINES:
        ax.plot(x, k / x, color=colour, linewidth=width)
    for style, group in results.groupby('style'):
        ax.scatter(group['Vulnerability'], group['Supply Risk'], **HOTSPOT_STYLES[style])
    for number, x_pos in enumerate(ZONE_LABEL_X, start=1):
        ax.text(x_pos, 0.925, str(number), fontsize=10, bbox=dict(boxstyle='round', facecolor='#ffffff'),
                verticalalignment='center', horizontalalignment='center')
    for _, row in results.iterrows():
        ax.annotate(row['Material'], (row['Vulnerability'], row['Supply Risk'] + label_offset), ha=label_align)

    ax.set(xlabel='Vulnerability', ylabel='Supply Risk')
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15), frameon=False, ncol=4)
    ax.grid()
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    settings.results_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(settings.results_dir / f'Matrix{settings.suffix}.png', dpi=450, bbox_inches='tight', pad_inches=0.0)
    if settings.show_plots:
        plt.show()
    plt.close(fig)


# =============================================================================
# 9. MAIN ENTRY POINT
# =============================================================================

def run_assessment(settings: Settings) -> dict[str, pd.DataFrame]:
    """Run the complete SCARCE workflow and return the final tables (with totals).

    Steps: load -> sourcing mix -> raw indicators -> scaling -> CSV/plots -> matrix.
    Also writes 'Scaled totals[_global].csv' (all category scores in one table).
    """
    print(f"SCARCE - {settings.country}, mode '{settings.mode}'"
          f"{' (known issues corrected)' if settings.refine_code else ''}")
    inputs = load_inputs(settings)
    materials = build_material_data(inputs, settings)
    raw = compute_raw_indicators(materials, inputs, settings)

    # Supply risk is compared with targets first; the other categories are only min-max scaled.
    scaled = {'supply_risk': min_max(distance_to_target(raw['supply_risk'], inputs.targets))}
    scaled.update({key: min_max(table) for key, table in raw.items() if key != 'supply_risk'})

    final = {}
    for category in CATEGORIES:
        if category.key not in scaled:
            continue
        final[category.key] = add_totals(scaled[category.key])
        export_tables(category, scaled[category.key], final[category.key], settings)
        plot_stacked_bars(final[category.key], category, settings)
        print(f"  {category.label}: exported")

    export_scaled_totals(final, settings)
    plot_criticality_matrix(settings)
    print(f"Done. Results in: {settings.results_dir.resolve()}")
    return final

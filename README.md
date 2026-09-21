# Scarce_Germany_Refinement

## Files
| File | Purpose |
|---|---|
| 'scarce_core.py' | All logic, written once: loading, sourcing mix, indicators, scaling, exports, plots. |
| 'SCARCE_Germany.py' | **Germany**, import mix (all four categories). Needs three German input files (below). |
| 'SCARCE_Germany_global.py' | **Germany**, world production mix (no vulnerability). |
| 'SCARCE_Japan.py', 'SCARCE_Japan_global.py' | The Japan versions (results unchanged). |

Put the files next to your 'Supporting files/' folder and run e.g. 'python SCARCE_Germany.py'.
Settings are at the top of each entry script. Needs 'pandas', 'numpy', 'matplotlib', 'openpyxl'.
File names with spaces or underscores ('Production 2019 2020.xlsx' / 'Production_2019_2020.xlsx') both work.

### Files needed for 'SCARCE_Germany.py' (put in 'Supporting files/')
1. 'Comtrade_Germany_2020.csv' – UN Comtrade **imports** of Germany, all 35 materials, same layout as your Japan file (incl. 'ReporterDesc', 'PartnerDesc', 'PartnerISO', 'NetWgt' and the 'World' row). The script stops if the file names another reporter.
2. 'Germany_value_added.csv' – columns 'Industry', 'Value added'; the **last row is the total**.
3. 'Germany_economic_importance.csv' – columns 'Material', 'Industry', 'Share'. Share = % of the material used by that industry (an industry may appear twice for a material). All 35 materials required and every industry must exist in file 2. The script lists any gaps.

Optional: 'Result_total_Germany.csv' ('Material', 'Supply Risk', 'Vulnerability', 'Hot Spots') draws the matrix; otherwise it is skipped, and 'Scaled totals.csv' gives you the numbers to fill it.

## Implementations to refine how SCARCE is calculated
Refinement to SCARCE code is activated when 'REFINE_CODE = True' in the entry script.

1. 
2. 
3. 

## Issues found in the original scripts
Set 'REFINE_CODE = True' in the entry script to correct 1–3 (only supply risk changes but the top-5 stays the same).

1. **Reserves workbook: stray spaces in 31 country names** ("China "). They never match other tables, so most reserve countries were skipped in *Feasibility of exploration* and *Mining capacity*.
2. **Global mode: 'Concentration of production' includes the 'Total' row** (+1.0 on every material).
3. **Co-production sheet: "Natural Gas"/"Rare Earths" capitalised**, so both got 0 (Rare earths should be 0.67).
4. **Nickel crashes the original Japan script** (no Japan production row). Domestic production is taken as 0 → dependency 1.0. The same rule applies to any material a country does not produce.
5. *(Method question, not changed)* **Negative dependency on imports** when domestic production exceeds imports (Japan: Cadmium −313,332; Germany: Lignite), plus *Domestically required demand* in raw tonnes – both distort the min-max scaling.
6. *(Plot only, fixed)* The global matrix skipped the "neither hot-spot" group because of a label mismatch (26 materials not drawn).
7. **'Result_total*.csv' are out of sync with the script output** (Japan: 8 of 35 supply-risk rows differ but more in the global file). Refresh them from 'Scaled totals*.csv'.

Note: the following scripts weren't used -> 'Categories and targets.csv' and 'Substitutability and Future Technology Indicators.xlsx'.

## Indicator reference
| Category | Indicator | Significance |
|---|---|---|
| Supply risk | Concentration of production / reserves | Few suppliers or reserve holders → higher risk (Herfindahl index) |
| | Feasibility of exploration | Political/societal hurdles to opening mines where reserves exist |
| | Political stability | Governance quality (WGI) of sourcing countries |
| | Mining capacity | Reserves ÷ production (years left); short → risk |
| | Trade barriers | Enabling Trade Index of sourcing countries |
| | Demand growth | Recent growth of world production; fast growth strains supply |
| | Price fluctuation | Volatility can price users out |
| | Primary material use | Low recycling → more dependence on mining |
| | Occurrence of co-production | By-products cannot follow their own demand |
| Vulnerability | Economic importance | Value added of the country's industries using the material |
| | Domestically required demand / Share of global production | Volume needed and competition with other buyers |
| | Dependency on imports | 1 − domestic production ÷ imports |
| | Substitutability / Future technologies | Hard to replace; needed for future technologies |
| Social | Small scale mining, Geopolitical risk, Human right abuse | Mix-weighted country scores |
| Environmental | Water scarcity, Climate change, Biodiversity sensitivity | Mix-weighted country/material scores |

Scaling: supply risk is first compared with the targets (score = (value/target)², values < 0.8 → 0); every category is then min-max scaled to 0–1 per indicator, summed to 'Total' and rescaled to 'Scaled total' (the matrix axis value).
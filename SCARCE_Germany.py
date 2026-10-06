#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCARCE_Germany.py - criticality assessment of 35 materials for GERMANY
=======================================================================

Sourcing mix : Germany's IMPORT mix (UN Comtrade), with imports from non-producing
               trading countries re-allocated to the real producers.
Categories   : supply risk, vulnerability, compliance with social standards, and
               compliance with environmental standards.

Note: This script requires three Germany specific input files that must be placed in DATA_DIR.
They are as follows:

1. Comtrade_Germany_2020.csv
       UN Comtrade download of Germany's IMPORTS (reporter = Germany), all 35 materials,
       same columns as Comtrade_all_2020.csv (Commodity, PartnerDesc, PartnerISO, NetWgt,
       ReporterDesc ...) and including the 'World' total row per material.
       Important: The script won't to run if the file has a different reporting country.

2. Germany_value_added.csv
       Value added of German industry sectors.  Columns:   Industry and Value added
       Important: The last row must be the total of all sectors. 'Value Added' sheet of Indicators.xlsx.

3. Germany_economic_importance.csv
       Which industries use each material.  Columns:   Material, Industry, and Share
       Share = percent of the material's use in that industry (an industry may appear
       twice for one material).  
       Important: All 35 materials are required and every Industry must
       exist in Germany_value_added.csv.

Also used files: production/reserves workbooks, Indicators.xlsx
(country and material indicators, targets) which are country-independent.

Outputs go to RESULTS_DIR.
"""
from pathlib import Path
from scarce_core import Settings, run_assessment

# ----------------------------- USER SETTINGS ---------------------------------
DATA_DIR = Path('Supporting files')                                     # folder with the input files
RESULTS_DIR = Path('Results_Germany')                                   # folder for CSV files and figures (created automatically)
REFINE_CODE = False                                                     # False = reproduce the data as the original Japan script
                                                                        # True  = add refinements listed in scarce_core.Settings
SHOW_PLOTS = True                                                       # show the criticality matrix in a window

IMPORTS_FILE = 'Comtrade_all_2017.csv'                           # Germany's imports (UN Comtrade)
#VALUE_ADDED_FILE = 'Germany_value_added.csv'                    # Industry, Value added
#ECONOMIC_IMPORTANCE_FILE = 'Germany_economic_importance.csv'    # Material, Industry, Share (using built-in file from Japan)
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    run_assessment(Settings(country='Germany', mode='import', data_dir=DATA_DIR, results_dir=RESULTS_DIR,
                            imports_file=IMPORTS_FILE, refine_code=REFINE_CODE, show_plots=SHOW_PLOTS))

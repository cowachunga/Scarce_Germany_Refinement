#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCARCE_Japan_global.py - criticality assessment of 35 materials, GLOBAL sourcing mix
=====================================================================================

Same method as SCARCE_Japan.py, but the sourcing mix is the WORLD PRODUCTION mix
(who mines the material globally) instead of Japan's import mix.

Categories   : supply risk, compliance with social standards, compliance with
               environmental standards.  Vulnerability is not assessed here 
               (the method still needs to be updated - the original script
               printed a warning about this.)

Outputs in RESULTS_DIR and files carry the suffix '_global', e.g. 'Supply risk total_global.csv',
'Supply risk_global.png', 'Matrix_global.png'.

Note: the criticality matrix reads 'Result_total_global.csv' which is maintained by hand.
"""
from pathlib import Path
from scarce_core import Settings, run_assessment

# ----------------------------- USER SETTINGS ---------------------------------
DATA_DIR = Path('Supporting files')     # folder with the input files
RESULTS_DIR = Path('Results')           # folder for CSV files and figures (created automatically)
REFINE_CODE = False                     # False = reproduce the data as the original Japan global script
                                        # True  = add refinements listed in scarce_core.Settings
SHOW_PLOTS = True                       # show the criticality matrix in a window
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    run_assessment(Settings(country='Japan', mode='global', data_dir=DATA_DIR, results_dir=RESULTS_DIR,
                            refine_code=REFINE_CODE, show_plots=SHOW_PLOTS))

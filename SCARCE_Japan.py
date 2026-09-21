#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCARCE_Japan.py - criticality assessment of 35 materials for JAPAN
===================================================================

Sourcing mix : Japan's IMPORT mix (UN Comtrade 2020), with imports from non-producing
               trading countries re-allocated to the real producers.
Categories   : supply risk, vulnerability, compliance with social standards,
               compliance with environmental standards.

Outputs the following files in RESULTS_DIR:
    Supply risk/, Vulnerability/, Social standards/, Environmental standards/
        <category>.csv                indicators scaled 0..1
        <category> total.csv         'Total' and 'Scaled total' (which feeds the criticality matrix)
        <category>.png                stacked bar charts with materials sorted by total score
    Scaled totals.csv                 the four category scores per material in one table
    Matrix.png                        criticality matrix (needs Result_total.csv)

Note: the criticality matrix reads 'Result_total.csv'
"""
from pathlib import Path
from scarce_core import Settings, run_assessment

# ----------------------------- USER SETTINGS ---------------------------------
DATA_DIR = Path('Supporting files')     # folder with the input files
RESULTS_DIR = Path('Results')           # folder for CSV files and figures (created automatically)
REFINE_CODE = False                     # False = reproduce the data as the original Japan script
                                        # True  = add refinements listed in scarce_core.Settings
SHOW_PLOTS = True                       # show the criticality matrix in a window
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    run_assessment(Settings(country='Japan', mode='import', data_dir=DATA_DIR, results_dir=RESULTS_DIR,
                            refine_code=REFINE_CODE, show_plots=SHOW_PLOTS))

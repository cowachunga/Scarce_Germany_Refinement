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

1. Replace the “ETI 2016” indicator with “KOFGI.” These values have already been scaled to match the “ETI 2016” values in the “Indicators.xlsx” spreadsheet.
2. Add “DCC” as a new indicator under the new category, “Disaster Coping Capacity,” under dimension “Supply Risk.” This new category should have equal weighting as the other categories within “Supply Risk.”
3. Replace the additive aggregation approach with multiplicative aggregation via the geometric mean. Instead of summing the scaled indicator values, use the geometric mean to obtain the total. Then proceed as normal with the Distance-to-target approach to obtain the final scores.
4. Modify each indicator's min_max() normalization from [0,1] to [1,10] (like the 2024 UK Criticality Assessment), and remove the 0.8 target floor.
5. Make the "Supply Risk" and "Vulnerability" scores normalized in the [1,10] scale like the indicators now are, just like the 2024 UK Criticality Assessment does.
6. Add a "Final Criticality" score for each material, which is the geometric mean of the material's "Supply Risk" and "Vulnerability" scores.
7. Remove the linearly spaced contour lines on the criticality matrix and their "1" "2" "3" "4" "5" markers on the top of the plot.
8. Replace the contour lines with color-coded "Final Criticality" convex contour continuous shaded gradients, just like the 2024 UK Criticality Assessment's criticality plot (Fig. 5). These continuous colored gradients should be based on the Final Criticality scores.

### Code modifications to implement code refinement
| Original lines | Refined lines | Difference in code | Impact on generated results |
|---|---|---|---|
| (insert after 56) | 57–84 | Adds `DISASTER_COPING_CAPACITY = 'Disaster coping capacity'`, `INVERTED_SUPPLY_RISK_CATEGORIES = {MINING_CAPACITY}`, and a new function `supply_risk_indicators(refine_code)`. That function returns the original 10 categories, plus DCC as an 11th when `refine_code=True`. | With `refine_code=True`, the Supply Risk tables gain an 11th column, "Disaster coping capacity". With `False`, nothing changes. |
| 58–70 | 86–88 | The hard-coded `SUPPLY_RISK_INDICATORS = [...]` list is replaced by `SUPPLY_RISK_INDICATORS = supply_risk_indicators(False)`. | None. The list contents are identical; it is kept only for backward compatibility. |
| 87 | 105–106 | Adds a comment to `'Trade barriers': 100` and a new entry, `'Disaster Coping Capacity': 100`. | This is meant to divide DCC by 100, but it never does (see note 1 below). |
| 153–156 | 172–198 | The placeholder docstring `(1.) !!!!` / `(2.) !!!!` is replaced by a description of refinements (1)–(8). | None. This is documentation only. |
| 167, 181 | 210–212, 227 | Adds a new setting, `criticality_threshold: float \| None = 4.0`, with docs. | In refine mode, a labelled contour line at Final Criticality = 4.0 is drawn on the matrix. |
| 265–268 | 311–315 | `'ReporterDesc' in ...columns` becomes a case-insensitive lookup: `next((c for c in header if c.lower() == 'reporterdesc'), None)`. | This is the only change that can affect results when `refine_code=False`. A trade CSV whose column is spelled differently (e.g. `reporterDesc`) now gets the reporter check applied, where before it was silently skipped. |
| 534–536 | 581–594 | `trade_barriers(md, inputs)` becomes `trade_barriers(md, inputs, settings)`, using `column = 'KOFGI' if settings.refine_code else 'ETI 2016'`. A new function, `disaster_coping_capacity()`, computes the mix-weighted `DCC` score. | In refine mode, Trade barriers values come from the KOF Globalisation Index instead of ETI 2016, so that column's raw values and rankings change. DCC values are computed for the new column. |
| 663–674 | 720–736 | The inline lambda list is moved into a `supply_risk_functions` variable. It passes `settings` to `trade_barriers` and appends the DCC function when `refine_code` is on. The table now uses `supply_risk_indicators(settings.refine_code)`. | This wires the KOFGI and DCC changes into the raw Supply Risk table. |
| 702 | 764–780 | Adds a helper, `_resolve_targets()`, which issues a warning when a category has no target. `distance_to_target` gains a `refine_code` parameter. | A warning is printed if "Disaster coping capacity" has no row in the "Categories and targets" sheet. |
| 714 | 798–799 | The unit rescaling is now guarded: `if column in values.columns:`. | This prevents a crash when the DCC entry exists but the column doesn't (non-refine mode). |
| 716–721 | 801–819 | Mining-capacity-only inversion is generalised into `direct` and `inverted` lists. A missing target is filled with `values[column].mean()`. `score.mask(score < 0.8, 0)` now runs only `if not refine_code`. | In refine mode, two things change. First, DCC is scored as `(value / mean)²`, so it is relative to the other materials rather than an external benchmark. Second, the 0.8 floor is gone, so materials that were previously zeroed ("target met") keep their small positive scores, and the min-max spread changes. Mining capacity is unchanged. |
| 724–726 | 822–832 | `min_max(table)` becomes `min_max(table, low=0.0, high=1.0)`, computing `low + (high-low) * ...`. | In refine mode, all indicators are scaled to [1, 10] instead of [0, 1]. |
| — | 835–841 | Adds a new function, `geometric_mean()`, computing `table.prod(axis=1) ** (1/n)`. | This supports multiplicative aggregation in refine mode. |
| 729–734 | 844–854 | `add_totals` gains `refine_code` and `final_scale`. `Total` is computed as `geometric_mean(scaled) if refine_code else scaled.sum(axis=1)`, and `Scaled total` is rescaled to `final_scale`. | This is the biggest change to results. A geometric mean penalises imbalance less and lets no single indicator dominate additively, so material rankings can shift in every category. |
| 788, 795 (insert before 788) | 907–914, 916–917, 925–926 | Adds `final_criticality() = sqrt(SR × V)` and writes a `Final Criticality` column into `Scaled totals.csv` when refine mode is on and Vulnerability exists. | A new output column appears in import mode only. |
| 807, 809, 810 | 938–950 | Comments are updated, and three new constants are added: `CRITICALITY_COLORMAP='Reds'`, `CRITICALITY_BAND_WIDTH=0.5`, and `CRITICALITY_THRESHOLD_COLOR`. | These control the look of the refine-mode matrix. |
| 814 | 954 | Docstring wording only. | None. |
| (insert before 823) | 963–984 | Adds a new function, `_live_hotspot_labels()`, which flags the top 5 Social and top 5 Environmental materials as hotspots. | In refine mode, the hotspot colours come from computed results instead of the hand-edited `Hot Spots` column. |
| 823–838 | 986–1022 | `plot_criticality_matrix(settings)` becomes `plot_criticality_matrix(settings, final)`. In refine/import mode, it builds the plot data from live `final` results on the [1, 10] scale instead of reading `Result_total.csv`. Label offsets scale with `span`. | The refine-mode matrix plots the current run's scores directly, with no manual CSV step needed. |
| 841–843, 846–848 | 1025–1047 | The `k/x` iso-lines and the "1"–"5" zone labels are kept only in the `else` branch. Refine mode instead draws `contourf` bands of `sqrt(V × S)` with a colorbar and an optional threshold contour. | Refine mode shows a shaded, banded criticality gradient instead of 5 discrete zones. |
| 845, 850 | 1049, 1051–1053 | Scatter points get `zorder=10`. Labels become `"Material (Final Criticality)"`, with `fontsize=8` in refine mode. | Points and labels sit above the shading, and each label shows its score. |
| 855–856 | 1058–1059 | Axis limits change from fixed `(-0.05, 1.05)` to `(low - 0.05*span, high + 0.05*span)`. | Axes span roughly 0.55–10.45 in refine mode. |
| 872, 875 | 1075–1084 | Docstring updated. The console banner changes from "(known issues corrected)" to list the refinements. | Printed text only. |
| 879–882 | 1089–1095 | `indicator_low, indicator_high` are set to (1, 10) in refine mode, and these plus `refine_code` are passed into `distance_to_target` and `min_max`. | Applies the [1, 10] scaling and the no-floor rule to all categories. |
| 888 | 1101–1105 | Supply Risk and Vulnerability `Scaled total` are scaled to [1, 10] in refine mode. Social and Environmental stay on [0, 1]. | In the output CSVs, Supply Risk and Vulnerability scores are on 1–10 while Social and Environmental remain on 0–1, so they are no longer directly comparable across categories. |
| 894 | 1111 | `plot_criticality_matrix(settings)` becomes `plot_criticality_matrix(settings, final)`. | Gives the plot access to the live results. |

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
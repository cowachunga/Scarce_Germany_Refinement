#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 15:51:38 2021

@author: sylvia
"""
import os

import pandas as pd
import numpy as np
import copy

import matplotlib.pyplot as plt

# os.chdir('Desktop/Work/Scarce_Germany_Refinement/Python')

# %%Import data

# =============================================================================
# Create a list of the materials included into the criticality assessment
# =============================================================================

# Create the list with the studied materials
list_of_materials = [
    'Aluminium',
    'Antimony',
    'Bismuth',
    'Cadmium',
    'Chromium',
    'Coal',
    'Cobalt',
    'Copper',
    'Crude oils',
    'Gold',
    'Graphite',
    'Indium',
    'Iron',
    'Lead',
    'Lignite',
    'Lithium',
    'Magnesium',
    'Manganese',
    'Molybdenum',
    'Natural gas',
    'Nickel',
    'Niobium',
    'Phosphorus',
    'Platinum',
    'Rare earths',
    'Selenium',
    'Silver',
    'Strontium',
    'Tantalum',
    'Titanium',
    'Tungsten',
    'Uranium',
    'Vanadium',
    'Zinc',
    'Zirconium'
]

# =============================================================================
# Define generic functions
# =============================================================================

nan_value = float('Nan')


def replace_nan(dataframe):  # Replace the Nan values with 0
    if nan_value:
        dataframe = dataframe.replace(
            nan_value, '0',
            inplace=True
        )
    return dataframe


def drop_all_nans(dataframe):  # Drop the columns containing all Nans
    dataframe = dataframe.dropna(
        how='all',
        inplace=True)
    return dataframe


def drop_any_nans(dataframe):  # Drop the columns containing any Nans
    dataframe = dataframe.dropna(
        how='any',
        inplace=True)
    return dataframe


# =============================================================================
# Create the import data dataframes
# =============================================================================

# Import the import CSV file
data_all = pd.read_csv('Supporting files/Comtrade_all_2020.csv', index_col='Commodity')
data = data_all[['Period', 'PartnerDesc', 'PartnerISO', 'NetWgt']]

# Combine the netweight of the different countries within the same material category
data = (data.groupby(['Period', 'PartnerDesc', 'Commodity', 'PartnerISO'], sort=False).
        agg(Netweight=('NetWgt', 'sum'))).reset_index()

data = data.set_index('Commodity')

# Get unique instances from data_new.index
materials = data.index.unique()

# Loop through all materials and save the results in a dictionary
material_imports = {}  # Create an empty dictionary

for material in materials:
    material_imports[material] = data[
        (data.index == material)
    ].reset_index()

imports = []  # Create an empty list

# Define functions to adapt the Comtrade file
for key in material_imports:
    imports.append(material_imports[key])


def unit_change(dataframe):  # Change the unit from kg to t
    dataframe['Netweight'] = dataframe['Netweight'].div(1000)
    return dataframe


def add_percentage(dataframe):  # Add percentage column (to calculate the shares of imports)
    dataframe['Percentage'] = dataframe['Netweight'] / dataframe['Netweight'].iloc[0] * 100
    return dataframe


def change_name(dataframe):  # Change columns' names
    dataframe = dataframe.rename(
        columns={'PartnerDesc': 'Country',
                 'Netweight': 'Netweight (t)'}, inplace=True
    )
    return dataframe


# Apply the functions to the import dictionary
for i in imports:
    i = unit_change(i), add_percentage(i), change_name(i)  # Apply the functions

# =============================================================================
# Create the import data dictionary
# =============================================================================

dict_of_imports = {
    list_of_materials[0]: material_imports['Aluminium'],
    list_of_materials[1]: material_imports['Antimony'],
    list_of_materials[2]: material_imports['Bismuth'],
    list_of_materials[3]: material_imports['Cadmium'],
    list_of_materials[4]: material_imports['Chromium'],
    list_of_materials[5]: material_imports['Coal'],
    list_of_materials[6]: material_imports['Cobalt'],
    list_of_materials[7]: material_imports['Copper'],
    list_of_materials[8]: material_imports['Crude oils'],
    list_of_materials[9]: material_imports['Gold'],
    list_of_materials[10]: material_imports['Graphite'],
    list_of_materials[11]: material_imports['Indium'],
    list_of_materials[12]: material_imports['Iron'],
    list_of_materials[13]: material_imports['Lead'],
    list_of_materials[14]: material_imports['Lignite'],
    list_of_materials[15]: material_imports['Lithium'],
    list_of_materials[16]: material_imports['Magnesium'],
    list_of_materials[17]: material_imports['Manganese'],
    list_of_materials[18]: material_imports['Molybdenum'],
    list_of_materials[19]: material_imports['Natural gas'],
    list_of_materials[20]: material_imports['Nickel'],
    list_of_materials[21]: material_imports['Niobium'],
    list_of_materials[22]: material_imports['Phosphorus'],
    list_of_materials[23]: material_imports['Platinum'],
    list_of_materials[24]: material_imports['Rare earths'],
    list_of_materials[25]: material_imports['Selenium'],
    list_of_materials[26]: material_imports['Silver'],
    list_of_materials[27]: material_imports['Strontium'],
    list_of_materials[28]: material_imports['Tantalum'],
    list_of_materials[29]: material_imports['Titanium'],
    list_of_materials[30]: material_imports['Tungsten'],
    list_of_materials[31]: material_imports['Uranium'],
    list_of_materials[32]: material_imports['Vanadium'],
    list_of_materials[33]: material_imports['Zinc'],
    list_of_materials[34]: material_imports['Zirconium']
}

# %%Production data

# =============================================================================
# Create the production data dictionary
# =============================================================================

##Read the Excel file with the production data, iterate over each Excel sheet and appends it to a dictionary
dict_of_production = pd.read_excel('Supporting files/Production 2019 2020.xlsx',
                                   sheet_name=None)


# Define the percentage calculation function
def add_percent(dataframe):
    dataframe['Percent'] = (
                                   dataframe[dataframe.columns[-1]] / (
                               dataframe[dataframe.columns[-1]].iloc[-1]
                           )) * 100  # Add percentage row (the shares of the producing countries)


# Apply the function to calculate the percentage and add the new column
for key, i in dict_of_production.items():
    i.set_index('Country', inplace=True)  # Set the index to "Country"
    i = add_percent(i)  # Add the percentage column to rach dataframe in the dictionary

# %%Reserves data

# =============================================================================
# Create the reserves data dictionary
# =============================================================================

# Read the Excel file with the reserves data, iterate over each Excel sheet and appends it to a dictionary
dict_of_reserves = pd.read_excel('Supporting files/Reserves 2020.xlsx',
                                 sheet_name=None)

# Apply the function to calculate the percentage and add the new column
for key, i in dict_of_reserves.items():
    i.set_index('Country', inplace=True)  # Set the index to "Country"
    i = add_percent(i)  # Add the percentage column to rach dataframe in the dictionary

# %%Indicators data

# ===========================================================================
# Upload the indicator files
# =============================================================================

# Read the Excel file with the idicators data, iterate over each Excel sheet and appends it to a separate dictionary
dict_of_indicators = pd.read_excel(
    'Supporting files/Indicators.xlsx',
    sheet_name=None)

indicators_by_countries = (
    dict_of_indicators['Indicators by country']
).set_index('Country')

indicators_by_materials = (
    dict_of_indicators['Indicators by materials']
).set_index('Commodity')

all_occurrence_of_coproduction = (
    dict_of_indicators['Occurrence of co-production']
).set_index('Qualitative criteria')
all_occurrence_of_coproduction = all_occurrence_of_coproduction.reset_index()
all_occurrence_of_coproduction.set_index('Commodity', inplace=True)

SSM = dict_of_indicators['SSM']

value_added = (
    dict_of_indicators['Value added']
).set_index('Industry')

targets_categories = (
    dict_of_indicators['Categories and targets']
).set_index('Categories')

# %%Indicator calculation

############## SUPPLY RISK ################

############## CONCENTRATION OF RESERVES ################

dict_concentration_of_reserves = {}
dict_concentration_of_reserves = copy.deepcopy(dict_of_reserves)

for key, i in dict_concentration_of_reserves.items():
    i.drop(i.index[-1], axis=0, inplace=True)  # Delete the last row of the dataframe
    i['S2'] = i['Percent'] ** 2
    i.loc['Result'] = pd.Series(
        i['S2'].sum(), index=['S2']
    )  # Add "the Result" row

############## CONCENTRATION OF PRODUCTION ################

dict_concentration_of_production = {}
dict_concentration_of_production = copy.deepcopy(dict_of_production)

for key, i in dict_concentration_of_production.items():
    i['S2'] = i['Percent'] ** 2
    i.loc['Result'] = pd.Series(
        i['S2'].sum(), index=['S2']
    )  # Add "the Result" row

############## FEASIBILITY OF EXPLORATION PROJECT 2017 ################

# Import data - PPI 2016
PPI = pd.DataFrame(indicators_by_countries['PPI 2020'])
PPI['100-PPI'] = 99.07 - PPI['PPI 2020']  # Normalize the PPI by subtracting it from 100

dict_of_feasibility = {}

for material in list_of_materials:
    dict_of_feasibility[material] = pd.merge(
        dict_of_production[material],
        dict_of_reserves[material],
        on=['Country'],
        how='right'
    )

for key, i in dict_of_feasibility.items():
    i.dropna(
        how='any',
        inplace=True
    )
    i['Reserves*100-PPI'] = PPI['100-PPI'] * i['Percent_x']
    i.loc['Result'] = pd.Series(
        i['Reserves*100-PPI'].sum(), index=['Reserves*100-PPI']
    )  # Add "the Result" row

############## POLITICAL STABILITY 2017 ################

# Import data - WGI 2016 average indicator
# (!!!for SCARCE, could we not scale it, compare the results of scaled
# and not scaled indicator!!!)
WGI = pd.DataFrame(indicators_by_countries['WGI 2020'])

dict_political_stability = {}
dict_political_stability = copy.deepcopy(dict_of_production)

for key, i in dict_political_stability.items():
    i['Production*WGI'] = WGI['WGI 2020'] * i['Percent']
    i.reset_index(inplace=True)
    i.loc['Result'] = pd.Series(
        i['Production*WGI'].sum(),
        index=['Production*WGI']
    )  # Add "the Result" row

############## MINING CAPACITY 2016/2017 ################

dict_mining_capacity = {}
dict_mining_capacity = copy.deepcopy(dict_of_reserves)

for key, i in dict_mining_capacity.items():
    i['Production*(Reserves/Production)'] = (
            dict_of_production[key]['Percent']
            * (dict_of_reserves[key]['Reserves'].
               astype(int) / dict_of_production[key].iloc[:, 4].
               astype(int)) / 100
    )
    i['Production*(Reserves/Production)'].replace(np.inf, 0, inplace=True)
    i.loc['Result'] = pd.Series(
        i['Production*(Reserves/Production)'].sum(),
        index=['Production*(Reserves/Production)']
    )  # Add "the Result" row

############## TRADE BARRIERS 2016/2017 ################

# Import data - ETI 2016
ETI = pd.DataFrame(indicators_by_countries['ETI 2016'])

dict_trade_barriers = {}
dict_trade_barriers = copy.deepcopy(dict_of_production)

for key, i in dict_trade_barriers.items():
    i['Production*ETI'] = ETI['ETI 2016'] * i['Percent']  # Multiply the ETI and the imported percentage
    i.reset_index(inplace=True)
    i.loc['Result'] = pd.Series(
        i['Production*ETI'].sum(),
        index=['Production*ETI']
    )  # Add "the Result" row

############## DEMAND GROWTH ################

dict_demand_growth = {}
dict_demand_growth = copy.deepcopy(dict_of_production)

for key, i in dict_demand_growth.items():
    i.reset_index(inplace=True)
    i = dict_demand_growth[key].set_index(
        'Country').T.rename_axis(None, axis=1).rename_axis('Year').reset_index()
    i = i.loc[0:4, ['Year', 'Total']].sort_index(ascending=False)
    i.reset_index(drop=True)
    dict_demand_growth[key] = i

for key, i in dict_demand_growth.items():
    i['Yearly Change'] = i['Total'].astype(int).diff(periods=-1)
    i['YoY Growth'] = (
                              i.iloc[0:4, 2].
                              astype(float) / i.iloc[0:4, 1].
                              astype(float)) * 100
    i.loc['Result'] = pd.Series(
        i['YoY Growth'].mean(),
        index=['YoY Growth']
    )  # Add a row with the average of the 5 years production changes in %
    i.loc['Result'] = i[['YoY Growth']].iloc[-1] / 100
    i['YoY Growth'] = i['YoY Growth'].apply(lambda x: x if x > 0 else 0)

############## PRICE FLUCTUATION ################

# Load the volatility sheet
volatility_index = pd.DataFrame(indicators_by_materials['Volatility index (%) 2020'])

dict_price_fluctuation = {
    list_of_materials[0]: volatility_index.
    filter(regex='Aluminium', axis=0).
    reset_index(),
    list_of_materials[1]: volatility_index.
    filter(regex='Antimony', axis=0).
    reset_index(),
    list_of_materials[2]: volatility_index.
    filter(regex='Bismuth', axis=0).
    reset_index(),
    list_of_materials[3]: volatility_index.
    filter(regex='Cadmium', axis=0).
    reset_index(),
    list_of_materials[4]: volatility_index.
    filter(regex='Chromium', axis=0).
    reset_index(),
    list_of_materials[5]: volatility_index.
    filter(regex='Coal', axis=0).
    reset_index(),
    list_of_materials[6]: volatility_index.
    filter(regex='Cobalt', axis=0).
    reset_index(),
    list_of_materials[7]: volatility_index.
    filter(regex='Copper', axis=0).
    reset_index(),
    list_of_materials[8]: volatility_index.
    filter(regex='Crude oils', axis=0).
    reset_index(),
    list_of_materials[9]: volatility_index.
    filter(regex='Gold', axis=0).
    reset_index(),
    list_of_materials[10]: volatility_index.
    filter(regex='Graphite', axis=0).
    reset_index(),
    list_of_materials[11]: volatility_index.
    filter(regex='Indium', axis=0).
    reset_index(),
    list_of_materials[12]: volatility_index.
    filter(regex='Iron', axis=0).
    reset_index(),
    list_of_materials[13]: volatility_index.
    filter(regex='Lead', axis=0).
    reset_index(),
    list_of_materials[14]: volatility_index.
    filter(regex='Lignite', axis=0).
    reset_index(),
    list_of_materials[15]: volatility_index.
    filter(regex='Lithium', axis=0).
    reset_index(),
    list_of_materials[16]: volatility_index.
    filter(regex='Magnesium', axis=0).
    reset_index(),
    list_of_materials[17]: volatility_index.
    filter(regex='Manganese', axis=0).
    reset_index(),
    list_of_materials[18]: volatility_index.
    filter(regex='Molybdenum', axis=0).
    reset_index(),
    list_of_materials[19]: volatility_index.
    filter(regex='Natural gas', axis=0).
    reset_index(),
    list_of_materials[20]: volatility_index.
    filter(regex='Nickel', axis=0).
    reset_index(),
    list_of_materials[21]: volatility_index.
    filter(regex='Niobium', axis=0).
    reset_index(),
    list_of_materials[22]: volatility_index.
    filter(regex='Phosphorus', axis=0).
    reset_index(),
    list_of_materials[23]: volatility_index.
    filter(regex='Platinum', axis=0).
    reset_index(),
    list_of_materials[24]: volatility_index.
    filter(regex='Rare earths', axis=0).
    reset_index(),
    list_of_materials[25]: volatility_index.
    filter(regex='Selenium', axis=0).
    reset_index(),
    list_of_materials[26]: volatility_index.
    filter(regex='Silver', axis=0).
    reset_index(),
    list_of_materials[27]: volatility_index.
    filter(regex='Strontium', axis=0).
    reset_index(),
    list_of_materials[28]: volatility_index.
    filter(regex='Tantalum', axis=0).
    reset_index(),
    list_of_materials[29]: volatility_index.
    filter(regex='Titanium', axis=0).
    reset_index(),
    list_of_materials[30]: volatility_index.
    filter(regex='Tungsten', axis=0).
    reset_index(),
    list_of_materials[31]: volatility_index.
    filter(regex='Uranium', axis=0).
    reset_index(),
    list_of_materials[32]: volatility_index.
    filter(regex='Vanadium', axis=0).
    reset_index(),
    list_of_materials[33]: volatility_index.
    filter(regex='Zinc', axis=0).
    reset_index(),
    list_of_materials[34]: volatility_index.
    filter(regex='Zirconium', axis=0).
    reset_index()
}

for key, i in dict_price_fluctuation.items():
    i.loc['Result'] = pd.Series(
        i['Volatility index (%) 2020'].sum(),
        index=['Volatility index (%) 2020']
    )

############## PRIMARY MATERIAL USE ################

all_recycled_content = pd.DataFrame(
    indicators_by_materials['Primary material use (%)']
)

dict_primary_material_use = {
    list_of_materials[0]: all_recycled_content.
    filter(regex='Aluminium', axis=0).reset_index(),
    list_of_materials[1]: all_recycled_content.
    filter(regex='Antimony', axis=0).reset_index(),
    list_of_materials[2]: all_recycled_content.
    filter(regex='Bismuth', axis=0).reset_index(),
    list_of_materials[3]: all_recycled_content.
    filter(regex='Cadmium', axis=0).reset_index(),
    list_of_materials[4]: all_recycled_content.
    filter(regex='Chromium', axis=0).reset_index(),
    list_of_materials[5]: all_recycled_content.
    filter(regex='Coal', axis=0).reset_index(),
    list_of_materials[6]: all_recycled_content.
    filter(regex='Cobalt', axis=0).reset_index(),
    list_of_materials[7]: all_recycled_content.
    filter(regex='Copper', axis=0).reset_index(),
    list_of_materials[8]: all_recycled_content.
    filter(regex='Crude oils', axis=0).reset_index(),
    list_of_materials[9]: all_recycled_content.
    filter(regex='Gold', axis=0).reset_index(),
    list_of_materials[10]: all_recycled_content.
    filter(regex='Graphite', axis=0).reset_index(),
    list_of_materials[11]: all_recycled_content.
    filter(regex='Indium', axis=0).reset_index(),
    list_of_materials[12]: all_recycled_content.
    filter(regex='Iron', axis=0).reset_index(),
    list_of_materials[13]: all_recycled_content.
    filter(regex='Lead', axis=0).reset_index(),
    list_of_materials[14]: all_recycled_content.
    filter(regex='Lignite', axis=0).reset_index(),
    list_of_materials[15]: all_recycled_content.
    filter(regex='Lithium', axis=0).reset_index(),
    list_of_materials[16]: all_recycled_content.
    filter(regex='Magnesium', axis=0).reset_index(),
    list_of_materials[17]: all_recycled_content.
    filter(regex='Manganese', axis=0).reset_index(),
    list_of_materials[18]: all_recycled_content.
    filter(regex='Molybdenum', axis=0).reset_index(),
    list_of_materials[19]: all_recycled_content.
    filter(regex='Natural gas', axis=0).reset_index(),
    list_of_materials[20]: all_recycled_content.
    filter(regex='Nickel', axis=0).reset_index(),
    list_of_materials[21]: all_recycled_content.
    filter(regex='Niobium', axis=0).reset_index(),
    list_of_materials[22]: all_recycled_content.
    filter(regex='Phosphorus', axis=0).reset_index(),
    list_of_materials[23]: all_recycled_content.
    filter(regex='Platinum', axis=0).reset_index(),
    list_of_materials[24]: all_recycled_content.
    filter(regex='Rare earths', axis=0).reset_index(),
    list_of_materials[25]: all_recycled_content.
    filter(regex='Selenium', axis=0).reset_index(),
    list_of_materials[26]: all_recycled_content.
    filter(regex='Silver', axis=0).reset_index(),
    list_of_materials[27]: all_recycled_content.
    filter(regex='Strontium', axis=0).reset_index(),
    list_of_materials[28]: all_recycled_content.
    filter(regex='Tantalum', axis=0).reset_index(),
    list_of_materials[29]: all_recycled_content.
    filter(regex='Titanium', axis=0).reset_index(),
    list_of_materials[30]: all_recycled_content.
    filter(regex='Tungsten', axis=0).reset_index(),
    list_of_materials[31]: all_recycled_content.
    filter(regex='Uranium', axis=0).reset_index(),
    list_of_materials[32]: all_recycled_content.
    filter(regex='Vanadium', axis=0).reset_index(),
    list_of_materials[33]: all_recycled_content.
    filter(regex='Zinc', axis=0).reset_index(),
    list_of_materials[34]: all_recycled_content.
    filter(regex='Zirconium', axis=0).reset_index()
}

for key, i in dict_primary_material_use.items():
    i.loc['Result'] = pd.Series(
        i['Primary material use (%)'].sum(),
        index=['Primary material use (%)']
    )

############## OCCURRENCE OF CO-PRODUCTION ################

dict_occurrence_of_coproduction = {
    list_of_materials[0]: all_occurrence_of_coproduction.
    filter(regex='Aluminium', axis=0).reset_index(),
    list_of_materials[1]: all_occurrence_of_coproduction.
    filter(regex='Antimony', axis=0).reset_index(),
    list_of_materials[2]: all_occurrence_of_coproduction.
    filter(regex='Bismuth', axis=0).reset_index(),
    list_of_materials[3]: all_occurrence_of_coproduction.
    filter(regex='Cadmium', axis=0).reset_index(),
    list_of_materials[4]: all_occurrence_of_coproduction.
    filter(regex='Chromium', axis=0).reset_index(),
    list_of_materials[5]: all_occurrence_of_coproduction.
    filter(regex='Coal', axis=0).reset_index(),
    list_of_materials[6]: all_occurrence_of_coproduction.
    filter(regex='Cobalt', axis=0).reset_index(),
    list_of_materials[7]: all_occurrence_of_coproduction.
    filter(regex='Copper', axis=0).reset_index(),
    list_of_materials[8]: all_occurrence_of_coproduction.
    filter(regex='Crude oils', axis=0).reset_index(),
    list_of_materials[9]: all_occurrence_of_coproduction.
    filter(regex='Gold', axis=0).reset_index(),
    list_of_materials[10]: all_occurrence_of_coproduction.
    filter(regex='Graphite', axis=0).reset_index(),
    list_of_materials[11]: all_occurrence_of_coproduction.
    filter(regex='Indium', axis=0).reset_index(),
    list_of_materials[12]: all_occurrence_of_coproduction.
    filter(regex='Iron', axis=0).reset_index(),
    list_of_materials[13]: all_occurrence_of_coproduction.
    filter(regex='Lead', axis=0).reset_index(),
    list_of_materials[14]: all_occurrence_of_coproduction.
    filter(regex='Lignite', axis=0).reset_index(),
    list_of_materials[15]: all_occurrence_of_coproduction.
    filter(regex='Lithium', axis=0).reset_index(),
    list_of_materials[16]: all_occurrence_of_coproduction.
    filter(regex='Magnesium', axis=0).reset_index(),
    list_of_materials[17]: all_occurrence_of_coproduction.
    filter(regex='Manganese', axis=0).reset_index(),
    list_of_materials[18]: all_occurrence_of_coproduction.
    filter(regex='Molybdenum', axis=0).reset_index(),
    list_of_materials[19]: all_occurrence_of_coproduction.
    filter(regex='Natural gas', axis=0).reset_index(),
    list_of_materials[20]: all_occurrence_of_coproduction.
    filter(regex='Nickel', axis=0).reset_index(),
    list_of_materials[21]: all_occurrence_of_coproduction.
    filter(regex='Niobium', axis=0).reset_index(),
    list_of_materials[22]: all_occurrence_of_coproduction.
    filter(regex='Phosphorus', axis=0).reset_index(),
    list_of_materials[23]: all_occurrence_of_coproduction.
    filter(regex='Platinum', axis=0).reset_index(),
    list_of_materials[24]: all_occurrence_of_coproduction.
    filter(regex='Rare earths', axis=0).reset_index(),
    list_of_materials[25]: all_occurrence_of_coproduction.
    filter(regex='Selenium', axis=0).reset_index(),
    list_of_materials[26]: all_occurrence_of_coproduction.
    filter(regex='Silver', axis=0).reset_index(),
    list_of_materials[27]: all_occurrence_of_coproduction.
    filter(regex='Strontium', axis=0).reset_index(),
    list_of_materials[28]: all_occurrence_of_coproduction.
    filter(regex='Tantalum', axis=0).reset_index(),
    list_of_materials[29]: all_occurrence_of_coproduction.
    filter(regex='Titanium', axis=0).reset_index(),
    list_of_materials[30]: all_occurrence_of_coproduction.
    filter(regex='Tungsten', axis=0).reset_index(),
    list_of_materials[31]: all_occurrence_of_coproduction.
    filter(regex='Uranium', axis=0).reset_index(),
    list_of_materials[32]: all_occurrence_of_coproduction.
    filter(regex='Vanadium', axis=0).reset_index(),
    list_of_materials[33]: all_occurrence_of_coproduction.
    filter(regex='Zinc', axis=0).reset_index(),
    list_of_materials[34]: all_occurrence_of_coproduction.
    filter(regex='Zirconium', axis=0).reset_index()
}

for key, i in dict_occurrence_of_coproduction.items():
    i.loc['Result'] = pd.Series(
        i['Quantitative indicator'].sum(),
        index=['Quantitative indicator']
    )

############## VULNERABILITY ################

############## ECONOMIC IMPORTANCE ################

aluminium_economic_importance = pd.DataFrame()
aluminium_economic_importance['Value added'] = (
    value_added.loc[['Beverages, tobacco and feed',
                     'Electrical machinery, equipment and supplies',
                     'Transportation equipment',
                     'Production machinery'],
    'Value added']
)
aluminium_economic_importance['Shares'] = [11, 16, 43, 2]

antimony_economic_importance = pd.DataFrame()
antimony_economic_importance['Value added'] = (
    value_added.loc[['Chemical and allied products',
                     'Electronic parts, devices and electronic circuits',
                     'Fabricated metal products',
                     'Chemical and allied products',
                     'Non-ferrous metals and products'],
    'Value added']
)
antimony_economic_importance['Shares'] = [40, 32, 14, 10, 4]

bismuth_economic_importance = pd.DataFrame()
bismuth_economic_importance['Value added'] = (
    value_added.loc[['Chemical and allied products',
                     'Iron and steel',
                     'Non-ferrous metals and products'],
    'Value added']
)
bismuth_economic_importance['Shares'] = [62, 10, 28]

chromium_economic_importance = pd.DataFrame()
chromium_economic_importance['Value added'] = (
    value_added.loc[['Fabricated metal products',
                     'Business oriented machinery',
                     'Electronic parts, devices and electronic circuits'],
    'Value added']
)
chromium_economic_importance['Shares'] = [25, 25, 5]

cadmium_economic_importance = pd.DataFrame()
cadmium_economic_importance['Value added'] = (
    value_added.loc[['Electrical machinery, equipment and supplies',
                     'Chemical and allied products'],
    'Value added']
)
cadmium_economic_importance['Shares'] = [99, 1]

coal_economic_importance = pd.DataFrame()
coal_economic_importance['Value added'] = (
    value_added.loc[['Petroleum and coal products'],
    'Value added']
)
coal_economic_importance['Shares'] = [100]

cobalt_economic_importance = pd.DataFrame()
cobalt_economic_importance['Value added'] = (
    value_added.loc[['Electrical machinery, equipment and supplies',
                     'Iron and steel', 'Ceramic, stone and clay products',
                     'Rubber products'],
    'Value added']
)
cobalt_economic_importance['Shares'] = [80, 4, 5, 4]

copper_economic_importance = pd.DataFrame()
copper_economic_importance['Value added'] = (
    value_added.loc[['Electrical machinery, equipment and supplies',
                     'Information and communication electronics equipment',
                     'Transportation equipment'],
    'Value added']
)
copper_economic_importance['Shares'] = [35, 5, 10]

crude_oils_economic_importance = pd.DataFrame()
crude_oils_economic_importance['Value added'] = (
    value_added.loc[['Textile mill products',
                     'Chemical and allied products',
                     'Petroleum and coal products'],
    'Value added']
)
crude_oils_economic_importance['Shares'] = [15, 11, 63]

gold_economic_importance = pd.DataFrame()
gold_economic_importance['Value added'] = (
    value_added.loc[['Electronic parts, devices and electronic circuits',
                     'Fabricated metal products'],
    'Value added']
)
gold_economic_importance['Shares'] = [11, 83]

graphite_economic_importance = pd.DataFrame()
graphite_economic_importance['Value added'] = (
    value_added.loc[['Fabricated metal products',
                     'Non-ferrous metals and products',
                     'Electronic parts, devices and electronic circuits',
                     'General-purpose machinery'],
    'Value added']
)
graphite_economic_importance['Shares'] = [38, 51, 6, 1]

indium_economic_importance = pd.DataFrame()
indium_economic_importance['Value added'] = (
    value_added.loc[['Electronic parts, devices and electronic circuits',
                     'Chemical and allied products'],
    'Value added']
)
indium_economic_importance['Shares'] = [80, 20]

iron_economic_importance = pd.DataFrame()
iron_economic_importance['Value added'] = (
    value_added.loc[['Fabricated metal products',
                     'Transportation equipment',
                     'Electrical machinery, equipment and supplies',
                     'Production machinery'],
    'Value added']
)
iron_economic_importance['Shares'] = [22, 30, 8, 5]

lead_economic_importance = pd.DataFrame()
lead_economic_importance['Value added'] = (
    value_added.loc[['Electronic parts, devices and electronic circuits',
                     'Chemical and allied products',
                     'Fabricated metal products'],
    'Value added']
)
lead_economic_importance['Shares'] = [85, 6, 9]

lignite_economic_importance = pd.DataFrame()
lignite_economic_importance['Value added'] = (
    value_added.loc[['Electrical machinery, equipment and supplies'],
    'Value added']
)
lignite_economic_importance['Shares'] = [86]

lithium_economic_importance = pd.DataFrame()
lithium_economic_importance['Value added'] = (
    value_added.loc[['Electrical machinery, equipment and supplies',
                     'Ceramic, stone and clay products',
                     'Chemical and allied products'],
    'Value added']
)
lithium_economic_importance['Shares'] = [71, 14, 6]

magnesium_economic_importance = pd.DataFrame()
magnesium_economic_importance['Value added'] = (
    value_added.loc[['Chemical and allied products',
                     'Iron and steel'],
    'Value added']
)
magnesium_economic_importance['Shares'] = [70, 10]

manganese_economic_importance = pd.DataFrame()
manganese_economic_importance['Value added'] = (
    value_added.loc[['Transportation equipment',
                     'Fabricated metal products',
                     'General-purpose machinery'],
    'Value added']
)
manganese_economic_importance['Shares'] = [14, 12, 11]

molybdenum_economic_importance = pd.DataFrame()
molybdenum_economic_importance['Value added'] = (
    value_added.loc[['Iron and steel',
                     'Chemical and allied products',
                     'Electrical machinery, equipment and supplies'],
    'Value added']
)
molybdenum_economic_importance['Shares'] = [90, 6, 2]

natural_gas_economic_importance = pd.DataFrame()
natural_gas_economic_importance['Value added'] = (
    value_added.loc[['Petroleum and coal products'],
    'Value added']
)
natural_gas_economic_importance['Shares'] = [100]

nickel_economic_importance = pd.DataFrame()
nickel_economic_importance['Value added'] = (
    value_added.loc[['Production machinery',
                     'Electronic parts, devices and electronic circuits',
                     'Transportation equipment'],
    'Value added']
)
nickel_economic_importance['Shares'] = [31, 33, 19]

niobium_economic_importance = pd.DataFrame()
niobium_economic_importance['Value added'] = (
    value_added.loc[['Fabricated metal products',
                     'Transportation equipment',
                     'Chemical and allied products',
                     'Iron and steel',
                     'Petroleum and coal products'],
    'Value added']
)
niobium_economic_importance['Shares'] = [29, 24, 5, 10, 24]

phosphorus_economic_importance = pd.DataFrame()
phosphorus_economic_importance['Value added'] = (
    value_added.loc[['Food',
                     'Chemical and allied products'],
    'Value added']
)
phosphorus_economic_importance['Shares'] = [70, 18]

platinum_economic_importance = pd.DataFrame()
platinum_economic_importance['Value added'] = (
    value_added.loc[['Transportation equipment',
                     'Chemical and allied products',
                     'Electronic parts, devices and electronic circuits'],
    'Value added']
)
platinum_economic_importance['Shares'] = [38, 13, 10]

rare_earths_economic_importance = pd.DataFrame()
rare_earths_economic_importance['Value added'] = (
    value_added.loc[['Electronic parts, devices and electronic circuits',
                     'Chemical and allied products',
                     'Iron and steel'],
    'Value added']
)
rare_earths_economic_importance['Shares'] = [45, 13, 16]

selenium_economic_importance = pd.DataFrame()
selenium_economic_importance['Value added'] = (
    value_added.loc[['Ceramic, stone and clay products',
                     'Chemical and allied products'],
    'Value added']
)
selenium_economic_importance['Shares'] = [40, 6]

silver_economic_importance = pd.DataFrame()
silver_economic_importance['Value added'] = (
    value_added.loc[['Chemical and allied products',
                     'Transportation equipment',
                     'General-purpose machinery',
                     'Electronic parts, devices and electronic circuits',
                     'Non-ferrous metals and products'],
    'Value added']
)
silver_economic_importance['Shares'] = [18, 13, 7, 13, 6]

strontium_economic_importance = pd.DataFrame()
strontium_economic_importance['Value added'] = (
    value_added.loc[['Chemical and allied products',
                     'Electronic parts, devices and electronic circuits',
                     'Fabricated metal products'],
    'Value added']
)
strontium_economic_importance['Shares'] = [1, 75, 0.2]

tantalum_economic_importance = pd.DataFrame()
tantalum_economic_importance['Value added'] = (
    value_added.loc[['Electronic parts, devices and electronic circuits',
                     'General-purpose machinery',
                     'Chemical and allied products'],
    'Value added']
)
tantalum_economic_importance['Shares'] = [48, 11, 16]

titanium_economic_importance = pd.DataFrame()
titanium_economic_importance['Value added'] = (
    value_added.loc[['Chemical and allied products'],
    'Value added']
)
titanium_economic_importance['Shares'] = [72]

tungsten_economic_importance = pd.DataFrame()
tungsten_economic_importance['Value added'] = (
    value_added.loc[['Production machinery',
                     'Chemical and allied products',
                     'Electronic parts, devices and electronic circuits',
                     'Fabricated metal products'],
    'Value added']
)
tungsten_economic_importance['Shares'] = [74, 7, 6, 7]

uranium_economic_importance = pd.DataFrame()
uranium_economic_importance['Value added'] = (
    value_added.loc[['General-purpose machinery'],
    'Value added']
)
uranium_economic_importance['Shares'] = [50]

vanadium_economic_importance = pd.DataFrame()
vanadium_economic_importance['Value added'] = (
    value_added.loc[['Iron and steel',
                     'Chemical and allied products'],
    'Value added']
)
vanadium_economic_importance['Shares'] = [98, 2]

zinc_economic_importance = pd.DataFrame()
zinc_economic_importance['Value added'] = (
    value_added.loc[['Fabricated metal products',
                     'Chemical and allied products',
                     'Electronic parts, devices and electronic circuits'],
    'Value added']
)
zinc_economic_importance['Shares'] = [85, 5, 10]

zirconium_economic_importance = pd.DataFrame()
zirconium_economic_importance['Value added'] = (
    value_added.loc[['Non-ferrous metals and products',
                     'Chemical and allied products',
                     'Ceramic, stone and clay products'],
    'Value added']
)
zirconium_economic_importance['Shares'] = [36, 35, 15]

dict_economic_importance = {
    list_of_materials[0]: aluminium_economic_importance,
    list_of_materials[1]: antimony_economic_importance,
    list_of_materials[2]: bismuth_economic_importance,
    list_of_materials[3]: cadmium_economic_importance,
    list_of_materials[4]: chromium_economic_importance,
    list_of_materials[5]: coal_economic_importance,
    list_of_materials[6]: cobalt_economic_importance,
    list_of_materials[7]: copper_economic_importance,
    list_of_materials[8]: crude_oils_economic_importance,
    list_of_materials[9]: gold_economic_importance,
    list_of_materials[10]: graphite_economic_importance,
    list_of_materials[11]: indium_economic_importance,
    list_of_materials[12]: iron_economic_importance,
    list_of_materials[13]: lead_economic_importance,
    list_of_materials[14]: lignite_economic_importance,
    list_of_materials[15]: lithium_economic_importance,
    list_of_materials[16]: magnesium_economic_importance,
    list_of_materials[17]: manganese_economic_importance,
    list_of_materials[18]: molybdenum_economic_importance,
    list_of_materials[19]: natural_gas_economic_importance,
    list_of_materials[20]: nickel_economic_importance,
    list_of_materials[21]: niobium_economic_importance,
    list_of_materials[22]: phosphorus_economic_importance,
    list_of_materials[23]: platinum_economic_importance,
    list_of_materials[24]: rare_earths_economic_importance,
    list_of_materials[25]: selenium_economic_importance,
    list_of_materials[26]: silver_economic_importance,
    list_of_materials[27]: strontium_economic_importance,
    list_of_materials[28]: tantalum_economic_importance,
    list_of_materials[29]: titanium_economic_importance,
    list_of_materials[30]: tungsten_economic_importance,
    list_of_materials[31]: uranium_economic_importance,
    list_of_materials[32]: vanadium_economic_importance,
    list_of_materials[33]: zinc_economic_importance,
    list_of_materials[34]: zirconium_economic_importance
}

for key, i in dict_economic_importance.items():
    i['(Shares*Value added)/total value added'] = (
                                                          i['Shares'] * i['Value added']) / \
                                                  value_added['Value added'].iloc[-1]
    i.loc['Result'] = pd.Series(
        i['(Shares*Value added)/total value added'].sum(),
        index=['(Shares*Value added)/total value added']
    )

print('For Economic importance! The method needs to be updated')

############## DOMESTICALLY REQUIRED DEMAND ################

dict_domestically_required_demand = {}
dict_domestically_required_demand = copy.deepcopy(dict_of_imports)

for key, i in dict_domestically_required_demand.items():
    i.drop(i.columns[2:4], axis=1, inplace=True)
    i.drop(i.columns[3], axis=1, inplace=True)
    i.drop(i.index[1:], axis=0, inplace=True)
    i.loc['Result'] = pd.Series(
        i['Netweight (t)'].sum(),
        index=['Netweight (t)']
    )

############## SHARE OF GLOBAL PRODUCTION ################

dict_share_of_global_production = {}
dict_share_of_global_production = copy.deepcopy(dict_of_production)

for key, i in dict_share_of_global_production.items():
    i.drop(i.index[:-1], axis=0, inplace=True)
    i.reset_index(inplace=True, drop=True)
    i['Demand/Global production'] = (
            dict_domestically_required_demand[key]['Netweight (t)'].
            astype(float) / i.iloc[:, 4].astype(float))
    i.drop(i.columns.difference(['Demand/Global production']),
           axis=1, inplace=True)

############## DEPENDENCY ON IMPORTS ################

# Select only the Japan import data
dict_dependency_on_imports = {}
dict_dependency_on_imports = copy.deepcopy(dict_of_production)

for key, i in dict_dependency_on_imports.items():
    i.reset_index(inplace=True)
    i = dict_dependency_on_imports[key][dict_dependency_on_imports[key]['Country'].
    str.match('Japan')].reset_index(drop=True)
    dict_dependency_on_imports[key] = i

for key, i in dict_dependency_on_imports.items():
    i = i.drop('Percent', axis=1, inplace=True)

for key, i in dict_dependency_on_imports.items():
    i['Dependency on import'] = 1 - (
            [dict_dependency_on_imports[key].columns[-1]] /
            dict_of_imports[key]['Netweight (t)'].iloc[0].astype(float)
    )

############## SUBSTITUTABILITY AND UTILIZATION OF FUTURE TECHNOLOGIES ################

substitutability_and_future_technologies = pd.DataFrame(
    indicators_by_materials['Substitutability']
)
substitutability_and_future_technologies['Future technologies'] = (
    indicators_by_materials['Future technologies']
)

dict_substitutability = {
    list_of_materials[0]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Aluminium', axis=0).reset_index(),
    list_of_materials[1]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Antimony', axis=0).reset_index(),
    list_of_materials[2]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Bismuth', axis=0).reset_index(),
    list_of_materials[3]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Cadmium', axis=0).reset_index(),
    list_of_materials[4]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Chromium', axis=0).reset_index(),
    list_of_materials[5]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Coal', axis=0).reset_index(),
    list_of_materials[6]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Cobalt', axis=0).reset_index(),
    list_of_materials[7]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Copper', axis=0).reset_index(),
    list_of_materials[8]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Crude oils', axis=0).reset_index(),
    list_of_materials[9]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Gold', axis=0).reset_index(),
    list_of_materials[10]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Graphite', axis=0).reset_index(),
    list_of_materials[11]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Indium', axis=0).reset_index(),
    list_of_materials[12]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Iron', axis=0).reset_index(),
    list_of_materials[13]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Lead', axis=0).reset_index(),
    list_of_materials[14]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Lignite', axis=0).reset_index(),
    list_of_materials[15]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Lithium', axis=0).reset_index(),
    list_of_materials[16]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Magnesium', axis=0).reset_index(),
    list_of_materials[17]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Manganese', axis=0).reset_index(),
    list_of_materials[18]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Molybdenum', axis=0).reset_index(),
    list_of_materials[19]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Natural gas', axis=0).reset_index(),
    list_of_materials[20]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Nickel', axis=0).reset_index(),
    list_of_materials[21]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Niobium', axis=0).reset_index(),
    list_of_materials[22]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Phosphorus', axis=0).reset_index(),
    list_of_materials[23]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Platinum', axis=0).reset_index(),
    list_of_materials[24]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Rare earths', axis=0).reset_index(),
    list_of_materials[25]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Selenium', axis=0).reset_index(),
    list_of_materials[26]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Silver', axis=0).reset_index(),
    list_of_materials[27]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Strontium', axis=0).reset_index(),
    list_of_materials[28]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Tantalum', axis=0).reset_index(),
    list_of_materials[29]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Titanium', axis=0).reset_index(),
    list_of_materials[30]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Tungsten', axis=0).reset_index(),
    list_of_materials[31]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Uranium', axis=0).reset_index(),
    list_of_materials[32]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Vanadium', axis=0).reset_index(),
    list_of_materials[33]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Zinc', axis=0).reset_index(),
    list_of_materials[34]: substitutability_and_future_technologies['Substitutability'].
    filter(regex='Zirconium', axis=0).reset_index()
}

for key, i in dict_substitutability.items():
    i.loc['Result'] = pd.Series(
        i['Substitutability'].sum(),
        index=['Substitutability']
    )

dict_future_technologies = {
    list_of_materials[0]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Aluminium', axis=0).reset_index(),
    list_of_materials[1]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Antimony', axis=0).reset_index(),
    list_of_materials[2]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Bismuth', axis=0).reset_index(),
    list_of_materials[3]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Cadmium', axis=0).reset_index(),
    list_of_materials[4]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Chromium', axis=0).reset_index(),
    list_of_materials[5]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Coal', axis=0).reset_index(),
    list_of_materials[6]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Cobalt', axis=0).reset_index(),
    list_of_materials[7]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Copper', axis=0).reset_index(),
    list_of_materials[8]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Crude oils', axis=0).reset_index(),
    list_of_materials[9]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Gold', axis=0).reset_index(),
    list_of_materials[10]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Graphite', axis=0).reset_index(),
    list_of_materials[11]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Indium', axis=0).reset_index(),
    list_of_materials[12]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Iron', axis=0).reset_index(),
    list_of_materials[13]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Lead', axis=0).reset_index(),
    list_of_materials[14]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Lignite', axis=0).reset_index(),
    list_of_materials[15]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Lithium', axis=0).reset_index(),
    list_of_materials[16]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Magnesium', axis=0).reset_index(),
    list_of_materials[17]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Manganese', axis=0).reset_index(),
    list_of_materials[18]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Molybdenum', axis=0).reset_index(),
    list_of_materials[19]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Natural gas', axis=0).reset_index(),
    list_of_materials[20]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Nickel', axis=0).reset_index(),
    list_of_materials[21]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Niobium', axis=0).reset_index(),
    list_of_materials[22]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Phosphorus', axis=0).reset_index(),
    list_of_materials[23]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Platinum', axis=0).reset_index(),
    list_of_materials[24]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Rare earths', axis=0).reset_index(),
    list_of_materials[25]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Selenium', axis=0).reset_index(),
    list_of_materials[26]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Silver', axis=0).reset_index(),
    list_of_materials[27]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Strontium', axis=0).reset_index(),
    list_of_materials[28]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Tantalum', axis=0).reset_index(),
    list_of_materials[29]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Titanium', axis=0).reset_index(),
    list_of_materials[30]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Tungsten', axis=0).reset_index(),
    list_of_materials[31]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Uranium', axis=0).reset_index(),
    list_of_materials[32]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Vanadium', axis=0).reset_index(),
    list_of_materials[33]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Zinc', axis=0).reset_index(),
    list_of_materials[34]: substitutability_and_future_technologies['Future technologies'].
    filter(regex='Zirconium', axis=0).reset_index()}

for key, i in dict_future_technologies.items():
    i.loc['Result'] = pd.Series(
        i['Future technologies'].sum(),
        index=['Future technologies']
    )

############## COMPLIANCE WITH SOCIAL STANDARDS ################

############## SMALL SCALE MINING ################

dict_small_scale_mining = dict(tuple(SSM.groupby('Commodity')))
for key, i in dict_small_scale_mining.items():
    i = i.set_index(['Commodity']).stack().reset_index()
    i.rename(columns={'level_1': 'Country', 0: 'SSM'}, inplace=True)
    i.set_index('Country', inplace=True, drop=True)
    i['Production*SSM'] = dict_of_production[key]['Percent'] * i['SSM']
    i.loc['Result'] = pd.Series(i['Production*SSM'].sum(), index=['Production*SSM'])
    dict_small_scale_mining[key] = i

############## GEOPOLITICAL RISK ################

GPI = pd.DataFrame(indicators_by_countries['GPI 2020'])
GI = pd.DataFrame(indicators_by_countries['GI 2020'])

dict_geopolitical_risk = {}
dict_geopolitical_risk = copy.deepcopy(dict_of_production)

for key, i in dict_geopolitical_risk.items():
    i['Production*(GI+GPI)^2'] = i['Percent'] * (GPI['GPI 2020'] + GI['GI 2020']) ** 2
    i.reset_index(inplace=True)
    i.loc['Result'] = pd.Series(i['Production*(GI+GPI)^2'].sum(), index=['Production*(GI+GPI)^2'])

############## HUMAN RIGHT ABUSE ################

HRA = pd.DataFrame(indicators_by_countries['Human right abuse scaled'])

dict_human_right_abuse = {}
dict_human_right_abuse = copy.deepcopy(dict_of_production)

for key, i in dict_human_right_abuse.items():
    i['Production*HRA'] = i['Percent'] * (HRA['Human right abuse scaled']) ** 2
    i.reset_index(inplace=True)
    i.loc['Result'] = pd.Series(i['Production*HRA'].sum(), index=['Production*HRA'])
    # Add "the Result" row

############## COMPLIANCE WITH ENVIRONMENTAL STANDARDS ################

############## WATER SCARCITY ################

WDI = pd.DataFrame(indicators_by_countries['WDI'])

dict_water_scarcity = {}
dict_water_scarcity = copy.deepcopy(dict_of_production)

for key, i in dict_water_scarcity.items():
    i['Production*Water_scarcity'] = i['Percent'] * (WDI['WDI']) ** 2
    i.reset_index(inplace=True)
    i.loc['Result'] = pd.Series(
        i['Production*Water_scarcity'].sum(),
        index=['Production*Water_scarcity']
    )  # Add "the Result" row

############## CLIMATE CHANGE ################

climate_change = pd.DataFrame(indicators_by_materials['Climate change'])
dict_climate_change = dict(tuple(climate_change.groupby('Commodity')))

for key, i in dict_climate_change.items():
    i.reset_index(inplace=True, drop=True)
    i.loc['Result'] = pd.Series(
        i['Climate change'].sum(),
        index=['Climate change']
    )  # Add "the Result" row

############## SENSITIVITY OF LOCAL BIODIVERSITY ################

biodiversity_indicator = pd.DataFrame(indicators_by_countries['Biodiversity'])

dict_sensitivity_local_biodiversity = {}
dict_sensitivity_local_biodiversity = copy.deepcopy(dict_of_production)

for key, i in dict_sensitivity_local_biodiversity.items():
    i['Production*Biodiversity'] = (
            i['Percent'] * (biodiversity_indicator['Biodiversity']) ** 2
    )
    i.reset_index(inplace=True)
    i.loc['Result'] = pd.Series(
        i['Production*Biodiversity'].sum(),
        index=['Production*Biodiversity']
    )  # Add "the Result" row

# %%Results collection (for categories)

############## RESULTS ################

############## SUPPLY RISK ################

list_concentration_of_production = []  # Create an empty list
for key in dict_concentration_of_production:
    list_concentration_of_production.append(
        dict_concentration_of_production[key]['S2'].iloc[-1]
    )
list_concentration_of_production = dict(zip(
    list_of_materials,
    list_concentration_of_production)
)

list_concentration_of_reserves = []  # Create an empty list
for key in dict_concentration_of_reserves:
    list_concentration_of_reserves.append(
        dict_concentration_of_reserves[key]['S2'].iloc[-1]
    )
list_concentration_of_reserves = dict(zip(
    list_of_materials,
    list_concentration_of_reserves)
)

list_feasibility = []  # Create an empty list
for key in dict_of_feasibility:
    list_feasibility.append(
        dict_of_feasibility[key]['Reserves*100-PPI'].iloc[-1]
    )
list_feasibility = dict(zip(
    list_of_materials,
    list_feasibility)
)

list_political_stability = []  # Create an empty list
for key in dict_political_stability:
    list_political_stability.append(
        dict_political_stability[key]['Production*WGI'].iloc[-1]
    )
list_political_stability = dict(zip(
    list_of_materials,
    list_political_stability)
)

list_mining_capacity = []  # Create an empty list
for key in dict_mining_capacity:
    list_mining_capacity.append(
        dict_mining_capacity[key]['Production*(Reserves/Production)'].iloc[-1]
    )
list_mining_capacity = dict(zip(
    list_of_materials,
    list_mining_capacity)
)

list_trade_barriers = []  # Create an empty list
for key in dict_trade_barriers:
    list_trade_barriers.append(
        dict_trade_barriers[key]['Production*ETI'].iloc[-1]
    )
list_trade_barriers = dict(zip(
    list_of_materials, list_trade_barriers)
)

list_demand_growth = []  # Create an empty list
for key in dict_demand_growth:
    list_demand_growth.append(
        dict_demand_growth[key]['YoY Growth'].iloc[-1]
    )
list_demand_growth = dict(zip(
    list_of_materials,
    list_demand_growth)
)

list_price_fluctuation = []  # Create an empty list
for key in dict_price_fluctuation:
    list_price_fluctuation.append(
        dict_price_fluctuation[key]['Volatility index (%) 2020'].iloc[-1]
    )
list_price_fluctuation = dict(zip(
    list_of_materials,
    list_price_fluctuation)
)

list_primary_material_use = []  # Create an empty list
for key in dict_primary_material_use:
    list_primary_material_use.append(
        dict_primary_material_use[key]['Primary material use (%)'].iloc[-1]
    )
list_primary_material_use = dict(zip(
    list_of_materials,
    list_primary_material_use)
)

list_occurrence_of_coproduction = []  # Create an empty list
for key in dict_occurrence_of_coproduction:
    list_occurrence_of_coproduction.append(
        dict_occurrence_of_coproduction[key]['Quantitative indicator'].iloc[-1]
    )
list_occurrence_of_coproduction = dict(zip(
    list_of_materials,
    list_occurrence_of_coproduction)
)

list_total_supply_risk = [
    list_concentration_of_production,
    list_concentration_of_reserves,
    list_feasibility,
    list_political_stability,
    list_mining_capacity,
    list_trade_barriers,
    list_demand_growth,
    list_price_fluctuation,
    list_primary_material_use,
    list_occurrence_of_coproduction
]

supply_risk_list = [
    'Concentration of production',
    'Concentration of reserves',
    'Feasibility of exploration projects',
    'Political stability',
    'Mining capacity',
    'Trade barriers',
    'Demand growth',
    'Price fluctuation',
    'Primary material use',
    'Occurrence of co-production'
]

dict_supply_risk = dict(zip(
    supply_risk_list,
    list_total_supply_risk)
)

supply_risk = pd.DataFrame(
    dict_supply_risk.values(),
    index=supply_risk_list
)

# Further scaling (if needed)

supply_risk.loc['Concentration of reserves'] = (
        supply_risk.loc['Concentration of reserves', :] / 10000
)
supply_risk.loc['Concentration of production'] = (
        supply_risk.loc['Concentration of production', :] / 10000
)
supply_risk.loc['Feasibility of exploration projects'] = (
        supply_risk.loc['Feasibility of exploration projects', :] / 100
)
supply_risk.loc['Political stability'] = (
        supply_risk.loc['Political stability', :] / 100
)
supply_risk.loc['Trade barriers'] = (
        supply_risk.loc['Trade barriers', :] / 100
)

############## COMPLIANCE WITH SOCIAL STANDARD ################

list_small_scale_mining = []  # Create an empty list
for key in dict_small_scale_mining:
    list_small_scale_mining.append(
        dict_small_scale_mining[key]['Production*SSM'].iloc[-1]
    )
list_small_scale_mining = dict(zip(
    list_of_materials, list_small_scale_mining)
)

list_geopolitical_risk = []  # Create an empty list
for key in dict_geopolitical_risk:
    list_geopolitical_risk.append(
        dict_geopolitical_risk[key]['Production*(GI+GPI)^2'].iloc[-1]
    )
list_geopolitical_risk = dict(zip(
    list_of_materials, list_geopolitical_risk)
)

list_human_right_abuse = []  # Create an empty list
for key in dict_human_right_abuse:
    list_human_right_abuse.append(
        dict_human_right_abuse[key]['Production*HRA'].iloc[-1]
    )
list_human_right_abuse = dict(zip(
    list_of_materials, list_human_right_abuse)
)

list_total_social_standard = [list_small_scale_mining,
                              list_geopolitical_risk,
                              list_human_right_abuse]

social_standard_list = ['Small scale mining', 'Geopolitical risk',
                        'Human right abuse']

dict_social_standard = dict(zip(
    social_standard_list,
    list_total_social_standard)
)

social_standard = pd.DataFrame(
    dict_social_standard.values(),
    index=social_standard_list).T

############## COMPLIANCE WITH ENVIRONMENTAL STANDARD ################

list_water_scarcity = []  # Create an empty list
for key in dict_water_scarcity:
    list_water_scarcity.append(
        dict_water_scarcity[key]['Production*Water_scarcity'].iloc[-1]
    )
list_water_scarcity = dict(zip(
    list_of_materials, list_water_scarcity)
)

list_climate_change = []  # Create an empty list
for key in dict_climate_change:
    list_climate_change.append(
        dict_climate_change[key]['Climate change'].iloc[-1]
    )
list_climate_change = dict(zip(
    list_of_materials, list_climate_change)
)

list_sensitivity_local_biodiversity = []  # Create an empty list
for key in dict_sensitivity_local_biodiversity:
    list_sensitivity_local_biodiversity.append(
        dict_sensitivity_local_biodiversity[key]['Production*Biodiversity'].iloc[-1]
    )
list_sensitivity_local_biodiversity = dict(zip(
    list_of_materials, list_sensitivity_local_biodiversity)
)

list_total_environmental_standard = [
    list_water_scarcity,
    list_climate_change,
    list_sensitivity_local_biodiversity
]

environmental_standard_list = [
    'Water scarcity',
    'Climate change',
    'Sensitivity of local biodiversity'
]

dict_environmental_standard = dict(zip(
    environmental_standard_list,
    list_total_environmental_standard))

environmental_standard = pd.DataFrame(
    dict_environmental_standard.values(),
    index=environmental_standard_list
).T

# %%Results scaling using the target values - calculating distance to target (only for supply risk)

supply_risk_scaled = copy.deepcopy(supply_risk).T

collist = [
    'Concentration of production',
    'Concentration of reserves',
    'Feasibility of exploration projects',
    'Political stability',
    'Trade barriers',
    'Demand growth',
    'Price fluctuation',
    'Primary material use',
    'Occurrence of co-production'
]

collist2 = [
    'Mining capacity'
]

targets_categories_nm = targets_categories.reset_index()
targets_categories_mc = targets_categories.reset_index()

targets_categories_nm = targets_categories_nm.loc[[0, 1, 2, 3, 5, 6, 7, 8, 9], 'Categories':'Target']
targets_categories_mc = targets_categories_mc.loc[[4], 'Categories':'Target']

targets_categories_nm = targets_categories_nm.set_index('Categories')
targets_categories_mc = targets_categories_mc.set_index('Categories')

supply_risk_scaled_nm = (supply_risk_scaled[collist] / targets_categories_nm.loc[:, 'Target']) ** 2
supply_risk_scaled_mc = ((targets_categories_mc.loc[:, 'Target'] / supply_risk_scaled[collist2]) ** 2).replace(np.inf,
                                                                                                               0)

supply_risk_scaled = pd.concat([supply_risk_scaled_mc, supply_risk_scaled], axis=1, ignore_index=True)

supply_risk_scaled_mc['Mining capacity'] = supply_risk_scaled_mc['Mining capacity'].astype(float)
supply_risk_scaled_nm['Mining capacity'] = supply_risk_scaled_mc['Mining capacity']

# Setting values to 0 (only for supply risk)
supply_risk_scaled_nm.values[supply_risk_scaled_nm < 0.8] = 0

# %%Performing Min-Max scaling (per indicator)

# Supply risk
supply_risk_scaled_final = (
                                   supply_risk_scaled_nm - supply_risk_scaled_nm.min()) / (
                                   supply_risk_scaled_nm.max() - supply_risk_scaled_nm.min())

# unscaled_supply_risk = (supply_risk - supply_risk.min())/(supply_risk.max() - supply_risk.min())

# Compliance with social standards

social_standard_final = (
                                social_standard - social_standard.min()) / (
                                social_standard.max() - social_standard.min())

# Compliance with environmental standards

environmental_standard_final = (
                                       environmental_standard - environmental_standard.min()) / (
                                       environmental_standard.max() - environmental_standard.min())

# %%Final indicator score (sum)

# all_categories_results_supply_risk_final['Total'] =
# all_categories_results_supply_risk_final.sum(axis=1)
# all_categories_results_vulnerability_final['Total'] =
# all_categories_results_vulnerability_final.sum(axis=1)

supply_risk_scaled_final_total = copy.deepcopy(supply_risk_scaled_final)
supply_risk_scaled_final_total['Total'] = supply_risk_scaled_final_total.sum(axis=1)
supply_risk_scaled_final_total['Scaled total'] = (
                                                         supply_risk_scaled_final_total['Total'] -
                                                         supply_risk_scaled_final_total['Total'].min()) / (
                                                         supply_risk_scaled_final_total['Total'].max() -
                                                         supply_risk_scaled_final_total['Total'].min())

social_standard_final_total = copy.deepcopy(social_standard_final)
social_standard_final_total['Total'] = social_standard_final.sum(axis=1)
social_standard_final_total['Scaled total'] = (
                                                      social_standard_final_total['Total'] -
                                                      social_standard_final_total['Total'].min()) / (
                                                      social_standard_final_total['Total'].max() -
                                                      social_standard_final_total['Total'].min())

environmental_standard_final_total = copy.deepcopy(environmental_standard_final)
environmental_standard_final_total['Total'] = environmental_standard_final.sum(axis=1)
environmental_standard_final_total['Scaled total'] = (
                                                             environmental_standard_final_total['Total'] -
                                                             environmental_standard_final_total['Total'].min()) / (
                                                             environmental_standard_final_total['Total'].max() -
                                                             environmental_standard_final_total['Total'].min())

# %%Export the results

outdir1 = '/home/jessica/PycharmProjects/Scarce_Germany_Refinement/Results/Supply risk'
if not os.path.exists(outdir1):
    os.mkdir(outdir1)

outdir3 = '/home/jessica/PycharmProjects/Scarce_Germany_Refinement/Results/Social standards'
if not os.path.exists(outdir3):
    os.mkdir(outdir3)

outdir4 = '/home/jessica/PycharmProjects/Scarce_Germany_Refinement/Results/Environmental standards'
if not os.path.exists(outdir4):
    os.mkdir(outdir4)

supply_risk_scaled_final.to_csv(
    '/home/jessica/PycharmProjects/Scarce_Germany_Refinement/Results/Supply risk/Supply risk scaled_global.csv', index=True
)
social_standard_final.to_csv(
    '/home/jessica/PycharmProjects/Scarce_Germany_Refinement/Results/Social standards/Compliance with social standards_global.csv',
    index=True
)
environmental_standard_final.to_csv(
    '/home/jessica/PycharmProjects/Scarce_Germany_Refinement/Results/Environmental standards/Compliance with environmental standards_global.csv',
    index=True
)

# %%Export the results with total column

supply_risk_scaled_final_total.to_csv(
    '/home/jessica/PycharmProjects/Scarce_Germany_Refinement/Results/Supply risk/Supply risk total_global.csv', index=True
)
social_standard_final_total.to_csv(
    '/home/jessica/PycharmProjects/Scarce_Germany_Refinement/Results/Social standards/Compliance with social standards total_global.csv',
    index=True
)
environmental_standard_final_total.to_csv(
    '/home/jessica/PycharmProjects/Scarce_Germany_Refinement/Results/Environmental standards/Compliance with environmental standards total_global.csv',
    index=True
)

# %%Plot

############## PLOT THE FIGURES ################

# Supply risk plot
# Sort the supply risk dataframe
supply_risk_scaled_final_total = supply_risk_scaled_final_total.sort_values(by='Total', ascending=False, inplace=False)
supply_risk_scaled_final_total = supply_risk_scaled_final_total.drop(columns='Total')
supply_risk_scaled_final_total = supply_risk_scaled_final_total.drop(columns='Scaled total')

# Draw the chart
supply_risk = supply_risk_scaled_final_total.reset_index().plot(
    figsize=(16, 10),
    x='index',
    kind='bar',
    grid=True,
    zorder=10,  # place the grids behind the bars
    stacked=True
)

# Additionally adjust the labels size and position
supply_risk.set_xlabel('Resources', fontsize=12)
supply_risk.set_ylabel('Supply risk', fontsize=12)
ha = 'right'  # adjust the position of the x-axis labels (resources' names)
supply_risk.set_xticklabels(supply_risk.get_xticklabels(), rotation=45, ha=ha)
supply_risk.legend(fontsize=12)

# Save the graph
supply_risk.get_figure().savefig('/home/jessica/PycharmProjects/Scarce_Germany_Refinement/Results/Sypply risk_global.png', dpi=300)

# Compliance with social standards plot
# Sort the compliance with social standards dataframe
social_standard_final_total = social_standard_final_total.sort_values(by='Total', ascending=False, inplace=False)
social_standard_final_total = social_standard_final_total.drop(columns='Total')
social_standard_final_total = social_standard_final_total.drop(columns='Scaled total')

# Draw the chart
social_standard = social_standard_final_total.reset_index().plot(
    figsize=(16, 10),
    x='index',
    kind='bar',
    grid=True,
    zorder=10,  # place the grids behind the bars
    stacked=True
)

# Additionally adjust the labels size and position
social_standard.set_xlabel('Resources', fontsize=12)
social_standard.set_ylabel('Compliance with social standards', fontsize=12)
ha = 'right'  # adjust the position of the x-axis labels (resources' names)
social_standard.set_xticklabels(social_standard.get_xticklabels(), rotation=45, ha=ha)
social_standard.legend(fontsize=12)

# Save the graph
social_standard.get_figure().savefig('/home/jessica/PycharmProjects/Scarce_Germany_Refinement/Results/Social standard_global.png', dpi=300)

# Compliance with environmental standards plot
# Sort the compliance with environmental standards dataframe
environmental_standard_final_total = environmental_standard_final_total.sort_values(by='Total', ascending=False,
                                                                                    inplace=False)
environmental_standard_final_total = environmental_standard_final_total.drop(columns='Total')
environmental_standard_final_total = environmental_standard_final_total.drop(columns='Scaled total')

# Draw the chart
environmental_standard = environmental_standard_final_total.reset_index().plot(
    figsize=(16, 10),
    x='index',
    kind='bar',
    grid=True,
    zorder=10,  # place the grids behind the bars
    stacked=True
)

# Additionally adjust the labels size and position
environmental_standard.set_xlabel('Resources', fontsize=12)
environmental_standard.set_ylabel('Compliance with environmental standards', fontsize=12)
ha = 'right'  # adjust the position of the x-axis labels (resources' names)
environmental_standard.set_xticklabels(environmental_standard.get_xticklabels(), rotation=45, ha=ha)
environmental_standard.legend(fontsize=12)

# Save the graph
environmental_standard.get_figure().savefig(
    '/home/jessica/PycharmProjects/Scarce_Germany_Refinement/Results/Environmental standard_global.png', dpi=300)

############## PLOT THE CRITICALITY MATRIX ################

results = pd.read_csv(
    '/home/jessica/PycharmProjects/Scarce_Germany_Refinement/Supporting files/Result_total_global.csv'
)


# =============================================================================
# Criticality functions
# =============================================================================

np.seterr(divide='ignore', invalid='ignore')

def low_crit(x):
    return 0.2 / x


def mid_crit(x):
    return 0.4 / x


def high_crit(x):
    return 0.6 / x


def highest_crit(x):
    return 0.8 / x


# =============================================================================
# Criticality lines
# =============================================================================

data_line_low_crit_x = np.arange(0.0, 2.0, 0.01)

data_line_low_crit_y = []

for i in data_line_low_crit_x:
    data_line_low_crit_y.append(low_crit(i))

data_line_mid_crit_x = np.arange(0.0, 2.0, 0.01)

data_line_mid_crit_y = []

for i in data_line_mid_crit_x:
    data_line_mid_crit_y.append(mid_crit(i))

data_line_high_crit_x = np.arange(0.0, 2.0, 0.01)

data_line_high_crit_y = []

for i in data_line_high_crit_x:
    data_line_high_crit_y.append(high_crit(i))

data_line_highest_crit_x = np.arange(0.0, 2.0, 0.01)

data_line_highest_crit_y = []

for i in data_line_highest_crit_x:
    data_line_highest_crit_y.append(highest_crit(i))

# =============================================================================
# Scatter plot data
# =============================================================================

# Group the social and environmental hot spots
x1 = results.loc[
    results['Hot Spots'] == 'Abiotic material that has neither an environmental nor a social hotspot', 'Vulnerability']
y1 = results.loc[
    results['Hot Spots'] == 'Abiotic material that has neither an environmental nor a social hotspot', 'Supply Risk']

x2 = results.loc[results['Hot Spots'] == 'Social', 'Vulnerability']
y2 = results.loc[results['Hot Spots'] == 'Social', 'Supply Risk']

x3 = results.loc[results['Hot Spots'] == 'Environmental', 'Vulnerability']
y3 = results.loc[results['Hot Spots'] == 'Environmental', 'Supply Risk']

x4 = results.loc[results['Hot Spots'] == 'Social and Environmental', 'Vulnerability']
y4 = results.loc[results['Hot Spots'] == 'Social and Environmental', 'Supply Risk']

# =============================================================================
# Plot
# =============================================================================

fig, ax = plt.subplots(
    figsize=(10, 10)
)

# Line plot - Low crit
ax.plot(
    data_line_low_crit_x,
    data_line_low_crit_y,
    color='#cccccc'
)

# Line plot - Mid crit
ax.plot(
    data_line_mid_crit_x,
    data_line_mid_crit_y,
    linewidth=1,
    color='#969696'
)

# Line plot - High crit
ax.plot(
    data_line_high_crit_x,
    data_line_high_crit_y,
    linewidth=1,
    color='#525252'
)

# Line plot - Highest crit
ax.plot(
    data_line_highest_crit_x,
    data_line_highest_crit_y,
    linewidth=1,
    color='#252525'
)

# Plot the data
ax.scatter(
    x1, y1, c='black',
    marker='.',
    s=70,
    label='Abiotic material that has neither an environmental nor a social hotspot'
)

ax.scatter(
    x2, y2, c='red',
    marker=',',
    s=30,
    label='Social'
)

ax.scatter(
    x3, y3, c='green',
    marker='^',
    s=40,
    label='Environmental'
)

ax.scatter(
    x4, y4, c='black',
    marker='^',
    s=40,
    label='Social and Environmental'
)

# =============================================================================
# Annotate
# =============================================================================

props = dict(
    boxstyle='round',
    facecolor='#ffffff',
)

ax.text(
    0.1, 0.925,  # x,y
    '1',
    fontsize=10,
    bbox=props,
    verticalalignment='center',
    horizontalalignment='center'
)

ax.text(
    0.3, 0.925,  # x,y
    '2',
    fontsize=10,
    bbox=props,
    verticalalignment='center',
    horizontalalignment='center'
)

ax.text(
    0.5, 0.925,  # x,y
    '3',
    fontsize=10,
    bbox=props,
    verticalalignment='center',
    horizontalalignment='center'
)

ax.text(
    0.7, 0.925,  # x,y
    '4',
    fontsize=10,
    bbox=props,
    verticalalignment='center',
    horizontalalignment='center'
)

ax.text(
    0.95, 0.925,  # x,y
    '5',
    fontsize=10,
    bbox=props,
    verticalalignment='center',
    horizontalalignment='center'
)

# Loop for annotation of all points - add the values labels
for i in range(len(results)):
    plt.annotate(
        results['Material'][i], (
            results['Vulnerability'][i],
            results['Supply Risk'][i] + 0.02),
        ha='right'
    )

# =============================================================================
# Last tweaks
# =============================================================================

# Some cosmetics
ax.set(
    xlabel='Vulnerability',
    ylabel='Supply Risk'
)

# Legend

plt.legend(
    loc="lower center",
    bbox_to_anchor=(
        0.5, -0.15
    ),
    frameon=False,
    ncol=4
)

# add grid - adjust if required
ax.grid()

# axes limits
ax.set_xlim(-0.05, 1.05)
ax.set_ylim(-0.05, 1.05)

# Save
fig.savefig('Matrix.png', dpi=450)
# fig.savefig("test.pdf")
# fig.savefig("test.svg")
plt.show()
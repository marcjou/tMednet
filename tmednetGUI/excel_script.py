import pandas as pd
import numpy as np

df_paper = pd.read_excel('../res/Comparacion datos paper y excel.xlsx', sheet_name='Paper')
df_paper.rename(columns={'Season_of_survey': 'EvenStart', 'Surveyed_site': 'Location',
                         'Surveyed_Lower_Depth': 'Mortality Lower Depth',
                         'Surveyed_Upper_Depth': 'Mortality Upper Depth', 'Taxon': 'Species',
                         'Percentage_of_affected_organisms': 'Damaged percentage',
                         'Severity_class' : 'Damaged qualitative'}, inplace=True)
df_BA = pd.read_excel('../res/data.xlsx', sheet_name=1)
merge_on = ['Year', 'EvenStart', 'Location', 'Mortality Lower Depth', 'Mortality Upper Depth', 'Species', 'Damaged percentage', 'Damaged qualitative']
df_merge = pd.merge(df_paper[merge_on], df_BA, on=merge_on, how='inner')
df_merge = df_merge[df_BA.columns]
df_merge.to_excel('output3.xlsx', index=False)
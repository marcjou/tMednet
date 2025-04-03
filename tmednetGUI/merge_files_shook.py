import pandas as pd


df_mortality = pd.read_excel(r'C:\Users\marcj\Documents\CSIC\OdM\Shook\OdMClimate Monitoring Mortality_Regions_V2.xlsx', sheet_name='Hoja1')
df_posidonia = pd.read_excel(r'C:\Users\marcj\Documents\CSIC\OdM\Shook\OdMClimate_FloracióPosidonia_Shook Version.xlsx')
df_visual = pd.read_excel(r'C:\Users\marcj\Documents\CSIC\OdM\Shook\OdMClimate Visual Census_Shook Version V3.xlsx')
df_medusas = pd.read_excel(r'C:\Users\marcj\Documents\CSIC\OdM\Shook\Indice de Medusas_Shook Version_V2.xlsx')
df_posidonia.rename(columns={'Lat': 'Latitude', 'Long': 'Longitude', 'Type':'Assessment'}, inplace=True)
df_medusas.rename(columns={'Condición total': 'Assessment'}, inplace=True)
df_mortality.rename(columns={'Level of mortality impact (Affected All)': 'Assessment'}, inplace=True)

dfs = {'Mortality': df_mortality, 'Visual Census': df_visual, 'Posidonia': df_posidonia, 'Medusas': df_medusas}


columnas_deseadas = ['Project', 'Project_Color', 'Latitude', 'Longitude', 'Assessment', 'Tropical. Index', 'Merid.zation index', 'Invasion index']

project_colors = {
    'Mortality': '#AC1520',
    'Visual Census': '#7A1841',
    'Posidonia': '#CFDE35',
    'Medusas': '#C53985'
}

# Concatenar directamente sin usar append
df_final = pd.concat(
    [df.assign(Project=name, Project_Color=project_colors[name]).reindex(columns=columnas_deseadas) for name, df in dfs.items()],
    ignore_index=True
)

df_final.to_excel(r'C:\Users\marcj\Documents\CSIC\OdM\Shook\final_V2.xlsx')
print('hey')


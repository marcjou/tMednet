import pandas as pd
import re

def check_center(df_centros, df_observers, df_lista):
    # Normalizar nombres eliminando espacios extra
    df_observers['Observer'] = df_observers['Observer'].str.split().str.join(' ')
    df_lista['Observer'] = df_lista['Observer'].str.split().str.join(' ')

    # Convertir nombres de centros y comments a minúsculas
    df_centros['Centro_lower'] = df_centros['Centro '].str.lower()
    df_observers['Comments_lower'] = df_observers['Comments'].fillna('').astype(str).str.lower()

    # Crear lista de centros y de nombres de Observer
    centros_list = df_centros['Centro_lower'].tolist()
    observers_list = df_lista['Observer'].tolist()

    # Función para encontrar el centro en los comentarios
    def encontrar_centro(comments):
        for centro in centros_list:
            # Expresión regular para buscar el centro exacto
            pattern = r'\b' + re.escape(centro) + r'\b'
            if re.search(pattern, comments):
                return centro
        return None

    # Función para encontrar Observers mencionados en Comments
    def encontrar_observers(comments):
        print(comments)
        encontrados = []
        for obs in observers_list:
            # Convertir a formato de búsqueda exacta
            pattern = r'\b' + re.escape(obs) + r'\b'
            if re.search(pattern, comments):
                encontrados.append(obs)

        return list(set(encontrados)) if encontrados else None

    # Aplicar la función de centros
    df_observers['Centro'] = df_observers['Comments_lower'].apply(encontrar_centro)

    # Aplicar la función de observadores
    df_observers['Observers_mencionados'] = df_observers['Comments_lower'].apply(encontrar_observers)

    # Crear df_resultado sin eliminar filas con Centro NaN
    df_resultado = df_observers[['Observer', 'Centro']]

    # Crear df_nuevos con los observadores mencionados en comentarios
    nuevos_observers = []
    for _, row in df_observers.iterrows():
        if row['Observers_mencionados']:
            for obs in row['Observers_mencionados']:
                nuevos_observers.append({'Observer': obs, 'Centro': row['Centro']})

    df_nuevos = pd.DataFrame(nuevos_observers)

    # Unir los datos sin eliminar observadores originales
    df_resultado = pd.concat([df_resultado, df_nuevos], ignore_index=True).drop_duplicates()

    # Hacer un merge con df_observers para garantizar que todos los observers estén presentes
    df_final = df_observers[['Observer']].merge(df_resultado, on='Observer', how='left')

    # Agregar "Tu mejor mail"
    df_final = df_final.merge(df_lista[['Observer', 'Tu mejor mail']], on='Observer', how='left')

    # Ordenar por cantidad de datos disponibles, priorizando las filas con más información
    df_final['Datos_completos'] = df_final[['Centro', 'Tu mejor mail']].notna().sum(axis=1)

    # Eliminar duplicados, quedándonos con la fila que tenga más datos
    df_final = df_final.sort_values(by='Datos_completos', ascending=False).drop_duplicates(subset=['Observer'],
                                                                                           keep='first')

    # Eliminar la columna auxiliar 'Datos_completos'
    df_final = df_final.drop(columns=['Datos_completos'])

    return df_final

df_mortality = pd.read_excel(r'C:\Users\marcj\Documents\CSIC\OdM\ODM Gala\OdMClimate RAW Data.xlsx', sheet_name='Monitoring Mortality')
df_visual_1 = pd.read_excel(r'C:\Users\marcj\Documents\CSIC\OdM\ODM Gala\OdMClimate RAW Data.xlsx', sheet_name='Visual Census - Validadas')
df_visual_2 = pd.read_excel(r'C:\Users\marcj\Documents\CSIC\OdM\ODM Gala\OdMClimate RAW Data.xlsx', sheet_name='Visual Census -No Validadas')
df_posidonia = pd.read_excel(r'C:\Users\marcj\Documents\CSIC\OdM\ODM Gala\OdMClimate RAW Data.xlsx', sheet_name='Praderas Marinas')
df_medusas = pd.read_excel(r'C:\Users\marcj\Documents\CSIC\OdM\ODM Gala\Jelly Raw.xlsx', sheet_name='Obs-protocolos medusa OdMClimat')
df_centros = pd.read_excel(r'C:\Users\marcj\Documents\CSIC\OdM\ODM Gala\Centros de Buceo.xlsx', sheet_name='Hoja1')

# Abre la lista de usuarios registrados
with open(r'C:\Users\marcj\Documents\CSIC\OdM\ODM Gala\Lista.csv', encoding='utf-8', errors='ignore') as f:
    df_lista = pd.read_csv(f, sep=',')
    df_lista['Observer'] = df_lista['Nombre']


# Ejecutar la función para cada df_observers
dofus_mortality = check_center(df_centros, df_mortality, df_lista)
dofus_visual = check_center(df_centros, pd.concat([df_visual_1, df_visual_2]), df_lista)
dofus_posidonia = check_center(df_centros, df_posidonia, df_lista)
dofus_medusas = check_center(df_centros, df_medusas, df_lista)

# Unir todos los dataframes en un único dataframe con todos los observers únicos
df_total = pd.concat([dofus_mortality, dofus_visual, dofus_posidonia, dofus_medusas], ignore_index=True).drop_duplicates(subset=['Observer'])

# Añadir las columnas de las categorías, marcando "Yes" si el observer estaba en cada df, "No" en caso contrario
df_total['mortality'] = df_total['Observer'].isin(dofus_mortality['Observer']).map({True: 'Yes', False: 'No'})
df_total['visual'] = df_total['Observer'].isin(dofus_visual['Observer']).map({True: 'Yes', False: 'No'})
df_total['posidonia'] = df_total['Observer'].isin(dofus_posidonia['Observer']).map({True: 'Yes', False: 'No'})
df_total['medusas'] = df_total['Observer'].isin(dofus_medusas['Observer']).map({True: 'Yes', False: 'No'})

df_total.to_excel(r'C:\Users\marcj\Documents\CSIC\OdM\ODM Gala\concursoV2.xlsx', index=False)



Observers = list(set(df_mortality['Observer'].unique().tolist() +df_visual_1['Observer'].unique().tolist() +df_visual_2['Observer'].unique().tolist() +df_posidonia['Observer'].unique().tolist() +df_medusas['Observer'].unique().tolist()))
Observers = list(set(df_lista['Nombre'].unique().tolist() + Observers))
df_final = pd.DataFrame(Observers, columns= ['Observer'])
df_final['Observer'] = df_final['Observer'].str.strip()
df_final.sort_values(by='Observer', ascending=True, inplace=True)
df_final = df_final[df_final['Observer'] != '']
df_final = df_final.drop_duplicates().reset_index(drop=True)
df_final.sort_values(by='Observer', ascending=True, inplace=True)
df_final.reset_index(drop=True, inplace=True)

import re
obs_in_mortality = [nombre for nombre in Observers if df_mortality['Comments'].str.contains(r'\b' + re.escape(nombre) + r'\b', case=False, na=False).any()]
obs_in_mortality = [nombre for nombre in obs_in_mortality if nombre.strip()]
obs_in_mortality = [nombre.strip() for nombre in obs_in_mortality if nombre.strip()]
pattern_mortality = r'\b(' + '|'.join(map(str, obs_in_mortality)) + r')\b'
centers_in_mortality = [nombre for nombre in df_centros['Centro '].str.strip() if df_mortality['Comments'].str.contains(r'\b' + re.escape(nombre) + r'\b', case=False, na=False).any()]

obs_in_visual = [nombre for nombre in Observers if pd.concat([df_visual_1['Comments'], df_visual_2['Comments']], ignore_index=True).str.contains(r'\b' + re.escape(nombre) + r'\b', case=False, na=False).any()]
obs_in_visual = [nombre for nombre in obs_in_visual if nombre.strip()]
obs_in_visual = [nombre.strip() for nombre in obs_in_visual if nombre.strip()]
pattern_visual = r'\b(' + '|'.join(map(str, obs_in_visual)) + r')\b'
centers_in_visual = [nombre for nombre in df_centros['Centro '].str.strip() if pd.concat([df_visual_1['Comments'], df_visual_2['Comments']], ignore_index=True).str.contains(r'\b' + re.escape(nombre) + r'\b', case=False, na=False).any()]

obs_in_posidonia = [nombre for nombre in Observers if df_posidonia['Comments'].str.contains(r'\b' + re.escape(nombre) + r'\b', case=False, na=False).any()]
obs_in_posidonia = [nombre for nombre in obs_in_posidonia if nombre.strip()]
obs_in_posidonia = [nombre.strip() for nombre in obs_in_posidonia if nombre.strip()]
pattern_posidonia = r'\b(' + '|'.join(map(str, obs_in_posidonia)) + r')\b'
centers_in_posidonia = [nombre for nombre in df_centros['Centro '].str.strip() if df_posidonia['Comments'].str.contains(r'\b' + re.escape(nombre) + r'\b', case=False, na=False).any()]

obs_in_medusas = [nombre for nombre in Observers if df_medusas['Comments'].str.contains(r'\b' + re.escape(nombre) + r'\b', case=False, na=False).any()]
obs_in_medusas = [nombre for nombre in obs_in_medusas if nombre.strip()]
obs_in_medusas = [nombre.strip() for nombre in obs_in_medusas if nombre.strip()]
pattern_medusas = r'\b(' + '|'.join(map(str, obs_in_medusas)) + r')\b'
centers_in_medusas = [nombre for nombre in df_centros['Centro '].str.strip() if df_medusas['Comments'].str.contains(r'\b' + re.escape(nombre) + r'\b', case=False, na=False).any()]


df_final['Monitoring Mortality'] = df_final['Observer'].isin(df_mortality['Observer'].str.strip().unique()).replace({True: 'Yes', False: 'No'} )
# Segunda condición: Si el comentario contiene un nombre de la lista, actualizar solo los 'No'
mask = df_final['Observer'].astype(str).str.contains(pattern_mortality, case=False, na=False)
mask = df_mortality['Observer'].str.contains('|'.join(obs_in_mortality), case=False, na=False)
df_final.loc[df_final['Monitoring Mortality'] == 'No', 'Monitoring Mortality'] = mask.replace({True: 'Yes', False: 'No'})



df_final['Visual Census'] = df_final['Observer'].isin(pd.concat([df_visual_1['Observer'].str.strip(), df_visual_2['Observer'].str.strip()], ignore_index=True).unique()).replace({True: 'Yes', False: 'No'} )
mask = df_final['Observer'].astype(str).str.contains(pattern_visual, case=False, na=False)
mask = pd.concat([df_visual_1['Observer'], df_visual_2['Observer']], ignore_index=True).str.contains('|'.join(obs_in_visual), case=False, na=False)
df_final.loc[df_final['Visual Census'] == 'No', 'Visual Census'] = mask.replace({True: 'Yes', False: 'No'})

df_final['Posidonia'] = df_final['Observer'].isin(df_posidonia['Observer'].str.strip().unique()).replace({True: 'Yes', False: 'No'} )
mask = df_final['Observer'].astype(str).str.contains(pattern_posidonia, case=False, na=False)
mask = df_posidonia['Observer'].str.contains('|'.join(obs_in_posidonia), case=False, na=False)
df_final.loc[df_final['Posidonia'] == 'No', 'Posidonia'] = mask.replace({True: 'Yes', False: 'No'})

df_final['Medusas'] = df_final['Observer'].isin(df_medusas['Observer'].str.strip().unique()).replace({True: 'Yes', False: 'No'} )
mask = df_final['Observer'].astype(str).str.contains(pattern_medusas, case=False, na=False)
mask = df_medusas['Observer'].str.contains('|'.join(obs_in_medusas), case=False, na=False)
df_final.loc[df_final['Medusas'] == 'No', 'Medusas'] = mask.replace({True: 'Yes', False: 'No'})

df_lista = df_lista.drop_duplicates(subset=['Observer'], keep='first').reset_index()

df_final = df_final.merge(df_lista[['Observer', 'Tu mejor mail']], on='Observer', how='left')
df_final.insert(1, 'Email', df_final.pop('Tu mejor mail'))

df_final[['Observer', 'Surnames']] = df_final['Observer'].str.split(n=1, expand=True)
col = df_final.pop('Surnames')
df_final.insert(1, 'Surnames', col)

df_final.to_excel(r'C:\Users\marcj\Documents\CSIC\OdM\ODM Gala\concurso.xlsx', index=False)
# TODO Check from df['Comments'] si alguna cadena coincide con la del archivo de registrados, así buscamos los nombres
print('stop')

#TODO seguir mejorando esto con la ayuda de chat_gpt



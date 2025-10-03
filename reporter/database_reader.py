import numpy as np
import pandas as pd
from zipfile import ZipFile
from os import listdir
from os.path import isfile, join

def calculate_percentile(df, cols, percentile_up, percentile_down):
    # Calculate the threshold according to the percentile
    thresholds_up = df[cols].quantile(percentile_up)
    thresholds_down = df[cols].quantile(percentile_down)

    # Returns the new df according to the threshold and type
    df_clean = df.copy()
    for col in cols:
        df_clean.loc[df_clean[col] > thresholds_up[col], col] = float("nan")
        df_clean.loc[df_clean[col] < thresholds_down[col], col] = float("nan")

    return df_clean


mega_dir_list = [f for f in listdir("../src/input_files/Subidos/") if isfile(join("../src/input_files/Subidos/", f))]

# Sets a dict to store all the DataBases insides the big ZIP file
dico_dfs_txt = {}

# Creates said dict by scraping the info inside the ZIP file
for zip_filename in mega_dir_list:
    zip_file = ZipFile("../src/input_files/Subidos/" + zip_filename)
    for file in zip_file.namelist():
        if file.endswith(".txt"):
            temp_df = pd.read_csv(zip_file.open(file), sep='\t')
            temp_df = calculate_percentile(temp_df, temp_df.columns[2:], 0.99, 0.01)
            dico_dfs_txt[file] = temp_df

dico_temps = {}
top_ten_max_temps = pd.DataFrame(columns=['Filename', 'MaxDate', 'Max'])
top_ten_min_temps = pd.DataFrame(columns=['Filename', 'MinDate', 'Min'])
# Search in each df for the highest and lowest temperature
for filename, df in dico_dfs_txt.items():
    dico_temps[filename] = {'max': float(df[df.columns[2:]].max().max()), 'min': float(df[df.columns[2:]].min().min())}

    # Searches and stores the max and min indexes
    temp_cols = df.columns[2:]
    max_row_idx = df[temp_cols].idxmax().max()
    min_row_idx = df[temp_cols].idxmin().min()

    # Searches and stores the max and min dates
    max_date = df.loc[max_row_idx, 'Date']
    min_date = df.loc[min_row_idx, 'Date']

    # Sets the Series containing the data for the given file
    max_series = pd.DataFrame([{'Filename': filename, 'MaxDate': max_date, 'Max': float(df[temp_cols].max().max())}])
    min_series = pd.DataFrame([{'Filename': filename, 'MinDate': min_date, 'Min': float(df[temp_cols].min().min())}])

    # Stores into the dfs only if they are inside the TOP10
    if len(top_ten_max_temps) < 10:
        top_ten_max_temps = pd.concat([top_ten_max_temps, max_series], ignore_index=True)
        top_ten_min_temps = pd.concat([top_ten_min_temps, min_series], ignore_index=True)
    elif float(df[temp_cols].max().max()) > top_ten_max_temps['Max'].min():
        top_ten_max_temps.drop(top_ten_max_temps['Max'].idxmin(), inplace = True)
        top_ten_max_temps = pd.concat([top_ten_max_temps, max_series], ignore_index=True)
    elif float(df[temp_cols].min().min()) < top_ten_min_temps['Min'].max():
        top_ten_min_temps.drop(top_ten_min_temps['Min'].idxmax(), inplace = True)
        top_ten_min_temps = pd.concat([top_ten_min_temps, min_series], ignore_index=True)

#TODO read reports to get ideas on new metrics
print('stop')
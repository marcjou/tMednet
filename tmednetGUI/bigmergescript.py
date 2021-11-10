import re
import numpy as np
import pandas as pd
from datetime import datetime

df1 = pd.read_csv("../src/input_files/Database_T_05_Cap de Creus-S_200705-201811.txt", '\t')
df2 = pd.read_csv("../src/output_files/merged.txt", sep="\s+", skiprows=6)
df2.index.set_names(["Date", "Time"], level=[0, 1], inplace=True)
df2.reset_index(inplace=True)

for i in range(len(df2["Date"])):
    df2.at[i, "Date"] = datetime.strftime(datetime.strptime(df2["Date"][i], "%Y-%m-%d"), "%d/%m/%Y")

dfconc = pd.concat([df1, df2])
dfconc.replace(np.nan, '', regex=True, inplace=True)

dfconc.to_csv('../src/output_files/mergedcompletedd.txt', sep='\t', index=False, float_format='%.3g')
'''
with open('../src/output_files/mergedcomplete.txt', 'w') as f:
    dfconc.to_string(f, col_space=10, index=False)
'''
print("me")
"""
with open("../src/input_files/Database_T_05_Cap de Creus-S_200705-201811.txt", "a") as file_object:
    f = open("../src/output_files/merged.txt", "r")
    lines = f.readlines()
    lines[:] = map(lambda item: re.sub('\t+', ' ', item.strip()).split(' '), lines)
    bad = lines[:8]
    goodlines = lines[9:]
    for line in goodlines:
        file_object.write("\n" + str(line))
    f.close()

"""
import re
import pandas as pd
from datetime import datetime

df1 = pd.read_csv("../src/input_files/Database_T_05_Cap de Creus-S_200705-201811.txt", '\t')
df2 = pd.read_csv("../src/output_files/merged.txt", sep="\s+", skiprows=6)
df2.index.set_names(["Date", "Hour"], level=[0,1], inplace=True)
df2.reset_index(inplace=True)

for i in range(len(df2["Date"])):
    df2.at[i, "Date"] = datetime.strftime(datetime.strptime(df2["Date"][i], "%Y-%m-%d"), "%d/%m/%Y")

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
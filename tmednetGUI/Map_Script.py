import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cf

df = pd.read_csv("../Participant TMEDNet.txt", sep="\t")
BBox = [df.LNG.min() - 1,   df.LNG.max() + 1, df.LAT.min() - 1, df.LAT.max() + 1]

ax = plt.axes(projection=ccrs.Mercator())
ax.set_extent(BBox, crs=ccrs.PlateCarree())
ax.add_feature(cf.OCEAN)
ax.add_feature(cf.LAND)
ax.coastlines(resolution='10m')
ax.add_feature(cf.BORDERS, linestyle=':', alpha=1)

colors = {'Research center' : '#c94b24', 'Private company':'#f7cb39', 'Environmental agency':'#86c716',
       'Managing authority':'#3749e6', 'NGO':'#f74fc5', np.nan:'black'}

ugh = ax.scatter(df.LNG, df.LAT, zorder=1, alpha=0.8, c=df['Category aggregate'].map(colors).values, s=10, transform=ccrs.PlateCarree())
#ax.legend(df["Category aggregate"].unique())

#ax.set_xlim(BBox[0],BBox[1])
#ax.set_ylim(BBox[2],BBox[3])
#ax.imshow(ruh_m, zorder=0, extent=BBox, aspect= 'equal')
plt.savefig('../cosas2.png')
print('hola')
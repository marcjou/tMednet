from datetime import datetime
import re


f = open('../src/10_20181116-11_20200602-08_allm/copia.txt', 'r')
datos = {"timegmt": [], "time": [], "temp": [], "S/N": "", "GMT": "",
                     "depth": 'X', "region": 'X',
                     "datainici": 'X',
                     "datafin": 'X'}

a = f.readlines()
f.close()
# We clean and separate values that contain "Enregistré"
a[:] = map(lambda item: re.sub('\t+', ' ', item.strip()).split(' '), a)
bad = []
for i in range(len(a)):
    if a[i][-1] == "Enregistré":
        bad.append(i)
nl = len(a) - len(bad) + 1
datos["timegmt"] = [datetime.strptime(a[i][1] + ' ' + a[i][2], "%d/%m/%y %H:%M:%S") for i in
                    range(1, nl)]
datos["temp"] = [float(a[i][3]) for i in range(1, nl)]
igm = '_'.join(a[0]).find("GMT")
gmtout = '_'.join(a[0])[igm + 3:igm + 6]
datos['GMT'] = gmtout
datos['S/N'] = a[0][a[0].index('S/N:') + 1]

print(datos)

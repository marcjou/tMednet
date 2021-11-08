import re


f = open('/home/marc/PycharmProjects/MedNet/src/ullastres/150_20210720-13_20211010-11_05.txt', "r")
good = f.readlines()
good[:] = map(lambda item: re.sub('\t+', ' ', item.strip()).split(' '), good)
f.close()

f = open('/home/marc/PycharmProjects/MedNet/src/ullastres/150_20210720-13_20211010-11_30.txt', "r")
tobeChanged = f.readlines()
tobeChanged[:] = map(lambda item: re.sub('\t+', ' ', item.strip()).split(' '), tobeChanged)
f.close()

for i in range(len(good)):
    if i > 0 and i < len(tobeChanged):
        tobeChanged[i][1] = good[i][1]
        tobeChanged[i][2] = good[i][2]

with open("/home/marc/PycharmProjects/MedNet/src/ullastres/150_20210720-13_20211010-11_30.txt", "w") as txt_file:
    for line in tobeChanged:
        txt_file.write(" ".join(line) + "\n")


print(tobeChanged[5])
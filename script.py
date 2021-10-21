import re


f = open('/home/marc/PycharmProjects/MedNet/src/Medes/masarchivos/6_20210724-12_20211019-11_05.txt', "r")
good = f.readlines()
good[:] = map(lambda item: re.sub('\t+', ' ', item.strip()).split(' '), good)
f.close()

f = open('/home/marc/PycharmProjects/MedNet/src/Medes/masarchivos/6_20210724-12_20211019-11_35.txt', "r")
tobeChanged = f.readlines()
tobeChanged[:] = map(lambda item: re.sub('\t+', ' ', item.strip()).split(' '), tobeChanged)
f.close()

for i in range(len(good)):
    if i > 0 and i < len(tobeChanged):
        tobeChanged[i][1] = good[i][1]
        tobeChanged[i][2] = good[i][2]

with open("/home/marc/PycharmProjects/MedNet/src/Medes/6_20210724-12_20211019-11_35.txt", "w") as txt_file:
    for line in tobeChanged:
        txt_file.write(" ".join(line) + "\n")


print(tobeChanged[5])
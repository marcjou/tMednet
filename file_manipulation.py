from datetime import datetime, timedelta
import re
import user_interaction as ui


def loaddata(args):
    """
    Method: loaddata(args)
    Purpose: read tmednet *.txt data files
    Require:
    Version: 01/2021, EGL: Documentation
    """
    for ifile in args.files:
        filein = args.path + ifile
        print("file", filein)
        # Extraemos campos del nombre del fichero
        datos = {"timegmt": [], "time": [], "temp": [], "S/N": "", "GMT": "",
                 "depth": int(ifile.split("_")[3].split(".")[0]), "region": int(ifile.split("_")[0]),
                 "datainici": datetime.strptime(ifile.split("_")[1], '%Y%m%d-%H'),
                 "datafin": datetime.strptime(ifile.split("_")[2], '%Y%m%d-%H')}

        f = open(filein, "r")
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
        args.mdata.append(datos)


def report(args, textbox, end):
    """
    Method: report(args)
    Purpose: List main file characteristics
    Require:
        textBox: text object
    Version: 01/2021, EGL: Documentation
    """
    textbox.delete(1.0, end)
    for item in args.mdata:
        daysinsitu = (item['datainici'] - item['datafin']).total_seconds() / 86400
        cadena = "=========\n"
        cadena += "Depth: " + str(item["depth"]) + "\n"
        cadena += "Init: " + item["datainici"].isoformat() + "\n"
        cadena += "End: " + item["datafin"].isoformat() + "\n"
        cadena += "Ndays: " + str(daysinsitu) + "\n"
        cadena += "GMT: " + item["GMT"] + "\n"
        cadena += "DInit: " + item["timegmt"][0].isoformat() + "\n"
        cadena += "DEnd: " + item["timegmt"][-1].isoformat() + "\n"
        textbox.insert("end", cadena)

    textbox.insert("end", "=========\n")


def to_utc(args):
    """
    Method: to_utc(self)
    Purpose: Shift temporal axis
    Require:
    Version: 01/2021, EGL: Documentation
    """
    gmthshift = int(args.mdata[0]["GMT"][1:])
    # Mirar timedelta
    args.mdata[0]["time"] = [args.mdata[0]["timegmt"][i] - timedelta(hours=gmthshift) for i in
                             range(len(args.mdata[0]["timegmt"]))];
    print(args.mdata[0]["time"][10], args.mdata[0]["timegmt"][10])
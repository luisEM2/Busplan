import xlrd
import time
start = time.time()
f = xlrd.open_workbook(r"C:\Users\luis\OneDrive\Desktop\Buspläne neu.xlsx")
print(time.time()-start)
links = []
for sheet in f.sheets():
    rows = [i for i in range(sheet.nrows)]
    for i in rows:
        links.append([sheet.cell_value(i, 0), sheet.cell_value(i, 2), sheet.cell_value(i, 3), sheet.cell_value(i, 4)])

haltestellen = []
for haltestelle in links:
    append = True
    for hs in haltestellen:
        # haltestelle bereits vorhanden
        if hs[0] == haltestelle[0] and hs[1] == haltestelle[1]:
            # haltestelle nicht hinzufügen
            append = False
            # check for contents 0 and 1 können falsch sein
            if not (hs[2] == haltestelle[2] and hs[3] == haltestelle[3]):
                print(haltestelle, hs)

    if append:
        haltestellen.append(haltestelle)

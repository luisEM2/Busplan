import xlsxwriter
import time
a = [0, 15, 16, 17, 18, 19, 25]
c = [3, 3, 3, 3, 3, 3, 3, 4]
"""for i in range(len(c)):
    c[i] += 1"""
b = [13, 16, 19, 21, 24]
c = [5 for _ in a]


def s(l, m):
    n = []
    #f = []
    #d = m
    for i in range(len(l)):
        h = l[i]
        #g = h + 20
        h += 30
        if h >= 60:
            h -= 60
            m[i] += 1
            if h >= 60:
                h -= 60
                m[i] += 1
        n.append(h)
        #if g >= 60:
        #    g -= 60
            #d[i] += 1
        #f.append(g)
    return n, m#, f, d

start = time.time()
with xlsxwriter.Workbook("File.xlsx") as file:
    sheet = file.add_worksheet()
    #sheet2 = file.add_worksheet()
    for i in range(48):
        column = 2 * i
        a, c = s(a, c)
        #b, d, = s(b, d)
        for h in range(len(c)):
            row = h+1
            sheet.write(row, column, c[h])
            #sheet2.write(row, column, c2[h])
        column += 1
        for j in range(len(a)):
            row = j+1
            sheet.write(row, column, a[j])
            #sheet2.write(row, column, a2[j])
        """column += 1
        for k in range(len(d)):
            row = k+1
            sheet.write(row, column, d[k])
            #sheet2.write(row, column, c2[h])
        column += 1
        for p in range(len(b)):
            row = p+1
            sheet.write(row, column, b[p])
            #sheet2.write(row, column, a2[j])"""
print(time.time()-start)
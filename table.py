import xlsxwriter
import sqlite3
from key_collector import Collector

row = 1

#conn = sqlite3.connect('UN_categories.sqlite')
#cursor = conn.cursor()

workbook = xlsxwriter.Workbook('table.xlsx')
worksheet = workbook.add_worksheet()

worksheet.set_column('B:B', 50)

worksheet.write(0, 0, "Категория")
worksheet.write(0, 1, "Запросы")

coll = Collector()
nc = coll.getSubniches()

row = 1
for ID, name in nc:
    worksheet.write(row, 0, name)
    rqs = list(set(coll.getRequests(ID)))
    
    col = 1
    for r in rqs:
        worksheet.write(row, col, r[0])
        worksheet.set_column(col, 500)
        col += 1
    row += 1
    
workbook.close()

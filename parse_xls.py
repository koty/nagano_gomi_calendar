import xlrd
import datetime
import json
import sys


def read_column_as_date(book, sheet, column_index, kind):
    calendar_list = []
    i = 6  # 7行目から読む
    while True:
        c = sheet.cell(i, column_index)
        if not c.value:
            break
        if isinstance(c.value, str):
            month_day = c.value.replace('○', '').replace('日', '').split('月')
            d = datetime.datetime.now()
            d = d.replace(month=int(month_day[0]), day=int(month_day[1]))
        else:
            d = datetime.datetime(*xlrd.xldate_as_tuple(c.value, book.datemode))
        calendar_list.append({'date': d.strftime('%Y-%m-%d'), 'kind': kind})
        i += 1

    return calendar_list


def parse_as_object(path):
    book = xlrd.open_workbook(path)
    calendar_dic = {}  # key: カレンダーNo、value, GomiCalendarレコード

    for sheet_name in book.sheet_names():
        if not sheet_name.isnumeric():
            continue
        sheet = book.sheet_by_name(sheet_name)
        calendar_list = []

        calendar_list.extend(read_column_as_date(book, sheet, 2, '可燃'))
        calendar_list.extend(read_column_as_date(book, sheet, 3, '可燃'))
        calendar_list.extend(read_column_as_date(book, sheet, 4, '可燃'))
        calendar_list.extend(read_column_as_date(book, sheet, 5, 'プラ'))
        calendar_list.extend(read_column_as_date(book, sheet, 6, 'プラ'))
        calendar_list.extend(read_column_as_date(book, sheet, 7, '不燃'))
        calendar_list.extend(read_column_as_date(book, sheet, 8, '枝葉'))
        calendar_list.extend(read_column_as_date(book, sheet, 9, '紙ペ'))
        calendar_list.extend(read_column_as_date(book, sheet, 10, '缶ペ'))
        calendar_list.extend(read_column_as_date(book, sheet, 11, 'ビン'))

        calendar_dic[sheet_name] = calendar_list
    return calendar_dic

if len(sys.argv) == 0:
    print('specify xls path')
    exit()
o = parse_as_object(sys.argv[1])
print(json.dumps(o, indent=2))

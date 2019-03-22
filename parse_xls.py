import xlrd
from datetime import datetime as dt
from datetime import timedelta
import json
import sys


def read_column_as_date(book, sheet, column_index, kind, day_of_the_weeks=None):
    calendar_list = []
    i = 6  # 7行目から読む
    while True:
        c = sheet.cell(i, column_index)
        if not c.value:
            break
        now = dt.now()
        current_year = now.year - 1 if now.month <= 3 else now.year
        # 29年度番のカレンダーだったので、一年足す
        current_year += 1
        if isinstance(c.value, str):
            month_day = c.value.replace('○', '').replace('日', '').split('月')
            month = int(month_day[0])
            day = int(month_day[1])
        else:
            date = dt(*xlrd.xldate_as_tuple(c.value, book.datemode))
            day = date.day
            month = date.month
        # yearは入力時点のものがはいっているので、置き換える
        year = current_year + 1 if month <= 3 else current_year
        d = dt(year=year, month=month, day=day)
        if len(calendar_list) > 2 and kind == '可燃':
            expected_day = _get_expected_day(calendar_list[-1]['date'], day_of_the_weeks)
            if expected_day and d.date() != expected_day.date():
                calendar_list.append({'date': expected_day.strftime('%Y-%m-%d'), 'kind': kind, 'not_available': True})
        calendar_list.append({'date': d.strftime('%Y-%m-%d'), 'kind': kind})
        i += 1

    return calendar_list


def _parse_str_to_day_of_the_weeks(weeks_str):
    ret = []
    weeks_dic = {'月': 0, '火': 1, '水': 2, '木': 3, '金': 4, '土': 5, '日': 6}
    for week_str in weeks_str:
        ret.append(weeks_dic[week_str])
    return ret


def _get_expected_day(s, day_of_the_weeks):
    if len(day_of_the_weeks) < 2:
        return None
    d = dt.strptime(s, '%Y-%m-%d')
    if d.weekday() == day_of_the_weeks[0]:
        expected_week = day_of_the_weeks[1]
    else:
        expected_week = day_of_the_weeks[0]
    # dの直近のexpected_weekを探す
    expected_day = d + timedelta(days=1)
    while expected_day.weekday() != expected_week:
        expected_day += timedelta(days=1)
    return expected_day


def parse_as_object(path):
    book = xlrd.open_workbook(path)
    calendar_dic = {}  # key: カレンダーNo、value, GomiCalendarレコード

    for sheet_name in book.sheet_names():
        if not sheet_name.isnumeric():
            continue
        sheet = book.sheet_by_name(sheet_name)
        calendar_list = []

        day_of_the_weeks = _parse_str_to_day_of_the_weeks(sheet.cell(5, 2).value)
        calendar_list.extend(read_column_as_date(book, sheet, 2, '可燃', day_of_the_weeks))
        calendar_list.extend(read_column_as_date(book, sheet, 3, '可燃', day_of_the_weeks))
        calendar_list.extend(read_column_as_date(book, sheet, 4, '可燃', day_of_the_weeks))
        calendar_list.extend(read_column_as_date(book, sheet, 5, 'プラ'))
        calendar_list.extend(read_column_as_date(book, sheet, 6, 'プラ'))
        calendar_list.extend(read_column_as_date(book, sheet, 7, '枝葉'))
        calendar_list.extend(read_column_as_date(book, sheet, 8, '不燃'))
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

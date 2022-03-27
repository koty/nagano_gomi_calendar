import requests
from datetime import datetime as dt
from datetime import timedelta
import json as JSON
import sys


def read_column_as_date(json, kind_index, kind):
    calendar_list = []
    kind_dic = json[f'http://linkdata.org/resource/rdf1s9118i#{kind_index}']
    date_str_list = [k.replace('http://linkdata.org/property/rdf1s9118i#','').replace('%2000%3A00%3A00','') for k in  kind_dic.keys()][3:]
    day_of_the_weeks = _get_day_of_the_weeks(date_str_list)
    for date_str in date_str_list:
        d = dt.strptime(date_str, '%Y-%m-%d')
        if len(calendar_list) > 2:
            expected_day = _get_expected_day(calendar_list[-1]['date'], day_of_the_weeks)
            if expected_day and d.date() != expected_day.date():
                calendar_list.append({'date': expected_day.strftime('%Y-%m-%d'), 'kind': kind, 'not_available': True})
        calendar_list.append({'date': d.strftime('%Y-%m-%d'), 'kind': kind})

    return calendar_list

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

def _get_day_of_the_weeks(date_str_list):
    # 0番目と1番目の曜日を調べる
    weekday1 = dt.strptime(date_str_list[0], '%Y-%m-%d').weekday()
    weekday2 = dt.strptime(date_str_list[1], '%Y-%m-%d').weekday()
    return list(set([weekday1, weekday2]))

def parse_as_object():

    calendar_dic = {}  # key: カレンダーNo、value, GomiCalendarレコード
    for i in range(1, 25):
        res = requests.get(f'http://linkdata.org/api/1/rdf1s9118i/gomi_calendar_2022_{i:02}_rdf.json')
        json = res.json()
        calendar_list = []

        # day_of_the_weeks = _parse_str_to_day_of_the_weeks(sheet.cell(5, 2).value)
        calendar_list.extend(read_column_as_date(json, 1, '可燃ごみ'))
        calendar_list.extend(read_column_as_date(json, 2, '不燃ごみ'))
        calendar_list.extend(read_column_as_date(json, 3, 'プラ類'))
        calendar_list.extend(read_column_as_date(json, 4, '紙'))
        calendar_list.extend(read_column_as_date(json, 5, '缶類'))
        calendar_list.extend(read_column_as_date(json, 6, 'ペットボトル'))
        calendar_list.extend(read_column_as_date(json, 7, 'ビン、乾電池、灰'))

        calendar_dic[str(i)] = calendar_list
    return calendar_dic

o = parse_as_object()
print(JSON.dumps(o, indent=2))

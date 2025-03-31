import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import json as JSON
import sys

date_fmt_slash = '%Y/%m/%d'
date_fmt_hyphen = '%Y-%m-%d'

def read_column_as_date(raw_list, kind):
    #print(json)
    #print(kind_index)
    #print(kind)
    # raw_listのなかから、1番目に◯がついているものにフィルタする
    date_str_list = [date_str[0] for date_str in raw_list if date_str[1] == '○']
    calendar_list = []
    day_of_the_weeks = _get_day_of_the_weeks(date_str_list)
    for date_str in date_str_list:
        d = dt.strptime(date_str, date_fmt_slash)
        if len(calendar_list) > 2:
            expected_day = _get_expected_day(calendar_list[-1]['date'], day_of_the_weeks)
            if expected_day and d.date() != expected_day.date():
                calendar_list.append({'date': expected_day.strftime(date_fmt_hyphen), 'kind': kind, 'not_available': True})
        calendar_list.append({'date': d.strftime(date_fmt_hyphen), 'kind': kind})

    return calendar_list

def _get_expected_day(s, day_of_the_weeks):
    if len(day_of_the_weeks) < 2:
        return None
    d = dt.strptime(s, date_fmt_hyphen)
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
    if not date_str_list:
        return []
    # 0番目と1番目の曜日を調べる
    weekday1 = dt.strptime(date_str_list[0], date_fmt_slash).weekday()
    weekday2 = dt.strptime(date_str_list[1], date_fmt_slash).weekday()
    return list(set([weekday1, weekday2]))

def _create_calendar_list(data, i):
    ret = list(zip(data[0], data[i]))
    # 3番目からがデータ
    return ret[3:]

def parse_as_object():

    calendar_dic = {}  # key: カレンダーNo、value, GomiCalendarレコード
    for i in range(1, 25):
        # ローカルファイルの ./令和7年度ごみ収集カレンダー/gomi_calendar_2025_{#i}.csv から読み込む
        # 元ネタは https://www.city.nagano.nagano.jp/n023500/contents/p006280.html
        df = pd.read_csv(f'./cal2025/gomi_calendar_2025_{i}.csv', header=None, encoding="utf-8")
        data = df.T
        calendar_list = []

        # day_of_the_weeks = _parse_str_to_day_of_the_weeks(sheet.cell(5, 2).value)
        calendar_list.extend(read_column_as_date(_create_calendar_list(data, 1), '可燃ごみ'))
        calendar_list.extend(read_column_as_date(_create_calendar_list(data, 2), '不燃ごみ'))
        calendar_list.extend(read_column_as_date(_create_calendar_list(data, 3), 'プラ類'))
        calendar_list.extend(read_column_as_date(_create_calendar_list(data, 4), '紙'))
        calendar_list.extend(read_column_as_date(_create_calendar_list(data, 5), '缶類'))
        calendar_list.extend(read_column_as_date(_create_calendar_list(data, 6), 'ペットボトル'))
        calendar_list.extend(read_column_as_date(_create_calendar_list(data, 7), 'ビン、乾電池、灰'))

        calendar_dic[str(i)] = calendar_list
    return calendar_dic

o = parse_as_object()
print(JSON.dumps(o, indent=2))

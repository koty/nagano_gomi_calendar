# nagano_gomi_calendar

http://www.city.nagano.nagano.jp/site/kateigomi/146311.html にある「資源物・ごみ収集日程一覧表(カレンダー番号１番から26番まで) 」というxlsファイルをjsonにparseします。

使い方

```
pip install -r requirements.txt
python parse_xls.py 115634.xls > data.json
```

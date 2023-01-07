from models import session, Anime

import csv
import sys

filename = 'result.csv' if len(sys.argv) < 2 else sys.argv[1]

with open(filename, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', '标题', '类型', '分数', '实际分数', '总人数',
        *(f'{i}星(短)' for i in range(6)), '平均(短)', '人数(短)',
        *(f'{i}星(长)' for i in range(6)), '平均(长)', '人数(长)'])
    for i in session.query(Anime):
        row = [
            i.media_id, i.title, '国创' if i.chinese else '番剧', i.score, i.average, i.total,
            *i.short.as_list(), i.short.average, i.short.total,
            *i.long.as_list(), i.long.average, i.long.total
        ]
        print(row)
        writer.writerow(row)
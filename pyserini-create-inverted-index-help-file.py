import time
import sqlite3 as sl
# Create docterm.recall for deepCT by using TF_IDF values calculated before

con = sl.connect('description.sqlite')
c = con.cursor()
start = time.time()

with open('jsonl/pyserini.jsonl', 'w', encoding='utf-8') as writer:
    writer.truncate(0)  # empty the file

    c.execute(f'select document_id, title from document')
    rows = c.fetchall()
    i = 0
    for row in rows:

        if (i % 200 == 0):
            end = time.time()
            print(row[0] + ' - ' + str(i) + ' of ' + str(len(rows)) +
                  ' === Time elapsed: ', '%.2f' % (end-start) + 's')
            start = time.time()

        i = i + 1

        # print(row)
        doc_id = row[0].replace('"', '')
        title = row[1].replace('"', '').replace('\\', '\\\\')
        writer.write('{"id": ' + '"' + doc_id + '",' + ' "contents":')

        writer.write('"' + title + '"')

        writer.write('}')

        writer.write('\n')

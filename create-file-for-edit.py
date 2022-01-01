import sqlite3 as sl
import time
# Create docterm.recall for deepCT by using TF_IDF values calculated before

con = sl.connect('10-abstract.sqlite')
c = con.cursor()

with open('output/test-10-abstract/edit.tsv', 'w', encoding='utf-8') as writer:
    writer.truncate(0)  # empty the file

    c.execute(f'select * from document')
    rows = c.fetchall()

    start = time.time()
    i = 0

    for row in rows:

        if (i % 200 == 0):
            end = time.time()
            print(row[0] + ' - ' + str(i) + ' of ' + str(len(rows)) +
                  ' === Time elapsed: ', '%.2f' % (end-start) + 's')
            start = time.time()

        i = i + 1
        # print(row)
        doc_id = row[0].replace('', '')
        title = row[1]
        writer.write(str(doc_id) + '\t' + str(title))

        writer.write('\n')

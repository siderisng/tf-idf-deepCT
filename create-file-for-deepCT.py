import time
import sqlite3 as sl
# Create docterm.recall for deepCT by using TF_IDF values calculated before

con = sl.connect('tf-idf.sqlite')
c = con.cursor()
start = time.time()

with open('sample_abstract.docterm_recall', 'w', encoding='utf-8') as writer:
    writer.truncate(0)  # empty the file

    c.execute(f'select * from document')
    rows = c.fetchall()
    i = 0;
    for row in rows:
        
        if (i % 200 == 0):
            end = time.time()
            print(row[0] + ' - ' + str(i) + ' of ' + str(len(rows)) +
                  ' === Time elapsed: ', '%.2f' % (end-start) + 's')
            start = time.time()

        i = i + 1;

        # print(row)
        doc_id = row[0].replace('"', '')
        title = row[2].replace('"', '')
        writer.write('{"query": '+ '"' + title + '",' + ' "term_recall": {')

        c.execute(
            f"select * from word_in_document WHERE document_id = '{doc_id}'")
        words = c.fetchall()
        for index, word in enumerate(words):
            text = word[3].replace('"', '')
            tf_idf = word[4]
            # print(word)

            writer.write(f'"{text}": {tf_idf}')
            if (index != len(words) - 1):
                writer.write(', ')

        writer.write('}, "doc": {"position": "1", "id": "' +
                     doc_id + '","title": "' + title + '" }}')

        writer.write('\n')

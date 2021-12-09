import sqlite3 as sl
# Create docterm.recall for deepCT by using TF_IDF values calculated before

con = sl.connect('tf-idf.sqlite')
c = con.cursor()

with open('test.docterm_recall', 'w', encoding='utf-8') as writer:
    writer.truncate(0)  # empty the file

    c.execute(f'select * from document')
    rows = c.fetchall()
    for row in rows:
        # print(row)
        doc_id = row[0]
        title = row[2]
        writer.write('{"term_recall": {')

        c.execute(
            f"select * from word_in_document WHERE document_id = '{doc_id}'")
        words = c.fetchall()
        for index, word in enumerate(words):
            text = word[3]
            tf_idf = word[4]
            # print(word)

            writer.write(f'"{text}": {tf_idf}')
            if (index != len(words) - 1):
                writer.write(', ')

        writer.write('}, "doc": {"position": "1", "id": "' +
                     doc_id + '","title": "' + title + '" }}')

        writer.write('\n')

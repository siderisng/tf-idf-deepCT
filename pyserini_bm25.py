from pyserini import index
from pyserini.index import IndexReader
import itertools
from pyserini.search import SimpleSearcher
import itertools
import time
import sqlite3 as sl


def calculateBM25(index_reader, docId, word):
    # # Initialize from an index path:
    # tf = index_reader.get_document_vector(docId)
    # df = {term: (index_reader.get_term_counts(term, analyzer=None))[
    #     0] for term in tf.keys()}
    # Note that the keys of get_document_vector() are already analyzed, we set analyzer to be None.
    bm25_score = index_reader.compute_bm25_term_weight(
        docId, word, analyzer=None)

    return str(bm25_score)


# Initialize from an index path:
index_reader = IndexReader('indexes/complete_description/')

con = sl.connect('description.sqlite')
c = con.cursor()
start = time.time()


c.execute(f'select title, document_id from document')
rows = c.fetchall()
i = 0
with open('output/complete_descriptions/train.docterm_recall', 'w', encoding='utf-8') as writer:
    writer.truncate(0)  # empty the file

    for row in rows:
        # if (i > 1000):
        #     print(row)
        if (i % 200 == 0):
            end = time.time()
            print(row[1] + ' - ' + str(i) + ' of ' + str(len(rows)) +
                  ' === Time elapsed: ', '%.2f' % (end-start) + 's ====== Progress: ' + str(round(i / len(rows) * 100, 2)) + '%', end='\r')
            start = time.time()

        i = i + 1

        title = row[0].replace('"', '')
        title = title.replace('\\', '')
        document_id = row[1]
        if title:
            writer.write('{"query": ' + '"' + title +
                         '",' + ' "term_recall": {')
        else:
            continue

        wordList = title.split(' ')
        index = 0
        for word in wordList:
            word = word.replace('"', '')
            word = word.replace('\\', '')

            score = calculateBM25(index_reader, document_id, word)
            writer.write(f'"{word}": {score}')
            if (index != len(wordList) - 1):
                writer.write(', ')
            index += 1

        writer.write('}, "doc": {"position": "1", "id": "' +
                     document_id + '","title": "' + title + '" }}')

        writer.write('\n')

from pyserini import index
from pyserini.index import IndexReader
import itertools
from pyserini.search import SimpleSearcher
import itertools
import time
import sqlite3 as sl


def calculateBM25(index_reader, docId, word):
    # Initialize from an index path:
    index_reader = IndexReader('indexes/sample_collection_jsonl/')
    tf = index_reader.get_document_vector(docId)
    df = {term: (index_reader.get_term_counts(term, analyzer=None))[0] for term in tf.keys()}
    # Note that the keys of get_document_vector() are already analyzed, we set analyzer to be None.
    bm25_score = index_reader.compute_bm25_term_weight(docId, word, analyzer=None)
    
    return str(bm25_score)


# Initialize from an index path:
index_reader = IndexReader('indexes/sample_collection_jsonl/')

con = sl.connect('description.sqlite')
c = con.cursor()
start = time.time()


c.execute(f'select title, document_id from document LIMIT 1000')
rows = c.fetchall()
i = 0;
for row in rows:
    if (i > 1):
         break

    title = row[0]
    document_id = row[1]
    if title:
        i = i + 1
    else:
        continue

    wordList = title.split(' ')
    for word in wordList:
        score = calculateBM25(index_reader, document_id, word)
        print(word + ': ' + score)

    if (i % 200 == 0):
        end = time.time()
        print(row[0] + ' - ' + str(i) + ' of ' + str(len(rows)) +
                ' === Time elapsed: ', '%.2f' % (end-start) + 's')
        start = time.time()




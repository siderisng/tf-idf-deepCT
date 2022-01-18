from pyserini import index
from pyserini.index import IndexReader
import itertools
from pyserini.search import SimpleSearcher
import itertools
import time
import sqlite3 as sl
import math

# def calculateBM25(index_reader, docId, word):
#     # # Initialize from an index path:
#     # tf = index_reader.get_document_vector(docId)
#     # df = {term: (index_reader.get_term_counts(term, analyzer=None))[
#     #     0] for term in tf.keys()}
#     # Note that the keys of get_document_vector() are already analyzed, we set analyzer to be None.
#     bm25_score = index_reader.compute_bm25_term_weight(
#         docId, word, analyzer=None)

#     return str(bm25_score)


# Initialize from an index path:
index_reader = IndexReader('indexes/test_10_abstract/')

con = sl.connect('10-abstract.sqlite')
c = con.cursor()
start = time.time()


c.execute(f'select title, document_id from document')
rows = c.fetchall()
i = 0
with open('output/test-10-abstract/train-with-title-full-score.docterm_recall', 'w', encoding='utf-8') as writer:
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
        if title: # TODO TITLE WILL HAVE ALL FIELD WORDS, BUT QUERY AND TERM_RECALL WILL HAVE THE WORDS WITH ABOVE AVERAGE TF_IDF
            writer.write('{"query": ' + '"' + title +
                         '",' + ' "term_recall": {')
        else:
            continue

        tf = index_reader.get_document_vector(document_id)
        df = {term: (index_reader.get_term_counts(term, analyzer=None))[
            0] for term in tf.keys()}
        N = len(rows)  # TOTAL NUMBER OF  OF DOCUMENTS
        lenTerms = len(df)
        tfIdf = {}
        index = 0
        for term in tf.keys():
            if (df[term] == 0):
                tfIdf[term] = math.log(0 + 1, 10)
            else:
                tfIdf[term] = tf[term] * math.log(N / df[term] + 1, 10)

        # baseTFIDF =
        sum = 0
        for term in tfIdf:
            sum += tfIdf[term]

        average = sum / len(tfIdf)
        # print(average)

        j = 0
        for term in tf.keys():
            if (tfIdf[term] >= average): # TODO PRINT AVERAGE NUMBER OF TERMS THAT HAVE MORE THAN AVERAGE SCORE
                if (j != 0):
                    writer.write(', ')
                writer.write(f'"{term}": {tfIdf[term]}')
                j += 1

            index += 1

        writer.write('}, "doc": {"position": "1", "id": "' +
                     document_id + '","title": "' + title + '" }}')

        writer.write('\n')

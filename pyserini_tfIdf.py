from pyserini import index
from pyserini.index import IndexReader
from pyserini.search import SimpleSearcher
import time
import sqlite3 as sl
import math


# Initialize from an index path:
index_reader = IndexReader('indexes/10_abstract/')

con = sl.connect('databases/10-abstract.sqlite')
c = con.cursor()
start = time.time()


c.execute(f'select title, document_id from document')
rows = c.fetchall()
total_words_above_average_tfidf = 0;
i = 0
with open('output/10-abstract/final_train.docterm_recall', 'w', encoding='utf-8') as writer:
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

        if not title:
            continue;

        tf = index_reader.get_document_vector(document_id)
        df = {term: (index_reader.get_term_counts(term, analyzer=None))[
            0] for term in tf.keys()}
        N = len(rows)  
        lenTerms = len(df)
        tfIdf = {}
        index = 0
        for term in tf.keys():
            if (df[term] == 0):
                tfIdf[term] = math.log(0 + 1, 10)
            else:
                tfIdf[term] = tf[term] * math.log(N / df[term] + 1, 10)

        sum = 0
        for term in tfIdf:
            sum += tfIdf[term]

        average = sum / len(tfIdf)
        # print(average)

        j = 0
        importantWords = '';
        importantWordsTermRecalls = ''
        for term in tf.keys():
            if (tfIdf[term] >= average):
                # print(term)
                if (j != 0):
                    importantWords += ' '
                    importantWordsTermRecalls += ', '
                importantWords += term
                
                importantWordsTermRecalls += f'"{term}": {tfIdf[term]}'
                
                j += 1

            index += 1

        writer.write('{"query": ' + '"' + importantWords +
         '",' + ' "term_recall": {')

        writer.write(importantWordsTermRecalls)
         
        
        total_words_above_average_tfidf = total_words_above_average_tfidf + j;

        writer.write('}, "doc": {"position": "1", "id": "' +
                     document_id + '","title": "' + title + '" }}')

        writer.write('\n')

print('Average number of words that have above average tf-idf score in every doc is: ' + str(total_words_above_average_tfidf/len(rows)))
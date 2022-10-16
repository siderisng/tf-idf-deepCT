import re
import os
import time
import math
import sqlite3 as sl
from bs4 import BeautifulSoup
import argparse
# Scikit Learn
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tfIdf import runTfIdf, getBestWords

import pandas as pd

WORD_LIMIT = 128


def cosineSimilarity(documents):
    # Create the Document Term Matrix
    # count_vectorizer = CountVectorizer(stop_words='english') # or TfidfVectorizer
    count_vectorizer = TfidfVectorizer()
    sparse_matrix = count_vectorizer.fit_transform(documents)

    # OPTIONAL: Convert Sparse Matrix to Pandas Dataframe if you want to see the word frequencies.
    doc_term_matrix = sparse_matrix.todense()
    df = pd.DataFrame(doc_term_matrix,
                      columns=count_vectorizer.get_feature_names_out(),
                      index=['full', 'fields'])

    return cosine_similarity(df)[0][1]


def createDBEntriesForDocument(c, con, documentId, finalText, howManyWords, j):

    # c.execute(
    #     f"INSERT OR IGNORE INTO document (document_id, title, total_words_not_unique) VALUES ('{documentId}', '{finalText}', {howManyWords})")
    # # store document with total word count and abstract contents

    c.execute(
        f"INSERT INTO document (document_id, title) VALUES ('{documentId}', '{finalText}')")
    # store document with total word count and abstract contents

    # if finalText:
    #     k = 0
    #     for word in finalText.split():
    #         j = j + 1

    #         if (k > 512):
    #             break  # we can't support more than 512 words for deepCT so no need to waste time with words that we won't use
    #         k = k + 1
    #         word = re.sub(r"[,./;:()']", '', word)

    #         # print(word)

    #         if word and word != '':
    #             c.execute(
    #                 f"SELECT word_id from word WHERE word = '{word}'")
    #             row = c.fetchone()  # find if WORD EXISTS IN DATABASE ALREADY

    #             if row and row[0]:  # if it exists, do nothing
    #                 id = str(row[0])
    #                 # c.execute(
    #                 #     f"INSERT OR IGNORE INTO word (word_id, word) VALUES ('{id}', '{word}')")
    #             else:  # else, insert new word with a new id
    #                 id = str(j)
    #                 c.execute(
    #                     f"INSERT INTO word (word_id, word) VALUES ('{str(j)}', '{word}')")

    #             c.execute(
    #                 f"SELECT word_id from word_in_document WHERE word_id = '{id}' AND document_id='{documentId}'")
    #             row = c.fetchone()  # find if word in document already exists in DATABASE

    #             if row and row[0]:  # if it exists, increment quantity by 1
    #                 # print('update')
    #                 c.execute(
    #                     f"UPDATE word_in_document SET quantity = quantity + 1 WHERE word_id = '{id}' AND document_id = '{documentId}'")
    #             else:  # else, insert new word_in_document row
    #                 # print('insert')
    #                 c.execute(
    #                     f"INSERT INTO word_in_document (word_id, document_id, word, quantity) VALUES ('{id}', '{documentId}', '{word}', 1)")

    con.commit()
    return j


def createDBAndTables(dbName):
    # if os.path.exists(dbName + ".sqlite"):
    #     os.remove(dbName + ".sqlite")
    con = sl.connect(dbName + '.sqlite')
    con.execute('''CREATE TABLE IF NOT EXISTS document
            (document_id TEXT PRIMARY KEY     NOT NULL,
            title           TEXT    NOT NULL) ''')
    # total_words_not_unique INT NOT NULL,

    con.execute('''CREATE TABLE IF NOT EXISTS word
            (word_id INT PRIMARY KEY     NOT NULL,
            word           TEXT    NOT NULL) ''')

    con.execute('''CREATE TABLE IF NOT EXISTS word_in_document
            (id INTEGER PRIMARY KEY,
            word_id INT NOT NULL REFERENCES word (word_id),
            document_id TEXT NOT NULL REFERENCES document (document_id),
            word TEXT NOT NULL,
            tf_idf REAL,
            quantity INT NOT NULL) ''')

    con.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_document
            ON document (document_id);
    ''')

    con.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_word
            ON word (word);
    ''')

    con.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_word_in_document
            ON word_in_document (word_id, document_id);
    ''')

    con.commit()

    return con


parser = argparse.ArgumentParser()
# parser.add_argument(
#     '--limit', '-l', help="how many patents? default is 100, 0 is unlimited", type=int, default=10)
# parser.add_argument('--fields', '-f', help="which fields to use, separated by comma (,)? default is abstract,title",
#                     type=str, default='abstract')

args = parser.parse_args()
LIMIT = int(input(
    'how many patent documents to scan? default is 100, type 0 for unlimited:  '))
# LIMIT = args.limit == 0 ? math.inf : args.limit;
LIMIT = math.inf if LIMIT == 0 else LIMIT
FIELDS = input(
    'Which fields do you want to process? separated by comma (,)? default is abstract,title: ')

if not FIELDS:
    FIELDS = 'abstract,title'

if not os.path.exists('databases/'):
    os.makedirs('databases/')

print('LIMIT is ' + str(LIMIT))
FIELDS = FIELDS.split(',')
print('FIELDS: ' + str(FIELDS))

dbName = 'databases/' + str(LIMIT) + '-' + '-'.join(FIELDS)
# create tables for my DB
con = createDBAndTables(dbName)

# DATASET FOLDER - WILL LOOP THROUGH ALL SUBFOLDERS
path = 'C:/Users/sider/Documents/final_clef_ip'
i = 0
wordId = 0
c = con.cursor()  # needed for printing results
total_count = 0  # will store total number of patents

for subdir, dirs, files in os.walk(path):
    total_count = total_count + len(files)
    i = i + 1
    if (i > LIMIT):
        break

start = time.time()


i = 0
for subdir, dirs, files in os.walk(path):

    for file in files:

        xml = str(os.path.join(subdir, file))

        documentId = file.replace('.txt', '')

        if ".DS_STORE" in xml:  # ignore .DS_STORE files (MacOS)
            continue

        if (i % 1000 == 0 and i != 0):
            end = time.time()
            print(str(documentId) + ' - ' + str(i) + ' of ' + str(total_count) +
                  ' ===== Time elapsed: ', '%.2f' % (end-start) + 's, ====== Progress: ' + str(round(i / total_count * 100, 2)) + '%')
            start = time.time()
            con.commit()

        i = i + 1
        if (i > LIMIT):
            break

        patent = open(xml, 'r', encoding='utf-8')
        root = BeautifulSoup(patent, features="html.parser")

        pro_fields = []
        finalText = ''
        for field in FIELDS:
            pro_fields.append(root.find(field))

        # print(pro_fields)

        for proField in pro_fields:
            if proField is None:
                proField = ''
            else:
                proField = proField.text
            proField = re.sub(r"[']", "''", proField)
            finalText += proField

        finalText = finalText.split()[:WORD_LIMIT]
        finalText = ' '.join(finalText)

        c.execute(
            f"SELECT * from document WHERE document_id = '{documentId}'")
        row = c.fetchone()

        if not row:
            createDBEntriesForDocument(
                c, con, documentId, finalText, '', wordId)


end = time.time()
print(xml + ' - ' + str(i) + ' of ' + str(total_count) +
      ' ===== Time elapsed: ', '%.2f' % (end-start) + 's ======')

con.commit()

print('DATABASE CREATED ' + dbName + '.sqlite!')

continueInverted = input(
    'Continue with creation of inverted index with pyserini?, y to continue:  ')

if continueInverted == 'y':
    import pyseriniCreateInvertedIndexHelpFile

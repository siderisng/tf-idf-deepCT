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


def createDBEntriesForDocument(c, con, documentId, finalText, howManyWords, j):

    c.execute(
        f"INSERT INTO document (document_id, title) VALUES ('{documentId}', '{finalText}')")
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
path = '/Users/giorgossideris/Downloads/final_clef_ip'
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

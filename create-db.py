# Create Database and connect to it

import re
import os
import time
import sqlite3 as sl
from bs4 import BeautifulSoup

f = open('output.txt', 'w')  # open output.txt for storing output

# create tables for my DB
con = sl.connect('tf-idf.sqlite')
con.execute('''CREATE TABLE IF NOT EXISTS document
         (document_id TEXT PRIMARY KEY     NOT NULL,
         total_words_not_unique INT NOT NULL,
         title           TEXT    NOT NULL) ''')

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

path = 'clef_small_dataset'  # DATASET FOLDER - WILL LOOP THROUGH ALL SUBFOLDERS
i = 0
j = 0
c = con.cursor()  # needed for printing results
total_count = 0  # will store total number of patents

for subdir, dirs, files in os.walk(path):
    total_count = total_count + len(files)
start = time.time()
for subdir, dirs, files in os.walk(path):

    for file in files:
        xml = str(os.path.join(subdir, file))
        if ".DS_STORE" in xml:  # ignore .DS_STORE files (MacOS)
            continue

        if (i % 200 == 0):
            end = time.time()
            print(xml + ' - ' + str(i) + ' of ' + str(total_count) +
                  ' === Time elapsed: ', '%.2f' % (end-start) + 's')
            start = time.time()

        i = i + 1
        if (i > 500):
            break

        patent = open(xml, 'r')
        root = BeautifulSoup(patent, features="html.parser")
        abstract = root.find('abstract')  # extract abstract

        if (abstract and abstract.text):
            abstract = abstract.text
            # avoid single quote problems with sql (It is a special character so we have to escape by making it -> '' )
            abstract = re.sub(r"[']", "''", abstract)
            howManyWords = len(abstract.split())
        else:
            abstract = 'NO ABSTRACT'
            hownManyWords = 0

        c.execute(
            f"INSERT OR IGNORE INTO document (document_id, title, total_words_not_unique) VALUES ('{xml}', '{abstract}', {howManyWords})")
        # store document with total word count and abstract contents

        if abstract:
            for word in abstract.split():
                j = j + 1
                word = re.sub(r"[,./;:()']", '', word)

                # print(word)

                if word and word != '':
                    c.execute(
                        f"SELECT word_id from word WHERE word = '{word}'")
                    row = c.fetchone()  # find if WORD EXISTS IN DATABASE ALREADY

                    if row and row[0]:  # if it exists, do nothing
                        id = str(row[0])
                        # c.execute(
                        #     f"INSERT OR IGNORE INTO word (word_id, word) VALUES ('{id}', '{word}')")
                    else:  # else, insert new word with a new id
                        id = str(j)
                        c.execute(
                            f"INSERT INTO word (word_id, word) VALUES ('{str(j)}', '{word}')")

                    c.execute(
                        f"SELECT word_id from word_in_document WHERE word_id = '{id}' AND document_id='{xml}'")
                    row = c.fetchone()  # find if word in document already exists in DATABASE

                    if row and row[0]:  # if it exists, increment quantity by 1
                        # print('update')
                        c.execute(
                            f"UPDATE word_in_document SET quantity = quantity + 1 WHERE word_id = '{id}' AND document_id = '{xml}'")
                    else:  # else, insert new word_in_document row
                        # print('insert')
                        c.execute(
                            f"INSERT INTO word_in_document (word_id, document_id, word, quantity) VALUES ('{id}', '{xml}', '{word}', 1)")


con.commit()

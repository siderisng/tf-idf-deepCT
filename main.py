# Create Database and connect to it

import re
import os
import glob
import math
import time
from bs4 import BeautifulSoup
import sqlite3 as sl
con = sl.connect('tf-idf.db')
con.close()
f = open('output.txt', 'w')

# extract abstracts from patents first and then
# Open a folder of files one by one, and create database to use for tf idt

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
# print("Tables created successfully")

path = 'clef_small_dataset'  # TODO LOOP THROUGH FOLDERS (00, 01, 02, ...)
# data = os.listdir(path)  # fakelos me xml arxeia
# print(data)

i = 0
j = 0
c = con.cursor()
total_count = 0
start = time.time()


for subdir, dirs, files in os.walk(path):
    total_count = total_count + len(files)

for subdir, dirs, files in os.walk(path):

    for file in files:
        xml = str(os.path.join(subdir, file))
        if ".DS_STORE" in xml:
            continue

        if (i % 200 == 0):
            end = time.time()
            print(xml + ' - ' + str(i) + ' of ' + str(total_count) +
                  ' === Time elapsed: ', '%.2f' % (end-start) + 's', end="\r")

        i = i + 1
        # if (i > 50):
        #     break

        # print(str(i) + ' of  ' + str(len(data)))
        patent = open(xml, 'r')

        root = BeautifulSoup(patent, features="html.parser")
        # print(root)
        abstract = root.find('abstract')

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
                    # print(row)
                    if row and row[0]:  # if it exists, increment quantity by 1
                        # print('update')
                        c.execute(
                            f"UPDATE word_in_document SET quantity = quantity + 1 WHERE word_id = '{id}' AND document_id = '{xml}'")
                    else:             # else, insert new word_in_document row
                        # print('insert')
                        c.execute(
                            f"INSERT INTO word_in_document (word_id, document_id, word, quantity) VALUES ('{id}', '{xml}', '{word}', 1)")


# TF-IDF

# tf = occurences of the word / total words (quantity, not unique words)

# idf = log (total number of documents / number of documents containing the word )

# tfIdf = tf * idf

# Calculate TF-IDF for every word_in_document


c.execute(f'select * from document')
all_docs = c.fetchall()
all_docs_n = len(all_docs)

c.execute(f'select * from word_in_document')
rows = c.fetchall()
for row in rows:
    word_id = row[1]
    doc_id = row[2]
    word = row[3]
    occurs = row[5]
    print(
        f'word {word} with word_id: {word_id} in doc: {doc_id} appears {occurs} times', file=f)

    c.execute(
        f"select total_words_not_unique from document where document_id = '{doc_id}'")
    row = c.fetchone()
    total_words = row[0]
    print(f"total words: {total_words}", file=f)

    tf = occurs / total_words

    print(f"tf is: {occurs} / {total_words} = {tf}", file=f)

    c.execute(f'select * from word_in_document where word_id = {word_id}')
    docs_with_word = c.fetchall()
    docs_with_word_n = len(docs_with_word)

    idf = math.log((all_docs_n / docs_with_word_n), 10)

    print(f"idf is: log({all_docs_n} / {docs_with_word_n}) = {idf}", file=f)

    tf_idf = tf * idf
    print(f"tf-idf is: {tf} X {idf} = {tf_idf}", file=f)

    c.execute(
        f"UPDATE word_in_document SET tf_idf = {tf_idf} where word_id = {word_id} AND document_id= '{doc_id}' ")

    print('========================', file=f)

# c.execute(f'select * from word_in_document')
# rows = c.fetchall();
# for row in rows:
#   print(row)


# Create docterm.recall for deepCT by using TF_IDF values calculated before

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

def cosine_similarity(documents):
# Scikit Learn
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    import pandas as pd

    # Create the Document Term Matrix
    count_vectorizer = CountVectorizer(stop_words='english') # or TfidfVectorizer
    count_vectorizer = CountVectorizer()
    sparse_matrix = count_vectorizer.fit_transform(documents)

    # OPTIONAL: Convert Sparse Matrix to Pandas Dataframe if you want to see the word frequencies.
    doc_term_matrix = sparse_matrix.todense()
    df = pd.DataFrame(doc_term_matrix, 
                    columns=count_vectorizer.get_feature_names_out(), 
                    index=['full', 'fields'])

    return cosine_similarity(df)[0][1]

def createDBEntriesForDocument(c, xml, finalText, howManyWords, j):
    c.execute(
        f"INSERT OR IGNORE INTO document (document_id, title, total_words_not_unique) VALUES ('{xml}', '{finalText}', {howManyWords})")
    # store document with total word count and abstract contents

    if finalText:
        k = 0
        for word in finalText.split():
            j = j + 1

            if (k > 512):
                break # we can't support more than 512 words for deepCT so no need to waste time with words that we won't use
            k = k + 1
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

        return j;

def createDBAndTables():
    if os.path.exists("tf-idf.sqlite"):
        os.remove("tf-idf.sqlite")
    
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

    return con


import re
import os
import time
import math
import sqlite3 as sl
from typing import final
from bs4 import BeautifulSoup
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--limit', '-l', help="how many patents? default is 100, 0 is unlimited", type= int, default=100)
parser.add_argument('--fields', '-f', help="which fields to use, separated by comma (,)? default is abstract,title", type= str, default='abstract,title')

args = parser.parse_args()
# LIMIT = args.limit == 0 ? math.inf : args.limit;  
LIMIT = math.inf if args.limit == 0 else args.limit
print ('LIMIT is ' + str(LIMIT))
FIELDS = args.fields.split(',')
print ('FIELDS: ' + str(FIELDS))

f = open('output.txt', 'w')  # open output.txt for storing output

# create tables for my DB
con = createDBAndTables();

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
            
        howManyWords = len(finalText.split())

        # Calculate cosine similarity of extracted fields compared to full text
        all_text = root.find().text
        documents = [all_text, finalText]
        
        similarity = cosine_similarity(documents)
        print('Similarity between selected fields and full text is: ' + str(similarity))
        print('word count --- fullText: ' + str(len(all_text.split())) + ', fields: ' + str(howManyWords))

        j = createDBEntriesForDocument(c, xml, finalText, howManyWords, j)


con.commit()



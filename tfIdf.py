import sqlite3 as sl
import math
import time

# TF-IDF

# tf = occurences of the word / total words (quantity, not unique words)

# idf = log (total number of documents / number of documents containing the word )

# tfIdf = tf * idf

def runTfIdf(docId): 
    # Calculate TF-IDF for every word_in_document.
    f = open('output.txt', 'w',encoding='utf-8')  # open output.txt for storing output

    con = sl.connect('tf-idf.sqlite')
    c = con.cursor()

    c.execute(f'select * from document')
    all_docs = c.fetchall()
    all_docs_n = len(all_docs)

    c.execute(f"select * from word_in_document where document_id = '{docId}'")
    rows = c.fetchall()
    i = 0
    start = time.time()
    total = len(rows)

    for row in rows:
        if (i % 200 == 0):
            end = time.time()
            print(str(i) + ' of ' + str(total) +
                ' === Time elapsed: ', '%.2f' % (end-start) + 's', end='\r')
            start = time.time()

        i = i + 1

        word_id = row[1]
        doc_id = row[2]
        word = row[3]
        occurs = row[5]
        tfidf_result = row[4]
        if (row[4] != None):  # skip words that td-idf had already been calculated
            continue

        print(
            f'word {word} with word_id: {word_id} in doc: {doc_id} appears {occurs} times', file=f, )

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

    con.commit()
    f.close();

def getBestWords(docId, limit):
    # print('==========')
    con = sl.connect('tf-idf.sqlite')
    c = con.cursor()

    c.execute(f"SELECT * FROM word_in_document WHERE document_id='{docId}'")
    rows = c.fetchall();


    def score(e):
        return e[4] # tf-idf score

    rows.sort(key=score, reverse= True)

    # print('==========')

    final = ''

    for ind, row in enumerate(rows):
        if ind > limit:
            break

        i = 0;
        while i < int(row[5]):
            i = i + 1;
            final += row[3] + ' '


    # print(final)
    return final

# main()

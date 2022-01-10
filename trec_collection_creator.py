import os
import math
import time
from bs4 import BeautifulSoup

path = '/Users/giorgossideris/Downloads/final_clef_ip'
LIMIT = int(input(
    'how many patent documents to scan? default is 100, type 0 for unlimited:  '))
# LIMIT = args.limit == 0 ? math.inf : args.limit;
LIMIT = math.inf if LIMIT == 0 else LIMIT

FIELDS = input(
    'Which fields do you want to process? separated by comma (,)? default is abstract,title: ')

if not FIELDS:
    FIELDS = 'abstract,title'

fieldsName = FIELDS.replace(',','-')

if not os.path.exists('trec_collections/'):
    os.makedirs('trec_collections/')

if not os.path.exists('trec_collections/' + fieldsName):
    os.makedirs('trec_collections/' + fieldsName)


start = time.time()

i = 0

for subdir, dirs, files in os.walk(path):
    for file in files:

        xml = str(os.path.join(subdir, file))
        patent = open(xml, 'r', encoding='utf-8')
        root = BeautifulSoup(patent, features="html.parser")
        documentId = file.replace('.txt', '')

        outPath = 'trec_collections/' + fieldsName + '/' + documentId + '.trec'

        with open(outPath, 'w', encoding='utf-8') as writer:
            writer.write('<DOC> \n<DOCNO>' + documentId + '</DOCNO> \n')
            
            titles = root.findAll('title');
            if titles:
                for title in titles: 
                    if title.text:
                        writer.write('<TITLE>' + title.text + '</TITLE>\n')

            abstracts = root.findAll('abstract');
            if abstracts:
                for abstract in abstracts: 
                    if abstract.text:
                        writer.write('<ABSTRACT>' + abstract.text + '</ABSTRACT>\n')

            descriptions = root.findAll('description');
            if descriptions:
                for description in descriptions: 
                    if description.text:
                        writer.write('<DESCRIPTION>' + description.text + '</DESCRIPTION>\n')

            claims = root.findAll('claims');
            if claims:
                for claim in claims: 
                    if claim.text:
                        writer.write('<CLAIMS>' + claim.text + '</CLAIMS>\n')

                
            writer.write('</DOC>')

        i = i + 1
        if (i > LIMIT):
            break

    if (i > LIMIT):
        break



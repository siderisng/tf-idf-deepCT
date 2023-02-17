import os
from pyserini.search import SimpleSearcher


#the name of the results file
results_file_name = 'inf-description-predict-without-training.res'

#the path you want the results to be saved
results_path = 'query_results/'

#the path to the queries
topics_path_300 = '300_topics_set3_EN.txt'

#the path to the index to be searched
index_path = 'pyserini_indexes/description/deepCT/predict-without-training'


topics = open(topics_path_300, "r", encoding= 'utf-8').read()
topics = topics.split('<seperator>')
searcher_centralized = SimpleSearcher(index_path)
counter = 0
with open(results_path + results_file_name, 'w', encoding='utf-8') as writer:
    for topic in topics:
        ind = 1
        topic = topic.split('<id_sep>')
        topic_text = topic[1]
        topic_id = topic[0]
        topic_text = topic_text.split()
        topic_text = topic_text[0:1000]
        topic_text = " ".join(topic_text)

        #Search centralized index
        results_centralized = searcher_centralized.search(topic_text, 1000)


        for res in results_centralized:
           writer.write(topic_id + ' ' + 'Q0' + ' ' + res.docid + ' ' + str(ind) + ' ' + str(res.score) + ' ' + 'ML_MERGING' + '\n')
           ind += 1
        #break
        if counter % 50 == 0:
            print(counter)
        counter += 1

with open(results_path+"no_dups.res", "w", encoding="utf-8") as writer:
    with open(results_path + results_file_name, "r", encoding="utf-8") as file:
        id_list = []
        current = 'EP-1310580-A2'
        for line in file:
            line2 = line.split()

            if line2[0] == current and (line2[2] in id_list):
                continue
            elif line2[0] == current and (line2[2] not in id_list):
                id_list.append(line2[2])
                writer.write(line2[0] + " " + line2[1] + " " + line2[2] + " " + line2[3] + " " + line2[4] + " " + line2[5] + "\n")
            else:
                current = line2[0]
                writer.write(line2[0] + " " + line2[1] + " " + line2[2] + " " + line2[3] + " " + line2[4] + " " + line2[5] + "\n")
                id_list = []
                id_list.append(line2[2])

os.remove(results_path + results_file_name)
os.rename(results_path+'no_dups.res', results_path+results_file_name)
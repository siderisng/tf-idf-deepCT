import subprocess
import os

EXPERIMENT_NAME = 'abstract'


data_dir = 'output/' + EXPERIMENT_NAME + '/train_files/'

with open('train_files_used.txt', 'a+') as writer:

	

	for train_file in os.listdir(data_dir):
		used = []
		for i in writer:
			used.append(i)
		if train_file in used:
			continue

		subprocess.run("python DeepCT-master/run_deepct.py --data_dir=output/" + EXPERIMENT_NAME + "/train_files/" + train_file + " --vocab_file=bert-base-uncased/vocab.txt --bert_config_file=bert-base-uncased/bert_config.json --init_checkpoint=output/" + EXPERIMENT_NAME + "/train/model.ckpt-0 --output_dir=output/" + EXPERIMENT_NAME + "/train --do_train=true --task_name=marcodoc --num_train_epochs=5.0 --train_batch_size=16", shell=True, check=True, capture_output=True)
        
		writer.write(train_file+"\n")
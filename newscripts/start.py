import subprocess
import os

EXPERIMENT_NAME = 'inf-description'





data_dir = 'output/' + EXPERIMENT_NAME + '/train_files/'

for train_file in os.listdir(data_dir):

    subprocess.run("/home/giorgos/anaconda3/envs/saved-env-deepCT/bin/python DeepCT-master/run_deepct.py	--data_dir=output/" + EXPERIMENT_NAME + "/train_files/"  + train_file + "	--vocab_file=bert-base-uncased/vocab.txt	--bert_config_file=bert-base-uncased/bert_config.json	--init_checkpoint=bert-base-uncased/bert_model.ckpt	--output_dir=output/" + EXPERIMENT_NAME + "/train	--do_train=true	--task_name=marcodoc	--num_train_epochs=1.0	--train_batch_size=16	", shell=True, check=True, capture_output=True)

	
    break
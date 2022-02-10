# INSTRUCTIONS

_run in Mac OS, Linux or WSL inside Windows_

## Install conda

link below for 64-bit linux:

```bash
wget https://repo.anaconda.com/archive/Anaconda3-2020.02-Linux-x86_64.sh
```

Run after download to install:

```bash
bash Anaconda3-2020.02-Linux-x86_64.sh
```

## Import conda environments

### First env is for deepCT and my custom scripts

```bash
conda-env create -n saved-env-deepCT -f=conda_envs/saved-env-deepCT.yml
```

### Second env is for pyserini

```bash
conda-env create -n saved-env-pyserini -f=conda_envs/saved-env-pyserini.yml
```

## Create DB from patent files

### Activate deepCT conda env

```bash
conda activate saved-env-deepCT
```

### Get conda env's python path to be sure we are using the right python executable

```bash
echo $CONDA_PREFIX
```

_will be something like `/Users/giorgossideris/opt/anaconda3/envs/saved-env-deepCT`_

### Create db

_IMPORTANT (before runnning `create-db.py`, edit path of patents inside file to correspond to the correct location in your filesystem)_
_sample files are included in the repo, if you want to use those, change path in file to `sample_patents`_

```bash
<PYTHON_PATH_FROM_PREVIOUS_STEP>/bin/python ./create-db.py
```

_keep the limit and fields you used in mind to use later for parameters eg. if you used limit 0 and fields claims,abstract, these 2 values will be used below as `EXPERIMENT_NAME`, in this case `0-claims,abstract`_

## Change to pyserini env and calculate tf-idf scores

### Change to pyserini env

```bash
conda activate saved-env-pyserini
```

### Get conda env's python path to be sure we are using the right python executable

```bash
echo $CONDA_PREFIX
```

### Run pyserini inverted index creation

```bash
<PYTHON_PATH_FROM_PREVIOUS_STEP>/bin/python -m pyserini.index --input jsonl/<EXPERIMENT_NAME> --collection JsonCollection --generator DefaultLuceneDocumentGenerator --index indexes/<EXPERIMENT_NAME> --stemmer=none --threads 1 --storePositions --storeDocvectors --storeRaw
```

### Calculate tf idf scores with pyserini

```bash
<PYTHON_PATH_FROM_PREVIOUS_STEP>/bin/python pyserini_tfIdf.py
```

## Run deepCT training and prediction

### Change to deepCT env

```bash
conda activate saved-env-deepCT
```

### Get conda env's python path to be sure we are using the right python executable

```bash
echo $CONDA_PREFIX`
```

### Run deepCT training

_before running deepCT training download <https://storage.googleapis.com/bert_models/2020_02_20/uncased_L-12_H-768_A-12.zip>, unzip and copy bert_model.ckpt.data-00000-of-00001 to folder bert-base-uncased_

```bash
<PYTHON_PATH_FROM_PREVIOUS_STEP>/bin/python DeepCT-master/run_deepct.py --data_dir=output/<EXPERIMENT_NAME>/train.docterm_recall --vocab_file=bert-base-uncased/vocab.txt --bert_config_file=bert-base-uncased/bert_config.json --init_checkpoint=bert-base-uncased/bert_model.ckpt --output_dir=output/<EXPERIMENT_NAME>/train --do_train=true --task_name=marcodoc --num_train_epochs=5.0 --train_batch_size=16
```

### Create file needed for deepCT predit

```bash
<PYTHON_PATH_FROM_PREVIOUS_STEP>/bin/python ./create-file-for-edit.py
```

_ΙMPORTANT: remove all lines with empty content before moving on to the next step_

### Run deepCT prediction

```bash
<PYTHON_PATH_FROM_PREVIOUS_STEP>/bin/python DeepCT-master/run_deepct.py --task_name=marcotsvdoc --do_train=false --do_eval=false --do_predict=true --data_dir=output/<EXPERIMENT_NAME>/edit.tsv --vocab_file=bert-base-uncased/vocab.txt --bert_config_file=bert-base-uncased/bert_config.json --init_checkpoint=output/<EXPERIMENT_NAME>/train/model.ckpt-0 --max_seq_length=128 --train_batch_size=16 --learning_rate=2e-5 --num_train_epochs=3.0 --output_dir=output/<EXPERIMENT_NAME>/predict
```

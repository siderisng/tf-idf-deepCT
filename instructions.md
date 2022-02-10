# INSTRUCTIONS

_run in Mac OS, Linux or WSL inside Windows_

### install conda

link below for 64-bit linux

`wget https://repo.anaconda.com/archive/Anaconda3-2020.02-Linux-x86_64.sh`

after download install

`bash Anaconda3-2020.02-Linux-x86_64.sh`

### import conda environments

`conda-env create -n saved-env-deepCT -f=conda_envs/saved-env-deepCT.yml`
`conda-env create -n saved-env-pyserini -f=conda_envs/saved-env-pyserini.yml`

conda-env create -n my_env -f= my_env.yml

echo $CONDA_PREFIX
/Users/giorgossideris/opt/anaconda3/envs/saved-env-deepCT

/Users/giorgossideris/opt/anaconda3/envs/saved-env-deepCT/bin/python ./create-db.py

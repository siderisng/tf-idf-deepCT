# tf-idf-deepCT

Prequisites:

- Install beautifulSoup `pip install bs4`

Steps:

- run `create-db.py`
```
usage: create-db.py [-h] [--limit LIMIT] [--fields FIELDS]

optional arguments:
  -h, --help            show this help message and exit
  --limit LIMIT, -l LIMIT
                        how many patents? default is 100, 0 is unlimited
  --fields FIELDS, -f FIELDS
                        which fields to use, separated by comma (,)? default is abstract,title
```

example run: `py .\create-db.py -l=0 -f abstract,title,inventor`

_(run for unlimited patent documents, process fields: abstract, title, inventor)_

- run `tf-idf.py`

- run `create-file-for-deepCT.py`

- use `.docterm_recall` file to train deepCT (TODO)

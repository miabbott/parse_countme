# parse_countme

![Pylint](https://github.com/miabbott/parse_countme/actions/workflows/pylint.yml/badge.svg)

Script for parsing Fedora countme data

```
usage: main.py [-h] [-a] [-d DIR] [-o OUTPUT] [-u] variant

positional arguments:
  variant               Name of the os_variant to query

options:
  -h, --help            show this help message and exit
  -a, --all             Query stats from all time; default is last year
  -d DIR, --dir DIR     Directory to download totals.db and write out CSV file; defaults to $CWD
  -o OUTPUT, --output OUTPUT
                        Filename to write results in CSV format; defaults to 'stats.csv'
  -u, --update          Force update of totals.dbr
```

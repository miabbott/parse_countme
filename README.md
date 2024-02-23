# parse_countme
Script for parsing Fedora countme data

```
usage: main.py [-h] [-d DIR] [-u] [-a] variant

positional arguments:
  variant            Name of the os_variant to query

options:
  -h, --help         show this help message and exit
  -d DIR, --dir DIR  Directory to download totals.db; defaults to $CWD
  -u, --update       Force update of totals.db
  -a, --all          Query stats from all time; default is last year
```

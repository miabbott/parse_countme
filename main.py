#!/usr/bin/python3

# Script for parsing Fedora countme data
# Originally implemented in bash by @travier

import argparse
import os
import os.path
import re
import sqlite3
import sys
import time
from contextlib import closing
from datetime import datetime

import requests
from tqdm import tqdm


# https://github.com/fedora-infra/mirrors-countme/blob/039f453998711fa360dd5ecc882eb87df9e45d2b/mirrors_countme/constants.py
DAY_LEN = 24 * 60 * 60  # seconds in a day
WEEK_LEN = 7 * DAY_LEN  # seconds in a week
COUNTME_EPOCH = 345600  # unix epoch: 1970-01-04

YEAR_LEN = 365 * DAY_LEN  # seconds in a year

TOTALSDB_FILENAME = "totals.db"
TOTALSDB_URL = "https://data-analysis.fedoraproject.org/csv-reports/countme/totals.db"


# download totals.db to directory
def download_stats(totals_db_path, update=False):
    if not os.path.exists(totals_db_path) or update:
        req = requests.get(TOTALSDB_URL, stream=True, timeout=60)

        total_size = int(req.headers.get("content-length", 0))
        block_size = 1024

        with tqdm(total=total_size, unit="8", unit_scale=True) as progress_bar:
            with open(totals_db_path, "wb") as f:
                for chunk in req.iter_content(block_size):
                    progress_bar.update(len(chunk))
                    f.write(chunk)


# convert week_num from totals.db to readable date (DD-MMM-YYYY)
def make_datetime(week_num):
    t = (int(week_num) * int(WEEK_LEN)) + int(COUNTME_EPOCH)
    return datetime.fromtimestamp(t).strftime("%d-%b-%Y")


# https://github.com/fedora-infra/mirrors-countme/blob/039f453998711fa360dd5ecc882eb87df9e45d2b/mirrors_countme/util.py#L31-L32
# convert a timestamp to weeknum in totals.db
def make_weeknum(timestamp):
    return (int(timestamp) - COUNTME_EPOCH) // WEEK_LEN


# run the queries against totals.db
def query_db(db_file, variant, alltime=False):
    # https://gist.github.com/eestrada/fd55398950c6ee1f1deb
    def regexp(y, x, search=re.search):
        return 1 if search(y, x) else 0

    # calculate the weeknum value from a year ago
    if not alltime:
        ts = int(time.time()) - YEAR_LEN
        year_ago_weeknum = make_weeknum(ts)
        ya_sql_addition = f"AND weeknum > {year_ago_weeknum}"

    # number of instances either all time or from the last year
    num_instance_sql = f"SELECT weeknum, SUM(hits) FROM countme_totals WHERE os_variant IS '{variant}' AND repo_tag REGEXP 'updates-released-f[3-4][0-9]' AND sys_age > 1 {ya_sql_addition if not alltime else ""} GROUP BY weeknum"
    # number of instances per version for the last week
    num_instance_per_version_sql = f"SELECT os_version, SUM(hits) FROM countme_totals WHERE os_variant IS '{variant}' AND repo_tag REGEXP 'updates-released-f[3-4][0-9]' AND sys_age > 1 AND weeknum = (SELECT MAX(weeknum) FROM countme_totals) GROUP BY os_version ORDER BY os_version"
    # number of instances per arch for the last week
    num_instances_per_arch_sql = f"SELECT os_variant, repo_arch, SUM(hits) FROM countme_totals WHERE os_variant IS '{variant}' AND repo_tag REGEXP 'updates-released-f[3-4][0-9]' AND sys_age > 1 AND weeknum = (SELECT MAX(weeknum) FROM countme_totals) GROUP BY repo_arch ORDER BY repo_arch"

    with closing(sqlite3.connect(db_file)) as connection:
        connection.create_function('regexp', 2, regexp)
        cursor = connection.cursor()
        rows = cursor.execute(num_instance_sql).fetchall()
        print(rows)
        rows = cursor.execute(num_instance_per_version_sql).fetchall()
        print(rows)
        rows = cursor.execute(num_instances_per_arch_sql).fetchall()
        print(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('variant', help="Name of the os_variant to query")
    parser.add_argument('-d', '--dir', help="Directory to download totals.db; defaults to $CWD")
    parser.add_argument('-u', '--update', action="store_true", help="Force update of totals.db")
    parser.add_argument('-a', '--all', action="store_true", help="Query stats from all time; default is last year")
    args = parser.parse_args()

    if args.dir is None:
        stats_dir = os.getcwd()
    else:
        stats_dir = args.dir

    totals_db_path = os.path.join(stats_dir, TOTALSDB_FILENAME)

    if args.update:
        download_stats(totals_db_path, update=True)
    else:
        download_stats(totals_db_path)

    query_db(totals_db_path, args.variant, args.all)


if __name__ == '__main__':
    sys.exit(main())

import os
from os.path import join

ROOT_DIR = os.path.abspath(join("../bot.py", '..'))
DATA_DIR = join(ROOT_DIR,"data")
DB_DATA = join(ROOT_DIR, "../database", "data", "data.db")
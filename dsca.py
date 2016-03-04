#!/usr/bin/env python3
import tkinter as tk
import sys, os, sqlite3, logging
from db import Database
from gui import Gui

DB_PATH = "~/.dsc_anaylsis"
DB_NAME = "data.sqlite"

logging.basicConfig(format="%(levelname)s %(asctime)s %(message)s",
        level=logging.INFO,datefmt="%Y-%d-%m %H:%M:%S")


def find_database():
    '''
    Finds whether a database file exists based on a statically
    defined path and database name.

    @return Full path to database if found, or None otherwise
    '''
    db_fullpath = os.path.expanduser("{}/{}".format(DB_PATH,DB_NAME))
    if not os.path.exists(db_fullpath):
        logging.info("database does not exist")
        return None
    # eventually maybe we also want to
    # check an environment variable
    return db_fullpath


def create_database():
    '''
    Creates database file and full containing directory path if necessary.

    @return Full path to the newly created database.
    '''
    dirpath = os.path.expanduser(DB_PATH)
    if not os.path.exists(dirpath):
        logging.info("creating new directory: {}".format(dirpath))
        os.makedirs(dirpath)
    if not os.path.exists(dirpath):
        logging.critical("failed to create directory {}".format(dirpath))
        sys.exit(1)
    db_fullpath = "{}/{}".format(dirpath,DB_NAME)
    # don't clobber the database if it's already there
    if os.path.exists(db_fullpath):
        logging.critical("database already exists")
        sys.exit(1)
    logging.info("creating database: {}".format(db_fullpath))
    Database.write_db_schema(db_fullpath)
    return db_fullpath


def main():

    db_path = find_database()
    if db_path == None:
        db_path = create_database()

    db = Database(db_path)
    gui = Gui("DSC Analyzer")


if __name__ == "__main__":
    main()

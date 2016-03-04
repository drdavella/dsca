import sqlite3, logging

DB_SCHEMA =
'''


'''


class Database():

    @classmethod
    def write_db_schema(cls,filename):
        '''
        Creates file and writes database schema at the specified path.

        @param filename Full path to database to be created
        '''
        pass

    def __init__(self,filename):
        '''
        Creates database object from file at given path.

        @param filename Full path representing the database file
        '''
        logging.info("opening database connection")
        pass

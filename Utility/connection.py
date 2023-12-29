import os
import traceback
import pyodbc
import pandas as pd
DATABASE_NAME = os.environ.get('DB_NAME','sqldb-pay-toscana-db-dev')
DATABASE_USER = os.environ.get('DB_USER','sqldb-exacto-main')
DATABASE_PASSWORD = os.environ.get('DB_PASSWORD','7Odo0aS5e!*3!f2P$Kno7Hq#c')
DATABASE_HOST = os.environ.get('DB_HOST','sqldb-pay-toscana-dbsrv.database.windows.net')
DATABASE_PORT = os.environ.get('DB_PORT','1433')

def connect_db():
    try:

        mydb = pyodbc.connect('Driver={SQL Server};' +

                              'Server={};'.format(DATABASE_HOST) +

                              'port={};'.format(DATABASE_PORT) +

                              'Database={};'.format(DATABASE_NAME) +

                              'uid={};'.format(DATABASE_USER) +

                              'pwd={};'.format(DATABASE_PASSWORD) +

                              'autocommit=True;'

                              )
        print('This is executed')
        return mydb
    except:
        print('Exception')
        print(traceback.print_exc())

connect_db()





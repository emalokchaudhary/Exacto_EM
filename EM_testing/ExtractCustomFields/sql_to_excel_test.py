import uuid
import pyodbc
import pandas as pd
import os
import sys
import traceback
#from  .datadrive.EM_Product.ips.invoiceProduct_solution.apps.db_connection import *  #datadrive/EM_Product/ips/invoiceProduct_solution/apps/db_connection.py
from db_connection import connect_db
sys.path.insert(0,'../..')
def sql_to_excel():
    conn = connect_db()
    # cursor = conn.cursor()
    table_name = "exacto_inv_qnt_li"
    insert_query = f'SELECT * FROM {table_name}'
    # print("Invoice Query------", insert_query)
    # cursor.execute(insert_query)
    df=pd.read_sql(insert_query,conn)
    df.to_excel('test_data_excel12.xlsx',index=False)
    conn.close()
# sql_to_excel()

#import MySQLdb
from flask import Flask, jsonify, request, send_from_directory, make_response
from flask_cors import CORS, cross_origin
import json
import shutil
import re, os
import time
import codecs
import traceback

from collections import OrderedDict
import pyodbc

def get_new_db_connection():
  try:
      mydb = pyodbc.connect('Driver={ODBC Driver 13 for SQL Server};'
                        'Server=127.0.0.1;'
                        'port=1433;'
                        'Database=db_exacto;'
  		                  'uid=SA;'
  		                  'pwd=Exacto_Prod;'
  		                  'autocommit=True;'
                          )
  except:
  	print(traceback.print_exc())
  return mydb

           	                
# mydb.set_attr(pyodbc.SQL_ATTR_TXN_ISOLATION, pyodbc.SQL_TXN_SERIALIZABLE)

def safe_create_db_tables():
  mydb = get_new_db_connection()
  mycursor = mydb.cursor()

  mycursor.execute("""IF NOT EXISTS (SELECT * FROM sys.objects WHERE name='predictedData')
  BEGIN
  CREATE TABLE predictedData(fileName VARCHAR(555) NOT NULL,PONumber VARCHAR(555),invoiceNumber VARCHAR(555),taxAmount VARCHAR(555),invoiceDate VARCHAR(555),netAmount VARCHAR(555),referencePerson VARCHAR(555),supplierName VARCHAR(555),shippingAmount VARCHAR(555),currency VARCHAR(555),invoiceCredit VARCHAR(555),deliveryNoteNumber VARCHAR(555),verificationNumber VARCHAR(555),bankAccount VARCHAR(555),dateCreated VARCHAR(555),Audited_Y_N VARCHAR(555),Lock_Acquired VARCHAR(555),cPONumber NVARCHAR(50),cinvoiceNumber NVARCHAR(50),ctaxAmount NVARCHAR(50),cinvoiceDate NVARCHAR(50),cnetAmount NVARCHAR(50),creferencePerson NVARCHAR(50),csupplierName NVARCHAR(50),cshippingAmount NVARCHAR(50),ccurrency NVARCHAR(50),cinvoiceCredit NVARCHAR(50),cdeliveryNoteNumber NVARCHAR(50),cverificationNumber NVARCHAR(50),cbankAccount NVARCHAR(50),filePath VARCHAR(555),deliveryAddress VARCHAR(555),cdeliveryAddress VARCHAR(55),tax1 VARCHAR(555),ctax1 VARCHAR(55),tax2 VARCHAR(555),ctax2 VARCHAR(55),tax3 VARCHAR(555),ctax3 VARCHAR(555),taxAmount1 VARCHAR(555),ctaxAmount1 VARCHAR(55),taxAmount2 VARCHAR(555),ctaxAmount2 VARCHAR(55),taxAmount3 VARCHAR(555),ctaxAmount3 VARCHAR(55),companyCode VARCHAR(555),ccompanyCode VARCHAR(55),vatNumber VARCHAR(555),cvatNumber VARCHAR(55),fileClassifier  VARCHAR(55), predicted_id INT NOT NULL IDENTITY(1,1) ,PRIMARY KEY (predicted_id)) ; 
  END""");
  mycursor.commit()

  sql_command ="""IF NOT EXISTS (SELECT * FROM sys.objects WHERE name='auditedData')
  BEGIN
  CREATE TABLE auditedData(fileName VARCHAR(555) NOT NULL,PONumber VARCHAR(555),invoiceNumber VARCHAR(555),taxAmount VARCHAR(555),invoiceDate VARCHAR(555),netAmount VARCHAR(555),referencePerson VARCHAR(555),supplierName VARCHAR(555),shippingAmount VARCHAR(555),currency VARCHAR(555),invoiceCredit VARCHAR(555),deliveryNoteNumber VARCHAR(555),verificationNumber VARCHAR(555),bankAccount VARCHAR(555),dateCreated VARCHAR(555),Audited_Y_N VARCHAR(55),Lock_Acquired VARCHAR(55),cPONumber NVARCHAR(50),cinvoiceNumber NVARCHAR(50),ctaxAmount NVARCHAR(50),cinvoiceDate NVARCHAR(50),cnetAmount NVARCHAR(50),creferencePerson NVARCHAR(50),csupplierName NVARCHAR(50),cshippingAmount NVARCHAR(50),ccurrency NVARCHAR(50),cinvoiceCredit NVARCHAR(50),cdeliveryNoteNumber NVARCHAR(50),cverificationNumber NVARCHAR(50),cbankAccount NVARCHAR(50),filePath VARCHAR(555),deliveryAddress VARCHAR(555),cdeliveryAddress VARCHAR(55),tax1 VARCHAR(555),ctax1 VARCHAR(55),tax2 VARCHAR(555),ctax2 VARCHAR(55),tax3 VARCHAR(555),ctax3 VARCHAR(555),taxAmount1 VARCHAR(555),ctaxAmount1 VARCHAR(55),taxAmount2 VARCHAR(555),ctaxAmount2 VARCHAR(55),taxAmount3 VARCHAR(555),ctaxAmount3 VARCHAR(55),companyCode VARCHAR(555),ccompanyCode VARCHAR(55),vatNumber VARCHAR(555),cvatNumber VARCHAR(55),fileClassifier  VARCHAR(55),audited_id INT NOT NULL IDENTITY(1,1) ,PRIMARY KEY (audited_id)) 
  END""";
  mycursor.execute(sql_command)
  mycursor.commit()

  sql_command ="""IF NOT EXISTS (SELECT * FROM sys.objects WHERE name='tableData')
  BEGIN
  CREATE TABLE tableData(fileName VARCHAR(555) NOT NULL, line_No VARCHAR(555),articleNumber VARCHAR(555),orderNumber VARCHAR(555),quantity VARCHAR(555),UOM VARCHAR(555),description VARCHAR(555),unitPrice VARCHAR(555),rowAmount VARCHAR(555),deliveryNote VARCHAR(555),table_id INT NOT NULL IDENTITY(1,1) ,PRIMARY KEY (table_id)) 
  END""";
  mycursor.execute(sql_command)
  mycursor.commit()

  sql_command ="""IF NOT EXISTS (SELECT * FROM sys.objects WHERE name='auditedTableData')
  BEGIN
  CREATE TABLE auditedTableData(fileName VARCHAR(555) NOT NULL,line_No VARCHAR(555),articleNumber VARCHAR(555),orderNumber VARCHAR(555),quantity VARCHAR(555),UOM VARCHAR(555),description VARCHAR(555),unitPrice VARCHAR(555),rowAmount VARCHAR(555),deliveryNote VARCHAR(555),auditedTable_id INT NOT NULL IDENTITY(1,1) ,PRIMARY KEY (auditedTable_id)) 
  END""";
  mycursor.execute(sql_command)
  mycursor.commit()

  print("Database Tables Created Successfully!!!!!")
  return mydb




import uuid
import pyodbc
import os,sys
#from  .datadrive.EM_Product.ips.invoiceProduct_solution.apps.db_connection import *  #datadrive/EM_Product/ips/invoiceProduct_solution/apps/db_connection.py
from db_connection import connect_db
from CGI_Invoice_headers import *
from CGI_Invoice_lineitems import *
from CGI_Quantity_headers import *
from CGI_qlty_lineitem import *
from CGI_Quality_headers import *
from CGI_qlty_lineitem import *
from CGI_Quality_headers import *


from CGI_nomination_headers_1 import Nomination_header_field
from CGI_Nomination_Table_main import main_call
from CGI_Nomiantion_final_table_exxon import Quality_line_items
import re
sys.path.insert(0,'../..')


def Nomination_Insertion(path):

    file=open(path,'r',encoding='windows-1258')
    read=file.read()
    lines=read.split('\n')

    conn = connect_db()
    cursor = conn.cursor()
    # row = Nomination_field(lines)
    match = re.search('\s*(Documentary Instructions:).*',read)
    if match:
        try:
            data_1 = Nomination_header_field(lines)
            data_2 = main_call(read)
            data_3 = Quality_line_items(lines)
            print('**********************************',data_3)
            UUID = str(uuid.uuid4().hex[:8])
            data_1['status'] = 0
            data_1['nom_hd_uuid'] = UUID
            insert_statement_1 = "INSERT INTO exacto_nom_hd(nom_hd_uuid, TripNumber, NominationNumber, Region, status  ) VALUES (?, ?, ?, ?, ?)"
            try:
                values_1 = (data_1.get('nom_hd_uuid',''),data_1.get('TripNumber',''), data_1.get('NominationNumber',''), data_1.get('Region',''), data_1.get('status',0))

                cursor.execute(insert_statement_1, values_1)
            except:
                print("Error occured in nomination headers")

            insert_statement_2 = "INSERT INTO exacto_nom_li(nom_hd_uuid, ActivityType, VendorName , ProductName, NominatedQuantity, UnitOfMeasure, JobLocation, JobDate ,EmAffiliates, NominationKey, VesselName, status ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

            insert_statement_3 = "INSERT INTO exacto_nom_ql_li( nom_hd_uuid ,SetNo ,SetDescription ,SampleLocation ,VendorName ,TestName ,TestCode ,Comments,status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            
            try:
                for table_data in data_2:

                    for row in table_data:
                        row['status'] = 0
                        row['nom_hd_uuid'] = UUID
                        print(row)
                        values_2 = (row.get('nom_hd_uuid',''), row.get('ActivityType',''), row.get('VendorName',''),  row.get('ProductName',''), row.get('NominatedQuantity',''), row.get('UnitOfMeasure',''), row.get('JobLocation',''), row.get('JobDate','')  ,row.get('EmAffiliates',''), row.get('NominationKey',''), row.get('VesselName','') ,row.get('status',0))

                        cursor.execute(insert_statement_2, values_2)
            except:
                print("Error occured in nomination line items")

            try:
                for table_data in data_3:

                    for row in table_data:
                        row['status'] = 0
                        row['nom_hd_uuid'] = UUID

                        values_3 = (row.get('nom_hd_uuid',''), row.get('SetNo',''), row.get('SetDescription','') ,row.get('SampleLocation',''),row.get('VendorName','') ,row.get('TestName',''), row.get('TestCode',''), row.get('Comments',''), row.get('status',0))

                        cursor.execute(insert_statement_3, values_3)
            except:
                print("Error occured in nomination quality line items")

            conn.commit()
            cursor.close()
            conn.close()
        except:
            print("Error in Nomination Insertion")


def cgi_invoice_db_insertion(inp_path):
    conn=connect_db()
    cursor=conn.cursor()
    UUID_invoice_header = str(uuid.uuid4().hex[:8])
    table_name="exacto_inv_hd"
    final_dict_hd=cgi_invoice_headers_extraction(read_textfile(inp_path),'0')
    values=[UUID_invoice_header,0]
    col_hd=['inv_hd_uuid',"status"]
    try:
        for i in final_dict_hd:
            col_hd.append(i)
        for j in  final_dict_hd:
            values.append(final_dict_hd.get(j,''))
        insert_query=f'INSERT INTO {table_name} ({", ".join(col_hd)}) VALUES {tuple(values)}'
        print(insert_query)
        cursor.execute(insert_query)
        cursor.commit()
    except:
        print("1.ERROR OCCURED DURING INSERTION OF INVOICE HEADERS :(")
    final_dict_li=cgi_lineitem_main(inp_path)
    try:
        col_li=['inv_hd_uuid','status','Description','QuantityValue','Price']
        # col_qnt_li = ['inv_hd_uuid', 'status',
        #               'Description', 'QuantityValue', 'Price','UoM','Category','SubCategory']
        for i in final_dict_li:
            if(i=='Quantity'):
                table_name_qnt_li="exacto_inv_qnt_li"
                for j in final_dict_li[i]:
                    valuesli=[UUID_invoice_header,0]
                    for k in j:
                        valuesli.append(j.get(k,''))
                    insert_query_li=f'INSERT INTO {table_name_qnt_li} ({", ".join(col_li)}) VALUES {tuple(valuesli)}'
                    print(insert_query_li)
                    cursor.execute(insert_query_li)
                    cursor.commit()
            elif(i=='quality'):
                table_name_qnt_li="exacto_inv_qlt_li"
                for j in final_dict_li[i]: 
                    valuesli=[UUID_invoice_header,0]
                    for k in j:
                        valuesli.append(j.get(k,''))
                    insert_query_li=f'INSERT INTO {table_name_qnt_li} ({", ".join(col_li)}) VALUES {tuple(valuesli)}'
                    print(insert_query_li)
                    cursor.execute(insert_query_li)
                    cursor.commit()
    except:
        print("2. ERROR OCCOURED DURING INSERTION OF INVOICE LINEITEM")
    cursor.close()
    print(insert_query)



def cgi_quantity_db_insertion(inp_path1):
    conn=connect_db()
    cursor=conn.cursor()
    UUID_quantity_header =str(uuid.uuid4().hex[:8])
    table_name="exacto_qnt_hd"
    final_dict_hd=cgi_quantity_headers_extraction(read_textfile(inp_path1))
    #print(fi)
    values=[UUID_quantity_header,0]
    col_hd=['qnt_hd_uuid',"status"]
    try:
        for i in final_dict_hd:
            col_hd.append(i)
        for j in  final_dict_hd:
            values.append(final_dict_hd.get(j,''))
        insert_query=f'INSERT INTO {table_name} ({", ".join(col_hd)}) VALUES {tuple(values)}'
        cursor.execute(insert_query)
        cursor.commit()
        print(insert_query)
    except:
        print("1.ERROR OCCURED DURING INSERTION OF QUANTITY HEADERS :(")


def cgi_quality_db_insertion(inp_path):
    conn = connect_db()
    cursor = conn.cursor()
    UUID_qlty_header = str(uuid.uuid4().hex[:8])
    table_name = "exacto_qlt_hd"
    final_dict_hd = cgi_quality_headers_extraction(read_textfile(inp_path))
    values = [UUID_qlty_header, 0]
    col_hd = ['qlt_hd_uuid', "status"]
    try:
        for i in final_dict_hd:
            col_hd.append(i)
        for j in final_dict_hd:
            values.append(final_dict_hd.get(j, ''))
        insert_query = f'INSERT INTO {table_name} ({", ".join(col_hd)}) VALUES {tuple(values)}'
        cursor.execute(insert_query)
        cursor.commit()
    except:
        print("1.ERROR OCCURED DURING INSERTION OF QUALITY HEADERS :(")
    final_dict_li = cgi_qlty_lineitem_main(inp_path)
    try:
        col_li = ['qlt_hd_uuid', 'status','method', 'component']
        for i in final_dict_li:
            table_name_qnt_li = "exacto_qlt_li"
            valuesli = [UUID_qlty_header, 0]
            for k in i:
                valuesli.append(i.get(k, ''))
            insert_query_li = f'INSERT INTO {table_name_qnt_li} ({", ".join(col_li)}) VALUES {tuple(valuesli)}'
            # print(insert_query_li)
            cursor.execute(insert_query_li)
            cursor.commit()

    except:
        print("2. ERROR OCCOURED DURING INSERTION OF QUALITY LINEITEM")
    cursor.close()


##################### for test ################
# provide the path of the text file
# inp_path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/Extra_data/Inv_302512/Inv_302512.text"
# inp_path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/Inv_301659/Inv_301659.text"
# inp_path1 = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/98889/98889.text"
# inp_path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/100150-264_WEB264_VGO_B20201223001_XOM_FINALupdated/100150-264_WEB264_VGO_B20201223001_XOM_FINALupdated.text"

# cgi_quality_db_insertion(inp_path)
# cgi_invoice_db_insertion(inp_path)
# cgi_quantity_db_insertion(inp_path1)
# path = r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/CGI/CHEM-US/305468/21E562874v.1.text'
# Nomination_Insertion(path)




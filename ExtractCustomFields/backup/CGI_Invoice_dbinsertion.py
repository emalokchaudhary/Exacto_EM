import uuid
import pyodbc
import sys
#from  .datadrive.EM_Product.ips.invoiceProduct_solution.apps.db_connection import *  #datadrive/EM_Product/ips/invoiceProduct_solution/apps/db_connection.py
from db_connection import connect_db
from CGI_Invoice_headers import *
from CGI_Invoice_lineitems import *
from CGI_Quantity_headers import *
inp_path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/Extra_data/Inv_302512/Inv_302512.text"   #provide the path of the text file
#inp_path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/Inv_301659/Inv_301659.text"
inp_path1=r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/98889/98889.text"

def invoice_header_lineitem(inp_path):
    conn=connect_db()
    cursor=conn.cursor()
    UUID_invoice_header = str(uuid.uuid4().hex[:8])
    table_name="exacto_inv_hd"
    final_dict_hd=cgi_invoice_headers_extraction(read_textfile(inp_path))
    values=[UUID_invoice_header,0]
    col_hd=['inv_hd_uuid',"status"]
    try:
        for i in final_dict_hd:
            col_hd.append(i)
        for j in  final_dict_hd:
            values.append(final_dict_hd.get(j,''))
        insert_query=f'INSERT INTO {table_name} ({", ".join(col_hd)}) VALUES {tuple(values)}'
        cursor.execute(insert_query)
        cursor.commit()
    except:
        print("1.ERROR OCCURED DURING INSERTION OF INVOICE HEADERS :(")
    final_dict_li=cgi_lineitem_main(inp_path)
    try:
        col_li=['inv_hd_uuid','status','Description','QuantityValue','Price']
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
    return UUID_invoice_header


def quantity_headers(inp_path1,UUID_quantity_header):
    conn=connect_db()
    cursor=conn.cursor()
    #UUID_quantity_header =#str(uuid.uuid4().hex[:8])
    table_name="exacto_qnt_hd"
    final_dict_hd=cgi_quantity_headers_extraction(read_textfile(inp_path1))
    #print(fi)
    values=[UUID_quantity_header,0]
    col_hd=['qnt_hd_uuid',"status"]
    #try:
    for i in final_dict_hd:
        col_hd.append(i)
    for j in  final_dict_hd:
        values.append(final_dict_hd.get(j,''))
    insert_query=f'INSERT INTO {table_name} ({", ".join(col_hd)}) VALUES {tuple(values)}'
    cursor.execute(insert_query)
    cursor.commit()
    print(insert_query)
    #except:
        #print("1.ERROR OCCURED DURING INSERTION OF QUANTITY HEADERS :(")
def invoice_quantity_main(inp_path1):
    uuid_quantity=invoice_header_lineitem(inp_path)
    quantity_headers(inp_path1,uuid_quantity)





    
invoice_quantity_main(inp_path1)
#quantity_headers(inp_path1)
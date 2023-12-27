import uuid
import pyodbc
import os
import sys
import traceback
import re
# sys.path.insert(0,'../..')
from ExtractCustomFields.EM_logging import logger
#from  .datadrive.EM_Product.ips.invoiceProduct_solution.apps.db_connection import *  #datadrive/EM_Product/ips/invoiceProduct_solution/apps/db_connection.py
from ExtractCustomFields.db_connection import connect_db
sys.path.insert(0,'../..')

def Nomination_Insertion(Nom_header_data, Nom_parcel_item, Nom_line_item,error_dict):  

    conn = connect_db()
    cursor = conn.cursor()

    # Nom_header_data = Nomination_header_field(lines)
    # Nom_parcel_item = main_call(read)
    # Nom_line_item = Quality_line_items(lines)
    # print('**********************************', Nom_line_item)
    UUID = str(uuid.uuid4().hex[:8])
    Nom_header_data['status'] = 0
    Nom_header_data['nom_hd_uuid'] = UUID
    flag_Nom_red=0
    try:

        insert_error_statement = "INSERT INTO exacto_doc_process_log(doc_uuid, VendorName, FileName ,Region, InvNo,ExtractionStatus, StartTime,FileType ) VALUES (?,?, ?, ?, ?, ?,? ,?)"
        err = ["doc_uuid", "VendorName", "FileName", "Region",
                "InvNo", "ExtractionStatus", "StartTime", "FileType"]
        err_value = []
        error_dict["ExtractionStatus"] = 6
        for i in err:

            err_value.append(error_dict[i])
        
        cursor.execute(insert_error_statement, tuple(err_value))
        cursor.commit()
    except Exception as e:
        
        flag_Nom_red +=1 
        logger.info("ERROR IN DOC PROCESS TABLE: NOMINATION")
        logger.exception(e)
        pass

    insert_statement_1 = "INSERT INTO exacto_nom_hd(nom_hd_uuid, TripNumber, NominationNumber, Region, status,doc_uuid  ) VALUES (?, ?, ?, ?, ?,?)"
    try:
        values_1 = (Nom_header_data.get('nom_hd_uuid', ''), Nom_header_data.get('TripNumber', ''), Nom_header_data.get(
            'NominationNumber', ''), Nom_header_data.get('Region', ''), Nom_header_data.get('status', 0), Nom_header_data.get('doc_uuid', ''))
        
        cursor.execute(insert_statement_1, values_1)
    except Exception as e:
        flag_Nom_red +=1
        logger.info("ERROR IN NOMINATION HEADER DICT INSERTION") 
        logger.exception(e)
        pass

    insert_statement_2 = "INSERT INTO exacto_nom_li(nom_hd_uuid, ActivityType, VendorName , ProductName, NominatedQuantity, UnitOfMeasure, JobLocation, JobDate ,EmAffiliates, NominationKey, VesselName,Inspection, status ) VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    insert_statement_3 = "INSERT INTO exacto_nom_ql_li( nom_hd_uuid ,SetNo ,SetDescription ,SampleLocation ,VendorName ,TestName ,TestCode ,Comments,status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"

    try:
        for table_data in Nom_parcel_item:
            for row in table_data:
                row['status'] = 0
                row['nom_hd_uuid'] = UUID
                
                values_2 = (row.get('nom_hd_uuid', ''), row.get('ActivityType', ''), row.get('VendorName', ''),  row.get('ProductName', ''), row.get('NominatedQuantity', ''), row.get(
                    'UnitOfMeasure', ''), row.get('JobLocation', ''), row.get('JobDate', ''), row.get('EmAffiliates', ''), row.get('NominationKey', ''), row.get('VesselName', ''),row.get('TypeofInspection', ''), row.get('status', 0))
                
                cursor.execute(insert_statement_2, values_2)
    except Exception as e:
        flag_Nom_red +=1 
        logger.info("ERROR IN NOMINATION PARCEL DICT INSERTION") 
        logger.exception(e)
        
        pass
    try:
        for table_data in Nom_line_item:
            for row in table_data:
                row['status'] = 0
                row['nom_hd_uuid'] = UUID

                values_3 = (row.get('nom_hd_uuid', ''), row.get('SetNo', ''), row.get('SetDescription', ''), row.get('SampleLocation', ''), row.get(
                    'VendorName', ''), row.get('TestName', ''), row.get('TestCode', ''), row.get('Comments', ''), row.get('status', 0))
                # print(insert_statement_3, "Nomination Line item query", values_3)
                cursor.execute(insert_statement_3, values_3)
    except Exception as e:
        # flag_Nom_red +=1 
        logger.info("ERROR IN NOMINATION LINE ITEM DICT INSERTION") 
        logger.exception(e)
        
        pass

    conn.commit()
    cursor.close()
    conn.close()
    
    return flag_Nom_red


def cgi_invoice_db_insertion(inv_header_data, inv_line_item,error_dict):
    conn = connect_db()
    cursor = conn.cursor()
    UUID_invoice_header = str(uuid.uuid4().hex[:8])
    table_name = "exacto_inv_hd"
    final_dict_hd = inv_header_data
    values = [UUID_invoice_header, 0]
    col_hd = ['inv_hd_uuid', "status"]
    flag_Inv_red=0
    try:
        insert_error_statement = "INSERT INTO exacto_doc_process_log(doc_uuid, VendorName, FileName ,Region, InvNo,ExtractionStatus, StartTime,FileType ) VALUES (?,?, ?, ?, ?, ?,? ,?)"
        err = ["doc_uuid", "VendorName", "FileName", "Region",
               "InvNo", "ExtractionStatus", "StartTime", "FileType"]
        err_value = []
        error_dict["ExtractionStatus"] = 6
        for i in err:

            err_value.append(error_dict[i])
        
        cursor.execute(insert_error_statement, tuple(err_value))
        cursor.commit()
        
    except Exception as e:
        flag_Inv_red +=1
        logger.info("ERROR IN DOC PROCESS LOG TABLE: INVOICE")
        logger.exception(e)
        
        pass
    try:
        for i in final_dict_hd:
            col_hd.append(i)
        for j in final_dict_hd:
            values.append(final_dict_hd.get(j, ''))
        insert_query = f'INSERT INTO {table_name} ({", ".join(col_hd)}) VALUES {tuple(values)}'
        
        cursor.execute(insert_query)
        cursor.commit()
        
    except Exception as e:
        flag_Inv_red +=1
        logger.info("ERROR IN INVOICE HEADER DICT INSERTION")
        logger.exception(e)
        
        pass
    
    final_dict_li = inv_line_item
    try:
        col_li = ['inv_hd_uuid', 'status','Description', 'QuantityValue', 'Price',
                  'UoM','Charge','Share','ShareCharge','TestName','TestMethod','Tax_Description','Amount_Li','Discount']
        col_qnt_li = ['inv_hd_uuid', 'status','Description', 'QuantityValue', 'Price','UoM',
                      'Category','SubCategory','Charge','Share','ShareCharge','Tax_Description','Amount_Li','Discount']
        for i in final_dict_li:
            if(i == 'Quantity'):
                table_name_qnt_li = "exacto_inv_qnt_li"
                for j in final_dict_li[i]:
                    valuesli = [UUID_invoice_header, 0]
                    for k in j:
                        valuesli.append(j.get(k, ''))
                    insert_query_li = f'INSERT INTO {table_name_qnt_li} ({", ".join(col_qnt_li)}) VALUES {tuple(valuesli)}'
                    
                    cursor.execute(insert_query_li)
                    cursor.commit()
                    
            elif(i == 'quality'):
                table_name_qnt_li = "exacto_inv_qlt_li"
                for j in final_dict_li[i]:
                    valuesli = [UUID_invoice_header, 0]
                    for k in j:
                        valuesli.append(j.get(k, ''))
                    insert_query_li = f'INSERT INTO {table_name_qnt_li} ({", ".join(col_li)}) VALUES {tuple(valuesli)}'
                    
                    cursor.execute(insert_query_li)
                    cursor.commit()
                    
    except Exception as e:
        flag_Inv_red +=1
        logger.info("ERROR IN INVOICE LINE ITEM DICT INSERTION")
        logger.exception(e)
        
        pass
    
    cursor.close()
    return flag_Inv_red
    # print(insert_query)


def cgi_quality_db_insertion(qlty_header_data, qlty_line_item, error_dict):
    conn = connect_db()
    cursor = conn.cursor()
    UUID_qlty_header = str(uuid.uuid4().hex[:8])
    table_name = "exacto_qlt_hd"
    final_dict_hd = qlty_header_data
    values = [UUID_qlty_header, 0]
    col_hd = ['qlt_hd_uuid', "status"]
    flag_qlt_red =0
    try:
        insert_error_statement = "INSERT INTO exacto_doc_process_log(doc_uuid, VendorName, FileName ,Region, InvNo,ExtractionStatus, StartTime,FileType ) VALUES (?,?, ?, ?, ?, ?,? ,?)"
        err = ["doc_uuid", "VendorName", "FileName", "Region",
               "InvNo", "ExtractionStatus", "StartTime", "FileType"]
        err_value = []
        error_dict["ExtractionStatus"] = 6
        for i in err:

            err_value.append(error_dict[i])

        cursor.execute(insert_error_statement, tuple(err_value))
        cursor.commit()
    except Exception as e:
        flag_qlt_red +=1
        logger.info("ERROR IN DOC PROCESS LOG TABLE: QUALITY")
        logger.exception(e)
        
        pass
    try:
        for i in final_dict_hd:
            col_hd.append(i)
        for j in final_dict_hd:
            values.append(final_dict_hd.get(j, ''))
        insert_query = f'INSERT INTO {table_name} ({", ".join(col_hd)}) VALUES {tuple(values)}'
       
        cursor.execute(insert_query)
        cursor.commit()
    except Exception as e :
        flag_qlt_red +=1
        logger.info("ERROR IN QUALITY HEADER DICT INSERTION")
        logger.exception(e)
        
        pass
    final_dict_li = qlty_line_item
    try:
        col_li = ['qlt_hd_uuid', 'status', 'method', 'component']
        for i in final_dict_li:
            table_name_qnt_li = "exacto_qlt_li"
            valuesli = [UUID_qlty_header, 0]
            for k in i:
                valuesli.append(i.get(k, ''))
            insert_query_li = f'INSERT INTO {table_name_qnt_li} ({", ".join(col_li)}) VALUES {tuple(valuesli)}'
            # print("QUALITY line item query----", insert_query_li)
            cursor.execute(insert_query_li)
            cursor.commit()

    except Exception as e:
        # flag_qlt_red +=1
        logger.info("ERROR IN QUALITY LINEITEM DICT INSERTION")
        logger.exception(e)
        
        pass
    cursor.close()
    return flag_qlt_red

def cgi_quantity_db_insertion(qnty_header_data, error_dict):
    conn = connect_db()
    cursor = conn.cursor()
    
    table_name = "exacto_qnt_hd"
    final_dict_hd = qnty_header_data
    # print("ggggggggggggggggggggggggggggggggg",final_dict_hd)
    # values = [UUID_quantity_header, 0]
    # col_hd = ['qnt_hd_uuid', "status"]
    flag_qnty_red =0
    try:
        insert_error_statement = "INSERT INTO exacto_doc_process_log(doc_uuid, VendorName, FileName ,Region, InvNo,ExtractionStatus, StartTime,FileType ) VALUES (?,?, ?, ?, ?, ?,? ,?)"
        err = ["doc_uuid", "VendorName", "FileName", "Region",
               "InvNo", "ExtractionStatus", "StartTime", "FileType"]
        err_value = []
        error_dict["ExtractionStatus"] = 6
        for i in err:

            err_value.append(error_dict[i])
        # print("Quantityyyyyyyyyy Trueeee----",
            #   insert_error_statement, tuple(err_value))
        cursor.execute(insert_error_statement, tuple(err_value))
        cursor.commit()
    except Exception as e:
        flag_qnty_red +=1
        logger.info("ERROR IN DOC PROCESS LOG TABLE: QUANTITY")
        logger.exception(e)
                
        pass
    try:
        if type(final_dict_hd)==type({}):
            UUID_quantity_header = str(uuid.uuid4().hex[:8])
            values = [UUID_quantity_header, 0]
            col_hd = ['qnt_hd_uuid', "status"]
            for i in final_dict_hd:
                col_hd.append(i)
            for j in final_dict_hd:
                values.append(final_dict_hd.get(j, ''))
            insert_query = f'INSERT INTO {table_name} ({", ".join(col_hd)}) VALUES {tuple(values)}'
            # print("quantity header query----", insert_query)
            cursor.execute(insert_query)
            cursor.commit()
        else:
            for k in final_dict_hd:
                UUID_quantity_header = str(uuid.uuid4().hex[:8])
                col_hd=[]
                values=[]
                values = [UUID_quantity_header, 0]
                col_hd = ['qnt_hd_uuid', "status"]
                for i in k.copy():
                    col_hd.append(i)
                for j in k.copy():
                    values.append(k.get(j, ''))
                insert_query = f'INSERT INTO {table_name} ({", ".join(col_hd)}) VALUES {tuple(values)}'
                # print("quantity header query----", insert_query)
                cursor.execute(insert_query)
                cursor.commit()
                
        
    except Exception as e:
        flag_qnty_red +=1
        logger.info("ERROR IN QUANTITY HEADER DICT INSERTION")
        logger.exception(e)
        
        pass
    cursor.close()

    return flag_qnty_red 



def camin_qnt_and_quality_db_insertion(qnty_header_data,qlty_header_data, qlty_line_item, error_dict):
    conn = connect_db()
    cursor = conn.cursor()
   
    table_name = "exacto_qnt_hd"
    final_dict_hd = qnty_header_data
   
    # values = [UUID_quantity_header, 0]
    # col_hd = ['qnt_hd_uuid', "status"]
    flag_qnty_qlt_red =0
    try:
        
        insert_error_statement = "INSERT INTO exacto_doc_process_log(doc_uuid, VendorName, FileName ,Region, InvNo,ExtractionStatus, StartTime,FileType ) VALUES (?,?, ?, ?, ?, ?,? ,?)"
        err = ["doc_uuid", "VendorName", "FileName", "Region",
               "InvNo", "ExtractionStatus", "StartTime", "FileType"]
        err_value = []
        error_dict["ExtractionStatus"] = 6
        for i in err:

            err_value.append(error_dict[i])
        # print("Quantityyyyyyyyyy Trueeee----",
        #       insert_error_statement, tuple(err_value))
        cursor.execute(insert_error_statement, tuple(err_value))
        cursor.commit()
    except Exception as e:
        flag_qnty_qlt_red +=1
        logger.info("ERROR IN DOC PROCESS LOG TABLE:  QUANTITY & QUALITY")
        logger.exception(e)
        
        pass
    try:
        if type(final_dict_hd)==type({}):
            UUID_quantity_header = str(uuid.uuid4().hex[:8])
            values = [UUID_quantity_header, 0]
            col_hd = ['qnt_hd_uuid', "status"]
            for i in final_dict_hd:
                col_hd.append(i)
            for j in final_dict_hd:
                values.append(final_dict_hd.get(j, ''))
            insert_query = f'INSERT INTO {table_name} ({", ".join(col_hd)}) VALUES {tuple(values)}'
            # print("quantity header query----", insert_query)
            cursor.execute(insert_query)
            cursor.commit()
        else:
            for k in final_dict_hd:
                UUID_quantity_header = str(uuid.uuid4().hex[:8])
                col_hd=[]
                values=[]
                values = [UUID_quantity_header, 0]
                col_hd = ['qnt_hd_uuid', "status"]
                for i in k.copy():
                    col_hd.append(i)
                for j in k.copy():
                    values.append(k.get(j, ''))
                insert_query = f'INSERT INTO {table_name} ({", ".join(col_hd)}) VALUES {tuple(values)}'
                # print("quantity header query----", insert_query)
                cursor.execute(insert_query)
                cursor.commit()
                
        
    except Exception as e:
        flag_qnty_qlt_red +=1
        logger.info("ERROR IN  QUANTITY HEADER DICT INSERTION")
        logger.exception(e)
        
        pass
    
    UUID_qlty_header = str(uuid.uuid4().hex[:8])
    table_name_qlt = "exacto_qlt_hd"
    final_dict_hd = qlty_header_data
    values = [UUID_qlty_header, 0]
    col_hd = ['qlt_hd_uuid', "status"]
    
    
    
    try:
        for i in final_dict_hd:
            col_hd.append(i)
        for j in final_dict_hd:
            values.append(final_dict_hd.get(j, ''))
        insert_query = f'INSERT INTO {table_name_qlt} ({", ".join(col_hd)}) VALUES {tuple(values)}'
        # print("QUALITY header query----- ", insert_query)
        cursor.execute(insert_query)
        cursor.commit()
    except Exception as e:
        flag_qnty_qlt_red +=1
        logger.info("ERROR IN QUALITY HEADER DICT INSERTION")
        logger.exception(e)
        
        pass
    final_dict_li = qlty_line_item
    try:
        col_li = ['qlt_hd_uuid', 'status', 'method', 'component']
        for i in final_dict_li:
            table_name_qnt_li = "exacto_qlt_li"
            valuesli = [UUID_qlty_header, 0]
            for k in i:
                valuesli.append(i.get(k, ''))
            insert_query_li = f'INSERT INTO {table_name_qnt_li} ({", ".join(col_li)}) VALUES {tuple(valuesli)}'
            # print("QUALITY line item query----", insert_query_li)
            cursor.execute(insert_query_li)
            cursor.commit()

    except Exception as e:
        flag_qnty_qlt_red +=1
        logger.info("ERROR IN QUALITY LINEITEM DICT INSERTION")
        logger.exception(e)
        
        pass
    
    cursor.close()    
    return flag_qnty_qlt_red 




def api_procedure_byuuid_main_2(procedure_name,arg):
    conn = connect_db()
    cursor = conn.cursor()
    res=0
    Inv_Row_ID='NA'
    try:
        print("Toscana data insert query move to exacto",procedure_name,arg)
        logger.info(f'Toscana data insert query move to exacto --{procedure_name},{arg}')
        cursor.execute("{call "+procedure_name+"('"+arg+"')}")
        cursor.commit()

        for msg in cursor.messages:
            if 'Success' in msg[1]:
                print(msg[1])
                try:
                    if(procedure_name=='HCL_Invoice_Data_Trans'):
                        print(msg[1])
                        Inv_Row_ID=int(re.sub("\s+","",(re.sub('Success\s+',"",re.search(r'Success\s*[0-9]+\s*',msg[1])[0]))))
                        print(Inv_Row_ID)
                        logger.info(msg[1])
                except Exception as e:
                    logger.info("Not able to extract the Inv_Row_Id")
                    logger.exception(e)
                    print('Not able to extract the Inv_Row_Id')
                print(f'seems like {procedure_name} is successfully executed')
                logger.info(f'seems like {procedure_name} is successfully executed')
                res=1
            else:
                res=0
                logger.info(f'seems like {procedure_name}  is Not successfully executed')
                print(f'seems like {procedure_name} is Not successfully executed')
    except Exception as e:
        logger.exception(e)
        print("Error in SP with  ",procedure_name)
        pass
        
    cursor.close()
    conn.close()
    return res,Inv_Row_ID

############# TOSCANA SP FUN.BELOW WHICH IS BEING CALLED AFTER MOVE. OF DOC TO CONTAINER ########

def toscan_blob_sp(procedure_name,file_name,Inv_Row_ID):
    conn = connect_db()
    cursor = conn.cursor()
    error_code=12
    content_type='application/pdf'
    document_type='pdf'

    try:
        logger.info(f'Toscana blob sp details --{procedure_name},{file_name},{Inv_Row_ID}')
        cursor.execute("{call "+procedure_name+"('"+file_name+"','"+content_type+"','"+document_type+"',"+Inv_Row_ID+")}")
        cursor.commit()
        for msg in cursor.messages:
            if 'Success' in msg[1]:
                error_code=12
                break
    except:
        error_code=13

    cursor.close()
    conn.close()
    return error_code







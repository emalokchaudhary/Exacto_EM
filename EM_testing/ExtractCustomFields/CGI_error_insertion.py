import os
import datetime
import traceback
from ExtractCustomFields.db_connection import connect_db

def Error_insert(error_dict):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        insert_error_statement = "INSERT INTO exacto_doc_process_log(doc_uuid, VendorName, FileName ,Region, InvNo,ExtractionStatus, StartTime ) VALUES (?, ?, ?, ?, ?,? ,?)"
        err = ["doc_uuid", "VendorName", "FileName", "Region",
               "InvNo", "ExtractionStatus", "StartTime"]
        err_value =[]
        
        for i in err:    
            err_value.append(error_dict[i])
        print("Falseeeeeeeeeeeeeeeeeeeeeeeeee",insert_error_statement, tuple(err_value))
        cursor.execute(insert_error_statement, tuple(err_value))
    except Exception as e:
        traceback.print_exc()
        print("Error inserrtion part when insert error dict ")
        pass
    conn.commit()
    cursor.close()
    conn.close()

# import os,datetime
# from db_connection import connect_db
# folder_path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_api_Input/CGI/CHEM-US/305468"
# error_dict = {}
# error_dict["doc_uuid"] = 123454
# error_dict["StartTime"] = datetime.datetime.now()
# error_dict["ExtractionStatus"] = 0
# error_dict["VendorName"] = folder_path.split("/")[-3]
# error_dict["Region"] = folder_path.split("/")[-2]
# error_dict["InvNo"] = folder_path.split("/")[-1]
# error_dict["FileName"] = "abcd.pdf"  # file_path.split("/")[-1]
# # def error_dict_insertion(error_dict):
# # error_dict["ExtractionStatus"] = 0


# def Error_insert(error_dict):
#     # try:
#         conn = connect_db()
#         cursor = conn.cursor()
#         insert_error_statement = "INSERT INTO exacto_doc_process_log(doc_uuid, VendorName, FileName ,Region, InvNo,ExtractionStatus, StartTime ) VALUES (?, ?, ?, ?, ?,? ,?)"
#         err = ["doc_uuid", "VendorName", "FileName", "Region",
#                "InvNo", "ExtractionStatus", "StartTime"]
#         err_value = []
#         # error_dict["ExtractionStatus"] = 1
#         for i in err:

#             err_value.append(error_dict[i])
#         print("Falseeeeeeeeeeeeeeeeeeeeeeeeee",
#               insert_error_statement, tuple(err_value))
#         cursor.execute(insert_error_statement, tuple(err_value))
#     # except:
#     #     print("error in inserrtion error dict ")
#     #     pass
#         conn.commit()
#         cursor.close()
#         conn.close()
# #ExtractionStatus


# print(Error_insert(error_dict))

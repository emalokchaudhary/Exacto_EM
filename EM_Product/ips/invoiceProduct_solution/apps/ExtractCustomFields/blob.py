import os, uuid
#from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import pandas
#import connection
import requests

#server connections
connection_string="DefaultEndpointsProtocol=https;AccountName=storpaypmipoc;AccountKey=sOSfoJZvVvmQsTyoixuks9vyUSFSvC7BjM54MOGlu9eLvuHxb9i1y5wNYI+50FCKN8t8V5Os8xhy+AStr+uSXw==;EndpointSuffix=core.windows.net"
storage_account_key='sOSfoJZvVvmQsTyoixuks9vyUSFSvC7BjM54MOGlu9eLvuHxb9i1y5wNYI+50FCKN8t8V5Os8xhy+AStr+uSXw=='
storage_account_name='storpaypmipoc'
container_name='toscana'

blob_service_client=BlobServiceClient.from_connection_string(connection_string)
print("CONNECTION ESTABLISHED")
container_client = blob_service_client.get_container_client(container_name)
print("TOSCANA CONTAINER PRESENT")


def upload_files_to_blob(local_pdf_paths, blob_folder_name):
    list_of_success_doc=[]
    list_of_failure_doc=[]
    for local_pdf_path in local_pdf_paths:
        if not os.path.exists(local_pdf_path):
            print(f"File '{local_pdf_path}' does not exist.")
            continue

        file_name = os.path.basename(local_pdf_path)
        blob_name = os.path.join(blob_folder_name, file_name).replace(os.path.sep, '/')
        blob_client = container_client.get_blob_client(blob_name)


        try:
            with open(local_pdf_path, "rb") as data:
                blob_client.upload_blob(data)
            print(f"File '{local_pdf_path}' uploaded to '{container_name}/{blob_name}'")
            list_of_success_doc.append(local_pdf_path)
        except Exception as e:
            print(f"An error occurred: {e}")
            list_of_failure_doc.append(local_pdf_path)
    return list_of_success_doc,list_of_failure_doc

def blob_main_call(local_pdf_paths, blob_folder_name):
    list_of_success_doc,list_of_failure_doc=upload_files_to_blob(local_pdf_paths, blob_folder_name)
    return list_of_success_doc,list_of_failure_doc


######################### PLEASE UNCOMMENT BELOW CODE FOR TESTING #############
    
# l=['/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Processed/CGI/CHEM-US/308779/21E581966v.1.pdf','/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Processed/CGI/CHEM-US/308779/104885EMCC.pdf','/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Processed/CGI/CHEM-US/308779/Inv308779.pdf']
# row_id='00001'
# blob_main_call(l,row_id)

import os, uuid
#from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import pandas
#import connection
import requests

connection_string="DefaultEndpointsProtocol=https;AccountName=storpaypmipoc;AccountKey=sOSfoJZvVvmQsTyoixuks9vyUSFSvC7BjM54MOGlu9eLvuHxb9i1y5wNYI+50FCKN8t8V5Os8xhy+AStr+uSXw==;EndpointSuffix=core.windows.net"
storage_account_key='sOSfoJZvVvmQsTyoixuks9vyUSFSvC7BjM54MOGlu9eLvuHxb9i1y5wNYI+50FCKN8t8V5Os8xhy+AStr+uSXw=='
storage_account_name='storpaypmipoc'
container_name='toscana'

blob_service_client=BlobServiceClient.from_connection_string(connection_string)
print("CONNECTION ESTABLISHED")
container_client = blob_service_client.get_container_client(container_name)
print("TOSCANA CONTAINER PRESENT")

folder_path = r"/datadrive/EM_testing/ExtractCustomFields/test1"
blob_name = "testing"

def folder_upload(folder_path,blob_name):
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            local_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(local_path, folder_path)
            #blob_name = relative_path.replace(os.path.sep, '/')

            #blob_client = container_client.get_blob_client(blob_name)
            with open(local_path,mode='rb') as data:
                blob_client=container_client.upload_blob(name="testing.txt", data=data, overwrite=True)
    return "SUCCESS"

def upload_blob_file():
    container_client = blob_service_client.get_container_client(container=container_name)
    with open(file=os.path.join(r"/datadrive/EM_testing/ExtractCustomFields/test1", 'test.txt'), mode="rb") as data:
        print(1)
        blob_client = container_client.upload_blob(name="test_file.txt", data=data, overwrite=True)
        print(2)
    return "SUCCESS"






if __name__=="__main__":
    upload_blob_file()
    #folder_upload(folder_path,blob_name)

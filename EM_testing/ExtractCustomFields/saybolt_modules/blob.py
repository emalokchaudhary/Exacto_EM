import os, uuid
#from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import pandas
#import connection
import requests

folder_path = r"/datadrive/EM_testing/ExtractCustomFields/test1"
blob_name = "testing"
connection_string="DefaultEndpointsProtocol=https;AccountName=storpaypmipoc;AccountKey=sOSfoJZvVvmQsTyoixuks9vyUSFSvC7BjM54MOGlu9eLvuHxb9i1y5wNYI+50FCKN8t8V5Os8xhy+AStr+uSXw==;EndpointSuffix=core.windows.net"
storage_account_key='sOSfoJZvVvmQsTyoixuks9vyUSFSvC7BjM54MOGlu9eLvuHxb9i1y5wNYI+50FCKN8t8V5Os8xhy+AStr+uSXw=='
storage_account_name='storpaypmipoc'
container_name='toscana'

def folder_upload_to_blob(connection_string,container_name,folder_path,blob_name):
    blob_service_client=BlobServiceClient.from_connection_string(connection_string)
    print("CONNECTION ESTABLISHED")
    container_client = blob_service_client.get_container_client(container_name)
    print("TOSCANA CONTAINER PRESENT")
    
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            local_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(local_path, folder_path)
            #blob_name = relative_path.replace(os.path.sep, '/')
 
            blob_client = container_client.get_blob_client(blob_name)
            with open(local_path, "rb") as data:
                blob_client.upload_blob(data)

    # file_name="xyz"
    # local_path=r"/datadrive/EM_testing/ExtractCustomFields/test222.txt"
    # blob_client = container_client.get_blob_client(blob_name,file_name)
    # for root, dirs, files in os.walk(folder_path):
    #         for file_name in files:
    #             local_path = os.path.join(root, file_name)
    #             relative_path = os.path.relpath(local_path, folder_path)
    #             #blob_name = relative_path.replace(os.path.sep, '/')
    
    #             blob_client = container_client.get_blob_client(blob_name)
    # with open(local_path, "rb") as data:
    #     blob_client.upload_blob(data)   
    return "SUCCESS"

folder_upload_to_blob(connection_string,container_name,folder_path,blob_name)








 
# IMPORTANT: Replace connection string with your storage account connection string

''' 
class AzureBlobFileUploader:
  
    
 
  def upload_all_images_in_folder(self):
    # Get all files with jpg extension and exclude directories
    all_file_names = [f for f in os.listdir(LOCAL_IMAGE_PATH)
                    if os.path.isfile(os.path.join(LOCAL_IMAGE_PATH, f)) and ".pdf" in f]
 
    # Upload each file
    for file_name in all_file_names:
      self.upload_image(file_name)
 
  def upload_image(self,file_name):
    # Create blob with same name as local file name
    blob_client = self.blob_service_client.get_blob_client(container=MY_IMAGE_CONTAINER,
                                                          blob=file_name)
    # Get full path to the file
    upload_file_path = os.path.join(LOCAL_IMAGE_PATH, file_name)
 
    # Create blob on storage
    # Overwrite if it already exists!
    image_content_setting = ContentSettings(content_type='image/jpeg')
    print(f"uploading file - {file_name}")
    with open(upload_file_path, "rb") as data:
      blob_client.upload_blob(data,overwrite=True,content_settings=image_content_setting)
 
 
# Initialize class and upload files
azure_blob_file_uploader = AzureBlobFileUploader()
azure_blob_file_uploader.upload_all_images_in_folder()




container_client=blob_service_client.get_container_client(container_name)
blob_list = container_client.list_blob()
for blob in blob_list:
    print(blob.name)



def upload_to_blob_storage(local_path_file_path,file_name_for_blob):
    blob_service_client=BlobServiceClient.from_connection_string(connection_string)
    blob_client=blob_service_client.get_blob_client(container=container_name,blob=file_name_for_blob)
    print(f'upload to Azure:{file_name_for_blob}')
    with open(local_path_file_path,'rb') as data:
        blob_client.upload_blob(data)
    print('Successfully upload data to blob')

path='https://navrick/Camin/Tobeanalyze/11234/'

invoice=pandas.read_sql('Select * from InvoiceHeader_External',database_connection)
for index,row in invoice.iterrows():
    folder_name=row['RowId']
    path='https://navrick/Camin'   #local path
    resp=requests.get(path)
    file_name=''
    number_folder=0
    for out in os.listdir(resp.content):
        if(out=='ToBeAnalyze'):
            out_path=os.path.join(path,out)
            resp=requests.get(out_path)
    # for sub_folder_number in os.listdir(path):
            for sub_folder_number in os.listdir(resp.content):
                if(sub_folder_number==row['InvoiceNumber']):
                    number_folder=sub_folder_number
                    join_path=os.path.join(path,sub_folder_number)
                    resp=requests.get(join_path)
                    for j in os.listdir(resp.content):
                    # for j in os.listdir(os.path.join(path,sub_folder_number)):
                        if(j.split('.')[0].isdigit() or 'invoice' in j.split('.')[0]):
                            file_name=j
                            break
                break
    file_name_for_blob=os.path.join(folder_name,file_name)
    local_path_file_path=os.path.join(path,os.path.join(number_folder,file_name))
    upload_to_blob_storage(local_path_file_path,file_name_for_blob)




# String connectionString = "DefaultEndpointsProtocol=https;
# AccountName=storpaypmipoc;
# AccountKey=sOSfoJZvVvmQsTyoixuks9vyUSFSvC7BjM54MOGlu9eLvuHxb9i1y5wNYI+50FCKN8t8V5Os8xhy+AStr+uSXw==;
# EndpointSuffix=core.windows.net";

'''
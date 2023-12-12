import os,re
import numpy as np

def read_textfile(fileName):
    with open(fileName,encoding="utf-8") as f:
        text_data = f.read()
        # data=f.readlines()
        # print(text_data)
    return  text_data

def saybolt_qnt_loading_sum_report(data,text_data,uuid_doc):
    data_dict={}
    trip_no=vendor_name=activity_type=vessel_no=product_name=quantity=uom=file_no=date=job_location=ref_no=bill_to=''
    for k,line in enumerate(data):
        match=re.search(r'(Loading Summary Report)',line,re.IGNORECASE)  
        li=[]
        breakpoint=0
        if match:
            span=match.span()
            # print(match.group())
    
            try:
                for i in range(k-1,k+10):
                    li.append(data[i].strip())
                    if i in [3,4,5,6] and data[i].strip().count(",") >=2:
                        break
                
                vessel_no=li[0]
                product_name=li[2]
                job_location=li[-1]
                    
                        
                print(li)    
            except:                
                pass
            try:
                date=re.findall(r'Date of issue(.*)',text_data)[0].strip().replace(":","")#.replace(" ","").split(":")[1].split("    ")[0]
                date=date.strip()
            except:
                pass
            try:
                trip_no=re.findall(r'Our reference number(.*)',text_data)[0].strip().replace(":","")#.replace(" ","").split(":")[1].split("    ")[0]
                trip_no=trip_no.strip()
            except:
                pass
            
            
            
    if trip_no:
        data_dict['Trip_no']=trip_no

    if vessel_no:
        data_dict['VesselName']=vessel_no
    if product_name:
        data_dict['ProductName']=product_name    
    if date:
        data_dict['JobDate']=date
    if job_location:
        data_dict['JobLocation']=job_location
    
    data_dict['doc_uuid']=uuid_doc

    return data_dict


def saybolt_inspection_headers(text_data,uuid_doc):
    
    line_data=text_data.split("\n")
    Quantity="Quantity header------------",saybolt_qnt_loading_sum_report(line_data,text_data,uuid_doc)
    

    return Quantity # Qualiity 

# path="/datadrive/EM_testing/ExtractCustomFields/Saybolt_qnt_quality_documents/Quantity_doc/EU/loading_summary_report/Emmafull.text"
# text_data=read_textfile(path)

# print(saybolt_inspection_headers(text_data,"22222"))

files=os.listdir(r"/datadrive/EM_testing/ExtractCustomFields/Saybolt_qnt_quality_documents/Quantity_doc/EU/loading_summary_report")
path=r"/datadrive/EM_testing/ExtractCustomFields/Saybolt_qnt_quality_documents/Quantity_doc/EU/loading_summary_report"
co=1
for file in files:
    path_full=os.path.join(path,file)
    # print(path_full)
    print(file)
    text_data=read_textfile(path_full)
    Quality=saybolt_inspection_headers(text_data,"22222")
    # print(Quantity)
    print(Quality)
    print(co,"--------------------------------------------------------------------------")
    co +=1



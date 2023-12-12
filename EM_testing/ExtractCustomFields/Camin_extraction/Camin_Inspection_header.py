import re
import os
import numpy as np

def read_textfile(fileName):
    with open(fileName,encoding="utf-8") as f:
        text_data = f.read()
        # data=f.readlines()
        # print(text_data)
    return text_data

def Vendor_Name(data):
    for k,line in enumerate(data):
        match=re.search(r'(Yours Sincerely)',line,re.IGNORECASE)
        if match:
            span=match.span()    
            try:
                for i in range(k+1,k+3):
                    vendor_name=data[i].strip()                           
            except:
                pass
    return vendor_name

def camin_quantity_header(data,text_data,uuid_doc):
    data_dict={}
    vendor_name=activity_type=vessel_no=product_name=quantity=uom=file_no=date=job_location=ref_no=bill_to=''

    for k,line in enumerate(data):
        match=re.search(r'(quantity certificate)',line,re.IGNORECASE)
        if match:
            span=match.span()               
            try:
                for i in range(k+1,k+7):
                    match_p=re.search(r'(product)',data[i],re.IGNORECASE)
                    if match_p:    
                        sp=match_p.span()                        
                        product_name=data[i][sp[1]:].strip().split("    ")[0].replace(":","").strip()
                        
                        
                    match_jobdate=re.search(r'(job completed)',data[i],re.IGNORECASE)
                    if match_jobdate:    
                        sp_date=match_jobdate.span()                        
                        # print("yess",match_p)
                        date=data[i][sp_date[1]:].strip().split("    ")[0].replace(":","").strip()
                        
                        
                    match_reference=re.search(r'(reference n°)',data[i],re.IGNORECASE)
                    if match_reference:    
                        sp_ref=match_reference.span()                        
                        ref_no=data[i][sp_ref[1]:].strip().split("    ")[0].replace(":","").strip()
                                            
                    match_vessel=re.search(r'(vessel)',data[i],re.IGNORECASE)
                    if match_vessel:    
                        sp_vessel=match_vessel.span()                                                
                        vessel_no=data[i][sp_vessel[1]:].strip().split("    ")[0].replace(":","").strip()
                        # print(vessel_no)   
                    
                    match_movement=re.search(r'(movement)',data[i],re.IGNORECASE)
                    if match_movement:    
                        sp_movement=match_movement.span()                                                
                        activity_type=data[i][sp_movement[1]:].strip().split("    ")[0].replace(":","").strip()                        
                    
                    match_joblocation=re.search(r'(location)',data[i],re.IGNORECASE)
                    if match_joblocation:    
                        sp_joblocation=match_joblocation.span()                                                
                        job_location=data[i][sp_joblocation[1]:].strip().split("    ")[0].replace(":","").strip()
                            
                                          
            except:                
                pass
            
            try:
                file_no=re.findall(r'File N° (.*)',text_data)[0].split(":")[1].split("    ")[0].strip()#.replace(":","").replace("  ","")
                # print(file_no)
            except:
                pass
            
            try: 
                bill_to=" ".join(re.findall(r'(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0]).split('Attention')[0].replace("  ","")
                # print(bill_to)
            except:
                pass
            try:
                # vendor_name=" ".join(re.findall(r'Yours Sincerely (.*)\n(.*)\n(.*)\n(.*)',data))#.replace("  ","")
                vendor_name= Vendor_Name(data)
                # print(vendor_name)
            except:
                pass
            
            
    
    if vendor_name:
        data_dict['VendorName']= vendor_name      
    if vessel_no:
        data_dict['VesselName']=vessel_no
    if product_name:
        data_dict['ProductName']=product_name
    if activity_type:
        data_dict['ActivityType']=activity_type
    if ref_no:
        data_dict['NominationKey']=ref_no
    if date:
        data_dict['JobDate']=date
    if job_location:
        data_dict['JobLocation']=job_location
    if file_no:
        data_dict['VendorInternalReferencenumber']=file_no
    if bill_to:
        data_dict['EmAffiliates']=bill_to
    data_dict['doc_uuid']=uuid_doc

    return data_dict



def camin_quality_header(data,text_data,uuid_doc):
    data_dict={}
    vendor_name=activity_type=vessel_no=product_name=quantity=uom=file_no=date=job_location=ref_no=bill_to=''

    for k,line in enumerate(data):
        match=re.search(r'(certificate of analysis)',line,re.IGNORECASE)
        if match:
            span=match.span()               
            try:
                for i in range(k+1,k+7):
                    match_p=re.search(r'(product)',data[i],re.IGNORECASE)
                    if match_p:    
                        sp=match_p.span()                        
                        product_name=data[i][sp[1]:].strip().split("    ")[0].replace(":","").strip()
                        
                        
                    match_jobdate=re.search(r'(job completed)',data[i],re.IGNORECASE)
                    if match_jobdate:    
                        sp_date=match_jobdate.span()                        
                        # print("yess",match_p)
                        date=data[i][sp_date[1]:].strip().split("    ")[0].replace(":","").strip()
                        
                        
                    match_reference=re.search(r'(ref. no.)',data[i],re.IGNORECASE)
                    if match_reference:    
                        sp_ref=match_reference.span()                        
                        ref_no=data[i][sp_ref[1]:].strip().split("    ")[0].replace(":","").strip()
                        # print(data[i+1][sp_ref[0]:sp_ref[1]])
                        # print(data[i+2][sp_ref[0]:sp_ref[1]]) 
                        if None ==re.search(r'[a-z]',data[i+1][sp_ref[0]:sp_ref[1]],re.I):
                            ref_no += data[i+1][sp_ref[1]:].strip()
                            print(re.search(r'[a-z]',data[i+1][sp_ref[0]:sp_ref[1]]))
                        if None == re.search(r'[a-z]',data[i+2][sp_ref[0]:sp_ref[1]],re.I):
                            ref_no += data[i+2][sp_ref[1]:].strip()
                            print(re.search(r'[a-z]',data[i+2][sp_ref[0]:sp_ref[1]]))
                                  
                    match_vessel=re.search(r'(vessel)',data[i],re.IGNORECASE)
                    if match_vessel:    
                        sp_vessel=match_vessel.span()                                                
                        vessel_no=data[i][sp_vessel[1]:].strip().split("    ")[0].replace(":","").strip()
                        # print(vessel_no)   
                    
                    match_movement=re.search(r'(movement)',data[i],re.IGNORECASE)
                    if match_movement:    
                        sp_movement=match_movement.span()                                                
                        activity_type=data[i][sp_movement[1]:].strip().split("    ")[0].replace(":","").strip()                        
                    
                    match_joblocation=re.search(r'(location)',data[i],re.IGNORECASE)
                    if match_joblocation:    
                        sp_joblocation=match_joblocation.span()                                                
                        job_location=data[i][sp_joblocation[1]:].strip().split("    ")[0].replace(":","").strip()
                        # print(job_location,"ddddddd")    
                                          
            except:                
                pass
            
            try:
                file_no=re.findall(r'File N° (.*)',text_data)[0].split(":")[1].split("    ")[0].strip()#.replace(":","").replace("  ","")
                # print(file_no)
            except:
                pass
            try: 
                bill_to=" ".join(re.findall(r'(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0]).split('Attention')[0].replace("  ","")
                # print(bill_to)
            except:
                pass
            try:
                # vendor_name=" ".join(re.findall(r'Yours Sincerely (.*)\n(.*)\n(.*)\n(.*)',data))#.replace("  ","")
                vendor_name= Vendor_Name(data)
                # print(vendor_name)
            except:
                pass   
                     
    if vendor_name:
        data_dict['VendorName']= vendor_name    
    if vessel_no:
        data_dict['VesselName']=vessel_no
    if product_name:
        data_dict['ProductName']=product_name
    if activity_type:
        data_dict['ActivityType']=activity_type
    if ref_no:
        data_dict['NominationKey']=ref_no
    if date:
        data_dict['JobDate']=date
    if job_location:
        data_dict['JobLocation']=job_location
    if file_no:
        data_dict['VendorInternalReferencenumber']=file_no
    if bill_to:
        data_dict['EmAffiliates']=bill_to
    data_dict['doc_uuid']=uuid_doc

    return data_dict
    

def camin_inspection_headers(text_data,uuid_doc):
    
    line_data=text_data.split("\n")
    Quantity="Quantity header------------",camin_quantity_header(line_data,text_data,uuid_doc)
    Quality="Quality header------------",camin_quality_header(line_data,text_data,uuid_doc)
    return Quantity,Quality

# path=r"/datadrive/EM_testing/ExtractCustomFields/Camin_Quantity_document/US/537443EXXM01-33wnyylc383120-59-24-0459.text"
# text_data=read_textfile(path)
# print(camin_inspection_headers(text_data,"22222"))

files=os.listdir(r"/datadrive/EM_testing/ExtractCustomFields/Camin_Quantity_document/INT")
path=r"/datadrive/EM_testing/ExtractCustomFields/Camin_Quantity_document/INT"
for file in files:
    path_full=os.path.join(path,file)
    # print(path_full)
    print(file)
    text_data=read_textfile(path_full)
    Quantity,Quality=camin_inspection_headers(text_data,"22222")
    # print(Quantity)
    print(Quality)
    print("--------------------------------------------------------------------------")
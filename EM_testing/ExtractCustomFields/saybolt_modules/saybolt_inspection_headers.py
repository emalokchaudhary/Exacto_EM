import re
import os
import numpy as np
from saybolt_inspection_quantity_lineitems import FinalQuantityLineItems

def read_textfile(fileName):
    with open(fileName,encoding="utf-8") as f:
        text_data = f.read()
        # data=f.readlines()
        # print(text_data)
    return  text_data

def EmAffiliate_Quality(data):
    EM=""
    count=0
    remove_list=["page","website","saybolt","date","location","reason"]
    break_list=["attention", "your" ,"to whom it may concern"]
    for k,line in enumerate(data):
        match=re.search(r'Page\s+\d+\s*of\s*\d+',line,re.IGNORECASE)
        if match:
            span=match.span() 
            # print(match.group())
            try:
                li=[]
                final_li=[]
                while (count >=0):
                    if re.search(r"(Certificate of Quality)",data[k],re.I)  or re.search(r'^\s*Analysis Report',re.sub('\s+',' ',data[k]),re.I):
                        count +=1
                        break
                    li.append(data[k])
                    k +=1
                # print(li,"this is original")
                if count>=1:                    
                    l=[i for i in li if i]
                    # print(l)
                    for i in l:
                        if [j for j in remove_list if  j in i.lower()]:
                            continue
                        if [j for j in break_list if  j in i.lower()]:
                            break
                        final_li.append(i)
                    EM=(" ".join(final_li)).replace("\x0c","")
                # print("############################",EM)
            except:
                pass
        
    ############ for single page EM affiliates ######   
    if count==0:
        final_li=[]
        for i in data:
            
            if [j for j in remove_list if  j in i.lower()]:
                continue
            if [j for j in break_list if  j in i.lower()]:
                break
            final_li.append(i)
        final_li=[i for i in final_li if i]
        # print("******************",final_li)
        EM=(" ".join(final_li).strip())
        
    return EM


def saybolt_quality_header(data,text_data,uuid_doc):
    
    data_dict={}
    trip_no=vendor_name=activity_type=vessel_no=product_name=quantity=uom=file_no=date=job_location=ref_no=bill_to=''
    break_loop=0
    for k,line in enumerate(data):
        match=re.search(r'(Certificate of Quality)|(Certificate of Analysis)',line,re.I) or re.search(r'^\s*Analysis Report',re.sub('\s+',' ',line),re.I)
        if match:
            span=match.span() 
            try:
                for i in range(k+1,k+9):
                    match_p=re.search(r'(Sample submitted as)',data[i],re.IGNORECASE)
                    if match_p:    
                        sp=match_p.span()                        
                        product_name=data[i][sp[1]:].strip().split("    ")[0].replace(":","").strip()
                        # print(product_name)
                        
                    match_jobdate=re.search(r'(Date completed)',data[i],re.IGNORECASE)
                    if match_jobdate:    
                        sp_date=match_jobdate.span()                        
                        # print("yess",sp_date,match.group())
                        date=data[i][sp_date[1]:].strip().split("    ")[0].replace(":","").strip()
                        # print(date)
                        
                    match_vendor_ref_num=re.search(r'(Report number)',data[i],re.IGNORECASE)
                    if match_vendor_ref_num:    
                        sp_ref=match_vendor_ref_num.span()                        
                        file_no=data[i][sp_ref[1]:].strip().split("    ")[0].replace(":","").strip()
                                 
                    match_vessel=re.search(r'(Main Object )',data[i],re.IGNORECASE)
                    if match_vessel:    
                        sp_vessel=match_vessel.span()                                                
                        vessel_no=data[i][sp_vessel[1]:].strip().split("    ")[0].replace(":","").strip()
                        # print(vessel_no)   
                    
                    match_movement=re.search(r'(Sample type)',data[i],re.IGNORECASE)
                    if match_movement:    
                        sp_movement=match_movement.span()                                                
                        activity_type=data[i][sp_movement[1]:].strip().split("    ")[0].replace(":","").strip()                        
                        # print(activity_type)
                        
                    match_joblocation=re.search(r'(Place of sampling)',data[i],re.IGNORECASE)
                    if match_joblocation:    
                        sp_joblocation=match_joblocation.span()                                                
                        job_location=data[i][sp_joblocation[1]:].strip().split("    ")[0].replace(":","").strip()
                        # print(job_location,"ddddddd")          
            except:                
                pass 
            
            
            try:
                trip_nom=re.findall(r'Your reference (.*)',text_data)[0].strip().replace(":","")#.replace(" ","").split(":")[1].split("    ")[0]
                trip_nom= re.sub(r"Trip","",trip_nom)                
                trip_nom=trip_nom.split("/")
                for z in trip_nom:
                    # print(z)
                    if re.search(r'[A-Z]',z,re.I):
                        trip_no=z.strip()                        
                    else:
                        ref_no=z.strip()
                
            except:
                pass
            try:
                bill_to=EmAffiliate_Quality(data)
            except:                
                pass 
            break_loop +=1
        if break_loop >=1:
            break
        
        
        
    if trip_no:
        data_dict['Trip_no']=trip_no
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
             
 
def EmAffiliate_Quantity(data):
   
    EM=""
    trip_nomkey=""
    count=0
    remove_list=["page","website","sail4","mr.","ms.","mrs.","saybolt","date","location","reason"]
    break_list=["job no","to whom it may concern","report"]#,"attention", "your" ,]
    for k,line in enumerate(data):
        match=re.search(r'Page\s+\d+\s*of\s*\d+',line,re.IGNORECASE) #or re.search(r'Date',line,re.IGNORECASE)
        if match:
            span=match.span() 
            # print(match.group())
            try:
                li=[]
                final_li=[]
                while (count >=0):
                    if re.search(r"(Certificate of Quantity)|(Summary Loading )",data[k],re.I) or re.search(r'\s+(SUMMARY REPORT)',data[k],re.IGNORECASE):
                        count +=1
                        break
                    li.append(data[k])
                    k +=1
                
                if count>=1:                    
                    l=[i for i in li if i]
                    # print(l)
                    for i in l:
                        if [j for j in remove_list if  j in i.lower()]:
                            continue
                        if [j for j in break_list if  j in i.lower()]:
                            break
                        final_li.append(i)
                print(final_li)
                trip_nomkey=final_li.pop()
                # print(trip_nomkey)
                EM=(" ".join(final_li)).replace("\x0c","")
                # print("############################",EM)
            except:
                pass
        
    ############ for single page EM affiliates ######   
    if count==0:
        # print("HIIIIIIIIIIII")
        final_li=[]
        for i in data:
            
            if [j for j in remove_list if  j in i.lower()]:
                continue
            if [j for j in break_list if  j in i.lower()]:
                break
            final_li.append(i)
        final_li=[i for i in final_li if i]
        # print("******************",final_li)
        trip_nomkey=final_li.pop()   
        EM=(" ".join(final_li).strip())
        
    return EM,trip_nomkey

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
                file_no=re.findall(r'Our reference number(.*)',text_data)[0].strip().replace(":","")#.replace(" ","").split(":")[1].split("    ")[0]
                file_no=file_no.strip()
            except:
                pass
            
            
    # if trip_no:
    #     data_dict['Trip_no']=trip_no
    
    if vessel_no:
        data_dict['VesselName']=vessel_no
    if product_name:
        data_dict['ProductName']=product_name    
    if date:
        data_dict['JobDate']=date
    if job_location:
        data_dict['JobLocation']=job_location
    if file_no:
        data_dict['VendorInternalReferencenumber']=file_no
    data_dict['doc_uuid']=uuid_doc

    return data_dict

def saybolt_quantity_header(data,text_data,uuid_doc):
    # data_dict={}
    li=[]
    trip_no=vendor_name=activity_type=vessel_no=product_name=quantity=uom=file_no=date=job_location=ref_no=bill_to=''
    product_name_li=[]
    for k,line in enumerate(data):
        match=re.search(r'\s+(Certificate of Quantity)',line,re.IGNORECASE)  or re.search(r'\s+(SUMMARY REPORT)',line,re.IGNORECASE)
        
        if match:
            span=match.span()
            # print(match.group())
            try:
                for i in range(k-10,k+1):
                    
                    match_p=re.search(r'(Product)',data[i],re.IGNORECASE)
                    if match_p:    
                        sp=match_p.span()                        
                        product_name=data[i][sp[1]:].strip().split("    ")[0].replace(":","").strip()
                        
                        product_name_li.append(product_name)
                    
                    match_vessel=re.search(r'(Barge)|(Vessel)|(Object)',data[i],re.IGNORECASE)
                    if match_vessel:    
                        sp_vessel=match_vessel.span()                                                
                        vessel_no=data[i][sp_vessel[1]:].strip().split("    ")[0].replace(":","").strip()
                        # print(vessel_no)   
                        
                    match_jobdate=re.search(r'(Bill of Lading Date)|(Outturn date)|(B/L Date)',data[i],re.IGNORECASE)
                    if match_jobdate:    
                        sp_date=match_jobdate.span()                        
                        # print("yess",sp_date)
                        date=data[i][sp_date[1]:].strip().split("    ")[0].replace(":","").strip()
                        # print(date)
                        
                    match_joblocation=re.search(r'(Installation)|(Location)',data[i],re.IGNORECASE)
                    if match_joblocation:    
                        sp_joblocation=match_joblocation.span()                                                
                        job_location=data[i][sp_joblocation[1]:].strip().split("    ")[0].replace(":","").strip()
                        # print(job_location,"ddddddd")
                        
                    match_vendor_ref_num=re.search(r'(Job No)',data[i],re.IGNORECASE)
                    if match_vendor_ref_num:    
                        sp_ref=match_vendor_ref_num.span()                        
                        file_no=data[i][sp_ref[1]:].strip().split("    ")[0].replace(":","").strip()                        
                     
                        
                       
            except:
                pass
            
            try:
                # print("GGGGGGGoood")
                bill_to,trip_nomkey=EmAffiliate_Quantity(data)
                print(trip_nomkey,type(trip_nomkey),"ddddd")
                if not  re.search(r"[A-Z]+[0-9]+",trip_nomkey):
                    trip_nomkey=''
                
                    
                print(bill_to,trip_nomkey,"trip and EM")
                # trip_nom=re.findall(r'Your reference (.*)',text_data)[0].strip().replace(":","")#.replace(" ","").split(":")[1].split("    ")[0]
                trip_nom= re.sub(r"Trip","",trip_nomkey).replace("#","")                
                trip_nom=trip_nom.split("/")
                # print(trip_nom)
                for z in trip_nom:
                    # print(z)
                    if re.search(r'[A-Z]',z,re.I):
                        trip_no=z.strip()                        
                    else:
                        ref_no=z.strip()
            except:                
                pass 
        
    if product_name_li==[]:
        print("summarry loading GSV ")
        for k,line in enumerate(data):
            match= re.search(r'\s+(Summary Loading \(GSV\))',line,re.IGNORECASE)
        
            if match:
                span=match.span()
                # print(match.group())
                try:
                    for i in range(k-10,k+1):
                        
                        match_p=re.search(r'(Product)',data[i],re.IGNORECASE)
                        if match_p:    
                            sp=match_p.span()                        
                            product_name=data[i][sp[1]:].strip().split("    ")[0].replace(":","").strip()
                            
                            product_name_li.append(product_name)
                        
                        match_vessel=re.search(r'(Barge)|(Vessel)|(Object)',data[i],re.IGNORECASE)
                        if match_vessel:    
                            sp_vessel=match_vessel.span()                                                
                            vessel_no=data[i][sp_vessel[1]:].strip().split("    ")[0].replace(":","").strip()
                            # print(vessel_no)   
                            
                        match_jobdate=re.search(r'(Bill of Lading Date)|(Outturn date)',data[i],re.IGNORECASE)
                        if match_jobdate:    
                            sp_date=match_jobdate.span()                        
                            # print("yess",sp_date)
                            date=data[i][sp_date[1]:].strip().split("    ")[0].replace(":","").strip()
                            # print(date)
                            
                        match_joblocation=re.search(r'(Installation)',data[i],re.IGNORECASE)
                        if match_joblocation:    
                            sp_joblocation=match_joblocation.span()                                                
                            job_location=data[i][sp_joblocation[1]:].strip().split("    ")[0].replace(":","").strip()
                            # print(job_location,"ddddddd")
                            
                        match_vendor_ref_num=re.search(r'(Job No)',data[i],re.IGNORECASE)
                        if match_vendor_ref_num:    
                            sp_ref=match_vendor_ref_num.span()                        
                            file_no=data[i][sp_ref[1]:].strip().split("    ")[0].replace(":","").strip()                        
                        
                            
                        
                except:
                    pass
                
                try:
                    bill_to,trip_nomkey=EmAffiliate_Quantity(data)
                    
                    # trip_nom=re.findall(r'Your reference (.*)',text_data)[0].strip().replace(":","")#.replace(" ","").split(":")[1].split("    ")[0]
                    trip_nom= re.sub(r"Trip","",trip_nomkey).replace("#","")                
                    trip_nom=trip_nom.split("/")
                    # print(trip_nom)
                    for z in trip_nom:
                        # print(z)
                        if re.search(r'[A-Z]',z,re.I):
                            trip_no=z.strip()                        
                        else:
                            ref_no=z.strip()
                except:                
                    pass 
            
    
    
    for product in product_name_li:
        data_dict={}
        if trip_no:
            data_dict['Trip_no']=trip_no   
        if vendor_name:
            data_dict['VendorName']= vendor_name      
        if vessel_no:
            data_dict['VesselName']=vessel_no
        if product_name:
            data_dict['ProductName']=product
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
        
        li.append(data_dict)
        
    if li==[]:
        qunatity_loding=saybolt_qnt_loading_sum_report(data,text_data,uuid_doc)
        li.append(qunatity_loding)
        
    return li


def saybolt_inspection_headers(text_data,uuid_doc):
    
    line_data=text_data.split("\n")
    Quantity_h=saybolt_quantity_header(line_data,text_data,uuid_doc)
    Quantity_Line=FinalQuantityLineItems(text_data)
    # Qualiity="Quality header------------",saybolt_quality_header(line_data,text_data,uuid_doc)
    # EmAffiliate(line_data)

    return Quantity_h ,Quantity_Line # Qualiity 


#########       Quality
# path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/CHEM-US/1300399295/COA_KIRBY_10562_USEBARGCHE-2011-045___5067731_13074_00001807_20210107164810_Bruna_Kukiela.text"
# path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/EU/1200143480/COA_Cayenne_INTB009FIN-2011-0411_12004_00128329_20201130224820_ExxonMobil_BNL_Mogas_supply_Operations.text"
# path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/US/1300398489/COA_CBC_317_Trip__2020-BT-VP-EHC120-11_13074_00001689_20201214081153_Kyle_C_Mcilroy.text"
###########3 Quantity Path
path="/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/CHEM-US/1300395101/5003856-10HTCO3118LoadTolueneExxonMobilBaytownFinalReport.text"
# ---------summert report
# path="/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/CHEM-US/1300405578/MergedReport_EXXONMOBILCHEMICALCO_USEBARGARO-2106-0855555525_1305500047854_General_Inspection.text"
#--------- summery loading (gsv)
# path="/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/EU/1200146545/FullReport1201000086990.text"
# path="/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/EU/10820200963/SURVEYREPORTODOARDOAMORETTI.text"
##### both are present quality and quantity
# path='/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/EU/16001200075447/MergedReport_Inspection.text'





# path="/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/EU/16001200076804/COA_THEO_T_INTV009FIN_ExxonMobil_Soir.text"
text_data=read_textfile(path)

Quantity_h ,Quantity_Line=saybolt_inspection_headers(text_data,"22222")
print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
print(Quantity_h)
print(Quantity_Line)

def saybolt_qnt_hd_li_merge(qnty_header_data,qnty_line_item):
    qnty_data=[]
    temp=qnty_header_data
    if qnty_line_item !={}:
        for i in qnty_line_item:            
            d={}
            d=temp
            d['NominatedQuantity'] = qnty_line_item[i]
            d['UnitOfMeasure']=i
            qnty_data.append(d.copy()) # copy() for removing memory refrence 
    
    # for j in qnty_data:
    #     print("\n",j)
         
    return qnty_data 
        
        
      

                
'''        


files=os.listdir(r"/datadrive/EM_testing/ExtractCustomFields/Saybolt_qnt_quality_documents/Quantity_doc/EU/Summary_report")#Summary_loading_GSV
path=r"/datadrive/EM_testing/ExtractCustomFields/Saybolt_qnt_quality_documents/Quantity_doc/EU/Summary_report"  #COQ_GSV
co=1
for file in files:
    path_full=os.path.join(path,file)
    # print(path_full)
    print(file)
    text_data=read_textfile(path_full)
    # Quality=saybolt_inspection_headers(text_data,"22222")
    Quantity_h,Quantity_Line =saybolt_inspection_headers(text_data,"22222")
    if len(Quantity_h)==len(Quantity_Line):
        qnty_li=[]
        for j in Quantity_h:
            for z in Quantity_Line :
                if j.get("ProductName")==z.get("ProductName"):
                    z.pop("ProductName")                
                    
                    qnty_data =saybolt_qnt_hd_li_merge(j,z)
                    for i in qnty_data:
                        qnty_li.append(i)
    print(qnty_li)
    # print(Quantity)
    # print(Quality)
    print(co,"--------------------------------------------------------------------------")
    co +=1
'''   


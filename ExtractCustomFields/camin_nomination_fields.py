import os,re 
import sys
sys.path.insert(0,'../..')

def file_data(filepath):
    
    with open (filepath, 'r') as f:
        lines=f.readlines() 
        # print(lines)
    return lines

def Trip_Nomination(data):
    fields_nomination={"Trip_no":"NA","Nomination_num":"NA"}
    for k,line in enumerate(data):
        match=re.search(r'(TRIP)|(trip)',line,re.IGNORECASE)
        
        if match:
            span=match.span()
            try: 
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                fields_nomination["Trip_no"]=hor_data[0].strip()
                fields_nomination["Nomination_num"]=hor_data[1].strip().split(" ")[0]
                
            except:
                print("erron in trip number)")
                fields_nomination["Trip_no"]="NA"
                fields_nomination["Nomination_num"]="NA"
    # print(fields_nomination)
    return fields_nomination


def Activity_loction(data):
    # print(data)
    fields_activity={"Activity_type":"NA","Transport":"NA","Loction":"NA","Inspector":"NA"}
    for k,line in enumerate(data):
        match=re.search(r'(Inspector:)',line,re.IGNORECASE)        
        if ("Inspector" in line) and (" Inspection Status" in line):
            temp=data[k-2]+data[k-1]
            inspector=data[k]            
            temp=re.sub("\s+"," ",temp)
            try: 
                # hor_data=line[max(0,span[0]+0):max(0,len(line))]
                Activity=temp.split(":")
                if len(Activity)>1:
                    # print(Activity)
                    fields_activity["Activity_type"]=Activity[0].strip()
                    loc=Activity[1].split(") -")[0]+")"
                    fields_activity["Transport"]=loc.strip()
                    fields_activity["Loction"]=Activity[1].split(") -")[1].strip()
                    
                
            except:
                print("erron in activity,loc,transport")
                fields_activity["Activity_type"]="NA"
                fields_activity["Transport"]="NA"
                fields_activity["Loction"]="NA"
            # break
        if match:
            span=match.span()
            try:
               
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                fields_activity["Inspector"]=hor_data[0].strip()
                # print(hor_data[0])
            except:
                print("error in find inspector")
                fields_activity["Inspector"]="NA"
           
    # print(fields_activity)
    return fields_activity

def grade(data):
    for k,line in enumerate(data):
        match=re.search(r'(GRADE)',line,re.IGNORECASE)
        
        if match:
            span=match.span()
            try: 
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                hor_data=hor_data[0].strip()
                
                
            except:
                print("erron in garde)")
                hor_data="NA"                
    return hor_data

def Etimate_time(data):
    for k,line in enumerate(data):
        match=re.search(r'(ETA)',line,re.IGNORECASE)
        
        if match:
            span=match.span()
            try: 
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                time=hor_data[0].strip()
                # print(time)
                
            except:
                print("erron in ETA")
                time="NA"  
            break              
    return time

def Nominated_Quantity(data):
    for k,line in enumerate(data):
        match=re.search(r'(Total Nominated Quantity)',line,re.IGNORECASE)
        
        if match:
            span=match.span()
            try: 
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                NominatedQuantity=hor_data[0].strip().split(" ")[0]
                NominatedQuantity_unit=hor_data[0].strip().split(" ")[1]
                
            except:
                print("erron in Nominated number)")
                NominatedQuantity="NA" 
                NominatedQuantity_unit="NA" 
            break              
    return NominatedQuantity,NominatedQuantity_unit

def Inspection_req(data):
    for k,line in enumerate(data):
        match=re.search(r'(INSPECTION REQUIREMENTS)',line,re.IGNORECASE)
        
        if match:
            span=match.span()
            try: 
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                inspection_req=hor_data[0].strip()
                # print(inspection_req)
                
            except:
                print("erron in Inspection req.")
                inspection_req="NA"  
            break              
    return inspection_req

def Region_country(data):
    for k,line in enumerate(data):
        match=re.search(r'(Region)',line,re.IGNORECASE)        
        if match:
            span=match.span()
            try: 
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                region=hor_data[0].strip()
                # print(hor_data)                
            except:
                print("erron in garde)")
                region="NA"                
    return region
    
def Voyage_Parcel_num(data):
    for k,line in enumerate(data):
        match=re.search(r'(Voyage Parcel External Reference Number)',line,re.IGNORECASE)        
        if match:
            span=match.span()
            try: 
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                nomination_key=hor_data[0].strip()
                # print(nomination_key)                
            except:
                print("erron in garde)")
                nomination_key="NA"                
    return nomination_key
    

def Nomination_field(file_path):
    # print("enter Nomination Fields")
    Nomination_field_dict={}
    data=file_data(file_path)

    try:
        field_dict=Trip_Nomination(data)
        Nomination_field_dict.update(field_dict)
        # print(Nomination_field_dict)
    except:
        print("error in nomination funtion while calling trip funtion")
    try:
        activity_loc=Activity_loction(data)
        # print(activity_loc)
        Nomination_field_dict.update(activity_loc)
    except:
        print("error in your  code")

    Nomination_field_dict["Region"]=Region_country(data)
    Nomination_field_dict["Nomination_key"]=Voyage_Parcel_num(data)
    Nomination_field_dict["Grade_type"]=grade(data)
    Nomination_field_dict["ETA"]=Etimate_time(data)
    Total_NominatedQuantity, unit=Nominated_Quantity(data)
    Nomination_field_dict["Nominated Quantity"]=Total_NominatedQuantity
    Nomination_field_dict["Quantity_unit"]=unit
    Nomination_field_dict["Inspection requreiment"]=Inspection_req(data)

    
    
    # print("Extract dic by Yogesh",Nomination_field_dict)
    return Nomination_field_dict
    # return a
print(Nomination_field(r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/20E543802v.1/20E543802v.1.text"))

# def Voyage_Parcel_num_PPPP(data):
#     for k,line in enumerate(data):
#         match=re.findall(r'(Voyage Parcel External Reference Number)',line,re.IGNORECASE)
#         print(match) 
#         if match:
#             # if len(match)<1:

#                 hor_data=line  
#                 print(hor_data.split(":"))      
#     #     if match:
#     #         span=match.span()
#     #         try: 
#     #             hor_data=line[max(0,span[1]+1):max(0,len(line))]
#     #             hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
#     #             nomination_key=hor_data[0].strip()
#     #             # print(nomination_key)                
#     #         except:
#     #             print("erron in garde)")
#     #             nomination_key="NA"                
#     # return nomination_key
    

# data=file_data(r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/20E536366v.1/20E536366v.1.text")
# print(Voyage_Parcel_num_PPPP(data))
    
# def Voyage_Parcel_num_PPPP(data):
#     li=[]
#     for k,line in enumerate(data):
#         match=re.search(r'(Voyage Parcel External Reference Number)',line,re.IGNORECASE)     
#         if match:
#             span=match.span()
#             try: 
#                 hor_data=line[max(0,span[1]+1):max(0,len(line))]
#                 hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
#                 nomination_key=hor_data[0].strip()
#                 li.append(nomination_key)
#                 nomination_key=li
#                 # print(li)                
#             except:
#                 print("erron in garde)")
#                 nomination_key="NA"                
#     return nomination_key
    
# def Em_affiliates(data):
#     for k,line in enumerate(data):
#         match=re.search(r'(Invoice Instructions)',line,re.IGNORECASE)
        
#         if match:
#             span=match.span()
#             # print(span)
#             for i in range(k+1,k+2):
#                 # print(i)
#                 if re.search(r'(Bill Invoice To)',data[i],re.I) and re.search(r'(Item to Bill)',data[i],re.I):
#                     a=(data[i].lower()).find("Item to Bill".lower())
#                     print(data[i])
#                     for j in range(i+1,i+5):
#                         print(data[j])
#                     #     print(re.sub("\s+"," ",data[j][:a-3]))


import os,re 
import sys
# sys.path.insert(0,r'datadrive//unzip//ips//invoiceProduct_solution//apps')
from db_connection import connect_db as conn
import uuid
sys.path.insert(0,'../..')

def file_data(filepath):
    
    with open (filepath, 'r',encoding="utf-8") as f:
        text_data=f.readlines() 
        # text_data=f.read()
        # print("rrrrrrrrrrrrrrrrrrrrrr",text_data)
    return text_data

def Trip_Nomination(data):
    fields_nomination={"trip_number":"NA","nomination_number":"NA"}
    for k,line in enumerate(data):
        match=re.search(r'(TRIP)|(trip)',line,re.IGNORECASE)
        
        if match:
            span=match.span()
            try: 
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                fields_nomination["trip_number"]= hor_data[0].strip()
                fields_nomination["nomination_number"]= hor_data[1].strip().split(" ")[0]
                
            except:
                print("erron in trip number)")
                fields_nomination["trip_number"]="NA"
                fields_nomination["nomination_number"]="NA"
    # print(fields_nomination)
    return fields_nomination


def Activity_loction(data):
    # print(data)
    load=[]
    Trans=[]
    loca=[]
    inspect=[]
    fields_activity={"Activity_Type":"NA","Vessel_Name":"NA","JOB_Location":"NA","Vendor_Name":"NA"}
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
                    load.append(Activity[0].strip())

                    fields_activity["Activity_Type"]=  load  #Activity[0].strip()
                    loc=Activity[1].split(") -")[0]+")"
                    Trans.append(loc.strip())
                    fields_activity["Vessel_Name"]=Trans   #loc.strip()
                    loca.append(Activity[1].split(") -")[1].strip())
                    fields_activity["JOB_Location"]=loca     #Activity[1].split(") -")[1].strip()
                    
                
            except:
                print("erron in activity,loc,transport")
                fields_activity["Activity_Type"]=["NA"]
                fields_activity["Vessel_Name"]=["NA"]
                fields_activity["JOB_Location"]=["NA"]
            # break
        if match:
            span=match.span()
            try:
               
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                inspect.append(hor_data[0].strip())
                fields_activity["Vendor_Name"]=  inspect   #hor_data[0].strip()
                # print(hor_data[0])
            except:
                print("error in find inspector")
                fields_activity["Vendor_Name"]=["NA"]
           
    # print(fields_activity)
    return fields_activity

def grade(data):
    gra=[]
    for k,line in enumerate(data):
        match=re.search(r'(GRADE)',line,re.IGNORECASE)
        
        if match:
            span=match.span()
            try: 
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                hor_data=hor_data[0].strip()
                gra.append(hor_data)
                hor_data=gra
                
                
            except:
                print("erron in garde)")
                hor_data=["NA" ]               
    return hor_data

def Etimate_time(data):
    tim=[]
    for k,line in enumerate(data):
        match=re.search(r'(ETA:)',line,re.IGNORECASE)
        
        if match:
            span=match.span()
            try: 
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                time=hor_data[0].strip()
                tim.append(time)
                time=tim
                # print(time)
                
            except:
                print("erron in ETA")
                time=["NA"  ]
                         
    return time

def Nominated_Quantity(data):
    quantity=[]
    unit=[]
    for k,line in enumerate(data):
        match=re.search(r'(Total Nominated Quantity)',line,re.IGNORECASE)
        
        if match:
            span=match.span()
            try: 
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                # NominatedQuantity=hor_data[0]
                # print("NNNNNNNN",NominatedQuantity)
                NominatedQuantity=hor_data[0].strip().split(" ")[0]
                quantity.append(NominatedQuantity)
                # print(quantity)
                NominatedQuantity=quantity
                NominatedQuantity_unit=hor_data[0].strip().split(" ")[1]
                unit.append(NominatedQuantity_unit)
                NominatedQuantity_unit=unit
            except:
                print("erron in Nominated number)")
                NominatedQuantity=["NA" ]
                NominatedQuantity_unit=["NA"] 
            break 
    # return NominatedQuantity             
    return NominatedQuantity,NominatedQuantity_unit

def Inspection_req(data):
    ins=[]
    for k,line in enumerate(data):
        match=re.search(r'(INSPECTION REQUIREMENTS:)',line,re.IGNORECASE)
        
        if match:
            span=match.span()
            try: 
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                inspection_req=hor_data[0].strip()
                ins.append(inspection_req)
                inspection_req=ins
                # print(inspection_req)
                
            except:
                print("erron in Inspection req.")
                inspection_req=["NA"]  
            break              
    return inspection_req

def Region_country(data):
    reg=[]
    region=""
    for k,line in enumerate(data):
        match=re.search(r'(Region)',line,re.IGNORECASE)        
        if match:
            span=match.span()
            try: 
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                region=hor_data[0].strip()
                reg.append(region)
                region=reg
                # print(hor_data)                
            except:
                print("erron in garde)")
                region=["NA"]                
    return region
    
def Voyage_Parcel_num(data):
    Nom_key=[]
    for k,line in enumerate(data):
        match=re.search(r'(Voyage Parcel External Reference Number)',line,re.IGNORECASE)        
        if match:
            span=match.span()
            try: 
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                nomination_key=hor_data[0].strip()
                Nom_key.append(nomination_key)
                nomination_key=Nom_key
                # print(nomination_key)                
            except:
                print("erron in garde)")
                nomination_key=["NA"  ]              
    return nomination_key
    
def bill_invoice_to(data):
    # data=data.split("\n")
    l=[]
    res=""
    count=0
    break_point=0
    k=0
    
    # for z in range(len(data)):
        # break_point=0
        # if (re.search(r'(Bill Invoice To)',data[z],re.I) and re.search(r'(Item to Bill)',data[z],re.I) and re.search(r'(Split)',data[z],re.I)):
    while(k<len(data)):
        break_point=0
        
        if (re.search(r'(Bill Invoice To)',data[k],re.I) and re.search(r'(Item to Bill)',data[k],re.I) and re.search(r'(Split)',data[k],re.I)):
            res=""
            for i in range(k,len(data)):
                # if (re.search(r'(Bill Invoice To)',data[i],re.I) and re.search(r'(Item to Bill)',data[i],re.I) and re.search(r'(Split)',data[i],re.I)):
                    k+=1
                    ed=(data[i].lower()).find('Item to Bill'.lower())
                    # print(ed)
                    for j in range(i+1,len(data)):
                        k+=1
                        if ("quantity" in data[j][ed-3:].lower()or "quality" in data[j][ed-3:].lower()):
                            # print(data[j])
                            count+=1
                            if count>1 :
                                res= re.sub("\s+"," ",res)
                                l.append(res)
                                # print("if inside the ", l)
                                res= re.sub("\s+"," ",data[j][:ed-3])
                                # print("if inside the ", res)
                            else:
                                res= re.sub("\s+"," ",data[j][:ed-3])
                                # print("if inside the else part asre", res)
                            # print("if condition satisfied", l)
                        elif (" "==re.sub("\s+"," ",data[j])):
                            l.append(re.sub(r"\s+"," ",res))
                            # print("elif ke inside ", l)
                            break_point=1
                            break
                        else:
                            res+=re.sub("\s+"," ",data[j][:ed-3])
                            # print("else ke part", res)

                    if break_point==1:
                            break
        k+=1  
    l=[i for i in l if i]
    bill_invoice=[]          
    for k in l:
        if  "ExxonMobil"  in k :
            bill_invoice.append(k.strip())

    # print(bill_invoice)
    return bill_invoice
                            


def Nomination_field(text_data):
    
    Nomination_field_dict={}
    # data=file_path
    data=text_data
    # print("tttttttttttttttttttttttttt",data)
    # data=file_data(file_path)
    if re.search('TRIP:'," ".join(data),re.IGNORECASE):
        print("This a nomination vendor")
        # data=data.split("\n")
        try:
            field_dict=Trip_Nomination(data)
            Nomination_field_dict.update(field_dict)
            # print(Nomination_field_dict)
        except:
            print("error in nomination funtion while calling trip funtion")
        # try:
        #     activity_loc=Activity_loction(data)
        #     # print(activity_loc)
        #     Nomination_field_dict.update(activity_loc)
        # except:
        #     print("error in your  code")

        Nomination_field_dict["region"]=Region_country(data)[0]
        Nomination_field_dict["status"]=0

        # Nomination_field_dict["Nomination_Key"]=Voyage_Parcel_num(data)
        # Nomination_field_dict["Product_Name"]=grade(data)
        # Nomination_field_dict["JOB_Date"]=Etimate_time(data)
        # Total_NominatedQuantity, unit=Nominated_Quantity(data)
        # # Total_NominatedQuantity= Nominated_Quantity(data)
        # Nomination_field_dict["Nominated_Quantity"]=Total_NominatedQuantity
        # Nomination_field_dict["Unit_of_Measure"]=unit
        # Nomination_field_dict["Type_of_Inspection"]=Inspection_req(data)
        # Nomination_field_dict["EM_Affiliates"]=bill_invoice_to(data)
        # # print("Extract dic by Yogesh",Nomination_field_dict)
        return Nomination_field_dict

# print("parcel",Nomination_field(r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/20E536366v.1/20E536366v.1.text"))
# print("Nooooooooooooooooo",Nomination_field(file_data(r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/20E536366v.1/20E536366v.1.text")))
# print("Nooooooooooooooooo",Nomination_field(file_data(r"/datadrive/20E543802v.1.text")))

# row = Nomination_field(file_data(r"/datadrive/20E543802v.1.text"))

# cursor = conn.cursor()

# insert_statement = "INSERT INTO exacto_cgi_nom_hd (trip_number, nomination_number, region, status  ) VALUES (?, ?, ?, ?)"

 





values = (row.get('trip_number',''), row.get('nomination_number',''), row.get('region',''), row.get('status',0))

cursor.execute(insert_statement, values)

        

        

conn.commit()

 



cursor.close()

conn.close()




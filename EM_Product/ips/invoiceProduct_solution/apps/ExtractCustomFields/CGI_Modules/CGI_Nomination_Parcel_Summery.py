import re

# file=open(r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/CGI/CHEM-US/305468/21E562874v.1.text','r',encoding='windows-1258')
# read=file.read()
# lines=read.split('\n')
# '''@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''
def Nominated_Quantity(data):
    quantity=[]
    unit=[]
    for k,line in enumerate(data):
        match=re.search(r'(Total Nominated Quantity)',line,re.IGNORECASE)
        
        if match:
            span=match.span()
            try: 
                # print(line)
                hor_data=line[max(0,span[1]+1):max(0,len(line))]
                hor_data=[x for x in (str(hor_data).strip().split("    ")) if len(x)>1]
                # NominatedQuantity=hor_data[0]
                # print("NNNNNNNN",NominatedQuantity)
                NominatedQuantity=hor_data[0].strip().split(" ")[0]
                NominatedQuantity = re.sub(",", "", NominatedQuantity)
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
        else:
           NominatedQuantity = [None]   
           NominatedQuantity_unit = [None] 
    # return NominatedQuantity             
    return NominatedQuantity,NominatedQuantity_unit

# '''@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''
# '''@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''
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
                print("erron in garde)@@@@@@@@@@@@@@@@")
                nomination_key=["NA"  ] 
        else:
            nomination_key=["NA"]             
    return nomination_key
    
# '''@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''
# '''@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''
def bill_invoice_to(data):
    bill_invoice = []
    for k,line in enumerate(data):
        match = re.search(r'Bill Invoice To',line)

        if match:
            # print('yes')
            affilates = data[k+1].split("  ")[0]
            # print(affilates)
            if  len(data[k+2].split("  ")[0]) >0:
                affilates += data[k+2].split("  ")[0]
            else:
                continue
            affilates = re.sub('\n','',affilates)
            # print(affilates)
            bill_invoice.append(affilates)
    # print('This is EM Affiliates',bill_invoice)
    return bill_invoice
# '''@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''
# print(lines)
def parcel_data(lines):
    # print('#######These are the lines##############',lines)
    for line in range(0,len(lines)):
        table=re.search(r'((Transport)+\s*(Location)+\s*(Activity)+\s*(Grade)+\s*(Quantity)+\s*(ETA)+\s*(Supply Contract Window)+\s*(Inspector)+\s*((Inspection Requirements)|(Inspection Requiremen))+\s*)+',lines[line])
        if(table!=None):
            
            start_table=line
            # print('#######$$$$$$This is the start line##############',start_table)
        end=re.search(r'\s*((Page)|(PAGE)|(page))+\s*\d+\s*((of)|(OF))+\s*\d+\s*',lines[line])
        if(end!=None):
            # Page 1 of 6
            end_table=line
            # print('#######$$$$$$This is the end of line##############',end_table)
            break

    all_table=lines[int(start_table):int(end_table)-1]


    for one_line in all_table:
            start_index_Transport=re.search(r'\s*Transport',one_line)
            end_index_Transport=re.search(r'Location',one_line)
            # print('1',start_index_Test.span(),end_index_Test.span())

            start_index_Location=re.search(r'Location',one_line)
            end_index_Location=re.search(r'Activity',one_line)
            # print('2',start_index_Methods.span(),end_index_Methods.span())

            start_index_Activity=re.search(r'Activity',one_line)
            end_index_Activity=re.search(r'Grade',one_line)
            # print('3',start_index_Min.span(),end_index_Min.span())

            start_index_Grade=re.search(r'Grade',one_line)
            end_index_Grade=re.search(r'Quantity',one_line)
            # print('4',start_index_Max.span(),end_index_Max.span())

            start_index_Quantity=re.search(r'Quantity',one_line)
            end_index_Quantity=re.search(r'ETA',one_line)
            # print('5',start_index_UOM.span(),end_index_UOM.span())

            start_index_ETA=re.search(r'ETA',one_line)
            end_index_ETA=re.search(r'Supply Contract Window',one_line)
            # print('6',start_index_Typical.span(),end_index_Typical.span())

            start_index_Supply_Contract_Window=re.search(r'Supply Contract Window',one_line)
            end_index_Supply_Contract_Window=re.search(r'Inspector',one_line)
            # print('7',start_index_R_O_.span(),end_index_R_O_.span())

            start_index_Inspector=re.search(r'Inspector',one_line)
            end_index_Inspector=re.search(r'Inspection',one_line)
            # print('8',start_index_Req_.span(),end_index_Req_.span())

            start_index_Inspection=re.search(r'(Inspection Requirements)|(Inspection Requiremen)',one_line)
            # end_index_Inspection=re.search(r'Requirements',one_line)

            # start_index_Requirements=re.search(r'Requirements',one_line)

            # print('9',start_index_Comment.span())
            break
    table_content=[]

    # print(all_table[1][int(start_index_Transport):int(end_index_Transport)])
    for one_line in range(1,len(all_table)):
            
            table_content.append([all_table[one_line][int(start_index_Transport.span()[0]):int(end_index_Transport.span()[0])],all_table[one_line][int(start_index_Location.span()[0]):int(end_index_Location.span()[0])],all_table[one_line][int(start_index_Activity.span()[0]):int(end_index_Activity.span()[0])],all_table[one_line][int(start_index_Grade.span()[0]):int(end_index_Grade.span()[0])],all_table[one_line][int(start_index_Quantity.span()[0]):int(end_index_Quantity.span()[0])],all_table[one_line][int(start_index_ETA.span()[0]):int(end_index_ETA.span()[0])],all_table[one_line][int(start_index_Supply_Contract_Window.span()[0]):int(end_index_Supply_Contract_Window.span()[0])],all_table[one_line][int(start_index_Inspector.span()[0]):int(end_index_Inspector.span()[0])],all_table[one_line][int(start_index_Inspection.span()[0]):]])


    list_for_check=['Discharge','Load']


    for one_list in range(0,len(table_content)):
            try:
                for one_list in range(0,len(table_content)):
                    try:
                        table_content[one_list][6]=re.sub(r'\s+','',table_content[one_list][6])
                        table_content[one_list][2]=re.sub(r'\s+','',table_content[one_list][2])
                        if(table_content[one_list][6]!='n/a' and table_content[one_list][2] not in list_for_check):
                            
                            # print(table_content[one_list])
                            # print(table_content[one_list])
                            table_content[one_list-1][0]=table_content[one_list-1][0].rstrip()+table_content[one_list][0].rstrip()
                            table_content[one_list-1][0]=re.sub('\s+',' ',table_content[one_list-1][0])

                            table_content[one_list-1][1]=table_content[one_list-1][1].rstrip()+table_content[one_list][1].rstrip()
                            table_content[one_list-1][1]=re.sub('\s\s+','',table_content[one_list-1][1])
                            table_content[one_list-1][1].strip()

                            table_content[one_list-1][2]=table_content[one_list-1][2]+table_content[one_list][2]
                            table_content[one_list-1][2]=re.sub('\s+',' ',table_content[one_list-1][2])

                            table_content[one_list-1][3]=table_content[one_list-1][3].rstrip()+table_content[one_list][3].rstrip()
                            table_content[one_list-1][3]=re.sub('\s+',' ',table_content[one_list-1][3])

                            table_content[one_list-1][4]=table_content[one_list-1][4]+table_content[one_list][4]
                            table_content[one_list-1][4]=re.sub('\s+',' ',table_content[one_list-1][4])

                            table_content[one_list-1][5]=table_content[one_list-1][5]+table_content[one_list][5]
                            table_content[one_list-1][5]=re.sub('\s+',' ',table_content[one_list-1][5])

                            table_content[one_list-1][6]=table_content[one_list-1][6]+table_content[one_list][6]
                            table_content[one_list-1][6]=re.sub('\s+',' ',table_content[one_list-1][6])

                            table_content[one_list-1][7]=table_content[one_list-1][7]+table_content[one_list][7]
                            table_content[one_list-1][7]=re.sub('\s+',' ',table_content[one_list-1][7])

                            table_content[one_list-1][8]=table_content[one_list-1][8]+table_content[one_list][8]
                            table_content[one_list-1][8]=re.sub('\s+',' ',table_content[one_list-1][8])

                            # table_content[one_list-1][9]=table_content[one_list-1][9]+table_content[one_list][9]
                            # table_content[one_list-1][9]=re.sub('\s+',' ',table_content[one_list-1][9])
                            
                            table_content.remove(table_content[one_list])
                            break
                    except:
                        pass
            except:
                pass
    Total_NominatedQuantity, unit=Nominated_Quantity(lines)
    # print(Total_NominatedQuantity, unit)
    bill_invoice = bill_invoice_to(lines)
    # print('@@@@@@@@@@@@@',bill_invoice)
    Nomination_ref = Voyage_Parcel_num(lines)
    # print(Nomination_ref)


    count = 0
    count_1 = 0
    for i in table_content:
        # print(len(i))
        # i.pop(-1)
        i[0] = re.sub('([(]\w+[)])','',i[0]).strip()
        i[-1] = re.sub('[/]\s*Time\s*log','',i[-1]).strip()
        i[-1] = re.sub('[/]','&',i[-1]).strip()
        i[5] = re.sub('\s*\d{2}[:]\d{2}','',i[5])
        i.pop(6)
        i.pop(4)
        for j in Total_NominatedQuantity:
            i.append(j)
    for i in table_content:
        for j in unit:
            i.append(j)
    for i in table_content:
        if count < len(bill_invoice):
            i.append(bill_invoice[count])
            count+=1
    for i in table_content:
        if count_1 < len(Nomination_ref):
            i.append(Nomination_ref[count_1])
            count_1+=1
    # print(table_content)
    Parcel_list=[]

    # print(table_content)
    keys=['VesselName','JobLocation','ActivityType','ProductName','JobDate','VendorName','TypeofInspection','NominatedQuantity','UnitOfMeasure','EmAffiliates','NominationKey']
    partial_data=[]

    for i in table_content:
        a=dict(zip(keys,i))
        partial_data.append(a)

    # print(partial_data)
    last_list=[]
    last_list.append(partial_data)
    return last_list

# a = parcel_data(lines)
# print(a)


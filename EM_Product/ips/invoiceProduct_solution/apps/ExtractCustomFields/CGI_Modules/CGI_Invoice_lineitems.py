import re
from ExtractCustomFields.EM_logging import logger

def inv_qualitylineitem(des):
    oodes=re.sub('\''," ",des)
    des=re.sub(r'\s*Analysis\s*of.*[:]\s*',"",des)
    lineitem=des.split("|")
    final_list=[]
    for i in range(len(lineitem)):
        f={}
        TestName=""
        TestMethod=""
        QuantityValue=1.0
        UnitPrice=0.0
        try:
            TestName=lineitem[i].split(",")[0]
        except:
            print("testname not recognize")
        try:
            TestMethod=(lineitem[i].split(",")[1]).split("=")[0]
        except:
            print('textmethod not recognize')
        try:
            if("@" in (lineitem[i].split(",")[1]).split("=")[1]):
                QuantityValue=((lineitem[i].split(",")[1]).split("=")[1]).split("@")[0]
                QuantityValue=float(re.sub("\s+","",QuantityValue))
        except:
            print('Quantity value not recognize')
        try:
            if(re.search(r'[0-9]+[\.]*[0-9]*\s*$',((lineitem[i].split(",")[1]).split("=")[1]))):
                UnitPrice=float(re.search(r'[0-9]+[\.]*[0-9]*\s*$',((lineitem[i].split(",")[1]).split("=")[1]))[0])
        except:
                print('unit price is not recognized')
        f['Description'] =oodes
        f['QuantityValue'] = str(QuantityValue)
        f['Price'] = str(UnitPrice)
        f['UoM'] = 'Per test'
        f['Charge']=''
        f['Share']=''
        f['ShareCharge']=''
        f['TestName']=TestName
        f['TestMethod']=TestMethod
        f['Tax']=''
        f['Amount']=''
        f['Discount']=''
        final_list.append(f)        
        
    return final_list

def find_header_item(lines):
    st=-1
    l=['description','qty','rate','amount']
    st_header=[]
    for i in range(len(lines)):
        lines[i]=lines[i].lower()
        if(re.search('description',lines[i]) and re.search('qty',lines[i]) and re.search('amount',lines[i]) and re.search('rate',lines[i])):
            st=i
            for j in l:
                st_header.append(lines[i].find(j))
            break
    return st,st_header
def cgi_invoice_lineitem_extraction(lines):
    res=[]
    kk=0
    breakpoint=0
    itemno=1
    final_dict={}
    while(kk<len(lines)):
        line=lines[kk:]
        st,st_header=find_header_item(line)
        dict_row_data={}
        invoice_total=""
        description=''
        qty=''
        rate=''
        amount=''
        if(st!=-1):
            kk+=st
            for i in range(st+1,len(line)):
                kk+=1
                if(re.search(r'invoice(\s+)*total',line[i],re.I)):
                    dict_row_data={}
                    temp=re.sub("\s+","",line[i],re.I).lower()
                    invoice_total=re.sub(r'invoice(\s+)*total.\s*',"",temp)
                    invoice_total=re.sub(r'\n',"",invoice_total)
                    description=re.sub(r"(\s*\|\s*)*$","",description)
                    dict_row_data['Description']=description
                    dict_row_data['QuantityValue']=qty
                    dict_row_data['Price']=rate
                    dict_row_data['amount']=amount
                    res.append(dict_row_data)
                    breakpoint=1
                    break
                elif(re.search(r'we understand that you have a',line[i],re.I) or re.search(r'choice . . . thanks for choosing',line[i],re.I)):
                    dict_row_data={}
                    description=re.sub(r"(\s*\|\s*)*$","",description)
                    dict_row_data['Description']=description
                    dict_row_data['QuantityValue']=qty
                    dict_row_data['Price']=rate
                    dict_row_data['amount']=amount
                    res.append(dict_row_data)
                    itemno+=1
                    break
                elif(re.search(r'[0-9]',line[i][st_header[1]-5:])):
                    dict_row_data={}
                    description=re.sub(r"(\s*\|\s*)*$","",description)
                    dict_row_data['Description']=description
                    dict_row_data['QuantityValue']=qty
                    dict_row_data['Price']=rate
                    dict_row_data['amount']=amount
                    res.append(dict_row_data)
                    
                    itemno+=1
                    description=re.sub("\s+"," ",line[i][:st_header[1]-5])
                    qty=re.sub('\s+',"",line[i][st_header[1]-5:st_header[2]-5])
                    rate=re.sub('\s+',"",line[i][st_header[2]-5:st_header[3]-5])
                    amount=re.sub('\s+',"",line[i][st_header[3]-5:])
                else:
                    description+=re.sub("\s+"," ",line[i][:st_header[1]-5])+" | "
        kk+=1
        if(breakpoint==1):
            break
    
    if(res!=[]):
        l1=[]
        l2=[]
        l3=[]
        l4=[]
        cc=0
        for i in res:
            # if(re.search('^\s*manpower.*',i['Description'].lower()) or (i['QuantityValue']==''  and i['Price']=='')):
            #     pass
            if(i['QuantityValue'] == '' and i['Price'] == ''):
                pass
            elif(re.search(r'^\s*analysis\s*of\s*.*',i['Description'].lower())):
                l1.append(i)
            elif(re.search(r'subtotal',i['Description'].lower())and cc==0):
                l2.append(i)
            elif(re.search(r'\s*navarik\s*e.*enablement\s*discount',i['Description'].lower())):
                l3.append(i)
            else:
                l4.append(i)
        final_dict['Quantity']=l4
        final_dict['quality']=l1
        # final_dict['subtotal']=l2
        # final_dict['discount']=l3
        # CHANGES FOR ADDING THE UOM AND EXTRACTIN CAT. AND SUBCAT. FROM DES. IN QTY
        if(final_dict['Quantity'] != []):
            final_list_quant = []
            for i in final_dict['Quantity']:
                temp = {}
                temp['Description'] = i['Description']
                temp['QuantityValue'] = i['QuantityValue']
                temp['Price'] = i['Price']
                temp['UoM'] = ''
                temp['Category'] = ''
                temp['Subcat'] = ''
                temp['Charge']=''
                temp['Share']=''
                temp['ShareCharge']=''
                temp['Tax']=''
                temp['Amount']=re.sub('\s+',"",i['amount'])
                temp['Discount']=''
                if('manpower' in i['Description'].lower()):
                    temp['Category'] = 'Manpower'
                    t = re.sub(r'^\s*(Manpower|manpower|Man-power)',
                               "", i['Description'])
                    tt = (t.split('('))[0]
                    tt = re.sub(r'[-]', " ", tt)
                    temp['Subcat'] = tt
                    if(re.search(r'\s*/Hr\)', t)):
                        temp['UoM'] = 'Per Hr'
                elif(re.search(r'^(\s*[a-z|A-Z|-|/]\s*)+[;]\s*[A-Z|a-z|0-9]', i['Description'])):
                    ttt = re.search(
                        r'^(\s*[a-z|A-Z|-|/]\s*)+[;]', i['Description'])[0]
                    tt = re.sub(r'[;]', "", ttt)
                    temp['Category'] = tt
                    temp['Subcat'] = re.sub(ttt, "", i['Description'])
                    rr = (i['Description'].split('(')[1]).split(')')[0]
                    rr = re.sub(r'.*[0-9]+', "", rr)
                    temp['UoM'] = rr
                elif(re.search(r'\(.*\)', i['Description'])):
                    ss = i['Description']
                    temp['Category'] = ss.split('(')[0]
                    ttt = ss.split(')')
                    ttt = ttt[len(ttt)-1]
                    if(re.search(r'[a-z|A-Z]', ttt)):
                        ttt = re.sub(r'\s+', " ", ttt)
                        ttt = re.sub(r'\s*(on)*\s*[0-9|/]*\s*$', "", ttt)
                        temp['Subcat'] = ttt
                    rr = (ss.split('(')[1]).split(')')[0]
                    rr = re.sub(r'.*[0-9]+', "", rr)
                    temp['UoM'] = rr
                elif(re.search(r'\s+at.*$', i['Description'])):
                    tt = i['Description'].split(" at ")
                    temp['Category'] = tt[0]
                    temp['Subcat'] = tt[1]

                else:
                    temp['Category'] = i['Description']

                
                final_list_quant.append(temp)
                
            final_dict['Quantity'] = final_list_quant
    if(final_dict['quality']!=[]):
        final_qlty_li=[]
        for i in final_dict['quality']:
            final_qlty_li+=inv_qualitylineitem(i['Description'])
        final_dict['quality']=final_qlty_li
 
    return final_dict

def classification_for_invoice(lines):
    res_cgi="NA"
    lp=[0,0,0,0,0]
    for  i in range(len(lines)):
        l=re.sub(r'\s+'," ",lines[i]).lower()
        if(re.search(r'((coastal\s*gulf\s*&\s*international)|(\s*cgi\s*))',l,re.I)):
            lp[0]=1
        elif(re.search(r'((bill\s*to)|(job\s*info.*))',l,re.I)):
            lp[1]=1
        elif(re.search('description',l) and re.search('qty',l) and re.search('amount',l) and re.search('rate',l)):
            lp[2]=1
        elif(re.search(r'we\s*understand\s*that\s*you\s*have\s*a',l,re.I) or re.search(r'choice\s*thanks\s*for\s*choosing',l,re.I)):
            lp[3]=1
        elif(re.search(r'invoice(\s+)*total',l,re.I)):
            lp[4]=1
    if(sum(lp)==5):
        res_cgi='inv'
    return res_cgi
    
def cgi_lineitem_main(inp_path):
    f=open(inp_path,'r')
    lines=f.readlines()
    final_dict={}
    status=0
    try:
        if(classification_for_invoice(lines)=='inv'):
            final_dict=cgi_invoice_lineitem_extraction(lines)
    except:
        pass
    logger.info(f'Line data Invoice -{final_dict}')
    return final_dict



################################### UNCOMMENT BELOW FOR TEST  ##########################

# inp_path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/Extra_data/Inv300686/Inv300686.text"   #provide the path of the text file

# print(cgi_lineitem_main(inp_path))
          

            

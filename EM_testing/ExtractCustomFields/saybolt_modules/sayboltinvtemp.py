import time
import datetime
import os
import sys
import re


def find_header_item_p2(lines):
    st = -1
    l = ['quantity', 'description', 'share', 'unitprice',"amount"]
    st_header = []
    for i in range(len(lines)):
        lines[i] = lines[i].lower()
        if(re.search('quantity', lines[i]) and re.search('description', lines[i]) and re.search(r'share', lines[i]) and re.search('unit[e]*(\s){,3}price', lines[i])  and re.search('amount', lines[i])):
            st = i
            for j in l:
                if(j=='unitprice'):
                    st_header.append(lines[i].find('unit'))
                else:
                    st_header.append(lines[i].find(j))
            break
    return st, st_header

def saybolt_invoice_lineitem_extraction_p2(lines):
    res_quantity=[]
    res_quality=[]
    kk = 0
    breakpoint = 0
    itemno = 1
    final_dict = {}
    type='inspection'
    tyc=0
    nano_checkpoint=0
    while(kk < len(lines)):
        line = lines[kk:]
        st, st_header = find_header_item_p2(line)
        # print(st_header)
        dict_row_data = {}
        description = ''
        qty = ''
        rate = ''
        tax=''
        share=''
        amount=''
        if(st != -1):
            kk += st
            for i in range(st+1, len(line)):
                kk += 1
                if(re.search(r'test\s+description.*\sastm',line[i],re.I)):
                    type='laboratory'
                    tyc+=1

                if(re.search(r'\s+sub\s+total',re.sub(r'\s+'," ",line[i]), re.I)):
                    dict_row_data = {}
                    temp = re.sub("\s+", "", line[i], re.I).lower()
                    description = re.sub(r"(\s*\|\s*)*$", "", description)
                    if(description != '' and (qty != '' or rate != '' or amount != '' or share != '' or tax != '')):
                        dict_row_data['Description'] = description
                        dict_row_data['QuantityValue'] = qty
                        dict_row_data['Price'] = rate
                        dict_row_data['Tax']=tax
                        dict_row_data['Share']=share
                        dict_row_data['Amount']=amount
                        if(type=='inspection'):
                            res_quantity.append(dict_row_data)
                        elif(type=='laboratory'):
                            res_quality.append(dict_row_data)
                    breakpoint = 1
                    break
                elif(re.search(r'All our activities are carried out under our general terms and conditions', line[i], re.I) ):
                    dict_row_data = {}

                    description = re.sub(r"(\s*\|\s*)*$", "", description)
                    if(description != '' and (qty != '' or rate != '' or amount != '' or share != '' or tax != '')):
                        dict_row_data['Description'] = description
                        dict_row_data['QuantityValue'] = qty
                        dict_row_data['Price'] = rate
                        dict_row_data['Tax'] = tax
                        dict_row_data['Share'] = share
                        dict_row_data['Amount'] = amount
                        if(type == 'inspection'):
                            res_quantity.append(dict_row_data)
                        elif(type == 'laboratory'):
                            res_quality.append(dict_row_data)
                        itemno += 1
                    break
               
                elif(re.search(r'^\s*total\s+((inspection)|(ancillary)|(analytical))', re.sub("\s+"," ",line[i]), re.I) ):
                    dict_row_data = {}

                    description = re.sub(r"(\s*\|\s*)*$", "", description)
                    if(description != '' and (qty != '' or rate != '' or amount != '' or share != '' or tax != '')):
                        dict_row_data['Description'] = description
                        dict_row_data['QuantityValue'] = qty
                        dict_row_data['Price'] = rate
                        dict_row_data['Tax'] = tax
                        dict_row_data['Share'] = share
                        dict_row_data['Amount'] = amount
                        if(type == 'inspection'):
                            res_quantity.append(dict_row_data)
                        elif(type == 'laboratory'):
                            res_quality.append(dict_row_data)
                        itemno += 1
                        description = ''
                        qty = ''
                        rate = ''
                        tax=''
                        share=''
                        amount=''
                    pass
               
                
                elif(re.search(r'test\s+description.*\s+astm', re.sub("\s+"," ",line[i]), re.I)):
                    dict_row_data = {}

                    description = re.sub(r"(\s*\|\s*)*$", "", description)
                    if(description != '' and (qty != '' or rate != '' or amount != '' or share != '' or tax != '')):
                        dict_row_data['Description'] = description
                        dict_row_data['QuantityValue'] = qty
                        dict_row_data['Price'] = rate
                        dict_row_data['Tax'] = tax
                        dict_row_data['Share'] = share
                        dict_row_data['Amount'] = amount
                        if(tyc<=1):
                            res_quantity.append(dict_row_data)
                            tyc+=1
                        elif(type == 'laboratory'):
                            res_quality.append(dict_row_data)
                        itemno += 1
                        description = ''
                        qty = ''
                        rate = ''
                        tax=''
                        share=''
                        amount=''
                    else:
                        tyc+=1
                    nano_checkpoint=line[i].find('ASTM')

                    
                elif(re.search(r'[0-9]', line[i][st_header[2]:])):
                    dict_row_data = {}
                    description = re.sub(r"(\s*\|\s*)*$", "", description)
                    if(description != '' and( qty != ''or rate != ''or amount != ''or share != '' or tax != '')):
                        dict_row_data['Description'] = description
                        dict_row_data['QuantityValue'] = qty
                        dict_row_data['Price'] = rate
                        dict_row_data['Tax'] = tax
                        dict_row_data['Share'] = share
                        dict_row_data['Amount'] = amount
                        if(type == 'inspection'):
                            res_quantity.append(dict_row_data)
                        elif(type == 'laboratory'):
                            res_quality.append(dict_row_data)

                    itemno += 1
                    if(type=='inspection'):
                        description = re.sub("\s+", " ", line[i][:st_header[2]-5])
                        if(not re.search('^\s*[0-9]',description)):
                            tempp=description
                            description=re.sub("\s+", " ", line[i-1][:st_header[2]-5])+" "+tempp

                        description=re.sub(r"^\s*[0-9,]+(\.)*[0-9,]*\s*","",description)
                    elif(type=='laboratory'):
                        description = re.sub("\s+", " ", line[i][:nano_checkpoint])
                        if(description==' '):
                            description=re.sub("\s+", " ", line[i-1][:nano_checkpoint])+re.sub("\s+", " ", line[i+1][:nano_checkpoint-3])+"##"+re.sub("\s+", " ", line[i][nano_checkpoint-3:st_header[2]-5])
                        else:
                            description=re.sub(r"^\s*[0-9,]+(\.)*[0-9,]*\s*","",description)
                            description+="##"+re.sub("\s+", " ", line[i][nano_checkpoint-3:st_header[2]-5])

                    # qty = re.sub(
                    #     '\s+', "", line[i][:st_header[1]-2])
                    qty=re.sub("\s+", " ", line[i][:st_header[1]+5])
                    if(re.search(r'^\s*[0-9,]+(\.)*[0-9,]*',qty)):
                        qty=re.search(r'^\s*[0-9,]+(\.)*[0-9,]*',qty)[0]
                    else:
                        qty=''
                        qty=re.sub("\s+", " ", line[i-1][:st_header[1]+5])
                        if(re.search(r'^\s*[0-9,]+(\.)*[0-9,]*',qty)):
                            qty=re.search(r'^\s*[0-9,]+(\.)*[0-9,]*',qty)[0]
                        else:
                            qty=''
                    rate = re.sub(
                        '\s+', "", line[i][st_header[3]:st_header[4]-5])
                    share = re.sub('\s+', "", line[i][st_header[2]-3:st_header[3]-5])
                    amount = re.sub('\s+', "", line[i][st_header[4]-3:])
                else:
                    if(type=='inspection'):
                        # description += re.sub("\s+", " ",
                        #                 line[i][:st_header[2]-5])
                        pass
                    elif(type=='laboratory'):
                        if(not re.search(r'[a-z0-9]',line[i-1][nano_checkpoint:st_header[2]-5]) and not  ""==re.sub('\s+',"",line[i][:nano_checkpoint])):
                            tempi=description
                            description =tempi+" "+re.sub("\s+", " ",
                                        line[i-1][:st_header[2]-5])


                        
        kk += 1
        if(breakpoint == 1):
            break


    # print(res_quantity)
    # print(res_quality)
    final_list_quant = []
    final_list_quality=[]




    # # CHANGES FOR ADDING THE UOM AND EXTRACTIN CAT. AND SUBCAT. FROM DES. IN QTY
    if(res_quantity != []):
        for i in res_quantity:
            temp = {}
            i['Description']=re.sub(r'\''," ",i['Description'])
            if(re.search(r'\s\|\s.*',i['Description'])):
                i['Description'] = re.sub(r'\s\|\s.*',"",i['Description'])
            temp['Description'] =i['Description']
            temp['QuantityValue'] = i['QuantityValue']
            temp['Price'] = ''
            temp['UoM'] = ''
            temp['Category'] = ''
            temp['Subcat'] = ''
            temp['Charge']=''
            temp['Share']=''
            temp['ShareCharge']=''
            temp['Tax']=re.sub("\s+"," ",i['Tax'])
            temp['Amount']=''

            if('('in i['Description'] and')' in i['Description']):
                t=i['Description']
                tt=t.split('(')[0]
                temp['Category']=tt
                tt=t.split(')')
                tt=tt[len(tt)-1]
                tt=re.sub(r'\s+'," ",tt)
                if(tt!=' '):
                    temp['Subcat']=tt
                u=(t.split('(')[1]).split(')')[0]
                u=re.sub('^\s*',"",u)
                u=re.sub(r'\s*$',"",u)
                if(re.search(r'per\s*[>]6 .*',u,re.I)):
                    temp['UoM']=''
                elif(' per ' in u or ' Per ' in u):
                    te=re.sub('.*\sper',"",u)
                    temp['UoM']='per '+re.search('\s*[a-zA-Z]+',te)[0]
                elif(re.search(r'\d+\s+\w+\s*$',u)):
                    uu=re.search(r'\w+\s*$',u)[0]
                    temp['UoM']=uu

            else:
                temp['Category'] = i['Description']
                if(re.search('\s+per\s+',i['Description'],re.I)):
                    temp['UoM']=re.sub('\s+'," ",re.search('per\s+[a-z]+',i['Description'],re.I)[0])
                elif(re.search('@.\s+\d+[\.]*\d*\s+\w+\s*$',re.sub('\s+'," ",i['Description']))):
                    temp['UoM']=re.search('\w+\s*$',re.sub('\s+'," ",i['Description']),re.I)[0]
            try:
                if(i['Share']!=''):
                    if(re.search(r'[0-9]',i['Share'])):
                        temp['Share']=re.search(r'[0-9]+\.*[0-9]*',i['Share'])[0]

            except:
                print('error in share')
            try:
                if(re.search(r'[0-9]',i['Price'])):
                    tt = re.sub(r'[,]', "", i['Price'])
                    temp['Price']=re.search(r'[0-9]+(\.)*[0-9]+',tt)[0]
                if(re.search(r'[0-9]', i['Amount'])):
                    tt = re.sub(r'[,]', "", i['Amount'])
                    temp['Amount'] = re.search(r'[0-9]+(\.)*[0-9]+',tt)[0]
            except :
                print('error in costs cleaning')

            # print(temp)
            final_list_quant.append(temp)
            # print(final_list_quant)
    if(res_quality!=[]):
        for i in res_quality:
            temp = {}
            i['Description']=re.sub(r'\''," ",i['Description'])
            temp['Description'] = i['Description']
            temp['QuantityValue'] = i['QuantityValue']
            temp['Price'] = ''
            temp['UoM'] = 'Per test'
            temp['Charge']=''
            temp['Share']=''
            temp['ShareCharge']=''
            temp['TestName']=''
            temp['TestMethod']=''
            temp['Tax']=re.sub('\s+'," ",i['Tax'])
            temp['Amount']=''
            if(i['Description']!='' and "##" in i['Description']):
                if(re.search('^\s+##',i['Description'])):
                    print(i['Description'])
                    tempt=i['Description']
                    tempt=re.sub('(\s){3,}',"  ",re.sub('^\s+##',"",tempt)).split("  ")
                    print(tempt)
                    temp['TestMethod']=re.sub("\s+","",tempt[1])
                    temp['TestName']=re.sub('\s+'," ",tempt[0])
                else:

                    tl=i['Description'].split("##")
                    temp['TestMethod']=re.sub("\s+","",tl[1])
                    temp['TestName']=re.sub('\s+'," ",tl[0])
            try:
                if(re.search(r'[0-9]', i['Price'])):
                    tt = re.sub(r'[,]', "", i['Price'])
                    temp['Price'] = re.search(
                        r'[0-9]+(\.)*[0-9]+', tt)[0]
                if(re.search(r'[0-9]', i['Amount'])):
                    tt = re.sub(r'[,]', "", i['Amount'])
                    temp['Amount'] = re.search(r'[0-9]+(\.)*[0-9]+',tt)[0]
            except:
                print('error in costs cleaning')
            try:
                if(i['Share'] != ''):
                    if(re.search(r'[0-9]', i['Share'])):
                        temp['Share']=re.search(r'[0-9]+\.*[0-9]*',i['Share'])[0]

            except:
                print('error in share')
            final_list_quality.append(temp)



    # print(final_list_quant)
    # print(final_list_quality)
    final_dict['Quantity']=final_list_quant
    final_dict['quality']=final_list_quality

    return final_dict



def saybolt_lineitem_main(inp_path):
    f = open(inp_path, 'r')
    lines = f.readlines()
    final_dict = {}
    status = 0
    # try:
        
    final_dict = saybolt_invoice_lineitem_extraction_p2(lines)
    # except:
    #     pass
    return final_dict


################################### UNCOMMENT BELOW FOR TEST  ##########################

# provide the path of the text file
# inp_path=r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/CHEM-US/1300396439/1300396439.text'
# inp_path = r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/CHEM-US/1300395101/1300395101.text'
inp_path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/INT/88806130221/Invoice.text"
p=(saybolt_lineitem_main(inp_path))
for i in p:
    print(i,'*'*50,"\n")
    for j in p[i]:
        print(j,"\n")


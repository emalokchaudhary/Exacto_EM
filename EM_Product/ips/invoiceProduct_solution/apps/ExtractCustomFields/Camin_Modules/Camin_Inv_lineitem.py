import time
import datetime
import os
import sys
import re
from ExtractCustomFields.EM_logging import logger

def find_header_item(lines):
    st = -1
    l = ['description', 'units', '/unit', 'charge',"share","share charge"]
    st_header = []
    for i in range(len(lines)):
        lines[i] = lines[i].lower()
        if(re.search('description', lines[i]) and re.search('units', lines[i]) and re.search(r'.[/]unit', lines[i]) and re.search('charge', lines[i]) and re.search('share', lines[i]) and re.search('share\s+charge', lines[i])):
            st = i
            for j in l:
                st_header.append(lines[i].find(j))
            break
    return st, st_header


def ancillary_lineitem(lines):
    anscc=[]
    st_header=[]
    kk = 0
    st=-1
    starting=0
    breakpoint = 0
    itemno = 1
    for i in range(len(lines)):
        if(re.search(r'ancillary\s+services', lines[i], re.I)):
            kk=i
            t,st_header = find_header_item(lines[0:kk])
            st=0
            break
   

    while(kk < len(lines)):
        line = lines[kk:]
        if(starting!=0):
            st,st_header = find_header_item(line[0:kk])
        dict_row_data = {}
        description = ''
        qty = ''
        rate = ''
        charge = ''
        share = ''
        sharecharge = ''
        if(st != -1):
            kk += st
            for i in range(st+1, len(line)):
                # print(line[i])
                
                kk += 1

                if(re.search(r'^\s*notes:', line[i], re.I) or re.search(r'camin cargo control, inc.', line[i], re.I) or re.search(r'contractual rates applied.', line[i+2], re.I)or re.search(r'navarik.*discount',line[i],re.I) or (re.sub("\s+","",line[i])=="")):
                    dict_row_data = {}
                    description = re.sub(r"(\s*\|\s*)*$", "", description)
                    if(description != '' and (qty != '' or rate != '' or sharecharge != '' or share != '' or charge != '')):
                        dict_row_data['Description'] = description
                        dict_row_data['QuantityValue'] = qty
                        dict_row_data['Price'] = rate
                        dict_row_data['Charge'] = charge
                        dict_row_data['Share'] = share
                        dict_row_data['ShareCharge'] = sharecharge
                        anscc.append(dict_row_data)
                        itemno += 1
                    breakpoint=1
                    break


                elif(re.search(r'[0-9]', line[i][st_header[1]-5:])):

                    dict_row_data = {}
                    description = re.sub(r"(\s*\|\s*)*$", "", description)
                    if(description != '' and (qty != '' or rate != '' or sharecharge != '' or share != '' or charge != '')):
                        dict_row_data['Description'] = description
                        dict_row_data['QuantityValue'] = qty
                        dict_row_data['Price'] = rate
                        dict_row_data['Charge'] = charge
                        dict_row_data['Share'] = share
                        dict_row_data['ShareCharge'] = sharecharge
                        anscc.append(dict_row_data)

                    itemno += 1
                    description = re.sub("\s+", " ", line[i][:st_header[1]-7])
                    qty = re.sub(
                        '\s+', "", line[i][st_header[1]-5:st_header[1]+15])
                    rate = re.sub(
                        '\s+', "", line[i][st_header[2]-10:st_header[3]-15])
                    charge = re.sub(
                        '\s+', "", line[i][st_header[3]-5:st_header[4]-2])
                    share = re.sub(
                        '\s+', "", line[i][st_header[4]-3:st_header[5]-7])
                    sharecharge = re.sub('\s+', "", line[i][st_header[5]-5:])
                else:
                    description += re.sub("\s+", " ",
                                          line[i][:st_header[1]-5])+" | "
        kk += 1
        starting+=1
        if(breakpoint == 1):
            break
    final_anscc=[]
    if(anscc != []):
        for i in anscc:
            temp = {}
            if(re.search(r'\s\|\s.*', i['Description'])):
                i['Description'] = re.sub(r'\s\|\s.*', "", i['Description'])
            temp['Description'] = i['Description']
            temp['QuantityValue'] = i['QuantityValue']
            temp['Price'] = ''
            temp['UoM'] = ''
            temp['Category'] = ''
            temp['Subcat'] = ''
            temp['Charge'] = ''
            temp['Share'] = ''
            temp['ShareCharge'] = ''
            temp['Tax']=''
            temp['Amount']=''
            temp['Discount']=''
            if('(' in i['Description'] and ')' in i['Description']):
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
                if(re.search(r'per.*',u,re.I)):
                    temp['UoM']=re.search(r'per\s*[a-z]+',u,re.I)[0]

            try:
                if(i['Share'] != ''):
                    if(re.search(r'[0-9]', i['Share'])):
                        ss=re.search(r'[0-9][/]*[0-9]*',i['Share'])[0]
                        if('/' in ss):
                            t = ss.split('/')
                            te = (
                                int(re.sub(r'\s*', "", t[0]))/int(re.sub(r'\s*', "", t[1])))*100
                            temp['Share'] = str(te)
                        else:
                            t = float(int(re.sub(r'\s*', "", ss))*100)
                            temp['Share'] = str(t)
            except:
                print('error in share')
            try:
                if(re.search(r'[0-9]', i['Price'])):
                    tt=re.sub(r'[,]',"",i['Price'])
                    temp['Price'] = re.search(r'[0-9]+(\.)*[0-9]+', tt)[0]
                if(re.search(r'[0-9]', i['Charge'])):
                    tt = re.sub(r'[,]', "", i['Charge'])
                    temp['Charge'] = re.search(
                        r'[0-9]+(\.)*[0-9]+', tt)[0]
                if(re.search(r'[0-9]', i['ShareCharge'])):
                    tt = re.sub(r'[,]', "", i['ShareCharge'])
                    temp['ShareCharge'] = re.search(
                        r'[0-9]+(\.)*[0-9]+',tt)[0]
            except:
                print('error in costs cleaning')
            final_anscc.append(temp)
    return final_anscc

def camin_invoice_lineitem_extraction(lines):
    res_quantity=[]
    res_quality=[]
    kk = 0
    breakpoint = 0
    itemno = 1
    final_dict = {}
    type=''
    while(kk < len(lines)):
        line = lines[kk:]
        st, st_header = find_header_item(line)
        # print(st_header)
        dict_row_data = {}
        description = ''
        qty = ''
        rate = ''
        charge=''
        share=''
        sharecharge=''
        if(st != -1):
            kk += st
            for i in range(st+1, len(line)):
                kk += 1
                if(re.search(r'inspection\s*services\s*',line[i],re.I)):
                    type='inspection'
                elif(re.search(r'laboratory\s*services\s*',line[i],re.I)):
                    type='laboratory'

                if(re.search(r'ancillary\s+services', line[i], re.I)):
                    dict_row_data = {}
                    temp = re.sub("\s+", "", line[i], re.I).lower()
                    description = re.sub(r"(\s*\|\s*)*$", "", description)
                    if(description != '' and (qty != '' or rate != '' or sharecharge != '' or share != '' or charge != '')):
                        dict_row_data['Description'] = description
                        dict_row_data['QuantityValue'] = qty
                        dict_row_data['Price'] = rate
                        dict_row_data['Charge']=charge
                        dict_row_data['Share']=share
                        dict_row_data['ShareCharge']=sharecharge
                        if(type=='inspection'):
                            res_quantity.append(dict_row_data)
                        elif(type=='laboratory'):
                            res_quality.append(dict_row_data)
                    breakpoint = 1
                    break
                elif(re.search(r'^\s*notes:', line[i], re.I) or re.search(r'camin cargo control, inc.', line[i], re.I) or re.search(r'contractual rates applied.', line[i+2], re.I)):
                    dict_row_data = {}

                    description = re.sub(r"(\s*\|\s*)*$", "", description)
                    if(description != '' and (qty != '' or rate != '' or sharecharge != '' or share != '' or charge != '')):
                        dict_row_data['Description'] = description
                        dict_row_data['QuantityValue'] = qty
                        dict_row_data['Price'] = rate
                        dict_row_data['Charge'] = charge
                        dict_row_data['Share'] = share
                        dict_row_data['ShareCharge'] = sharecharge
                        if(type == 'inspection'):
                            res_quantity.append(dict_row_data)
                        elif(type == 'laboratory'):
                            res_quality.append(dict_row_data)
                        itemno += 1
                    break
                elif(re.search(r'((inspection\s*services\s*[:]*)|(laboratory\s*services\s*[:]*))', line[i], re.I)):
                    dict_row_data = {}
                    description = re.sub(r"(\s*\|\s*)*$", "", description)
                    if(description != '' and (qty != '' or rate != '' or sharecharge != '' or share != '' or charge != '')):
                        dict_row_data['Description'] = description
                        dict_row_data['QuantityValue'] = qty
                        dict_row_data['Price'] = rate
                        dict_row_data['Charge'] = charge
                        dict_row_data['Share'] = share
                        dict_row_data['ShareCharge'] = sharecharge
                        if(type == 'inspection'):
                            res_quantity.append(dict_row_data)
                        elif(type == 'laboratory'):
                            res_quality.append(dict_row_data)
                        description = ''
                        qty = ''
                        rate = ''
                        charge = ''
                        share = ''
                        sharecharge = ''
                        
                elif(re.search(r'[0-9]', line[i][st_header[1]-5:])):
                    dict_row_data = {}
                    description = re.sub(r"(\s*\|\s*)*$", "", description)
                    if(description != '' and( qty != ''or rate != ''or sharecharge != ''or share != '' or charge != '')):
                        dict_row_data['Description'] = description
                        dict_row_data['QuantityValue'] = qty
                        dict_row_data['Price'] = rate
                        dict_row_data['Charge'] = charge
                        dict_row_data['Share'] = share
                        dict_row_data['ShareCharge'] = sharecharge
                        if(type == 'inspection'):
                            res_quantity.append(dict_row_data)
                        elif(type == 'laboratory'):
                            res_quality.append(dict_row_data)

                    itemno += 1
                    description = re.sub("\s+", " ", line[i][:st_header[1]-7])
                    qty = re.sub(
                        '\s+', "", line[i][st_header[1]-5:st_header[1]+15])
                    rate = re.sub(
                        '\s+', "", line[i][st_header[2]-10:st_header[3]-15])
                    charge = re.sub('\s+', "", line[i][st_header[3]-5:st_header[4]-2])
                    share = re.sub('\s+', "", line[i][st_header[4]-3:st_header[5]-7])
                    sharecharge = re.sub('\s+', "", line[i][st_header[5]-5:])
                else:
                    description += re.sub("\s+", " ",
                                          line[i][:st_header[1]-5])+" | "
        kk += 1
        if(breakpoint == 1):
            break
    # print(res_quantity)
    # print(res_quality)
    final_list_quant = []
    final_list_quality=[]




    # CHANGES FOR ADDING THE UOM AND EXTRACTIN CAT. AND SUBCAT. FROM DES. IN QTY
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
            temp['Tax']=''
            temp['Amount']=''
            temp['Discount']=''

            if('manpower' in i['Description'].lower()):
                temp['Category'] = 'Manpower'
                t = re.sub(r'^\s*(Manpower|manpower|Man-power)',
                            "", i['Description'])
                tt = (t.split('-'))[0]
                # tt = re.sub(r'[-]', " ", tt)
                if(len(tt)>=3):
                    temp['Subcat'] = tt[2]
                if(re.search(r'\s*/Hr\)', t)):
                    temp['UoM'] = 'Per Hr'
            elif((re.search(r'[0-9]',i['Price']))==None and not(i['Price']=='')):
                t=i['Description']
                t=t.split('-')
                if(len(t)>=2):
                    temp['Category']=t[1]
                temp['Subcat']=i['Price']
                temp['Price']=''
                if('(' in i['Description'] and ')' in i['Description']):
                    u=i['Description']
                    temp['Category']=u.split('(')[0]
                    u=(u.split('(')[1]).split(')')[0]
                    if(re.search(r'per|[/]',u,re.I)):
                        u=re.sub(r'^\s*',"",u)
                        u=re.sub(r'\s*$',"",u)
                        if(re.search(r'per\s*[>]6 .*', u, re.I)):
                            temp['UoM'] = ''
                        else:
                            temp['UoM']=u
          
            elif('('in i['Description'] and')' in i['Description']):
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
                else:
                    temp['UoM']=u
            elif(len(re.findall(r'[-]',i['Description']))>=2):
                u=(i['Description']).split('-')
                if(len(u)>=3):
                    temp['Subcat']=re.sub(r'\s+|[-]'," ",(u[len(u)-1]))
                    temp['Category']=re.sub(u[len(u)-1],"",i['Description'])
                else:
                    temp['Category'] = i['Description']

            else:
                temp['Category'] = i['Description']
            try:
                if(i['Share']!=''):
                    if(re.search(r'[0-9]',i['Share'])):
                        if('/' in i['Share'] ):
                            t=i['Share'].split('/')
                            te=(int(re.sub(r'\s*',"",t[0]))/int(re.sub(r'\s*',"",t[1])))*100
                            temp['Share']=str(te)
                        else:
                            t=float(int(re.sub(r'\s*',"",i['Share']))*100)
                            temp['Share']=str(t)
            except:
                print('error in share')
            try:
                if(re.search(r'[0-9]',i['Price'])):
                    tt = re.sub(r'[,]', "", i['Price'])
                    temp['Price']=re.search(r'[0-9]+(\.)*[0-9]+',tt)[0]
                if(re.search(r'[0-9]', i['Charge'])):
                    tt = re.sub(r'[,]', "", i['Charge'])
                    temp['Charge'] = re.search(r'[0-9]+(\.)*[0-9]+', tt)[0]
                if(re.search(r'[0-9]', i['ShareCharge'])):
                    tt = re.sub(r'[,]', "", i['ShareCharge'])
                    temp['ShareCharge'] = re.search(r'[0-9]+(\.)*[0-9]+',tt)[0]
            except:
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
            temp['Tax']=''
            temp['Amount']=''
            temp['Discount']=''
            if('(' in i['Description']):
                t=i['Description']
                tt=t.split('(')
                temp['TestName']=tt[0]
                tl=(tt[1].split(')'))[0]
                temp['TestMethod']=tl
            try:
                if(re.search(r'[0-9]', i['Price'])):
                    tt = re.sub(r'[,]', "", i['Price'])
                    temp['Price'] = re.search(
                        r'[0-9]+(\.)*[0-9]+', tt)[0]
                if(re.search(r'[0-9]', i['Charge'])):
                    tt = re.sub(r'[,]', "", i['Charge'])
                    temp['Charge'] = re.search(
                        r'[0-9]+(\.)*[0-9]+', tt)[0]
                if(re.search(r'[0-9]', i['ShareCharge'])):
                    tt = re.sub(r'[,]', "", i['ShareCharge'])
                    temp['ShareCharge'] = re.search(
                        r'[0-9]+(\.)*[0-9]+', tt)[0]
            except:
                print('error in costs cleaning')
            try:
                if(i['Share'] != ''):
                    if(re.search(r'[0-9]', i['Share'])):
                        if('/' in i['Share']):
                            t = i['Share'].split('/')
                            te = (
                                int(re.sub(r'\s*', "", t[0]))/int(re.sub(r'\s*', "", t[1])))*100
                            temp['Share'] = str(te)
                        else:
                            t = float(int(re.sub(r'\s*', "", i['Share']))*100)
                            temp['Share'] = str(t)
            except:
                print('error in share')
            final_list_quality.append(temp)
    anccc_list = []
    try:
        anccc_list = ancillary_lineitem(lines)
        # print(anccc_list, "*********************")
    except:
        print('error in ancillary')
    final_list_quant+=anccc_list

    # print(final_list_quant)
    # print(final_list_quality)
    final_dict['Quantity']=final_list_quant
    final_dict['quality']=final_list_quality

    return final_dict



def camin_lineitem_main(inp_path):
    f = open(inp_path, 'r')
    lines = f.readlines()
    final_dict = {}
    status = 0
    # try:
        
    final_dict = camin_invoice_lineitem_extraction(lines)
    # except:
    #     pass
    logger.info(f'Camin line data Invoice - {final_dict}')
    
    return final_dict


################################### UNCOMMENT BELOW FOR TEST  ##########################

# provide the path of the text file
# inp_path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/Invoice115407501-25-2021.text"
# inp_path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/Invoice113875410-29-2020.text"
# inp_path = r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Camin/INT/1136684/1136684.text'
# print(camin_lineitem_main(inp_path))

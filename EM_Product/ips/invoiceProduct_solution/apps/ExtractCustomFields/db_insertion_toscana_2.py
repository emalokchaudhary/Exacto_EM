import re
import pyodbc
import uuid
import datefinder
from variable import *
from datetime import datetime
from db_connection import connect_db
from CGI_Invoice_headers import *
from CGI_Invoice_lineitems import *


def inv_qualitylineitem(des):
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
        f['TestName']=TestName
        f['TestMetod']=TestMethod
        f['QuantityValue']=QuantityValue
        f['UnitPrice']=UnitPrice
        final_list.append(f)        
        
    return final_list
def inv_header_dict_formatting(inv_header):

    if(inv_header['JobDate']!=""):
        temp=datefinder.find_dates(inv_header['JobDate'])
        d=''
        for match in temp:
            d=match
        d=d.date()
        inv_header['JobDate']=d
    try:
        if(inv_header['VendorInternalReferencenumber']!=""):
            inv_header['VendorInternalReferencenumber'] = int(re.sub(r'\s+', "", inv_header['VendorInternalReferencenumber']))
    except:
        pass
    try:
        if(inv_header['TotalAmount']!=""):
            inv_header['TotalAmount'] = float(re.sub(r'\s+|[,]', "", inv_header['TotalAmount']))
    except:
        pass
    try:
        if(inv_header['DiscountPercent']!=""):
            inv_header['DiscountPercent'] = int(re.sub(r'\s+|[%,-]', "", inv_header['DiscountPercent']))
    except:
        pass
    try:
        if(inv_header['TotalTaxAmount']!=""):
            inv_header['TotalTaxAmount'] = float(re.sub(r'\s+|[,]', "", inv_header['TotalTaxAmount']))
    except:
        pass
    try:
        if(inv_header['TotalAmountAfterTax']!=''):
            inv_header['TotalAmountAfterTax'] = float(re.sub(r'\s+|[,]', "", inv_header['TotalAmountAfterTax']))
    except:
        pass
    try:
        if(inv_header['TotalDueAmount']!=''):
            inv_header['TotalDueAmount'] = float(re.sub(r'\s+|[,]', "", inv_header['TotalDueAmount']))
    except:
        pass
    return inv_header
def dict_formatting_lineitem_inv(inv_qnt,inv_qlty):
    inv_qnt_final=[]
    inv_qlty_final=[]
    for j in inv_qnt:
        j['QuantityValue'] = re.sub(r'\s+', "", j['QuantityValue'])
        j['Price'] = re.sub(r'\s+', "", j['Price'])
        if(j['QuantityValue'] != ""):
            j['QuantityValue'] = float(re.sub(r'\s+|[,]', "", j['QuantityValue']))
        if(j['Price']!=""):
            j['Price'] = float(re.sub(r'\s+|[,]', "", j['Price']))
        ddd={}
        ddd['Description'] = j['Description']
        ddd['QuantityValue'] = j['QuantityValue']
        ddd['UnitPrice']=j['Price']
        inv_qnt_final.append(ddd)
    for k in inv_qlty:
        try:
            inv_qlty_final+=inv_qualitylineitem(k['Description'])
        except:
            pass
    return inv_qnt_final,inv_qlty_final

        
def toscana_inv_insertion(final_inv_header_dict,final_inv_qnt,final_inv_qlty):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        table_name='InvoiceHeader_External'
        list_of_col_heading=['LobId']
        list_of_values=[45]
        
        try:
            list_of_values.append(final_inv_header_dict.get('InvoiceNumber',""))
            list_of_col_heading.append('InvoiceNumber')
        except:
            print('error in InvoiceNumber')
        try:
            list_of_values.append(value_createdby)
            list_of_col_heading.append('CreatedBy')
        except:
            print('error in Created By')
        try:
            NominationDeatilID=''
            try:
                nomid=''
                NominationDeatilID=''
                trpno=(re.sub(r'^\s+',"",final_inv_header_dict['TripNumber'])).upper()
                trpno=re.sub(r'\s+$',"",trpno)
                temp1=f"SELECT RowId from NominationHeaderExternal WHERE TripNumber = {final_inv_header_dict['TripNumber']}"
                cursor.execute(temp1)
                row=cursor.fetchone()
                if row:
                    nomid=row[0]
                    print('nomination id found')
                else:
                    print('no match in nominationid')
                if(nomid):
                    vendor = (re.sub(r"^\s+","",{final_inv_header_dict['VendorName']})).upper()
                    vendor=re.sub(r'\s+$',"",vendor)
                    jobdate = final_inv_header_dict.get('JobDate', "")
                    activity=re.sub(r'\s+$',"",(re.sub(r'^\s+',"",final_inv_header_dict['ActivityType']).upper()))
                    location = re.sub(r'\s+$', "", (re.sub(r'^\s+', "", final_inv_header_dict['JobLocation']).upper()))
            
                    temp2=f"SELECT RowId from NominationDetails_External WHERE Vendor = {vendor}  OR UPPER(Activity) = {activity} OR UPPER(Location) = {location} OR JobDate = {jobdate}"
                    cursor.execute(temp1)
                    row1=cursor.fetchone()
                    if row1:
                        NominationDeatilID=row1[0]
                        print('Nominationdetail id found')
                    else:
                        print('hhh no match')
            except:
                print('error in fetching foreign key')

            list_of_values.append(NominationDeatilID)
            list_of_col_heading.append('NominationDetailId')
        except:
            print('error in NominationDeatilID')
        try:
            list_of_values.append(final_inv_header_dict.get('VendorName',""))
            list_of_col_heading.append('Vendor')
        except:
            print('error in Vendor')
        try:
            list_of_values.append(final_inv_header_dict.get('ActivityType',""))
            list_of_col_heading.append('Activity')
        except:
            print('error in Activity')
        try:
            list_of_values.append(final_inv_header_dict.get('JobLocation',""))
            list_of_col_heading.append('Location')
        except:
            print('error in Location')

        try:
            list_of_values.append(final_inv_header_dict.get('JobDate',""))
            list_of_col_heading.append('JobDate')  
        except:
            print('error in JobDate')
        try:
            list_of_values.append(final_inv_header_dict.get('VendorInternalReferencenumber',""))
            list_of_col_heading.append('VendorReferenceNumber')
        except:
            print('error in VendorReferenceNumber')
        try:
            list_of_values.append(final_inv_header_dict.get('EmAffiliates',""))
            list_of_col_heading.append('BillTo')
        except:
            print('error in BillTo')
        try:
            list_of_values.append(final_inv_header_dict.get('Currency',""))
            list_of_col_heading.append('Currency')
        except:
            print('error in Currency')
        try:
            list_of_values.append(final_inv_header_dict.get('DiscountPercent',""))
            list_of_col_heading.append('DiscountPercent')
        except:
            print('error in DiscountPercent')
        try:
            list_of_values.append(final_inv_header_dict.get('TotalTaxAmount',""))
            list_of_col_heading.append('TotalTaxAmount')
        except:
            print('error in TotalTaxAmount')
        try:
            list_of_values.append(final_inv_header_dict.get('TotalAmountAfterTax',""))
            list_of_col_heading.append('TotalAmountAfterTax')
        except:
            print('error in TotalAmountAfterTax')
        try:
            list_of_values.append(final_inv_header_dict.get('TotalDueAmount',""))
            list_of_col_heading.append('TotalDueAmount')
        except:
            print('error in TotalDueAmount')
        try:
            list_of_values.append(53)
            list_of_col_heading.append('StatusId')
        except:
            print('error in status')
        try:
            currdt=datetime.now()
            list_of_values.append(currdt)
            list_of_col_heading.append('CreatedDate')
        except:
            print('error in createdDate')

        ############ QUERY EXE FOR INVOICE HEADER #######
        try:

            insert_query=f'INSERT INTO {table_name} ({", ".join(list_of_col_heading)}) VALUES {tuple(list_of_values)}'
            # cursor.execute(insert_query)
            # cursor.commit()
            print(insert_query)
        except:
            print("1.ERROR OCCURED DURING INSERTION OF INVOICE HEADERS :(")
    except:
        print('ERROR IN INSERTION OF INV HEADER')
def inv_qunatity_toscana_insertion(final_inv_header_dict,final_inv_qnt):
    try:
        InvoiceNumber=1
        try:
            temp1=f"SELECT RowId from InvoiceHeaderExternal WHERE InvoiceNumber = {final_inv_header_dict['InvoiceNumber']}"
            cursor.execute(temp1)
            row=cursor.fetchone()
            if row:
                InvoiceNumber=row[0]
                print('nomination id found')
            else:
                print('no match in nominationid')
        except:
            pass


        table_name1='InvoiceQuantity_External'
        for i in final_inv_qnt:
            list_of_li_qnt_hd=[]
            list_of_li_qnt_val=[]
            try:
                list_of_li_qnt_val.append(InvoiceId)#hardcode
                list_of_li_qnt_hd.append('InvoiceId')
            except:
                print('error 1')
            try:
                list_of_li_qnt_val.append(1)#hardcode
                list_of_li_qnt_hd.append('NominationDetailId')
            except:
                print('error in NominationDeatilID')
            try:
                list_of_li_qnt_val.append(final_inv_header_dict.get('VesselName'))
                list_of_li_qnt_hd.append('VesselName')
            except:
                print('err3')
            try:
                list_of_li_qnt_val.append(final_inv_header_dict.get('ProductName'))
                list_of_li_qnt_hd.append('ProductName')
            except:
                print('err 4')
            try:
                list_of_li_qnt_val.append(final_inv_header_dict.get('NominationKey'))
                list_of_li_qnt_hd.append('NominationKey')
            except:
                print('err 5')

            try:
                list_of_li_qnt_val.append(final_inv_header_dict.get('UnitOfMeasure'))
                list_of_li_qnt_hd.append('UoM')
            except:
                print('err 6')
            try:
                list_of_li_qnt_val.append(final_inv_header_dict.get('DiscountPercent',""))
                list_of_li_qnt_hd.append('DiscountPercent')
            except:
                print('error in DiscountPercent')
            try:
                list_of_li_qnt_val.append(final_inv_header_dict.get('AmountBeforeTax',''))
                list_of_li_qnt_hd.append('AmountBeforeTax')
            except:
                print('error in amountbeforetax')
            try:
                list_of_li_qnt_val.append(value_createdby)
                list_of_li_qnt_hd.append('CreatedBy')
            except:
                print('error in created By')
            try:
                currdt=datetime.now()
                list_of_li_qnt_val.append(currdt)
                list_of_li_qnt_hd.append('CreatedDate')
            except:
                print('error in createdDate')
            try:
                for j in i:
                    list_of_li_qnt_val.append(i[j])

                    list_of_li_qnt_hd.append(j)

            except:
                print('error in 2323232####')
            try:

                insert_query=f'INSERT INTO {table_name1} ({", ".join(list_of_li_qnt_hd)}) VALUES {tuple(list_of_li_qnt_val)}'
                # cursor.execute(insert_query)
                # cursor.commit()
                print(insert_query)
            except:
                print("1.ERROR OCCURED DURING INSERTION OF INVOICE qunatity insertion :(")
            


    except:
        print('Error occoured in invoice quantity ')

            
    
def  inv_qlty_db_insertion_toscana(final_inv_header_dict,final_inv_qlty):

    InvoiceNumber=1
    NominationQualityID=0
    try:
        temp1=f"SELECT RowId from InvoiceHeaderExternal WHERE InvoiceNumber = {final_inv_header_dict['InvoiceNumber']}"
        cursor.execute(temp1)
        row=cursor.fetchone()
        if row:
            InvoiceNumber=row[0]
            print('nomination id found')
        else:
            print('no match in nominationid')
    except:
        pass
    try:
        temp1=f'SELECT NominationDetailId from InvoiceHeaderExternal WHERE  '###

    table_name='InvoiceQuality_External'
    for i in final_inv_qlty:
        list_of_qlty_val=[]
        list_of_qlty_hd=[]
        try:
            list_of_qlty_val.append(InvoiceNumber)#hardcode
            list_of_qlty_hd.append('InvoiceId')
        except:
            print('error in InvoiceId qlty')
        try:
            list_of_qlty_val.append(NominationQualityID)# hardcode
            list_of_qlty_hd.append('NominationQualityID')
        except:
            print('error in Nomqltyid')
        try:
            list_of_qlty_val.append(final_inv_header_dict.get('VesselName'))
            list_of_qlty_hd.append('VesselName')
        except:
            print('err3')
        try:
            list_of_qlty_val.append(final_inv_header_dict.get('ProductName'))
            list_of_qlty_hd.append('ProductName')
        except:
            print('err 4')
        try:
            list_of_qlty_val.append(final_inv_header_dict.get('NominationKey'))
            list_of_qlty_hd.append('NominationKey')
        except:
            print('err 5')
        try:
            list_of_qlty_val.append(final_inv_header_dict.get('UnitOfMeasure'))
            list_of_qlty_hd.append('UoM')
        except:
            list_of_qlty_val.append(final_inv_header_dict.get('UnitOfMeasure'))
            list_of_qlty_hd.append('')
            print('err 6')
        try:
            list_of_qlty_val.append(final_inv_header_dict.get('DiscountPercent',""))
            list_of_qlty_hd.append('DiscountPercent')
        except:
            print('error in DiscountPercent')
        try:
            list_of_qlty_val.append(final_inv_header_dict.get('AmountBeforeTax',''))
            list_of_qlty_hd.append('AmountBeforeTax')
        except:
            print('error in amountbeforetax')
        try:
            list_of_qlty_val.append(value_createdby)
            list_of_qlty_hd.append('CreatedBy')
        except:
            print('error in created By')
        try:
            currdt=datetime.now()
            list_of_qlty_val.append(currdt)
            list_of_qlty_hd.append('CreatedDate')
        except:
            print('error in createdDate')
        try:
            for j in  i:
                list_of_qlty_val.append(i[j])
                list_of_qlty_hd.append(j)
        except:
            print('error in qlty dict ins')

        try:

            insert_query=f'INSERT INTO {table_name} ({", ".join(list_of_qlty_hd)}) VALUES {tuple(list_of_qlty_val)}'
            # cursor.execute(insert_query)
            # cursor.commit()
            print(insert_query)
        except:
            print("1.ERROR OCCURED DURING INSERTION OF INVOICE quality insertion :(")

def db_main_toscana(inp_path):
    final_dict_hd=(cgi_invoice_headers_extraction(read_textfile(inp_path),'1'))
    final_dict_hd=inv_header_dict_formatting(final_dict_hd)
    temp_di=cgi_lineitem_main(inp_path)
    final_list_qnt=temp_di['Quantity']
    final_list_qlty=temp_di['quality']
    final_list_qnt,final_list_qlty=dict_formatting_lineitem_inv(final_list_qnt,final_list_qlty)
    # print(final_list_qnt,final_list_qlty)
    toscana_inv_insertion(final_dict_hd,final_list_qnt,final_list_qlty)
    inv_qunatity_toscana_insertion(final_dict_hd,final_list_qnt)
    inv_qlty_db_insertion_toscana(final_dict_hd,final_list_qlty)


inp_path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/Extra_data/Inv_302512/Inv_302512.text"
db_main_toscana(inp_path)


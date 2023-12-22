import re
import pyodbc
import uuid
import datefinder
import traceback
from ExtractCustomFields.variable import *
import datetime
from datetime import datetime

from ExtractCustomFields.db_connection import connect_db
# from CGI_Invoice_headers import *
# from CGI_Invoice_lineitems import *
# from CGI_qlty_lineitem import *
# from CGI_Quality_headers import *
# from CGI_Quantity_headers import *


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
        f['TestMethod']=TestMethod
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
        d=d.date().strftime('%Y-%m-%d')
        inv_header['JobDate']=str(d)
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
        if(inv_header['AmountBeforeTax']!=''):
            inv_header['AmountBeforeTax'] = float(re.sub(r'\s+|[,]', "", inv_header['AmountBeforeTax']))
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

######################################### TOSCANA HEADER INSERTION ########################################

        
def toscana_inv_insertion(final_inv_header_dict,final_inv_qnt,final_inv_qlty,global_nom_parcel):
    conn = connect_db()
    cursor = conn.cursor()
    table_name='InvoiceHeader_External'
    list_of_col_heading=['LobId','currQueue','LockByUserName','LockedBy']
    list_of_values=[45,'Ready to Validate','-',0]
    # try:
    #     list_of_values.append(global_nom_parcel['TypeofInspection'])
        
    #     list_of_col_heading.append('Inspection')
    # except:
    #     print("ttttttttttttttttttttttttttttttttttt",global_nom_parcel)
    #     print("Inspection Not found")
    try:
        winumber=''
        temp1="select	(SELECT CodePrefix  FROM TOSCANA3_LobMaster WHERE LobID=45) + substring('00000000', 1, 8 - len(NEXT VALUE FOR seq_ExxonMobil))+ convert(varchar, NEXT VALUE FOR seq_ExxonMobil)"
        print(temp1,"########")
        cursor.execute(temp1)
        row=cursor.fetchone()
        print(row,"#########")
        if row:
            winumber=row[0]
            print('winumber found')
        else:
            print('no match in winumbwerid')
        if(winumber!=''):
            list_of_values.append(str(winumber))
            list_of_col_heading.append('WINumber')
        else:
            list_of_values.append('NULL')
            list_of_col_heading.append('WINumber')

    except:
        list_of_values.append('NULL')
        list_of_col_heading.append('WINumber')
        print('error in Wi number')


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
    nomid=''
    NominationDeatilID=''
    trpno=(re.sub(r'^\s+',"",final_inv_header_dict['TripNumber'])).upper()
    trpno=re.sub(r'\s+$',"",trpno)
    temp1=f"SELECT NominationId from NominationHeader_External WHERE UPPER(TripNumber) = '{trpno}'"
    print(temp1,"########")
    cursor.execute(temp1)
    row=cursor.fetchone()
    print(row,"#########")
    if row:
        nomid=row[0]
        print('nomination id found')
    else:
        print('no match in nominationid')
    print(nomid)
    if(nomid):
        print('hi')
        print({final_inv_header_dict['VendorName']})
        vendor = (re.sub(r"^\s+","",final_inv_header_dict['VendorName']))
        vendor=re.sub(r'\s+$',"",vendor).upper()
        if('COASTAL GULF'in vendor):
            vendor='COASTAL GULF'
        jobdate = final_inv_header_dict.get('JobDate', "")
        activity=re.sub(r'\s+$',"",(re.sub(r'^\s+',"",final_inv_header_dict['ActivityType']).upper()))
        location = re.sub(r'\s+$', "", (re.sub(r'^\s+', "", final_inv_header_dict['JobLocation']).upper()))

        temp2=f"SELECT NominationDetailId from NominationDetails_External WHERE NominationId={nomid}  AND CHARINDEX(Activity,'{activity}')>0  AND UPPER(Vendor) = '{vendor}' OR UPPER(Location) = '{location}' OR DATEDIFF(day, ETA,'{jobdate}') =0"
        print(temp2)
        cursor.execute(temp2)
        row1=cursor.fetchone()
        print(row1)
        if row1:
            NominationDeatilID=row1[0]
            print('Nominationdetail id found')
        else:
            print('hhh no match')

        list_of_values.append(NominationDeatilID)
        list_of_col_heading.append('NominationDetailId')
    GICid=''
    try:
        vendorid=''
        locationid=''
        regionid=''
        temp2=f"SELECT VendorId,LocationId from NominationDetails_External WHERE NominationId={nomid}  AND CHARINDEX(Activity,'{activity}')>0  AND UPPER(Vendor) = '{vendor}' OR UPPER(Location) = '{location}' OR DATEDIFF(day, ETA,'{jobdate}') =0"
        print(temp2)
        cursor.execute(temp2)
        row1=cursor.fetchone()
        print(row1)
        if row1:
            vendorid=row1[0]
            locationid=row1[1]
        trpno=(re.sub(r'^\s+',"",final_inv_header_dict['TripNumber'])).upper()
        trpno=re.sub(r'\s+$',"",trpno)
        temp1=f"SELECT RegionId from NominationHeader_External WHERE UPPER(TripNumber) = '{trpno}'"
        print(temp1,"########")
        cursor.execute(temp1)
        row=cursor.fetchone()
        print(row,"#########")
        if row:
            regionid=row[0]
        temp1=f"SELECT GICId from GICHeaderExternal WHERE VendorId = {vendorid} AND RegionId={regionid} AND LocationId={locationid} AND {final_inv_header_dict.get('JobDate','')}=>EffectiveFrom AND {final_inv_header_dict.get('JobDate','')}<=EffectiveTo"
        print(temp1,"########")
        cursor.execute(temp1)
        row=cursor.fetchone()
        print(row,"#########")
        if row:
            GICid=row[0]
            list_of_values.append(GICid)
            list_of_col_heading.append('GICId')

        

    except:
        print('error in gicid')


    try:
        list_of_values.append(final_inv_header_dict.get('VendorName',""))
        list_of_col_heading.append('Vendor')
    except:
        print('error in Vendor')
    try:
        #temp changes
        # act=final_inv_header_dict.get('ActivityType',"")[len(final_inv_header_dict.get('ActivityType',""))-8:]
        # print(act,"#########$")
        list_of_values.append(final_inv_header_dict.get('ActivityType',""))
        # list_of_values.append(act)
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
        list_of_values.append(0)
        list_of_col_heading.append('Status')
    except:
        print('error in status')
    try:
        currdt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')[:-9]
        list_of_values.append(str(currdt))
        list_of_col_heading.append('CreatedDate')
    except:
        print('error in createdDate')
    ###### new code add
    try:
        AffilateId=''
        temp1=f"SELECT RowId from  AffiliateMaster where description= '{final_inv_header_dict['JobLocation']}'"
        print(temp1)
        cursor.execute(temp1)
        row=cursor.fetchone()
        print(row,'################')
        if row:
            AffilateId=row[0]
            print('affilate id found',AffilateId)
        else:
            print('no match in affilateid')
        list_of_values.append(AffilateId)
        list_of_col_heading.append('AffiliateId')
    except:
        print('affilate Id not found')
    try:
        CurrencyId=''
        temp1=f"SELECT RowId from CurrencyMaster where description= '{final_inv_header_dict['Currency']}' OR CurrencyCode='{final_inv_header_dict['Currency']}'"
        print(temp1)
        cursor.execute(temp1)
        row=cursor.fetchone()
        print(row,'################')
        if row:
            CurrencyId=row[0]
            print('currency id found',CurrencyId)
        else:
            print('no match in currencyid')
        list_of_values.append(CurrencyId)
        list_of_col_heading.append('CurrencyId')
    except:
        print('currency id not found')

    ############ QUERY EXE FOR INVOICE HEADER #######
    try:

        insert_query=f'INSERT INTO {table_name} ({", ".join(list_of_col_heading)}) VALUES {tuple(list_of_values)}'
        insert_query=re.sub("''|None",'NULL',insert_query)
        print(insert_query)
        cursor.execute(insert_query)
        cursor.commit()

    except:
        print("1.ERROR OCCURED DURING INSERTION OF INVOICE HEADERS :(")

#################################### INVOICE QUANTITY INSERTION TOSCANA #############################

def inv_qunatity_toscana_insertion(final_inv_header_dict,final_inv_qnt):
    conn = connect_db()
    cursor = conn.cursor()
    InvoiceId=''
    NominationDetailId=''

    temp1=f"SELECT RowId from InvoiceHeader_External WHERE InvoiceNumber = {final_inv_header_dict['InvoiceNumber']}"
    print(temp1)
    cursor.execute(temp1)
    row=cursor.fetchone()
    if row:
        InvoiceId=row[0]
        print('nomination id found')
    else:
        print('no match in nominationid')
    print(InvoiceId)

    nomid=''
    nnn=''
    temp=f'SELECT NominationDetailId FROM InvoiceHeader_External WHERE RowId = {InvoiceId}'
    print(temp,"######")
    cursor.execute(temp)
    row=cursor.fetchone()
    print(row,"###")
    if row:
        nomid=row[0]
        print('nomination id found')
        t=f"SELECT NominationQuantityId from NominationQuantity_External Where NominationDetailId= {nomid} and VesselName= '{final_inv_header_dict['VesselName']}' and ProductName='{final_inv_header_dict['ProductName']}' and NominationKey = '{final_inv_header_dict['NominationKey']}'"
        print(t,'@@@@')
        cursor.execute(t)
        ro=cursor.fetchone()
        if ro:
            nnn=ro[0]
    else:
        print('no match ')


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
            list_of_li_qnt_val.append(NominationDetailId)#hardcode
            list_of_li_qnt_hd.append('NominationQuantityId')
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
        
            temp1=f"SELECT RowId from ProductCatalogMaster WHERE description= '{final_inv_header_dict.get('ProductName')}'"
            print(temp1)
            cursor.execute(temp1)
            row=cursor.fetchone()
            print(row,'################')
            if row:
                ProductId=row[0]
                print('product id found',ProductId)
            else:
                print('no match in invid')
            list_of_li_qnt_val.append(ProductId)
            list_of_li_qnt_hd.append('ProductId')
        except:
            print('Product Id not found')
        try:
            UoMId=''
            temp1=f"SELECT RowId from UoMMaster where description= '{final_inv_header_dict.get('UnitOfMeasure')}'"
            print(temp1)
            cursor.execute(temp1)
            row=cursor.fetchone()
            print(row,'################')
            if row:
                UoMId=row[0]
                print('uom id found',UoMId)
            else:
                print('no match in uomid')
            list_of_li_qnt_val.append(UoMId)
            list_of_li_qnt_hd.append('UoMId')
        except:
            print('Uom Id not found')
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
            currdt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')[:-3]
            list_of_li_qnt_val.append(str(currdt))
            list_of_li_qnt_hd.append('CreatedDate')
        except:
            print('error in createdDate')
        try:
            for j in i:
                list_of_li_qnt_val.append(i[j])

                list_of_li_qnt_hd.append(j)

        except:
            print('error in 2323232####')
        # try:

        insert_query=f'INSERT INTO {table_name1} ({", ".join(list_of_li_qnt_hd)}) VALUES {tuple(list_of_li_qnt_val)}'
        # print(insert_query)
        insert_query=re.sub("''|None",'NULL',insert_query)
        print(insert_query)
        cursor.execute(insert_query)
        cursor.commit()
        print(insert_query)
        # except :
        #     print("1.ERROR OCCURED DURING INSERTION OF INVOICE qunatity insertion :(")
            
############################################## TOSCANA INVOICE QUALITY INSERION #############################
            
    
def  inv_qlty_db_insertion_toscana(final_inv_header_dict,final_inv_qlty):
    conn = connect_db()
    cursor = conn.cursor()
    InvoiceId=1
    NomId=''

    temp1=f"SELECT RowId from InvoiceHeader_External WHERE InvoiceNumber = {final_inv_header_dict['InvoiceNumber']}"
    print(temp1)
    cursor.execute(temp1)
    row=cursor.fetchone()
    print(row,'################')
    if row:
        InvoiceId=row[0]
        print('inv id found',InvoiceId)
    else:
        print('no match in invid')


        
    table_name='InvoiceQuality_External'
    for i in final_inv_qlty:
        list_of_qlty_val=[]
        list_of_qlty_hd=[]
        try:
            list_of_qlty_val.append(InvoiceId)
            list_of_qlty_hd.append('InvoiceId')
        except:
            print('error in InvoiceId qlty')
        try:
            try:
                nomid=''
                temp=f'SELECT NominationDetailId FROM InvoiceHeader_Exteranl WHERE RowId = {InvoiceId}'
                cursor.execute(temp)
                row=cursor.fetchone()
                if row:
                    nomid=row[0]
                    print('nomination id found')
                    t=f"SELECT NominationQualityId from NominationQuality_External Where NominationDetailId= {nomid} and ProductName='{final_inv_header_dict['ProductName']}' and TestName='{i['TestName']}' and  TestMethod='{i['TestMethod']}'"
                    cursor.execute(t)
                    ro=cursor.fetchone()
                    if ro:
                        NomId=ro[0]
            except:
                print('not able to get nomid')
            list_of_qlty_val.append(NomId)# hardcode
            list_of_qlty_hd.append('NominationQualityID')
        except:
            print('error in Nomqltyid')
        try:
            gicId=''
            temp1=f"SELECT GICId from InvoiceHeader_External WHERE InvoiceNumber = {final_inv_header_dict['InvoiceNumber']}"
            print(temp1)
            cursor.execute(temp1)
            row=cursor.fetchone()
            print(row,'################')
            if row:
                gicId=row[0]
                UoMId=''
                temp1=f"SELECT RowId from UoMMaster where description= '{final_inv_header_dict.get('UnitOfMeasure')}'"
                print(temp1)
                cursor.execute(temp1)
                row=cursor.fetchone()
                print(row,'################')
                if row:
                    UoMId=row[0]
                    LabTestId=''
                    temp1=f"SELECT RowId from LabTestMaster where TestMethod= '{i['TestMethod']}'"
                    print(temp1)
                    cursor.execute(temp1)
                    row=cursor.fetchone()
                    print(row,'################')
                    if row:
                        LabTestId=row[0]
                        LabTestId=''
                        temp1=f"SELECT GICQualityId from GICQuality_External where LabTestID={LabTestId} AND UoMId={UoMId} AND GICId={gicId}"
                        print(temp1)
                        cursor.execute(temp1)
                        row=cursor.fetchone()
                        print(row,'################')
                        if row:
                            gicqltyId=row[0]
                            list_of_qlty_val.append(gicqltyId)
                            list_of_qlty_hd.append('GICQualityID')



                

        except:
            print('error in gicqultid')
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
        
            temp1=f"SELECT RowId from ProductCatalogMaster WHERE description= '{final_inv_header_dict.get('ProductName')}'"
            print(temp1)
            cursor.execute(temp1)
            row=cursor.fetchone()
            print(row,'################')
            if row:
                ProductId=row[0]
                print('product id found',ProductId)
            else:
                print('no match in productid')
            list_of_qlty_val.append(ProductId)
            list_of_qlty_hd.append('ProductId')
        except:
            print('error in productid')
        try:
            UoMId=''
            temp1=f"SELECT RowId from UoMMaster where description= '{final_inv_header_dict.get('UnitOfMeasure')}'"
            print(temp1)
            cursor.execute(temp1)
            row=cursor.fetchone()
            print(row,'################')
            if row:
                UoMId=row[0]
                print('uom id found',UoMId)
            else:
                print('no match in uomid')
            list_of_qlty_val.append(UoMId)
            list_of_qlty_hd.append('UoMId')
        except:
            print('Uom Id not found')
        try:
            LabTestId=''
            temp1=f"SELECT RowId from LabTestMaster where TestMethod= '{i['TestMethod']}'"
            print(temp1)
            cursor.execute(temp1)
            row=cursor.fetchone()
            print(row,'################')
            if row:
                LabTestId=row[0]
                print('lab id found',LabTestId)
            else:
                print('no match in labid')
            list_of_qlty_val.append(LabTestId)
            list_of_qlty_hd.append('LabTestId')
        except:
            print('Lab Id not found')
        try:
            list_of_qlty_val.append(final_inv_header_dict.get('DiscountPercent',""))
            list_of_qlty_hd.append('DiscountPercent')
        except:
            print('error in DiscountPercent')
        try:
            list_of_qlty_val.append(final_inv_header_dict.get('AmountBeforeTax',""))
            list_of_qlty_hd.append('AmountBeforeTax')
        except:
            print('error in amountbeforetax')
        try:
            list_of_qlty_val.append(value_createdby)
            list_of_qlty_hd.append('CreatedBy')
        except:
            print('error in created By')
        try:
            currdt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')[:-3]
            list_of_qlty_val.append(str(currdt))
            list_of_qlty_hd.append('CreatedDate')
        except:
            print('error in createdDate')
        try:
            for j in  i:
                list_of_qlty_val.append(i[j])
                list_of_qlty_hd.append(j)
        except:
            print('error in qlty dict ins')



        
        insert_query=f'INSERT INTO {table_name} ({", ".join(list_of_qlty_hd)}) VALUES {tuple(list_of_qlty_val)}'
        insert_query=re.sub("''|None",'NULL',insert_query)
        print(insert_query)
        cursor.execute(insert_query)
        cursor.commit()
       
############################################ main for running the above invoice insertioncode ####################################


# def db_main_toscana(inp_path):
#     conn = connect_db()
#     cursor = conn.cursor()
#     final_dict_hd=(cgi_invoice_headers_extraction(read_textfile(inp_path),'1'))
#     final_dict_hd=inv_header_dict_formatting(final_dict_hd)
#     # print(final_dict_hd)
#     temp_di=cgi_lineitem_main(inp_path)
#     final_list_qnt=temp_di['Quantity']
#     final_list_qlty=temp_di['quality']
#     final_list_qnt,final_list_qlty=dict_formatting_lineitem_inv(final_list_qnt,final_list_qlty)
#     # print(final_list_qnt,final_list_qlty)
#     # toscana_inv_insertion(final_dict_hd,final_list_qnt,final_list_qlty)
#     # inv_qunatity_toscana_insertion(final_dict_hd,final_list_qnt)
#     # inv_qlty_db_insertion_toscana(final_dict_hd,final_list_qlty)
#     cursor.close()
#     conn.close()

# # inp_path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/Extra_data/Inv_302512/Inv_302512.text"
# db_main_toscana(inp_path)





########################## DB INSPECTION DATA INSERTION ##################################################################################################
def toscana_inspection_ins(insqnt_dict,inv_hd_dict):
    table_name='InspectionQuantity_External'
    conn = connect_db()
    cursor = conn.cursor()
    list_of_val=[]
    list_of_hd=[]
    tempuomid=''
    tempproductid=''
    try:
        list_of_val=[2]
        list_of_hd=['CreatedBy']
    except:
        print('error in createdby')
    try:
        currdt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')[:-3]
        list_of_val.append(str(currdt))
        list_of_hd.append('CreatedDate')
    except:
        print('error in createdDate')
    try:
        if(insqnt_dict['NominatedQuantity']!=''):
            insqnt_dict['NominatedQuantity'] = float(re.sub(r'\s+|[,]', "", insqnt_dict['NominatedQuantity']))
        list_of_val.append(insqnt_dict['NominatedQuantity'])
        list_of_hd.append('InspectedQuantity')
    except:
        print('error in inspected quantity')

    try:
        list_of_val.append(insqnt_dict['ProductName'])
        list_of_hd.append('ProductName')
    except:
        print('error in ProductName')
    try:
        list_of_val.append(insqnt_dict['VesselName'])
        list_of_hd.append('VesselName')
    except:
        print('error in vessel name')
    try:
        list_of_val.append(insqnt_dict['UnitOfMeasure'])
        list_of_hd.append('UoM')
    except:
        print('error in uom')
    try:
        InvoiceId=''
        temp1=f"SELECT RowId from InvoiceHeader_External WHERE InvoiceNumber = '{inv_hd_dict['InvoiceNumber']}'"
        # print(temp1)
        cursor.execute(temp1)
        row=cursor.fetchone()
        print(row,'################')
        if row:
            InvoiceId=row[0]
            print('inv id found',InvoiceId)
        else:
            print('no match in invid')
        list_of_val.append(InvoiceId)
        list_of_hd.append('InvoiceId')
    except:
        print('Invoice Id not found')
    try:
        ProductId=''
        temp1=f"SELECT RowId from ProductCatalogMaster WHERE description= '{insqnt_dict['ProductName']}'"
        print(temp1)
        cursor.execute(temp1)
        row=cursor.fetchone()
        print(row,'################')
        if row:
            ProductId=row[0]
            tempproductid=ProductId
            print('inv id found',ProductId)
        else:
            print('no match in invid')
        list_of_val.append(ProductId)
        list_of_hd.append('ProductId')
    except:
        print('Product Id not found')
    try:
        UoMId=''
        temp1=f"SELECT RowId from UoMMaster where description= '{insqnt_dict['UnitOfMeasure']}'"
        print(temp1)
        cursor.execute(temp1)
        row=cursor.fetchone()
        print(row,'################')
        if row:
            UoMId=row[0]
            tempuomid=UoMId
            print('inv id found',UoMId)
        else:
            print('no match in invid')
        list_of_val.append(UoMId)
        list_of_hd.append('UoMId')
    except:
        print('Uom Id not found')
    try:
        NomqntId=''
        nomdtid=''
        temp1=f"SELECT NominationDetailId from InvoiceHeader_External WHERE InvoiceNumber = '{inv_hd_dict['InvoiceNumber']}'"
        # print(temp1)
        cursor.execute(temp1)
        row=cursor.fetchone()
        print(row,'################')
        if row:
            nomdtid=row[0]
            print('nomdtid id found')
        else:
            print('no match in nomdtid')
        temp1=f"SELECT NominationQuantityId from NominationQuantity_External WHERE NominationDetailId = {nomdtid} AND UoMId={tempuomid} AND ProductId={tempproductid} AND VesselName='{insqnt_dict['VesselName']}'"
        # print(temp1)
        cursor.execute(temp1)
        row=cursor.fetchone()
        print(row,'################')
        if row:
            NomqntId=row[0]
            print('nomdtid id found',NomqntId)
        else:
            print('no match in nomqntid')
        list_of_val.append(NomqntId)
        list_of_hd.append('NominationQuantityId')
    except:
        print('NominationQuantity Id not found')



    insert_query=f'INSERT INTO {table_name} ({", ".join(list_of_hd)}) VALUES {tuple(list_of_val)}'
    insert_query=re.sub("''|None",'NULL',insert_query)
    print(insert_query)
    cursor.execute(insert_query)
    cursor.commit()

    cursor.close()
    
    
####### calling inspection_tos_main #####



# def inspection_tos_main(inp_path,inp_inv):
#     final_dict_hd=(cgi_invoice_headers_extraction(read_textfile(inp_inv),'1'))
#     insqnt_dict=cgi_quantity_headers_extraction(read_textfile(inp_path),'1')
#     toscana_inspection_ins(insqnt_dict,final_dict_hd)

# ####### calling inspection_tos_main #####
# inp_path=r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/CGI/US/302512/99093.text'
# inp_inv=r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/CGI/US/302512/Inv_302512.text'

# inspection_tos_main(inp_path,inp_inv)




################################## TOSCANA DB INSPECTION QUALITY #####################################################
def toscana_inspection_quality_ins(insqli_hd_dict,insqli_li_hd_dict,inv_hd_dict):
    # list_of_val=[]
    # list_of_hd=[]
    ProductId=''
    InvoiceId=''
    table_name='InspectionQuality_External'
    conn = connect_db()
    cursor = conn.cursor()


    try:
        InvoiceId=''
        temp1=f"SELECT RowId from InvoiceHeader_External WHERE InvoiceNumber = '{inv_hd_dict['InvoiceNumber']}'"
        # print(temp1)
        cursor.execute(temp1)
        row=cursor.fetchone()
        print(row,'################')
        if row:
            InvoiceId=row[0]
            print('inv id found',InvoiceId)
        else:
            print('no match in invid')
        # list_of_val.append(InvoiceId)
        # list_of_hd.append('InvoiceId')
    except:
        print('Invoice Id not found')
    try:
        
        temp1=f"SELECT RowId from ProductCatalogMaster WHERE description= '{insqli_hd_dict['ProductName']}'"
        print(temp1)
        cursor.execute(temp1)
        row=cursor.fetchone()
        print(row,'################')
        if row:
            ProductId=row[0]
            print('inv id found',ProductId)
        else:
            print('no match in invid')
        # list_of_val.append(ProductId)
        # list_of_hd.append('ProductId')
    except:
        print('Product Id not found')

    for i in insqli_li_hd_dict:
        # conn = connect_db()
        # cursor = conn.cursor()
        templabtestid=''
        list_of_val=[]
        list_of_hd=[]
        try:
            list_of_val.append(InvoiceId)
            list_of_hd.append('InvoiceId')
        except:
            print('error in invid')
        try:
            list_of_val.append(ProductId)
            list_of_hd.append('ProductId')
        except:
            print("error in proid")
        try:
            list_of_val.append(2)
            list_of_hd.append('CreatedBy')
        except:
            print('error in created by')
        try:
            currdt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')[:-3]
            list_of_val.append(str(currdt))
            list_of_hd.append('CreatedDate')
        except:
            print('error in createdDate')
        try:
            list_of_val.append(insqli_hd_dict['ProductName'])
            list_of_hd.append('ProductName')
        except:
            print("error in ProductName")
        try:
            list_of_val.append(insqli_hd_dict['VesselName'])
            list_of_hd.append('VesselName')
        except:
            print('error in vesselname')
        try:
            LabTestId=''
            temp1=f"SELECT RowId from LabTestMaster where TestMethod= '{i['method']}'"
            print(temp1)
            cursor.execute(temp1)
            row=cursor.fetchone()
            print(row,'################')
            if row:
                LabTestId=row[0]
                templabtestid=LabTestId
                print('lab id found',LabTestId)
            else:
                print('no match in labid')
            list_of_val.append(LabTestId)
            list_of_hd.append('LabTestId')
        except:
            print('Lab Id not found')

        try:
            list_of_val.append(i['method'])
            list_of_hd.append('TestMethod')
        except:
            print(i['method'])
        try:
            list_of_val.append(i['component'])
            list_of_hd.append('TestName')
        except:
            print('error in',i['component'])



        try:
            NomqltId=''
            nomdtid=''
            temp1=f"SELECT NominationDetailId from InvoiceHeader_External WHERE InvoiceNumber = '{inv_hd_dict['InvoiceNumber']}'"
            # print(temp1)
            cursor.execute(temp1)
            row=cursor.fetchone()
            print(row,'################')
            if row:
                nomdtid=row[0]
                print('nomdtid id found')
            else:
                print('no match in nomdtid')
            temp1=f"SELECT NominationQualityId from NominationQuality_External WHERE NominationDetailId = {nomdtid} AND ProductId={ProductId} AND VesselName='{insqli_hd_dict['VesselName']}' AND LabTestId={templabtestid} AND TestName='{i['component']}' AND TestMethod='{i['method']}'"
            # print(temp1)
            cursor.execute(temp1)
            row=cursor.fetchone()
            print(row,'################')
            if row:
                NomqltId=row[0]
                print('nomdtid id found',NomqltId)
                list_of_val.append(NomqltId)
                list_of_hd.append('NominationDetailId')




        except:
            print('error in NominationQualityid')
        insert_query=f'INSERT INTO {table_name} ({", ".join(list_of_hd)}) VALUES {tuple(list_of_val)}'
        insert_query=re.sub("''|None",'NULL',insert_query)
        print(insert_query)
        cursor.execute(insert_query)
        cursor.commit()

    cursor.close()

######## INCPECTION QUALITY MAIN ################



# def Inspection_Quality_tos_main(inp_path,inp_inv):
#     final_dict_hd=(cgi_invoice_headers_extraction(read_textfile(inp_inv),'1'))
#     insqli_hd_dict=cgi_quality_headers_extraction(read_textfile(inp_path),'1')
#     insqli_li_hd_dict=cgi_qlty_lineitem_main(inp_path)
#     toscana_inspection_quality_ins(insqli_hd_dict,insqli_li_hd_dict,final_dict_hd)


###################### calling of ins qlt li insertion ##
# inp_inv=r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/CGI/US/302512/Inv_302512.text'
# inp_path=r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/CGI/US/302512/9907599093_217_CSOMCB_L20201105004_Exxon_Final.text'

# Inspection_Quality_tos_main(inp_path,inp_inv)






################################ MAIN FUNTION FOR CALLING IN API #############
# USE THIS TO CALL IN API FRO INVOICE
def api_db_toscana_inv_main_call(final_dict_hd, inv_lineitem_dict,global_nom_parcel):
    conn = connect_db()
    cursor = conn.cursor()
    final_dict_hd = inv_header_dict_formatting(final_dict_hd)
    temp_di = inv_lineitem_dict
    final_list_qnt = temp_di['Quantity']
    final_list_qlty = temp_di['quality']
    final_list_qnt, final_list_qlty = dict_formatting_lineitem_inv(
        final_list_qnt, final_list_qlty)
    toscana_inv_insertion(final_dict_hd, final_list_qnt, final_list_qlty,global_nom_parcel)
    inv_qunatity_toscana_insertion(final_dict_hd, final_list_qnt)
    inv_qlty_db_insertion_toscana(final_dict_hd, final_list_qlty)
    cursor.close()
    conn.close()


# USE THIS FOR API CALL FOR INSPECTION QUANTITY
def api_tos_inspection_quantity_main(insqnt_dict, final_dict_hd):
    toscana_inspection_ins(insqnt_dict, final_dict_hd)


# USE THIS FOR API CALL INSPECTION QUALITY
def api_tos_inspection_quality_main(insqli_hd_dict, insqli_li_hd_dict, final_dict_hd):
    toscana_inspection_quality_ins(
        insqli_hd_dict, insqli_li_hd_dict, final_dict_hd)
    
    
#use for this Nomination data to toscana

def api_tos_nomination_main(global_nom_hd):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        stored_proc = "HCL_Nomination_Data_Trans"
        # params = 
        print("Toscana data insert query move to exacto",stored_proc,global_nom_hd['nom_hd_uuid'])
        
        cursor.execute("{call HCL_Nomination_Data_Trans('"+global_nom_hd['nom_hd_uuid']+"')}")
        cursor.commit()
    except:
        traceback.print_exc()
        print("Error in toscana table ")
        pass

    cursor.close()
    conn.close()

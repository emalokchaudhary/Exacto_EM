import pandas as pd
from connection import connect_db
import warnings
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
warnings.filterwarnings('ignore')
conn=connect_db()
def nominationvsInspection(nominationQuantity,inspectionQuantity,conn):
    for index,rows in nominationQuantity.iterrows():
        nominationQuantityId=rows['NominationQuantityId']
        nominationVesselName=rows['NominationVesselName']
        nominationProductName=rows['NominationProductName']
        nominationProductId=rows['NominationProductId']
        nominationUom=rows['NominationUoM']
        nominationUomId=rows['NominationUoMId']
        nominationQuantity=rows['NominatedQuantity']
        for index1,rows1 in inspectionQuantity.iterrows():
            inspectionQuantityId=rows1['InspectionQuantityId']
            inspectionVesselName=rows1['InspectionVesselName']
            inspectionProductName=rows1['InspectionProductName']
            inspectionProductId=rows1['InspectionProductId']
            if(nominationVesselName != None and inspectionVesselName != None):
                nominationVesselName = re.sub(r'(\(\W*\w*\))+', '', nominationVesselName)
                nominationVesselName = re.sub(r'(\s)+', '', nominationVesselName)
                # print(nominationVesselName,'________________-------->')
                inspectionVesselName = re.sub(r'(\(\W*\w*\))+', '', inspectionVesselName)
                inspectionVesselName = re.sub(r'(\s)+', '', inspectionVesselName)
                # print('nom',nominationVesselName,'--inv->',inspectionVesselName)
                if(re.search(r'\W', nominationVesselName) != None):
                    regexsearch = re.search(r'\W', nominationVesselName)
                    if(regexsearch != None):
                        add = regexsearch.group()
                if(re.search(r'&\W*\d+', inspectionVesselName) != None):
                    regexsearch = re.search(r'\s*[a-zA-Z]+', inspectionVesselName)
                    # print(inspectionVesselName.group())
                    if(regexsearch != None):
                        nam = add+regexsearch.group()
                        inspectionVesselName = re.sub(r'&', nam, inspectionVesselName)
                # print('After Preprocess-','nom',nominationVesselName,'--inv->',inspectionVesselName)
                if(re.search(r'&', inspectionVesselName) != None):
                    inspectionVesselName = re.sub(r'&', ',', inspectionVesselName)
                if(('-' in inspectionVesselName) and ('-' not in nominationVesselName)):
                    inspectionVesselName = re.sub('-', '', inspectionVesselName)
            ratio=fuzz.token_set_ratio(nominationVesselName,inspectionVesselName)
            if ratio>89:
                print('Vessel Matched')
                print(inspectionVesselName,'----------------',nominationVesselName)
                inspectionQuantityUoM=pd.read_sql(f"Select * From InspectionQuantityUoM_External where InspectionQuantityId='{inspectionQuantityId}'",conn)
                if inspectionQuantityUoM.empty==True:
                    inspectionQuantityUoM=pd.DataFrame()
                else:
                    inspectionQuantityUoM=pd.DataFrame({'InspectionInspectedQuantity':inspectionQuantityUoM['InspectedQuantity'],'InspectionUoM_UoM':inspectionQuantityUoM['UoM'],'InspectionUoM_UomId':inspectionQuantityUoM['UoMId']})
                for inspectionIndex,inspectionRows in inspectionQuantityUoM.iterrows():
                    inspectionInspectionQuantity=inspectionRows['InspectionInspectedQuantity']
                    inspectionInspectionUom=inspectionRows['InspectionUoM_UoM']
                    inspectionInspectionUomId=inspectionRows['InspectionUoM_UomId']
                    if((nominationUom!=None and inspectionInspectionUom!=None) or (nominationUomId!=None and inspectionInspectionUomId!=None)):
                                        if(nominationUom==inspectionInspectionUom or nominationUomId==inspectionInspectionUomId or re.search(nominationUom,inspectionInspectionUom)):
                                            nominationInspectionUom=20
                                            count=0
                                            if(inspectionInspectionQuantity!=None and nominationQuantity!=None):
                                                lessvalue=nominationQuantity-nominationQuantity*(5/100)
                                                greatvalue=nominationQuantity+nominationQuantity*(5/100)
                                                print('InspectionQUantityvalues',inspectionInspectionQuantity,'----',lessvalue,'-----',greatvalue)
                                                if(inspectionInspectionQuantity>=lessvalue and inspectionInspectionQuantity<=greatvalue):
                                                    if(inspectionInspectionQuantity<greatvalue):
                                                        thresholdoutcome=15
                                                        quantityoutcome=18
                                                    else:
                                                        thresholdoutcome=15
                                                        quantityoutcome=18
                                                else:
                                                    quantityoutcome=19
                                                    thresholdoutcome=16
                                                    count+=1
                                                    print('Else 16InspectionQUantityvalues',inspectionInspectionQuantity,'----',lessvalue,'-----',greatvalue)
                                            else:
                                                quantityoutcome=17
                                                thresholdoutcome=17

                break
            else:
                continue
        
        else:
            print('Fuck')

def invoicevsInspection(invoiceQuantity,inspectionQuantity,conn):
    for index,rows in invoiceQuantity.iterrows():
        nominationQuantityId=rows['NominationQuantityId']
        nominationVesselName=rows['NominationVesselName']
        nominationProductName=rows['NominationProductName']
        nominationProductId=rows['NominationProductId']
        nominationUom=rows['NominationUoM']
        nominationUomId=rows['NominationUoMId']
        nominationQuantity=rows['NominatedQuantity']
        for index1,rows1 in inspectionQuantity.iterrows():
            inspectionQuantityId=rows1['InspectionQuantityId']
            inspectionVesselName=rows1['InspectionVesselName']
            inspectionProductName=rows1['InspectionProductName']
            inspectionProductId=rows1['InspectionProductId']
            if(nominationVesselName != None and inspectionVesselName != None):
                nominationVesselName = re.sub(r'(\(\W*\w*\))+', '', nominationVesselName)
                nominationVesselName = re.sub(r'(\s)+', '', nominationVesselName)
                # print(nominationVesselName,'________________-------->')
                inspectionVesselName = re.sub(r'(\(\W*\w*\))+', '', inspectionVesselName)
                inspectionVesselName = re.sub(r'(\s)+', '', inspectionVesselName)
                # print('nom',nominationVesselName,'--inv->',inspectionVesselName)
                if(re.search(r'\W', nominationVesselName) != None):
                    regexsearch = re.search(r'\W', nominationVesselName)
                    if(regexsearch != None):
                        add = regexsearch.group()
                if(re.search(r'&\W*\d+', inspectionVesselName) != None):
                    regexsearch = re.search(r'\s*[a-zA-Z]+', inspectionVesselName)
                    # print(inspectionVesselName.group())
                    if(regexsearch != None):
                        nam = add+regexsearch.group()
                        inspectionVesselName = re.sub(r'&', nam, inspectionVesselName)
                # print('After Preprocess-','nom',nominationVesselName,'--inv->',inspectionVesselName)
                if(re.search(r'&', inspectionVesselName) != None):
                    inspectionVesselName = re.sub(r'&', ',', inspectionVesselName)
                if(('-' in inspectionVesselName) and ('-' not in nominationVesselName)):
                    inspectionVesselName = re.sub('-', '', inspectionVesselName)
            ratio=fuzz.token_set_ratio(nominationVesselName,inspectionVesselName)
            if ratio>89:
                print('Vessel Matched')
                print(inspectionVesselName,'----------------',nominationVesselName)
                inspectionQuantityUoM=pd.read_sql(f"Select * From InspectionQuantityUoM_External where InspectionQuantityId='{inspectionQuantityId}'",conn)
                if inspectionQuantityUoM.empty==True:
                    inspectionQuantityUoM=pd.DataFrame()
                else:
                    inspectionQuantityUoM=pd.DataFrame({'InspectionInspectedQuantity':inspectionQuantityUoM['InspectedQuantity'],'InspectionUoM_UoM':inspectionQuantityUoM['UoM'],'InspectionUoM_UomId':inspectionQuantityUoM['UoMId']})
                for inspectionIndex,inspectionRows in inspectionQuantityUoM.iterrows():
                    inspectionInspectionQuantity=inspectionRows['InspectionInspectedQuantity']
                    inspectionInspectionUom=inspectionRows['InspectionUoM_UoM']
                    inspectionInspectionUomId=inspectionRows['InspectionUoM_UomId']
                    if((nominationUom!=None and inspectionInspectionUom!=None) or (nominationUomId!=None and inspectionInspectionUomId!=None)):
                                        if(nominationUom==inspectionInspectionUom or nominationUomId==inspectionInspectionUomId or re.search(nominationUom,inspectionInspectionUom)):
                                            thresholdoutcome=20
                                            count=0
                                            if(inspectionInspectionQuantity!=None and nominationQuantity!=None):
                                                lessvalue=nominationQuantity-nominationQuantity*(5/100)
                                                greatvalue=nominationQuantity+nominationQuantity*(5/100)
                                                print('InspectionQUantityvalues',inspectionInspectionQuantity,'----',lessvalue,'-----',greatvalue)
                                                if(inspectionInspectionQuantity>=lessvalue and inspectionInspectionQuantity<=greatvalue):
                                                    if(inspectionInspectionQuantity<greatvalue):
                                                        thresholdoutcome=15
                                                        
                                                    else:
                                                        thresholdoutcome=15
                                                        quantityoutcome=18
                                                else:
                                                    
                                                    thresholdoutcome=16
                                                    count+=1
                                                    print('Else 16InspectionQUantityvalues',inspectionInspectionQuantity,'----',lessvalue,'-----',greatvalue)
                                            else:
                                                quantityoutcome=17
                                                thresholdoutcome=17

                break
            else:
                continue
        
        else:
            print('Fuck')


def wrongQuantity(invoiceId,nominationDetailId,conn):
    inspectionId=pd.read_sql(f"Select InspectionId From InspectionHeader_External where InvoiceId='{invoiceId}'",conn)
    if inspectionId.empty==True:
        inspectionId=0
    else:
        inspectionId=int(inspectionId['InspectionId'][0])
    invoiceQuantity=pd.read_sql(f"Select * From InvoiceQuantity_External where InvoiceId='{invoiceId}'",conn)
    if invoiceQuantity.empty==True:
        invoiceQuantity=pd.DataFrame()
    else:
        invoiceQuantity=pd.DataFrame({'InvoiceQuantityId':invoiceQuantity['InvoiceQantityId'],'InvoiceVesselName':invoiceQuantity['VesselName'],'InvoiceProductName':invoiceQuantity['ProductName'],'InvoiceProductId':invoiceQuantity['ProductId'],'InvoiceUoM':invoiceQuantity['UoM'],'InvoiceUoMId':invoiceQuantity['UoMId'],'InvoiceQuantityValue':invoiceQuantity['QuantityValue']})
    nominationQuantity=pd.read_sql(f"Select * From NominationQuantity_External where NominationDetailId='{nominationDetailId}'",conn)
    if nominationQuantity.empty==True:
        nominationQuantity=pd.DataFrame()
    else:
        nominationQuantity=pd.DataFrame({'NominationQuantityId':nominationQuantity['NominationQuantityId'],'NominationVesselName':nominationQuantity['VesselName'],'NominationProductName':nominationQuantity['ProductName'],'NominationProductId':nominationQuantity['ProductId'],'NominationUoM':nominationQuantity['UoM'],'NominationUoMId':nominationQuantity['UoMId'],'NominatedQuantity':nominationQuantity['NominatedQuanity']})
    inspectionQuantity=pd.read_sql(f"Select * From InspectionQuantity_External where InspectionId='{inspectionId}'",conn)
    if inspectionQuantity.empty==True:
        inspectionQuantity=pd.DataFrame()
    else:
        inspectionQuantity=pd.DataFrame({'InspectionQuantityId':inspectionQuantity['InspectionQuantityId'],'InspectionVesselName':inspectionQuantity['VesselName'],'InspectionProductName':inspectionQuantity['ProductName'],'InspectionProductId':inspectionQuantity['ProductId']})
    nominationvsInspection(nominationQuantity,inspectionQuantity,conn)
invoices=pd.read_sql(f"Select * from InvoiceHeader_External where StatusID=53",conn)
for index,rows in invoices.iterrows():
    nominationDetailId=rows['NominationDetailId']
    invoiceId=rows['RowID']
    print('--------------------------------------------')
    print(invoiceId)
    wrongQuantity(invoiceId,nominationDetailId,conn)
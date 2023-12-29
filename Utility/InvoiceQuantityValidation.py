
from connection import connect_db
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import datetime
import numpy as np
import warnings
import re
warnings.filterwarnings("ignore")


def invoiceQuantityValidation(invoiceId,nominationDetailId,conn):
    createdBy=2
    createdDate=datetime.datetime.now()
    isactive=0
    cursor=conn.cursor()
    invoiceQuantityItems=pd.read_sql(f"Select * From InvoiceQuantity_External where InvoiceId={invoiceId}",conn)
    nominationQuantityItems=pd.read_sql(f"Select * From NominationQuantity_External where NominationDetailId='{nominationDetailId}'",conn)
    d1=pd.DataFrame({'InvoiceQuantityId':invoiceQuantityItems['InvoiceQantityId'],'InvoiceVesselName':invoiceQuantityItems['VesselName'],'InvoiceProductName':invoiceQuantityItems['ProductName'],'InvoiceProductId':invoiceQuantityItems['ProductId'],'InvoiceUoM':invoiceQuantityItems['UoM'],'InvoiceUoMId':invoiceQuantityItems['UoMId'],'InvoiceCostShare':invoiceQuantityItems['CostShare'],'InvoiceQuantity':invoiceQuantityItems['QuantityValue']})
    d2=pd.DataFrame({'NominationVesselName':nominationQuantityItems['VesselName'],'NominationProductName':nominationQuantityItems['ProductName'],'NominationProductId':nominationQuantityItems['ProductId'],'NominationUoM':nominationQuantityItems['UoM'],'NominationUoMId':nominationQuantityItems['UoMId'],'NominationCostShare':nominationQuantityItems['CostSharePercent'],'NominationQuantity':nominationQuantityItems['NominatedQuanity']})
    ProductIdCheck=''
    ProductIdDiff=''
    vesselNameDiff=''
    vesselNameId=''
    CostShareDiff=''
    CostShareCheck=''
    total=0
    for index,rows in d1.iterrows():
        invoiceVesselName=rows['InvoiceVesselName'].lower()
        invoiceProductName=rows['InvoiceProductName'].lower()
        invoiceProductId=rows['InvoiceProductId']
        invoiceUoM=rows['InvoiceUoM']
        invoiceUoMId=rows['InvoiceUoMId']
        invoiceQuantityId=rows['InvoiceQuantityId']
        invoiceCostShare=rows['InvoiceCostShare']
        invoiceQuantity=rows['InvoiceQuantity']
        print('This is Invoice',invoiceId,'-------',invoiceVesselName)
        # invoiceVesselName=re.sub(r'[-()]+',' ',invoiceVesselName)
        # invoiceVesselName=re.sub(' ','',invoiceVesselName)
        invoiceProductName=re.sub(r'[-()]+',' ',invoiceProductName)
        invoiceProductName=re.sub(' ','',invoiceProductName)
        for nindex,nrows in d2.iterrows():
            nominationVesselName=nrows['NominationVesselName'].lower()
            nominationProductName=nrows['NominationProductName'].lower()
            nominationProductId=nrows['NominationProductId']
            nominationUoM=nrows['NominationUoM']
            nominationUoMId=nrows['NominationUoMId']
            nominationCostShare=nrows['NominationCostShare']
            nominationQuantity=nrows['NominationQuantity']
            nominationProductName=re.sub(r'\([^)]*\)|[-]|[\&]|[/]',' ',nominationProductName)
            nominationProductName=re.sub(' ','',nominationProductName)
            if(nominationVesselName != None and invoiceVesselName != None):
                        nominationVesselName = re.sub(r'(\(\W*\w*\))+', '', nominationVesselName)
                        nominationVesselName = re.sub(r'(\s)+', '', nominationVesselName)
                        # print(nominationVesselName,'________________-------->')
                        invoiceVesselName = re.sub(r'(\(\W*\w*\))+', '', invoiceVesselName)
                        invoiceVesselName = re.sub(r'(\s)+', '', invoiceVesselName)
                        # print('nom',nominationVesselName,'--inv->',invoiceVesselName)
                        if(re.search(r'\W', nominationVesselName) != None):
                            regexsearch = re.search(r'\W', nominationVesselName)
                            if(regexsearch != None):
                                add = regexsearch.group()
                        if(re.search(r'&\W*\d+', invoiceVesselName) != None):
                            regexsearch = re.search(r'\s*[a-zA-Z]+', invoiceVesselName)
                            # print(invoiceVesselName.group())
                            if(regexsearch != None):
                                nam = add+regexsearch.group()
                                invoiceVesselName = re.sub(r'&', nam, invoiceVesselName)
                        # print('After Preprocess-','nom',nominationVesselName,'--inv->',invoiceVesselName)
                        if(re.search(r'&', invoiceVesselName) != None):
                            invoiceVesselName = re.sub(r'&', ',', invoiceVesselName)
                        if(('-' in invoiceVesselName) and ('-' not in nominationVesselName)):
                            invoiceVesselName = re.sub('-', '', invoiceVesselName)
                        # print('After Preprocess-----','nom',nominationVesselName,'--inv->',invoiceVesselName)
            if nominationCostShare==None:
                nominationCostShare=100
            ratio=fuzz.token_set_ratio(invoiceVesselName,nominationVesselName)
            if ratio>89:
                vesselNameDiff='Vessel Name Matched'
                vesselNameId=True
                if invoiceProductId!=None and nominationProductId!=None:
                    if invoiceProductId==nominationProductId:
                        ProductIdCheck=True
                        ProductIdDiff='Product Name Matched'
                    else:
                        ProductIdCheck=False
                        ProductIdDiff='Product Name Not Matched'
                        isactive+=1
                        total+=1
                elif nominationProductId==None and invoiceProductId==None:
                    ratio=fuzz.token_set_ratio(invoiceProductName,nominationProductName)
                    if ratio>85:
                        ProductIdCheck=True
                        ProductIdDiff='Product Name Matched'
                    else:
                        ProductIdCheck=False
                        total+=1
                        ProductIdDiff='Product Name Not Matched'
                        isactive+=1
                elif nominationProductName==None or invoiceProductName==None:
                    ProductIdCheck=False
                    ProductIdDiff='Product Name is Missing in Invoice or Nomination'
                    isactive+=1
                    total+=1
                else:
                    ratio=fuzz.token_set_ratio(invoiceProductName,nominationProductName)
                    if ratio>85:
                        ProductIdCheck=True
                        ProductIdDiff='Product Name Matched'
                    else:
                        ProductIdCheck=False
                        ProductIdDiff='Product Name Not Matched'
                        total+=1
                        isactive+=1
                if invoiceCostShare==None:
                    CostShareDiff='Cost Share is empty'
                    CostShareCheck=False
                    isactive+=1
                    total+=1
                else:
                    if invoiceCostShare==nominationCostShare:
                        CostShareCheck=True
                        CostShareDiff='CostShare Matched'
                    else:
                        CostShareCheck=False
                        CostShareDiff='CostShare Not Matched'
                        total+=1
                        isactive+=1

                print(invoiceVesselName,'---',nominationVesselName)
                print('This is product',invoiceProductName,'---',nominationProductName)
                print(ProductIdDiff)
                print(vesselNameDiff)
                d2.drop(index,inplace=True)
                d1.drop(nindex,inplace=True)

                break        

            else:
                print('Not Match Vessel',invoiceVesselName,'^^^^^',nominationVesselName,ratio)
                vesselNameDiff='VesselName Not Matched'
                vesselNameId=False
                ProductIdCheck=False
                ProductIdDiff='Vessel Name not Matched'
                CostShareCheck=False
                CostShareDiff='VesselName Not Matched'
                ProductIdCheck=False
                total+=1
                isactive+=1     
                
        if isactive>0:
            isactive=1
        else:
            isactive=0

        insert_sql=f"Insert Into InvoiceQuantity_Validation (InvoiceQantityId,CostShareQtyCheck,CostShareQtyDiffReason,CreatedBy,CreatedDate,IsActive,ProductIdCheck,ProductIdDiffReason,VesselNameQtyCheck,VesselNameQtyDiffReason,InvoiceId) Values (?,?,?,?,?,?,?,?,?,?,?)" 
        values=(invoiceQuantityId,CostShareCheck,CostShareDiff,createdBy,createdDate,isactive,ProductIdCheck,ProductIdDiff,vesselNameId,vesselNameDiff,invoiceId)       
        try:

            cursor.execute(insert_sql,values)
            conn.commit()
            print('Record Inserted')
        except Exception as e:
            print('Error In INsertion of Invoice',invoiceId)
    return total



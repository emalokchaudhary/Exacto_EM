
from connection import connect_db
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import datetime
import numpy as np
import warnings
import re
warnings.filterwarnings("ignore")

def InvoiceQualityValidation(invoiceId,nominationDetailId,conn):
    isactive=0
    createdDate=datetime.datetime.now()
    InvoiceQualityItems=pd.read_sql(f"Select * From InvoiceQuality_External where InvoiceId='{invoiceId}'",conn)
    NominationQualityItems=pd.read_sql(f"Select * From NominationQuality_External where NominationDetailId='{nominationDetailId}'",conn)
    d1=pd.DataFrame({'InvoiceQualityId':InvoiceQualityItems['InvoiceQualityId'],'TestMethod':InvoiceQualityItems['TestMethod'],'TestName':InvoiceQualityItems['TestName'],'VesselName':InvoiceQualityItems['VesselName'],'CostShare':InvoiceQualityItems['CostShare']})
    d2=pd.DataFrame({'TestMethod':NominationQualityItems['TestMethod'],'TestName':NominationQualityItems['TestName'],'VesselName':NominationQualityItems['VesselName'],'CostShare':NominationQualityItems['CostSharePercent']})
    VesselNameCheck=''
    VesselNameDiff=''
    TestNameCheck=''
    TestNameDiff=''
    TestMethodCheck=''
    TestMethodDiff=''
    CostShareCheck=''
    CostShareDiff=''
    createdBy=2
    cursor=conn.cursor()
    currentDate=datetime.datetime.now()
    topValue=80
    smallValue=45
    total=0
    if d1.empty!=True and d2.empty!=True:
        for index,rows in d1.iterrows():

            invoicemethod,invoicetest=rows['TestMethod'],rows['TestName']
            invoiceVesselName,invoiceCostShare=rows['VesselName'],rows['CostShare']
            invoiceQualityId=rows['InvoiceQualityId']
            for index1,rows1 in d2.iterrows():
                nomimethod,nomitest=rows1['TestMethod'],rows1['TestName']
                nominationVesselName,nomiCostShare=rows1['VesselName'],rows1['CostShare']
                
                if nomiCostShare==None:
                    nomiCostShare=100
                    nomiCostShare=float(nomiCostShare)
                if nominationVesselName!=None and invoiceVesselName!=None:
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
                m=fuzz.token_set_ratio(invoicetest,nomitest)
                n=fuzz.token_set_ratio(invoicemethod,nomimethod)
                if n>topValue or m>smallValue:
                        print(invoiceVesselName,'---------------',nominationVesselName)
                        ratio=fuzz.token_set_ratio(invoiceVesselName,nominationVesselName)
                        if ratio>89:
                            VesselNameCheck=True
                            VesselNameDiff='Vessel Name Matched'
                        else:
                            if invoiceVesselName==None:
                                 VesselNameCheck=True
                                 VesselNameDiff='No Vessel Name in Invoice'
                            else:
                                VesselNameCheck=False
                                VesselNameDiff='Vessel Name Not Matched'
                                total+=1
                                isactive+=1
                        if invoiceCostShare==nomiCostShare:
                             CostShareCheck=True
                             CostShareDiff='Cost Share Matched'
                        else:
                             if invoiceCostShare==None:
                                  CostShareCheck=True
                                  CostShareDiff='Cost Share Empty Invoice'
                                  isactive+=1
                                  total+=1
                             else:
                                CostShareCheck=False
                                CostShareDiff='CostShare Not Matched'
                                total+=1
                                isactive+=1
                        TestNameCheck=True
                        TestMethodCheck=True
                        TestMethodDiff='TestMethod Matched'
                        TestNameDiff='TestName Matched'
                        d2.drop(index1,inplace=True)
                        d1.drop(index,inplace=True)
                        break
            else:
                VesselNameCheck=False
                VesselNameDiff='Data Not Found Nomination'
                CostShareCheck=False
                CostShareDiff='Data Not Found Nomination'
                TestNameCheck=False
                TestMethodCheck=False
                TestMethodDiff='Data Not Found Nomination'
                TestNameDiff='Data Not Found Nomination'
                isactive+=1
                total+=1
                d1.drop(index,inplace=True) 
            
            if isactive>0:
                isactive=1
            else:
                isactive=0
            insert_sql=f"Insert Into InvoiceQuality_Validation (InvoiceQualityId,CostShareQlyCheck,CostShareQlyDiffReason,CreatedBy,CreatedDate,IsActive,TestCodeCheck,TestCodeDiffReason,TestNameCheck,TestNameDiffReason,VesselNameQlyCheck,VesselNameQlyDiffReason,InvoiceId) Values(?,?,?,?,?,?,?,?,?,?,?,?,?)"
            values=(invoiceQualityId,CostShareCheck,CostShareDiff,createdBy,createdDate,isactive,TestMethodCheck,TestMethodDiff,TestNameCheck,TestNameDiff,VesselNameCheck,VesselNameDiff,invoiceId)  
            try:
                cursor.execute(insert_sql,values)
                conn.commit()
                print('Record Inserted')
            except Exception as e:
                print('Error In INsertion of Invoice',invoiceId)
                print(f"ExceptionCaught {str(e)}")    
    elif d1.empty!=True and d2.empty==True:
        for index1,rows1 in d1.iterrows():
            isactive=0
            invoicemethod,invoicetest=rows['TestMethod'],rows['TestName']
            invoiceVesselName,invoiceCostShare=rows['VesselName'],rows['CostShare']
            invoiceQualityId=rows['InvoiceQualityId']
            VesselNameCheck=False
            VesselNameDiff='Data Not Found Nomination'
            TestMethodCheck=False
            TestNameCheck=False
            TestMethodDiff='Data Not Found Nomination'
            TestNameDiff='Data Not Found Nomination'
            CostShareCheck=False
            CostShareDiff='Data Not Found Nomination'
            total+=1
            
            d1.drop(index1,inplace=True)
            isactive=1
            insert_sql=f"Insert Into InvoiceQuality_Validation (InvoiceQualityId,CostShareQlyCheck,CostShareQlyDiffReason,CreatedBy,CreatedDate,IsActive,TestCodeCheck,TestCodeDiffReason,TestNameCheck,TestNameDiffReason,VesselNameQlyCheck,VesselNameQlyDiffReason,InvoiceId) Values(?,?,?,?,?,?,?,?,?,?,?,?,?)"
            values=(invoiceQualityId,CostShareCheck,CostShareDiff,createdBy,createdDate,isactive,TestMethodCheck,TestMethodDiff,TestNameCheck,TestNameDiff,VesselNameCheck,VesselNameDiff,invoiceId)  
            try:
                cursor.execute(insert_sql,values)
                conn.commit()
                print('Record Inserted')
            except Exception as e:
                print('Error In INsertion of Invoice',invoiceId)
                print(f'Error in Inserting:{str(e)}')
    return total
    

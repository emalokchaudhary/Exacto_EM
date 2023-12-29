import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import datetime
import numpy as np
import warnings
import re

warnings.filterwarnings("ignore")

def InspectionQuality_Validation(invoiceId,nominationDetailId,conn):
    createdBy=2
    createdDate=datetime.datetime.now()
    isactive=0
    VesselNameCheck=''
    VesselNameDiff=''
    TestNameCheck=''
    TestNameDiff=''
    TestMethodCheck=''
    TestMethodDiff=''
    CreatedBy=2
    totalError=0
    cursor=conn.cursor()
    createdDate=datetime.datetime.now()
    InspectionHeader=pd.read_sql(f"Select * From InspectionHeader_External where InvoiceId='{invoiceId}'",conn)
    if InspectionHeader.empty==True:
        isactive=1
        TestMethodCheck,TestNameCheck,VesselNameCheck=False
        InspectionQualityId,TestMethodDiff,TestNameDiff,VesselNameDiff='Inspection is Empty'
        insert_sql=f"Insert Into InspectionQuality_Validation (InspectionQualityId,CreatedBy,CreatedDate,IsActive,TestCodeCheck,TestCodeDiffCheck,TestNameCheck,TestNameDiffReason,VesselNameQlyCheck,VesselNameQlyDiffReason) Values(?,?,?,?,?,?,?,?,?,?)"
        values=(InspectionQualityId,createdBy,createdDate,isactive,TestMethodCheck,TestMethodDiff,TestNameCheck,TestNameDiff,VesselNameCheck,VesselNameDiff)  
        try:
            cursor.execute(insert_sql,values)
            conn.commit()   
            print('Record Inserted')
        except Exception as e:
            print('Error In INsertion of Invoice',invoiceId)
            print(f'Error in Inserting:{str(e)}')
        return 1
    else:
        
        InspectionId=InspectionHeader['InspectionId'][0]
      
    isactive=0
    InspectionQualityItems=pd.read_sql(f"Select * From InspectionQuality_External where InspectionId='{InspectionId}'",conn)
    NominationQualityItems=pd.read_sql(f"Select * From NominationQuality_External where NominationDetailId='{nominationDetailId}'",conn)
    d1=pd.DataFrame({'InspectionQualityId':InspectionQualityItems['InspectionQualityId'],'TestMethod':InspectionQualityItems['TestMethod'],'TestName':InspectionQualityItems['TestName'],'VesselName':InspectionQualityItems['VesselName']})
    d2=pd.DataFrame({'TestMethod':NominationQualityItems['TestMethod'],'TestName':NominationQualityItems['TestName'],'VesselName':NominationQualityItems['VesselName']})
    
    topValue=80
    smallValue=45
    if d1.empty!=True and d2.empty!=True:
        for index,rows in d1.iterrows():
            isactive=0
            invoicemethod,invoicetest=rows['TestMethod'],rows['TestName']
            invoiceVesselName,InspectionQualityId=rows['VesselName'],rows['InspectionQualityId']
            for index1,rows1 in d2.iterrows():
                nomimethod,nomitest=rows1['TestMethod'],rows1['TestName']
                nominationVesselName=rows1['VesselName']
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
                        ratio=fuzz.partial_token_set_ratio(invoiceVesselName,nominationVesselName)
                        if ratio>89:
                            VesselNameCheck=True
                            VesselNameDiff='VesselName Matched'
                        else:
                            if invoiceVesselName==None:
                                 VesselNameCheck=True
                                 VesselNameDiff='VesselName Not Found In Invoice'

                                 print('InvoiceVeselCalled')
                            else:
                                if nominationVesselName==None:
                                    VesselNameCheck=False
                                    VesselNameDiff='VeselName Not Found In Nomination'
                                    isactive+=1
                                    totalError+=1
                                    print('NominationVesselCalled')
                                else:
                                    VesselNameCheck=False
                                    isactive+=1
                                    VesselNameDiff='VesselName Not Matched'
                                    totalError+=1
                                    print('Not Matched Called')
                        
                        TestNameCheck=True
                        TestMethodCheck=True
                        TestMethodDiff='Matched'
                        TestNameDiff='Matched'
                        d2.drop(index1,inplace=True)
                        d1.drop(index,inplace=True)
                        break
            else:
                VesselNameCheck=False
                VesselNameDiff='Data Not Found Nomination'
                TestNameCheck=False
                TestMethodCheck=False
                TestMethodDiff='Data Not Found Nomination'
                TestNameDiff='Data Not Found Nomination'
                totalError+=1
                isactive+=1
                d1.drop(index,inplace=True) 
            if isactive>0:
                isactive=1
            else:
                isactive=0
            print('This is isactive',isactive)
            print(VesselNameDiff)
            print()
            insert_sql=f"Insert Into InspectionQuality_Validation (InspectionQualityId,CreatedBy,CreatedDate,IsActive,TestCodeCheck,TestCodeDiffCheck,TestNameCheck,TestNameDiffReason,VesselNameQlyCheck,VesselNameQlyDiffReason) Values(?,?,?,?,?,?,?,?,?,?)"
            values=(InspectionQualityId,createdBy,createdDate,isactive,TestMethodCheck,TestMethodDiff,TestNameCheck,TestNameDiff,VesselNameCheck,VesselNameDiff)  
            try:
                cursor.execute(insert_sql,values)
                conn.commit()
                print("Record Inserted")
            except Exception as e:
                print('Error In INsertion of Invoice',invoiceId)
                print(f'Error in Inserting:{str(e)}')
    
    elif d1.empty!=True and d2.empty==True:
        for index1,rows1 in d1.iterrows():
            invoicemethod,invoicetest=rows['TestMethod'],rows['TestName']
            invoiceVesselName,InspectionQualityId=rows['VesselName'],rows['InspectionQualityId']
            VesselNameCheck=False
            VesselNameDiff='Nomination Empty'
            TestMethodCheck=False
            TestNameCheck=False
            TestMethodDiff='Nomination Empty'
            TestNameDiff='Nomination Empty'
            CostShareCheck=False
            CostShareDiff='Nomination Empty'
            totalError+=1
            isactive=1
            d1.drop(index1,inplace=True)
            insert_sql=f"Insert Into InspectionQuality_Validation (InspectionQualityId,CreatedBy,CreatedDate,IsActive,TestCodeCheck,TestCodeDiffCheck,TestNameCheck,TestNameDiffReason,VesselNameQlyCheck,VesselNameQlyDiffReason) Values(?,?,?,?,?,?,?,?,?,?)"
            values=(InspectionQualityId,createdBy,createdDate,isactive,TestMethodCheck,TestMethodDiff,TestNameCheck,TestNameDiff,VesselNameCheck,VesselNameDiff)  
            try:
                cursor.execute(insert_sql,values)
                conn.commit()
                print('Record Inserted')
            except Exception as e:
                print('Error In INsertion of Invoice')
                print(f'Error in Inserting:{str(e)}')
    return totalError

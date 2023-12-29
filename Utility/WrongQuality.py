from connection import connect_db
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import numpy as np
import datetime
import warnings
warnings.filterwarnings('ignore')
def WrongQualityService(NominationQualityItems,NominationQuantityItems,InspectionQualityItems,InspectionQuantityItems,conn,r1):
    
    count=0
    Services=0
    cursor=conn.cursor()
    currentDate=datetime.datetime.now()
    error=[]
    createdBy=2
    r2=r1
    r2=int(r1)
    nominationList={}
    inspectionList={}
    for index4,row4 in InspectionQuantityItems.iterrows():
            # NominationQualityId = row2['NominationQualityId']
            # InspectionQualityId = row3['InspectionQualityId']
            InspectionQuantityId = row4['InspectionQuantityId']
            InspectionQuantityUOMItems=pd.read_sql(f"Select * From InspectionQuantityUoM_External where InspectionQuantityId={InspectionQuantityId}",conn)

            if (NominationQuantityItems.empty!=True and (NominationQuantityItems['VesselName'].empty!=True or NominationQuantityItems['ProductName'].empty!=True)):
                nominationList['Quantity']=True
            if (NominationQuantityItems.empty!=True and(NominationQualityItems['TestMethod'].empty!=True or NominationQualityItems['TestName'].empty!=True)):
                nominationList['Quality']=True
            if (InspectionQualityItems.empty!=True and (InspectionQualityItems['TestName'].empty!=True or InspectionQualityItems['TestMethod'].empty!=True)):
                inspectionList['Quality']=True
            if (InspectionQuantityUOMItems.empty!=True and (InspectionQuantityUOMItems['InspectedQuantity'].empty!=True)):
                inspectionList['Quantity']=True
    
    count = 0
    Services = len(inspectionList)
    nominationData=''
    inspectionData=''
    outcome = 0
    for i in nominationList.keys():
        nominationData+=i
        nominationData+='  '
    for i in inspectionList.keys():
        inspectionData+=i
        inspectionData+=" "
    missingInspection=set(inspectionList.keys())-set(nominationList.keys())

    missingNomination=set(nominationList.keys())-set(inspectionList.keys())

    if len(inspectionList)==0 and len(nominationList)==0:

        print("Data not found in both")
        count += 1
        outcome = 12

    elif len(missingInspection)==0 and len(missingNomination)==0:

        print('All Values are present')
        
        outcome=9

    elif len(missingInspection)==0 and len(missingNomination)>0:

        a = list(missingNomination)[0] +' is missing in Inspection'
        print(a)
        count +=1
        if a == 'Quatity is missing in Inspection':
            outcome = 10
        if a == 'Quality is missing in Inspection':
            outcome = 10        

    elif len(missingNomination)==0 and len(missingInspection)>0:

        print(list(missingInspection)[0],'is missing in Nomination')
        outcome=27
        count+=1

               
    # currencyInvoice=pd.read_sql(f"Select Currency from InvoiceHeader_External where rowID={r1}",conn)
    # if currencyInvoice.empty!=True:
    #     currencyInvoice=str(currencyInvoice['Currency'][0])
    # else:
    #     currencyInvoice=None
        
        
    r2=r1
    r2=int(r1)
    insert_sql="Insert Into UtilityWrongServiceQuality_External(InvoiceId,NominationService,InspectionService,ServiceOutcome,CreatedBy,CreatedDate) VALUES(?,?,?,?,?,?)"
    values_insert=(r2,nominationData,inspectionData,outcome,createdBy,currentDate)
    try:
        cursor.execute(insert_sql,values_insert)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}')
    # print(outcome,'\n',count,'\n@@@@\n',Services)
    return count,Services

def WrongQualityTest(NominationQualityItems,InspectionQualityItems,conn,r1):
    count=0
    # invoiceqlt = pd.read_sql

    d1=pd.DataFrame({'TestMethod':NominationQualityItems['TestMethod'],'TestName':NominationQualityItems['TestName'],'Comments':NominationQualityItems['Comments'],'NominationQualityId':NominationQualityItems['NominationQualityId']})
    d2=pd.DataFrame({'TestMethod':InspectionQualityItems['TestMethod'],'TestName':InspectionQualityItems['TestName'],'InspectionQualityId':InspectionQualityItems['InspectionQualityId']})
    a=[]
    r2=int(r1)
    totalTests=len(d1['TestMethod'])
    outcome=0
    CreatedBy=2
    cursor=conn.cursor()
    currentDate=datetime.datetime.now()
    topValue=80
    smallValue=60
    if d1.empty!=True and d2.empty!=True:
        for index,rows in d1.iterrows():
            method,test,comments,NominationQualityId=rows['TestMethod'],rows['TestName'],rows['Comments'],rows['NominationQualityId']
            # invoicequantity=rows['QuantityValue']
            # invoicetotalunitPrice=rows['UnitPrice']
            # invoiceunitPrice=invoicetotalunitPrice/invoicequantity
            for index1,rows1 in d2.iterrows():
                smethod,stest,InspectionQualityId=rows1['TestMethod'],rows1['TestName'],rows1['InspectionQualityId']
                m=fuzz.token_set_ratio(test,stest)
                n=fuzz.token_set_ratio(method,smethod)
                if n>topValue or m>smallValue:
                        NominationMethod=method
                        InspectionMethod=smethod
                        Nominationcomments = comments                    
                        NominationTest=test
                        InspectionTest=test
                        outcome=1
                        d2.drop(index1,inplace=True)
                        d1.drop(index,inplace=True)
                        print('R1')
                        insert_sql="Insert Into UtilityWrongTestQuality_External(InspectionQualityId,NominationQualityId,CreatedBy,CreatedDate,NominationTestCode,NominationTestName,TestCodeComments,InspectionTestCode,InspectionTestName,TestCheckOutcome,InvoiceId) VALUES(?,?,?,?,?,?,?,?,?,?,?)"
                        values_insert=(int(InspectionQualityId),int(NominationQualityId),CreatedBy,currentDate,NominationMethod,NominationTest,Nominationcomments,InspectionMethod,InspectionTest,outcome,r2)
                        try:
                            cursor.execute(insert_sql,values_insert)
                            conn.commit()
                            print('Record Inserted')
                            print(' TestName',NominationTest,'of InvoiceId',r2)
                        except Exception as e:
                            print(f'Error in Inserting:{str(e)}')
                            print('Test Failed to upload')

                        break
            else:
                a.append([test,method])
                NominationTest=test
                NominationMethod=method
                Nominationcomments = comments
                NominationQualityId = NominationQualityId
                InspectionTest='Data Not Found in Inspection'
                InspectionMethod='Data Not Found in Inspection'
                # InspectionQualityId = None
                outcome=4
                count+=1
                d1.drop(index,inplace=True)
                print('R2')
                insert_sql="Insert Into UtilityWrongTestQuality_External(NominationQualityId,CreatedBy,CreatedDate,NominationTestCode,NominationTestName,TestCodeComments,InspectionTestCode,InspectionTestName,TestCheckOutcome,InvoiceId) VALUES(?,?,?,?,?,?,?,?,?,?)"
                values_insert=(int(NominationQualityId),CreatedBy,currentDate,NominationMethod,NominationTest,Nominationcomments,InspectionMethod,InspectionTest,outcome,r2)
                try:
                    cursor.execute(insert_sql,values_insert)
                    conn.commit()
                    print('Record Inserted')
                    print('Test Name Not Found in Inspection',r2)
                except Exception as e:
                    print(f'Error in Inserting:{str(e)}')
    elif d1.empty==True and d2.empty!=True:
        insert_sql="Insert Into UtilityWrongTestQuality_External(InspectionQuantityId,CreatedBy,CreatedDate,TestCodeInvoice,TestNameInvoice,TestCodeInspection,TestNameInspection,TestCheckOutcome,InvoiceId) VALUES(?,?,?,?,?,?,?,?,?,?)"
        for index1,rows1 in d2.iterrows():
            InspectionMethod,InspectionTest,InspectionQualityId=rows1['TestMethod'],rows1['TestName'],rows1['InspectionQualityId']
            NominationTest='Data Not Found in Nomiantion'
            NominationMethod='Data Not Found in Nomiantion'
            Nominationcomments = 'Data Not found in Nomination'
            outcome=6
            values_insert=(int(InspectionQualityId),CreatedBy,currentDate,NominationMethod,NominationTest,InspectionMethod,InspectionTest,outcome,r2)
            try:
                cursor.execute(insert_sql,values_insert)
                conn.commit()
                print('Record Inserted')
                print('Test Not found In Invoice ',r2)
            except Exception as e:
                print(f'Error in Inserting: {str(e)}')
    elif d1.empty!=True and d2.empty==True:
        insert_sql="Insert Into UtilityWrongTestQuality_External(NominationQualityId,CreatedBy,CreatedDate,NominationTestCode,NominationTestName,TestCodeComments,InspectionTestCode,InspectionTestName,TestCheckOutcome,InvoiceId) VALUES(?,?,?,?,?,?,?,?,?,?)"
        for index1,rows1 in d1.iterrows():
            NominationMethod,NominationTest,Nominationcomments,NominationQualityId=rows1['TestMethod'],rows1['TestName'],rows1['Comments'],rows1['NominationQualityId']
            InspectionTest='Data Not Found in Inspection'
            InspectionMethod='Data Not Found in Inspection' 
            outcome=4
            count+=1
            values_insert=(int(NominationQualityId),CreatedBy,currentDate,NominationMethod,NominationTest,Nominationcomments,InspectionMethod,InspectionTest,outcome,r2)
            d1.drop(index1,inplace=True)
            try:
                cursor.execute(insert_sql,values_insert)
                conn.commit()
                print('Record Inserted')
                print('Test Not in INspection',r2)
            except Exception as e:
                print(f'Error in Inserting: {str(e)}')
    else:
        outcome=6
        NominationMethod='Data Not Found'
        InspectionMethod='Data Not Found'
        Nominationcomments = 'Data Not Found'
        NominationTest='Data Not Found'
        InspectionTest='Data Not Found'
        count=1 
    return count,totalTests



conn=connect_db()
# data1=pd.read_sql('Select  RowId,NominationDetailId,JobDate,Location,Vendor from InvoiceHeader_External where Status=53',conn)
# # print(data1)
# for index,rows in data1.iterrows():
#     r1=rows['RowId']
#     r2=r1
#     r2=int(r1)
#     print('This is mainINvoice of ID',r2)
#     n1=rows['NominationDetailId']
#     if np.isnan(n1):
#         break    
#     n2=int(n1)
#     NominationQuantityItems=pd.read_sql(f"Select * From NominationQuantity_External where NominationDetailId={n2}",conn)
#     InspectionHeaderItems=pd.read_sql(f"Select * From InspectionHeader_External where InvoiceId={r2}",conn)
#     # print('This is for InvoiceId',r1)
#     InvoiceQlt = pd.read_sql(f"select InvoiceQualityId from InvoiceQuality_External where InvoiceId={r2}",conn)
#     for index,row in InvoiceQlt.iterrows():
#         for index1,row1 in InspectionHeaderItems.iterrows():
#             InvoiceQualityId = row['InvoiceQualityId']
#             l1 = row1['InspectionId']
#             l2 = l1
#             l2 = int(l1)
#             NominationQualityItems=pd.read_sql(f"Select * From NominationQuality_External where NominationDetailId={n2}",conn)
#             InspectionQuantityItems=pd.read_sql(f"Select * From InspectionQuantity_External where InspectionId={l2}",conn)
#             InspectionQualityItems=pd.read_sql(f"Select * From InspectionQuality_External where InspectionId={l2}",conn)
#             print(NominationQualityItems)
            
#             for index4,row4 in InspectionQuantityItems.iterrows():
#                 # NominationQualityId = row2['NominationQualityId']
#                 # InspectionQualityId = row3['InspectionQualityId']
#                 InspectionQuantityId = row4['InspectionQuantityId']
#                 InspectionQuantityUOMItems=pd.read_sql(f"Select * From InspectionQuantityUoM_External where InspectionQuantityId={InspectionQuantityId}",conn)
#                 # WrongQualityService(NominationQualityItems,NominationQuantityItems,InspectionQualityItems,InspectionQuantityItems,InspectionQuantityUOMItems,conn,r1)
#                 # print('Wrong Service')
#                 # print(NominationQualityId)
#                 WrongQualityTest(NominationQualityItems,InspectionQualityItems,InvoiceQualityId,conn,r1)
#                 print('Wrong Test')

def WrongQualityTestLeakage(InvoiceId,NominationDetailId,conn):

    InspectionHeaderItems=pd.read_sql(f"Select * From InspectionHeader_External where InvoiceId={InvoiceId}",conn)
    if InspectionHeaderItems.empty!=True:
        InspectionId = InspectionHeaderItems['InspectionId'][0]
    else:
        InspectionId = 0

    NominationQualityItems=pd.read_sql(f"Select * From NominationQuality_External where NominationDetailId={NominationDetailId}",conn)
    InspectionQuantityItems=pd.read_sql(f"Select * From InspectionQuantity_External where InspectionId={InspectionId}",conn)
    InspectionQualityItems=pd.read_sql(f"Select * From InspectionQuality_External where InspectionId={InspectionId}",conn)
    # InvoiceQlt = pd.read_sql(f"select InvoiceQualityId from InvoiceQuality_External where InvoiceId={InvoiceId}",conn)

    # print(InvoiceQlt)
    WrongQualityTest(NominationQualityItems,InspectionQualityItems,conn,r1)
    print('Wrong Test')


def wrongQualityServiceLeakage(InvoiceId,NominationDetailId,conn):
    NominationQuantityItems=pd.read_sql(f"Select * From NominationQuantity_External where NominationDetailId={n2}",conn)
    InspectionHeaderItems=pd.read_sql(f"Select * From InspectionHeader_External where InvoiceId={r2}",conn)
    # print('This is for InvoiceId',r1)
    # InvoiceQlt = pd.read_sql(f"select InvoiceQualityId from InvoiceQuality_External where InvoiceId={r2}",conn)
    for index1,row1 in InspectionHeaderItems.iterrows():
        l1 = row1['InspectionId']
        l2 = l1
        l2 = int(l1)
        NominationQualityItems=pd.read_sql(f"Select * From NominationQuality_External where NominationDetailId={NominationDetailId}",conn)
        InspectionQuantityItems=pd.read_sql(f"Select * From InspectionQuantity_External where InspectionId={l2}",conn)
        InspectionQualityItems=pd.read_sql(f"Select * From InspectionQuality_External where InspectionId={l2}",conn)
        # print(NominationQualityItems)
        WrongQualityService(NominationQualityItems,NominationQuantityItems,InspectionQualityItems,InspectionQuantityItems,conn,r1)


data1=pd.read_sql('Select  RowId,NominationDetailId,JobDate,Location,Vendor from InvoiceHeader_External where Status=53',conn)
# print(data1)
for index,rows in data1.iterrows():
    r1=rows['RowId']
    r2=r1
    r2=int(r1)
    print('This is mainINvoice of ID',r2)
    n1=rows['NominationDetailId']
    if np.isnan(n1):
        break    
    n2=int(n1)

    WrongQualityTestLeakage(r2,n2,conn)
    wrongQualityServiceLeakage(r2,n2,conn)



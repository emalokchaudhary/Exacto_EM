
from connection import connect_db
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import datetime
import numpy as np
import warnings
warnings.filterwarnings("ignore")
def CurrencyMatch(invoiceId,conn):
    cursor=conn.cursor()
    totalCurrency=1
    currencyOutcomeId=0
    count=0
    currencyInvoice=pd.read_sql(f"Select Currency from InvoiceHeader_External where rowID={invoiceId}",conn)
    if currencyInvoice.empty!=True:
        currencyInvoice=str(currencyInvoice['Currency'][0])
        print(currencyInvoice)
    else:
        print(currencyInvoice)
        currencyOutcomeId=3
        currencyInvoice='Currency Field Missing in Invoice'
        insert_sql=f"Update UtilityInvoiceLeakage_External Set CurrencyOutcomeId=? where InvoiceId=?"
        values=(currencyOutcomeId,invoiceId)
        try:
            cursor.execute(insert_sql,values)
            conn.commit()
            print('Record Inserted')
        

        except Exception as e:
            print(f'Error in Inserting:{str(e)}')
        return 1
    GICCurrency=None
    CurrencyGIC=pd.read_sql(f"Select description,Symbol,CurrencyCode from CurrencyMaster",conn)
    for index,rows in CurrencyGIC.iterrows():
        if currencyInvoice==rows['description'] or currencyInvoice==rows['Symbol'] or currencyInvoice==rows['CurrencyCode']:
            print(currencyInvoice,'------',rows['description'])
            GICCurrency=currencyInvoice
            
            currencyOutcomeId=1
            count=0
            break
        else:
            
            currencyOutcomeId=6
            count+=1 
            
    insert_sql=f"Update UtilityInvoiceLeakage_External Set CurrencyGIC=?,CurrencyOutcomeId=? where InvoiceId=?"
    values=(GICCurrency,currencyOutcomeId,invoiceId)
    try:
        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
        
    except Exception as e:
        print(f'Error in Inserting:{str(e)}')
    return count

def serviceRecieved(invoiceId,nominationDetailId,conn):
    cursor=conn.cursor()
    inspectionQualityItems=''
    createdBy=2
    currentDate=datetime.datetime.now()
    inspectionQuantityItems=''
    invoiceList={}
    inspectionList={}
    invoiceQuantityItems=pd.read_sql(f"Select * From InvoiceQuantity_External where InvoiceId={invoiceId}",conn)
    invoiceQualityItems=pd.read_sql(f"Select * From InvoiceQuality_External where InvoiceId={invoiceId}",conn)
    inspectionId=pd.read_sql(f"Select InspectionId From InspectionHeader_External where InvoiceId={invoiceId}",conn)
    if inspectionId['InspectionId'].empty==True :
        inspectionQualityItems=None
        inspectionQuantityItems=None
    
        if (invoiceQuantityItems.empty!=True and (invoiceQuantityItems['Description'].empty!=True or invoiceQuantityItems['QuantityValue'].empty!=True)):
            invoiceList['Quantity']=True
        if (invoiceQualityItems.empty!=True and(invoiceQualityItems['TestMethod'].empty!=True or invoiceQualityItems['TestName'].empty!=True)):
            invoiceList['Quality']=True
    else:
        inspectionId=inspectionId['InspectionId'][0]
        inspectionQuantityItems=pd.read_sql(f"Select * From InspectionQuantity_External where InspectionId={inspectionId}",conn)
        inspectionQualityItems=pd.read_sql(f"Select * From InspectionQuality_External where InspectionId={inspectionId}",conn)
        if (invoiceQuantityItems.empty!=True and (invoiceQuantityItems['Description'].empty!=True or invoiceQuantityItems['QuantityValue'].empty!=True)):
            invoiceList['Quantity']=True
        if (invoiceQualityItems.empty!=True and(invoiceQualityItems['TestMethod'].empty!=True or invoiceQualityItems['TestName'].empty!=True)):
            invoiceList['Quality']=True
        if (inspectionQualityItems.empty!=True and (inspectionQualityItems['TestName'].empty!=True or inspectionQualityItems['TestMethod'].empty!=True)):
            inspectionList['Quality']=True
        if (inspectionQuantityItems.empty!=True):
            inspectionList['Quantity']=True
    invoiceData=''
    inspectionData=''
    count=0
    for i in invoiceList.keys():
        invoiceData+=i
        invoiceData+='  '
    for i in inspectionList.keys():
        inspectionData+=i
        inspectionData+=" "
    Services=len(invoiceList)
    
    if len(invoiceList)==0 and len(inspectionList)==0:
        outcomeId=5   
        count+=1

    else:
        missingKey=[key for key in invoiceList if key not in inspectionList]        
        
        if len(missingKey)==0:
            outcomeId=1 
            count=0           
        else:
            for i in missingKey:
                count+=1
                if i=='Quantity':
                    outcomeId=7
                elif i=='Quality':
                    outcomeId=8
                
    print('This is invoiceList',invoiceList)
    print('This is inspectionList',inspectionList)
     
    print('THis is count',count)       
    currencyInvoice=pd.read_sql(f"Select Currency from InvoiceHeader_External where rowID={invoiceId}",conn)
    if currencyInvoice.empty!=True:
        currencyInvoice=str(currencyInvoice['Currency'][0])
    else:
        currencyInvoice=None
        
    insert_sql="Insert Into UtilityInvoiceLeakage_External(InvoiceId,ServicesInvoice,ServicesInspection,CreatedBy,CreatedDate,CurrencyInvoice,ServiceOutcomeId) VALUES(?,?,?,?,?,?,?)"
    values_insert=(invoiceId,invoiceData,inspectionData,createdBy,currentDate,currencyInvoice,outcomeId)
    try:
        cursor.execute(insert_sql,values_insert)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}')
    return count,Services

def serviceTestCheck(invoiceId,conn):
    invoiceQualityItems=pd.read_sql(f"Select * from InvoiceQuality_External where InvoiceId={invoiceId} ",conn)
    inspectionId=pd.read_sql(f"Select InspectionId from InspectionHeader_External  where InvoiceId={invoiceId}",conn)
    if inspectionId.empty!=True:
        inspectionId=inspectionId['InspectionId'][0]
    else:
        inspectionId=0
    inspectionQualityItems=pd.read_sql(f"Select * From InspectionQuality_External where InspectionId={inspectionId}",conn)
    count=0
    d1=pd.DataFrame({'TestMethod':invoiceQualityItems['TestMethod'],'TestName':invoiceQualityItems['TestName'],'QuantityValue':invoiceQualityItems['QuantityValue'],'UnitPrice':invoiceQualityItems['UnitPrice']})
    d2=pd.DataFrame({'TestMethod':inspectionQualityItems['TestMethod'],'TestName':inspectionQualityItems['TestName']})
    a=[]
    totalTests=len(d1['TestMethod'])
    insert_sql="Insert Into UtilityTestLeakage_External(CreatedBy,CreatedDate,TestCodeInvoice,TestNameInvoice,TestCodeInspection,TestNameInspection,InvoiceId,InvoiceQuantity,UnitPriceInvoice,InspectionOutcomeId) VALUES(?,?,?,?,?,?,?,?,?,?)"
    outcome=''
    outcomeId=0
    CreatedBy=2
    cursor=conn.cursor()
    currentDate=datetime.datetime.now()
    topValue=80
    smallValue=45
    if d1.empty!=True and d2.empty!=True:
        for index,rows in d1.iterrows():
            method,test=rows['TestMethod'],rows['TestName']
            invoicequantity=rows['QuantityValue']
            invoicetotalunitPrice=rows['UnitPrice']
            invoiceunitPrice=invoicetotalunitPrice/invoicequantity
            for index1,rows1 in d2.iterrows():
                smethod,stest=rows1['TestMethod'],rows1['TestName']
                m=fuzz.token_set_ratio(test,stest)
                n=fuzz.token_set_ratio(method,smethod)
                if n>topValue or m>smallValue:
                        InvoiceMethod=method
                        InspectionMethod=smethod                    
                        InvoiceTest=test
                        InspectionTest=stest
                    
                        outcomeId=1
                        d2.drop(index1,inplace=True)
                        d1.drop(index,inplace=True)
                        
                        values_insert=(CreatedBy,currentDate,InvoiceMethod,InvoiceTest,InspectionMethod,InspectionTest,invoiceId,invoicequantity,invoiceunitPrice,outcomeId)
                        try:
                            cursor.execute(insert_sql,values_insert)
                            conn.commit()
                            print('Record Inserted')
                            print(' TestName',InvoiceTest,'of InvoiceId',invoiceId)
                        except Exception as e:
                            print(f'Error in Inserting:{str(e)}')
                            print('Test Failed to upload')

                        break
            else:
                a.append([test,method])
                InvoiceTest=test
                InvoiceMethod=method
                InspectionTest='Data not Found in Inspection'
                InspectionMethod='Data not Found in Inspection'
                
                outcomeId=4
                count+=1
                d1.drop(index,inplace=True)
                insert_sql="Insert Into UtilityTestLeakage_External(CreatedBy,CreatedDate,TestCodeInvoice,TestNameInvoice,TestCodeInspection,TestNameInspection,InvoiceId,InvoiceQuantity,UnitPriceInvoice,InspectionOutcomeId) VALUES(?,?,?,?,?,?,?,?,?,?)"
                values_insert=(CreatedBy,currentDate,InvoiceMethod,InvoiceTest,InspectionMethod,InspectionTest,invoiceId,invoicequantity,invoiceunitPrice,outcomeId)
                try:
                    cursor.execute(insert_sql,values_insert)
                    conn.commit()
                    print('Record Inserted')
                    print('Test Name Not Found in Inspection',invoiceId)
                except Exception as e:
                    print(f'Error in Inserting:{str(e)}')
    elif d1.empty==True and d2.empty!=True:
        insert_sql="Insert Into UtilityTestLeakage_External(CreatedBy,CreatedDate,TestCodeInvoice,TestNameInvoice,TestCodeInspection,TestNameInspection,InvoiceId,InspectionOutcomeId) VALUES(?,?,?,?,?,?,?,?)"
        for index1,rows1 in d2.iterrows():
            InspectionMethod,InspectionTest=rows1['TestMethod'],rows1['TestName']
            InvoiceTest='Data not Found in Invoice'
            InvoiceMethod='Data not Found in Invoice'
            outcomeId=5
            values_insert=(CreatedBy,currentDate,InvoiceMethod,InvoiceTest,InspectionMethod,InspectionTest,invoiceId,outcomeId)
            try:
                cursor.execute(insert_sql,values_insert)
                conn.commit()
                print('Record Inserted')
                print('Test Not found In Invoice ',invoiceId)
            except Exception as e:
                print(f'Error in Inserting: {str(e)}')
            d2.drop(inplace=True,index=index1)
            break
    elif d1.empty!=True and d2.empty==True:
        insert_sql="Insert Into UtilityTestLeakage_External(CreatedBy,CreatedDate,TestCodeInvoice,TestNameInvoice,TestCodeInspection,TestNameInspection,InvoiceId,InvoiceQuantity,UnitPriceInvoice,InspectionOutcomeId) VALUES(?,?,?,?,?,?,?,?,?,?)"
        for index1,rows1 in d1.iterrows():
            InvoiceMethod,InvoiceTest=rows1['TestMethod'],rows1['TestName']
            invoicequantity=rows1['QuantityValue']
            invoicetotalunitPrice=rows1['UnitPrice']
            invoiceunitPrice=invoicetotalunitPrice/invoicequantity
            InspectionTest='Data Not Found in Inspection'
            InspectionMethod='Data Not Found in Inspection' 
            outcomeId=4
            count+=1
            values_insert=(CreatedBy,currentDate,InvoiceMethod,InvoiceTest,InspectionMethod,InspectionTest,invoiceId,invoicequantity,invoiceunitPrice,outcomeId)
            d1.drop(index1,inplace=True)
            try:
                cursor.execute(insert_sql,values_insert)
                conn.commit()
                print('Record Inserted')
                print('Test Not in INspection',invoiceId)
            except Exception as e:
                print(f'Error in Inserting: {str(e)}')
    else:
        outcome='Data Not Found'
        InvoiceMethod='Data Not Found'
        InspectionMethod='Data Not Found'
        InvoiceTest='Data Not Found'
        InspectionTest='Data Not Found'
        count=1
    return count
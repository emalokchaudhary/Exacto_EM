from connection import connect_db
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import numpy as np
import datetime
import warnings
warnings.filterwarnings('ignore')
conn=connect_db()
def wrongPriceQuality(invoiceId,nominationDetailId,conn): 
    CreatedBy=2
    cursor=conn.cursor()
    GICTestOutcomeId=0
    count=0
    createdDate=datetime.datetime.now()
    print(invoiceId,'----',nominationDetailId)
    values=0
    NominationHeader=pd.read_sql(f"Select * from NominationDetails_External where NominationDetailId='{nominationDetailId}'",con=conn)
    InvoiceQualityItems=pd.read_sql(f"Select * From InvoiceQuality_External where InvoiceId='{invoiceId}'",conn)
    invoicepdtName=pd.read_sql(f"Select ProductName from InvoiceQuantity_External where InvoiceId='{invoiceId}' ",conn)
    invoiceHeader=pd.read_sql(f"Select * From InvoiceHeader_External where RowID='{invoiceId}'",conn)
    jobdate=invoiceHeader['JobDate'][0]
    vendor=invoiceHeader['Vendor']
    jobdate=invoiceHeader['JobDate'][0]
    location=NominationHeader['Location']
    if location.empty!=True:
        location=str(location[0])
    # print('THis is location',location)
    locationId=NominationHeader['LocationId']
    if  locationId[0]==None:
        LocationMasterTable=pd.read_sql(f"Select * From LocationMaster",conn)
        for lindex,lrows in LocationMasterTable.iterrows():
            ratio=70
            locationMaster=lrows['description']
            fuzzRatio=fuzz.partial_ratio(location.lower(),locationMaster.lower())
            if fuzzRatio>ratio:
                locationId=lrows['RowId']
                locationId=int(locationId)
                # print(locationId)
                
        else:
            locationId=52
    else:
        locationId=int(locationId[0]) 
    vendorId=invoiceHeader['VendorId']
    if vendorId.empty==True:
        VendorList=pd.read_sql(f"Select * from VendorMaster",conn)
        for index,rows in VendorList.iterrows():
            x=fuzz.token_set_ratio(rows['description'],vendor)
            if x>80:
                vendorId=rows['RowId']
                break
    else:
        vendorId=vendorId[0]

    for tindex,trows in InvoiceQualityItems.iterrows():
        invoiceTestName=trows['TestName']
        invoiceMethodName=trows['TestMethod']
        invoicetotalUnitPrice=trows['UnitPrice']
        invoiceQuantityValue=trows['QuantityValue']
        uomInvoice=trows['UoM'] 
        invoiceUnitPrice=invoicetotalUnitPrice/invoiceQuantityValue
        uomInvoiceId=trows['UoMId']
        labTestIdInvoice=trows['LabTestId']
        qualityInvoiceId=trows['GICQualityId']
        gic_TestOutcome=''
        totalTests=len(InvoiceQualityItems['TestName'])
        print('Main Test Names',invoiceTestName)
        print(invoiceId,'This is invoiceId of invoice')
        if uomInvoiceId==None:
            uomInvoiceId=pd.read_sql(f"Select RowId from UoMMaster where description='{uomInvoice}'",conn)
            uomInvoiceId=int(uomInvoiceId['RowId'])

        if labTestIdInvoice == None or np.isnan(labTestIdInvoice):
            labTestTable=pd.read_sql(f"Select RowId,description,TestMethod from LabTestMaster",conn)
            for labIndex,labrows in labTestTable.iterrows():
                labTestNameGIC=labrows['description']
                labTestMethodGIC=labrows['TestMethod']
                topValue=80
                smallValue=45
                testMethodRatio=fuzz.partial_ratio(invoiceMethodName,labTestMethodGIC)
                testNameRatio=fuzz.partial_ratio(invoiceTestName,labTestNameGIC)
                if testMethodRatio>=topValue and testNameRatio>=smallValue:
                    testNameGIC=labTestNameGIC
                    testMethodGIC=labTestMethodGIC
                    labTestIdInvoice=labrows['RowId']
                    GICTestOutcomeId=1
                    insert_sql=f"Update  UtilityTestLeakage_External Set TestNameGIC=?,TestCodeGIC=?,GICTestOutcomeId=? where  TestNameInvoice=? and UnitPriceInvoice=?"
                    values=(testNameGIC,testMethodGIC,GICTestOutcomeId,invoiceTestName,invoiceUnitPrice)
                    #Test Insertion
                    try:
                        cursor.execute(insert_sql,values)
                        conn.commit()
                        print('Record Inserted')
                        print('Updated the Test Value')
                    except Exception as e:
                        print(f'Error in Inserting:{str(e)}')
                        print("Error In Updating Test Value")
                
                    break
            
            
            else:            
                testNameGIC='Data Not Found in GIC'
                testMethodGIC='Data Not Found in GIC'
                diffUnitPrice=invoiceUnitPrice
                diffNetPrice=invoicetotalUnitPrice

                GICTestOutcomeId=3
                count+=1

                # print('THis is count Value of count ',count)
                # print('This is test name not found in gic',invoiceTestName)
                insert_sql=f"Update  UtilityTestLeakage_External Set TestNameGIC=?,TestCodeGIC=?,GICTestOutcomeId=?,DifferenceUnitPriceGIC=?,DifferenceNetAmount=? where  TestCodeInvoice=? and UnitPriceInvoice=?"
                values=(testNameGIC,testMethodGIC,GICTestOutcomeId,diffUnitPrice,diffNetPrice,invoiceMethodName,invoiceUnitPrice)
                
                try:
                    cursor.execute(insert_sql,values)
                    conn.commit()
                    print('Record Inserted')
                    print('Updated the Test Value')
                except Exception as e:
                    print(f'Error in Inserting:{str(e)}')
                    print("Error In Updating Test Value")

        elif  labTestIdInvoice!=None:
            # print('These have labTestID')
            # print(invoiceTestName)
            # print('-------------------')
            labTestTable=pd.read_sql(f"Select description,TestMethod from LabTestMaster where RowId={labTestIdInvoice}",conn)
            testNameGIC=labTestTable['description'][0]
            testMethodGIC=labTestTable['TestMethod'][0]
            # print(testMethodGIC,'---------------',testNameGIC)
            
            GICTestOutcomeId=1
            insert_sql=f"Update  UtilityTestLeakage_External Set TestNameGIC=?,TestCodeGIC=?,GICTestOutcomeId=? where  TestCodeInvoice=? and UnitPriceInvoice=?"
            values=(testNameGIC,testMethodGIC,GICTestOutcomeId,invoiceMethodName,invoiceUnitPrice)
            try:
                cursor.execute(insert_sql,values)
                conn.commit()
                print('Record Inserted')
                print('Updated the Test Value')
            except Exception as e:
                print(f'Error in Inserting:{str(e)}')
                print("Error In Updating Test Value")
            
        if qualityInvoiceId==None:
            GICId=pd.read_sql(f"Select GICId from GICHeader_External where ('{jobdate}' between EffectiveFrom and EffectiveTo) and(VendorId={vendorId})and (LocationId ={locationId})  ",conn)
            GICId=GICId['GICId']
            # print('quality')
            if GICId.empty:
                GICTestOutcomeId=3
                insert_sql=f"Update  UtilityTestLeakage_External Set TestNameGIC=?,TestCodeGIC=?,GICTestOutcomeId=?,DifferenceUnitPriceGIC=?,DifferenceNetAmount=? where  TestCodeInvoice=? and UnitPriceInvoice=?"
                values=(testNameGIC,testMethodGIC,GICTestOutcomeId,diffUnitPrice,diffNetPrice,invoiceMethodName,invoiceUnitPrice)
                
                try:
                    cursor.execute(insert_sql,values)
                    conn.commit()
                    print('Record Inserted')
                    print('Updated the Test Value')
                except Exception as e:
                    print(f'Error in Inserting:{str(e)}')
                    print("Error In Updating Test Value")
                count+=1
            else:
                print('THis is GICID',GICId)
                GICId=GICId[0]
                print(GICId,'After comintcl')
                qualityInvoiceGICTable=pd.read_sql(f"Select GICQualityId,Price from GICQuality_External where (GICId={GICId}) and (LabTestId={labTestIdInvoice}) and (UoMId={uomInvoiceId})",conn)
                if qualityInvoiceGICTable.empty==True or qualityInvoiceGICTable['Price'].empty==True:
                    GICTestOutcomeId=3
                    insert_sql=f"Update  UtilityTestLeakage_External Set TestNameGIC=?,TestCodeGIC=?,GICTestOutcomeId=?,DifferenceUnitPriceGIC=?,DifferenceNetAmount=? where  TestCodeInvoice=? and UnitPriceInvoice=?"
                    values=(testNameGIC,testMethodGIC,GICTestOutcomeId,diffUnitPrice,diffNetPrice,invoiceMethodName,invoiceUnitPrice)
                    
                    try:
                        cursor.execute(insert_sql,values)
                        conn.commit()
                        print('Record Inserted')
                        print('Updated the Test Value')
                    except Exception as e:
                        print(f'Error in Inserting:{str(e)}')
                        print("Error In Updating Test Value")
                    count+=1
                else:
                    invoiceUnitPrice=invoicetotalUnitPrice/invoiceQuantityValue
                    gicPriceTest=qualityInvoiceGICTable['Price'][0]
                    # print(invoiceTestName,'This is unitPrice##########',invoiceUnitPrice,'This is gicPRice',gicPriceTest)
                    gic_NetPrice=gicPriceTest*invoiceQuantityValue
                    invoice_NetPrice=invoiceUnitPrice*invoiceQuantityValue
                    diffUnitPrice=invoiceUnitPrice-gicPriceTest
                    diffNetPrice=invoice_NetPrice-gic_NetPrice
                    print('This is invoice',invoiceUnitPrice,'this is gicPrice',gicPriceTest,'of invoice id',invoiceId)
                    GICTestOutcomeId=1
                    # print('Before Count Value of Pprice',count)
                    if diffUnitPrice!=0:
                        
                        count+=1
                        # print('This is Count value After Price',count)
                    insert_sql=f"Update  UtilityTestLeakage_External Set DifferenceNetAmount=?,DifferenceUnitPriceGIC=?,UnitPriceGIC=? where  TestCodeInvoice=? and UnitPriceInvoice=?"
                    values=(diffNetPrice,diffUnitPrice,gicPriceTest,invoiceMethodName,invoiceUnitPrice)
                    # print(values)
                    try:
                        cursor.execute(insert_sql,values)
                        conn.commit()
                        print('Record Inserted')
                    except Exception as e:
                        print(f'Error in Inserting:{str(e)}')
                    break
                    
                
        else:
            # print(invoiceTestName)
            if  np.isnan(qualityInvoiceId):
                print("QualitytID NONEEEEEEEEEEEEEEEE")
                print(invoiceTestName)
                continue
            qualityInvoiceGICTable=pd.read_sql(f"Select Price from GICQuality_External where (GICQualityId={qualityInvoiceId}) and (LabTestId={labTestIdInvoice}) ",conn)

            if qualityInvoiceGICTable['Price'].empty==True:
                print("This is empty")
                # print(qualityInvoiceId)
                # print(gicPriceTest)
            else:
                gicPriceTest=qualityInvoiceGICTable['Price'][0]
                # print('this is invoiceTestname ',invoiceTestName,'and this is the price ',gicPriceTest)
                invoiceUnitPrice=invoicetotalUnitPrice/invoiceQuantityValue
                gic_NetPrice=gicPriceTest*invoiceQuantityValue
                invoice_NetPrice=invoiceUnitPrice*invoiceQuantityValue
                diffUnitPrice=invoiceUnitPrice-gicPriceTest
                diffNetPrice=invoice_NetPrice-gic_NetPrice
                
                if diffUnitPrice!=0 :
                    count+=1
                    # print('This is  count Value of after price',count)
                print('This is invoice',invoiceUnitPrice,'this is gicPrice',gicPriceTest,'of invoice id',invoiceId)
                GICTestOutcomeId=1
                # print(diffNetPrice,'---',diffUnitPrice)
                # insert_sql=f"Update  UtilityTestLeakage_External Set DifferenceNetAmount=?,DifferenceUnitPriceGIC=?,UnitPriceGIC=? where  TestCodeInvoice=?"
                insert_sql=f"Update UtilityTestLeakage_External Set DifferenceNetAmount='{diffNetPrice}', DifferenceUnitPriceGIC='{diffUnitPrice}' ,UnitPriceGIC='{gicPriceTest}' where TestNameInvoice='{invoiceTestName}' and UnitPriceInvoice='{invoiceUnitPrice}'"

                # print('THis is InsertQuery',insert_sql)
                # print('THHHHHHHHHHHHHHHHHHHHHHHHHHHH')
                
                try:
                    cursor.execute(insert_sql)
                    conn.commit()
                    print('This test is inserted',invoiceTestName)
                    print('Record Inserted')
                except Exception as e:
                    print(f'Error in Inserting:{str(e)}')
                

    return count
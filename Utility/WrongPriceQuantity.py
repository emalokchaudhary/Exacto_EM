import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import datetime
import numpy as np
import re
import warnings

warnings.filterwarnings("ignore")
def wrongPriceQuantity(invoiceId,nominationDetailId,conn):
    cursor=conn.cursor()
    count=0
    CreatedBy=2
    CreatedDate=datetime.datetime.now()
    cursor=conn.cursor()
    print(invoiceId,'InvoiceId')
    GICGradeIDProduct=''
    GradeType=''
    objectType=''
    objectTypeId=''
    NominationHeader=pd.read_sql(f'Select * from NominationDetails_External where NominationDetailId={nominationDetailId}',con=conn)
    locationId=NominationHeader['LocationId']
    vendor=NominationHeader['Vendor'][0]
    vendorId=NominationHeader['VendorId']
    productNameNomination=pd.read_sql(f"Select ProductName from NominationQuantity_External where NominationDetailId='{nominationDetailId}'",conn)
    productNameNomination=productNameNomination['ProductName'][0]
    jobDate=pd.read_sql(f"Select JobDate from InvoiceHeader_External where RowID='{invoiceId}'",conn)
    jobDate=jobDate['JobDate'][0]
    if vendorId.empty==True:
        VendorList=pd.read_sql(f"Select * from VendorMaster",conn)
        for index,rows in VendorList.iterrows():
            x=fuzz.token_set_ratio(rows['description'],vendor)
            if x>80:
                vendorId=rows['RowId']
                break
    else:
        vendorId=vendorId[0]
        
    if  locationId[0]==None:
        if vendorId==14:
            locationId=52
        else:
            location=NominationHeader['Location'][0]
            print('Before ',location)
            locationMaster=pd.read_sql(f"Select * From LocationMaster",conn)
            allLocations=locationMaster['description'].tolist()
            location=process.extractOne(location,allLocations)[0]
            print('After ',location)
            locationId=pd.read_sql(f"Select RowId from LocationMaster where description='{location}'",conn)
            locationId=locationId['RowId'][0]
    else:
        locationId=int(locationId[0])
       
    print(locationId)
    invoiceQuantityItems=pd.read_sql(f"Select * From InvoiceQuantity_External where InvoiceId={invoiceId}",conn)
    for index,rows in invoiceQuantityItems.iterrows():
        invoiceproductName=rows['ProductName']
        invoiceproductNameId=rows['ProductId']
        invoiceVesselName=rows['VesselName']
        invoiceQuantityValue=rows['QuantityValue']
        invoicePriceTotal=rows['UnitPrice']
        GICQuantityId=rows['GICQuantityId']
        invoiceDescription=rows['Description']
        invoiceUoM=rows['UoM']
        invoiceUoMId=rows['UoMId']
        invoiceUnitPrice=invoicePriceTotal/invoiceQuantityValue
        if GICQuantityId!=None:
            gic_Quantity_data=pd.read_sql(f"Select * From GICQuantity_External where GICQuantityId='{GICQuantityId}'",conn)
            gic_ProductId=gic_Quantity_data['ProductTypeId'][0]
            gic_ProductType=pd.read_sql(f"Select description From GICGradeTypeMaster where RowId='{gic_ProductId}'",conn)
            gic_ProductType=gic_ProductType['description'][0]
            gic_objectTypeId=gic_Quantity_data['ObjectId'][0]
            gic_objectType=pd.read_sql(f"Select description from ObjectMaster where RowId='{gic_objectTypeId}'",conn)
            GIC_UnitPrice=gic_Quantity_data['Price'][0]
            gic_objectType=gic_objectType['description'][0]
            gic_UomId=gic_Quantity_data['UoMId'][0]
            total_GICUnitPrice=GIC_UnitPrice*invoiceQuantityValue
            if invoiceproductNameId!=None:
                print('THis is executed with ProductId but With GIC QuantityID')
                productCatalogue=pd.read_sql(f"Select GICGradeTypeId from ProductCatalogMaster where RowId='{invoiceproductNameId}'",conn)
                if productCatalogue.empty==True:
                    ProductTypeOutcomeId=6
                    count+=1 
                else:
                    invoice_GradeTypeId=productCatalogue['GICGradeTypeId'][0]
                    invoiceGradeType=pd.read_sql(f"Select description from GICGradeTypeMaster where RowId='{invoice_GradeTypeId}'",conn)
                    if invoiceGradeType.empty==True:
                        ProductTypeOutcomeId=6
                        count+=1
                    else:
                        invoiceGradeType=invoiceGradeType['description'][0]
                        if invoice_GradeTypeId==gic_ProductId:
                            ProductTypeOutcomeId=1
                        else:
                            ProductTypeOutcomeId=2
                            count+=1
            else:
                print('This is Executed No Pdt Id but GICQuantitytId')
                productCatalogue=pd.read_sql(f"Select GICGradeTypeId from ProductCatalogMaster where description='{invoiceproductName}'",conn)
                if productCatalogue.empty==True:
                    ProductTypeOutcomeId=6
                    count+=1
                else:
                    invoice_GradeTypeId=productCatalogue['GICGradeTypeId'][0]
                    invoiceGradeType=pd.read_sql(f"Select description from GICGradeTypeMaster where RowId='{invoice_GradeTypeId}'",conn)
                    if invoiceGradeType.empty==True:
                        ProductTypeOutcomeId=6
                        count+=1
                    else:
                        invoiceGradeType=invoiceGradeType['description'][0]
                        if invoice_GradeTypeId==gic_ProductId:
                            ProductTypeOutcomeId=1
                        else:
                            ProductTypeOutcomeId=2
                            count+=1
            
            objectMaster=pd.read_sql(f"Select * From ObjectMaster",conn)
            objectDescription=objectMaster['description'].tolist()
            objectTypeInvoice=objectDescription
            print('This is InvoiceDescription')
            print(invoiceDescription)
            if invoiceDescription!=None:
                invoiceobjectTypeGIC=process.extractOne(invoiceDescription,objectTypeInvoice)[0]
                objectTypeId=pd.read_sql(f"Select RowId from ObjectMaster where description='{invoiceobjectTypeGIC}'",conn)
            
                invoice_objectTypeId=int(objectTypeId['RowId'][0])
                if invoice_objectTypeId==gic_objectTypeId:
                    objectTypeOutcome=1
                else:
                    objectTypeOutcome=2
                    count+=1
                print('Object',objectTypeOutcome)
                print(invoiceGradeType,'----',gic_ProductType)
                print('Product',ProductTypeOutcomeId)   
            else:
                objectTypeOutcome=2   
                count+=1
            diff_UnitPrice=invoiceUnitPrice-GIC_UnitPrice
            diff_NetPrice=invoicePriceTotal-total_GICUnitPrice
            print(diff_UnitPrice)
            if diff_UnitPrice==0:
                count+=1

        else:
            if invoiceproductNameId!=None:
                # print('NO GIC ID but have ProductID')
                productCatalogue=pd.read_sql(f"Select GICGradeTypeId from ProductCatalogMaster where RowId='{invoiceproductNameId}'",conn)
                if productCatalogue.empty==True:
                    ProductTypeOutcomeId=6
                    count+=1
                else:
                    invoice_GradeTypeId=productCatalogue['GICGradeTypeId'][0]
                    invoiceGradeType=pd.read_sql(f"Select description from GICGradeTypeMaster where RowId='{invoice_GradeTypeId}'",conn)
                    if invoiceGradeType.empty==True:
                        ProductTypeOutcomeId=6
                        count+=1
                    else:
                        invoiceGradeType=invoiceGradeType['description'][0]
                        gic_ProductType=invoiceGradeType
                        gic_ProductId=invoice_GradeTypeId
                        if invoice_GradeTypeId==gic_ProductId:
                            ProductTypeOutcomeId=1
                        else:
                            ProductTypeOutcomeId=2
                            count+=1
            else:
                print('This is No GICQuantity no PDtID')  
                print(invoiceproductName)  
                productCatalogue=pd.read_sql(f"Select GICGradeTypeId from ProductCatalogMaster where description='{invoiceproductName}'",conn)
                if productCatalogue.empty==True:
                    ProductTypeOutcomeId=6
                    count+=1
                else:
                    invoice_GradeTypeId=productCatalogue['GICGradeTypeId'][0]
                    invoiceGradeType=pd.read_sql(f"Select description from GICGradeTypeMaster where RowId='{invoice_GradeTypeId}'",conn)
                    if invoiceGradeType.empty==True:
                        ProductTypeOutcomeId=6
                        count+=1
                    else:
                        gic_ProductId=invoice_GradeTypeId
                        invoiceGradeType=invoiceGradeType['description'][0]
                        gic_ProductType=invoiceGradeType
                        if invoice_GradeTypeId==gic_ProductId:
                            ProductTypeOutcomeId=1
                        else:
                            ProductTypeOutcomeId=2
                            count+=1
            print('THis is ProductTypeOutcome of ID',ProductTypeOutcomeId)
            objectMaster=pd.read_sql(f"Select * From ObjectMaster",conn)
            objectDescription=objectMaster['description'].tolist()
            objectTypeInvoice=objectDescription
            invoiceobjectTypeGIC=process.extractOne(invoiceDescription,objectTypeInvoice)[0]
            objectTypeId=pd.read_sql(f"Select RowId from ObjectMaster where description='{invoiceobjectTypeGIC}'",conn)
            invoice_objectTypeId=int(objectTypeId['RowId'][0])
            print('This is error invoiceObject',invoice_objectTypeId)
            print('This is error',invoiceGradeType)
            gic_objectTypeId=invoice_objectTypeId
            gic_objectType=invoiceGradeType
            if invoice_objectTypeId==gic_objectTypeId:
                objectTypeOutcome=1
            else:
                objectTypeOutcome=2
                count+=1
            objectSubData=pd.read_sql(f"Select RowId,description from ObjectSubCategory",conn)
            objectsubId=-1
            for index,rows in objectSubData.iterrows():
                objectsub=rows['description']
                ratio=fuzz.partial_ratio(objectsub,invoiceDescription)
                ratioTop=85
                
                if ratio>=ratioTop:
                    objectsubId=rows['RowId']
                    outputObject=objectsub
                    break
            if objectsubId==None or objectsubId==-1:
                objectsubId=9
            GICId=pd.read_sql(f"Select GICId from GICHeader_External where ('{jobDate}' between EffectiveFrom and EffectiveTo) and(VendorId={vendorId})and (LocationId ={locationId})  ",conn)
            if GICId.empty==True:
                print('Can not Proceed')
                diff_UnitPrice=None
                gic_NetAmount=None 
                invoiceNetAmount=invoiceUnitPrice*invoiceQuantityValue   
                diffUnitPrice=invoiceUnitPrice
                diff_NetPrice=invoiceNetAmount
                count+=1
                #NEED TO DO SOMETHING
                
            else:
                GICId=GICId['GICId'][0]
                    # print('This is GICID',GICId)
                gicQuantityTable=pd.read_sql(f"Select GICQuantityId,Price from GICQuantity_External where GICId={GICId} and(ObjectId={invoice_objectTypeId}) and (ProductTypeId={invoice_GradeTypeId}) and (UoMId={invoiceUoMId}) and (ObjectSubCategoryId ={objectsubId})",conn)
                # print("@@@@@@")    
                if gicQuantityTable.empty==True:
                        # print('Unit Price not Present')
                        diff_UnitPrice=None
                        gic_NetAmount=None 
                        invoiceNetAmount=invoiceUnitPrice*invoiceQuantityValue   
                        diffUnitPrice=invoiceUnitPrice
                        diff_NetPrice=invoiceNetAmount
                    
                else:
                    
                    gic_Price=gicQuantityTable['Price'][0]
                    # print(gic_Price)
                    diffUnitPrice=invoiceUnitPrice-gic_Price
                    gic_NetAmount=gic_Price*invoiceQuantityValue
                    invoiceNetAmount=invoiceUnitPrice*invoiceQuantityValue
                    diff_NetPrice=invoiceNetAmount-gic_NetAmount
                    if diffUnitPrice>0:
                        count+=1
        print('FOR INVOICE ID---------------------------',invoiceId)
        print(ProductTypeOutcomeId,'----',objectTypeOutcome)
        insert_sql=f"Insert Into UtilityProductLeakage_External (InvoiceQuantity,VesselName,ProductNameInvoice,ProductNameNomination,ProductTypeInvoice,ProductTypeGIC,ProductTypeOutcomeId,ObjectTypeInvoice,ObjectTypeGIC,ObjectTypeOutcomeId,UnitPriceInvoice,UnitPriceGIC,DifferenceUnitPriceGIC,DifferenceNetAmount,CreatedBy,CreatedDate,InvoiceId) Values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"                
        values=(invoiceQuantityValue,invoiceVesselName,invoiceproductName,productNameNomination,invoiceGradeType,gic_ProductType,ProductTypeOutcomeId,invoiceobjectTypeGIC,gic_objectType,objectTypeOutcome,invoiceUnitPrice,GIC_UnitPrice,diff_UnitPrice,diff_NetPrice,CreatedBy,CreatedDate,invoiceId)
        print(invoiceQuantityValue,invoiceVesselName,invoiceproductName,productNameNomination,invoiceGradeType,gic_ProductType,ProductTypeOutcomeId,invoiceobjectTypeGIC,gic_objectType,objectTypeOutcome,invoiceUnitPrice,GIC_UnitPrice,diff_UnitPrice,diff_NetPrice,CreatedBy,CreatedDate,invoiceId)
        try:
            cursor.execute(insert_sql,values)
            conn.commit()
            print('Record Inserted')
        except Exception as e:
            print(f'Error in Inserting:{str(e)}')

    return count


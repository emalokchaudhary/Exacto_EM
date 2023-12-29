import pandas as pd
import datetime
from connection import connect_db
import warnings
warnings.filterwarnings('ignore')
conn=connect_db()
def Summarization_All(invoiceId,conn):
    createdBy=2
    cursor=conn.cursor()
    createdDate=datetime.datetime.now()
    invoiceLeakageData=pd.read_sql(f"Select * from UtilityInvoiceLeakage_External where InvoiceId='{invoiceId}'",conn)
    serviceInvoice=invoiceLeakageData['ServicesInvoice']
    if serviceInvoice.empty==True:
        totalItems=0
    else:
        
        serviceInvoice=invoiceLeakageData['ServicesInvoice'][0].lower()
        print(serviceInvoice)
    if 'quantity' in serviceInvoice and 'quality' not in serviceInvoice:
        totalItems=1
    if 'quantity' in serviceInvoice and 'quality' in serviceInvoice:
        totalItems=2
    if 'quality' in serviceInvoice and 'quantity' not in serviceInvoice:
        totalItems=1
    serviceOutcomeId=invoiceLeakageData['ServiceOutcomeId'][0]
    if serviceOutcomeId==1:
        mismatchItems=0
    elif serviceOutcomeId==7:
        mismatchItems=1
    elif serviceOutcomeId==8:
        mismatchItems=1
    else:
        mismatchItems=totalItems
    totalTests=pd.read_sql(f"Select Count(InspectionOutcomeId) from UtilityTestLeakage_External where InvoiceId='{invoiceId}' ",conn)
    if totalTests.empty==True:
        totalTests=0
    else:
        totalTests=totalTests[''][0]
        totalTests=int(totalTests)
        
    mismatchTests=pd.read_sql(f"Select Count(InspectionOutcomeId) From UtilityTestLeakage_External where (InspectionOutcomeId<>'1') and InvoiceId='{invoiceId}'",conn)
    print(mismatchTests)
    if mismatchTests.empty==True:
        mismatchTests=0
    else:
        mismatchTests=mismatchTests[''][0]
        mismatchTests=int(mismatchTests)
    leakageScenarioId=2
    leakageScenarioCategoryId=5
    insert_sql=f"Insert Into UtilityLeakageSummary_External (CreatedBy,CreatedDate,LeakageScenarioId,LeakageCategoryId,TotalItems,MismatchItems,InvoiceId) Values (?,?,?,?,?,?,?)"
    values=(createdBy,createdDate,leakageScenarioId,leakageScenarioCategoryId,totalItems,mismatchItems,invoiceId)
    try:
        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}') 
    
    leakageScenarioId=2
    leakageScenarioCategoryId=6
    values=(createdBy,createdDate,leakageScenarioId,leakageScenarioCategoryId,totalTests,mismatchTests,invoiceId)
    try:
        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}') 
    
    leakageScenarioId=1
    leakageScenarioCategoryId=1
    AllProductTypeCount=pd.read_sql(f"Select Count(ProductTypeOutcomeId) From UtilityProductLeakage_External where InvoiceId='{invoiceId}'",conn)
    MisMatchProductType=pd.read_sql(f"Select Count(ProductTypeOutcomeId) From UtilityProductLeakage_External where (ProductTypeOutcomeId<>'1') and InvoiceId='{invoiceId}'",conn)
    ObjectProductTypeCount=pd.read_sql(f"Select Count(ObjectTypeOutcomeId) From UtilityProductLeakage_External where InvoiceId='{invoiceId}'",conn)
    MisMatchObjectTypeOutcome=pd.read_sql(f"Select Count(ObjectTypeOutcomeId) From UtilityProductLeakage_External where (ObjectTypeOutcomeId <>'1')and InvoiceId='{invoiceId}'",conn)
    if AllProductTypeCount.empty==True:
        AllProductTypeCount=0
    else:
        AllProductTypeCount=int(AllProductTypeCount[''][0])
    if MisMatchProductType.empty==True:
        MisMatchProductType=0
    else:    
        MisMatchProductType=int(MisMatchProductType[''][0])
    if ObjectProductTypeCount.empty==True:
        ObjectProductTypeCount=0
    else: 
        ObjectProductTypeCount=int(ObjectProductTypeCount[''][0])
    if MisMatchObjectTypeOutcome.empty==True:
        MisMatchObjectTypeOutcome=0
    else:
        MisMatchObjectTypeOutcome=int(MisMatchObjectTypeOutcome[''][0])
    #ProductType Checking 
    insert_sql=f"Insert Into UtilityLeakageSummary_External (CreatedBy,CreatedDate,LeakageScenarioId,LeakageCategoryId,TotalItems,MismatchItems,InvoiceId) Values (?,?,?,?,?,?,?)"
    values=(createdBy,createdDate,leakageScenarioId,leakageScenarioCategoryId,AllProductTypeCount,MisMatchProductType,invoiceId)
    try:
        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}')
    #Object Checking in Product
    values=(createdBy,createdDate,leakageScenarioId,leakageScenarioCategoryId,ObjectProductTypeCount,MisMatchObjectTypeOutcome,invoiceId)
    try:
        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}')

    productPricingTotal=pd.read_sql(f"Select Count(DifferenceUnitPriceGIC) From UtilityProductLeakage_External where InvoiceId='{invoiceId}'",conn)
    if productPricingTotal.empty==True:
        productPricingTotal=0
    else:
        productPricingTotal=int(productPricingTotal[''][0])
    
    mismatchProductPricing=pd.read_sql(f"Select Count (DifferenceUnitPriceGIC) From UtilityProductLeakage_External where (DifferenceUnitPriceGIC>0 or DifferenceUnitPriceGIC<0) and InvoiceId='{invoiceId}' ",conn)
    if mismatchProductPricing.empty==True:
        mismatchProductPricing=0
    else:
        mismatchProductPricing=int(mismatchProductPricing[''][0])

    totalGICTests=pd.read_sql(f"Select Count(GICTestOutcomeId) From UtilityTestLeakage_External where InvoiceId='{invoiceId}'",conn)
    if totalGICTests.empty==True:
        totalGICTests=0
    else:
        totalGICTests=int(totalGICTests[''][0])
    errorGICTests=pd.read_sql(f"Select Count(GICTestOutcomeId) From UtilityTestLeakage_External where (GICTestOutcomeId<>'1') and InvoiceId='{invoiceId}'",conn)
    if errorGICTests.empty==True:
        errorGICTests=0
    else:
        errorGICTests=int(errorGICTests[''][0])
    testPricingTotal=pd.read_sql(f"Select Count (DifferenceUnitPriceGIC) From UtilityTestLeakage_External where InvoiceId='{invoiceId}' ",conn)
    if testPricingTotal.empty==True:
        testPricingTotal=0
    else:
        testPricingTotal=int(testPricingTotal[''][0])
    
    testerrorPricingTotal=pd.read_sql(f"Select Count (DifferenceUnitPriceGIC) From UtilityTestLeakage_External where (DifferenceUnitPriceGIC>0 or DifferenceUnitPriceGIC<0) and InvoiceId='{invoiceId}' ",conn)
    if testerrorPricingTotal.empty==True:
        testerrorPricingTotal=0
    else:
        testerrorPricingTotal=int(testerrorPricingTotal[''][0])
    #GIC Tests
    leakageScenarioCategoryId=2
    leakageScenarioId=1
    insert_sql=f"Insert Into UtilityLeakageSummary_External (CreatedBy,CreatedDate,LeakageScenarioId,LeakageCategoryId,TotalItems,MismatchItems,InvoiceId) Values (?,?,?,?,?,?,?)"
    values=(createdBy,createdDate,leakageScenarioId,leakageScenarioCategoryId,totalGICTests,errorGICTests,invoiceId)
    try:
        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}')
    #Pricing Annomoly 
    leakageScenarioId=1
    leakageScenarioCategoryId=4
    totalTestnProduct=testPricingTotal+productPricingTotal
    totalErrorTestnProduct=testerrorPricingTotal+mismatchProductPricing
    insert_sql=f"Insert Into UtilityLeakageSummary_External (CreatedBy,CreatedDate,LeakageScenarioId,LeakageCategoryId,TotalItems,MismatchItems,InvoiceId) Values (?,?,?,?,?,?,?)"
    values=(createdBy,createdDate,leakageScenarioId,leakageScenarioCategoryId,totalTestnProduct,totalErrorTestnProduct,invoiceId)
    try:
        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}')

    #CurrencyCheck
    leakageScenarioId=1
    leakageScenarioCategoryId=3
    currencyTotalCount=pd.read_sql(f"Select Count(CurrencyOutcomeId) From UtilityInvoiceLeakage_External where InvoiceId='{invoiceId}'",conn)
    if currencyTotalCount.empty==True:
        currencyTotalCount=0
    else:
        currencyTotalCount=int(currencyTotalCount[''][0])
    mismatchCurrencyCount=pd.read_sql(f"Select Count(CurrencyOutcomeId) From UtilityInvoiceLeakage_External where InvoiceId='{invoiceId}' and (CurrencyOutcomeId<>'1')",conn)
    if mismatchCurrencyCount.empty==True:
        mismatchCurrencyCount=0
    else:
        mismatchCurrencyCount=int(mismatchCurrencyCount[''][0])
    values=(createdBy,createdDate,leakageScenarioId,leakageScenarioCategoryId,currencyTotalCount,mismatchCurrencyCount,invoiceId)
    try:
        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}')

    #Discount
    leakageScenarioId=3
    leakageScenarioCategoryId=8
    discountTotalCount=pd.read_sql(f"Select Count(discountCheckOutcome) from UtilityDiscountError_External where InvoiceId='{invoiceId}'",conn)
    if discountTotalCount.empty==True:
        discountTotalCount=0
    else:
        discountTotalCount=int(discountTotalCount[''][0])
    
    discountError=pd.read_sql(f"Select Count(discountCheckOutcome) From UtilityDiscountError_External where (discountCheckOutcome<>'1') and InvoiceId='{invoiceId}'",conn)
    if discountError.empty==True:
        discountError=0
    else:
        discountError=int(discountError[''][0])
    
    insert_sql=f"Insert Into UtilityLeakageSummary_External (CreatedBy,CreatedDate,LeakageScenarioId,LeakageCategoryId,TotalItems,MismatchItems,InvoiceId) Values (?,?,?,?,?,?,?)"
    values=(createdBy,createdDate,leakageScenarioId,leakageScenarioCategoryId,discountTotalCount,discountError,invoiceId)
    try:
        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}')  

    #DiscountStatusCheckOutcome
    leakageScenarioId=3
    leakageScenarioCategoryId=8
    discountStatusTotal=pd.read_sql(f"Select Count(DiscountStatusCheckOutcome)From UtilityDiscountError_External where InvoiceId='{invoiceId}'",conn)
    if discountStatusTotal.empty==True:
        discountStatusTotal=0
    else:
        discountStatusTotal=int(discountStatusTotal[''][0])
    
    discountStatusErrorTotal=pd.read_sql(f"Select Count(DiscountStatusCheckOutcome) From UtilityDiscountError_External where (DiscountStatusCheckOutcome<>'25') and InvoiceId='{invoiceId}'",conn)
    if discountStatusErrorTotal.empty==True:
        discountStatusErrorTotal=0
    else:
        discountStatusErrorTotal=int(discountStatusErrorTotal[''][0])
    insert_sql=f"Insert Into UtilityLeakageSummary_External (CreatedBy,CreatedDate,LeakageScenarioId,LeakageCategoryId,TotalItems,MismatchItems,InvoiceId) Values (?,?,?,?,?,?,?)"
    values=(createdBy,createdDate,leakageScenarioId,leakageScenarioCategoryId,discountStatusTotal,discountStatusErrorTotal,invoiceId)
    try:
        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}')  
#Cost Share Product
    totalProductCostShare=pd.read_sql(f"Select Count(CostShareCheckOutcome) From UtilityProductCostShare_External where InvoiceId='{invoiceId}'",conn)
    if totalProductCostShare.empty==True:
        totalProductCostShare=0
    else:
        totalProductCostShare=int(totalProductCostShare[''][0])
    totalProductCostShareError=pd.read_sql(f"Select Count(CostShareCheckOutcome) From UtilityProductCostShare_External where (CostShareCheckOutcome<>'1') and InvoiceId='{invoiceId}'",conn)
    if totalProductCostShareError.empty==True:
        totalProductCostShareError=0
    else:
        totalProductCostShareError=int(totalProductCostShareError[''][0])
#Test Cost Share
    leakageScenarioId=4
    leakageScenarioCategoryId=9
    totalTestCostShare=pd.read_sql(f"Select Count(CostShareCheckOutcome) From UtilityTestCostShare_External where InvoiceId='{invoiceId}'",conn)
    if totalTestCostShare.empty==True:
        totalTestCostShare=0
    else:
        totalTestCostShare=int(totalTestCostShare[''][0])
    totalTestCostShareError=pd.read_sql(f"Select Count(CostShareCheckOutcome) From UtilityTestCostShare_External where (CostShareCheckOutcome<>'1') and InvoiceId='{invoiceId}'",conn)
    if totalTestCostShareError.empty==True:
        totalTestCostShareError=0
    else:
        totalTestCostShareError=int(totalTestCostShareError[''][0])
    totalCostShare=totalProductCostShare+totalTestCostShare
    totalCostShareError=totalProductCostShareError+totalTestCostShareError
    insert_sql=f"Insert Into UtilityLeakageSummary_External (CreatedBy,CreatedDate,LeakageScenarioId,LeakageCategoryId,TotalItems,MismatchItems,InvoiceId) Values (?,?,?,?,?,?,?)"
    values=(createdBy,createdDate,leakageScenarioId,leakageScenarioCategoryId,totalCostShare,totalCostShareError,invoiceId)
    try:
        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}')
#WrongQuality
    leakageScenarioId=6
    leakageScenarioCategoryId=13
    WrongQualityLeakageData=pd.read_sql(f"Select NominationService from UtilityWrongServiceQuality_External where InvoiceId='{invoiceId}'",conn)
    serviceNomination=WrongQualityLeakageData['NominationService']
    if serviceNomination.empty==True:
        totalItems=0
    else:
        serviceNomination=WrongQualityLeakageData['NominationService'][0].lower()
        print(serviceNomination)
    if 'quantity' in serviceNomination and 'quality' not in serviceNomination:
        totalItems=1
    if 'quantity' in serviceNomination and 'quality' in serviceNomination:
        totalItems=2
    if 'quality' in serviceNomination and 'quantity' not in serviceNomination:
        totalItems=1
    
    serviceOutcomeId=pd.read_sql(f"Select ServiceOutcome from UtilityWrongServiceQuality_External where InvoiceId='{invoiceId}'",conn)
    if serviceOutcomeId.empty==True:
        mismatchItems=totalItems
    else:
        serviceOutcomeId=serviceOutcomeId['ServiceOutcome'][0]
    if serviceOutcomeId==9:
        mismatchItems=0
    elif serviceOutcomeId==10:
        mismatchItems=1
    elif serviceOutcomeId==27:
        mismatchItems=1
    else:
        mismatchItems=totalItems
    
    totalTests=pd.read_sql(f"Select Count(TestCheckOutcome) from UtilityWrongTestQuality_External where InvoiceId='{invoiceId}' ",conn)
    if totalTests.empty==True:
        totalTests=0
    else:
        totalTests=totalTests[''][0]
        totalTests=int(totalTests)
        
    mismatchTests=pd.read_sql(f"Select Count(TestCheckOutcome) From UtilityWrongTestQuality_External where (TestCheckOutcome<>'1') and InvoiceId='{invoiceId}'",conn)
    
    if mismatchTests.empty==True:
        mismatchTests=0
    else:
        mismatchTests=mismatchTests[''][0]
        mismatchTests=int(mismatchTests)
    print(mismatchTests)
#ServiceCheck OF WrongQuality
    insert_sql=f"Insert Into UtilityLeakageSummary_External (CreatedBy,CreatedDate,LeakageScenarioId,LeakageCategoryId,TotalItems,MismatchItems,InvoiceId) Values (?,?,?,?,?,?,?)"
    values=(createdBy,createdDate,leakageScenarioId,leakageScenarioCategoryId,totalItems,mismatchItems,invoiceId)
    try:
        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}') 
#QualityTest For WrongQuality
    leakageScenarioId=6
    leakageScenarioCategoryId=15
    values=(createdBy,createdDate,leakageScenarioId,leakageScenarioCategoryId,totalTests,mismatchTests,invoiceId)
    try:
        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}') 
    
#WrongQuantity Summarization
    leakageScenarioId=5
    leakageScenarioCategoryId=11
    UomTotalOutcome=pd.read_sql(f"Select Count(UoMCheckOutcome) From UtilityWrongQuantity_External where InvoiceId='{invoiceId}'",conn)
    if UomTotalOutcome.empty==True:
        UomTotalOutcome=0
    else:
        UomTotalOutcome=int(UomTotalOutcome[''][0])
    UomMismatchOutcome=pd.read_sql(f"Select Count(UoMCheckOutcome) From UtilityWrongQuantity_External where (UoMCheckOutcome<>'20') and InvoiceId='{invoiceId}'",conn)
    if UomMismatchOutcome.empty==True:
        UomMismatchOutcome=0
    else:
        UomMismatchOutcome=int(UomMismatchOutcome[''][0])
    values=(createdBy,createdDate,leakageScenarioId,leakageScenarioCategoryId,UomTotalOutcome,UomMismatchOutcome,invoiceId)
    try:
        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}')
    
    leakageScenarioCategoryId=10
    totalQuantityOutcome=pd.read_sql(f"Select Count(QuantityValueCheckOutcome)From UtilityWrongQuantity_External where InvoiceId='{invoiceId}'",conn)
    if totalQuantityOutcome.empty==True:
        totalQuantityOutcome=0
    else:
        totalQuantityOutcome=int(totalQuantityOutcome[''][0])
    mismatchQuantityOutcome=pd.read_sql(f"Select Count(QuantityValueCheckOutcome)From UtilityWrongQuantity_External where InvoiceId='{invoiceId}' and (QuantityValueCheckOutcome<>'18')",conn)
    if mismatchQuantityOutcome.empty==True:
        mismatchQuantityOutcome=0
    else:
        mismatchQuantityOutcome=int(mismatchQuantityOutcome[''][0])
    values=(createdBy,createdDate,leakageScenarioId,leakageScenarioCategoryId,totalQuantityOutcome,mismatchQuantityOutcome,invoiceId)
    try:
        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}')
    
    leakageScenarioCategoryId=12
    totalQuantityThresholdOutcome=pd.read_sql(f"Select Count(QuantityThresholdCheckOutcome) From UtilityWrongQuantity_External where InvoiceId='{invoiceId}'",conn)
    if totalQuantityThresholdOutcome.empty==True:
        totalQuantityThresholdOutcome=0
    else:
        totalQuantityThresholdOutcome=int(totalQuantityThresholdOutcome[''][0])
    missingQuantityThresholdOutcome=pd.read_sql(f"Select Count(QuantityThresholdCheckOutcome) From UtilityWrongQuantity_External where InvoiceId='{invoiceId}' and (QuantityThresholdCheckOutcome <>'15')",conn)
    if missingQuantityThresholdOutcome.empty==True:
        missingQuantityThresholdOutcome=0
    else:
        missingQuantityThresholdOutcome=int(missingQuantityThresholdOutcome[''][0])
    values=(createdBy,createdDate,leakageScenarioId,leakageScenarioCategoryId,totalQuantityThresholdOutcome,missingQuantityThresholdOutcome,invoiceId)
    try:
        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}')

      
def potentialLeakage(InvoiceId,conn):
    cursor=conn.cursor()
    product_amount=pd.read_sql(f'Select Sum(DifferenceNetAmount) from UtilityProductLeakage_External where (DifferenceNetAmount<0 or DifferenceNetAmount>0) and InvoiceId={InvoiceId} ',conn)
    test_amount=pd.read_sql(f'Select Sum(DifferenceNetAmount) from UtilityTestLeakage_External where (DifferenceNetAmount>0 or DifferenceNetAmount<0) and InvoiceId={InvoiceId}',conn)

    if product_amount[''][0]==None and test_amount[''][0]==None:
        totalAmount=0
    elif product_amount[''][0]!=None and test_amount[''][0]!=None:
        totalAmount=float(product_amount[''][0])+float(test_amount[''][0])
    elif product_amount[''][0]!=None and test_amount[''][0]==None:
        totalAmount=float(product_amount[''][0])
    elif product_amount[''][0]==None and test_amount[''][0]!=None:
        totalAmount=float(test_amount[''][0])
    print('PotentialLeakage of InvoiceId',InvoiceId,'The amount is ',totalAmount)
    insert_sql=f"Update InvoiceHeader_External Set PotentialLeakageValue={totalAmount} where RowID={InvoiceId}"
    try:
        cursor.execute(insert_sql)
        cursor.commit()
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}')
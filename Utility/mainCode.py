from connection import connect_db
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import datetime
import numpy as np
from InvoiceHeaderException import invoiceHeaderException
from InvoiceQuantityValidation import invoiceQuantityValidation
from InvoiceQualityValidation import InvoiceQualityValidation
from InspectionHeader_Validation import  InspectionHeaderValidation
from InspectionQuality_Exception import InspectionQuality_Validation
from InspectionQuantity_Validation import InspectionQuantityValidationcall
from InspectionQuantityUoM_Validation import wrongquantity_uom_validation
from ServiceRecievedButNotInvoice import serviceRecieved,serviceTestCheck,CurrencyMatch
from WrongPriceQuantity import wrongPriceQuantity
from WrongPriceQuality import wrongPriceQuality
from ProductCostShare import productcostshare
from TestCostShare import testCostShare
from WrongQuality import wrongQualityServiceLeakage,WrongQualityTestLeakage
from DiscountLeakage import DiscountLeakage
from WrongQuantity import wrongQuantity
from Summarization import Summarization_All,potentialLeakage
import warnings
import logging

warnings.filterwarnings("ignore")
def main():
    conn=connect_db()
    cursor=conn.cursor()
    invoices=pd.read_sql(f"Select * from InvoiceHeader_External where StatusID=53",conn)
    for index,rows in invoices.iterrows():
        try:
            nominationDetailId=rows['NominationDetailId']
            invoiceId=rows['RowID']
            inspection=pd.read_sql(f"Select TypeOfInspection from NominationDetails_External where NominationDetailId={nominationDetailId}",conn)
            inspection=inspection['TypeOfInspection'][0]
            if inspection!=None:
                if 'quantity' in inspection.lower() and 'quality' not in inspection.lower():
                    errorInvoiceHeader=invoiceHeaderException(invoiceId,nominationDetailId,conn)
                    errorInvoiceQuantity=invoiceQuantityValidation(invoiceId,nominationDetailId,conn)
                    errorInspectionHeader=InspectionHeaderValidation(invoiceId,nominationDetailId,conn)
                    errorInspectionQuantity=InspectionQuantityValidationcall(invoiceId,nominationDetailId,conn)
                    errorInspectionQuantityUoM=wrongquantity_uom_validation(invoiceId,nominationDetailId,conn)
                    if errorInvoiceHeader==0 and errorInvoiceQuantity ==0 and errorInspectionHeader==0 and errorInspectionQuantity==0 and errorInspectionQuantityUoM==0:
                        serviceError,TotalServices=serviceRecieved(invoiceId,nominationDetailId,conn)
                        wrongPriceQuantityError=wrongPriceQuantity(invoiceId,nominationDetailId,conn)
                        discountError=DiscountLeakage(invoiceId,conn)
                        productCostShareError=productcostshare(invoiceId,nominationDetailId,conn)
                        wrongQualityServiceLeakageError=wrongQualityServiceLeakage(invoiceId,nominationDetailId,conn)
                        wrongQuantityError=wrongQuantity(invoiceId,nominationDetailId,conn)
                        totalError=serviceError+wrongPriceQuantityError+discountError+productCostShareError+wrongQuantityError
                        if totalError==0:
                            insert_sql=f"Update InvoiceHeader_External Set Status=55, StatusId=55,LeakageCount={totalError} where InvoiceId={invoiceId}"
                            try:
                                cursor.execute(insert_sql)
                                conn.commit()
                                print('Record Inserted')
                            except Exception as e:
                                print(f"Exception Occured")
                        else:
                            insert_sql=f"Update InvoiceHeader_External Set Status=56, StatusId=56,LeakageCount={totalError} where InvoiceId={invoiceId}"
                            try:
                                cursor.execute(insert_sql)
                                conn.commit()
                                print('Record Inserted')
                            except Exception as e:
                                print(f"Error Occured {str(e)}")

                    else:
                        insert_sql=f"Update InvoiceHeader_External Set Status=58,StatusId=58 where RowID='{invoiceId}'"
                        try:
                            cursor.execute(insert_sql)
                            conn.commit()
                            print('Record Inserted')
                        except Exception as e:
                            print(f"Error Occured {str(e)}")
    
                elif  'quantity' in inspection.lower() and 'quality' in inspection.lower():
                    errorInvoiceHeader=invoiceHeaderException(invoiceId,nominationDetailId,conn)
                    errorInvoiceQuantity=invoiceQuantityValidation(invoiceId,nominationDetailId,conn)
                    errorInvoiceQuality=InvoiceQualityValidation(invoiceId,nominationDetailId,conn)
                    errorInspectionHeader=InspectionHeaderValidation(invoiceId,nominationDetailId,conn)
                    errorInspectionQuantity=InspectionQuantityValidationcall(invoiceId,nominationDetailId,conn)
                    errorInspectionQuality=InspectionQuality_Validation(invoiceId,nominationDetailId,conn)
                    errorInspectionQuantityUoM=wrongquantity_uom_validation(invoiceId,nominationDetailId,conn)
                    if errorInvoiceHeader==0 and errorInvoiceQuantity ==0 and errorInvoiceQuality==0 and errorInspectionHeader==0 and errorInspectionQuantity==0 and errorInspectionQuantityUoM==0 and errorInspectionQuality==0:
                        print('This is Leakage Table')
                        serviceError,TotalServices=serviceRecieved(invoiceId,nominationDetailId,conn)
                        serviceTestError=serviceTestCheck(invoiceId,conn)
                        wrongPriceQuantityError=wrongPriceQuantity(invoiceId,nominationDetailId,conn)
                        wrongPriceQualityError=wrongPriceQuality(invoiceId,nominationDetailId,conn)
                        discountError=DiscountLeakage(invoiceId,conn)
                        productCostShareError=productcostshare(invoiceId,nominationDetailId,conn)
                        testCostShareError=testCostShare(invoiceId,nominationDetailId,conn)
                        wrongQuantityError=wrongQuantity(invoiceId,nominationDetailId,conn)
                        wrongQualityServiceLeakageError=wrongQualityServiceLeakage(invoiceId,nominationDetailId,conn)
                        wrongQualityTestError=WrongQualityTestLeakage(invoiceId,nominationDetailId,conn)
                        total=serviceError+serviceTestError+wrongPriceQuantityError+wrongPriceQualityError+discountError+productCostShareError+testCostShareError+wrongQuantityError+wrongQualityServiceLeakageError+wrongQualityTestError
                        if totalError==0:
                                insert_sql=f"Update InvoiceHeader_External Set Status=55, StatusId=55,LeakageCount={totalError} where InvoiceId={invoiceId}"
                                try:
                                    cursor.execute(insert_sql)
                                    conn.commit()
                                    print('Record Inserted')
                                except Exception as e:
                                    print(f"Error Occured {str(e)}")
                        else:
                            insert_sql=f"Update InvoiceHeader_External Set Status=56, StatusId=56,LeakageCount={totalError} where InvoiceId={invoiceId}"
                            try:
                                cursor.execute(insert_sql)
                                conn.commit()
                                print('Record Inserted')
                            except Exception as e:
                                print(f"Error Occured {str(e)}")

                    else:
                        insert_sql=f"Update InvoiceHeader_External Set Status=58,StatusId=58 where RowID='{invoiceId}'"
                        try:
                            cursor.execute(insert_sql)
                            conn.commit()
                            print('Record Inserted')
                        except Exception as e:
                            print(f"Error Occured {str(e)}")
                    
                elif 'quality' in inspection.lower() and 'quantity' not in inspection.lower():
                    errorInvoiceHeader=invoiceHeaderException(invoiceId,nominationDetailId,conn)
                    errorInvoiceQuality=InvoiceQualityValidation(invoiceId,nominationDetailId,conn)
                    errorInspectionHeader=InspectionHeaderValidation(invoiceId,nominationDetailId,conn)
                    errorInspectionQuality=InspectionQuality_Validation(invoiceId,nominationDetailId,conn)
                    if errorInvoiceHeader==0 and errorInvoiceQuality==0 and errorInspectionHeader==0 and errorInspectionQuality==0:
                        print('This is LeakageTable')
                        serviceError,TotalServices=serviceRecieved(invoiceId,nominationDetailId,conn)
                        serviceTestError=serviceTestCheck(invoiceId,conn)
                        wrongPriceQualityError=wrongPriceQuality(invoiceId,nominationDetailId,conn)
                        discountError=DiscountLeakage(invoiceId,conn)
                        testCostShareError=testCostShare(invoiceId,nominationDetailId,conn)
                        wrongQualityServiceLeakageError=wrongQualityServiceLeakage(invoiceId,nominationDetailId,conn)
                        wrongQualityTestError=WrongQualityTestLeakage(invoiceId,nominationDetailId,conn)
                        total=serviceError+serviceTestError+wrongPriceQualityError+discountError+testCostShareError+wrongQualityServiceLeakageError+wrongQualityTestError
                        if totalError==0:
                                insert_sql=f"Update InvoiceHeader_External Set Status=55, StatusId=55,LeakageCount={totalError} where InvoiceId={invoiceId}"
                                try:
                                    cursor.execute(insert_sql)
                                    conn.commit()
                                    print('Record Inserted')
                                except Exception as e:
                                    print(f"Error Occured {str(e)}")
                        else:
                            insert_sql=f"Update InvoiceHeader_External Set Status=56, StatusId=56,LeakageCount={totalError} where InvoiceId={invoiceId}"
                            try:
                                cursor.execute(insert_sql)
                                conn.commit()
                                print('Record Inserted')
                            except Exception as e:
                                print(f"Error Occured {str(e)}")
                    else:
                        insert_sql=f"Update InvoiceHeader_External Set Status=58,StatusId=58 where RowID='{invoiceId}'"
                        try:
                            cursor.execute(insert_sql)
                            conn.commit()
                            print('Record Inserted')
                        except Exception as e:
                            print(f"Error Occured {str(e)}")

        except Exception as e:
            print(f"Error Occured {str(e)}")
        
main()
"""
Delete InvoiceHeader_Validation
Delete InvoiceQuantity_Validation
Delete InvoiceQuality_Validation
Delete InspectionHeader_Validation  
Delete InspectionQuantity_Validation
Delete InspectionQuantityUoM_Validation
Delete InspectionQuality_Validation
Delete UtilityInvoiceLeakage_External
Delete UtilityLeakageSummary_External
Delete UtilityProductCostShare_External
Delete UtilityProductLeakage_External
Delete UtilityTestCostShare_External
Delete UtilityTestLeakage_External
Delete UtilityWrongQuantity_External
Delete UtilityWrongServiceQuality_External
Update InvoiceHeader_External Set StatusID=53,Status=53
"""
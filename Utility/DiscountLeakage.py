from connection import connect_db
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import datetime
from connection import connect_db
import warnings
warnings.filterwarnings("ignore")
conn=connect_db()
def DiscountLeakage(invoiceId,conn):
    error=0
    cursor=conn.cursor()
    createdBy=2
    createdDate=datetime.datetime.now()
    invoiceHeader=pd.read_sql(f"Select * From InvoiceHeader_External where RowID='{invoiceId}'",conn)
    VendorName=invoiceHeader['Vendor'][0]
    VendorId=invoiceHeader['VendorId']
    invoicediscountPercentage=invoiceHeader['DiscountPercent']
    jobDate=invoiceHeader['JobDate'][0]
    totalDueAmount=invoiceHeader['TotalDueAmount']
    
    if VendorId.empty==True or VendorId[0]==None:
        
        VendorList=pd.read_sql(f"Select * from VendorMaster",conn)
        for index,rows in VendorList.iterrows():
            x=fuzz.token_set_ratio(rows['description'],VendorName)
            if x>80:
                VendorId=rows['RowId']
                break
    else:
        VendorId=VendorId[0]
        VendorId=int(VendorId)

    if invoicediscountPercentage.empty==True or invoicediscountPercentage[0]==None:
        print(invoicediscountPercentage,agreedDiscountPercentage,discountCheckOutcome,invoiceDiscountValue,ApplicableDiscountValue,totalDueAmount,VendorDiscountAmount,UtilityDiscountAmount,PotentialLekageAmount,discountStatusCheckOutcome)
        discountCheckOutcome=26
        discountStatusCheckOutcome=24
        agreedDiscountPercentage=pd.read_sql(f"Select DiscountPercent,RowId From DiscountMaster where ('{jobDate}' between StartDate and EndDate) and (VendorId='{VendorId}')",conn)
        if agreedDiscountPercentage.empty==True:
            discountCheckOutcome=26
            discountStatusCheckOutcome=24
            agreedDiscountPercentage=None
            #DiscountNot IN Masters
            error+=1
        else:
            agreedDiscountPercentage=agreedDiscountPercentage['DiscountPercent'][0]
            
            insert_sql=f"Insert Into UtilityDiscountError_External (DiscountCheckOutcome,DiscountStatusCheckOutcome,CreatedBy,CreatedDate,InvoiceId,AgreedDiscountPercentage) Values (?,?,?,?,?,?) "     
            values=(discountCheckOutcome,discountStatusCheckOutcome,createdBy,createdDate,invoiceId,agreedDiscountPercentage)
            try:
                print('THis is FirstCase INsertion')
                cursor.execute(insert_sql,values)
                conn.commit()
                print('This discount is inserted',invoiceId)
                
                print('Record Inserted')
            except Exception as e:
                print(f'Error in Inserting:{str(e)}')
            

        #Discount Not Present
        error+=1
        return error
    else:

        invoicediscountPercentage=invoicediscountPercentage[0]
        invoicediscountPercentage=int(invoicediscountPercentage)
        
        agreedDiscountPercentage=pd.read_sql(f"Select DiscountPercent,RowId From DiscountMaster where ('{jobDate}' between StartDate and EndDate) and (VendorId='{VendorId}')",conn)
       
        if agreedDiscountPercentage.empty==True:
            discountCheckOutcome=26
            discountStatusCheckOutcome=24
            #DiscountNot IN Masters
            error+=2
            
            insert_sql=f"Insert Into UtilityDiscountError_External (DiscountCheckOutcome,DiscountStatusCheckOutcome,CreatedBy,CreatedDate,InvoiceId) Values (?,?,?,?,?) "     
            values=(discountCheckOutcome,discountStatusCheckOutcome,createdBy,createdDate,invoiceId)
            try:
                print('Second Case INsertion')
                cursor.execute(insert_sql,values)
                conn.commit()
                print('This discount is inserted',invoiceId)
                
                print('Record Inserted')
            except Exception as e:
                print(f'Error in Inserting:{str(e)}')
            return error
        else:
            agreedDiscountPercentage=agreedDiscountPercentage['DiscountPercent'][0]
            agreedDiscountPercentage=int(agreedDiscountPercentage)
            print('this is agreedDiscount',agreedDiscountPercentage)
            print('this is invoiceDisocunt',invoicediscountPercentage)
            if agreedDiscountPercentage==invoicediscountPercentage:
                discountCheckOutcome=1
                #Discount Matched
            else:
                #Discount Not Matched
                discountCheckOutcome=2
                error+=1
            if totalDueAmount.empty==True:
                #Amount Not FOund
                totalDueAmount=None
                discountStatusCheckOutcome=24
                error+=1
            else:
                totalDueAmount=totalDueAmount[0]
                totalDueAmount=int(totalDueAmount)
                invoiceDiscountValue=(invoicediscountPercentage/100)*totalDueAmount
                ApplicableDiscountValue=(agreedDiscountPercentage/100)*totalDueAmount
                VendorDiscountAmount=totalDueAmount-invoiceDiscountValue
                UtilityDiscountAmount=totalDueAmount-ApplicableDiscountValue
                PotentialLekageAmount=abs(UtilityDiscountAmount-VendorDiscountAmount)
                if PotentialLekageAmount==0:
                    discountStatusCheckOutcome=25
                else:
                    discountStatusCheckOutcome=24
                    error+=1
                print('UtilityDiscount',ApplicableDiscountValue)
    insert_sql=f"Insert Into UtilityDiscountError_External (InvoiceDiscountPercentage,AgreedDiscountPercentage,DiscountCheckOutcome,InvoiceDiscountValue,ApplicableDiscountValue,AmountBeforeTax,VendorDiscountAmount,UtilityDiscountAmount,PotentialLeakageAmount,DiscountStatusCheckOutcome,CreatedBy,CreatedDate,InvoiceId) Values (?,?,?,?,?,?,?,?,?,?,?,?,?) "     
    values=(invoicediscountPercentage,agreedDiscountPercentage,discountCheckOutcome,invoiceDiscountValue,ApplicableDiscountValue,totalDueAmount,VendorDiscountAmount,UtilityDiscountAmount,PotentialLekageAmount,discountStatusCheckOutcome,createdBy,createdDate,invoiceId)
    try:
        print("Third Case Insertion")
        cursor.execute(insert_sql,values)
        conn.commit()
        print('This discount is inserted',invoiceId)
        
        print('Record Inserted')
    except Exception as e:
        print(f'Error in Inserting:{str(e)}')
    
    return error
invoices=pd.read_sql(f"Select * from InvoiceHeader_External where StatusID=53",conn)
for index,rows in invoices.iterrows():
    nominationDetailId=rows['NominationDetailId']
    invoiceId=rows['RowID']
    print(invoiceId)
    errors=DiscountLeakage(invoiceId,conn)
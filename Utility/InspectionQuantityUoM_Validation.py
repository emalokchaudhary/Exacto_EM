from connection import connect_db
import pandas as pd
import numpy as np
conn=connect_db()
cursor=conn.cursor()
countValue=0
import re
import datetime
import warnings
warnings.filterwarnings('ignore')
# data1=pd.read_sql('Select  RowId,NominationDetailId,JobDate,Location,Vendor from InvoiceHeader_External where Status=53',conn)

# for index,rows in data1.iterrows():
#     r1=rows['RowId']
#     r2=r1
#     r2=int(r1)
#     # print('THis is type',type(r2))
#     result=''
#     n1=rows['NominationDetailId']
#     print('This is mainINvoice of ID',r2,'NominationDetailId-->',n1)
    
#     if np.isnan(n1):
#         break
#     createdBy=int(2)
#     createdDate=datetime.datetime.now()
#     IsActive=int(1)
def wrongquantity_uom_validation(r2,n1,conn):    
    #Here r2 is InvoiceId and n1 is NominationDetailId From From InvoiceHeader_External from Main Function
    count=0
    createdBy=2
    createdDate=datetime.datetime.now()
    IsActive=0
    cursor=conn.cursor()
    # print(r2)
    inspectionheader=pd.read_sql(f"Select InspectionId from InspectionHeader_External where InvoiceId={r2}",conn)
    if(inspectionheader.empty!=True):
        print(inspectionheader)           
        for index,row in inspectionheader.iterrows():
            invoice=pd.read_sql(f"Select UoM,UoMId,VesselName,ProductName,InvoiceQantityId,QuantityValue from InvoiceQuantity_External where InvoiceId={r2}",conn)
            Inspection=pd.read_sql(f"Select InspectionQuantityId from InspectionQuantity_External where InspectionId={row['InspectionId']}",conn)
            print(Inspection,'------>',row['InspectionId'])
            if(Inspection.empty!=True):
                for iins,irow in Inspection.iterrows():
                    if(irow['InspectionQuantityId']!=None):
                        InspectionQuantityId=irow['InspectionQuantityId']
                        detail_inspection=pd.read_sql(f"Select UoM,UoMId,InspectedQuantity,InspectionQuantityUoMId from InspectionQuantityUoM_External where InspectionQuantityId={irow['InspectionQuantityId']}",conn)
                        print(detail_inspection)
                        nomination=pd.read_sql(f"Select NominatedQuanity,UoM,UoMId,NominationQuantityId from NominationQuantity_External where NominationDetailId={n1}",conn)
                        if(nomination.empty!=True and detail_inspection.empty!=True):
                            for index,row in nomination.iterrows(): 
                                for dindex,drow in detail_inspection.iterrows():
                                    inspectionquantityuomid=drow['InspectionQuantityUoMId']
                                    variable=1
                                    sum=0
                                    uomid_check=False
                                    uomid_check_diff='Not Match'
                                    print(row['UoM'],drow['UoM'],'may be matched or not Nomination',r2,'insid->',InspectionQuantityId)
                                    if((row['UoM']!=None and drow['UoM']!=None) or (row['UoMId']!=None and drow['UoMId']!=None)):

                                        if(row['UoM']==drow['UoM'] or row['UoMId']==drow['UoMId'] or re.search(row['UoM'],drow['UoM'])):
                                            print(row['UoM'],drow['UoM'],'may be matched or not')
                                            uomid_check=True
                                            uomid_check_diff='Matched2'
                                            # IsActive=0
                                            if(drow['InspectedQuantity']!=None):
                                                less_insp_quantity=drow['InspectedQuantity']-drow['InspectedQuantity']*(5/100)
                                                great_insp_quantity=drow['InspectedQuantity']+drow['InspectedQuantity']*(5/100)
                                                print(row['NominatedQuanity'],'===------------------>',less_insp_quantity)
                                                print(row['NominatedQuanity'],'----------------->',great_insp_quantity)
                                                if(row['NominatedQuanity']!=None):
                                                    if(row['NominatedQuanity']>=less_insp_quantity and row['NominatedQuanity']<=great_insp_quantity):
                                                        # print(row['NominatedQuanity'],'===------------------>',less_insp_quantity)
                                                        # print(row['NominatedQuanity'],'----------------->',great_insp_quantity)
                                                        if(row['NominatedQuanity']>=less_insp_quantity):                                                                
                                                            qunatityvalue_check=True
                                                            quantity_check_diff='Match2'
                                                            IsActive=0
                                                            count=0                                                                
                                                        else:                                                                
                                                            qunatityvalue_check=True
                                                            IsActive=0
                                                            quantity_check_diff='Match2'
                                                            count=0                                                                
                                                        # break                                                                                            
                                                    else:                                                            
                                                        qunatityvalue_check=False
                                                        quantity_check_diff='NotMatch2'
                                                        count=count+1
                                                        # break
                                                else:
                                                    count=count+1
                                                    qunatityvalue_check=False
                                                    quantity_check_diff='Nomination NotFound'
                                            else:
                                                qunatityvalue_check=False
                                                quantity_check_diff='Not found Inspection'
                                            break          
                                        else:
                                            count=count+1
                                            uomid_check=False
                                            uomid_check_diff='Not Matched2'
                                            qunatityvalue_check=False
                                            quantity_check_diff='UOM not match2'
                                        # break
                                    else:
                                        if(row['UoM']==None):
                                            count=count+1
                                            uomid_check=False
                                            uomid_check_diff='Nomination Notfound2'
                                            qunatityvalue_check=False
                                            quantity_check_diff='UOM Not found2'    
                                        elif(drow['UoM']==None):
                                            count=count+1
                                            qunatityvalue_check=False
                                            uomid_check=False
                                            uomid_check_diff='Inspection NotFound2'
                                            quantity_check_diff='UOM not found2'
                            insert_sql=f"Insert Into InspectionQuantityUoM_Validation (CreatedBy,CreatedDate,IsActive,UoMIdCheck,UoMIdDiffReason,InspectionQuantityId,QuantityValueCheck,QuantityValueCheckDiffReason,InspectionQuantityUoMId) Values(?,?,?,?,?,?,?,?,?)"
                            values=(int(createdBy),createdDate,int(IsActive),int(uomid_check),uomid_check_diff,int(InspectionQuantityId),int(qunatityvalue_check),quantity_check_diff,int(inspectionquantityuomid))     
                            try:
                                # print(insert_sql)
                                cursor.execute(insert_sql,values)
                                conn.commit()
                                print('Record Inserted')
                            except Exception as e:
                                print(type(r2))
                                print(f'Error in Inserting:{str(e)}')                            
                            print('---------------------invoice----------->')        
                            invoice=pd.read_sql(f"Select UoM,UoMId,VesselName,ProductName,InvoiceQantityId,QuantityValue from InvoiceQuantity_External where InvoiceId={r2}",conn)
                            IsActive=1
                            if(invoice.empty!=True):
                                for invindex,invrow in invoice.iterrows():
                                    for dindex,drow in detail_inspection.iterrows():
                                        print(drow['UoM'],'->',invrow['UoM'],'Invoice',r2,'-->',InspectionQuantityId)
                                        if((drow['UoM']!=None and invrow['UoM']!=None) or (drow['UoMId']!=None and invrow['UoMId']!=None)):
                                            if(drow['UoM']==invrow['UoM'] or drow['UoMId']==invrow['UoMId']):
                                                print('yess')
                                                uomid_check=True
                                                # IsActive=0
                                                uomid_check_diff='Matched'
                                                if(drow['InspectedQuantity']!=None or invrow['QuantityValue']!=None):
                                                    if(drow['InspectedQuantity']==None):
                                                        qunatityvalue_check=False
                                                        quantity_check_diff='Not found inInspection'
                                                    elif(invrow['QuantityValue']==None):
                                                        qunatityvalue_check=False
                                                        quantity_check_diff='Not found in Invoice'
                                                    count=count+1
                                                else:
                                                    if(drow['InspectedQuantity']==invrow['QuantityValue']):
                                                        qunatityvalue_check=True
                                                        IsActive=0
                                                        quantity_check_diff='Matched'                                                            
                                                    else:
                                                        quantity_check_diff='Not Matched'
                                                        qunatityvalue_check=False
                                                        count=count+1
                                                break
                                            else:
                                                uomid_check=False
                                                uomid_check_diff='Not Matched'
                                                qunatityvalue_check=False
                                                quantity_check_diff='Not compare'
                                        else:                                
                                            uomid_check_diff='Not found Invoice'
                                            uomid_check=False
                                            quantity_check_diff='Not found Invoice'
                                            qunatityvalue_check=False
                                            count=count+1
                                insert_sql=f"Insert Into InspectionQuantityUoM_Validation (CreatedBy,CreatedDate,IsActive,UoMIdCheck,UoMIdDiffReason,InspectionQuantityId,QuantityValueCheck,QuantityValueCheckDiffReason,InspectionQuantityUoMId) Values(?,?,?,?,?,?,?,?,?)"
                                values=(int(createdBy),createdDate,int(IsActive),int(uomid_check),uomid_check_diff,int(InspectionQuantityId),int(qunatityvalue_check),quantity_check_diff,int(inspectionquantityuomid))
                                try:
                                    # print(insert_sql)
                                    cursor.execute(insert_sql,values)
                                    conn.commit()
                                    print('Record Inserted')
                                except Exception as e:
                                    print(type(r2))
                                    print(f'Error in Inserting:{str(e)}')                            
                            else:
                                uomid_check=1
                                uomid_check_diff='Not found in Invoice'
                                quantity_check_diff='Not found in Invoice'
                                quantity_check=1
                                count=count+1
                                print('NOT FOUND IN INVOICE',r2)
    return(count)
# wrongquantity_uom_validation(r2,n1,conn)
                    

from connection import connect_db
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import datetime
import numpy as np
import warnings
import re
warnings.filterwarnings("ignore")

def InspectionQuantityValidationcall(conn,invoiceId,inspectionId,nominationDetailId):
    conn=connect_db()
    createdBy=2
    cursor=conn.cursor()
    createdDate=datetime.datetime.now()
    isactive=0
    error = 0
    productIdcheck = -1
    prodcuctIdcheckreason = ''
    vesselnamecheck = -1
    vesselnamecheckreason = ''
    nominationdetail=pd.read_sql(f"Select * from NominationDetails_External where NominationDetailId={nominationDetailId}",conn)
    nominationquantity = pd.read_sql(f"Select * from NominationQuantity_External where NominationDetailId={nominationDetailId}",conn)
    inspectionHeader=pd.read_sql(f"Select * From InspectionHeader_External where InvoiceId={invoiceId}",conn)
    inspectionquantity = pd.read_sql(f"Select * From InspectionQuantity_External where InspectionId={inspectionId}",conn)
    inspectionvalidation = pd.read_sql(f"Select * From InspectionHeader_Validation where InspectionId={inspectionId}",conn)
    for index,row in nominationquantity.iterrows():
        for index1,row1 in inspectionquantity.iterrows():
            inspectionquantid = row1['InspectionQuantityId']
            nominationvesselname = row['VesselName']
            InspectionVesselname = row1['VesselName']
            NominationproductId = row['ProductId']
            Nominationproductname = row['ProductName']
            InspectionproductId = row1['ProductId']
            Inspectionproductname = row1['ProductName']
            nominationvesselname = re.sub('\s[-]\s','',nominationvesselname)
            nominationvesselname = nominationvesselname.lower()
            InspectionVesselname = re.sub('\s[-]\s','',nominationvesselname)
            InspectionVesselname = InspectionVesselname.lower()
            if NominationproductId!= None and InspectionproductId!= None:
                if NominationproductId == InspectionproductId:
                    productIdcheck = True
                    prodcuctIdcheckreason = 'ProductName Matched'
                else:
                    productIdcheck = False
                    prodcuctIdcheckreason = 'ProductName Not Matched'
                    error+=1
                    isactive+=1
            elif Nominationproductname == None or Inspectionproductname == None :
                productIdcheck = True
                prodcuctIdcheckreason = 'ProductName empty in Nomination or Inspection'

            elif Nominationproductname != None and NominationproductId == None or Inspectionproductname != None and  InspectionproductId== None:
                ratio = fuzz.partial_ratio(Nominationproductname,Inspectionproductname)
                if ratio > 80:
                    productIdcheck = True
                    prodcuctIdcheckreason = 'ProductName Matched'
                else:
                    productIdcheck = 1
                    prodcuctIdcheckreason = 'ProductName Not Matched'
                    error+=1
                    isactive+=1
            else:
                if ratio > 80:
                    productIdcheck = 0
                    prodcuctIdcheckreason = 'ProductName Matched'
                else:
                    productIdcheck = 1
                    prodcuctIdcheckreason = 'ProductName Not Matched'
                    error+=1
                    isactive+=1

            if nominationvesselname != None and InspectionVesselname != None:
                ratio=fuzz.partial_ratio(nominationvesselname,InspectionVesselname)
                if ratio>85:
                    vesselnamecheck = True
                    vesselnamecheckreason = 'VesselName Matched'
                else:
                    vesselnamecheck = False
                    vesselnamecheckreason = 'VesselName Not Matchd'
                    error+=1
                    isactive+=1
            if nominationvesselname == None or InspectionVesselname == None:
                vesselnamecheck = False
                vesselnamecheckreason = 'Vessel name missing in Nomination or Inspection'
                error+=1
                isactive+=1
            for index3,rows3 in inspectionvalidation.iterrows(): 
                inspectionheadid = rows3['InsHeadValidId']
                if isactive>0:
                    isactive=1
                else:
                    isactive=0
                insert_sql = f"Insert Into InspectionQuantity_Validation(InsHeadValidId,IsActive,ProductIdCheck,ProductIdDiffReason,VesselNameQtyCheck,VesselNameQtyDiffReason,CreatedBy,CreatedDate,InspectionQuantityId) Values(?,?,?,?,?,?,?,?,?)"
                values = (inspectionheadid,isactive,productIdcheck,prodcuctIdcheckreason,vesselnamecheck,vesselnamecheckreason,createdBy,createdDate,inspectionquantid)
                try:
                    cursor.execute(insert_sql,values)
                    conn.commit()
                    print('Record Inserted')
                except Exception as e:
                    print('Error In INsertion of Invoice',invoiceId)
                    print(f'Error in Inserting:{str(e)}')
                    

                    
    return error


def InspectionQuantityValidationcall(invoiceId,nominationDetailId,conn):
    inspection = pd.read_sql(f"Select * From InspectionHeader_External where InvoiceId={invoiceId}",conn)
    for index1,rows1 in inspection.iterrows():
    # print("reading")
        inspectionId = rows1['InspectionId']
        # print('Inspectionid',inspectionId)
        error = InspectionQuantityValidationcall(conn,invoiceId,inspectionId,nominationDetailId)
    return error
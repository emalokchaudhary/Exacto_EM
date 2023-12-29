import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import datetime
import numpy as np
import warnings

warnings.filterwarnings("ignore")

def InspectionHeader_Validation(invoiceId, nominationDetailId,conn):
    nominationdetail=pd.read_sql(f"Select * from NominationDetails_External where NominationDetailId={nominationDetailId}",conn)
    nominationId=nominationdetail['NominationId'][0]
    nominationHeader=pd.read_sql(f"Select * from NominationHeader_External where NominationId={nominationId}",conn)
    inspectionHeader=pd.read_sql(f"Select * From InspectionHeader_External where InvoiceId={invoiceId}",conn)
    # nominationNumber=nominationHeader['NominationNumber'][0]
    outNominationNumberCheck=''
    NominationNumberCheck=-1
    isactive=0
    if nominationHeader['NominationNumber'].empty!=True:
        if  nominationHeader['NominationNumber'][0]!= None:            
            InspectionNominationNumberValue=inspectionHeader['NominationNumber'][0]
            print(len(InspectionNominationNumberValue))
            print(len(nominationHeader['NominationNumber'][0]))
            if InspectionNominationNumberValue.strip()==nominationHeader['NominationNumber'][0].strip():
                print("nominationNo matched")
                outNominationNumberCheck='NominationNumber Matched'
                NominationNumberCheck=True
                
            else:
                outNominationNumberCheck='NominationNumber Not Matched'
                outcomeNominationNumber=False
                isactive+=1
         
            
        else:
            outNominationNumberCheck='NominationNumber is empty in Inspection'
            NominationNumberCheck=True
          
            
    else:
        outNominationNumberCheck='NominationNumber empty in Inspection'
        NominationNumberCheck=True
      
    
    return NominationNumberCheck,outNominationNumberCheck,isactive

    
def InspectionTripNumberValidation(nominationDetailId,invoiceId,conn):
    isactive=0
    nominationdetail=pd.read_sql(f"Select * from NominationDetails_External where NominationDetailId={nominationDetailId}",conn)
    nominationId=nominationdetail['NominationId'][0]
    nominationHeader=pd.read_sql(f"Select * from NominationHeader_External where NominationId={nominationId}",conn)
    inspectionHeader=pd.read_sql(f"Select * From InspectionHeader_External where InvoiceId={invoiceId}",conn)
    nominationTripNumber=nominationHeader['TripNumber'][0]
    TripNumberCheck=-1
    outTripNumberCheck=''
    if inspectionHeader['TripNumber'].empty!=True:
        if inspectionHeader['TripNumber'][0]!=None:
            InspectionTripNumberValue=inspectionHeader['TripNumber'][0]
            if InspectionTripNumberValue.strip()==nominationTripNumber.strip():
                outTripNumberCheck='TripNumber Matched'
                TripNumberCheck=True
            else:
                outTripNumberCheck='TripNumber Not Matched'
                TripNumberCheck=False
                isactive+=1
        else:
            outTripNumberCheck='TripNumber Empty In invoice'
            TripNumberCheck=True
    else:
        outTripNumberCheck='TripNumber Empty in Invoice'
        TripNumberCheck=True
    
    return TripNumberCheck,outTripNumberCheck,isactive

def VendorCheckException(nominationDetailId,invoiceId,conn):
    isactive=0
    nominationdetail=pd.read_sql(f"Select * from NominationDetails_External where NominationDetailId={nominationDetailId}",conn)
    nominationId=nominationdetail['NominationId'][0]
    nominationHeader=pd.read_sql(f"Select * from NominationHeader_External where NominationId={nominationId}",conn)
    inspectionHeader=pd.read_sql(f"Select * From InspectionHeader_External where InvoiceID={invoiceId}",conn)
    #If id updation Needed
    # VendorList=pd.read_sql(f"Select * From VendorMaster",conn)
    # vendorListdescription=VendorList['description'].tolist()
    print('Invoice Id',invoiceId)
    NominationVendor=nominationdetail['Vendor'][0]
    InvoiceVendor=inspectionHeader['Vendor'][0]
    NominationVendorId=nominationdetail['VendorId']
    InvoiceVendorId=inspectionHeader['VendorId']
    VendorIdCheck=-1
    outcomeVendorId=''
    if InvoiceVendorId.empty!=True:
        if   InvoiceVendorId[0]!=None:
            InvoiceVendorId=inspectionHeader['VendorId'][0]
            print(InvoiceVendorId,'INvoiceID')
            if InvoiceVendorId==NominationVendorId[0]:
                print('THis is equal Vendor Id')
                outcomeVendorId='Vendor Matched'
                VendorIdCheck=True
                
            else:
                
                outcomeVendorId='Vendor Not Matched'
                VendorIdCheck=False
                isactive+=1
        else:
            
            outcomeVendorId='Vendor is None in Inspection '
            # VendorIdCheck=0
            # result=process.extractOne(InvoiceVendor,vendorListdescription)[0]
            #We can Update id here 
            ratio=80
            ratioValue=fuzz.partial_token_set_ratio(NominationVendor,InvoiceVendor)
            if ratioValue>ratio:
                outcomeVendorId='VendorName Matched'
                VendorIdCheck=True
            else:
                outcomeVendorId='VendorName Not Matched'
                VendorIdCheck=False
                isactive+=1
    else:
        outcomeVendorId='Vendor Not Available'
        VendorIdCheck=True
    
    return VendorIdCheck,outcomeVendorId,isactive
    
def locationCheckingValidation(nominationDetailId,invoiceId,conn):
    LocationReason=''
    LocationCheck=''
    isactive=0
    nominationdetail=pd.read_sql(f"Select * from NominationDetails_External where NominationDetailId={nominationDetailId}",conn)   
    inspectionHeader=pd.read_sql(f"Select * From InspectionHeader_External where InvoiceID={invoiceId}",conn)
    LocationNomination=nominationdetail['Location'][0]
    NominationLocationId=nominationdetail['LocationId']
    if NominationLocationId.empty==True:
        NominationLocationId=None
    else:
        NominationLocationId=nominationdetail['LocationId'][0]
    LocationInvoice=inspectionHeader['Location'][0]
    InspectionLocationId=inspectionHeader['LocationId']
    if InspectionLocationId.empty==True:
        InspectionLocationId=None
    else:
        InspectionLocationId=inspectionHeader['LocationId'][0]
    if NominationLocationId!=None and InspectionLocationId!=None:
        if NominationLocationId==InspectionLocationId:
            LocationCheck=True
            LocationReason='Location Matched'
        else:
            LocationReason='Location Not Matched'
            LocationCheck=False
            isactive+=1
    elif LocationNomination==None or LocationInvoice==None:
        LocationCheck=False
        LocationReason='Location in Invoice or Nomination Empty'
        isactive+=1
    elif NominationLocationId==None and LocationNomination!=None:

        ratio=fuzz.partial_ratio(LocationNomination,LocationInvoice)
        if ratio>80:
            LocationReason='Location Matched'
            LocationCheck=True
        else:
            LocationCheck=False
            LocationReason='Location Not Matched'
            isactive+=1
    else:
        ratio=fuzz.partial_ratio(LocationNomination,LocationInvoice)
        if ratio>80:
            LocationReason='Location Matched'
            LocationCheck=True
        else:
            LocationCheck=False
            isactive+=1
            LocationReason='Location Not Matched'
    return LocationCheck,LocationReason,isactive

def InspectionVendorReferenceNumber_Validation(nominationDetailId,invoiceId,conn):
    isactive=0
    nominationdetail=pd.read_sql(f"Select * from NominationDetails_External where NominationDetailId={nominationDetailId}",conn)
    nominationquantity = pd.read_sql(f"Select * from NominationQuantity_External where NominationDetailId={nominationDetailId}",conn)
    nominationId=nominationdetail['NominationId'][0]
    nominationHeader=pd.read_sql(f"Select * from NominationHeader_External where NominationId={nominationId}",conn)
    inspectionHeader=pd.read_sql(f"Select * From InspectionHeader_External where InvoiceId={invoiceId}",conn)
    # nominationNumber=nominationHeader['NominationNumber'][0]
    outNominationKeyCheck=''
    NominationKeyCheck=-1
    if nominationquantity['NominationKey'].empty!=True:
        if  nominationquantity['NominationKey'][0]!= None:            
            InspectionNominationKeyValue=inspectionHeader['VendorReferenceNumber'][0]

            print(InspectionNominationKeyValue)
            print(nominationquantity['NominationKey'][0])
            ratio=fuzz.partial_ratio(nominationquantity['NominationKey'][0],InspectionNominationKeyValue)
            if ratio>70:
                print("VendorReference")
                outNominationKeyCheck='VendorRefNo Matched'
                NominationKeyCheck=True
                
            else:
                outNominationKeyCheck='VendorRefNo Not Matched'
                NominationKeyCheck=False
                isactive+=1
         
            
        else:
            outNominationKeyCheck='VendorRefNo empty in Inspection'
            NominationKeyCheck=True
          
            
    else:
        outNominationKeyCheck='VendorRefNo empty in Inspection'
        NominationKeyCheck=True
      
    
    return NominationKeyCheck,outNominationKeyCheck,isactive



def InspectionHeaderValidation(invoiceId,nominationDetailId,conn):
    error=0
    createdBy=2
    cursor=conn.cursor()
    createdDate=datetime.datetime.now()
    isactive=0    

    inspection = pd.read_sql(f"Select * From InspectionHeader_External where InvoiceId={invoiceId}",conn)
    for index1,rows1 in inspection.iterrows():
    # print("reading")
        inspectionId = rows1['InspectionId']
        # print('#######',inspectionId)
        # print("before call am here!")
        NominationNumberCheck,outNominationNumberCheck,isactive1=InspectionHeader_Validation(invoiceId,nominationDetailId,conn)
        TripNumberCheck,outTripNumberCheck,isactive2 = InspectionTripNumberValidation(nominationDetailId,invoiceId,conn)
        VendorIdCheck,outcomeVendorId,isactive3 = VendorCheckException(nominationDetailId,invoiceId,conn)
        LocationCheck,LocationReason,isactive4 = locationCheckingValidation(nominationDetailId,invoiceId,conn)
        NominationKeyCheck,outNominationKeyCheck,isactive5 = InspectionVendorReferenceNumber_Validation(nominationDetailId,invoiceId,conn)
        if isactive1>0 or isactive2>0 or isactive3>0 or isactive4>0 or isactive5>0:
            isactive=1
        else:
            isactive=0

        insert_sql=f"Insert Into InspectionHeader_Validation(InvoiceId,NominationNumberCheck,NominationNumberDiffReason,TripNumberCheck,TripNumberDiffReason,VendorIdCheck,VendorIdDiffReason,LocationIdCheck,LocationIdDiffReason,VendorReferenceNumberCheck,VendorReferenceNumberDiffReason,CreatedBy,CreatedDate,InspectionId,IsActive) Values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        values=(invoiceId,NominationNumberCheck,outNominationNumberCheck,TripNumberCheck,outTripNumberCheck,VendorIdCheck,outcomeVendorId,LocationCheck,LocationReason,NominationKeyCheck,outNominationKeyCheck,createdBy,createdDate,inspectionId,isactive)
        try:

            cursor.execute(insert_sql,values)
            conn.commit()
            print('Record Inserted')
        except Exception as e:
            print('Error In INsertion of Invoice',invoiceId)
            print(f'Error in Inserting:{str(e)}')
        if  NominationNumberCheck> 0 or  TripNumberCheck>0 or VendorIdCheck>0 or LocationCheck>0 or NominationKeyCheck>0:
            error = 1
        else:
            error = 0
    return error


# invoice=pd.read_sql(f"Select * From InvoiceHeader_External where Status = 53",conn)
# for index,rows in invoice.iterrows():
#     nominationDetailId=rows['NominationDetailId']
#     invoiceId=rows['RowID']
#     InspectionHeaderValidation(conn,invoiceId,nominationDetailId)
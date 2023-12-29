import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import datetime
import numpy as np
import warnings



warnings.filterwarnings("ignore")
def activityInvoiceValidation(nominationDetailId,invoiceId,isactive,conn):
    
    nominationActivityId=''
    nominationActivity=''
    invoiceActivity=''
    invoiceActivityId=''
    activityIdCheck=''
    activityIdReason=''
    nominationdetail=pd.read_sql(f"Select * from NominationDetails_External where NominationDetailId={nominationDetailId}",conn)
    invoiceHeader=pd.read_sql(f"Select * From InvoiceHeader_External where RowID={invoiceId}",conn)
    nominationActivity=nominationdetail['Activity'][0]
    if nominationdetail['ActivityId'].empty==True:
        nominationActivityId=None
    else:
        nominationActivityId=nominationdetail['ActivityId'][0]
    invoiceActivityId=invoiceHeader['ActivityId']
    if invoiceActivityId.empty!=True or invoiceActivityId!=None:
        
        invoiceActivity=invoiceHeader['Activity'][0]
        invoiceActivity=invoiceActivity.lower()
        nominationActivity=nominationActivity.lower()
        ratio=fuzz.partial_ratio(invoiceActivity,nominationActivity)
        ratioValue=90
        if ratio>ratioValue:
            activityIdReason='ActivityId Matched'
            activityIdCheck=True
        else:
            activityIdReason='ActivityId Not Matched'
            activityIdCheck=False
            isactive+=1

    else:

        if nominationActivityId!=None:
            if invoiceActivityId==nominationActivityId:
                activityIdCheck=True
                activityIdReason='ActivityId Matched'
                
            else:
                activityIdCheck=False
                activityIdReason='ActivityId Not Matched'
                isactive+=1
        else:
            invoiceActivity=invoiceHeader['Activity'][0]
            invoiceActivity=invoiceActivity.lower()
            nominationActivity=nominationActivity.lower()
            ratio=fuzz.partial_ratio(invoiceActivity,nominationActivity)
            ratioValue=90
            if ratio>ratioValue:
               
                activityIdReason='ActivityId Matched'
                activityIdCheck=True
                
            
            else:
                activityIdReason='ActivityId Not Matched'
               
                activityIdCheck=False
                isactive+=1
    return activityIdCheck,activityIdReason,isactive
            
def NominationNumberValidation(nominationDetailId,invoiceId,isactive,conn):
    nominationdetail=pd.read_sql(f"Select * from NominationDetails_External where NominationDetailId={nominationDetailId}",conn)
    nominationId=nominationdetail['NominationId'][0]
    nominationHeader=pd.read_sql(f"Select * from NominationHeader_External where NominationId={nominationId}",conn)
    invoiceHeader=pd.read_sql(f"Select * From InvoiceHeader_External where RowID={invoiceId}",conn)
    nominationNumber=nominationHeader['NominationNumber'][0]
    outNominationNumberCheck=''
    NominationNumberCheck=-1
    if invoiceHeader['NominationNumber'].empty!=True:
        if  invoiceHeader['NominationNumber'][0]!= None:            
            InvoiceNominationNumberValue=invoiceHeader['NominationNumber'][0]
            if InvoiceNominationNumberValue==nominationHeader['NominationNumber'][0]:
                outNominationNumberCheck='NominationNumber Matched'
                NominationNumberCheck=True
            else:
                outNominationNumberCheck='NominationNumber not Matched'
                outcomeNominationNumber=False
                isactive+=1
         
            
        else:
            outNominationNumberCheck='NominationNumber empty in Invoice'
            NominationNumberCheck=True
            
    else:
        outNominationNumberCheck='NominationNumber empty in Invoice'
        NominationNumberCheck=True
      
    
    return NominationNumberCheck,outNominationNumberCheck,isactive

def NominationTripNumberValidation(nominationDetailId,invoiceId,isactive,conn):
    nominationdetail=pd.read_sql(f"Select * from NominationDetails_External where NominationDetailId={nominationDetailId}",conn)
    nominationId=nominationdetail['NominationId'][0]
    nominationHeader=pd.read_sql(f"Select * from NominationHeader_External where NominationId={nominationId}",conn)
    invoiceHeader=pd.read_sql(f"Select * From InvoiceHeader_External where RowID={invoiceId}",conn)
    nominationTripNumber=nominationHeader['TripNumber'][0]
    TripNumberCheck=-1
    outTripNumberCheck=''
    if invoiceHeader['TripNumber'].empty!=True:
        if invoiceHeader['TripNumber'][0]!=None:
            InvoiceTripNumberValue=invoiceHeader['TripNumber'][0]
            if InvoiceTripNumberValue==nominationTripNumber:
                outTripNumberCheck='TripNumber Matched'
                TripNumberCheck=True
            else:
                outTripNumberCheck='TripNumber Not Matched'
                TripNumberCheck=False
                isactive+=1
        else:
            outTripNumberCheck='TripNumber Empty Invoice'
            TripNumberCheck=True
    else:
        outTripNumberCheck='TripNumber Empty Invoice'
        TripNumberCheck=True
    
    return TripNumberCheck,outTripNumberCheck,isactive

def VendorCheckException(nominationDetailId,invoiceId,isactive,conn):
    nominationdetail=pd.read_sql(f"Select * from NominationDetails_External where NominationDetailId={nominationDetailId}",conn)
    nominationId=nominationdetail['NominationId'][0]
    nominationHeader=pd.read_sql(f"Select * from NominationHeader_External where NominationId={nominationId}",conn)
    invoiceHeader=pd.read_sql(f"Select * From InvoiceHeader_External where RowID={invoiceId}",conn)
    #If id updation Needed
    # VendorList=pd.read_sql(f"Select * From VendorMaster",conn)
    # vendorListdescription=VendorList['description'].tolist()
    print('Invoice Id',invoiceId)
    NominationVendor=nominationdetail['Vendor'][0]
    InvoiceVendor=invoiceHeader['Vendor'][0]
    NominationVendorId=nominationdetail['VendorId']
    InvoiceVendorId=invoiceHeader['VendorId']
    VendorIdCheck=-1
    outcomeVendorId=''
    if InvoiceVendorId.empty!=True or InvoiceVendor!=None:
        if   InvoiceVendorId[0]!=None:
            InvoiceVendorId=invoiceHeader['VendorId'][0]
            
            if InvoiceVendorId==NominationVendorId[0]:
                
                outcomeVendorId='VendorId Matched'
                VendorIdCheck=True
            else:
                
                outcomeVendorId='VendorId Not Matched'
                VendorIdCheck=False
                isactive+=1
        else:
            
            outcomeVendorId='VendorId is None in Invoice '
            # VendorIdCheck=0
            # result=process.extractOne(InvoiceVendor,vendorListdescription)[0]
            #We can Update id here 
            ratio=80
            ratioValue=fuzz.partial_token_set_ratio(NominationVendor,InvoiceVendor)
            if ratioValue>ratio:
                outcomeVendorId='VendorId Matched'
                VendorIdCheck=True
                
            else:
                outcomeVendorId='VendorId Not Matched'
                VendorIdCheck=False
                isactive+=1
    else:
        outcomeVendorId='VendorId Not Found'
        VendorIdCheck=False
        isactive+=1
        
    
    return VendorIdCheck,outcomeVendorId,isactive
    
    
def affiliateCheckValidation(nominationDetailId,invoiceId,isactive,conn):
    createdBy=2
    createdDate=datetime.datetime.now()
    affilateReason=''
    affilateCheck=''
    nominationdetail=pd.read_sql(f"Select * from NominationDetails_External where NominationDetailId={nominationDetailId}",conn)
    nominationId=nominationdetail['NominationId'][0]
    nominationHeader=pd.read_sql(f"Select * from NominationHeader_External where NominationId={nominationId}",conn)
    invoiceHeader=pd.read_sql(f"Select * From InvoiceHeader_External where RowID={invoiceId}",conn)
    affilateIdNomination=nominationdetail['AffiliateId']
    affilateIdInvoice=invoiceHeader['AffiliateId']
    if (affilateIdNomination.empty==True or affilateIdNomination[0]==None):
        affilateReason='AffiliateId Empty in Nomination'
        affilateCheck=False
        isactive+=1
    elif affilateIdNomination.empty!=True and affilateIdInvoice.empty==True:
        affilateReason='Invoice AffilateId is Empty'
        affilateCheck=True
    elif (affilateIdNomination.empty!=True and affilateIdInvoice.empty!=True):
        
        affilateIdNomination=(nominationdetail['AffiliateId'][0])
        affilateIdInvoice=(invoiceHeader['AffiliateId'][0])
        if affilateIdNomination!=None and affilateIdInvoice!=None:
            if affilateIdInvoice==affilateIdNomination:
                affilateReason='AffilateId Matched'
                affilateCheck=True
                
            else:
                affilateReason='AffilateId Not Matched'
                affilateCheck=False
                isactive+=1
        else:
            affilateReason='AffiliateId Empty In Inovice or Nomination'
            affilateCheck=False
            isactive+=1
    
    return affilateCheck,affilateReason,isactive

def locationCheckingValidation(nominationDetailId,invoiceId,isactive,conn):
    LocationReason=''
    LocationCheck=''
    nominationdetail=pd.read_sql(f"Select * from NominationDetails_External where NominationDetailId={nominationDetailId}",conn)   
    invoiceHeader=pd.read_sql(f"Select * From InvoiceHeader_External where RowID={invoiceId}",conn)
    LocationNomination=nominationdetail['Location'][0]
    NominationLocationId=nominationdetail['LocationId']
    if NominationLocationId.empty==True:
        NominationLocationId=None
    else:
        NominationLocationId=nominationdetail['LocationId'][0]
    LocationInvoice=invoiceHeader['Location'][0]
    InvoiceLocationId=invoiceHeader['LocationId']
    if InvoiceLocationId.empty==True:
        InvoiceLocationId=None
    else:
        InvoiceLocationId=invoiceHeader['LocationId'][0]
    if NominationLocationId!=None and InvoiceLocationId!=None:
        if NominationLocationId==InvoiceLocationId:
            LocationCheck=True
            LocationReason='Location Matched'
        else:
            LocationReason='Location Not Matched'
            LocationCheck=False
            isactive+=1
    elif LocationNomination==None or LocationInvoice==None:
        LocationCheck=False
        isactive+=1
        LocationReason='Location in Invoice or Nomination Empty'
    elif NominationLocationId==None and LocationNomination!=None:

        ratio=fuzz.partial_ratio(LocationNomination,LocationInvoice)
        if ratio>80:
            LocationReason='Location Matched'
            LocationCheck=True
        else:
            LocationCheck=False
            isactive+=1
            LocationReason='Location Not Matched'
    else:
        ratio=fuzz.partial_ratio(LocationNomination,LocationInvoice)
        if ratio>80:
            LocationReason='Location Matched'
            LocationCheck=True
        else:
            LocationCheck=False
            LocationReason='Location Not Matched'
            isactive+=1
    return LocationCheck,LocationReason,isactive


def typeOfInspectionValidation(nominationDetailId,invoiceId,isactive,conn):
    createdBy=2
    createdDate=datetime.datetime.now()
    InspectionReason=''
    InspectionIdInvoice=''
    InspectionType=''
    InspectionCheck=''
    invoiceList={}
    cursor=conn.cursor()
    nominationdetail=pd.read_sql(f"Select * from NominationDetails_External where NominationDetailId={nominationDetailId}",conn)   
    invoiceHeader=pd.read_sql(f"Select * From InvoiceHeader_External where RowID={invoiceId}",conn)
    invoiceQuantityItems=pd.read_sql(f"Select * From InvoiceQuantity_External where InvoiceId={invoiceId}",conn)
    invoiceQualityItems=pd.read_sql(f"Select * From InvoiceQuality_External where InvoiceId={invoiceId}",conn)
    if (invoiceQuantityItems.empty!=True and (invoiceQuantityItems['Description'].empty!=True or invoiceQuantityItems['QuantityValue'].empty!=True)):
        invoiceList['Quantity']=True
    if (invoiceQualityItems.empty!=True and(invoiceQualityItems['TestMethod'].empty!=True or invoiceQualityItems['TestName'].empty!=True)):
        invoiceList['Quality']=True
    print(invoiceList)
    result=''
    for i in invoiceList.keys():
        result+=i+' '
    if 'quantity' in result.lower() and 'quality' not in result.lower():
        InspectionIdInvoice=5
        InspectionType='Quantity'
    elif 'quantity' in result.lower() and 'quality' in result.lower():
        InspectionIdInvoice=7
        InspectionType='Quantity & Quality'
    elif 'quality' in result.lower() and 'quantity' not in result.lower():
        InspectionIdInvoice=6
        InspectionType='Quality'
        #Insertion for Invoice
    insert_sql=f"Update InvoiceHeader_External Set TypeOfInspection=?,TypeOfInspectionId=? where RowID=?"
    values=(InspectionType,InspectionIdInvoice,invoiceId)
    if len(invoiceList)!=0:
        try:
            cursor.execute(insert_sql,values)
            conn.commit()
            print('Record Inserted')        
        except Exception as e:
            print(f'Exception caught {str(e)} ')
    typeOfInspectionNomination=nominationdetail['TypeOfInspectionId'][0]
    if typeOfInspectionNomination==InspectionIdInvoice:
        InspectionCheck=True
        
        InspectionReason='TypeOfInspection Matched'
    else:
        InspectionCheck=False
        isactive+=1
        InspectionReason='TypeOfInspection Not Match '
    return InspectionCheck,InspectionReason,isactive

def invoiceHeaderException(invoiceId,nominationDetailId,conn):
    createdBy=2
    cursor=conn.cursor()
    createdDate=datetime.datetime.now()
    isactive=0
    error=0
    activityIdCheck,activityReason,isactive1=activityInvoiceValidation(nominationDetailId,invoiceId,isactive,conn)
    affilateIdCheck,affilateIdReason,isactive2=affiliateCheckValidation(nominationDetailId,invoiceId,isactive,conn)
    nominationNumberCheck,nominationNumberReason,isactive3=NominationNumberValidation(nominationDetailId,invoiceId,isactive,conn)
    tripNumberCheck,tripNumberReason,isactive4=NominationTripNumberValidation(nominationDetailId,invoiceId,isactive,conn)
    vendorCheck,VendorReason,isactive5=VendorCheckException(nominationDetailId,invoiceId,isactive,conn)
    locationCheck,locationReason,isactive6=locationCheckingValidation(nominationDetailId,invoiceId,isactive,conn)
    typeCheck,typeCheckReason,isactive7=typeOfInspectionValidation(nominationDetailId,invoiceId,isactive,conn)    
    if isactive1>0 or isactive2>0 or isactive3>0 or isactive4>0 or isactive5>0 or isactive6>0 or isactive7>0:
        isactive=1
    else:
        isactive=0
    insert_sql=f"Insert Into InvoiceHeader_Validation(ActivityIdCheck,ActivityIdDifferenceReason,AffiliateIdCheck,AffiliateIdDifferenceReason,CreatedBy,CreatedDate,TypeOfInspectionIdCheck,TypeOfInspectionIdDifferenceReason,LocationIdCheck,LocationIdDifferenceReason,NominationNumberCheck,NominationNumberDifferenceReason,TripNumberCheck,TripNumberDifferenceReason,VendorIdCheck,VendorIdDifferenceReason,InvoiceId,IsActive) Values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    values=(activityIdCheck,activityReason,affilateIdCheck,affilateIdReason,createdBy,createdDate,typeCheck,typeCheckReason, locationCheck,locationReason,nominationNumberCheck,nominationNumberReason,tripNumberCheck,tripNumberReason,vendorCheck,VendorReason,invoiceId,isactive)
    try:

        cursor.execute(insert_sql,values)
        conn.commit()
        print('Record Inserted')
    except Exception as e:
        print('Error In Insertion of Invoice',invoiceId)
        print(f'Exception Caught {str(e)}')
    if activityIdCheck>0 or affilateIdCheck>0 or nominationNumberCheck>0 or tripNumberCheck>0 or vendorCheck>0 or locationCheck>0 or typeCheck>0:
        
        error=1

    return error

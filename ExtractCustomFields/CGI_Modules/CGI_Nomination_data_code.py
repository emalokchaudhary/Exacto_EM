from db_connection import connect_db
from CGI_nomination_headers_1 import Nomination_header_field
from CGI_Nomination_Table_main import main_call
from CGI_Nomiantion_final_table_exxon import Quality_line_items
import uuid
import re
import os,sys
import datetime
from variable import *
sys.path.insert(0,'../..')

Curr_time= datetime.datetime.now()
print('toscana user variable',value_createdby)

# path = r'/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/20E552683v.1/20E552683v.1.text'
# path = r'/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/20E546055v.2/20E546055v.2.text'
# path = r'/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/20E545381v.2/20E545381v.2.text'
path = r'/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/20E540636v.1/20E540636v.1.text'
def Nomination_Insertion(path):

    file=open(path,'r',encoding='windows-1258')
    read=file.read()
    lines=read.split('\n')

    conn = connect_db()
    cursor = conn.cursor()
    # row = Nomination_header_field(lines)
    match = re.search('\s*(Documentary Instructions:).*',read)
    if match:
        data_1 = Nomination_header_field(lines)
        data_2 = main_call(read)
        data_3 = Quality_line_items(lines)
        # print('**********************************',data_3)
        UUID = str(uuid.uuid4().hex[:8])
        data_1['status'] = 0
        data_1['nom_hd_uuid'] = UUID
        # entry to exacto header table
        insert_statement_1 = "INSERT INTO exacto_nom_hd(nom_hd_uuid, TripNumber, NominationNumber, Region, status  ) VALUES (?, ?, ?, ?, ?)"
########### For Toscana insertion NominationHeader_External
        # insert_toscana_1 = "INSERT INTO NominationHeader_External ( NominationNumber,TripNumber, Region, CreatedBy, CreatedDate  ) VALUES (?, ?, ?, ?, ?)"  
        # values_toscana_1 = (data_1.get('NominationNumber',''),data_1.get('TripNumber',''), data_1.get('Region',''), value_createdby, Curr_time)
        # cursor.execute(insert_toscana_1, values_toscana_1)
        #getting inserted primary key  
        # NomID = "select NominationId from NominationHeader_External where NominationNumber = data_1.get('NominationNumber','') and ,data_1.get('TripNumber','')"
        # a = cursor.execute(NomID)
        # l = ''
        # for i in a:
        #         l = i[0]

###############################
        values_1 = (data_1.get('nom_hd_uuid',''),data_1.get('TripNumber',''), data_1.get('NominationNumber',''), data_1.get('Region',''), data_1.get('status',0))
        cursor.execute(insert_statement_1, values_1)

        insert_statement_2 = "INSERT INTO exacto_nom_li(nom_hd_uuid, ActivityType, VendorName , ProductName, NominatedQuantity, UnitOfMeasure, JobLocation, JobDate ,EmAffiliates, NominationKey, VesselName, status ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        
########### For Toscana insertion NominationDetails_External
#insert_toscana_2 = "INSERT INTO NominationDetails_External(NominationId, Vendor , Activity, Inspection, , Location, ExtractedETA ,BillTo, CreatedBy, CreatedDate ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
# insert_toscana2_3 = "INSERT INTO NominationQuantity_External(NominationDetailId ,VesselName, NominationKey, ProductName, NominatedQuanity, UoM ,CostSharePercent, CreatedBy, CreatedDate ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
# insert_toscana_3 = "INSERT INTO NominationQuality_External( NominationDetailId, VesselName,  NominationKey ,ProductName, TestName ,TestMethod ,SetNumber ,SetDescription ,SampleLocation ,Comments, CostSharePercent , CreatedBy, CreatedDate ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,? ,? ,?, ?)"
#######################
        insert_statement_3 = "INSERT INTO exacto_nom_ql_li( nom_hd_uuid ,SetNo ,SetDescription ,SampleLocation ,VendorName ,TestName ,TestCode ,Comments,status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        
        for table_data in data_2:

            for row in table_data:
                row['status'] = 0
                row['nom_hd_uuid'] = UUID
                print(row)
                values_2 = (row.get('nom_hd_uuid',''), row.get('ActivityType',''), row.get('VendorName',''),  row.get('ProductName',''), row.get('NominatedQuantity',''), row.get('UnitOfMeasure',''), row.get('JobLocation',''), row.get('JobDate','')  ,row.get('EmAffiliates',''), row.get('NominationKey',''), row.get('VesselName','') ,row.get('status',0))
                cursor.execute(insert_statement_2, values_2)
################## For Toscana 
# # insert_toscana_2 = "INSERT INTO NominationDetails_External(NominationId, Vendor , Activity, Inspection, , Location, ExtractedETA ,BillTo, CreatedBy, CreatedDate ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
#                 values_toscana_2 = (l, row.get('VendorName',''), row.get('ActivityType',''),row.get('Inspection',''),  row.get('JobLocation',''), row.get('JobDate','')  ,row.get('EmAffiliates',''), 1, Curr_time)
#                 cursor.execute(insert_toscana_2, values_toscana_2)
# # insert_toscana2_3 = "INSERT INTO NominationQuantity_External(NominationDetailId ,VesselName, NominationKey, ProductName, NominatedQuanity, UoM ,CostSharePercent, CreatedBy, CreatedDate ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
#                 values_toscana2_3 = (row.get('VesselName',''),  row.get('NominationKey',''), row.get('ProductName',''), row.get('NominatedQuantity',''), row.get('UnitOfMeasure',''),1, Curr_time)
#                 cursor.execute(insert_toscana2_3, values_toscana2_3)

######################################
              


        for table_data in data_3:

            for row in table_data:
                row['status'] = 0
                row['nom_hd_uuid'] = UUID

                values_3 = (row.get('nom_hd_uuid',''), row.get('SetNo',''), row.get('SetDescription','') ,row.get('SampleLocation',''),row.get('VendorName','') ,row.get('TestName',''), row.get('TestCode',''), row.get('Comments',''), row.get('status',0))
                cursor.execute(insert_statement_3, values_3)
################## For Toscana 
            # NominationQuality_External( NominationDetailId, VesselName,  NominationKey ,ProductName, TestName ,TestMethod ,SetNumber ,SetDescription ,SampleLocation ,Comments, CostSharePercent , CreatedBy, CreatedDate )
                # values_toscana_3 = (row.get('TestName',''), row.get('TestCode','')row.get('SetNo',''), row.get('SetDescription','') ,row.get('SampleLocation','') , row.get('Comments',''), 1, Curr_time)
                # cursor.execute(insert_toscana_3, values_toscana_3)

        conn.commit()
        cursor.close()
        conn.close()

Nomination_Insertion(path)


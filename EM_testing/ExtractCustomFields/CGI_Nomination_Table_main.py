import re
import os
import sys
sys.path.insert(0,"./")
# from ExtractCustomFields.CGI_nomination_Parcel import Nomination_field
# from ExtractCustomFields.CGI_Nomination_Parcel_Summery import parcel_data
from CGI_nomination_Parcel import Nomination_field
from CGI_Nomination_Parcel_Summery import parcel_data
# from EM_Product.ips.invoiceProduct_solution.apps.db_connection import connect_db as conn

# path = r"/datadrive/EM_testing/ExtractCustomFields/20E545381v.2.text"
# path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/CGI/CHEM-US/300784/20E536366v.1.text"
# path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/EU/16001200075415/21E563724v.1.text"
# path = r'/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/20E545381v.2/20E545381v.2.text'
# file=open(path,'r',encoding='windows-1258')
# read=file.read()

def read_file(filepath):
    with open(filepath, 'r', encoding="utf-8") as f:
        text_data = f.read()
        
    return text_data


def main_call(read):
    lines=read.split('\n')

    match = re.search('Parcel Summary\s*',read)
    
    try:
        if match:
            # print(match.group())
            print('yes')
            a = parcel_data(lines)
            return a
        else:
            print('No')
            b = Nomination_field(lines)
            return b
    except Exception as e:
        print("Error in parcal summery",e)
        pass

# print('@@@@@@@@@@@@@@@@@@$$$$$$$$$$$',main_call(read_file(path)))
# data = main_call(read)

# cursor = conn.cursor()

# insert_statement = "INSERT INTO Exacto_cgi_nomination_quality_lineitem ('VesselName','JobLocation','ActivityType','ProductName','JobDate','VendorName','NominatedQuanity','UnitOfMeasure','EmAffiliates','NominationKey ) VALUES (?, ?, ?, ?, ?, ?)"

 



# for table_data in data:

#     for row in table_data:

#         values = (row.get('set_description',''), row.get('set_no',''), row.get('sample_location',''), row.get('test',''), row.get('methods',''), row.get('comment',''))

#         cursor.execute(insert_statement, values)

        

        

# conn.commit()

 



# cursor.close()

# conn.close()

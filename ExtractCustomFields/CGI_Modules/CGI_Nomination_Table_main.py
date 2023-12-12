import re
import os
import sys,traceback
sys.path.insert(0,"./")
from ExtractCustomFields.CGI_Modules.CGI_nomination_Parcel import Nomination_field
from ExtractCustomFields.CGI_Modules.CGI_Nomination_Parcel_Summery import parcel_data
# from CGI_nomination_Parcel import Nomination_field
# from CGI_Nomination_Parcel_Summery import parcel_data
# from EM_Product.ips.invoiceProduct_solution.apps.db_connection import connect_db as conn


# path = r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/CGI/CHEM-US/300784/20E536366v.1.text'
# path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/CGI/CHEM-US/303776/20E552683v.1.text"
# file=open(path,'r',encoding='windows-1258')
# read=file.read()


def main_call(read):
    lines=read.split('\n')

    match = re.search('Parcel Summary\s*',read)
    
    try:
        if match:

            # print(match.group())
            # print('yes')
            a = parcel_data(lines)
            return a
        else:
            # print('No')
            b = Nomination_field(lines)
            # print(b)
            return b
    except Exception as e:
        traceback.print_exc()
        print("Error in parcal summery",e)
        pass



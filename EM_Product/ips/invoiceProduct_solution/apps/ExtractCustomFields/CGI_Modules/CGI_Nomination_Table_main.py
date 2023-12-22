import re
import os
import sys,traceback
sys.path.insert(0,"./")
from ExtractCustomFields.EM_logging import logger
from ExtractCustomFields.CGI_Modules.CGI_nomination_Parcel import Nomination_field
from ExtractCustomFields.CGI_Modules.CGI_Nomination_Parcel_Summery import parcel_data
# from CGI_nomination_Parcel import Nomination_field
# from CGI_Nomination_Parcel_Summery import parcel_data
# from EM_Product.ips.invoiceProduct_solution.apps.db_connection import connect_db as conn


def main_call(read):
    lines=read.split('\n')
    match = re.search('Parcel Summary\s*',read)    
    try:
        if match:
            # print(match.group())
            # print('yes')
            a = parcel_data(lines)
            logger.info(f'Parcel data extraction - {a}')
            return a
        else:
            # print('No')
            b = Nomination_field(lines)
            # print(b)
            logger.info(f'Parcel data extraction (pracel summary not available) - {b}')
            return b
    except Exception as e:
        logger.info("Error in parcal summery")
        logger.exception(e)
        traceback.print_exc()
        print("Error in parcal summery",e)
        pass



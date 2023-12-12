import os
import re
import sys
import traceback


def read_file(filepath):
    with open(filepath, 'r', encoding="utf-8") as f:
        text_data = f.read()
        
    return text_data

def CGI_classifcation(text_data):
    data = text_data
    document_type=""
    try: 
        if re.search('TRIP:', data, re.IGNORECASE):
            document_type="Nomination"
            print("This a nomination document")

        elif re.search('Inv No', data, re.IGNORECASE):
            document_type="Invoice"
            print("THIS IS INVOICE DOCUMENT")

        elif re.search('Certificate of Analysis', data, re.IGNORECASE):
            print("THIS IS INSPECTION DOCUMENT FOR QUALITY")
            document_type = "Quality"   

        elif re.search('RECAPITULATION', data, re.IGNORECASE):
            print("THIS IS INSPECTION DOCUMENT FOR QUANTITY")
            document_type = "Quantity"
            
        else:
            print("this doc is not belong to ")
            # document_type ="Not classified"
            # pass
    except Exception as e:
        traceback.print_exc()
        print("Error in classfication ", e)
        pass

    return document_type
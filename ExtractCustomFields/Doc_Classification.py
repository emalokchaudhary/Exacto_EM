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
    a=1
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

        elif a==1:
            try:
                if re.search('RECAPITULATION' , data, re.IGNORECASE):
                    print("THIS IS INSPECTION DOCUMENT FOR QUANTITY")
                    document_type = "Quantity"
            except:
                if re.search('CERTIFICATE OF QUANTITY', data, re.IGNORECASE):
                    print("THIS IS INSPECTION DOCUMENT FOR QUANTITY")
                    document_type = "Quantity"
                    pass
        else:
            print("this doc is not belong to ")
            # document_type ="Not classified"
            # pass
    except Exception as e:
        traceback.print_exc()
        print("Error in classfication ", e)
        pass

    return document_type

def Camin_classifcation(text_data):
    data = text_data
    document_type=""
    a=1
    try: 
        if re.search('TRIP:', data, re.IGNORECASE):
            document_type="Nomination"
            #print("This a nomination document")

        elif re.search('Invoice N:°', data, re.IGNORECASE):
            document_type="Invoice"
            #print("THIS IS INVOICE DOCUMENT")

        elif re.search('QUANTITY CERTIFICATE', data, re.IGNORECASE):
            if re.search('CERTIFICATE OF ANALYSIS',data,re.IGNORECASE):
                document_type = "Quality and Quantity"   
                #print("THIS IS INSPECTION DOCUMENT FOR QUALITY AND QUANTITY BOTH")
            else:
                document_type = "Quantity"   
                #print("THIS IS INSPECTION DOCUMENT FOR QUANTITY ONLY")
            
        elif re.search('CERTIFICATE OF ANALYSIS',data,re.IGNORECASE):
            document_type="Quality"  
            #print("THIS IS INSPECTION DOCUMENT FOR QUALITY ONLY")

        else:
            #print("THIS DOCUMENT DOES NOT BELONG TO ANT CATEGORY ")
            document_type ="Not classified"
            pass
    except Exception as e:
        traceback.print_exc()
        print("Error in classfication ", e)
        pass

    return document_type


def Saybolt_classifcation(text_data):
    data = text_data
    line=data.split("\n")
    document_type=""
    a=1
    try: 
        if re.search('TRIP:', line[0], re.IGNORECASE):
            document_type="Nomination"
            #print("This a nomination document")

        elif re.search('Invoice Number', data, re.IGNORECASE):
            document_type="Invoice"
            #print("THIS IS INVOICE DOCUMENT")

        elif re.search(r'(Certificate of Quantity)', data, re.IGNORECASE) or re.search(r'(Summary Loading \(GSV\))', data, re.IGNORECASE) or re.search(r'(Loading Summary Report)', data, re.IGNORECASE) or re.search(r'(^\s+SUMMARY REPORT)',re.sub('\s+',' ',data) ,re.I) :
            document_type="Quantity"  
            #print("THIS IS INSPECTION DOCUMENT FOR QUALITY ONLY")
            
        elif re.search(r'(Certificate of Quality)',data,re.IGNORECASE) or re.search(r'(Analysis Report)',data,re.IGNORECASE) or re.search(r'(Certificate of Analysis)',data,re.IGNORECASE):
            document_type="Quality"  
            #print("THIS IS INSPECTION DOCUMENT FOR QUALITY ONLY")

        else:
            #print("THIS DOCUMENT DOES NOT BELONG TO ANT CATEGORY ")
            document_type ="Not classified"
            pass
    except Exception as e:
        traceback.print_exc()
        print("Error in classfication ", e)
        pass

    return document_type
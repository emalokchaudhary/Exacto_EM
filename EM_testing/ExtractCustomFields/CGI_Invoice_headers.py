# check if invoice document
# check for vendor
# extract  EMAffiliates, Vendor internal reference number

import re
import os
import numpy as np

def read_textfile(fileName):
    with open(fileName,encoding="utf-8") as f:
        text_data = f.read()
        #print(text_data)
    return text_data

def cgi_invoice_headers_extraction(text_data,uuid_doc):
    data_dict={}
    vendor_name=invoice_no=date_worked=po_number=file_no=discount=sub_total=invoice_total=currency=vessel_no=product_name=job_location=activity_type=ref_no=bill_to=''

    # if re.search('Inv No',text_data,re.IGNORECASE):
    #     print("THIS IS INVOICE DOCUMENT")
    #     if re.search('Coastal Gulf & International, Inc.',text_data):
    #         print("VENDOR MATCHED !!!!!!!!!")
    try:
        vendor_name=re.findall(r'Remit to:\n(.*)',text_data)[0].replace("  ","")
    except:
        pass
    try:
        po_number=re.findall(r'P.O. No. (.*)',text_data)[0].split()[0]
    except:
        pass
    try:
        invoice_no=re.findall(r'Inv No\n(.*)\n(.*)',text_data)[0][1].split()[-1]
    except:
        pass
    try:
        date_worked=re.findall(r'Date Worked(.*)\n(.*)\n(.*)',text_data)[0][-1].split()[-2]
    except:
        pass
    try:
        file_no=re.findall(r'File Number(.*)\n(.*)\n(.*)',text_data)[0][-1].split()[-1]
    except:
        pass
    try:
        ref_no=re.findall(r'Ref.#(.*)',text_data)[0]#.split()[0]
    except:
        pass
    try:
        invoice_total=re.findall(r'INVOICE TOTAL: (.*)',text_data)[0].split()[-1][1:]
    except:
        pass
    try:
        currency=re.findall(r'INVOICE TOTAL: (.*)',text_data)[0].split()[-1][0]
    except:
        pass
    try:
        sub_total=re.findall(r'Subtotal (.*)',text_data)[0].split()[-1]
    except:
        pass
    try:
        discount=re.findall(r'Navarik E-Enablement Discount (.*)',text_data)[0].split(')')[0].split('(')[-1]
    except:
        pass
    try:
        vessel_no=re.findall(r'JOB INFORMATION\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][1].split("  ")[-1]
    except:
        pass
    try:    
        product_name=re.findall(r'JOB INFORMATION\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][2].split("  ")[-1]
    except:
        pass
    try:        
        activity_type=re.findall(r'JOB INFORMATION\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][3].split("  ")[-1]
    except:
        pass
    try:    
        job_info4=re.findall(r'JOB INFORMATION\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][4].split("  ")[-1]
    except:
        pass
    try:
        job_info5=re.findall(r'JOB INFORMATION\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][5].split("  ")[-1]
    except:
        pass
    try:
        job_location=job_info4+"|"+job_info5
        job_location=job_location.split("|")
        job_location=" ".join(job_location).split('at')[1]
    except:
        pass
    try:
        address_line1=re.findall(r'JOB INFORMATION\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][1].split("  ")[0]
    except:
        pass
    try:
        address_line2=re.findall(r'JOB INFORMATION\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][2].split("  ")[0]
    except:
        pass
    try:
        address_line3=re.findall(r'JOB INFORMATION\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][3].split("  ")[0]
    except:
        pass
    try:
        address_line4=re.findall(r'JOB INFORMATION\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][4].split("  ")[0]
    except:
        pass
    try:
        address_line5=re.findall(r'JOB INFORMATION\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][5].split("  ")[0]
    except:
        pass
    try:
        # bill_to=job_info4+"|"+job_info5
        # bill_to=job_location.split("|")
        # bill_to=" ".join(job_location).split('at')[1]
        bill_to=address_line1+" "+address_line2+" "+address_line3+" "+address_line4+" "+address_line5
    except:
        pass
    
    if vendor_name:
        data_dict['VendorName']=vendor_name
    if po_number:
        data_dict['TripNumber']=po_number
    if invoice_no:
        data_dict['InvoiceNumber']=invoice_no
    if file_no:
        data_dict['VendorInternalReferencenumber']=file_no
    if date_worked:
        data_dict['JobDate']=date_worked
    if ref_no:
        data_dict['NominationKey']=ref_no
    if discount:
        data_dict['DiscountPercent']=discount
    if sub_total:
        data_dict['AmountBeforeTax']=sub_total
    if invoice_total:
        data_dict['TotalDueAmount']=invoice_total
    if currency:
        data_dict['Currency']=currency
    if vessel_no:
        data_dict['VesselName']=vessel_no
    if product_name:
        data_dict['ProductName']=product_name
    if activity_type:
        data_dict['ActivityType']=activity_type
    if job_location:
        data_dict['JobLocation']=job_location
    if bill_to:
        data_dict['EmAffiliates']=bill_to

    data_dict['doc_uuid'] = uuid_doc

    return data_dict


#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/Inv309560/Inv309560.text"  #Chem-US
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/300586/300586.text"        #US
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/Inv300686/Inv300686.text"   #2 pages
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/ExxonInv306271/ExxonInv306271.text"    # 20 pages
#print(cgi_invoice_headers_extraction(read_textfile(path)))




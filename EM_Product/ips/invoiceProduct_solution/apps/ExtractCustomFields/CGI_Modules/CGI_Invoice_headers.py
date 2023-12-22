import re
import os
import numpy as np
import datefinder
from ExtractCustomFields.EM_logging import logger

def date_formater(date):
    try:
        if(date!=""):
            temp=datefinder.find_dates(date)
            d=''
            for match in temp:
                d=match
            d=d.date().strftime('%Y-%m-%d')
            date=str(d)
    except:
        print('issue in date conversion')
        pass
    return date

def read_textfile(fileName):
    with open(fileName,encoding="utf-8") as f:
        text_data = f.read()
    return text_data

def cgi_invoice_headers_extraction(text_data,uuid_doc):
    data_dict={}
    vendor_name=invoice_no=date_worked=po_number=file_no=discount=sub_total=invoice_total=currency=vessel_no=product_name=job_location=activity_type=ref_no=bill_to=''

    try:
        vendor_name=re.findall(r'Remit to:\n(.*)',text_data)[0].replace("  ","")
        vendor_name=re.sub(r'^(\s+)',"",vendor_name)
        vendor_name=re.sub(r'\s+$',"",vendor_name)
    except:
        pass
    try:
        po_number=re.findall(r'P.O. No. (.*)',text_data)[0].split()[0]
        po_number=re.sub(r'^(\s+)',"",po_number)
        po_number=re.sub(r'\s+$',"",po_number)
    except:
        pass
    try:
        invoice_no=re.findall(r'Inv No\n(.*)\n(.*)',text_data)[0][1].split()[-1]
        
    except:
        pass
    try:
        date_worked=re.findall(r'Date Worked(.*)\n(.*)\n(.*)',text_data)[0][-1].split()[-2]
        date_worked=date_formater(date_worked)
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
        currency=re.findall(r'INVOICE TOTAL: (.*)',text_data)[0].split()[-1][0].replace("$","USD")
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
        job_location=" ".join(job_location).split('at ')[1]
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
    for i in data_dict:
        data_dict[i]=re.sub(r'^(\s+)',"",data_dict[i])
        data_dict[i]=re.sub(r'\s+$',"",data_dict[i])
    logger.info(f'Header data Invoice -{data_dict}')
    return data_dict


#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/CGI/US/302512/Inv_302512.text"  #Chem-US
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/300586/300586.text"        #US
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/Inv300686/Inv300686.text"   #2 pages
# path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/CGI/CHEM-US/300784/300784.text"    # 20 pages
# print(cgi_invoice_headers_extraction(read_textfile(path),'2323'))




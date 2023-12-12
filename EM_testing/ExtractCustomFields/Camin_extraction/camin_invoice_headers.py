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

def camin_invoice_headers_extraction(text_data,uuid_doc):
    data_dict={}
    vendor_name=invoice_no=date_worked=nomination=trip=file_no=discount=sub_total=invoice_total=currency=vessel_no=product_name=job_location=activity_type=ref_no=bill_to=''

    # if re.search('Inv No',text_data,re.IGNORECASE):
    #     print("THIS IS INVOICE DOCUMENT")
    #     if re.search('Coastal Gulf & International, Inc.',text_data):
    #         print("VENDOR MATCHED !!!!!!!!!")
    try:
        vendor_name=re.findall(r'INVOICE\n(.*)\n(.*)',text_data)[0][1].split("  ")[-1].replace("  ","")
    except:
        pass
    try:
        invoice_no=re.findall(r'Invoice N:° (.*)',text_data)[0].split('Date')[0].replace("  ","")
    except:
        pass
    try:
        date_worked=re.findall(r'Job Date: (.*)',text_data)[0].split('Ordered')[0].replace("  ","")
    except:
        pass
    try:
        file_no=re.findall(r'File N°: (.*)',text_data)[0].split('Customer')[0].replace("  ","")
    except:
        pass
    try:
        ref_no=re.findall(r'Job Ref. N°: (.*)',text_data)[0].replace("  ","")
        print(ref_no)
        if "/" in ref_no:
            nomination = ref_no.split("/")[0]
            trip = ref_no.split("/")[1]
        else:
            ref= re.sub(r'(\s+)',"",ref_no.replace("-",""))
            print(ref)
            print(ref_no)
            if ref.isdigit()==True:
                nomination=ref_no
                print("Nomina")
            else:
                trip=ref_no
                print("Trip")
            
        
    except:
        pass
    try:
        invoice_total=re.findall(r'Invoice Total\n(.*)\n(.*)',text_data)[0][1].split('$')[1].split('(')[0]
        #print(invoice_total)
    except:
        pass
    try:
        currency=re.findall(r'Invoice Total\n(.*)\n(.*)',text_data)[0][1].split('(')[1].split(')')[0]
    except:
        pass
    try:
        discount=re.findall(r'-Navarik(.*)',text_data)[0].split('Discount')[0].split('%')[0]
        #print(discount,"dddddddddddddddd")
        # discount=re.search(r'Navrik\s*[0-9]+.*[%]\s*Discount',text_data)
        # print(discount,"1111111111111111")
        # discount=re.sub(r'Navrik',"",discount)
        # print(discount,"222222222222222222")
        # discount=re.sub('[%]\s*Discount',"",discount) 
        # print(discount,"333333333333333")
    except:
        pass
    try:
        vessel_no=re.findall(r'Vessel/Tank: (.*)',text_data)[0].split("File")[0].replace("  ","")
    except:
        pass
    try:    
        product_name=re.findall(r'Product(.*)',text_data)[0].split(":")[1].split("Job")[0].replace("  ","")
        #print(product_name)
    except:
        pass
    try:        
        activity_type=re.findall(r'Movement: (.*)',text_data)[0].split("Job")[0].replace("  ","")
    except:
        pass
    try:    
        job_location=re.findall(r'Location: (.*)',text_data)[0].split("E-mail")[0].replace("  ","")
    except:
        pass
    try:
        address_line1=re.findall(r'(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][0].split("  ")[0]
    except:
        pass
    try:
        address_line2=re.findall(r'(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][1].split("  ")[0]
    except:
        pass
    try:
        address_line3=re.findall(r'(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][2].split("  ")[0]
    except:
        pass
    try:
        bill_to=address_line1+" "+address_line2+" "+address_line3
    except:
        pass
    
    if vendor_name:
        data_dict['VendorName']=vendor_name
    if trip:
        data_dict['TripNumber']=trip
    if invoice_no:
        data_dict['InvoiceNumber']=invoice_no
    if file_no:
        data_dict['VendorInternalReferencenumber']=file_no
    if date_worked:
        data_dict['JobDate']=date_worked
    if nomination:
        data_dict['NominationKey']=nomination
    if discount:
        data_dict['DiscountPercent']=discount
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
    return data_dict



# path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/1130611.text"    # 20 pages
# path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Camin/INT/1136684/1136684.text"
# print(camin_invoice_headers_extraction(read_textfile(path,),"3333"))



files=os.listdir(r"/datadrive/EM_testing/ExtractCustomFields/Camin_Invoice_documents/US")
path=r"/datadrive/EM_testing/ExtractCustomFields/Camin_Invoice_documents/US"
for file in files:
    path_full=os.path.join(path,file)
    #print(path_full)
    #print("*************************************")
    print("----------------------------------------",file,"-----------------------------------")
    text_data=read_textfile(path_full)
    extracted_data=camin_invoice_headers_extraction(text_data,"333333")
    print(extracted_data)
    print()
    print("*********************************************************************************************************")
    print()


'''
import os
filePath=r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_input/Camin/INT/1130611/1130611.pdf"
fileName=filePath.split("/")[-1]
Outpath=r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234"
def pdftotext(filePath, fileName, Outpath):
    # out_path= Outpath(outpath, folder_path)
    outFilePath = os.path.join(Outpath, fileName.replace(".pdf", ".text"))
    print(outFilePath)
    # outFilePath = os.path.join(folderPath, fileName + ".text")
    command = "pdftotext -layout '" + filePath + "' '" + outFilePath + "'"
    os.system(command)
    return outFilePath

pdftotext(filePath,fileName,Outpath)
'''

# check if invoice document
# check for vendor
# extract  EMAffiliates, Vendor internal reference number

import re
import os
import numpy as np

def read_textfile(fileName):
    with open(fileName,encoding="utf-8") as f:
        text_data = f.read()
        #lines = f.readlines()
        #print(text_data)
    return text_data


def saybolt_invoice_headers_extraction(text_data,uuid_doc):
    
    def saybolt_invoice_headers_extraction_1(text_data,uuid_doc):
        vendor_name=invoice_no=date_worked=nomination=trip=file_no=discount=sub_total=invoice_total=currency=vessel_no=product_name=job_location=activity_type=ref_no=bill_to=''
        data_dict={}
        
        try:
            vendor_name=re.findall(r'(.*)',text_data)[0].split(" ")[0].replace("  ","")
            #print(vendor_name)
        except:
            pass
        
        try:
            invoice_no=re.findall(r'Invoice Number(.*)',text_data,re.I)[0].split(':')[-1].replace("  ","")
            #print(invoice_no)
        except:
            pass
        
        try:
            date_worked=re.findall(r'Job Date (.*)',text_data)[0].split(':')[-1].replace("  ","")
            #print(date_worked)
        except:
            pass
        
        try:
            file_no=re.findall(r'Ref. number (.*)',text_data)[0].split(':')[-1].replace("  ","")
            #print(file_no)
        except:
            pass
            
        try:    
            product_name=re.findall(r'Products(.*)',text_data)[0].split(":")[-1].replace("  ","")
            #print(product_name)
        except:
            pass
        
        try:
            vessel_no=re.findall(r'Object(.*)',text_data)[0].split(":")[-1].replace("  ","")
            #print(vessel_no)
        except:
            pass
        
        try:    
            location_line1=re.findall(r'Installation(.*)',text_data)[0].split(":")[-1].replace("  ","")
            #print(location_line1)
        except:
            pass
        try:    
            location_line2=re.findall(r'Installation(.*)\n(.*)',text_data)[0][1]
            #print(location_line2)
            if "Products" in location_line2:
                location_line2=""
            else:
                location_line2=re.findall(r'Installation(.*)\n(.*)',text_data)[0][1].split("  ")[-1].replace("  ","")
        except:
            pass
        try:
            job_location = location_line1+location_line2
            #print(job_location)
        except:
            pass
        
        try:
            address_line1=re.findall(r'Billing Address (.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][1].split("  ")[0]
            # print()
            # print(address_line1)
        except:
            pass
        try:
            address_line2=re.findall(r'Billing Address (.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][2].split("  ")[0]
        except:
            pass
        try:
            address_line3=re.findall(r'Billing Address (.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][3].split("  ")[0]
        except:
            pass
        try:
            address_line4=re.findall(r'Billing Address (.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][4].split("  ")[0]
        except:
            pass
        try:
            address_line5=re.findall(r'Billing Address (.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][5].split("  ")[0]
        except:
            pass
        try:
            bill_to=address_line1+" "+address_line2+" "+address_line3+" "+address_line4+" "+address_line5
            #print(bill_to)
        except:
            pass
        
        try:
            lines=text_data.split('\n')
            for line in lines:
                if (re.search(r'Navarik(.*)discount',line,re.I))or(re.search(r'e[-]*discount',line,re.I))or(re.search(r'Discount Navarik',line,re.I)):
                    #discount=re.search('([0-9])+[%]',line)[0]
                    discount=re.search('([0-9])+\s*([%]|\spct\s)',line)[0]
                    discount=re.sub("pct","",discount)
                    break
            #print("#############",discount)
        except:
            pass
        
        try:
            lines = text_data.split("\n")
            temp_ref=''
            for i in range(len(lines)):
                if(re.search(r'Your ref\..*',lines[i],re.I)):
                    tt=lines[i].find('Your ref')
                    temp_ref+=lines[i][tt:]+" "
                    if(not re.search(r'Our ref\.',lines[i+1],re.I)):
                        temp_ref+=lines[i+1][tt:]
                    break
            # print(temp_ref)
            tt=(re.sub("\s+"," ",(re.sub(r'Your ref\s*\.\s+([\.:])*',"",temp_ref)))).split('/')
            trip=''
            nomination=''
            for j in tt:
                if(re.search(r'[a-z]',j,re.I)):
                    # print(j)
                    trip=re.sub("\s+","",(re.sub(r'\s*((TRIP)|(Trip))\s*[#:]*',"",j,re.I)))
                else:
                    nomination=re.sub("\s+","",j)
            # print(trip,"##",nom)
            # ref_no=re.findall(r'Your ref\. (.*)',text_data)[0].split(":")[-1].replace("  ","")
            # print(ref_no)
            # if "Trip" in ref_no:
            #     nomination = ref_no.split("/")[0]
            #     trip = re.findall(r'Your ref\. (.*)\n(.*)',text_data)[0][1].split(":")[-1].replace("  ","")
            #     print("TTTTT","  ",trip)
            #     print("NNNNN","  ",nomination)
            # elif "/" in ref_no:
            #     nomination = ref_no.split("/")[0]
            #     trip = ref_no.split("/")[1]
            # else:
            #     ref= re.sub(r'(\s+)',"",ref_no.replace("-",""))
            #     # print(ref)
            #     # print(ref_no)
            #     if ref.isdigit()==True:
            #         nomination=ref_no
            #         #print("Nomina")
            #     else:
            #         trip=ref_no
            #         #print("Trip")
        
        except:
            pass
        try:
            # taxpercent=re.findall(r'Tax%(.*)\n(.*)',text_data)[0][1]#.split(' ')[-3]#.replace(" ","")
            # print(taxpercent)
            # print(taxpercent.find('Tax%'))
            lines = text_data.split("\n")
            taxpercent=''
            for i in range(len(lines)):
                if(re.search(r'Tax%',re.sub("\s+"," ",lines[i]),re.I)):

                    tt=lines[i].find('Tax%')

                    if(re.search(r'[0-9]',lines[i+1],re.I)):
                        taxpercent=re.search(r'[0-9]+\.[0-9]*',lines[i+1][tt-3:tt+8])[0]
                        break

            print(taxpercent)
        except:
            pass
        
        try:
            invoice_total=re.findall(r'Total to Pay (.*)',text_data)[0].split(' ')[-1].replace(" ","")
            print(invoice_total)
        except:
            pass
        try:
            currency=re.findall(r'Total to Pay (.*)',text_data)[0].split(invoice_total)[0].replace(" ","").replace('$',"").replace('€',"EUR")
            print(currency)
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
        if taxpercent:
            data_dict['Tax_percent']=taxpercent

        data_dict['doc_uuid'] = uuid_doc
        for i in data_dict:
            data_dict[i]=re.sub(r'^(\s+)',"",data_dict[i])
            data_dict[i]=re.sub(r'\s+$',"",data_dict[i])
        
        return data_dict
        
        
        
        
        
    
    def saybolt_invoice_headers_extraction_2(text_data,uuid_doc):
        vendor_name=invoice_no=date_worked=nomination=trip=file_no=discount=sub_total=invoice_total=currency=vessel_no=product_name=job_location=activity_type=ref_no=bill_to=''
        data_dict={}   
        
        try:
            vendor_name=re.findall(r'(.*)',text_data)[0].split(" ")[0].replace("  ","")
            #print(vendor_name)
        except:
            pass
        
        try:
            invoice_no=re.findall(r'Invoice Number(.*)',text_data,re.I)[0].split(':')[-1].replace("  ","")
            #print(invoice_no)
        except:
            pass
        
        try:
            date_worked=re.findall(r'Job Date (.*)',text_data)[0].split(':')[-1].replace("  ","")
            #print(date_worked)
        except:
            pass
        
        try:
            file_no=re.findall(r'Report Nr(.*)',text_data)[0].split(':')[-1].replace("  ","")
            #print(file_no)
        except:
            pass
            
        try:    
            product_name=re.findall(r'Products(.*)',text_data)[0].split(":")[-1].replace("  ","")
            #print(product_name)
        except:
            pass
        
        try:
            vessel_no=re.findall(r'Object(.*)',text_data)[0].split(":")[-1].replace("  ","")
            #print(vessel_no)
        except:
            pass
        
        try:    
            location_line1=re.findall(r'Installation(.*)',text_data)[0].split(":")[-1].replace("  ","")
            #print(location_line1)
        except:
            pass
        try:    
            location_line2=re.findall(r'Installation(.*)\n(.*)',text_data)[0][1]
            #print(location_line2)
            if "Products" in location_line2:
                location_line2=""
            else:
                location_line2=re.findall(r'Installation(.*)\n(.*)',text_data)[0][1].split("  ")[-1].replace("  ","")
        except:
            pass
        try:
            job_location = location_line1+location_line2
            #print(job_location)
        except:
            pass
        try:
            #address_line1=re.findall(r'LOCATION CODE & NAME: (.*)\n(.*)\n(.*)\n(.*)',text_data)[0][3].split("  ")[0]
            address_line1=re.findall(r'BILLING ADDRESS: (.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][3].split("  ")[0]
            # print()
            # print(address_line1)        
        except:
            pass
        try:
            address_line2=re.findall(r'BILLING ADDRESS: (.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][4].split("  ")[0]
        except:
            pass
        try:
            address_line3=re.findall(r'BILLING ADDRESS: (.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)',text_data)[0][5].split("  ")[0]
        except:
            pass
        
        try:
            bill_to=address_line1+" "+address_line2+" "+address_line3
            #print(bill_to)
        except:
            pass
        
        try:
            lines=text_data.split('\n')
            for line in lines:
                if (re.search(r'Navarik(.*)discount',line,re.I))or(re.search(r'e[-]*discount',line,re.I))or(re.search(r'Discount Navarik',line,re.I)):
                    #discount=re.search('([0-9])+[%]',line)[0]
                    discount=re.search('([0-9])+\s*([%]|\spct\s)',line)[0]
                    break
            #print("#############",discount)
        except:
            pass
        
        try:
            invoice_total=re.findall(r'TOTAL TO YOUR ACCOUNT BY NOMINATION(.*)',text_data)[0].split(' ')[-1].replace(" ","")
            print(invoice_total)
        except:
            pass
        try:
            currency=re.findall(r'TOTAL TO YOUR ACCOUNT BY NOMINATION(.*)',text_data)[0].split('$')[0].replace("…","").replace(".","")
            print(currency)
        except:
            pass
        
        try:
            trip=re.findall(r'TRIP: (.*)',text_data)[0].split('$')[0]
            print(trip)
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

    
        
         
    
    def classification_inv(li):
        cl='p2'
        for i in range(len(li)):
            if(re.search('quantity', li[i],re.I) and re.search('description', li[i],re.I) and re.search(r'share', li[i],re.I) and re.search('unit(\s){,3}price', li[i],re.I) and re.search('tax', li[i],re.I) and re.search('amount', li[i],re.I)):
                cl='p1'
                break
        return cl
    
    
    lines = text_data.split('\n')
    cl_res=classification_inv(lines)
    #print(cl_res)
    if(cl_res=='p1'):
        final_dict = saybolt_invoice_headers_extraction_1(text_data,uuid_doc)
        
    elif(cl_res=='p2'):
        final_dict = saybolt_invoice_headers_extraction_2(text_data,uuid_doc)

    return final_dict
















    
   
    
   
    
    
    
    

# path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/INT/88806130221/Invoice.text"
path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/INT/16000660000910/Invoice_160-0066-0000910_EXXONMOBILSALES&SUPPLYLLC-MTAEGEANVISION.text"
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/INT/16002600024221/Invoice160-0260-0024221.text"
# path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/CHEM-US/1300395101/1300395101.text"
#path = r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/CHEM-US/1300405578/Invoice_1300405578_EXXONMOBILCHEMICALCO.text"    # 20 pages
#path=r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/CHEM-US/1300396439/1300396439.text'
print(saybolt_invoice_headers_extraction(read_textfile(path,),"3333"))


'''
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

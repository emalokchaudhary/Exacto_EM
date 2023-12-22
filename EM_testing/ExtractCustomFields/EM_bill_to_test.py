import re


# def bill_invoice_to(data):
#     # data=data.split("\n")
#     l=[]
#     res=""
#     count=0
#     break_point=0
#     # k=0
    
#     for z in range(len(data)):
#         # break_point=0
#         res=""
#         if (re.search(r'(Bill Invoice To)',data[z],re.I) and re.search(r'(Item to Bill)',data[z],re.I) and re.search(r'(Split)',data[z],re.I)):
#     # while(k<len(data)):
#     #     break_point=0
#     #     
#     #     if (re.search(r'(Bill Invoice To)',data[k],re.I) and re.search(r'(Item to Bill)',data[k],re.I) and re.search(r'(Split)',data[k],re.I)):
            
#             # for i in range(k,len(data)):
#             #     # if (re.search(r'(Bill Invoice To)',data[i],re.I) and re.search(r'(Item to Bill)',data[i],re.I) and re.search(r'(Split)',data[i],re.I)):
#                     # k+=1
#             ed=(data[z].lower()).find('Item to Bill'.lower())
#             # print(ed)
#             for j in range(z+1,len(data)):
#                 # k+=1
#                 if ("quantity" in data[j][ed-3:].lower()or "quality" in data[j][ed-3:].lower()):
#                     # print(data[j])
#                     count+=1
#                     if count>1 :
#                         res= re.sub("\s+"," ",res)
#                         l.append(res)
#                         # print("if inside the ", l)
#                         res= re.sub("\s+"," ",data[j][:ed-3])
#                         # print("if inside the ", res)
#                     else:
#                         res= re.sub("\s+"," ",data[j][:ed-3])
#                         # print("if inside the else part asre", res)
#                     # print("if condition satisfied", l)
#                 elif (" "==re.sub("\s+"," ",data[j])):
#                     l.append(re.sub(r"\s+"," ",res))
#                     # print("elif ke inside ", l)
#                     break_point=1
#                     break
#                 else:
#                     res+=re.sub("\s+"," ",data[j][:ed-3])
#                     # print("else ke part", res)

#         if break_point==1:
#                 break
#         # k+=1  
#     l=[i for i in l if i]
#     bill_invoice=[]          
#     for k in l:
#         if  "ExxonMobil"  in k :
#             # k=re.sub(r"(Recipient List.*)| (NOMINATION COMMENTS.*)" ,"",k)
#             bill_invoice.append(k.strip())

#     # print(bill_invoice)
#     return bill_invoice
                            
# f=open(r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/CGI/US/302941/20E545314v.3.text','r')
# import re

# lines=f.readlines()

def find_bill_invoice_to(lines):
    l=[]
    res=""
    count=0
    breakp=0
    for i in range(len(lines)):
        res=""
        if(re.search(r"Bill\s*Invoice\s*To",lines[i],re.I) and re.search(r"Item to Bill",lines[i],re.I) and re.search(r"Split",lines[i],re.I)):
            ed=(lines[i].lower()).find('Item to Bill'.lower())
            for j in range(i+1,len(lines)):
                if("quantity" in lines[j][ed-3:].lower() or "quality" in lines[j][ed-3:].lower()):
                    count+=1
                    if(count>1):
                        res=re.sub('\s+'," ",res)
                        l.append(res)
                        res=re.sub("\s+"," ",lines[j][:ed-3])
                    else:
                        res+=re.sub("\s+"," ",lines[j][:ed-3])
                elif(""==re.sub("\s+","",lines[j]) ):
                    l.append(re.sub(r'\s+'," ",res))
                    breakp=1
                    break
                else:
                    res+=re.sub("\s+"," ",lines[j][:ed-3])
            if breakp==1:
                break            
            
    return l

 

 
def read_file(filepath):
    with open(filepath, 'r', encoding="utf-8") as f:
        text_data = f.read()
        # lines = f.readlines()
        lines=text_data.split("\n")
        print(lines)
    return lines



path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/CGI/US/302941/20E545314v.3.text"
# path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/CGI/US/303610/20E552661v.1.text"
# print(bill_invoice_to(read_file(path)))
print(find_bill_invoice_to(read_file(path)) )

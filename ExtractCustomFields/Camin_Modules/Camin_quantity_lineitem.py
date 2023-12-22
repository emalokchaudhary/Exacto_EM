import re
import os
import numpy as np

def read_textfile(fileName):
    with open(fileName,encoding="utf-8") as f:
        text_data = f.read()

    return text_data



def Camin_quantity_Nominated(data,uuid_doc):
    data_dict={}
    # data_dict['doc_uuid']=uuid_doc
    i=0
    while(i<len(data)):
        breakpoint=0
        startflag=0
       
    # for k,line in enumerate(data):
        match=re.search(r'(quantity certificate)',data[i],re.IGNORECASE)
        if match: 
            k=i 
            # print(match)           
            span=match.span() 
            for j in range(k+1,len(data)):
                # if ((re.search(r'All gauges, temperatures and volumes were obtained in accordance to the latest API and ASTM procedures',data[j]))or (re.search(r' ',re.sub("\s+"," ",data[j])) and (re.search(r' ',re.sub("\s+"," ",data[j+1])) and (re.search(r' ',re.sub("\s+"," ",data[j+2]))) ))):
                #     break
                if(breakpoint==1):
                    break
                if ((re.search(r'(total quantities)|(vessel quantities)',data[j],re.IGNORECASE))and (re.search(r'(delivered)|(received)',data[j],re.IGNORECASE)) and (re.search(r'(TCV, Barrels)',data[j+1],re.IGNORECASE) or re.search(r'(TCV, Barrels)',data[j+2],re.IGNORECASE)) ):
                    # print(data[j])
                    
                    for z in range(i+1,len(data)):
                        if ((re.search(r'All gauges, temperatures and volumes were obtained in accordance to the latest API and ASTM procedures', data[z],re.I)) or ((' ' == re.sub("\s+", " ", data[z])) and (' ' == re.sub("\s+", " ", data[z+1]) and (' ' == re.sub("\s+", " ", data[z+2]))))):
                            breakpoint=1
                            break
                        elif (re.search(r'(TCV, Barrels)',data[z],re.I)):
                            temp_li=re.sub("(\s+){2,}","  ",data[z]).split("  ")
                            data_dict['Barrels']=temp_li[1]
                        elif(re.search(r'(\s+gs[vw]\s+)|(\s+ns[vw]\s+)',data[z],re.I)):
                            startflag=1
                        elif(startflag==1):
                            if(''!=re.sub('\s+',"",data[z])):
                                temp=re.sub(r'(\s+){2,}',"  ",data[z]).split("  ")
                                for m in range(len(temp)):
                                    if(re.search('barrels',temp[m],re.I)):
                                        try:
                                            tt=data_dict['Barrels']
                                            tt=float(re.search(r'[0-9]+(\.)*[0-9]*',tt)[0])
                                            ttt = float(re.search(r'[0-9]+(\.)*[0-9]*',temp[m+1])[0])
                                            if(ttt>tt):
                                                data_dict['Barrels']=str(ttt)
                                        except:
                                            print('error in Barrels')

                                    elif(re.search(r'[a-z]+',temp[m])):
                                        hd=re.sub(r'@.*',"",temp[m])
                                        hd=hd.strip()
                                        data_dict[hd]=temp[m+1]


                        
                    break
                i +=1
        i +=1
    
    return data_dict
                    
                    
                            
def Camin_inspection_lineitem_main(text_data,uuid_doc):
    
    line_data=text_data.split("\n")
    
    res=Camin_quantity_Nominated(line_data,uuid_doc)
    
    return res
    
 
# path=r"/datadrive/EM_testing/ExtractCustomFields/Camin_Quantity_document/CHEM-US/565635EXXO06-02cogksp831121-58-12-0458.text"           
# path=r"/datadrive/EM_testing/ExtractCustomFields/Camin_Quantity_document/CHEM-US/543767EXXO06-04tmx5ma318120-54-22-0454.text"
# print(Camin_inspection_lineitem_main(read_textfile(path)))

# files = os.listdir(
#     r"/datadrive/EM_testing/ExtractCustomFields/Camin_Quantity_document/US")
# path = r"/datadrive/EM_testing/ExtractCustomFields/Camin_Quantity_document/US"
# c=1
# for file in files:
#     c+=1
#     print(c)
#     path_full = os.path.join(path, file)
#     # print(path_full)
#     print(file)
#     res=Camin_inspection_lineitem_main(read_textfile(path_full))
#     print(res,"\n","*"*90,"\n")


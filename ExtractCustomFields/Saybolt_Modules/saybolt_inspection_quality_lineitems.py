import re

def find_header_item(lines):
    st=-1
    l=['name','method','unit','result']
    st_header=[]
    for i in range(len(lines)):
        if(re.search('method',lines[i],re.IGNORECASE) and re.search('name',lines[i],re.IGNORECASE) and re.search('result',lines[i],re.IGNORECASE) and re.search('unit',lines[i],re.IGNORECASE)):
            st=i
            for j in l:
                st_header.append((lines[i].lower()).find(j))
            break

    return st,st_header


def saybolt_qlty_lineitem_extraction(lines):
    res=[]
    kk=0
    breakpoint=0
    itemno=1
    prev_st_header=[]
    tempmethod=''
    while(kk<len(lines)):
        line=lines[kk:]
        st,st_header=find_header_item(line)
        # print(st,st_header)
        dict_row_data={}
        method=''
        component=''


        if(st!=-1):
            prev_st_header=st_header
            kk+=st
            for i in range(st+1,len(line)):
                kk+=1
                if(re.search(r'all results in this report refer',line[i].lower(),re.I) or 
                   re.search(r'^\s*remarks',line[i].lower())
                   or re.search(r'^\s*test comments',line[i].lower())
                   or re.search(r'^\s*[~]\s*Due to restrictions enforced by terminal',line[i].lower(),re.I)):
                    dict_row_data={}
                    method=re.sub(r"(\s*\|\s*)*$","",method)
                    dict_row_data['method']=method
                    component=re.sub(r'\s+'," ",component)
                    dict_row_data['component']=component
                    res.append(dict_row_data)
                    break
                elif(re.search(r'[a-z0-9]',line[i][st_header[0]:st_header[0]+10],re.I) and 
                     ((re.search('[a-z0-9]',line[i][st_header[0]:st_header[0]+10],re.I).span()[0])-st_header[0])<2
                     ):
                    dict_row_data={}
                    if(method!='' and component!=''):
                        method=re.sub(r"(\s*\|\s*)*$","",method)
                        dict_row_data['method']=method
                        component=re.sub(r'\s+'," ",component)
                        dict_row_data['component']=component
                        res.append(dict_row_data)
                        method=''
                        component=''
                        tempmethod=''
                    method=re.sub("\s+"," ",line[i][st_header[1]-5:st_header[2]-10])
                    tempmethod=method
                    component=re.sub('\s+'," ",line[i][:st_header[1]-5])
                elif(re.search(r'[a-z0-9]',line[i][st_header[0]:st_header[0]+10],re.I) and 
                     3<((re.search('[a-z0-9]',line[i][st_header[0]:st_header[0]+10],re.I).span()[0])-st_header[0])<10
                     ):
                    dict_row_data={}
                    if(method!='' and component!=''):
                        method=re.sub(r"(\s*\|\s*)*$","",method)
                        dict_row_data['method']=method
                        component=re.sub(r'\s+'," ",component)
                        dict_row_data['component']=component
                        res.append(dict_row_data)
                        method=''
                        component=''
                    method=tempmethod
                    component=re.sub('\s+'," ",line[i][:st_header[1]-5])
                
                else:
                    component+=re.sub('\s+'," ",line[i][:st_header[1]-5])

        kk+=1
        if(breakpoint==1):
            break
    final_res=[]
    if(res!=[]):
        for i in res:
            if(i['method']=='' and i['component']==''):
                pass
            else:
                final_res.append(i)

    return final_res

  
def saybolt_qlty_lineitem_main(inp_path):
    f=open(inp_path,'r')
    lines=f.readlines()
    final_dict={}
    status=0
    # try:

    final_dict=saybolt_qlty_lineitem_extraction(lines)
    # except:
    #     pass

    return final_dict



################################### UNCOMMENT BELOW FOR TEST  ##########################

# inp_path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/100150-264_WEB264_VGO_B20201223001_XOM_FINALupdated/100150-264_WEB264_VGO_B20201223001_XOM_FINALupdated.text"   #provide the path of the text file
# inp_path=r'/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/98697-215_ST215_CSO-MCB_083020-003_XOM_Final_Updated/98697-215_ST215_CSO-MCB_083020-003_XOM_Final_Updated.text'
# inp_path=r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/US/1300398489/COA_CBC_317_Trip__2020-BT-VP-EHC120-11_13074_00001689_20201214081153_Kyle_C_Mcilroy.text'
# p=(saybolt_qlty_lineitem_main(inp_path))
# for i in p:
#     print(i,"\n")

            

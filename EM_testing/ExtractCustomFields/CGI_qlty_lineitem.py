import re
def find_header_item(lines):
    st=-1
    l=['method','component','result','units']
    st_header=[]
    for i in range(len(lines)):
        if(re.search('method',lines[i],re.IGNORECASE) and re.search('component',lines[i],re.IGNORECASE) and re.search('result',lines[i],re.IGNORECASE) and re.search('units',lines[i],re.IGNORECASE)):
            st=i
            for j in l:
                st_header.append((lines[i].lower()).find(j))
            break
    if(st==-1):
        for i in range(len(lines)):
            if(re.search(r'\s*subject\s*',lines[i].lower()) and re.search(r'\s*terminal\s*',lines[i-1].lower())):
                if((re.search(r'sample\s*number',lines[i+1].lower()) and re.search(r'sample\s*type',lines[i+2].lower())) or (re.search(r'sample\s*number',lines[i+2].lower()) and re.search(r'sample\s*type',lines[i+3].lower()))):
                    break
                else:
                    st=i
                    break



    return st,st_header
def split_line(line):
    l=[]
    line=re.sub(r'^\s+',"",line)
    line=re.sub(r'\s*$',"",line)
    line=re.sub(r'(\s){3,}',"  ",line)
    l=line.split("  ")
    return l

def cgi_qlty_lineitem_extraction(lines):
    res=[]
    kk=0
    breakpoint=0
    itemno=1
    prev_st_header=[]
    while(kk<len(lines)):
        line=lines[kk:]
        st,st_header=find_header_item(line)
        dict_row_data={}
        method=''
        component=''
        if(st!=-1 and st_header==[]):
            st_header=prev_st_header

        if(st!=-1):
            prev_st_header=st_header
            kk+=st
            for i in range(st+1,len(line)):
                kk+=1
                if(re.search(r'signed\s*[:]',line[i].lower(),re.I) or re.search(r'signed.*reviewed',line[i+1].lower())):
                    dict_row_data={}
                    method=re.sub(r"(\s*\|\s*)*$","",method)
                    dict_row_data['method']=method
                    component=re.sub(r'\s+'," ",component)
                    dict_row_data['component']=component
                    res.append(dict_row_data)
                    breakpoint=1
                    break
                elif(re.search(r'sample\s*number',line[i].lower()) or re.search(r'sample\s*type.*sample\s*location',line[i].lower()) or (re.sub(r'\s+',"",line[i][st_header[0]:st_header[1]+5])=="")):
                    dict_row_data={}
                    method=re.sub(r"(\s*\|\s*)*$","",method)
                    dict_row_data['method']=method
                    component=re.sub(r'\s+'," ",component)
                    dict_row_data['component']=component
                    res.append(dict_row_data)
                    itemno+=1
                    break
                elif(re.search(r'[0-9a-z]',line[i][st_header[0]:st_header[0]+10])):
                    dict_row_data={}
                    method=re.sub(r"(\s*\|\s*)*$","",method)
                    dict_row_data['method']=method
                    component=re.sub(r'\s+'," ",component)
                    dict_row_data['component']=component
                    res.append(dict_row_data)
                    
                    itemno+=1
                    temp= split_line(line[i][st_header[0]:st_header[2]-5])
                    if(len(temp)<=1):
                        method=re.sub(r"\s+"," ",line[i][:st_header[0]+10])
                        component=re.sub(r'\s+'," ",line[i][st_header[0]+11:st_header[2]-7])
                    else:
                        method=re.sub(r"\s+"," ",temp[0])
                        component=re.sub(r'\s+'," ",temp[1])

                else:
                    component+=re.sub(r"\s+"," ",line[i][st_header[0]+11:st_header[2]-7])+" " 
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

def classification_for_qlty_lineitem(lines):

    res_cgi="NA"
    lp=[0,0,0,0,0]
    for  i in range(len(lines)):
        l=re.sub(r'\s+'," ",lines[i]).lower()
        if(re.search(r'((coastal\s*gulf)|(\s*cgi\s*))',l,re.I)):
            lp[0]=1
        elif(re.search(r'((shore\s*tank)|(lab\s*num.*))',l,re.I)):
            lp[1]=1
        elif(re.search('method',l) and re.search('component',l) and re.search('result',l) and re.search('units',l)):
            lp[2]=1
        elif(re.search(r'\s*sample\s*type.*sample\s*location',l,re.I)):
            lp[3]=1
        elif(re.search(r'certificate\s*of\s*analysis',l,re.I)):
            lp[4]=1
    if(sum(lp)==5):
        res_cgi='qlty'
    return res_cgi
    
def cgi_qlty_lineitem_main(inp_path):
    f=open(inp_path,'r')
    lines=f.readlines()
    final_dict={}
    status=0
    try:
        if(classification_for_qlty_lineitem(lines)=='qlty'):
            final_dict=cgi_qlty_lineitem_extraction(lines)
    except:
        pass
    return final_dict



################################### UNCOMMENT BELOW FOR TEST  ##########################

# inp_path=r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/100150-264_WEB264_VGO_B20201223001_XOM_FINALupdated/100150-264_WEB264_VGO_B20201223001_XOM_FINALupdated.text"   #provide the path of the text file
# inp_path=r'/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/98697-215_ST215_CSO-MCB_083020-003_XOM_Final_Updated/98697-215_ST215_CSO-MCB_083020-003_XOM_Final_Updated.text'
# print(cgi_qlty_lineitem_main(inp_path))
            

            

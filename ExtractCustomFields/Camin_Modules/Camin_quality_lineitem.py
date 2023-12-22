import re
def quality_lineitem(lines):
    res=[]
    i=0

    temp_name=''

    while(i<len(lines)):
        test_method=''
        test_name=''

        if(re.search(r'CERTIFICATE OF ANALYSIS',lines[i])):
            flag1=0
            checkpoint=0  
            for j in range(i+1,len(lines)):
                d={}
                i+=1
                # print(lines[j])
                if(re.search(r'sample\s*n', lines[j], re.I) and (re.search(r'sampled', lines[j], re.I) or re.search(r'sampled', lines[j+1], re.I))):
                    if(test_method!='' and test_name!=''):
                        d['TestMethod'] =test_method
                        d['TestName']=test_name
                        res.append(d)
                        test_method=''
                        test_name=''
                    flag1=1
                    pass
                elif(re.search(r'The results apply to the samples as received and specifically to the items listed on this certificate', lines[j], re.I)):
                    if(test_method != '' and test_name != ''):
                        d['TestMethod'] =test_method
                        d['TestName']=test_name
                        res.append(d)
                        test_method=''
                        test_name=''
                    break
                elif(re.search(r'^\s*description\s*[:]',lines[j],re.I)):
                    pass
                elif(re.search(r'[a-z]+\s*[0-9]+',lines[j][:20],re.I) and flag1==1):
                    # print(lines[j])
                    if(temp_name!="" and res!=[]):
                        res[len(res)-1]['TestName']+=temp_name
                        temp_name=""
                        
                    elif(test_method != '' and test_name != ''):
                        d['TestMethod'] =test_method
                        d['TestName']=test_name
                        res.append(d)
                        test_method=''
                        test_name=''
                    
                    temp = re.sub('\s+', " ", lines[j][:15])+lines[j][15:]
                    temp = re.sub('\n$', "",temp)
                    temp=re.sub('(\s+){2,}',"  ",temp).split("  ")
                    try:
                        test_method=temp[0]
                        test_name=temp[1]
                        checkpoint=lines[j].find(test_name)
                    except:
                        pass
                elif("" != re.sub(r'\s+', "", lines[j]) and len(re.sub(r'\s+', "", lines[j]))>1 and not (re.search(r'[a-z]',lines[j][:3],re.I)) and flag1==1):
                    temp=(re.sub("(\s+){2,}","  ",re.sub('^\s+',"",lines[j]))).split("  ")
                    vall=temp[0]
                    if(lines[j].find(vall)==checkpoint):
                        vall=re.sub("\n$","",vall)
                        test_name+=" "+vall
                    elif(('Office Phone' in lines[j+2] and 'Email' in lines[j+3]) or ('Office Phone' in lines[j+3] and 'Email' in lines[j+4])):
                        d['TestMethod']=test_method
                        d['TestName']=test_name
                        res.append(d)
                        break
                    elif("" == re.sub("\s+", "", lines[j][:20]) and test_method == ""):
                        if(len(lines[j])<100):
                            t=re.sub('(\s+){2,}',"  ",re.sub(r'^\s+',"",lines[j]))
                            if(1<len(t.split("  "))<4):
                                temp_name+=" | "+t.split("  ")[0]
                    else:
                        # print(test_name)
                        test_name+=" | "+vall



        else:
            i+=1

    ############################   BELOW CODE FOR EDIT RESULT ##############
    # print(res)
    final_res=[]
    if(res!=[]):
        for i in res:
            d={}
            if(" | " in i['TestName']):
                temp_li=i['TestName'].split(' | ')
                if(temp_li!=[]):
                    for j in temp_li:
                        d={}
                        d['TestMethod']=i['TestMethod']
                        d['TestName']=re.sub("^\s+","",j)
                        final_res.append(d)
            else:
                d['TestMethod']=i['TestMethod']
                d['TestName']=i['TestName']
                final_res.append(d)


    return final_res
def Camin_Ins_quality_li_main(inp_path):
    f=open(inp_path,'r')
    lines=f.readlines()
    res=quality_lineitem(lines)
    return res
    ################# FRO TESTING ################
    # for k in res:
    #     print(k,"\n")
    
    
############################ RUN MAIN ################
# inp_path = r'/datadrive/EM_testing/ExtractCustomFields/Camin_Quantity_document/US/563733EXXM17-03q2w13m409121-41-02-1241.text'
# inp_path = r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Camin/US/1131470/539313EXXM01-143mc1bs742120-28-15-0228.text'
# inp_path = r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Camin/US/1145425/551113EXXM00-31m3kkq1167120-28-02-0828(1).text'
# quality_main(inp_path)


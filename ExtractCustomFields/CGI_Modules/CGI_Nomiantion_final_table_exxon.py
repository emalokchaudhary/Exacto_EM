import re
# import pyodbc
# file=open(r"/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/560/20E552683v.1/20E552683v.1.text",'r',encoding='windows-1258')
# read=file.read()

# match = re.search('\s*(Documentary Instructions:).*',read)

'''For editing the output uncomment line 337 and comment 336'''


# lines=read.split('\n')
# lines = file.readlines()
# if match:
    # print('YesSSSSSSSSSSSSSSSSSSSSS')
def nomination_key(lines):
    for i in lines:
        try:
            # print(i)
            if(re.search('\s*(Voyage Parcel External Reference Number:)+.*',i)):

                if(re.search('\s*\d+-\d+',i)):

                    d=re.search('\s*(\d+\s*(-)*\s*\d+)+',i)

                    return(d.group().strip())
        except:
            pass

# def vessel_name(lines):
#     vessel_key=[]

#     for i in lines:
#         try:
#             # print(i)
#             if(re.search('\s*(LOAD)+:|\s*(DISCHARGE)+:.*',i)):
#                 patt = '([LOAD|DISCHARGE]+:)'
#                 line_val = re.sub(patt,'',i)
#                 print(line_val)
#                 vessel_lst = line_val.split(' - ')
#                 vessel_key.append([[vessel_lst[0].strip()]])

            
#         except:
#             pass
    
#     return vessel_key



def set_func(lines):
    list_start_index_set=[]
    list_end_index_set=[]
    load_discharge = []
    for i in range(0,len(lines)):

        if(re.search('\s*(SET)+\s*(:|-)*\d+\s*',lines[i])):
            start_set=i
            list_start_index_set.append(start_set)
        if(re.search('\s*((Description)|(DESCRIPTION)|(description))+\s*(:|-)*.*',lines[i])):
            end_set=i
        if(re.search('\s*((Sample)|(SAMPLE))+\s*((Location)|(LOCATION))+\s*(:|-)*.*',lines[i])):
            start_sample=i
        if(re.search('((\s*((Quality)|(QUALITY))+\s*((TEST)|(Test))+\s*((Comments)|(COMMENTS))+\s*(:|-)*\s*.*)|((Test|TEST|test)+\s*(Methods|METHODS|methods)+\s*(MIN|min|Min)+\s*(Max|max|MAX)+\s*(UOM|uom|Uom)+\s*(Typical|TYPICAL|typical)+\s*(R.o.|r.o.|R.O.)+\s*(Req.|req.|REQ.)+\s*(Comment|comment|COMMENT)+))',lines[i])):
            end_sample=i
            list_end_index_set.append(end_sample)
        if(re.search('\s*(LOAD)+.*',lines[i])):

            if(re.search('\s*(Inspector)+.*(Inspection Status)+.*',lines[i+1])):

                load_discharge.append(int(i))

        if(re.search('\s*(DISCHARGE)+.*',lines[i])):

            if(re.search('\s*(Inspector)+.*(Inspection Status)+.*',lines[i+1])):

                load_discharge.append(int(i))
        
        
    all_set_content=[]
    fields=['SET','set','SET:','Location:','Description:','Sample Location:','SAMPLE','Sample','Location','LOCATION','Description','DESCRIPTION',':']
    
    # print(list_start_index_set)
    # print('&************************************88')
    # print(list_end_index_set)
    # print(load_discharge)
    # lines[list_start_index_set[1]:list_end_index_set[1]]
    for start in range(0,len(list_start_index_set)):
        for end in range(start+0,len(list_end_index_set)):
            # print(list_end_index_set[end])
            if(list_start_index_set[start]>list_end_index_set[end]):
                continue
            content=[]
            element=[]
            cont=[]
            set_table=lines[int(list_start_index_set[start]):int(list_end_index_set[end])]
            if len(load_discharge)>1:

                for d in range(0,len(load_discharge)):
                    vessel=''
                    vesel_location=''
                    if(load_discharge[d]<int(list_start_index_set[start])):
                        if(load_discharge[d+1]<int(list_start_index_set[start])):
                            if(re.search('\s*(LOAD)+.*',lines[load_discharge[d+1]])):
                                vessel=lines[load_discharge[d+1]].split(':')[1].split('-')[0]
                                vesel_location=lines[load_discharge[d+1]].split(':')[1].split('-')[1]
                                if re.search('\s*(Inspector)+.*(Inspection Status)+.*',str(lines[load_discharge[d+1]+1])):
                                    lo_dis=''
                                    
                                    lines[load_discharge[d+1]+1]=lines[load_discharge[d+1]+1].split(' ')
                                    for i in lines[load_discharge[d+1]+1]:
                                        if(i=='Inspector'):
                                            lines[load_discharge[d+1]+1].remove(i)
                                    for i in lines[load_discharge[d+1]+1]:
                                        if(i!='Inspection'):
                                            lo_dis=lo_dis+i+' '
                                        else:
                                            break

                                #     if(i=='LOAD:' or i=='DISCHARGE:'):

                                #         lines[load_discharge[d+1]].remove(i)

                                # for i in lines[load_discharge[d+1]]:

                                #     lo_dis=lo_dis+i+' '

                                # # print(lines[load_discharge[d+1]])
                                lo_dis=re.sub('\s+(Inspector:)+','',lo_dis)
                                lo_dis=re.sub('\s+',' ',lo_dis)

                                cont.append('LOAD')
                                cont.append(lo_dis)
                                cont.append(vessel)
                                cont.append(vesel_location)
                                # cont.append(nomination_key(lines[d+1:]))

                                break

                            if(re.search(r'\s*(DISCHARGE)+.*',lines[load_discharge[d+1]])):
                                vessel=lines[load_discharge[d+1]].split(':')[1].split('-')[0]
                                vesel_location=lines[load_discharge[d+1]].split(':')[1].split('-')[1]
                                if re.search('\s*(Inspector)+.*(Inspection Status)+.*',str(lines[load_discharge[d+1]+1])):
                                    lo_dis=''
                                    
                                    lines[load_discharge[d+1]+1]=lines[load_discharge[d+1]+1].split(' ')
                                    for i in lines[load_discharge[d+1]+1]:
                                        if(i=='Inspector'):
                                            lines[load_discharge[d+1]+1].remove(i)
                                    for i in lines[load_discharge[d+1]+1]:
                                        if(i!='Inspection'):
                                            lo_dis=lo_dis+i+' '
                                        else:
                                            break
                                # lo_dis=''

                                # lines[load_discharge[d+1]]=lines[load_discharge[d+1]].split(' ')

                                # for i in lines[load_discharge[d+1]]:

                                #     if(i=='LOAD:' or i=='DISCHARGE:'):

                                #         lines[load_discharge[d+1]].remove(i)

                                # for i in lines[load_discharge[d+1]]:

                                #     lo_dis=lo_dis+i+' '
                                lo_dis=re.sub('\s+(Inspector:)+','',lo_dis)
                                lo_dis=re.sub('\s+',' ',lo_dis)
                                cont.append('DISCHARGE')
                                cont.append(lo_dis)
                                cont.append(vessel)
                                cont.append(vesel_location)
                                # cont.append(nomination_key(lines[d+1:]))

                                break

                            break

                        else:

                            # print(lines[load_discharge[d]])

                            if(re.search(r'\s*(LOAD)+.*',lines[load_discharge[d]])):
                                vessel=lines[load_discharge[d]].split(':')[1].split('-')[0]
                                vesel_location=lines[load_discharge[d]].split(':')[1].split('-')[1]
                                if re.search('\s*(Inspector)+.*(Inspection Status)+.*',str(lines[load_discharge[d]+1])):
                                    lo_dis=''
                                    
                                    lines[load_discharge[d]+1]=lines[load_discharge[d]+1].split(' ')
                                    for i in lines[load_discharge[d]+1]:
                                        if(i=='Inspector'):
                                            lines[load_discharge[d]+1].remove(i)
                                    for i in lines[load_discharge[d]+1]:
                                        if(i!='Inspection'):
                                            lo_dis=lo_dis+i+' '
                                        else:
                                            break
                                # lo_dis=''

                                # lines[load_discharge[d]]=lines[load_discharge[d]].split(' ')

                                # for i in lines[load_discharge[d]]:

                                #     if(i=='LOAD:' or i=='DISCHARGE:'):

                                #         lines[load_discharge[d]].remove(i)

                                # for i in lines[load_discharge[d]]:

                                #     lo_dis=lo_dis+i+' '

                                # print(lines[load_discharge[d+1]])
                                lo_dis=re.sub('\s+(Inspector:)+','',lo_dis)
                                lo_dis=re.sub('\s+',' ',lo_dis)
                                cont.append('LOAD')
                                cont.append(lo_dis)
                                cont.append(vessel)
                                cont.append(vesel_location)
                                # cont.append(nomination_key(lines[d:]))

                                break

                        

                            if(re.search(r'\s*(DISCHARGE)+\s*(:|-)*\s*.*',lines[load_discharge[d]])):
                                vessel=lines[load_discharge[d]].split(':')[1].split('-')[0]
                                vesel_location=lines[load_discharge[d]].split(':')[1].split('-')[1]
                                if re.search('\s*(Inspector)+.*(Inspection Status)+.*',str(lines[load_discharge[d]+1])):
                                    lo_dis=''
                                    
                                    lines[load_discharge[d]+1]=lines[load_discharge[d]+1].split(' ')
                                    for i in lines[load_discharge[d]+1]:
                                        if(i=='Inspector'):
                                            lines[load_discharge[d]+1].remove(i)
                                    for i in lines[load_discharge[d]+1]:
                                        if(i!='Inspection'):
                                            lo_dis=lo_dis+i+' '
                                        else:
                                            break
                                lo_dis=re.sub('\s+(Inspector:)+','',lo_dis)
                                lo_dis=re.sub('\s+',' ',lo_dis)
                                # lo_dis=''

                                # lines[load_discharge[d]]=lines[load_discharge[d]].split(' ')

                                # for i in lines[load_discharge[d]]:

                                #     if(i=='LOAD:' or i=='DISCHARGE:'):

                                #         lines[load_discharge[d]].remove(i)

                                # for i in lines[load_discharge[d]]:

                                #     lo_dis=lo_dis+i+' '

                                # print(lines[load_discharge[d+1]])

                                cont.append('DISCARGE')
                                cont.append(lo_dis)
                                cont.append(vessel)
                                cont.append(vesel_location)
                                # cont.append(nomination_key(lines[d:]))

                                break

                            break

            else:

                # print(lines[load_discharge[0]])
                if(re.search(r'\s*(LOAD)+.*',lines[load_discharge[0]])):
                    vessel=lines[load_discharge[0]].split(':')[1].split('-')[0]
                    vesel_location=lines[load_discharge[0]].split(':')[1].split('-')[1]
                    # print('Ashish')
                    if re.search('\s*(Inspector)+.*(Inspection Status)+.*',str(lines[load_discharge[0]+1])):
                        lo_dis=''
                        # print('@@@@@@@@@@@@@@@@@@@@@@@@@')
                        lines[load_discharge[0]+1]=lines[load_discharge[0]+1].split(' ')
                        for i in lines[load_discharge[0]+1]:
                            if(i=='Inspector'):
                                lines[load_discharge[0]+1].remove(i)
                        for i in lines[load_discharge[0]+1]:
                            if(i!='Inspection'):
                                lo_dis=lo_dis+i+' '
                            else:
                                break
                    lo_dis=re.sub('\s+(Inspector:)+','',lo_dis)
                    lo_dis=re.sub('\s+',' ',lo_dis)
                    cont.append('LOAD')
                    cont.append(lo_dis)
                    cont.append(vessel)
                    cont.append(vesel_location)
                    # cont.append(nomination_key(lines[0:]))
                # lo_dis=''

                # lines[load_discharge[0]]=str(lines[load_discharge[0]]).split(' ')

                # for i in lines[load_discharge[0]]:

                #     if(i=='LOAD:' or i=='DISCHARGE:'):

                #         lines[load_discharge[0]].remove(i)

                # for i in lines[load_discharge[0]]:

                #     lo_dis=lo_dis+i+' '

                # # print(lines[load_discharge[d+1]])
                if(re.search(r'\s*(DISCHARGE)+\s*(:|-)*\s*.*',lines[load_discharge[0]])):
                    # print('Aditya')
                    vessel=lines[load_discharge[0]].split(':')[1].split('-')[0]
                    vesel_location=lines[load_discharge[0]].split(':')[1].split('-')[1]
                    if re.search('\s*(Inspector)+.*(Inspection Status)+.*',str(lines[load_discharge[0]+1])):
                        lo_dis=''
                        # print('#############################')
                        lines[load_discharge[0]+1]=lines[load_discharge[0]+1].split(' ')
                        for i in lines[load_discharge[0]+1]:
                            if(i=='Inspector:'):
                                lines[load_discharge[0]+1].remove(i)
                        for i in lines[load_discharge[0]+1]:
                            if(i!='Inspection:'):
                                lo_dis=lo_dis+i+' '

                            else:
                                break
                    lo_dis=re.sub('\s+(Inspector:)+','',lo_dis)
                    lo_dis=re.sub('\s+',' ',lo_dis)
                    # print('This is lo_dis',lo_dis)
                    cont.append('DISCHARGE')
                    cont.append(lo_dis)
                    cont.append(vessel)
                    cont.append(vesel_location)
                    # cont.append(nomination_key(lines))

#############################################################################
                # int(set_table)
            # print(cont)    
            print('***********************************')
            for one_line in range(0,len(set_table)):
                if(re.search('\s*((SET)|(Set))+\s*(:|-)*\d+\s*',set_table[one_line])):
                    start_set=int(one_line)
                    element.append(start_set)
                    # print(start_set,'start_set')
                if(re.search('\s*((Description)|(DESCRIPTION)|(description))+\s*(:|-)*.*',set_table[one_line])):
                    end_set_start_Description=int(one_line)
                    element.append(end_set_start_Description)
                    # print(end_set_start_Description)
                if(re.search('\s*((Sample)|(SAMPLE))+\s*((Location)|(LOCATION))+\s*(:|-)*.*',set_table[one_line])):
                    end_description_start_Sample=int(one_line)
                    # print(end_description_start_Sample)
                    element.append(end_description_start_Sample)
                if(re.search('((\s*((Quality)|(QUALITY))+\s*((TEST)|(Test))+\s*((Comments)|(COMMENTS))+\s*(:|-)*\s*.*)|((Test|TEST|test)+\s*(Methods|METHODS|methods)+\s*(MIN|min|Min)+\s*(Max|max|MAX)+\s*(UOM|uom|Uom)+\s*(Typical|TYPICAL|typical)+\s*(R.o.|r.o.|R.O.)+\s*(Req.|req.|REQ.)+\s*(Comment|comment|COMMENT)+))',set_table[one_line])):
                    end_table=int(one_line)
                    element.append(end_table)
                    # print(end_table)
            # print(element)
            start_table_set_no=set_table[int(element[0]):int(element[1])]
            number=''
            no_=''
            # print(start_table_set_no)
            for i in start_table_set_no:
                number=number+i
            number=number.split(' ')
            for check in number:
                if(check in fields):
                    number.remove(check) 
            for i in number:
                no_=no_+i+' '
            no_ = re.sub(r'(TRIP).*','',no_)
            no_=re.sub(r'\s+',' ',no_)
            start_table_set_description=set_table[int(element[1]):int(element[2])]
            description=''
            desc=''
            for i in start_table_set_description:
                description=description+i
            description=description.split(' ')
            for check in description:
                if(check in fields):
                    description.remove(check)
            for i in description:
                desc=desc+i+' '
            # print(start_table_set_description)
            desc=re.sub('\s+',' ',desc)
            start_table_set_location=set_table[int(element[2]):]
            location =''
            loc=''
            for i in start_table_set_location:
                location=location+i
            location=location.split(' ')
            for check in location:
                if(check in fields):
                    location.remove(check)
            for i in location:
                loc=loc+i+' '
            loc=re.sub('\s+',' ',loc)
            loc=loc[10:]
            # content.append([no_,desc,loc,cont[0],cont[1]])
            content.append([no_,desc,loc,cont[1],cont[2],cont[3]])
            # print(content)
            break
        all_set_content.append(content)
        # break
    # print(all_set_content)
    return(all_set_content)
                    


def Quality_line_items(lines):
    list_of_dicts=[]
    for line in lines:
        if(re.search(r'.*(Trip|TRIP|trip)+(:)*.*',line) and re.search('(\(ISSUED\)).*',line)):
            lines.remove(line)
        if(re.search(r'.*\s*(Page|PAGE|page)+\s*\d*\s*(of)+\s*\d*.',line)):
            lines.remove(line)
        if(re.search(r'.*((RO = Report Only)|(Required))+.*',line)):
            lines.remove(line)
        if(re.search(r'.*(Additional Tests)+\s*',line)):
            lines.remove(line)


    start_table=[]
    end_table=[]
    for line in range(0,len(lines)):
        start_index_Test=re.search('(Test|TEST|test)+\s*(Methods|METHODS|methods)+\s*(MIN|min|Min)+\s*(Max|max|MAX)+\s*(UOM|uom|Uom)+\s*(Typical|TYPICAL|typical)+\s*(R.o.|r.o.|R.O.)+\s*(Req.|req.|REQ.)+\s*(Comment|comment|COMMENT)+',lines[line])
        if(start_index_Test!=None):        
            start_table.append(line)
    for line in range(0,len(lines)):
        table_end=re.search('((Invoice Instructions:)|(SET 2)|(SET 3))+(:)*',lines[line])
        if(table_end!=None):
            end_table.append(line)
    # print("ANUPAAAAAAAAAAAAMMMMM  431")
    if len(start_table)<1:
        final = [[['','','','','','','','']]]
        list_of_dicts = []

        # keys=['Test Name','Test Code','Comment','set_no','set_description','sample_location','Activity_type','Inspector']
        keys=['Test Name','Test Code','Comment','set_no','set_description','sample_location','vessel','vessel_location']
        # Iterate through the nested structure

        for outer_list in final:

            # Create a list of dictionaries for each inner list

            inner_list_dicts = []

            for sub_list in outer_list:

            # Use zip to pair the keys with the values from the sub-list

                sub_dict = dict(zip(keys, sub_list))

                inner_list_dicts.append(sub_dict)

            list_of_dicts.append(inner_list_dicts)
        return list_of_dicts

    else:
        start_table.append(1)

        count=0

        no_of_tables=[]
        for i in range(0,len(start_table)-1):
            if(start_table[i]!=start_table[i+1]):
                for j in range(i+0,len(end_table)):
                
                    if((start_table[i]<start_table[i+1])):
                        if((start_table[i+1]<end_table[j])):
                            full_table=lines[int(start_table[i]):int(end_table[j])]

                            for one in full_table:
                                if(re.search('.*((TRIP)|(Trip)|(trip))+(:)*.*',one)):
                                    full_table.remove(one)
                                # if(re.search('(Test|TEST|test)+\s*(Methods|METHODS|methods)+\s*(MIN|min|Min)+\s*(Max|max|MAX)+\s*(UOM|uom|Uom)+\s*(Typical|TYPICAL|typical)+\s*(R.o.|r.o.|R.O.)+\s*(Req.|req.|REQ.)+\s*(Comment|comment|COMMENT)+',one)):
                                #     count=count+1
                                #     if(count>1):
                                #         full_table.remove(one)
                            # print(full_table)
                            start_table.remove(start_table[i+1])
                            start_table.append(1)
                            # a.append(full_table)
                            # print(full_table)
                            no_of_tables.append(full_table)
                            break
                        else:
                            # a=[]
                            full_table=lines[int(start_table[i]):int(end_table[j])]
                            for one in full_table:
                                if(re.search('.*((TRIP)|(Trip)|(trip))+(:)*.*',one)):
                                    full_table.remove(one)
                            # print(full_table)
                            # a.append(full_table)
                            # print(full_table)
                            no_of_tables.append(full_table)
                            break
                    else:
                        a=[]
                        full_table=lines[int(start_table[i]):int(end_table[j])]
                        for one in full_table:
                                if(re.search('.*((TRIP)|(Trip)|(trip))+(:)*.*',one)):
                                    full_table.remove(one)
                        # print(full_table)
                        # a.append(full_table)
                        # print(full_table)
                        no_of_tables.append(full_table)
                        break
                # no_of_tables.append(a)
            else:
                break
        # print(no_of_tables)
        total_list=[]
        # one_table_data=[]
        for one_element in no_of_tables:
            one_table_data=[]
            for one_line in range(0,len(one_element)):
                # print(one_element[one_line])

                if(re.search(r'(Test|TEST|test)+\s*(Methods|METHODS|methods)+\s*(MIN|min|Min)+\s*(Max|max|MAX)+\s*(UOM|uom|Uom)+\s*(Typical|TYPICAL|typical)+\s*(R.o.|r.o.|R.O.)+\s*(Req.|req.|REQ.)+\s*(Comment|comment|COMMENT)+',one_element[one_line])):
                    start_index_Test=re.search(r'\s*Test',one_element[one_line])
                    end_index_Test=re.search(r'Methods',one_element[one_line])
                    # print('1',start_index_Test.span(),end_index_Test.span())

                    start_index_Methods=re.search(r'Methods',one_element[one_line])
                    end_index_Methods=re.search(r'Min',one_element[one_line])
                    # print('2',start_index_Methods.span(),end_index_Methods.span())

                    start_index_Min=re.search(r'Min',one_element[one_line])
                    end_index_Min=re.search(r'Max',one_element[one_line])
                    # print('3',start_index_Min.span(),end_index_Min.span())

                    start_index_Max=re.search(r'Max',one_element[one_line])
                    end_index_Max=re.search(r'UOM',one_element[one_line])
                    # print('4',start_index_Max.span(),end_index_Max.span())

                    start_index_UOM=re.search(r'UOM',one_element[one_line])
                    end_index_UOM=re.search(r'Typical',one_element[one_line])
                    # print('5',start_index_UOM.span(),end_index_UOM.span())

                    start_index_Typical=re.search(r'Typical',one_element[one_line])
                    end_index_Typical=re.search(r'(R.O.)',one_element[one_line])
                    # print('6',start_index_Typical.span(),end_index_Typical.span())

                    start_index_R_O_=re.search(r'(R.O.)',one_element[one_line])
                    end_index_R_O_=re.search(r'(Req.)',one_element[one_line])
                    # print('7',start_index_R_O_.span(),end_index_R_O_.span())

                    start_index_Req_=re.search(r'(Req.)',one_element[one_line])
                    end_index_Req_=re.search(r'Comment',one_element[one_line])
                    # print('8',start_index_Req_.span(),end_index_Req_.span())

                    start_index_Comment=re.search(r'Comment',one_element[one_line])
                    # print('9',start_index_Comment.span())
                else:
                    one_table_data.append([one_element[one_line][start_index_Test.span()[0]:end_index_Test.span()[0]],one_element[one_line][start_index_Methods.span()[0]:end_index_Methods.span()[0]],one_element[one_line][start_index_Min.span()[0]:end_index_Min.span()[0]],one_element[one_line][start_index_Max.span()[0]:end_index_Max.span()[0]],one_element[one_line][start_index_UOM.span()[0]:end_index_UOM.span()[0]],one_element[one_line][start_index_Typical.span()[0]:end_index_Typical.span()[0]],one_element[one_line][start_index_R_O_.span()[0]:end_index_R_O_.span()[0]],one_element[one_line][start_index_Req_.span()[0]:end_index_Req_.span()[0]],one_element[one_line][start_index_Comment.span()[0]:]])
                    
            total_list.append(one_table_data)
                

        final=[]
        for each_table in total_list:
            for one_list in range(0,len(each_table)):
                        try:
                            for one_list in range(0,len(each_table)):
                                each_table[one_list][6]=re.sub(r'\s+','',each_table[one_list][6])
                                each_table[one_list][7]=re.sub(r'\s+','',each_table[one_list][7])
                                try:
                                    if(each_table[one_list][6]=='' and each_table[one_list][7]==''):
                                        
                                        # print(each_table[one_list])
                                        each_table[one_list-1][0]=each_table[one_list-1][0].rstrip()+each_table[one_list][0].rstrip()
                                        each_table[one_list-1][0]=re.sub('\s+',' ',each_table[one_list-1][0])

                                        each_table[one_list-1][1]=each_table[one_list-1][1].rstrip()+each_table[one_list][1].rstrip()
                                        each_table[one_list-1][1]=re.sub('\s\s+','',each_table[one_list-1][1])
                                        each_table[one_list-1][1].strip()

                                        each_table[one_list-1][2]=each_table[one_list-1][2]+each_table[one_list][2]
                                        each_table[one_list-1][2]=re.sub('\s+',' ',each_table[one_list-1][2])

                                        each_table[one_list-1][3]=each_table[one_list-1][3].rstrip()+each_table[one_list][3].rstrip()
                                        each_table[one_list-1][3]=re.sub('\s+',' ',each_table[one_list-1][3])

                                        each_table[one_list-1][4]=each_table[one_list-1][4]+each_table[one_list][4]
                                        each_table[one_list-1][4]=re.sub('\s+',' ',each_table[one_list-1][4])

                                        each_table[one_list-1][5]=each_table[one_list-1][5]+each_table[one_list][5]
                                        each_table[one_list-1][5]=re.sub('\s+',' ',each_table[one_list-1][5])

                                        each_table[one_list-1][6]=each_table[one_list-1][6]+each_table[one_list][6]
                                        each_table[one_list-1][6]=re.sub('\s+',' ',each_table[one_list-1][6])

                                        each_table[one_list-1][7]=each_table[one_list-1][7]+each_table[one_list][7]
                                        each_table[one_list-1][7]=re.sub('\s+',' ',each_table[one_list-1][7])

                                        each_table[one_list-1][8]=each_table[one_list-1][8]+each_table[one_list][8]
                                        each_table[one_list-1][8]=re.sub('\s+',' ',each_table[one_list-1][8])
                                        
                                        each_table.remove(each_table[one_list])
                                        break
                                except:
                                    pass
                            # line_list.append(each_table)
                        except:
                            pass
            final.append(each_table)


        # keys=['test','methods','comment','set_no','set_description','sample_location','Activity_type','Inspector']
        keys=['TestName','TestCode','Comments','SetNo','SetDescription','SampleLocation','VendorName','VesselName','JobLocation']
        for i in final:
            for j in i:
                j[2:-1]=[]

        
        op = set_func(lines)
        # vessel = vessel_name(lines)
        # nom = nomination_key(lines)
        # print('op',op)
        # print('this is vessel',vessel)
        # print('this is nom',nom)
        for i in final:
            for i in range(0,len(final)):
                for j in range(i+0,len(op)):
                    for d in final[i]:
                        for y in op[j]:
                            d.extend(y)
                    break
        final = [[[element.strip() for element in inner_list] for inner_list in outer_list] for outer_list in final]
        list_of_dicts = []


        for outer_list in final:

            inner_list_dicts = []

            for sub_list in outer_list:


                sub_dict = dict(zip(keys, sub_list))

                inner_list_dicts.append(sub_dict)

            list_of_dicts.append(inner_list_dicts)

            

            # Print the list of dictionaries in the desired format
        # print(list_of_dicts,"YYYYYYYYY::::::::")
        return list_of_dicts
    

# data = Quality_line_items(lines)
# print(data)


# conn = pyodbc.connect(

# 'Driver=ODBC Driver 17 for SQL Server;Server=LP-221216061\SQLEXPRESS;Database=My_Local_EM;Trusted_Connection=yes;'

# )

# cursor = conn.cursor()





# insert_statement = "INSERT INTO Exacto_cgi_nomination_quality_lineitem ( set_description ,set_no, sample_location, test, methods, comment ) VALUES (?, ?, ?, ?, ?, ?)"





# for table_data in data:

#     for row in table_data:

#         values = (row.get('set_description',''), row.get('set_no',''), row.get('sample_location',''), row.get('test',''), row.get('methods',''), row.get('comment',''))

#         cursor.execute(insert_statement, values)

    

    

# conn.commit()





# cursor.close()

# conn.close()




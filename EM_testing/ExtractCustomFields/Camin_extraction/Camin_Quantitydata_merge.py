def Camin_qnt_hd_li_merge(qnty_header_data,qnty_line_item):
    qnty_data=[]
    temp=qnty_header_data
    if qnty_line_item !={}:
        for i in qnty_line_item:
            d={}
            d=temp
            d['NominatedQuantity']=qnty_line_item[i]
            d['UnitOfMeasure']=i
            qnty_data.append(d)
            
    return qnty_data 
        
        
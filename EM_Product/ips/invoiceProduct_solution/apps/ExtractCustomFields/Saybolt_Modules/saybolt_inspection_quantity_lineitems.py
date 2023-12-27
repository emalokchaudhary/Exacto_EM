import re
from ExtractCustomFields.EM_logging import logger
# path = open(r'/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Saybolt/US/1300400686/CBC307_2021-BR-SNO-AC600-01_Discharge_AC600_Discharge_DeerPark_24February2021.text')
# doc = path.readlines()
def productnamecqq(doc):
    final = []
    final_1 =[]
    for i,line in enumerate(doc):
        match = re.search('^Product\s\s+',line)
        if i<len(doc)-1:
            match1 = re.search('\s\s+Certificate of Quantity',doc[i+1])
        if match and match1:
            a = match1.group()
            lst = re.split('\s\s+',line)
            final.append(lst[1])
        else:
            continue
    for j in final:
        j = re.sub('\n','',j)
        final_1.append(j)
        # final_1 = list(set(final_1))
        # print(final_1)
        
            
    return final_1  

def productnamereport(doc):
    final = []
    final_1 =[]
    for i,line in enumerate(doc):
        match = re.search('^Product\s\s+',line)
        if i<len(doc)-4:
            match1 = re.search('\s\s+SUMMARY REPORT',doc[i+3])
        # if match1:
        #     print('yeahhhhhh')
        if match and match1:
            
            a = match1.group()
            lst = re.split('\s\s+',line)
            final.append(lst[1])
        else:
            continue
    for j in final:
        j = re.sub('\n','',j)
        final_1.append(j)
        # final_1 = list(set(final_1))
        # print(final_1)
        
    # print(final_1)      
    return final_1    


def productnameloading(doc):
    final = []
    final_1 =[]
    for i,line in enumerate(doc):
        match = re.search('^Product\s\s+',line)
        if i<len(doc)-1:
            match1 = re.search('\s\s+(Summary Loading [(]GSV[)])',doc[i+1])
        if match and match1:
            a = match1.group()
            lst = re.split('\s\s+',line)
            final.append(lst[1])
        else:
            continue
    for j in final:
        j = re.sub('\n','',j)
        final_1.append(j)
        # final_1 = list(set(final_1))
        # print(final_1)
        
            
    return final_1 

def productnamedischarge(doc):
    final = []
    final_1 =[]
    for i,line in enumerate(doc):
        match = re.search('^Product\s\s+',line)
        if i<len(doc)-1:
            match1 = re.search('\s\s+(Summary Discharge [(]GSV[)])',doc[i+1])
        if match and match1:
            a = match1.group()
            lst = re.split('\s\s+',line)
            final.append(lst[1])
        else:
            continue
    for j in final:
        j = re.sub('\n','',j)
        final_1.append(j)
        # final_1 = list(set(final_1))
        # print(final_1)
        
            
    return final_1 

def SummaryReport(doc):
    lst = []
    dictlist =  []
    finaldictlist = []
    finaldictlist1 = []
    for i,line in enumerate(doc):
        lines = []
        search = re.search('\s\s+SUMMARY REPORT',line,re.IGNORECASE)
        if search:
            if search:
                    # print(' Yes search')
                    for j in range(i+5,len(doc)):
                        search1 = re.search('\s\s+VESSEL QUANTITY RECEIVED',doc[j])
                        if not search1:
                            doc[j] = re.sub('\n','',doc[j])
                            doc[j] = re.sub('[:]','',doc[j])
                            doc[j] = re.sub('\s*(G.S.V.)\s+','',doc[j])
                            if len(doc[j].split())>0:
                                doclst = re.split('\s+[*]\s+|\s\s+|\s+[:]\s+',doc[j])
                                # print(doclst)
                                lines.append(doclst)
                            # print(doc[j])
                        else:
                            break
                    lst.append(lines)
                

    # print('List doc *****\n',lst)

    for val in lst:
            finaldict = {}
            for line in val:
                line[1] = re.sub(',','',line[1])
                try:
                    finaldict[line[0]] = float(line[1])
                except:
                    pass
            # print('Finaldict ********',finaldict)
            dictlist.append(finaldict)
            
    for finaldict in dictlist:
            unit = finaldict.keys()
            values = finaldict.values()
            units = []
            val1  = []
            valu = []
            for i in values:
                valu.append(i)

            # print(valu)
            for i in unit:
                i = re.sub('\s*[@]\s*.*','',i)   
                i = re.sub('Metric Tons.*','Metric Tons',i,re.IGNORECASE)
                i = re.sub('Cubic meters.*','Cubic meters',i,re.IGNORECASE)
                i = re.sub('Liters.*','Liters',i,re.IGNORECASE)
                i = re.sub('(US Gallons).*','US Gallons',i,re.IGNORECASE)
                i = re.sub('Gallons.*','Gallons',i,re.IGNORECASE)
                i = re.sub('Barrels.*','Barrels',i,re.IGNORECASE)
                i = re.sub('Kilos.*','Kilos',i,re.IGNORECASE)
                units.append(i)

            # print(units)
            unit_1 = list(set(units))
            # print(unit_1)

            for i in unit_1:
                # print(i)
                val = []
                for j in range(len(units)):
                    # print(i)
                    if units[j]==i:
                        # index.append(j)
                        val.append(valu[j])
                        # print(valu[j])
                # print('@@@@@@',val)
                val1.append(max(val))    


            # print(val1)
            # print(unit_1)

            for i in val1:
                dict1 = dict(zip(unit_1,val1))
            
            finaldictlist.append(dict1)

    # print(finaldictlist)
    prodname = productnamereport(doc)
    for i,finaldict in enumerate(finaldictlist):
        finaldict['ProductName'] = prodname[i]
        finaldictlist1.append(finaldict)

    return finaldictlist1
            
        
def QuantityLineItems(doc):
    lst = []
    dictlist =  []
    finaldictlist = []
    finaldictlist1 = []
    for i,line in enumerate(doc):
            lines = []
            search = re.search('\s\s+Certificate of Quantity',line)
            # search_1 = re.search('(\s*GSV Figures\s+ Bill of Lading.*)',line)
            # search_2 = re.search('\s+Bill Of Lading Report',line)
            if search:
                # print(' Yes search')
                for j in range(i+5,len(doc)):
                    search1 = re.search('(as calculated by Saybolt only.)|(These quantities have been determined by Shore tank measurements)|(These quantities have been determined by .)',doc[j])
                    if not search1:
                        doc[j] = re.sub('\n','',doc[j])
                        if len(doc[j].split())>0:
                            doclst = re.split('\s+[*]\s+|\s\s+',doc[j])
                            # print(doclst)
                            lines.append(doclst)
                        # print(doc[j])
                    else:
                        break
                lst.append(lines)
            
    # print('List doc *****',len(lst))
    for val in lst:
        finaldict = {}
        for line in val:
            line[1] = re.sub(',','',line[1])
            try:
                finaldict[line[0]] = float(line[1])
            except:
                pass
        # print('Finaldict ********',finaldict)
        dictlist.append(finaldict)
        

    for finaldict in dictlist:
        unit = finaldict.keys()
        values = finaldict.values()
        units = []
        val1  = []
        valu = []
        for i in values:
            valu.append(i)

        # print(valu)
        for i in unit:
            i = re.sub('\s*[@]\s*.*','',i)   
            i = re.sub('Metric Tons.*','Metric Tons',i,re.IGNORECASE)
            i = re.sub('Cubic meters.*','Cubic meters',i,re.IGNORECASE)
            i = re.sub('Liters.*','Liters',i,re.IGNORECASE)
            i = re.sub('(US Gallons).*','US Gallons',i,re.IGNORECASE)
            i = re.sub('Gallons.*','Gallons',i,re.IGNORECASE)
            i = re.sub('Barrels.*','Barrels',i,re.IGNORECASE)
            i = re.sub('Kilos.*','Kilos',i,re.IGNORECASE)
            units.append(i)

        # print(units)
        unit_1 = list(set(units))
        # print(unit_1)

        for i in unit_1:
            # print(i)
            val = []
            for j in range(len(units)):
                # print(i)
                if units[j]==i:
                    # index.append(j)
                    val.append(valu[j])
                    # print(valu[j])
            # print('@@@@@@',val)
            val1.append(max(val))    


        # print(val1)
        # print(unit_1)

        for i in val1:
            dict1 = dict(zip(unit_1,val1))
        
        finaldictlist.append(dict1)
    
    prodname = productnamecqq(doc)
    # print(prodname)
    for i,finaldict in enumerate(finaldictlist):
        finaldict['ProductName'] = prodname[i]
        finaldictlist1.append(finaldict)
    
    return finaldictlist1

def SummaryLoadingGSV(doc):
    lst = []
    dictlist =  []
    finaldictlist = []
    finaldictlist1 = []
    for i,line in enumerate(doc):
        loading = []
        match = re.search('\s\s+(Summary Loading [(]GSV[)])',line)
        # match1 = re.search('\s\s+(Summary Discharge [(]GSV[)])',line)
        if match:
            for j in range(i+6,len(doc)):
                search1 = re.search('GSV Figures [(]VEF Adjusted[])].*',doc[j])
                if not search1:
                    doc[j] = re.sub('\n','',doc[j])
                    if len(doc[j].split())>0:
                        doclst = re.split('\s+[*]\s+|\s\s+',doc[j])
                        # print(doclst)
                        loading.append(doclst)
                    # print(doc[j])
                if search1:
                    break
            lst.append(loading)

    

    # print(loading)

    for val in lst:
        finaldict = {}
        for line in val:
            line[1] = re.sub(',','',line[1])
            line[2] = re.sub(',','',line[2])
            try:
                finaldict[line[0]] = float(line[2])
            except:
                pass
        dictlist.append(finaldict)

    for finaldict in dictlist:
        unit = finaldict.keys()
        values = finaldict.values()
        units = []
        val1  = []
        valu = []
        for i in values:
            valu.append(i)

        # print(valu)
        for i in unit:
            i = re.sub('\s*[@]\s*.*','',i)   
            i = re.sub('Metric Tons.*','Metric Tons',i,re.IGNORECASE)
            i = re.sub('Cubic meters.*','Cubic meters',i,re.IGNORECASE)
            i = re.sub('Liters.*','Liters',i,re.IGNORECASE)
            i = re.sub('(US Gallons).*','US Gallons',i,re.IGNORECASE)
            i = re.sub('Gallons.*','Gallons',i,re.IGNORECASE)
            i = re.sub('Barrels.*','Barrels',i,re.IGNORECASE)
            i = re.sub('Kilos.*','Kilos',i,re.IGNORECASE)
            units.append(i)

        # print(units)
        unit_1 = list(set(units))
        # print(unit_1)

        for i in unit_1:
            # print(i)
            val = []
            for j in range(len(units)):
                # print(i)
                if units[j]==i:
                    # index.append(j)
                    val.append(valu[j])
                    # print(valu[j])
            # print('@@@@@@',val)
            val1.append(max(val))    


        # print(val1)
        # print(unit_1)

        for i in val1:
            dict1 = dict(zip(unit_1,val1))
        
        finaldictlist.append(dict1)
    
    prodname = productnameloading(doc)
    # print(prodname)
    for i,finaldict in enumerate(finaldictlist):
        finaldict['ProductName'] = prodname[i]
        finaldictlist1.append(finaldict)

    return finaldictlist

def loadingsummary(doc):
    finaldictlist = []
    finaldictlist1 = []
    productname = []
    for i,line in enumerate(doc):
        landingsummary = []
        landing = []
        finallanding = []
        if i==2 and len(line.strip())>0:
            productname.append(line.strip())
        match1 = re.search('Bill of Lading|Bill of Landing',line)
        match2 = re.search('Outturn.*',line)
        # span = match1.span()
        if match1:
            # print('yes')
            span = match1.span()
            # print(span)
            for j in range(i+2,len(doc)):
                search1 = re.search('Density.*',doc[j])
                if not search1:
                    doc[j] = re.sub('\n','',doc[j])
                    if len(doc[j].split())>0:
                        # doclst = re.split('\s+[*]\s+|\s\s+',doc[j])
                        # print(doclst)
                        landing.append(doc[j][span[0]-2:])
                    # print(doc[j])
                if search1:
                    break
            break
        # if match2:
        #     # print('yes')
        #     span = match2.span()
        #     # print(span)
        #     for j in range(i+2,len(doc)):
        #         search1 = re.search('Density.*',doc[j])
        #         if not search1:
        #             doc[j] = re.sub('\n','',doc[j])
        #             if len(doc[j].split())>0:
        #                 # doclst = re.split('\s+[*]\s+|\s\s+',doc[j])
        #                 # print(doclst)
        #                 landing.append(doc[j][span[0]-3:])
        #                 # print(doc[j][span[0]-3:])
        #         if search1:
        #             # print('Yes')
        #             break
        #     break
    
    for i,line in enumerate(landing):
        line = re.sub('                                                 →         Discharged','',line)
        if len(line.strip())<7:#change made acccording to document in EU region 
            landing.pop(i)

    # print("@@@@@@@",landing)
    for i in range(0,len(landing),2):
            if i < len(landing)-1:
                v = []
                landing[i] = re.sub('\s+[-]*\d*[.]*\d+','  ',landing[i])
                landing[i+1] = re.sub(r'\s(\d+)',lambda match:match.group(1),landing[i+1])
                # print(landing[i])
                an = landing[i+1].strip().split('  ')[0]
                # print(an)
                ln= landing[i]+'  '+an
                # print(a[i])
                v.append(ln)
                landingsummary.append(v)
        

    for line in landingsummary:
        # print(line)
        for val in line:
            if len(val.strip())>1:
                # print(val)
                summ = re.split('\s\s+',val)
                finallanding.append(summ)

    # print(finallanding)

    finaldict = {}
    for line in finallanding:
        line[1] = re.sub(',','',line[1])
        # line[2] = re.sub(',','',line[2])
        try:
            finaldict[line[0]] = float(line[1])
        except:
            pass
    # print(finaldict)

    unit = finaldict.keys()
    values = finaldict.values()
    units = []
    val1  = []
    valu = []
    for i in values:
        valu.append(i)

    # print(valu)
    for i in unit:
        i = re.sub('\s*[@]\s*.*','',i)   
        i = re.sub('Metric Tons.*','Metric Tons',i,re.IGNORECASE)
        i = re.sub('Cubic meters.*|Cu m.*','Cubic meters',i,re.IGNORECASE)
        i = re.sub('.*Liters.*','Liters',i,re.IGNORECASE)
        i = re.sub('(US Gallons).*','US Gallons',i,re.IGNORECASE)
        i = re.sub('Gallons.*','Gallons',i,re.IGNORECASE)
        i = re.sub('.*Barrels.*','Barrels',i,re.IGNORECASE)
        i = re.sub('.*Kilos.*','Kilos',i,re.IGNORECASE)
        units.append(i)

    # print(units)
    unit_1 = list(set(units))
    # print(unit_1)

    for i in unit_1:
        # print(i)
        val = []
        for j in range(len(units)):
            # print(i)
            if units[j]==i:
                # index.append(j)
                val.append(valu[j])
                # print(valu[j])
        # print('@@@@@@',val)
        val1.append(max(val))    


    # print(val1)
    # print(unit_1)

    for i in val1:
        dict1 = dict(zip(unit_1,val1))
    # print(dict1)
    finaldictlist.append(dict1)
    for i,finaldict in enumerate(finaldictlist):
        finaldict['ProductName'] = productname[i]
        finaldictlist1.append(finaldict)
    return finaldictlist1

def SummaryDischrageGSV(doc):
    lst = []
    dictlist = []
    finaldictlist =[]
    finaldictlist1 = []
    for i,line in enumerate(doc):
            loading = []
            match = re.search('\s\s+(Summary Discharge [(]GSV[)])',line)
            # match1 = re.search('\s\s+(Summary Discharge [(]GSV[)])',line)
            if match:
                # print('yes')
                for j in range(i+15,len(doc)):
                    search1 = re.search('\s*(Density).*',doc[j])
                    if not search1:
                        doc[j] = re.sub('\n','',doc[j])
                        if len(doc[j].split())>0:
                            doclst = re.split('\s+[*]\s+|\s\s+',doc[j])
                            # print(doclst)
                            loading.append(doclst)
                        # print(doc[j])
                    if search1:
                        break
                lst.append(loading)
    # print(lst)

    for val in lst:
            finaldict = {}
            for line in val:
                if len(line)>2:
                    line[1] = re.sub(',','',line[1])
                    line[2] = re.sub(',','',line[2])
                if len(line)<=2:
                    line[1] = re.sub(',','',line[1])
                try:
                    if len(line)>2:
                        finaldict[line[0]] = float(line[2])
                    if len(line)<=2:
                        finaldict[line[0]] = float(line[1])
                except:
                    pass
            dictlist.append(finaldict)
    # print(dictlist)

    for finaldict in dictlist:
        unit = finaldict.keys()
        values = finaldict.values()
        units = []
        val1  = []
        valu = []
        for i in values:
            valu.append(i)

        # print(valu)
        for i in unit:
            i = re.sub('\s*[@]\s*.*','',i)   
            i = re.sub('Metric Tons.*','Metric Tons',i,re.IGNORECASE)
            i = re.sub('Cubic meters.*','Cubic meters',i,re.IGNORECASE)
            i = re.sub('Liters.*','Liters',i,re.IGNORECASE)
            i = re.sub('(US Gallons).*','US Gallons',i,re.IGNORECASE)
            i = re.sub('Gallons.*','Gallons',i,re.IGNORECASE)
            i = re.sub('Barrels.*','Barrels',i,re.IGNORECASE)
            i = re.sub('Kilos.*','Kilos',i,re.IGNORECASE)
            units.append(i)

        # print(units)
        unit_1 = list(set(units))
        # print(unit_1)

        for i in unit_1:
            # print(i)
            val = []
            for j in range(len(units)):
                # print(i)
                if units[j]==i:
                    # index.append(j)
                    val.append(valu[j])
                    # print(valu[j])
            # print('@@@@@@',val)
            val1.append(max(val))    

        for i in val1:
            dict1 = dict(zip(unit_1,val1))
        
        finaldictlist.append(dict1)
    
    prodname = productnamedischarge(doc)
    # print(prodname)
    for i,finaldict in enumerate(finaldictlist):
        finaldict['ProductName'] = prodname[i]
        finaldictlist1.append(finaldict)

    return finaldictlist
            

def FinalQuantityLineItems(read,uuid_doc):
    match1 = re.search('\s\s+Certificate of Quantity',read)
    match2 = re.search('\s\s+(Summary Loading [(]GSV[)])',read)
    match3 = re.search('\s*Bill of Lading\s*|\s*Outturn\s*',read)
    match4 = re.search('(Outturn date:)\s*\w*\s*\w*\s*\w*\s\s+(Summary Discharge [(]GSV[)])|(Outturn date:)\w*\s\s+(Summary Discharge [(]GSV[)])',read)
    match5 = re.search('\s\s+SUMMARY REPORT',read,re.IGNORECASE)
    doc = read.split('\n')
    if match1:
        # statement = 'quantity cerrtificate'
        # print('quantity certificate')
        a = QuantityLineItems(doc)
        logger.info(f'Saybolt Quantity line data -{a}')
        return a
    elif match1 and match2:
        # statement = 'quantity cerrtificate'
        # print('quantity cerrtificate')
        b = QuantityLineItems(doc)
        logger.info(f'Saybolt Quantity line data -{b}') 
        return b
    elif match2:
        # print('GSV')
        c= SummaryLoadingGSV(doc)
        logger.info(f'Saybolt Quantity line data -{c}')
        return c
    elif match1 and match5:
        f = QuantityLineItems(doc)
        logger.info(f'Saybolt Quantity line data -{f}')
        return f
    elif match3 and match5:
        # print('Summ')
        g = SummaryReport(doc)
        logger.info(f'Saybolt Quantity line data -{g}')
        return g
    # elif match3 and match4:
    #     print('Both cases')
    #     f = SummaryDischrageGSV(doc)
        
    elif match3:
        # print('Loading Summary')
        d = loadingsummary(doc)
        logger.info(f'Saybolt Quantity line data -{d}')
        return d
    elif match5:
        # print('Report')
        e = SummaryReport(doc)
        logger.info(f'Saybolt Quantity line data -{e}')
        return e
    # elif match4:
    #     print('discharge')
    #     g = SummaryDischrageGSV(doc)
    #     return g
    elif match4 and match1:
        e = QuantityLineItems(doc)
        logger.info(f'Saybolt Quantity line data -{e}')
        return e
    else:
        return None

# path = open(r'/datadrive/EM_testing/ExtractCustomFields/Saybolt_qnt_quality_documents/Quantity_doc/CHEM-US/FullReport1307400001759-FMT1068-USEBARGCHE-2102-006-5132330-EXXONMOBILCHEMICALCOD.N.Nakata.text')
# read  = path.read()
# ans = FinalQuantityLineItems(read)

# print('Solution',ans)

# def main():
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from connection import connect_db
import pandas as pd
import numpy as np
conn = connect_db()
cursor = conn.cursor()
import datetime
import re
countValue = 0

data1 = pd.read_sql('Select  RowId,NominationDetailId,JobDate,Location,Vendor from InvoiceHeader_External where Status=53', conn)
# print(data1)
for index, rows in data1.iterrows():
    r1 = rows['RowId']
    r2 = r1
    r2 = int(r1)
    n1 = rows['NominationDetailId']
    print('This is mainINvoice of ID', r2, 'Thsi nominationdetailid', n1)
    if np.isnan(n1):
        break
    result = 'Not Matched'
    createdBy = 2
    createdDate = datetime.datetime.now()
    count=0
    def productcostshare(r2,n1,conn):
        '''This function return count and inside this function compare between invoicequantity and nominationquantity for cost share on behalf of productname and vesselname
        r2: Invoice RowId integer type
        n1: NominationDetail NominationDetailId int type'''
        createdBy=2
        createdDate=datetime.datetime.now()
        count=0
        nomination = pd.read_sql(f'Select CostSharePercent,ProductName,VesselName from NominationQuantity_External where NominationDetailId={n1}', conn)
        invoice = pd.read_sql(f'Select CostShare,VesselName,ProductName,InvoiceQantityId from InvoiceQuantity_External where InvoiceId={r1}', conn)
        if(invoice.empty != True and nomination.empty != True):
            for nominationindex, nominationrow in nomination.iterrows():
                nominationcostshare=nominationrow['CostSharePercent']
                invoicecostshare=0
                invoicequantityid=0
                costshareoutcome=0
                for invoiceindex, invoicerow in invoice.iterrows():
                    matchvalue = 89
                    # nominationcostshare = nominationrow['CostSharePercent']
                    invoicecostshare = invoicerow['CostShare']
                    invoicequantityid = invoicerow['InvoiceQantityId']
                    if(nominationrow['VesselName'] != None and invoicerow['VesselName'] != None):
                        nominationrow['VesselName'] = re.sub(r'(\(\W*\w*\))+', '', nominationrow['VesselName'])
                        nominationrow['VesselName'] = re.sub(r'(\s)+', '', nominationrow['VesselName'])
                        invoicerow['VesselName'] = re.sub(r'(\(\W*\w*\))+', '', invoicerow['VesselName'])
                        invoicerow['VesselName'] = re.sub(r'(\s)+', '', invoicerow['VesselName'])
                        # print('nom',row['VesselName'],'--inv->',invoicerow['VesselName'])
                        if(re.search(r'\W', nominationrow['VesselName']) != None):
                            regexsearch = re.search(r'\W', nominationrow['VesselName'])
                            if(regexsearch != None):
                                add = regexsearch.group()
                        if(re.search(r'&\W*\d+', invoicerow['VesselName']) != None):
                            regexsearch = re.search(r'\s*[a-zA-Z]+', invoicerow['VesselName'])
                            if(regexsearch != None):
                                nam = add+regexsearch.group()
                                invoicerow['VesselName'] = re.sub(r'&', nam, invoicerow['VesselName'])
                        if(re.search(r'&', invoicerow['VesselName']) != None):
                            invoicerow['VesselName'] = re.sub(r'&', ',', invoicerow['VesselName'])
                        if(('-' in invoicerow['VesselName']) and ('-' not in nominationrow['VesselName'])):
                            invoicerow['VesselName'] = re.sub('-', '', invoicerow['VesselName'])
                        # print('After Preprocess-----','nom',row['VesselName'],'--inv->',invoicerow['VesselName'])
                        vessel_value = fuzz.token_set_ratio(nominationrow['VesselName'].lower(), invoicerow['VesselName'].lower())
                        if vessel_value > matchvalue:
                            matchvalue = 40
                            if(nominationrow['ProductName'] != None and invoicerow['ProductName'] != None):
                                prod = fuzz.ratio(nominationrow['ProductName'].lower(), invoicerow['ProductName'].lower())
                                # print(prod,row['ProductName'].lower(),'---',invoicerow['ProductName'].lower(),'PROD')
                                if(prod > matchvalue):
                                    if(nominationrow['CostSharePercent'] == None):
                                        nominationrow['CostSharePercent'] = 100
                                    if(nominationrow['CostSharePercent'] == invoicerow['CostShare']):
                                        print(nominationrow['CostSharePercent'], '--------------->',invoicerow['CostShare'], 'for nominationid', n1)
                                        # result='Matched'
                                        
                                        costshareoutcome = 1
                                    else:
                                        print('NOT MATCHED', nominationrow['CostSharePercent'], '--------------->', invoicerow['CostShare'], 'for nominationid', n1)
                                        result = 'Not Matched'
                                        costshareoutcome = 2
                                        count+=1
                                    if(invoicerow['CostShare']==None):
                                        costshareoutcome=23
                                        count+=1
                                        print('cost share not foun[d]')
                                    break
                                else:
                                    # print('ProductNOtMAtched',prod,'nom',nominationrow['CostSharePercent'],'inv',invoicerow['CostShare'])
                                    result = 'Not Matched'
                                    costshareoutcome = 23
                                    count+=1
                        else:
                            # print('VesselName Not Matched')
                            costshareoutcome = 23
                            count+=1
                            result = 'Not Matched'
                            print('Veselnamenot match')
                    else:
                        # invoicecostshare = 5
                        count+=1
                        costshareoutcome = 23
                insert_sql=f"Insert into UtilityProductCostShare_External (CreatedBy,CreatedDate,InvoiceCostSharePercentage,NominationCostSharePercentage,CostShareCheckOutcome,InvoiceId,InvoiceQantityId,ProductName) Values(?,?,?,?,?,?,?,?)"
                values=(int(createdBy),createdDate,invoicecostshare,nominationcostshare,costshareoutcome,int(r2),int(invoicequantityid),invoicerow['ProductName'])
                try:
                    cursor.execute(insert_sql, values)
                    conn.commit()
                    print('Record Inserted')
                except Exception as e:
                    print(type(r2))
                    print(f'Error in Inserting:{str(e)}')
                    # break
                        # nominationcostshare=4
                        # print('vessel',x,'nom ',row['VesselName'].lower(),'-inv-',invoicerow['VesselName'].lower(),'VESSELNAME')
                # else:
                #     break
                        # print(row['VesselName'],'------------>',invoicerow['VesselName'])
            else:
                return(count)
            # print(result, '------------->Result')
        else:
            print('DATAFRAME ARE EMPTY SO CANNOT PROGRESS')
            result = 'Not Found'
            invoicecostshare =0
            costshareoutcome = 23
            count=count+1
            print(result, '-------->Result')
            return(count)
    # productcostshare(r2,n1,conn)
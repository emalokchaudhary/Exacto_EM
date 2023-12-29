# def main():
import re
import datetime
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from connection import connect_db
import pandas as pd
import numpy as np
conn = connect_db()
cursor = conn.cursor()
import warnings
warnings.filterwarnings('ignore')

data1 = pd.read_sql('Select  RowId,NominationDetailId,JobDate,Location,Vendor from InvoiceHeader_External where Status=53', conn)
# print(data1)
for index, rows in data1.iterrows():
    r1 = rows['RowId']
    r2 = r1
    r2 = int(r1)
    n1 = rows['NominationDetailId']
    print('This is mainINvoice of ID', r2, 'NominationDetailId-->', n1)
    if np.isnan(n1):
        break
    count=0
    createdDate=datetime.datetime.now()
    createdBy=2
    def testCostShare(r2,n1,conn):
        '''This function return count and inside this function compare between nominationquality and invoicequality for costshare  percentage on behalf of testname and testmethod
        r2: Invoice RowId int type
        n1: from nomination NominationDetailId
        count: It return count for leakage
        createdDate: today date
        createdBy: intger type'''
        count=0
        createdBy=2
        createdDate=datetime.datetime.now()
        invoice = pd.read_sql(f"Select TestName,TestMethod,CostShare,InvoiceQualityId from InvoiceQuality_External where InvoiceId={r2}", conn)
        nomination = pd.read_sql(f"Select TestName,TestMethod,CostSharePercent from NominationQuality_External where NominationDetailId={n1}", conn)
        result = 'Not Match'
        invoicetestname = invoice['TestName'].to_list()
        # print(len(invoicetestname))
        invoicemethodname = invoice['TestMethod'].to_list()
        invoicecostshare = invoice['CostShare'].to_list()
        invoicequalityid=invoice['InvoiceQualityId'].to_list()
        combine_method_cost_qualityid = list(zip(invoicemethodname, invoicecostshare,invoicequalityid))
        product_dictionary = {}
        for i in range(0, len((invoicetestname))):
            product_dictionary.update({invoicetestname[i]: combine_method_cost_qualityid[i]})
        # print(product_dictionary)
        if(nomination.empty != True):
            try:
                for nominationindex, nominationrow in nomination.iterrows():
                    nominationcostshare=nominationrow['CostSharePercent']
                    lastitem=invoicetestname[-1]
                    for i in range(0,len(invoicetestname)):
                        status=0
                        print(status)
                        invoicequalityid=product_dictionary[invoicetestname[i]][2]
                        invid=invoicequalityid
                        invoicecostshare=product_dictionary[invoicetestname[i]][1]
                        nominationcostshare=nominationrow['CostSharePercent']
                        matchvalue = 80
                        value = fuzz.partial_token_set_ratio(nominationrow['TestName'].lower(), invoicetestname[i])
                        # print('Testnam  ',value,i,'---nom--->',nominationrow['TestName'])
                        matchmethod = 60
                        invoicemethod = product_dictionary[invoicetestname[i]][0]
                        valuemethod = 0
                        if(invoicemethod != None):
                            if('&' in invoicemethod):
                                invoicemethod = re.sub(r'&', ',', invoicemethod)
                            if(',' in invoicemethod):
                                split = invoicemethod.split(',')
                                for one_split in split:
                                    valuemethod = fuzz.partial_ratio(nominationrow['TestMethod'].lower(), invoicemethod.lower())
                                    if(valuemethod > matchmethod):
                                        break
                            else:
                                valuemethod = fuzz.partial_ratio(nominationrow['TestMethod'].lower(), invoicemethod)
                            # print(valuemethod,'method--',invoicemethod,'---nom--->',nominationrow['TestMethod'])
                            print(valuemethod,'prod', 'inv',invoicemethod,i,'-nom-',nominationrow['TestMethod'],nominationrow['TestName'],value)
                            if((valuemethod > matchmethod) or (value > matchvalue)):
                                print(valuemethod,'prod', 'inv',invoicemethod,i,'-nom-',nominationrow['TestMethod'],nominationrow['TestName'],value)
                                invoicecost = product_dictionary[invoicetestname[i]][1]
                                status=1
                                # print('***************',nominationrow['CostSharePercent'],invoicequalityid,n1,'-----',r2)
                                if(nominationrow['CostSharePercent'] == None):
                                    nominationrow['CostSharePercent'] = 100
                                if(invoicecost != None):
                                    if(invoicecost == nominationrow['CostSharePercent']):
                                        # print('Costshare match wwith invoice',invoicecost,'--------->',nominationrow['CostSharePercent'])
                                        costshareoutcome=1
                                        result = 'Match'
                                        count=0
                                    else:
                                        # print('NOT AMAtch',invoicecost,'------->',nominationrow['CostSharePercent'])
                                        costshareoutcome=2
                                        result = 'Not Match'
                                        count=count+1
                                    # invoicetestname.remove(i)
                                else:
                                    # print('invoice  Cost share are none')
                                    result = 'Not Match'
                                    count=count+1
                                    costshareoutcome=23
                                insert_sql = f"Insert into UtilityTestCostShare_External (CreatedBy,CreatedDate,InvoiceCostSharePercentage,NominationCostSharePercentage,CostShareCheckOutcome,InvoiceId,InvoiceQualityId,TestName) Values(?,?,?,?,?,?,?,?)"
                                values = (int(createdBy),createdDate,invoicecostshare,nominationcostshare,costshareoutcome,int(r2),int(invoicequalityid),invoicetestname[i])
                                try:
                                    cursor.execute(insert_sql,values)
                                    conn.commit()
                                    print('Record Inserted')
                                except Exception as e:
                                    print(type(r2))
                                    print(f'Error in Inserting:{str(e)}')
                                invoicetestname.remove(invoicetestname[i])
                                break                            
                            else:
                                # invoicecostshare=2
                                costshareoutcome=23
                        else:
                            # count=count+1
                            costshareoutcome=23
                        if(len(invoicetestname)-1==i):
                            count=count+1
                            testname=invoicetestname[i]
                            insert_sql = f"Insert into UtilityTestCostShare_External (CreatedBy,CreatedDate,NominationCostSharePercentage,CostShareCheckOutcome,InvoiceId,InvoiceQualityId,TestName) Values(?,?,?,?,?,?,?)"
                            values = (int(createdBy),createdDate,nominationcostshare,costshareoutcome,int(r2),int(invoicequalityid),testname)
                            try:
                                cursor.execute(insert_sql,values)
                                conn.commit()
                                print('Record Inserted')
                            except Exception as e:
                                print(type(r2))
                                print(f'Error in Inserting:{str(e)}')
                            invoicetestname.remove(invoicetestname[i])       
            except:
                result = 'Not Found'
                print('nomination have extra or none element')
                count=count+1
                # return(count,'notfound')
        # return(count,result, '----------------> Result')
        return(count)
    # d=testCostShare(r2,n1,count,createdDate,createdBy,conn)
    # print(d,'---------',r2,'------n1-',n1)

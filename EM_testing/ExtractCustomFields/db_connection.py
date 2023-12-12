import json

import pprint, traceback

import os

from collections import OrderedDict

import pyodbc

DATABASE_NAME = os.environ.get('DB_NAME','sqldb-pay-toscana-db-dev')
DATABASE_USER = os.environ.get('DB_USER','sqldb-exacto-main')
DATABASE_PASSWORD = os.environ.get('DB_PASSWORD','7Odo0aS5e!*3!f2P$Kno7Hq#c')
DATABASE_HOST = os.environ.get('DB_HOST','sqldb-pay-toscana-dbsrv.database.windows.net')
DATABASE_PORT = os.environ.get('DB_PORT','1433')



def connect_db():
    try:

        mydb = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};' +

                              'Server={};'.format(DATABASE_HOST) +

                              'port={};'.format(DATABASE_PORT) +

                              'Database={};'.format(DATABASE_NAME) +

                              'uid={};'.format(DATABASE_USER) +

                              'pwd={};'.format(DATABASE_PASSWORD) +

                              'autocommit=True;'

                              )
        return mydb
    except:

        print(traceback.print_exc())




def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"

    columns = [col[0]

               for col in cursor.description]

    return [

        OrderedDict(zip(columns, row))

        for row in cursor.fetchall()

        ]


def execute_non_query(query, mydb):
    try:
        mycursor = mydb.cursor()
        mycursor.execute(query)
        mycursor.commit()
        return 'success'
    except:
        print("Error in db")
        traceback.print_exc()


def execute_query(mydb,query):
    myresult = []
    #mydb = connect_db()
    mycursor = mydb.cursor()

    mycursor.execute(query)

    myresult = dictfetchall(mycursor)

    return myresult





def execute_query_v2(mydb, query):
    try:
        cursor=mydb.cursor()
        cursor.execute(query)
        db_out = dictfetchall(cursor)
        return db_out
    except:

        traceback.print_exc()
        return db_out
def fetch_client_email_data_without_Userid(mydb):
    # user_id = ""
    config_list = []
    out_json = {}
    # query = "SELECT * from mail_configuration where userid = '" + user_id + "'";
    query = "SELECT f.config_name, f.id as config_id, m.* from mail_configuration m left join form_fields_master as f on  \
            m.user_id = f.user_id order by config_id desc";
    out = execute_query_v2(mydb,query)
    if len(out)==0:
        out_json = {"success" : "0", "config_list" : "", "user_id" : "","message" : "Could not fetch Client mail Configuration !!", \
                "company_code": "", "mail_id" : "", "subject": "", "from_email" : "", "smtp" : "", "username" : "", "password" : "", \
                "port" : ""}
        return out_json
    else:
        return out



def get_fields_Names(dbList):
        standard_fields = ""
        standard_custom_fields = ""
        table_fields = ""
        table_custom_fields = ""
        for field_map in dbList:
            if(field_map["field_type"]=='S'):
                standard_fields = standard_fields + "," +  field_map["field_key"]
            if(field_map["field_type"]=='SC'):
                standard_custom_fields = standard_custom_fields + "," +  field_map["mapped_field"]
            if(field_map["field_type"]=='T'):
                table_fields = table_fields + "," +  field_map["field_key"]
            if(field_map["field_type"]=='TC'):
                table_custom_fields = table_custom_fields + "," +  field_map["mapped_field"]

        refine_list= { 'standard_list':standard_fields[1:],'standard_custom_list':standard_custom_fields[1:],'table_list':table_fields[1:],'table_custom_list':table_custom_fields[1:] }
         
        return refine_list
def get_standard_fields_mapping(user_id,ftype,config_uuid,company_code):
        
        query = "SELECT fields_name,field_key,field_type,field_sequence,mapped_field from form_fields_mapping WITH (NOLOCK)  where field_type = '" + ftype + "' and company_code = '" + str(company_code) + "' and config_uuid =  '" + str(config_uuid) + "' order by field_sequence"
         
        mydb = connect_db()
        result = execute_query(mydb,query) 
        output = get_fields_Names(result) 
        return output

def mapping_fields(user_id,field_type,config_id,company_code):
        fields_name = ""

        results = get_standard_fields_mapping(user_id,field_type,config_id,company_code)
        if(field_type == "S"):
            fields_name = results["standard_list"]
        elif(field_type == "SC"):
            fields_name = results["standard_custom_list"]
        elif(field_type == "T"):
            fields_name = results["table_list"]
        elif(field_type == "TC"):
            fields_name =  results["table_custom_list"]

        return fields_name

def get_standard_data(uuid,rec_id,user_id,company_code):

        #config_id = self.get_config_uuid(rec_id)
        config_id = rec_id 
        
         
        fields_name = mapping_fields(user_id,"S",config_id,company_code)
        custom_fields = mapping_fields(user_id,"SC",config_id,company_code) 
         
        if(custom_fields != ""):
            fields_name = fields_name + "," + custom_fields
         
        
        fields_conf_score = fields_name.replace(",",",conf_")
        fields_conf_score = fields_conf_score.replace("file_name","conf_file_name")
        query = "SELECT original_file_name,user_id,company_code,config_uuid,predicted_uuid," + fields_name + ", " + fields_conf_score + "  from predicted_data WITH (NOLOCK) where predicted_uuid = '" + uuid + "'"; 

        mydb = connect_db()
        result = execute_query(mydb,query)
         
        return result
    
def get_table_data(uuid,rec_id,user_id,company_code):
        #config_id = self.get_config_uuid(rec_id)
        config_id = rec_id
        
        
        fields_name = mapping_fields(user_id,"T",config_id,company_code)
        custom_fields = mapping_fields(user_id,"TC",config_id,company_code)
         
        if mapping_fields(user_id,"TC",config_id,company_code) != "":
            fields_name = fields_name + ","+ mapping_fields(user_id,"TC",config_id,company_code)
        else:
            fields_name = fields_name 
        
        fields_name = fields_name.strip(",")

        if(fields_name != ""):
            query = "SELECT " + fields_name + "  from predicted_table_data WITH (NOLOCK) where predicted_uuid = '" + uuid + "'"; 

            mydb = connect_db()
            result = execute_query(mydb,query)
            return result
        else:
            return ''
def get_display_list(dbList):
        standard_list=[]
        standard_custom_list=[]
        table_list=[]
        table_custom_list=[]
        for field_map in dbList:
            if(field_map["field_type"]=='S'):
                standard_list.append(field_map)
            if(field_map["field_type"]=='SC'):
                standard_custom_list.append(field_map)
            if(field_map["field_type"]=='T'):
                table_list.append(field_map)
            if(field_map["field_type"]=='TC'):
                table_custom_list.append(field_map)
        refine_list= { 'standard_list':standard_list,'standard_custom_list':standard_custom_list,'table_list':table_list,'table_custom_list':table_custom_list  }
        return refine_list


def get_custom_fields_by_uuid(config_uuid,user_id,company_code):
    query = "SELECT fields_name,field_key,field_type,field_sequence,mapped_field from form_fields_mapping WITH (NOLOCK) where config_uuid = '" + str(config_uuid) + "' and company_code = '"+ company_code+"' order by field_sequence";
    mydb = connect_db()
    result = execute_query(mydb,query)
    output = get_display_list(result)
    return output






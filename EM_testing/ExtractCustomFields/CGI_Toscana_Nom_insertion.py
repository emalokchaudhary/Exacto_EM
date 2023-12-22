from ExtractCustomFields.db_connection import connect_db
conn = connect_db()
cursor = conn.cursor()



def toscana_insertion(uuid):
    a = 'select nom_hd_uuid from exacto_nom_hd order by created_datetime desc limit 1 '
    cursor.exceute(a)
    p=cursor.fetchone()
    stored_proc = "EXEC HCL_Nomination_Data_Trans"
    params = p[0]
    cursor.exceute(stored_proc,params)





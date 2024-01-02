
BEGIN TRY
BEGIN TRANSACTION
DELETE from exacto_qlt_li where extraction_datetime < GETDATE();
DELETE from exacto_qlt_hd where extraction_datetime < GETDATE();
DELETE from exacto_qnt_hd where extraction_datetime < GETDATE();
COMMIT
PRINT 'Successfully Deleted data from exacto Qunatity and Quality tables till date'
END TRY
BEGIN CATCH 
ROLLBACK
PRINT ERROR_MESSAGE();
END CATCH

BEGIN TRY
BEGIN TRANSACTION
DELETE from exacto_inv_qnt_li where extraction_datetime < GETDATE();
DELETE from exacto_inv_qlt_li where created_datetime < GETDATE();
DELETE from exacto_inv_hd where extraction_datetime < GETDATE();
COMMIT
PRINT 'Successfully Deleted data from exacto Invoice tables till date'
END TRY
BEGIN CATCH 
ROLLBACK
PRINT ERROR_MESSAGE();
END CATCH

BEGIN TRY
BEGIN TRANSACTION
DELETE from exacto_nom_ql_li where extraction_datetime < GETDATE();
DELETE from exacto_nom_li where extraction_datetime < GETDATE();
DELETE from exacto_nom_hd where extraction_datetime < GETDATE();
COMMIT
PRINT 'Successfully Deleted data from exacto nomination tables till date'
END TRY
BEGIN CATCH 
ROLLBACK
PRINT ERROR_MESSAGE();
END CATCH



BEGIN TRY
BEGIN TRANSACTION

DELETE FROM exacto_doc_process_log 

COMMIT
PRINT 'Successfully Deleted data from exacto_doc_process_log tables till date'
END TRY
BEGIN CATCH 
ROLLBACK
PRINT ERROR_MESSAGE();
END CATCH
/****** Object:  StoredProcedure [dbo].[HCL_Inspection_Data_Quality_Trans]    Script Date: 12/27/2023 11:36:21 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:      <Author, , Name>
-- Create Date: <Create Date, , >
-- Description: <Description, , >
-- =============================================

ALTER PROCEDURE [dbo].[HCL_Inspection_Data_Quality_Trans]
											(
    -- Add the parameters for the stored procedure here
    @Docuuid nvarchar(100),
	@NominationUUID nvarchar(20),
	@InvoiceUUID nvarchar(20)
)
AS
BEGIN
	BEGIN TRY
	BEGIN TRANSACTION
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON
	SET ARITHABORT ON
	--Declare @TripNumber varchar(50);

	-- Insert data into InspectionQuality_External table

	--PRINT 'Inserting data into InspectionQuality_External table'

	/*select @TripNumber = TripNumber from exacto_doc_process_log  e1 , exacto_doc_process_log e2
	Inner join exacto_nom_hd enh on enh.doc_uuid = e2.doc_uuid
	where e1.invno = e2.invno AND e1.VendorName = e2.VendorName And
	e1.doc_uuid = @Docuuid AND e2.FileType = 'Nomination'
	*/
	INSERT INTO [dbo].[InspectionQuality_External]
           ([TestMethod],[CreatedBy],[CreatedDate],[ModifiedBy],[ModifiedDate]
           ,[ProductName],[TestName],[VesselName],[LabTestId],[NominationQualityId]
           ,[ProductId],[InspectionId])
	select eql.method,2,GETDATE(),NULL,NULL,
			eqh.ProductName,eql.component,eqh.VesselName,ltm.RowId,nqe.NominationQualityId,
			pcm.RowId,ihe.InspectionId
	from exacto_qlt_hd eqh 
	LEFT JOIN exacto_qlt_li eql with (nolock) on eqh.qlt_hd_uuid = eql.qlt_hd_uuid
	LEFT JOIN InspectionHeader_External ihe with (nolock) on eqh.qlt_hd_uuid = ihe.InpsectionUUID
	--INNER JOIN InspectionQuantity_External iqe with (nolock) on ihe.InspectionId = iqe.InspectionId
	LEFT JOIN LabTestMaster ltm with (nolock) on eql.method = ltm.TestMethod
	LEFT JOIN ProductCatalogMaster pcm with (nolock) on eqh.ProductName = pcm.description
	LEFT JOIN NominationHeader_External nhe with (nolock) on  NominationUUID = @NominationUUID
	INNER JOIN NominationDetails_External nde with (nolock) on nhe.NominationId = nde.NominationId
	INNER JOIN NominationQuality_External nqe with (nolock) on nde.NominationDetailId = nqe.NominationDetailId
	where eqh.doc_uuid = @Docuuid AND CHARINDEX(nde.Activity,eqh.ActivityType) > 0 
	--and nqe.TestName = eql.component and CHARINDEX(eql.method,nqe.TestMethod)>0;

	--PRINT 'Done Inserting data into InspectionQuality_External table'

COMMIT
print 'Success ' + @Docuuid;
END TRY
BEGIN CATCH
    ROLLBACK;
    DECLARE @ErrorMessage NVARCHAR(1000) = ERROR_MESSAGE();
    INSERT INTO Exception_table values (@Docuuid, GETDATE(), @ErrorMessage, 'InvoiceQuality');
	print 'Fail ' + @Docuuid; 
END CATCH

	

END

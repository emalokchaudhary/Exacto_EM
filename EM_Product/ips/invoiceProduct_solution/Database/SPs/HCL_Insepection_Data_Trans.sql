/****** Object:  StoredProcedure [dbo].[HCL_Insepection_Data_Trans]    Script Date: 12/27/2023 11:25:32 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- =============================================
-- Author:      <Author, , Name>
-- Create Date: <Create Date, , >
-- Description: <Description, , >
-- =============================================

ALTER PROCEDURE [dbo].[HCL_Insepection_Data_Trans]
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
	Declare @TripNumber varchar(50);
	--Inserting data into InspectionHeader_External
	
	--print'-Inserting data into InspectionHeader_External'

	/*select @TripNumber = TripNumber from exacto_doc_process_log  e1 , exacto_doc_process_log e2
	Inner join exacto_nom_hd enh on enh.doc_uuid = e2.doc_uuid
	where e1.invno = e2.invno AND e1.VendorName = e2.VendorName And
	e1.doc_uuid = @Docuuid AND e2.FileType = 'Nomination'
   */
	INSERT INTO [dbo].[InspectionHeader_External]
           ([CreatedBy],[CreatedDate],[Location],[ModifiedBy],[ModifiedDate],[NominationNumber]
           ,[TripNumber],[Vendor],[VendorReferenceNumber],[InvoiceId],[LocationId],[VendorId], [InpsectionUUID])
	
	select 2,GETDATE(),eqh.JobLocation,NULL,NULL,nhe.NominationNumber,
	nhe.TripNumber,VendorName,VendorInternalReferencenumber,ihe.RowID,lm.RowId,vm.RowId,qnt_hd_uuid
	from exacto_qnt_hd eqh
	LEFT JOIN NominationHeader_External nhe with (nolock) on  NominationUUID = @NominationUUID
	--INNER JOIN exacto_nom_hd enh with (nolock) on eqh.doc_uuid = enh.doc_uuid
	INNER JOIN InvoiceHeader_External ihe with (nolock) on ihe.InvoiceUUID = @InvoiceUUID
	--INNER JOIN InvoiceHeader_External ihe with (nolock) on enh.TripNumber = ihe.TripNumber
	LEFT JOIN LocationMaster lm with (nolock) on eqh.JobLocation = lm.description
	LEFT JOIN VendorMaster vm with (nolock) on eqh.VendorName = vm.description
	where eqh.doc_uuid = @Docuuid 
--print' DONE Inserting data into InspectionHeader_External'

	--Inserting values into InspectionQuantity_External
	--print 'Inserting values into InspectionQuantity_External'
	INSERT INTO [dbo].[InspectionQuantity_External]
           ([CreatedBy],[CreatedDate],[ModifiedBy],[ModifiedDate],[ProductName]
           ,[VesselName],[NominationQuantityId],[ProductId],[InspectionId])
	select 2,GETDATE(),NULL,NULL,eqh.ProductName,
			eqh.VesselName,nqe.NominationQuantityId,pcm.RowId,ihe.InspectionId
	from exacto_qnt_hd eqh
	--INNER JOIN exacto_nom_hd enh with (nolock) on eqh.doc_uuid = enh.doc_uuid
	LEFT JOIN NominationHeader_External nhe with (nolock) on NominationUUID = @NominationUUID
	INNER JOIN NominationDetails_External  nde with (nolock) on nde.NominationId = nhe.NominationId
	INNER JOIN NominationQuantity_External nqe with (nolock) on nde.NominationDetailId = nqe.NominationDetailId
	INNER JOIN InspectionHeader_External ihe with (nolock) on eqh.qnt_hd_uuid = ihe.InpsectionUUID
 	--INNER JOIN NominationQuantity_External nqe with (nolock) on eqh.NominationKey = nqe.NominationKey
	--INNER JOIN InspectionHeader_External ihe with (nolock) on eqh.TripNumber = ihe.TripNumber
	LEFT JOIN ProductCatalogMaster pcm with (nolock) on eqh.ProductName = pcm.description
	where eqh.doc_uuid = @Docuuid and CHARINDEX(nde.Activity,eqh.ActivityType) > 0

	--print 'Done Inserting values into InspectionQuantity_External'



	--Inserting values into InspectionQuantityUoM_External

	--print'Inserting values into InspectionQuantityUoM_External'

	INSERT INTO [dbo].[InspectionQuantityUoM_External]
           ([CreatedBy],[CreatedDate],[InspectedQuantity],[ModifiedBy]
           ,[ModifiedDate],[UoM],[InspectionQuantityId],[UoMId])
	select 2,GETDATE(),TRY_CONVERT(decimal(12,2),REPLACE(NominatedQuantity, ',', '')),NULL,
			NULL,eqh.UnitOfMeasure,iqe.InspectionQuantityId,um.RowId
	from exacto_qnt_hd eqh 
	--INNER JOIN exacto_nom_hd enh with (nolock) on eqh.doc_uuid = enh.doc_uuid
	LEFT JOIN NominationHeader_External nhe with (nolock) on NominationUUID = @NominationUUID
	INNER JOIN InspectionHeader_External ihe with (nolock) on  eqh.qnt_hd_uuid = ihe.InpsectionUUID
	INNER JOIN InspectionQuantity_External iqe with (nolock) on ihe.InspectionId = iqe.InspectionId
	LEFT JOIN UoMMaster um with (nolock) on eqh.UnitOfMeasure = um.description
	--INNER JOIN InspectionHeader_External ihe with (nolock) on eqh.TripNumber = ihe.TripNumber
	where eqh.doc_uuid = @Docuuid 

	--print 'Done Inserting values into InspectionQuantityUoM_External'
COMMIT
print 'Success ' + @Docuuid;
END TRY
BEGIN CATCH
    ROLLBACK;
    DECLARE @ErrorMessage NVARCHAR(1000) = ERROR_MESSAGE();
    INSERT INTO Exception_table values (@Docuuid, GETDATE(), @ErrorMessage, 'InvoiceQuantity');
	print 'Fail ' + @Docuuid;  
END CATCH



END

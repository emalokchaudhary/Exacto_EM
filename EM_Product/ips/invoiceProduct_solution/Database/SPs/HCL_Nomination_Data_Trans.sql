/****** Object:  StoredProcedure [dbo].[HCL_Nomination_Data_Trans]    Script Date: 12/27/2023 11:22:44 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO


-- =============================================
-- Author:      <Author, , Name>
-- Create Date: <Create Date, , >
-- Description: <Description, , >
-- =============================================

ALTER PROCEDURE [dbo].[HCL_Nomination_Data_Trans]
											(
    -- Add the parameters for the stored procedure here
    @DocUUID nvarchar(100)
	--,@Result nvarchar(100) output
	
)

AS
BEGIN
	BEGIN TRY
	BEGIN TRANSACTION
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON
	SET ARITHABORT ON
	

	-- Inserting the data into NominationHeader_External table

	Insert into NominationHeader_External 
		(CreatedBy, CreatedDate,NominationNumber, Region, TripNumber, RegionId, NominationUUID) 
    SELECT 2,GETDATE(), NominationNumber, Region, TripNumber,rm.RowId, nom_hd_uuid
	FROM exacto_nom_hd enh with (nolock)
	LEFT JOIN RegionMaster rm with (nolock) on enh.Region = rm.description
	WHERE doc_uuid = @DocUUID;

		--PRINT '---1---'
	
    -- Inserting the data into NominationDetails_External table

	Insert into NominationDetails_External 
		(Activity,BillTo, CreatedBy, CreatedDate, ETA, [Location], Vendor, NominationId,VendorId,ActivityId,LocationId)
	Select ActivityType,EmAffiliates,2, GETDATE(), JobDate, JobLocation, VendorName, nhe.NominationId,vm.RowId,am.RowId,lm.RowId
	from exacto_nom_li enl with (nolock)
	LEFT JOIN VendorMaster vm with (nolock) on enl.VendorName = vm.description
	LEFT JOIN ActivityMaster am with (nolock) on enl.ActivityType = am.description 
	LEFT JOIN LocationMaster lm with (nolock) on enl.JobLocation = lm.description 
	INNER JOIN exacto_nom_hd enh with (nolock) on enl.nom_hd_uuid = enh.nom_hd_uuid
	INNER JOIN NominationHeader_External nhe with (nolock) on enh.nom_hd_uuid = nhe.NominationUUID --nhe.NominationNumber = enh.NominationNumber
	where enh.doc_uuid = @DocUUID;

		--PRINT '---2---'

    -- Inserting the data into NominationQuantity_External table

    insert into NominationQuantity_External
		(CostSharePercent,CreatedBy, CreatedDate,  NominationKey, ProductName,NominatedQuanity,UoM, VesselName, NominationDetailId, IsActive)
	Select 100.00, 2, GETDATE(), NominationKey, ProductName,NominatedQuantity,UnitOfMeasure, VesselName,nde.NominationDetailId, 1
	from exacto_nom_li enl with (nolock)
	INNER JOIN exacto_nom_hd enh with (nolock) on enl.nom_hd_uuid = enh.nom_hd_uuid
	INNER JOIN NominationHeader_External nhe with (nolock) on enh.nom_hd_uuid = nhe.NominationUUID --nhe.NominationNumber = enh.NominationNumber
	INNER JOIN NominationDetails_External nde with (nolock) on nde.NominationId = nhe.NominationId AND CHARINDEX(nde.Activity,enl.ActivityType) > 0
	where enh.doc_uuid = @DocUUID; --and VendorName = nde.Vendor
	
		
--PRINT '---3---'
			
	-- Inserting the data into NominationQuality_External table
			
	insert into NominationQuality_External
	(Comments, CostSharePercent,CreatedBy, CreatedDate, ModifiedBy, ModifiedDate, 
		SampleLocation, SetDescription, SetNumber,TestMethod, TestName, NominationDetailId, IsActive)
	Select Comments,100.00, 2, GETDATE(), 00, GETDATE(), 
		SampleLocation, SetDescription, cast(SetNo as int), TestCode, TestName,nde.NominationDetailId, 1
	from exacto_nom_ql_li enql with (nolock)
	INNER JOIN exacto_nom_hd enh with (nolock) on enql.nom_hd_uuid = enh.nom_hd_uuid
	INNER JOIN NominationHeader_External  nhe with (nolock) on enh.nom_hd_uuid = nhe.NominationUUID --nhe.NominationNumber = enh.NominationNumber
	INNER JOIN NominationDetails_External  nde with (nolock) on nde.NominationId = nhe.NominationId
	where enh.doc_uuid = @DocUUID --and VendorName = nde.Vendor


--PRINT '---4---'
COMMIT
print 'Success ' + @DocUUID;
--set @Result = 'Success ' + @DocUUID;
END TRY
BEGIN CATCH
    ROLLBACK;
    DECLARE @ErrorMessage NVARCHAR(1000) = ERROR_MESSAGE();
    INSERT INTO Exception_table values (@DocUUID, GETDATE(), @ErrorMessage, 'Nomination');
	print 'Fail ' + @DocUUID; 
	--set @Result = 'Fail ' + @DocUUID;
END CATCH
--RETURN @Result

END
 

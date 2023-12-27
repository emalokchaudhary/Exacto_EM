/****** Object:  StoredProcedure [dbo].[HCL_Invoice_Data_Trans]    Script Date: 12/27/2023 11:24:37 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO


-- =============================================
-- Author:      <Author, , Name>
-- Create Date: <Create Date, , >
-- Description: <Description, , >
-- =============================================

ALTER PROCEDURE [dbo].[HCL_Invoice_Data_Trans]
											(
    -- Add the parameters for the stored procedure here
    @DocUUID nvarchar(100),
	@NominationUUID nvarchar(20)
)

AS
BEGIN
	BEGIN TRANSACTION
	BEGIN TRY
	
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON
	SET ARITHABORT ON
	

	-- Inserting the data into InvoiceHeader_External table
	--Print 'Going to insert data in InvoiceHeader_External'
	Declare @WIName varchar(255)
	Declare @DocRowId int

	SELECT inv_hd_uuid,ActivityType,Currency,TRY_CONVERT(tinyint,substring(DiscountPercent,1,LEN(DiscountPercent)-1)) as DiscountPercent,
			InvoiceNumber,JobDate,JobLocation,
			TRY_CONVERT(decimal(12,2),REPLACE(TotalDueAmount, ',', '')) as TotalAmount,TRY_CONVERT(decimal(12,2),REPLACE(TotalAmountAfterTax, ',', '')) as TotalAmountAfterTax,
			TRY_CONVERT(decimal(12,2),REPLACE(TotalDueAmount, ',', '')) as TotalDueAmount,TRY_CONVERT(decimal(10,2),REPLACE(TotalTaxAmount, ',', '')) as TotalTaxAmount,VendorName,
			VendorInternalReferencenumber,NominationDetailId,nhe.NominationNumber,eih.TripNumber as Tripnumber,EmAffiliates into #Temptable1
	FROM exacto_inv_hd eih with (nolock), NominationHeader_External nhe with (nolock) 
	INNER JOIN NominationDetails_External nde with (nolock) on nde.NominationId = nhe.NominationId
	WHERE eih.doc_uuid = @DocUUID AND CHARINDEX(nde.Activity,eih.ActivityType) > 0 and nhe.NominationUUID = @NominationUUID

	INSERT INTO [dbo].[InvoiceHeader_External]
           ([Activity],[AssignDate],[AssignTo],[BillTo],[CreatedBy],[CreatedDate],[currQueue],[Currency],[DiscountPercent]
           ,[TypeOfInspection],[InvoiceNumber],[JobDate],[LobId],[Location],[LockByUserName],[LockedBy],[ModifiedBy]
           ,[ModifiedDate],[Status],[TotalAmount],[TotalAmountAfterTax],[TotalDueAmount],[TotalTaxAmount],[Vendor]
           ,[VendorReferenceNumber],[WINumber],[AffiliateId],[CurrencyId],[StatusID],[NominationDetailId],[LeakageCount]
           ,[PotentialLeakageValue],[NominationNumber],[TripNumber],[ActivityId],[TypeOfInspectionId],[LocationId],[VendorId],[InvoiceUUID])
  SELECT ActivityType,NULL,NULL,afm.RowId,2,GETDATE(),'Ready To Validate',Currency,DiscountPercent,
			NULL,InvoiceNumber,JobDate,45,JobLocation,'-',0,NULL,
			NULL,53,TotalAmount,TotalAmountAfterTax,
			TotalDueAmount,TotalTaxAmount,VendorName,
			VendorInternalReferencenumber,((SELECT CodePrefix  FROM TOSCANA3_LobMaster WHERE LobID=45) 
		+ substring('00000000', 1, 8 - len(NEXT VALUE FOR seq_ExxonMobil))
		+ convert(varchar, NEXT VALUE FOR seq_ExxonMobil))
			,afm.RowId,cm.RowId,53,NominationDetailId,NULL,NULL,
		NominationNumber,TripNumber,am.RowId,NULL,lm.RowId,vm.RowId,inv_hd_uuid
	FROM #Temptable1 t1 with (nolock)
	LEFT JOIN AffiliateMaster afm with (nolock) on t1.EmAffiliates = afm.description
	LEFT JOIN CurrencyMaster cm with (nolock) on t1.Currency = cm.CurrencyCode
	LEFT JOIN ActivityMaster am with (nolock) on CHARINDEX(am.description,t1.ActivityType) > 0 
	LEFT JOIN LocationMaster lm with (nolock) on t1.JobLocation = lm.description
	LEFT JOIN VendorMaster vm with (nolock) on t1.VendorName = vm.description

--PRINT 'Data inserted in table InvoiceHeader_External'

	
    -- Inserting the data into InvoiceQuantity_External table
	--Print 'Going to insert data in InvoiceQuantity_External'
		Select 	TRY_CONVERT(decimal(12,2),REPLACE(AmountBeforeTax, ',', '')) as AmountBeforeTax,
			TRY_CONVERT(tinyint,substring(eih.DiscountPercent,1,LEN(eih.DiscountPercent)-1)) as DiscountPercent,
			eih.NominationKey as NominationKey,eih.ProductName as productName,
			TRY_CONVERT(decimal, Tax_Percent) as Tax_Percent,
			UnitOfMeasure,eih.VesselName as VesselName,
			nqe.NominationQuantityId as NominationQuantityId, nhe.RegionId as RegionId,inv_hd_UUID,vendorName,joblocation,eih.invoicenumber as invoicenumber 
			into #Temptable2
	from exacto_inv_hd eih with (nolock),NominationHeader_External nhe with (nolock) 
	INNER JOIN NominationDetails_External nde with (nolock) on nde.NominationId = nhe.NominationId
	INNER JOIN NominationQuantity_External nqe with (nolock) on nqe.NominationDetailId = nde.NominationDetailId
	where eih.doc_uuid = @DocUUID AND CHARINDEX(nde.Activity,eih.ActivityType) > 0 and nhe.NominationUUID = @NominationUUID

	INSERT INTO [dbo].[InvoiceQuantity_External]
           ([AfterCostShare],[AmountBeforeTax],[CostShare],[CreatedBy],[CreatedDate],[Description]
           ,[DiscountPercent],[ModifiedBy],[ModifiedDate],[NominationKey],[ProductName],[QuantityValue]
           ,[TaxDescription],[TaxPercent],[UnitPrice],[UoM],[VesselName],[GICQuantityId]
           ,[InvoiceId],[NominationQuantityId],[ProductId],[UoMId],[isActive])
	Select TRY_CONVERT(decimal(10,2),REPLACE(eiql.sharecharge, ',', '')),
			AmountBeforeTax,
			TRY_CONVERT(decimal(5,2),REPLACE(eiql.Share, ',', '')),
			2,GETDATE(),eiql.Description,
			t.DiscountPercent,NULL,NULL,NominationKey,ProductName,
			TRY_CONVERT(decimal(10,2),REPLACE(eiql.QuantityValue,',', '')),
			eiql.Tax_Description,Tax_Percent,
			TRY_CONVERT(decimal(10,2),REPLACE(eiql.Price, ',', '')),
			UnitOfMeasure,t.VesselName,Gqe.GICQuantityId,
			ie.RowID,t.NominationQuantityId,pcm.RowId,uom.RowId,1
			from #Temptable2 t 
    INNER JOIN Exacto_inv_qnt_li eiql with(nolock) on t.inv_hd_UUID = eiql.inv_hd_uuid
	INNER JOIN InvoiceHeader_External ie with(nolock) on t.invoicenumber = ie.InvoiceNumber
	LEFT JOIN ObjectMaster om with(nolock) on eiql.Category = om.description
	LEFT JOIN ObjectSubCategory osc with(nolock) on eiql.SubCategory = osc.description
	LEFT JOIN ProductCatalogMaster pcm with (nolock) on t.ProductName = pcm.description
	LEFT JOIN UoMMaster uom with (nolock) on t.UnitOfMeasure = pcm.description
	LEFT JOIN VendorMaster vm with (nolock) on t.VendorName = vm.description
	LEFT JOIN LocationMaster lm with (nolock) on t.JobLocation = lm.description
	LEFT JOIN GICHeader_External ghe with (nolock) on vm.RowId = ghe.VendorId AND lm.RowId = ghe.LocationId AND t.RegionId = ghe.RegionId  
	LEFT JOIN GICQuantity_External gqe with (nolock) on ghe.GICId = gqe.GICId --AND gqe.ProductTypeId = pcm.GICGradeTypeId 
	--AND gqe.ObjectId = om.RowId AND gqe.ObjectSubCategoryId = coalesce(osc.RowId,om.RowId) OR gqe.UoMId = uom.RowId
		--PRINT 'Data inserted in table InvoiceQuantity_External'

   
		-- Inserting the data into InvoiceQuality_External table
		--Print 'Going to insert data in InvoiceQuality_External'	
	Select 	TRY_CONVERT(decimal(12,2),REPLACE(AmountBeforeTax, ',', '')) as AmountBeforeTax,
			TRY_CONVERT(tinyint,substring(eih.DiscountPercent,1,LEN(eih.DiscountPercent)-1)) as DiscountPercent,
			eih.NominationKey as NominationKey,eih.ProductName as productName,
			TRY_CONVERT(decimal, Tax_Percent) as Tax_Percent,
			UnitOfMeasure,eih.VesselName as VesselName,
			nqe.NominationQualityId as NominationQualityId, nhe.RegionId as RegionId,inv_hd_UUID,vendorName,joblocation,
			eih.invoicenumber as invoicenumber,nqe.TestName as Testname, nqe.Testmethod as Testmethod
			into #Temptable3
	from exacto_inv_hd eih with (nolock),NominationHeader_External nhe with (nolock) 
	INNER JOIN NominationDetails_External nde with (nolock) on nde.NominationId = nhe.NominationId
	INNER JOIN NominationQuality_External nqe with (nolock) on nqe.NominationDetailId = nde.NominationDetailId
	where eih.doc_uuid = @DocUUID and CHARINDEX(nde.Activity,eih.ActivityType) > 0 and nhe.NominationUUID = @NominationUUID

	INSERT INTO [dbo].[InvoiceQuality_External]
           ([AfterCostShare],[AmountBeforeTax],[CostShare],[CreatedBy],[CreatedDate],[DiscountPercent]
           ,[ModifiedBy],[ModifiedDate],[NominationKey],[ProductName],[QuantityValue],[TaxDescription],[TaxPercent]
           ,[TestMethod],[TestName],[UnitPrice],[UoM],[VesselName],[GICQualityId],[InvoiceId]
           ,[LabTestId],[NominationQualityId],[ProductId],[UoMId],[isActive])
	Select TRY_CONVERT(decimal(10,2),REPLACE(eiql.sharecharge, ',', '')),
			AmountBeforeTax,
			TRY_CONVERT(decimal(5,2),REPLACE(eiql.Share, ',', '')),
			2,GETDATE(),t.DiscountPercent,NULL,NULL,NominationKey,ProductName,
			TRY_CONVERT(decimal(10,2),REPLACE(eiql.QuantityValue,',', '')),
			eiql.Tax_Description,Tax_Percent,eiql.TestMethod,eiql.TestName,
			TRY_CONVERT(decimal(10,2),REPLACE(eiql.Price, ',', '')),
			UnitOfMeasure,t.VesselName,Gqe.GICQualityId,
			ie.RowID,ltm.RowId,t.NominationQualityId,pcm.RowId,uom.RowId,1
			from #Temptable3 t 
    INNER JOIN Exacto_inv_qlt_li eiql with(nolock) on t.inv_hd_UUID = eiql.inv_hd_uuid
	INNER JOIN InvoiceHeader_External ie with(nolock) on t.invoicenumber = ie.InvoiceNumber
	LEFT JOIN ProductCatalogMaster pcm with (nolock) on t.ProductName = pcm.description
	LEFT JOIN UoMMaster uom with (nolock) on t.UnitOfMeasure = pcm.description
	LEFT JOIN VendorMaster vm with (nolock) on t.VendorName = vm.description
	LEFT JOIN LocationMaster lm with (nolock) on t.JobLocation = lm.description
	LEFT JOIN LabTestMaster ltm with (nolock) on eiql.TestMethod = ltm.TestMethod
	LEFT JOIN GICHeader_External ghe with (nolock) on vm.RowId = ghe.VendorId AND lm.RowId = ghe.LocationId AND t.RegionId = ghe.RegionId  
	LEFT JOIN GICQuality_External gqe with (nolock) on ghe.GICId = gqe.GICId
	where t.TestName = eiql.TestName and t.Testmethod = eiql.TestMethod
	-- AND eih.ProductName = nqe.ProductName AND eiql.TestName = nqe.TestName AND
	--eiql.TestMethod = nqe.TestMethod;
	
--PRINT 'Data inserted in table InvoiceQuality_External'
COMMIT

select @DocRowId = RowID from InvoiceHeader_External ihe with (nolock)
	Inner join exacto_inv_hd eih with (nolock) on eih.InvoiceNumber = ihe.InvoiceNumber
	where eih.doc_uuid = @DocUUID 

	print @DocRowId
print 'Success ' + cast(@DocRowId as varchar);
END TRY
BEGIN CATCH
    ROLLBACK
    DECLARE @ErrorMessage NVARCHAR(1000) = ERROR_MESSAGE();
    INSERT INTO Exception_table values (@DocUUID, GETDATE(), @ErrorMessage, 'Invoice')
	print 'Fail ' + @DocUUID;  
END CATCH

END

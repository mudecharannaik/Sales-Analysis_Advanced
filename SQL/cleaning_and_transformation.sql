-- ============================================================================
-- CLEANING AND TRANSFORMATION
-- ============================================================================
-- Transform RawData into CleanedData with derived columns and business rules
-- ============================================================================

USE SalesAnalysisDB;
GO

-- ============================================================================
-- 1. IDENTIFY AND FLAG DUPLICATES
-- ============================================================================

-- Create a flag column in RawData to mark duplicates
-- Duplicates are defined as identical values across all key columns

IF COL_LENGTH('RawData', 'IsDuplicate') IS NULL
    ALTER TABLE RawData ADD IsDuplicate BIT DEFAULT 0;
GO

-- Flag exact duplicates (same RowID - shouldn't happen but check)
UPDATE r
SET IsDuplicate = 1
FROM RawData r
INNER JOIN (
    SELECT RowID
    FROM RawData
    GROUP BY RowID
    HAVING COUNT(*) > 1
) dup ON r.RowID = dup.RowID;
GO

-- Flag duplicate OrderID + ProductID combinations (same order, same product)
-- This identifies duplicate line items within the same order
UPDATE r
SET IsDuplicate = 1
FROM RawData r
INNER JOIN (
    SELECT OrderID, ProductID, COUNT(*) AS cnt
    FROM RawData
    GROUP BY OrderID, ProductID, Sales, Quantity, Discount, Profit, ShippingCost
    HAVING COUNT(*) > 1
) dup ON r.OrderID = dup.OrderID 
   AND r.ProductID = dup.ProductID;
GO

-- Log duplicate counts
INSERT INTO DataQualityLog (CheckType, ColumnName, IssueType, IssueCount, Severity, ActionTaken)
SELECT 
    'Duplicate Check', 'Multiple', 'Duplicate Rows Flagged',
    COUNT(*), 'Medium', 'Flagged in IsDuplicate column'
FROM RawData
WHERE IsDuplicate = 1;
GO

-- ============================================================================
-- 2. HANDLE NULL VALUES
-- ============================================================================

-- Log all NULLs before transformation
-- Postal Code: many NULLs expected, document but keep
INSERT INTO DataQualityLog (CheckType, ColumnName, IssueType, IssueCount, Severity, ActionTaken)
SELECT 
    'Null Documentation', 'PostalCode', 'NULL Values',
    COUNT(*), 'Medium', 'Documented - postal code not required for core analysis'
FROM RawData
WHERE PostalCode IS NULL;
GO

-- ShipDate NULLs: keep as NULL (some orders may not have shipped yet)
INSERT INTO DataQualityLog (CheckType, ColumnName, IssueType, IssueCount, Severity, ActionTaken)
SELECT 
    'Null Documentation', 'ShipDate', 'NULL Values',
    COUNT(*), 'Low', 'Documented - order not yet shipped'
FROM RawData
WHERE ShipDate IS NULL;
GO

-- Standardize NULL text fields to empty string for text columns that shouldn't be NULL
-- But keep true NULLs for optional fields

-- ============================================================================
-- 3. STANDARDIZE CATEGORICAL VALUES
-- ============================================================================

-- Trim and uppercase categorical values for consistency
-- Create a staging table for cleaned data

IF OBJECT_ID('tempdb..#CleanedStaging') IS NOT NULL
    DROP TABLE #CleanedStaging;
GO

SELECT 
    RowID,
    UPPER(TRIM(OrderID)) AS OrderID,
    -- Convert date strings to DATE type
    TRY_CONVERT(DATE, TRIM(OrderDate), 101) AS OrderDate,
    TRY_CONVERT(DATE, TRIM(ShipDate), 101) AS ShipDate,
    UPPER(TRIM(ShipMode)) AS ShipMode,
    UPPER(TRIM(CustomerID)) AS CustomerID,
    UPPER(TRIM(CustomerName)) AS CustomerName,
    UPPER(TRIM(Segment)) AS Segment,
    UPPER(TRIM(City)) AS City,
    UPPER(TRIM(State)) AS State,
    UPPER(TRIM(Country)) AS Country,
    -- Keep NULLs explicit for PostalCode
    NULLIF(UPPER(TRIM(PostalCode)), '') AS PostalCode,
    UPPER(TRIM(Market)) AS Market,
    UPPER(TRIM(Region)) AS Region,
    UPPER(TRIM(ProductID)) AS ProductID,
    UPPER(TRIM(Category)) AS Category,
    UPPER(TRIM(SubCategory)) AS SubCategory,
    UPPER(TRIM(ProductName)) AS ProductName,
    -- Numeric columns
    ISNULL(Sales, 0) AS Sales,
    ISNULL(Quantity, 1) AS Quantity,
    -- Discount: clamp to [0,1]
    CASE 
        WHEN Discount IS NULL THEN 0
        WHEN Discount < 0 THEN 0
        WHEN Discount > 1 THEN 1
        ELSE Discount 
    END AS Discount,
    ISNULL(Profit, 0) AS Profit,
    ISNULL(ShippingCost, 0) AS ShippingCost,
    UPPER(TRIM(OrderPriority)) AS OrderPriority,
    IsDuplicate
INTO #CleanedStaging
FROM RawData;
GO

-- ============================================================================
-- 4. INSERT INTO CLEANEDDATA WITH DERIVED COLUMNS
-- ============================================================================

-- CleanedData has computed columns (generated always as stored)
-- We insert the base columns; derived columns are auto-computed

TRUNCATE TABLE CleanedData;
GO

INSERT INTO CleanedData (
    RowID, OrderID, OrderDate, ShipDate, ShipMode, CustomerID,
    CustomerName, Segment, City, State, Country, PostalCode,
    Market, Region, ProductID, Category, SubCategory, ProductName,
    Sales, Quantity, Discount, Profit, ShippingCost, OrderPriority
)
SELECT 
    RowID, OrderID, OrderDate, ShipDate, ShipMode, CustomerID,
    CustomerName, Segment, City, State, Country, PostalCode,
    Market, Region, ProductID, Category, SubCategory, ProductName,
    Sales, Quantity, Discount, Profit, ShippingCost, OrderPriority
FROM #CleanedStaging
WHERE IsDuplicate = 0;  -- Exclude flagged duplicates
GO

-- ============================================================================
-- 5. POPULATE DIMENSION TABLES
-- ============================================================================

-- 5.1 Customers
TRUNCATE TABLE Customers;
GO

INSERT INTO Customers (CustomerID, CustomerName, Segment, FirstOrderDate, LastOrderDate, TotalOrders, TotalSales, TotalProfit)
SELECT 
    CustomerID,
    MAX(CustomerName) AS CustomerName,  -- should be consistent
    MAX(Segment) AS Segment,
    MIN(OrderDate) AS FirstOrderDate,
    MAX(OrderDate) AS LastOrderDate,
    COUNT(DISTINCT OrderID) AS TotalOrders,
    SUM(Sales) AS TotalSales,
    SUM(Profit) AS TotalProfit
FROM CleanedData
GROUP BY CustomerID;
GO

-- 5.2 Products
TRUNCATE TABLE Products;
GO

INSERT INTO Products (ProductID, ProductName, Category, SubCategory)
SELECT DISTINCT
    ProductID,
    ProductName,
    Category,
    SubCategory
FROM CleanedData;
GO

-- 5.3 Orders (distinct OrderID level)
TRUNCATE TABLE Orders;
GO

INSERT INTO Orders (OrderID, OrderDate, ShipDate, ShipMode, CustomerID, Segment, Market, Region, OrderPriority)
SELECT DISTINCT
    OrderID,
    MIN(OrderDate) AS OrderDate,  -- should be same within order
    MIN(ShipDate) AS ShipDate,
    MAX(ShipMode) AS ShipMode,
    MAX(CustomerID) AS CustomerID,
    MAX(Segment) AS Segment,
    MAX(Market) AS Market,
    MAX(Region) AS Region,
    MAX(OrderPriority) AS OrderPriority
FROM CleanedData
GROUP BY OrderID;
GO

-- 5.4 OrderDetails (line items)
TRUNCATE TABLE OrderDetails;
GO

INSERT INTO OrderDetails (OrderID, ProductID, Sales, Quantity, Discount, Profit, ShippingCost)
SELECT 
    OrderID,
    ProductID,
    SUM(Sales) AS Sales,
    SUM(Quantity) AS Quantity,
    AVG(Discount) AS Discount,
    SUM(Profit) AS Profit,
    SUM(ShippingCost) AS ShippingCost
FROM CleanedData
GROUP BY OrderID, ProductID;
GO

-- 5.5 Geography
TRUNCATE TABLE Geography;
GO

INSERT INTO Geography (Country, State, City, PostalCode, Market, Region)
SELECT DISTINCT
    Country,
    State,
    City,
    PostalCode,
    Market,
    Region
FROM CleanedData;
GO

-- ============================================================================
-- 6. UPDATE STATISTICS
-- ============================================================================

-- Update statistics for all tables to ensure optimal query plans
UPDATE STATISTICS CleanedData WITH FULLSCAN;
UPDATE STATISTICS Customers WITH FULLSCAN;
UPDATE STATISTICS Products WITH FULLSCAN;
UPDATE STATISTICS Orders WITH FULLSCAN;
UPDATE STATISTICS OrderDetails WITH FULLSCAN;
UPDATE STATISTICS Geography WITH FULLSCAN;
GO

-- ============================================================================
-- 7. VERIFICATION QUERIES
-- ============================================================================

-- Verify row counts
SELECT 
    'CleanedData' AS TableName,
    COUNT(*) AS RowCount
FROM CleanedData
UNION ALL
SELECT 
    'Customers',
    COUNT(*)
FROM Customers
UNION ALL
SELECT 
    'Products',
    COUNT(*)
FROM Products
UNION ALL
SELECT 
    'Orders',
    COUNT(*)
FROM Orders
UNION ALL
SELECT 
    'OrderDetails',
    COUNT(*)
FROM OrderDetails
UNION ALL
SELECT 
    'Geography',
    COUNT(*)
FROM Geography;
GO

-- Verify derived columns
SELECT TOP 10 
    RowID, OrderID, OrderDate, OrderYear, OrderMonth, OrderQuarter,
    OrderDayOfWeek, ShippingDays, ProfitRatio, SalesPerUnit, DiscountBand, OrderPeriod
FROM CleanedData;
GO

-- Clean up temp table
DROP TABLE IF EXISTS #CleanedStaging;
GO

PRINT 'Cleaning and transformation completed successfully.';
GO

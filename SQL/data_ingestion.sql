-- ============================================================================
-- DATA INGESTION: Load CSV into RawData staging table
-- ============================================================================
-- CSV: D:\All_Data_Projects\Final\GoodProjects\SalesAnalysis\Data\superstore_raw.csv
-- Target: SalesAnalysisDB.dbo.RawData
-- ============================================================================

USE SalesAnalysisDB;
GO

-- ============================================================================
-- 1. STAGING TABLE (optional, for extra validation before final load)
-- ============================================================================
-- Using a staging table allows us to validate data before inserting into RawData

IF OBJECT_ID('staging_StagingRaw', 'U') IS NOT NULL
    DROP TABLE staging_StagingRaw;
GO

CREATE TABLE staging_StagingRaw (
    RowID           INT,
    OrderID         VARCHAR(50),
    OrderDate       VARCHAR(50),
    ShipDate        VARCHAR(50),
    ShipMode        VARCHAR(100),
    CustomerID      VARCHAR(50),
    CustomerName    VARCHAR(200),
    Segment         VARCHAR(100),
    City            VARCHAR(200),
    State           VARCHAR(200),
    Country         VARCHAR(200),
    PostalCode      VARCHAR(50),
    Market          VARCHAR(100),
    Region          VARCHAR(100),
    ProductID       VARCHAR(50),
    Category        VARCHAR(100),
    SubCategory     VARCHAR(100),
    ProductName     VARCHAR(500),
    Sales           VARCHAR(50),           -- load as string for validation
    Quantity        VARCHAR(50),
    Discount        VARCHAR(50),
    Profit          VARCHAR(50),
    ShippingCost    VARCHAR(50),
    OrderPriority   VARCHAR(50),
    LoadTimestamp   DATETIME DEFAULT GETDATE(),
    RowHash         VARBINARY(64)         -- for duplicate detection
);
GO

-- ============================================================================
-- 2. BULK INSERT COMMAND (SQL Server)
-- ============================================================================

-- First, clear staging table
TRUNCATE TABLE staging_StagingRaw;
GO

-- Bulk insert from CSV
-- Note: Adjust FIELDTERMINATOR and ROWTERMINATOR if CSV uses different delimiters
BULK INSERT staging_StagingRaw
FROM 'D:\All_Data_Projects\Final\GoodProjects\SalesAnalysis\Data\superstore_raw.csv'
WITH (
    FIRSTROW = 2,                          -- skip header row
    FIELDTERMINATOR = ',',                 -- standard CSV comma delimiter
    ROWTERMINATOR = '\n',                  -- newline row terminator
    CODEPAGE = '65001',                    -- UTF-8 encoding
    DATAFILETYPE = 'char',
    KEEPNULLS,
    TABLOCK
);
GO

-- ============================================================================
-- 3. DATA TYPE CONVERSIONS AND VALIDATION
-- ============================================================================

-- Convert and validate data from staging to RawData
-- Using TRY_CONVERT to handle any malformed values gracefully

TRUNCATE TABLE RawData;
GO

INSERT INTO RawData (
    RowID, OrderID, OrderDate, ShipDate, ShipMode, CustomerID,
    CustomerName, Segment, City, State, Country, PostalCode,
    Market, Region, ProductID, Category, SubCategory, ProductName,
    Sales, Quantity, Discount, Profit, ShippingCost, OrderPriority
)
SELECT
    -- RowID: must be valid integer
    TRY_CONVERT(INT, TRIM(RowID)),

    -- OrderID: text field, trim whitespace
    TRIM(OrderID),

    -- OrderDate: convert string to DATE, keep original if invalid
    TRY_CONVERT(DATE, TRIM(OrderDate), 101),   -- 101 = mm/dd/yyyy format

    -- ShipDate: convert string to DATE
    TRY_CONVERT(DATE, TRIM(ShipDate), 101),

    -- ShipMode: trim text
    TRIM(ShipMode),

    -- CustomerID: trim text
    TRIM(CustomerID),

    -- CustomerName: trim text
    TRIM(CustomerName),

    -- Segment: trim text
    TRIM(Segment),

    -- City: trim text
    TRIM(City),

    -- State: trim text
    TRIM(State),

    -- Country: trim text
    TRIM(Country),

    -- PostalCode: keep NULLs explicit, trim non-null
    NULLIF(TRIM(PostalCode), ''),

    -- Market: trim text
    TRIM(Market),

    -- Region: trim text
    TRIM(Region),

    -- ProductID: trim text
    TRIM(ProductID),

    -- Category: trim text
    TRIM(Category),

    -- SubCategory: trim text
    TRIM(SubCategory),

    -- ProductName: trim text
    TRIM(ProductName),

    -- Sales: numeric, convert from string
    TRY_CONVERT(DECIMAL(18,2), TRIM(Sales)),

    -- Quantity: integer
    TRY_CONVERT(INT, TRIM(Quantity)),

    -- Discount: decimal (0-1 range)
    TRY_CONVERT(DECIMAL(5,4), TRIM(Discount)),

    -- Profit: decimal, can be negative
    TRY_CONVERT(DECIMAL(18,2), TRIM(Profit)),

    -- ShippingCost: decimal
    TRY_CONVERT(DECIMAL(18,2), TRIM(ShippingCost)),

    -- OrderPriority: trim text
    TRIM(OrderPriority)

FROM staging_StagingRaw;
GO

-- ============================================================================
-- 4. POSTAL CODE HANDLING
-- ============================================================================
-- Explicitly document NULL postal codes
-- PostalCode has 41296 missing values expected

INSERT INTO DataQualityLog (CheckType, ColumnName, IssueType, IssueCount, Severity, ActionTaken)
SELECT 
    'Null Check',
    'PostalCode',
    'NULL Values',
    COUNT(*),
    'Medium',
    'Retained NULLs - postal code not required for analysis'
FROM RawData
WHERE PostalCode IS NULL;
GO

-- ============================================================================
-- 5. DATE VALIDATION
-- ============================================================================

-- Log any rows where date conversion failed
INSERT INTO DataQualityLog (CheckType, ColumnName, IssueType, IssueCount, Severity, ActionTaken)
SELECT 
    'Date Conversion',
    'OrderDate',
    'Invalid Date Format',
    COUNT(*),
    'High',
    'Rows with invalid dates will be excluded from time-series analysis'
FROM RawData
WHERE OrderDate IS NULL
   OR TRY_CONVERT(DATE, OrderDate, 101) IS NULL
   AND OrderDate IS NOT NULL;
GO

-- ============================================================================
-- 6. CLEAR STAGING TABLE AFTER SUCCESSFUL LOAD
-- ============================================================================

TRUNCATE TABLE staging_StagingRaw;
GO

-- Drop staging table if no longer needed
-- DROP TABLE staging_StagingRaw;
GO

-- ============================================================================
-- 7. VERIFICATION QUERY
-- ============================================================================

SELECT 
    'RawData Load Summary' AS Summary,
    COUNT(*) AS TotalRows,
    MIN(TRY_CONVERT(DATE, OrderDate, 101)) AS MinOrderDate,
    MAX(TRY_CONVERT(DATE, OrderDate, 101)) AS MaxOrderDate,
    SUM(CASE WHEN PostalCode IS NULL THEN 1 ELSE 0 END) AS NullPostalCodes,
    SUM(CASE WHEN Sales IS NULL THEN 1 ELSE 0 END) AS NullSales,
    SUM(CASE WHEN Profit IS NULL THEN 1 ELSE 0 END) AS NullProfit
FROM RawData;
GO

PRINT 'Data ingestion completed successfully.';
GO

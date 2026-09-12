-- ============================================================================
-- DATA LINEAGE AND METADATA
-- ============================================================================
-- Metadata documentation and data lineage tracking
-- ============================================================================

USE SalesAnalysisDB;
GO

-- ============================================================================
-- 1. POPULATE TABLE METADATA
-- ============================================================================

INSERT INTO TableMetadata (TableName, Description, SourceTable, RowCount)
VALUES 
    ('RawData', 'Raw data loaded directly from CSV file without any transformation', 'superstore_raw.csv', (SELECT COUNT(*) FROM RawData)),
    ('CleanedData', 'Cleaned and transformed data with derived columns and business rule validations', 'RawData', (SELECT COUNT(*) FROM CleanedData)),
    ('Customers', 'Dimension table with one row per customer and aggregated metrics', 'CleanedData', (SELECT COUNT(*) FROM Customers)),
    ('Products', 'Dimension table with distinct product information', 'CleanedData', (SELECT COUNT(*) FROM Products)),
    ('Orders', 'Order header table with one row per order', 'CleanedData', (SELECT COUNT(*) FROM Orders)),
    ('OrderDetails', 'Order line items fact table', 'CleanedData', (SELECT COUNT(*) FROM OrderDetails)),
    ('Geography', 'Geographic dimension table with distinct location combinations', 'CleanedData', (SELECT COUNT(*) FROM Geography)),
    ('DataQualityLog', 'Log of all data quality checks and issues found', 'System', (SELECT COUNT(*) FROM DataQualityLog)),
    ('AnalyticsSummary', 'Pre-computed analytics metrics for reporting', 'CleanedData', (SELECT COUNT(*) FROM AnalyticsSummary)),
    ('schema', 'Schema definition for SalesAnalysisDB', 'Manual', 0);
GO

-- ============================================================================
-- 2. POPULATE COLUMN METADATA
-- ============================================================================

-- RawData columns
INSERT INTO ColumnMetadata (TableName, ColumnName, DataType, IsNullable, Description, SourceColumn, Transformation)
VALUES
('RawData', 'RowID', 'INT', 0, 'Primary key - sequential row number from source', 'Row ID', 'None'),
('RawData', 'OrderID', 'VARCHAR(50)', 0, 'Unique order identifier', 'Order ID', 'TRIM(UPPER())'),
('RawData', 'OrderDate', 'VARCHAR(50)', 1, 'Order date as string (mm/dd/yyyy)', 'Order Date', 'TRY_CONVERT(DATE, ..., 101)'),
('RawData', 'ShipDate', 'VARCHAR(50)', 1, 'Ship date as string (mm/dd/yyyy)', 'Ship Date', 'TRY_CONVERT(DATE, ..., 101)'),
('RawData', 'ShipMode', 'VARCHAR(100)', 1, 'Shipping method used', 'Ship Mode', 'TRIM(UPPER())'),
('RawData', 'CustomerID', 'VARCHAR(50)', 1, 'Unique customer identifier', 'Customer ID', 'TRIM(UPPER())'),
('RawData', 'CustomerName', 'VARCHAR(200)', 1, 'Full customer name', 'Customer Name', 'TRIM(UPPER())'),
('RawData', 'Segment', 'VARCHAR(100)', 1, 'Customer segment (Consumer/Corporate/Home Office)', 'Segment', 'TRIM(UPPER())'),
('RawData', 'City', 'VARCHAR(200)', 1, 'City name', 'City', 'TRIM(UPPER())'),
('RawData', 'State', 'VARCHAR(200)', 1, 'State name', 'State', 'TRIM(UPPER())'),
('RawData', 'Country', 'VARCHAR(200)', 1, 'Country name', 'Country', 'TRIM(UPPER())'),
('RawData', 'PostalCode', 'VARCHAR(50)', 1, 'Postal/ZIP code (many NULLs expected)', 'Postal Code', 'NULLIF(TRIM(), '''')'),
('RawData', 'Market', 'VARCHAR(100)', 1, 'Market region', 'Market', 'TRIM(UPPER())'),
('RawData', 'Region', 'VARCHAR(100)', 1, 'Geographic region', 'Region', 'TRIM(UPPER())'),
('RawData', 'ProductID', 'VARCHAR(50)', 1, 'Unique product identifier', 'Product ID', 'TRIM(UPPER())'),
('RawData', 'Category', 'VARCHAR(100)', 1, 'Product category', 'Category', 'TRIM(UPPER())'),
('RawData', 'SubCategory', 'VARCHAR(100)', 1, 'Product sub-category', 'Sub-Category', 'TRIM(UPPER())'),
('RawData', 'ProductName', 'VARCHAR(500)', 1, 'Full product name', 'Product Name', 'TRIM(UPPER())'),
('RawData', 'Sales', 'DECIMAL(18,2)', 1, 'Sales amount in currency', 'Sales', 'TRY_CONVERT(DECIMAL, ...)'),
('RawData', 'Quantity', 'INT', 1, 'Number of units sold', 'Quantity', 'TRY_CONVERT(INT, ...)'),
('RawData', 'Discount', 'DECIMAL(5,4)', 1, 'Discount applied (0.0 to 1.0)', 'Discount', 'TRY_CONVERT(DECIMAL, ...)'),
('RawData', 'Profit', 'DECIMAL(18,2)', 1, 'Profit amount (can be negative)', 'Profit', 'TRY_CONVERT(DECIMAL, ...)'),
('RawData', 'ShippingCost', 'DECIMAL(18,2)', 1, 'Shipping cost', 'Shipping Cost', 'TRY_CONVERT(DECIMAL, ...)'),
('RawData', 'OrderPriority', 'VARCHAR(50)', 1, 'Order priority level', 'Order Priority', 'TRIM(UPPER())');
GO

-- CleanedData columns
INSERT INTO ColumnMetadata (TableName, ColumnName, DataType, IsNullable, Description, SourceColumn, Transformation)
VALUES
('CleanedData', 'RowID', 'INT', 0, 'Primary key', 'RawData.RowID', 'Direct copy'),
('CleanedData', 'OrderID', 'VARCHAR(50)', 0, 'Unique order identifier', 'RawData.OrderID', 'TRIM(UPPER())'),
('CleanedData', 'OrderDate', 'DATE', 0, 'Order date converted from string', 'RawData.OrderDate', 'TRY_CONVERT(DATE, ..., 101)'),
('CleanedData', 'ShipDate', 'DATE', 1, 'Ship date converted from string', 'RawData.ShipDate', 'TRY_CONVERT(DATE, ..., 101)'),
('CleanedData', 'ShipMode', 'VARCHAR(100)', 1, 'Shipping method', 'RawData.ShipMode', 'TRIM(UPPER())'),
('CleanedData', 'CustomerID', 'VARCHAR(50)', 1, 'Customer identifier', 'RawData.CustomerID', 'TRIM(UPPER())'),
('CleanedData', 'CustomerName', 'VARCHAR(200)', 1, 'Customer name', 'RawData.CustomerName', 'TRIM(UPPER())'),
('CleanedData', 'Segment', 'VARCHAR(100)', 1, 'Customer segment', 'RawData.Segment', 'TRIM(UPPER())'),
('CleanedData', 'City', 'VARCHAR(200)', 1, 'City name', 'RawData.City', 'TRIM(UPPER())'),
('CleanedData', 'State', 'VARCHAR(200)', 1, 'State name', 'RawData.State', 'TRIM(UPPER())'),
('CleanedData', 'Country', 'VARCHAR(200)', 1, 'Country name', 'RawData.Country', 'TRIM(UPPER())'),
('CleanedData', 'PostalCode', 'VARCHAR(50)', 1, 'Postal code (NULLs retained)', 'RawData.PostalCode', 'NULLIF(TRIM(UPPER()), '''')'),
('CleanedData', 'Market', 'VARCHAR(100)', 1, 'Market region', 'RawData.Market', 'TRIM(UPPER())'),
('CleanedData', 'Region', 'VARCHAR(100)', 1, 'Geographic region', 'RawData.Region', 'TRIM(UPPER())'),
('CleanedData', 'ProductID', 'VARCHAR(50)', 1, 'Product identifier', 'RawData.ProductID', 'TRIM(UPPER())'),
('CleanedData', 'Category', 'VARCHAR(100)', 1, 'Product category', 'RawData.Category', 'TRIM(UPPER())'),
('CleanedData', 'SubCategory', 'VARCHAR(100)', 1, 'Product sub-category', 'RawData.SubCategory', 'TRIM(UPPER())'),
('CleanedData', 'ProductName', 'VARCHAR(500)', 1, 'Product name', 'RawData.ProductName', 'TRIM(UPPER())'),
('CleanedData', 'Sales', 'DECIMAL(18,2)', 1, 'Sales amount', 'RawData.Sales', 'ISNULL(0)'),
('CleanedData', 'Quantity', 'INT', 1, 'Quantity sold', 'RawData.Quantity', 'ISNULL(1)'),
('CleanedData', 'Discount', 'DECIMAL(5,4)', 1, 'Discount rate', 'RawData.Discount', 'CASE clamp [0,1]'),
('CleanedData', 'Profit', 'DECIMAL(18,2)', 1, 'Profit amount', 'RawData.Profit', 'ISNULL(0)'),
('CleanedData', 'ShippingCost', 'DECIMAL(18,2)', 1, 'Shipping cost', 'RawData.ShippingCost', 'ISNULL(0)'),
('CleanedData', 'OrderPriority', 'VARCHAR(50)', 1, 'Order priority', 'RawData.OrderPriority', 'TRIM(UPPER())'),
('CleanedData', 'OrderYear', 'INT', 0, 'Year of order date (derived)', 'OrderDate', 'YEAR(OrderDate)'),
('CleanedData', 'OrderMonth', 'INT', 0, 'Month of order date (derived)', 'OrderDate', 'MONTH(OrderDate)'),
('CleanedData', 'OrderQuarter', 'INT', 0, 'Quarter of order date (derived)', 'OrderDate', 'DATEPART(QUARTER, OrderDate)'),
('CleanedData', 'OrderDayOfWeek', 'INT', 0, 'Day of week (1=Monday)', 'OrderDate', 'DATEPART(WEEKDAY, OrderDate)'),
('CleanedData', 'ShippingDays', 'INT', 1, 'Days between order and ship', 'OrderDate, ShipDate', 'DATEDIFF(DAY, OrderDate, ShipDate)'),
('CleanedData', 'ProfitRatio', 'DECIMAL(10,4)', 1, 'Profit / Sales ratio', 'Sales, Profit', 'Profit / Sales'),
('CleanedData', 'SalesPerUnit', 'DECIMAL(18,2)', 1, 'Sales / Quantity', 'Sales, Quantity', 'Sales / Quantity'),
('CleanedData', 'DiscountBand', 'VARCHAR(20)', 0, 'Discount categorization', 'Discount', 'CASE statement'),
('CleanedData', 'OrderPeriod', 'VARCHAR(20)', 0, 'Seasonal period', 'OrderMonth', 'CASE statement');
GO

-- Customers columns
INSERT INTO ColumnMetadata (TableName, ColumnName, DataType, IsNullable, Description, SourceColumn, Transformation)
VALUES
('Customers', 'CustomerID', 'VARCHAR(50)', 0, 'Primary key - customer identifier', 'CleanedData.CustomerID', 'GROUP BY'),
('Customers', 'CustomerName', 'VARCHAR(200)', 0, 'Customer full name', 'CleanedData.CustomerName', 'MAX()'),
('Customers', 'Segment', 'VARCHAR(100)', 1, 'Customer segment', 'CleanedData.Segment', 'MAX()'),
('Customers', 'FirstOrderDate', 'DATE', 1, 'Date of first order', 'CleanedData.OrderDate', 'MIN()'),
('Customers', 'LastOrderDate', 'DATE', 1, 'Date of most recent order', 'CleanedData.OrderDate', 'MAX()'),
('Customers', 'TotalOrders', 'INT', 0, 'Total number of orders', 'CleanedData.OrderID', 'COUNT(DISTINCT)'),
('Customers', 'TotalSales', 'DECIMAL(18,2)', 0, 'Total sales amount', 'CleanedData.Sales', 'SUM()'),
('Customers', 'TotalProfit', 'DECIMAL(18,2)', 0, 'Total profit amount', 'CleanedData.Profit', 'SUM()');
GO

-- Products columns
INSERT INTO ColumnMetadata (TableName, ColumnName, DataType, IsNullable, Description, SourceColumn, Transformation)
VALUES
('Products', 'ProductID', 'VARCHAR(50)', 0, 'Primary key - product identifier', 'CleanedData.ProductID', 'DISTINCT'),
('Products', 'ProductName', 'VARCHAR(500)', 0, 'Full product name', 'CleanedData.ProductName', 'DISTINCT'),
('Products', 'Category', 'VARCHAR(100)', 0, 'Product category', 'CleanedData.Category', 'DISTINCT'),
('Products', 'SubCategory', 'VARCHAR(100)', 0, 'Product sub-category', 'CleanedData.SubCategory', 'DISTINCT');
GO

-- Orders columns
INSERT INTO ColumnMetadata (TableName, ColumnName, DataType, IsNullable, Description, SourceColumn, Transformation)
VALUES
('Orders', 'OrderID', 'VARCHAR(50)', 0, 'Primary key - order identifier', 'CleanedData.OrderID', 'DISTINCT'),
('Orders', 'OrderDate', 'DATE', 0, 'Order date', 'CleanedData.OrderDate', 'MIN()'),
('Orders', 'ShipDate', 'DATE', 1, 'Ship date', 'CleanedData.ShipDate', 'MIN()'),
('Orders', 'ShipMode', 'VARCHAR(100)', 1, 'Shipping method', 'CleanedData.ShipMode', 'MAX()'),
('Orders', 'CustomerID', 'VARCHAR(50)', 1, 'Customer identifier', 'CleanedData.CustomerID', 'MAX()'),
('Orders', 'Segment', 'VARCHAR(100)', 1, 'Customer segment', 'CleanedData.Segment', 'MAX()'),
('Orders', 'Market', 'VARCHAR(100)', 1, 'Market region', 'CleanedData.Market', 'MAX()'),
('Orders', 'Region', 'VARCHAR(100)', 1, 'Geographic region', 'CleanedData.Region', 'MAX()'),
('Orders', 'OrderPriority', 'VARCHAR(50)', 1, 'Order priority', 'CleanedData.OrderPriority', 'MAX()');
GO

-- OrderDetails columns
INSERT INTO ColumnMetadata (TableName, ColumnName, DataType, IsNullable, Description, SourceColumn, Transformation)
VALUES
('OrderDetails', 'OrderDetailID', 'INT', 0, 'Primary key - identity column', 'System', 'IDENTITY(1,1)'),
('OrderDetails', 'OrderID', 'VARCHAR(50)', 0, 'Foreign key to Orders', 'CleanedData.OrderID', 'GROUP BY'),
('OrderDetails', 'ProductID', 'VARCHAR(50)', 0, 'Foreign key to Products', 'CleanedData.ProductID', 'GROUP BY'),
('OrderDetails', 'Sales', 'DECIMAL(18,2)', 1, 'Sales amount for line item', 'CleanedData.Sales', 'SUM()'),
('OrderDetails', 'Quantity', 'INT', 1, 'Quantity for line item', 'CleanedData.Quantity', 'SUM()'),
('OrderDetails', 'Discount', 'DECIMAL(5,4)', 1, 'Discount for line item', 'CleanedData.Discount', 'AVG()'),
('OrderDetails', 'Profit', 'DECIMAL(18,2)', 1, 'Profit for line item', 'CleanedData.Profit', 'SUM()'),
('OrderDetails', 'ShippingCost', 'DECIMAL(18,2)', 1, 'Shipping cost for line item', 'CleanedData.ShippingCost', 'SUM()');
GO

-- Geography columns
INSERT INTO ColumnMetadata (TableName, ColumnName, DataType, IsNullable, Description, SourceColumn, Transformation)
VALUES
('Geography', 'GeographyID', 'INT', 0, 'Primary key - identity', 'System', 'IDENTITY(1,1)'),
('Geography', 'Country', 'VARCHAR(200)', 0, 'Country name', 'CleanedData.Country', 'DISTINCT'),
('Geography', 'State', 'VARCHAR(200)', 0, 'State name', 'CleanedData.State', 'DISTINCT'),
('Geography', 'City', 'VARCHAR(200)', 0, 'City name', 'CleanedData.City', 'DISTINCT'),
('Geography', 'PostalCode', 'VARCHAR(50)', 1, 'Postal/ZIP code', 'CleanedData.PostalCode', 'DISTINCT'),
('Geography', 'Market', 'VARCHAR(100)', 0, 'Market region', 'CleanedData.Market', 'DISTINCT'),
('Geography', 'Region', 'VARCHAR(100)', 0, 'Geographic region', 'CleanedData.Region', 'DISTINCT');
GO

-- DataQualityLog columns
INSERT INTO ColumnMetadata (TableName, ColumnName, DataType, IsNullable, Description, SourceColumn, Transformation)
VALUES
('DataQualityLog', 'LogID', 'INT', 0, 'Primary key - identity', 'System', 'IDENTITY(1,1)'),
('DataQualityLog', 'CheckDate', 'DATETIME', 0, 'Date/time of check', 'System', 'GETDATE()'),
('DataQualityLog', 'CheckType', 'VARCHAR(100)', 0, 'Type of data quality check', 'System', 'Manual'),
('DataQualityLog', 'ColumnName', 'VARCHAR(100)', 1, 'Column being checked', 'System', 'Manual'),
('DataQualityLog', 'IssueType', 'VARCHAR(200)', 0, 'Type of issue found', 'System', 'Manual'),
('DataQualityLog', 'IssueCount', 'INT', 0, 'Number of issues found', 'System', 'COUNT()'),
('DataQualityLog', 'Severity', 'VARCHAR(20)', 0, 'Issue severity (High/Medium/Low)', 'System', 'Manual'),
('DataQualityLog', 'ActionTaken', 'VARCHAR(500)', 1, 'Action taken to resolve', 'System', 'Manual');
GO

-- AnalyticsSummary columns
INSERT INTO ColumnMetadata (TableName, ColumnName, DataType, IsNullable, Description, SourceColumn, Transformation)
VALUES
('AnalyticsSummary', 'SummaryID', 'INT', 0, 'Primary key - identity', 'System', 'IDENTITY(1,1)'),
('AnalyticsSummary', 'MetricName', 'VARCHAR(200)', 0, 'Name of the metric', 'System', 'Manual'),
('AnalyticsSummary', 'MetricValue', 'DECIMAL(18,4)', 0, 'Value of the metric', 'CleanedData', 'Aggregation'),
('AnalyticsSummary', 'Period', 'VARCHAR(50)', 1, 'Time period (yyyy-MM)', 'CleanedData.OrderDate', 'FORMAT()'),
('AnalyticsSummary', 'Category', 'VARCHAR(100)', 1, 'Metric category', 'System', 'Manual'),
('AnalyticsSummary', 'GeneratedDate', 'DATETIME', 0, 'When metric was generated', 'System', 'GETDATE()');
GO

-- ============================================================================
-- 3. DATA LINEAGE DOCUMENTATION
-- ============================================================================

-- Create a dedicated lineage tracking table
IF OBJECT_ID('DataLineage', 'U') IS NOT NULL
    DROP TABLE DataLineage;
GO

CREATE TABLE DataLineage (
    LineageID      INT IDENTITY(1,1) PRIMARY KEY,
    ProcessName    VARCHAR(200) NOT NULL,
    ProcessStep    INT NOT NULL,
    SourceTable    VARCHAR(200) NOT NULL,
    TargetTable    VARCHAR(200) NOT NULL,
    TransformDesc  VARCHAR(1000),
    ProcessDate    DATETIME DEFAULT GETDATE(),
    ProcessedBy    VARCHAR(100) DEFAULT SYSTEM_USER,
    RowCount       INT,
    Status         VARCHAR(50) DEFAULT 'Success'
);
GO

-- Document the ETL lineage
INSERT INTO DataLineage (ProcessName, ProcessStep, SourceTable, TargetTable, TransformDesc, RowCount)
VALUES
('ETL_LoadRawData', 1, 'superstore_raw.csv', 'RawData', 
 'Bulk insert CSV with TRY_CONVERT for dates, NULLIF for PostalCode, ISNULL for numerics', 
 (SELECT COUNT(*) FROM RawData)),
('ETL_QualityChecks', 2, 'RawData', 'DataQualityLog',
 'Duplicate detection, null analysis, outlier detection, business rule validation',
 (SELECT COUNT(*) FROM DataQualityLog)),
('ETL_Cleaning', 3, 'RawData', 'CleanedData',
 'TRIM/UPPER for text, date conversion, discount clamping, derived columns (OrderYear, OrderMonth, etc.)',
 (SELECT COUNT(*) FROM CleanedData)),
('ETL_DimCustomers', 4, 'CleanedData', 'Customers',
 'GROUP BY CustomerID with aggregated metrics (TotalSales, TotalProfit, FirstOrderDate)',
 (SELECT COUNT(*) FROM Customers)),
('ETL_DimProducts', 5, 'CleanedData', 'Products',
 'DISTINCT ProductID, ProductName, Category, SubCategory',
 (SELECT COUNT(*) FROM Products)),
('ETL_DimOrders', 6, 'CleanedData', 'Orders',
 'DISTINCT OrderID with aggregated header fields',
 (SELECT COUNT(*) FROM Orders)),
('ETL_FactOrderDetails', 7, 'CleanedData', 'OrderDetails',
 'GROUP BY OrderID, ProductID with summed measures',
 (SELECT COUNT(*) FROM OrderDetails)),
('ETL_DimGeography', 8, 'CleanedData', 'Geography',
 'DISTINCT geographic combinations',
 (SELECT COUNT(*) FROM Geography));
GO

-- ============================================================================
-- 4. DATA FLOW DIAGRAM (as metadata)
-- ============================================================================

IF OBJECT_ID('DataFlowDiagram', 'U') IS NOT NULL
    DROP TABLE DataFlowDiagram;
GO

CREATE TABLE DataFlowDiagram (
    FlowID         INT IDENTITY(1,1) PRIMARY KEY,
    FlowName       VARCHAR(200) NOT NULL,
    Source         VARCHAR(500) NOT NULL,
    Transformation VARCHAR(1000) NOT NULL,
    Destination    VARCHAR(500) NOT NULL,
    Schedule       VARCHAR(100),  -- e.g., 'Daily', 'Weekly', 'On-demand'
    Owner          VARCHAR(100),
    CreatedDate    DATETIME DEFAULT GETDATE()
);
GO

INSERT INTO DataFlowDiagram (FlowName, Source, Transformation, Destination, Schedule, Owner)
VALUES
('Load Raw Data', 'superstore_raw.csv', 'BULK INSERT with type conversion, TRIM, NULLIF', 'RawData', 'On-demand', 'ETL Process'),
('Data Quality Check', 'RawData', 'Duplicate detection, null analysis, outlier detection, business rule validation', 'DataQualityLog', 'After load', 'ETL Process'),
('Clean and Transform', 'RawData', 'Date conversion, text standardization, NULL handling, derived columns', 'CleanedData', 'After load', 'ETL Process'),
('Build Customer Dimension', 'CleanedData', 'GROUP BY CustomerID, aggregate metrics', 'Customers', 'After clean', 'ETL Process'),
('Build Product Dimension', 'CleanedData', 'DISTINCT ProductID, ProductName, Category, SubCategory', 'Products', 'After clean', 'ETL Process'),
('Build Order Dimension', 'CleanedData', 'DISTINCT OrderID with header fields', 'Orders', 'After clean', 'ETL Process'),
('Build Order Details Fact', 'CleanedData', 'GROUP BY OrderID, ProductID, sum measures', 'OrderDetails', 'After clean', 'ETL Process'),
('Build Geography Dimension', 'CleanedData', 'DISTINCT geographic combinations', 'Geography', 'After clean', 'ETL Process'),
('Refresh Analytics', 'CleanedData, Customers, Products, Orders, OrderDetails', 'sp_RefreshMonthlyAnalytics aggregation', 'AnalyticsSummary', 'Daily', 'ETL Process');
GO

-- ============================================================================
-- 5. METADATA QUERIES FOR DOCUMENTATION
-- ============================================================================

-- List all tables with row counts
SELECT 
    t.TableName,
    t.Description,
    m.RowCount,
    m.CreatedDate,
    CASE WHEN m.LastUpdated IS NULL THEN 'Never' ELSE CONVERT(VARCHAR, m.LastUpdated) END AS LastUpdated
FROM TableMetadata t
JOIN (
    SELECT 'RawData' AS TableName, COUNT(*) AS RowCount, MAX(CheckDate) AS LastUpdated FROM RawData UNION ALL
    SELECT 'CleanedData', COUNT(*), MAX(CheckDate) FROM CleanedData UNION ALL
    SELECT 'Customers', COUNT(*), MAX(CheckDate) FROM Customers UNION ALL
    SELECT 'Products', COUNT(*), MAX(CheckDate) FROM Products UNION ALL
    SELECT 'Orders', COUNT(*), MAX(CheckDate) FROM Orders UNION ALL
    SELECT 'OrderDetails', COUNT(*), MAX(CheckDate) FROM OrderDetails UNION ALL
    SELECT 'Geography', COUNT(*), MAX(CheckDate) FROM Geography UNION ALL
    SELECT 'DataQualityLog', COUNT(*), MAX(CheckDate) FROM DataQualityLog UNION ALL
    SELECT 'AnalyticsSummary', COUNT(*), MAX(CheckDate) FROM AnalyticsSummary
) m ON t.TableName = m.TableName
ORDER BY t.TableName;
GO

-- List all columns with their metadata
SELECT 
    TableName,
    ColumnName,
    DataType,
    IsNullable,
    Description,
    SourceColumn,
    Transformation
FROM ColumnMetadata
ORDER BY TableName, ColumnName;
GO

-- Data lineage summary
SELECT 
    ProcessName,
    ProcessStep,
    SourceTable,
    TargetTable,
    TransformDesc,
    RowCount,
    Status,
    ProcessDate
FROM DataLineage
ORDER BY ProcessStep;
GO

-- ETL flow diagram
SELECT 
    FlowName,
    Source,
    Transformation,
    Destination,
    Schedule,
    Owner
FROM DataFlowDiagram
ORDER BY FlowID;
GO

-- ============================================================================
-- 6. DATA GOVERNANCE INFORMATION
-- ============================================================================

-- Data sensitivity classification
IF OBJECT_ID('DataClassification', 'U') IS NOT NULL
    DROP TABLE DataClassification;
GO

CREATE TABLE DataClassification (
    TableName      VARCHAR(200) NOT NULL,
    ColumnName     VARCHAR(200) NOT NULL,
    Sensitivity    VARCHAR(50) NOT NULL,  -- Public, Internal, Confidential, Restricted
    Reason         VARCHAR(500),
    MaskingRule    VARCHAR(500)           -- e.g., 'HASH', 'TRUNCATE', 'MASK'
);
GO

INSERT INTO DataClassification (TableName, ColumnName, Sensitivity, Reason, MaskingRule)
VALUES
('Customers', 'CustomerName', 'Confidential', 'PII - Full name', 'TRUNCATE to first letter + ***'),
('Customers', 'CustomerID', 'Internal', 'Business identifier', 'HASH'),
('RawData', 'CustomerName', 'Confidential', 'PII - Full name', 'TRUNCATE'),
('RawData', 'PostalCode', 'Restricted', 'PII - Location data', 'MASK to XXX'),
('CleanedData', 'CustomerName', 'Confidential', 'PII - Full name', 'TRUNCATE'),
('CleanedData', 'PostalCode', 'Restricted', 'PII - Location data', 'MASK to XXX'),
('Geography', 'City', 'Internal', 'Location data', 'None'),
('Geography', 'State', 'Internal', 'Location data', 'None'),
('Geography', 'PostalCode', 'Restricted', 'PII - Location data', 'MASK to XXX');
GO

-- ============================================================================
-- 7. REFRESH METADATA
-- ============================================================================

-- Update last updated timestamps
UPDATE TableMetadata
SET LastUpdated = GETDATE()
WHERE TableName IN ('RawData', 'CleanedData', 'Customers', 'Products', 'Orders', 'OrderDetails', 'Geography', 'AnalyticsSummary');
GO

PRINT 'Data lineage and metadata populated successfully.';
GO

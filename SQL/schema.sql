-- ============================================================================
-- SCHEMA DEFINITION FOR SALES ANALYSIS DATABASE
-- ============================================================================
-- Database: SalesAnalysisDB
-- Source: superstore_raw.csv (51290 rows, 24 columns)
-- Compatible with: SQL Server / PostgreSQL
-- ============================================================================

CREATE DATABASE IF NOT EXISTS SalesAnalysisDB;
GO

USE SalesAnalysisDB;
GO

-- ============================================================================
-- 1. RAW DATA TABLE
-- ============================================================================
-- Stores the exact data as loaded from CSV, before any transformations
-- ============================================================================

CREATE TABLE RawData (
    RowID           INT PRIMARY KEY,
    OrderID         VARCHAR(50) NOT NULL,
    OrderDate       VARCHAR(50),           -- stored as string initially
    ShipDate        VARCHAR(50),           -- stored as string initially
    ShipMode        VARCHAR(100),
    CustomerID      VARCHAR(50),
    CustomerName    VARCHAR(200),
    Segment         VARCHAR(100),
    City            VARCHAR(200),
    State           VARCHAR(200),
    Country         VARCHAR(200),
    PostalCode      VARCHAR(50),           -- many NULLs expected (41296 missing)
    Market          VARCHAR(100),
    Region          VARCHAR(100),
    ProductID       VARCHAR(50),
    Category        VARCHAR(100),
    SubCategory     VARCHAR(100),
    ProductName     VARCHAR(500),
    Sales           DECIMAL(18,2),
    Quantity        INT,
    Discount        DECIMAL(5,4),          -- stored as 0.0 to 1.0
    Profit          DECIMAL(18,2),
    ShippingCost    DECIMAL(18,2),
    OrderPriority   VARCHAR(50)
);

CREATE INDEX IX_RawData_OrderID ON RawData(OrderID);
CREATE INDEX IX_RawData_CustomerID ON RawData(CustomerID);
CREATE INDEX IX_RawData_ProductID ON RawData(ProductID);
CREATE INDEX IX_RawData_OrderDate ON RawData(OrderDate);
GO

-- ============================================================================
-- 2. CLEANED DATA TABLE
-- ============================================================================
-- Derived from RawData with standardized types and calculated columns
-- ============================================================================

CREATE TABLE CleanedData (
    RowID               INT PRIMARY KEY,
    OrderID             VARCHAR(50) NOT NULL,
    OrderDate           DATE NOT NULL,
    ShipDate            DATE,
    ShipMode            VARCHAR(100),
    CustomerID          VARCHAR(50),
    CustomerName        VARCHAR(200),
    Segment             VARCHAR(100),
    City                VARCHAR(200),
    State               VARCHAR(200),
    Country             VARCHAR(200),
    PostalCode          VARCHAR(50),
    Market              VARCHAR(100),
    Region              VARCHAR(100),
    ProductID           VARCHAR(50),
    Category            VARCHAR(100),
    SubCategory         VARCHAR(100),
    ProductName         VARCHAR(500),
    Sales               DECIMAL(18,2),
    Quantity            INT,
    Discount            DECIMAL(5,4),
    Profit              DECIMAL(18,2),
    ShippingCost        DECIMAL(18,2),
    OrderPriority       VARCHAR(50),

    -- Derived columns
    OrderYear           INT GENERATED ALWAYS AS (YEAR(OrderDate)) STORED,
    OrderMonth          INT GENERATED ALWAYS AS (MONTH(OrderDate)) STORED,
    OrderQuarter        INT GENERATED ALWAYS AS (DATEPART(QUARTER, OrderDate)) STORED,
    OrderDayOfWeek      INT GENERATED ALWAYS AS (DATEPART(WEEKDAY, OrderDate)) STORED,
    ShippingDays        INT GENERATED ALWAYS AS (
        CASE 
            WHEN ShipDate IS NOT NULL AND OrderDate IS NOT NULL 
            THEN DATEDIFF(DAY, OrderDate, ShipDate)
            ELSE NULL 
        END
    ) STORED,
    ProfitRatio         DECIMAL(10,4) GENERATED ALWAYS AS (
        CASE 
            WHEN Sales <> 0 THEN Profit / Sales
            ELSE NULL 
        END
    ) STORED,
    SalesPerUnit        DECIMAL(18,2) GENERATED ALWAYS AS (
        CASE 
            WHEN Quantity > 0 THEN Sales / Quantity
            ELSE NULL 
        END
    ) STORED,
    DiscountBand        VARCHAR(20) GENERATED ALWAYS AS (
        CASE 
            WHEN Discount IS NULL THEN 'Unknown'
            WHEN Discount = 0 THEN 'None'
            WHEN Discount <= 0.10 THEN 'Low'
            WHEN Discount <= 0.20 THEN 'Medium'
            ELSE 'High'
        END
    ) STORED,
    OrderPeriod         VARCHAR(20) GENERATED ALWAYS AS (
        CASE 
            WHEN OrderMonth IN (12,1,2) THEN 'Winter'
            WHEN OrderMonth IN (3,4,5) THEN 'Spring'
            WHEN OrderMonth IN (6,7,8) THEN 'Summer'
            WHEN OrderMonth IN (9,10,11) THEN 'Fall'
            ELSE 'Unknown'
        END
    ) STORED,

    CONSTRAINT CHK_CleanedData_Sales CHECK (Sales >= 0),
    CONSTRAINT CHK_CleanedData_Quantity CHECK (Quantity > 0),
    CONSTRAINT CHK_CleanedData_Discount CHECK (Discount >= 0 AND Discount <= 1),
    CONSTRAINT CHK_CleanedData_ShippingCost CHECK (ShippingCost >= 0),
    CONSTRAINT CHK_CleanedData_ShipDate CHECK (ShipDate >= OrderDate OR ShipDate IS NULL)
);

CREATE INDEX IX_CleanedData_OrderID ON CleanedData(OrderID);
CREATE INDEX IX_CleanedData_CustomerID ON CleanedData(CustomerID);
CREATE INDEX IX_CleanedData_ProductID ON CleanedData(ProductID);
CREATE INDEX IX_CleanedData_OrderDate ON CleanedData(OrderDate);
CREATE INDEX IX_CleanedData_OrderYear ON CleanedData(OrderYear);
CREATE INDEX IX_CleanedData_Category ON CleanedData(Category);
CREATE INDEX IX_CleanedData_Region ON CleanedData(Region);
GO

-- ============================================================================
-- 3. CUSTOMERS TABLE
-- ============================================================================
-- One row per customer with aggregated metrics
-- ============================================================================

CREATE TABLE Customers (
    CustomerID       VARCHAR(50) PRIMARY KEY,
    CustomerName     VARCHAR(200) NOT NULL,
    Segment          VARCHAR(100),
    FirstOrderDate   DATE,
    LastOrderDate    DATE,
    TotalOrders      INT DEFAULT 0,
    TotalSales       DECIMAL(18,2) DEFAULT 0,
    TotalProfit      DECIMAL(18,2) DEFAULT 0,

    CONSTRAINT CHK_Customers_TotalOrders CHECK (TotalOrders >= 0),
    CONSTRAINT CHK_Customers_TotalSales CHECK (TotalSales >= 0)
);

CREATE INDEX IX_Customers_Segment ON Customers(Segment);
CREATE INDEX IX_Customers_FirstOrderDate ON Customers(FirstOrderDate);
GO

-- ============================================================================
-- 4. PRODUCTS TABLE
-- ============================================================================
-- Distinct products from the dataset
-- ============================================================================

CREATE TABLE Products (
    ProductID     VARCHAR(50) PRIMARY KEY,
    ProductName   VARCHAR(500) NOT NULL,
    Category      VARCHAR(100) NOT NULL,
    SubCategory   VARCHAR(100) NOT NULL
);

CREATE INDEX IX_Products_Category ON Products(Category);
CREATE INDEX IX_Products_SubCategory ON Products(SubCategory);
GO

-- ============================================================================
-- 5. ORDERS TABLE
-- ============================================================================
-- One row per order (header level)
-- ============================================================================

CREATE TABLE Orders (
    OrderID        VARCHAR(50) PRIMARY KEY,
    OrderDate      DATE NOT NULL,
    ShipDate       DATE,
    ShipMode       VARCHAR(100),
    CustomerID     VARCHAR(50),
    Segment        VARCHAR(100),
    Market         VARCHAR(100),
    Region         VARCHAR(100),
    OrderPriority  VARCHAR(50),

    CONSTRAINT FK_Orders_CustomerID FOREIGN KEY (CustomerID) 
        REFERENCES Customers(CustomerID) ON DELETE SET NULL
);

CREATE INDEX IX_Orders_OrderDate ON Orders(OrderDate);
CREATE INDEX IX_Orders_CustomerID ON Orders(CustomerID);
CREATE INDEX IX_Orders_Region ON Orders(Region);
CREATE INDEX IX_Orders_Market ON Orders(Market);
GO

-- ============================================================================
-- 6. ORDER DETAILS TABLE
-- ============================================================================
-- Line items within each order
-- ============================================================================

CREATE TABLE OrderDetails (
    OrderDetailID   INT IDENTITY(1,1) PRIMARY KEY,
    OrderID         VARCHAR(50) NOT NULL,
    ProductID       VARCHAR(50) NOT NULL,
    Sales           DECIMAL(18,2),
    Quantity        INT,
    Discount        DECIMAL(5,4),
    Profit          DECIMAL(18,2),
    ShippingCost    DECIMAL(18,2),

    CONSTRAINT FK_OrderDetails_OrderID FOREIGN KEY (OrderID) 
        REFERENCES Orders(OrderID) ON DELETE CASCADE,
    CONSTRAINT FK_OrderDetails_ProductID FOREIGN KEY (ProductID) 
        REFERENCES Products(ProductID) ON DELETE RESTRICT,
    CONSTRAINT CHK_OrderDetails_Sales CHECK (Sales >= 0),
    CONSTRAINT CHK_OrderDetails_Quantity CHECK (Quantity > 0),
    CONSTRAINT CHK_OrderDetails_Discount CHECK (Discount >= 0 AND Discount <= 1),
    CONSTRAINT CHK_OrderDetails_ShippingCost CHECK (ShippingCost >= 0)
);

CREATE INDEX IX_OrderDetails_OrderID ON OrderDetails(OrderID);
CREATE INDEX IX_OrderDetails_ProductID ON OrderDetails(ProductID);
GO

-- ============================================================================
-- 7. GEOGRAPHY TABLE
-- ============================================================================
-- Distinct geographic combinations
-- ============================================================================

CREATE TABLE Geography (
    GeographyID   INT IDENTITY(1,1) PRIMARY KEY,
    Country       VARCHAR(200) NOT NULL,
    State         VARCHAR(200) NOT NULL,
    City          VARCHAR(200) NOT NULL,
    PostalCode    VARCHAR(50),
    Market        VARCHAR(100) NOT NULL,
    Region        VARCHAR(100) NOT NULL,

    CONSTRAINT UQ_Geography UNIQUE (Country, State, City, PostalCode, Market, Region)
);

CREATE INDEX IX_Geography_Region ON Geography(Region);
CREATE INDEX IX_Geography_Market ON Geography(Market);
GO

-- ============================================================================
-- 8. DATA QUALITY LOG TABLE
-- ============================================================================
-- Tracks all data quality checks and actions taken
-- ============================================================================

CREATE TABLE DataQualityLog (
    LogID         INT IDENTITY(1,1) PRIMARY KEY,
    CheckDate     DATETIME DEFAULT GETDATE(),
    CheckType     VARCHAR(100) NOT NULL,        -- e.g., 'Null Check', 'Duplicate Check'
    ColumnName    VARCHAR(100),                 -- NULL if table-level check
    IssueType     VARCHAR(200) NOT NULL,        -- e.g., 'NULL', 'Duplicate', 'Outlier'
    IssueCount    INT NOT NULL,
    Severity      VARCHAR(20) NOT NULL,         -- 'High', 'Medium', 'Low'
    ActionTaken   VARCHAR(500)                  -- e.g., 'Flagged', 'Imputed', 'Excluded'
);

CREATE INDEX IX_DataQualityLog_CheckDate ON DataQualityLog(CheckDate);
CREATE INDEX IX_DataQualityLog_CheckType ON DataQualityLog(CheckType);
GO

-- ============================================================================
-- 9. ANALYTICS SUMMARY TABLE
-- ============================================================================
-- Stores computed metrics for dashboard/reporting
-- ============================================================================

CREATE TABLE AnalyticsSummary (
    SummaryID       INT IDENTITY(1,1) PRIMARY KEY,
    MetricName      VARCHAR(200) NOT NULL,
    MetricValue     DECIMAL(18,4) NOT NULL,
    Period          VARCHAR(50),                -- e.g., '2024-01', 'Q1-2024', '2024'
    Category        VARCHAR(100),               -- e.g., 'Sales', 'Profit', 'Customers'
    GeneratedDate   DATETIME DEFAULT GETDATE()
);

CREATE INDEX IX_AnalyticsSummary_MetricName ON AnalyticsSummary(MetricName);
CREATE INDEX IX_AnalyticsSummary_Period ON AnalyticsSummary(Period);
GO

-- ============================================================================
-- 10. METADATA TABLE (for data lineage)
-- ============================================================================

CREATE TABLE TableMetadata (
    TableName       VARCHAR(200) PRIMARY KEY,
    Description     VARCHAR(1000),
    SourceTable     VARCHAR(200),
    CreatedDate     DATETIME DEFAULT GETDATE(),
    CreatedBy       VARCHAR(100) DEFAULT SYSTEM_USER,
    RowCount        INT,
    LastUpdated     DATETIME
);

CREATE TABLE ColumnMetadata (
    ColumnID        INT IDENTITY(1,1) PRIMARY KEY,
    TableName       VARCHAR(200) NOT NULL,
    ColumnName      VARCHAR(200) NOT NULL,
    DataType        VARCHAR(100),
    IsNullable      BIT,
    Description     VARCHAR(500),
    SourceColumn    VARCHAR(200),
    Transformation  VARCHAR(500),

    CONSTRAINT UQ_ColumnMetadata UNIQUE (TableName, ColumnName)
);

CREATE INDEX IX_ColumnMetadata_TableName ON ColumnMetadata(TableName);
GO

PRINT 'Schema created successfully.';
GO

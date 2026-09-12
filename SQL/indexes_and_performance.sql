-- ============================================================================
-- INDEXES AND PERFORMANCE OPTIMIZATION
-- ============================================================================
-- Index creation for fact tables and performance tuning
-- ============================================================================

USE SalesAnalysisDB;
GO

-- ============================================================================
-- 1. INDEXES FOR CLEANEDDATA (Primary fact table)
-- ============================================================================

-- Composite index for common filter patterns (Date + Category)
CREATE NONCLUSTERED INDEX IX_CleanedData_OrderDate_Category
ON CleanedData (OrderDate)
INCLUDE (Category, SubCategory, Sales, Profit, Quantity, Discount);
GO

-- Composite index for region-based queries
CREATE NONCLUSTERED INDEX IX_CleanedData_Region_OrderDate
ON CleanedData (Region, OrderDate)
INCLUDE (Sales, Profit, CustomerID, ProductID);
GO

-- Composite index for customer analysis
CREATE NONCLUSTERED INDEX IX_CleanedData_CustomerID_OrderDate
ON CleanedData (CustomerID, OrderDate)
INCLUDE (Sales, Profit, ProductID);
GO

-- Composite index for product analysis
CREATE NONCLUSTERED INDEX IX_CleanedData_ProductID_OrderDate
ON CleanedData (ProductID, OrderDate)
INCLUDE (Sales, Profit, Quantity, Discount);
GO

-- Index for segment analysis
CREATE NONCLUSTERED INDEX IX_CleanedData_Segment
ON CleanedData (Segment)
INCLUDE (Sales, Profit, OrderID, CustomerID);
GO

-- Index for market analysis
CREATE NONCLUSTERED INDEX IX_CleanedData_Market
ON CleanedData (Market)
INCLUDE (Sales, Profit, Region, OrderDate);
GO

-- Index for ship mode analysis
CREATE NONCLUSTERED INDEX IX_CleanedData_ShipMode
ON CleanedData (ShipMode)
INCLUDE (Sales, Profit, ShippingDays, ShippingCost);
GO

-- Covering index for discount analysis
CREATE NONCLUSTERED INDEX IX_CleanedData_DiscountBand
ON CleanedData (DiscountBand)
INCLUDE (Sales, Profit, Category, Discount);
GO

-- ============================================================================
-- 2. INDEXES FOR ORDERDETAILS (Line item fact table)
-- ============================================================================

-- Composite index for order-product joins
CREATE NONCLUSTERED INDEX IX_OrderDetails_OrderID_ProductID
ON OrderDetails (OrderID, ProductID)
INCLUDE (Sales, Quantity, Discount, Profit, ShippingCost);
GO

-- Index for product performance queries
CREATE NONCLUSTERED INDEX IX_OrderDetails_ProductID
ON OrderDetails (ProductID)
INCLUDE (OrderID, Sales, Profit, Quantity);
GO

-- Index for sales analysis
CREATE NONCLUSTERED INDEX IX_OrderDetails_Sales
ON OrderDetails (Sales DESC)
INCLUDE (OrderID, ProductID, Profit, Quantity);
GO

-- ============================================================================
-- 3. INDEXES FOR CUSTOMERS
-- ============================================================================

-- Index for customer lookups
CREATE NONCLUSTERED INDEX IX_Customers_Segment_TotalSales
ON Customers (Segment)
INCLUDE (CustomerName, TotalOrders, TotalSales, TotalProfit, FirstOrderDate, LastOrderDate);
GO

-- Index for top customer queries
CREATE NONCLUSTERED INDEX IX_Customers_TotalSales
ON Customers (TotalSales DESC)
INCLUDE (CustomerName, Segment, TotalProfit);
GO

-- ============================================================================
-- 4. INDEXES FOR ORDERS
-- ============================================================================

-- Composite index for order date range queries
CREATE NONCLUSTERED INDEX IX_Orders_OrderDate_CustomerID
ON Orders (OrderDate, CustomerID)
INCLUDE (ShipMode, Segment, Region, Market, OrderPriority);
GO

-- Index for region-based order queries
CREATE NONCLUSTERED INDEX IX_Orders_Region_OrderDate
ON Orders (Region, OrderDate)
INCLUDE (Sales, CustomerID, ShipMode);
GO

-- ============================================================================
-- 5. INDEXES FOR PRODUCTS
-- ============================================================================

-- Index for category-subcategory lookups
CREATE NONCLUSTERED INDEX IX_Products_Category_SubCategory
ON Products (Category, SubCategory)
INCLUDE (ProductName);
GO

-- ============================================================================
-- 6. INDEXES FOR GEOGRAPHY
-- ============================================================================

-- Index for regional lookups
CREATE NONCLUSTERED INDEX IX_Geography_Region_Country
ON Geography (Region, Country)
INCLUDE (State, City, Market);
GO

-- Index for market analysis
CREATE NONCLUSTERED INDEX IX_Geography_Market_Region
ON Geography (Market, Region)
INCLUDE (Country, State, City);
GO

-- ============================================================================
-- 7. INDEXES FOR ANALYTICSSUMMARY
-- ============================================================================

-- Index for time-based summary queries
CREATE NONCLUSTERED INDEX IX_AnalyticsSummary_Period_MetricName
ON AnalyticsSummary (Period, MetricName)
INCLUDE (MetricValue, Category);
GO

-- ============================================================================
-- 8. INDEXED VIEWS (Materialized views for performance)
-- ============================================================================
-- Note: Indexed views require specific settings in SQL Server
-- SCHEMABINDING, ANSI_NULLS, QUOTED_IDENTIFIER, etc.

-- 8.1 Monthly Sales Summary (Indexed View)
-- This view pre-aggregates monthly sales for faster dashboard queries

IF OBJECT_ID('mv_MonthlySales', 'V') IS NOT NULL
    DROP VIEW mv_MonthlySales;
GO

-- Enable required settings for indexed views
SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

CREATE VIEW mv_MonthlySales
WITH SCHEMABINDING
AS
SELECT 
    OrderYear,
    OrderMonth,
    COUNT_BIG(*) AS TransactionCount,
    COUNT_BIG(DISTINCT OrderID) AS OrderCount,
    COUNT_BIG(DISTINCT CustomerID) AS CustomerCount,
    SUM(Sales) AS TotalSales,
    SUM(Profit) AS TotalProfit,
    SUM(Quantity) AS TotalQuantity,
    AVG(Discount) AS AvgDiscount
FROM dbo.CleanedData
GROUP BY OrderYear, OrderMonth;
GO

-- Create clustered index on the view
CREATE UNIQUE CLUSTERED INDEX IX_mv_MonthlySales
ON mv_MonthlySales (OrderYear, OrderMonth);
GO

-- ============================================================================
-- 9. PARTITIONING STRATEGY
-- ============================================================================
-- Partition CleanedData by OrderYear for improved query performance
-- This is particularly useful for large datasets and time-range queries

-- Note: Partitioning requires:
-- 1. A partition function
-- 2. A partition scheme
-- 3. Rebuilding the table on the partition scheme

-- Create partition function (partition by year)
-- CREATE PARTITION FUNCTION pf_OrderYear (INT)
-- AS RANGE RIGHT FOR VALUES (2015, 2016, 2017, 2018, 2019);

-- Create partition scheme
-- CREATE PARTITION SCHEME ps_OrderYear
-- AS PARTITION pf_OrderYear
-- ALL TO ([PRIMARY]);

-- To partition CleanedData, you would:
-- 1. Drop the current clustered index (if exists)
-- 2. Create a new clustered index on the partition scheme
-- 
-- CREATE CLUSTERED INDEX IX_CleanedData_Partitioned
-- ON CleanedData (OrderYear, OrderID)
-- ON ps_OrderYear(OrderYear);
--
-- Benefits:
-- - Faster queries filtering by date ranges
-- - Easier data archival (switch partitions)
-- - Improved maintenance operations

-- ============================================================================
-- 10. PERFORMANCE MONITORING QUERIES
-- ============================================================================

-- Check index usage and fragmentation
SELECT 
    OBJECT_NAME(ips.object_id) AS TableName,
    i.name AS IndexName,
    i.type_desc AS IndexType,
    ips.user_seeks,
    ips.user_scans,
    ips.user_lookups,
    ips.user_updates,
    ips.avg_fragmentation_in_percent
FROM sys.dm_db_index_usage_stats ips
JOIN sys.indexes i ON ips.object_id = i.object_id AND ips.index_id = i.index_id
WHERE OBJECT_NAME(ips.object_id) IN ('CleanedData', 'OrderDetails', 'Customers', 'Orders', 'Products')
ORDER BY ips.user_seeks DESC;
GO

-- Check table sizes
SELECT 
    OBJECT_NAME(s.object_id) AS TableName,
    s.name AS SchemaName,
    p.rows AS RowCounts,
    p.data_compression_desc AS Compression,
    a.total_pages * 8 / 1024.0 AS TotalSpaceMB,
    a.used_pages * 8 / 1024.0 AS UsedSpaceMB
FROM sys.tables s
JOIN sys.indexes i ON s.object_id = i.object_id AND i.index_id < 2
JOIN sys.partitions p ON s.object_id = p.object_id AND i.index_id = p.index_id
JOIN sys.allocation_units a ON p.partition_id = a.container_id
ORDER BY TotalSpaceMB DESC;
GO

-- Missing index suggestions
SELECT 
    migs.avg_total_user_cost * migs.avg_user_impact * (migs.user_seeks + migs.user_scans) AS ImprovementScore,
    OBJECT_NAME(mid.object_id) AS TableName,
    mid.statement AS TableQuery,
    mid.equality_columns,
    mid.inequality_columns,
    mid.included_columns
FROM sys.dm_db_missing_index_group_stats migs
JOIN sys.dm_db_missing_index_groups mig ON migs.group_handle = mig.index_group_handle
JOIN sys.dm_db_missing_index_details mid ON mig.index_handle = mid.index_handle
WHERE OBJECT_NAME(mid.object_id) IN ('CleanedData', 'OrderDetails', 'Customers', 'Orders')
ORDER BY ImprovementScore DESC;
GO

-- Update statistics on all indexed tables
UPDATE STATISTICS CleanedData WITH FULLSCAN, ALL;
UPDATE STATISTICS OrderDetails WITH FULLSCAN, ALL;
UPDATE STATISTICS Customers WITH FULLSCAN, ALL;
UPDATE STATISTICS Orders WITH FULLSCAN, ALL;
UPDATE STATISTICS Products WITH FULLSCAN, ALL;
GO

PRINT 'Indexes and performance optimization completed.';
GO

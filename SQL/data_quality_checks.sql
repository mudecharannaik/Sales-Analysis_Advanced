-- ============================================================================
-- DATA QUALITY CHECKS
-- ============================================================================
-- Comprehensive data quality analysis for the Superstore dataset
-- ============================================================================

USE SalesAnalysisDB;
GO

-- ============================================================================
-- HELPER: Calculate Data Quality Score
-- ============================================================================

-- Overall data quality score (0-100)
-- Based on completeness, validity, and uniqueness

DECLARE @TotalRows INT = (SELECT COUNT(*) FROM RawData);
DECLARE @NullScore INT;
DECLARE @ValidityScore INT;
DECLARE @UniquenessScore INT;
DECLARE @OverallScore INT;

-- Null Score: percentage of non-null values across all columns
SELECT @NullScore = 
    CAST(100.0 * (
        (SELECT COUNT(*) FROM RawData WHERE RowID IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE OrderID IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE OrderDate IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE ShipDate IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE ShipMode IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE CustomerID IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE CustomerName IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE Segment IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE City IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE State IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE Country IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE Market IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE Region IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE ProductID IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE Category IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE SubCategory IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE ProductName IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE Sales IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE Quantity IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE Discount IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE Profit IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE ShippingCost IS NOT NULL) +
        (SELECT COUNT(*) FROM RawData WHERE OrderPriority IS NOT NULL)
    ) / (24.0 * @TotalRows) AS INT);

-- Validity Score: check business rules
SELECT @ValidityScore = 
    CAST(100.0 * (
        (SELECT COUNT(*) FROM RawData WHERE Sales >= 0 OR Sales IS NULL) +
        (SELECT COUNT(*) FROM RawData WHERE Quantity > 0 OR Quantity IS NULL) +
        (SELECT COUNT(*) FROM RawData WHERE Discount >= 0 AND Discount <= 1 OR Discount IS NULL) +
        (SELECT COUNT(*) FROM RawData WHERE ShippingCost >= 0 OR ShippingCost IS NULL) +
        (SELECT COUNT(*) FROM RawData WHERE 
            TRY_CONVERT(DATE, OrderDate, 101) IS NOT NULL OR OrderDate IS NULL)
    ) / (5.0 * @TotalRows) AS INT);

-- Uniqueness Score: check for duplicate RowIDs
SELECT @UniquenessScore = 
    CAST(100.0 * 
        (SELECT COUNT(DISTINCT RowID) FROM RawData) / @TotalRows AS INT);

SET @OverallScore = (@NullScore + @ValidityScore + @UniquenessScore) / 3;

INSERT INTO DataQualityLog (CheckType, ColumnName, IssueType, IssueCount, Severity, ActionTaken)
VALUES 
    ('Overall Score', NULL, 'Data Quality Score', @OverallScore, 
     CASE WHEN @OverallScore >= 90 THEN 'Low'
          WHEN @OverallScore >= 70 THEN 'Medium'
          ELSE 'High' END,
     'Calculated from null, validity, and uniqueness scores');

SELECT 
    'Data Quality Score' AS Metric,
    @OverallScore AS Score,
    @NullScore AS CompletenessScore,
    @ValidityScore AS ValidityScore,
    @UniquenessScore AS UniquenessScore;
GO

-- ============================================================================
-- 1. DUPLICATE DETECTION
-- ============================================================================

-- 1.1 Exact duplicates on RowID (primary key - should be 0)
SELECT 
    'RowID Duplicates' AS CheckName,
    COUNT(*) AS DuplicateCount
FROM RawData
GROUP BY RowID
HAVING COUNT(*) > 1;
GO

-- 1.2 Duplicate Order IDs
SELECT 
    'OrderID Duplicates' AS CheckName,
    OrderID,
    COUNT(*) AS OccurrenceCount
FROM RawData
GROUP BY OrderID
HAVING COUNT(*) > 1
ORDER BY OccurrenceCount DESC;
GO

-- 1.3 Duplicate Customer IDs
SELECT 
    'CustomerID Duplicates' AS CheckName,
    CustomerID,
    COUNT(*) AS OccurrenceCount
FROM RawData
GROUP BY CustomerID
HAVING COUNT(*) > 1
ORDER BY OccurrenceCount DESC;
GO

-- 1.4 Duplicate Product IDs
SELECT 
    'ProductID Duplicates' AS CheckName,
    ProductID,
    COUNT(*) AS OccurrenceCount
FROM RawData
GROUP BY ProductID
HAVING COUNT(*) > 1
ORDER BY OccurrenceCount DESC;
GO

-- 1.5 Full row duplicates (all columns)
SELECT 
    COUNT(*) AS FullRowDuplicates
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY 
                   OrderID, OrderDate, ShipDate, ShipMode, CustomerID, CustomerName,
                   Segment, City, State, Country, PostalCode, Market, Region,
                   ProductID, Category, SubCategory, ProductName, Sales, Quantity,
                   Discount, Profit, ShippingCost, OrderPriority
               ORDER BY RowID
           ) AS rn
    FROM RawData
) t
WHERE rn > 1;
GO

-- ============================================================================
-- 2. NULL VALUE ANALYSIS
-- ============================================================================

-- Null analysis for all columns with counts and percentages
SELECT 
    'RowID' AS ColumnName, 
    COUNT(*) - COUNT(RowID) AS NullCount,
    CAST(100.0 * (COUNT(*) - COUNT(RowID)) / COUNT(*) AS DECIMAL(5,2)) AS NullPercentage
FROM RawData
UNION ALL
SELECT 
    'OrderID', 
    COUNT(*) - COUNT(OrderID),
    CAST(100.0 * (COUNT(*) - COUNT(OrderID)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'OrderDate', 
    COUNT(*) - COUNT(OrderDate),
    CAST(100.0 * (COUNT(*) - COUNT(OrderDate)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'ShipDate', 
    COUNT(*) - COUNT(ShipDate),
    CAST(100.0 * (COUNT(*) - COUNT(ShipDate)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'ShipMode', 
    COUNT(*) - COUNT(ShipMode),
    CAST(100.0 * (COUNT(*) - COUNT(ShipMode)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'CustomerID', 
    COUNT(*) - COUNT(CustomerID),
    CAST(100.0 * (COUNT(*) - COUNT(CustomerID)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'CustomerName', 
    COUNT(*) - COUNT(CustomerName),
    CAST(100.0 * (COUNT(*) - COUNT(CustomerName)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'Segment', 
    COUNT(*) - COUNT(Segment),
    CAST(100.0 * (COUNT(*) - COUNT(Segment)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'City', 
    COUNT(*) - COUNT(City),
    CAST(100.0 * (COUNT(*) - COUNT(City)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'State', 
    COUNT(*) - COUNT(State),
    CAST(100.0 * (COUNT(*) - COUNT(State)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'Country', 
    COUNT(*) - COUNT(Country),
    CAST(100.0 * (COUNT(*) - COUNT(Country)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'PostalCode', 
    COUNT(*) - COUNT(PostalCode),
    CAST(100.0 * (COUNT(*) - COUNT(PostalCode)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'Market', 
    COUNT(*) - COUNT(Market),
    CAST(100.0 * (COUNT(*) - COUNT(Market)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'Region', 
    COUNT(*) - COUNT(Region),
    CAST(100.0 * (COUNT(*) - COUNT(Region)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'ProductID', 
    COUNT(*) - COUNT(ProductID),
    CAST(100.0 * (COUNT(*) - COUNT(ProductID)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'Category', 
    COUNT(*) - COUNT(Category),
    CAST(100.0 * (COUNT(*) - COUNT(Category)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'SubCategory', 
    COUNT(*) - COUNT(SubCategory),
    CAST(100.0 * (COUNT(*) - COUNT(SubCategory)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'ProductName', 
    COUNT(*) - COUNT(ProductName),
    CAST(100.0 * (COUNT(*) - COUNT(ProductName)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'Sales', 
    COUNT(*) - COUNT(Sales),
    CAST(100.0 * (COUNT(*) - COUNT(Sales)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'Quantity', 
    COUNT(*) - COUNT(Quantity),
    CAST(100.0 * (COUNT(*) - COUNT(Quantity)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'Discount', 
    COUNT(*) - COUNT(Discount),
    CAST(100.0 * (COUNT(*) - COUNT(Discount)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'Profit', 
    COUNT(*) - COUNT(Profit),
    CAST(100.0 * (COUNT(*) - COUNT(Profit)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'ShippingCost', 
    COUNT(*) - COUNT(ShippingCost),
    CAST(100.0 * (COUNT(*) - COUNT(ShippingCost)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
UNION ALL
SELECT 
    'OrderPriority', 
    COUNT(*) - COUNT(OrderPriority),
    CAST(100.0 * (COUNT(*) - COUNT(OrderPriority)) / COUNT(*) AS DECIMAL(5,2))
FROM RawData
ORDER BY NullPercentage DESC;
GO

-- ============================================================================
-- 3. OUTLIER DETECTION - Z-SCORE METHOD
-- ============================================================================
-- Flag values more than 3 standard deviations from mean

-- 3.1 Sales outliers (Z-Score > 3)
WITH SalesStats AS (
    SELECT 
        AVG(CAST(Sales AS FLOAT)) AS MeanSales,
        STDEV(CAST(Sales AS FLOAT)) AS StdSales
    FROM RawData
    WHERE Sales IS NOT NULL
)
SELECT 
    'Sales Outliers (Z-Score > 3)' AS CheckName,
    r.RowID,
    r.OrderID,
    r.Sales,
    s.MeanSales,
    s.StdSales,
    ABS(CAST(r.Sales AS FLOAT) - s.MeanSales) / NULLIF(s.StdSales, 0) AS ZScore
FROM RawData r
CROSS JOIN SalesStats s
WHERE ABS(CAST(r.Sales AS FLOAT) - s.MeanSales) / NULLIF(s.StdSales, 0) > 3;
GO

-- 3.2 Profit outliers (Z-Score > 3)
WITH ProfitStats AS (
    SELECT 
        AVG(CAST(Profit AS FLOAT)) AS MeanProfit,
        STDEV(CAST(Profit AS FLOAT)) AS StdProfit
    FROM RawData
    WHERE Profit IS NOT NULL
)
SELECT 
    'Profit Outliers (Z-Score > 3)' AS CheckName,
    r.RowID,
    r.OrderID,
    r.Profit,
    p.MeanProfit,
    p.StdProfit,
    ABS(CAST(r.Profit AS FLOAT) - p.MeanProfit) / NULLIF(p.StdProfit, 0) AS ZScore
FROM RawData r
CROSS JOIN ProfitStats p
WHERE ABS(CAST(r.Profit AS FLOAT) - p.MeanProfit) / NULLIF(p.StdProfit, 0) > 3;
GO

-- 3.3 Quantity outliers (Z-Score > 3)
WITH QtyStats AS (
    SELECT 
        AVG(CAST(Quantity AS FLOAT)) AS MeanQty,
        STDEV(CAST(Quantity AS FLOAT)) AS StdQty
    FROM RawData
    WHERE Quantity IS NOT NULL
)
SELECT 
    'Quantity Outliers (Z-Score > 3)' AS CheckName,
    r.RowID,
    r.OrderID,
    r.Quantity,
    q.MeanQty,
    q.StdQty,
    ABS(CAST(r.Quantity AS FLOAT) - q.MeanQty) / NULLIF(q.StdQty, 0) AS ZScore
FROM RawData r
CROSS JOIN QtyStats q
WHERE ABS(CAST(r.Quantity AS FLOAT) - q.MeanQty) / NULLIF(q.StdQty, 0) > 3;
GO

-- ============================================================================
-- 4. OUTLIER DETECTION - IQR METHOD (1.5 * IQR)
-- ============================================================================

-- 4.1 Sales outliers using IQR
WITH SalesQuartiles AS (
    SELECT 
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY CAST(Sales AS FLOAT)) AS Q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY CAST(Sales AS FLOAT)) AS Q3
    FROM RawData
    WHERE Sales IS NOT NULL
),
SalesIQR AS (
    SELECT 
        Q1,
        Q3,
        Q3 - Q1 AS IQR,
        Q1 - 1.5 * (Q3 - Q1) AS LowerFence,
        Q3 + 1.5 * (Q3 - Q1) AS UpperFence
    FROM SalesQuartiles
)
SELECT 
    'Sales Outliers (IQR Method)' AS CheckName,
    r.RowID,
    r.OrderID,
    r.Sales,
    i.LowerFence,
    i.UpperFence
FROM RawData r
CROSS JOIN SalesIQR i
WHERE r.Sales < i.LowerFence OR r.Sales > i.UpperFence;
GO

-- 4.2 Profit outliers using IQR
WITH ProfitQuartiles AS (
    SELECT 
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY CAST(Profit AS FLOAT)) AS Q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY CAST(Profit AS FLOAT)) AS Q3
    FROM RawData
    WHERE Profit IS NOT NULL
),
ProfitIQR AS (
    SELECT 
        Q1,
        Q3,
        Q3 - Q1 AS IQR,
        Q1 - 1.5 * (Q3 - Q1) AS LowerFence,
        Q3 + 1.5 * (Q3 - Q1) AS UpperFence
    FROM ProfitQuartiles
)
SELECT 
    'Profit Outliers (IQR Method)' AS CheckName,
    r.RowID,
    r.OrderID,
    r.Profit,
    i.LowerFence,
    i.UpperFence
FROM RawData r
CROSS JOIN ProfitIQR i
WHERE r.Profit < i.LowerFence OR r.Profit > i.UpperFence;
GO

-- ============================================================================
-- 5. REFERENTIAL INTEGRITY CHECKS
-- ============================================================================

-- Check for orphaned records in CleanedData (if it exists)
-- CleanedData.OrderID should exist in Orders (after ETL)
-- CleanedData.ProductID should exist in Products (after ETL)
-- CleanedData.CustomerID should exist in Customers (after ETL)

-- Pre-ETL: Check if foreign key values exist in source
-- OrderIDs in RawData
SELECT DISTINCT OrderID INTO #TempOrderIDs FROM RawData WHERE OrderID IS NOT NULL;

-- Check if any OrderID appears with conflicting CustomerID
SELECT 
    'Conflicting Customer per Order' AS CheckName,
    OrderID,
    COUNT(DISTINCT CustomerID) AS CustomerCount
FROM RawData
WHERE OrderID IS NOT NULL
GROUP BY OrderID
HAVING COUNT(DISTINCT CustomerID) > 1;
GO

-- Check if any OrderID appears with conflicting dates
SELECT 
    'Conflicting Dates per Order' AS CheckName,
    OrderID,
    COUNT(DISTINCT OrderDate) AS DateCount
FROM RawData
WHERE OrderID IS NOT NULL
GROUP BY OrderID
HAVING COUNT(DISTINCT OrderDate) > 1;
GO

-- ============================================================================
-- 6. BUSINESS RULE VALIDATIONS
-- ============================================================================

-- 6.1 Sales must be >= 0
INSERT INTO DataQualityLog (CheckType, ColumnName, IssueType, IssueCount, Severity, ActionTaken)
SELECT 
    'Business Rule', 'Sales', 'Sales < 0',
    COUNT(*), 'High',
    'Excluded from analysis - invalid sales value'
FROM RawData
WHERE Sales < 0;
GO

-- 6.2 Profit can be negative but not NULL (or document NULLs)
INSERT INTO DataQualityLog (CheckType, ColumnName, IssueType, IssueCount, Severity, ActionTaken)
SELECT 
    'Business Rule', 'Profit', 'NULL Profit',
    COUNT(*), 'Medium',
    'Flagged - profit is NULL'
FROM RawData
WHERE Profit IS NULL;
GO

-- 6.3 Discount must be between 0 and 1
INSERT INTO DataQualityLog (CheckType, ColumnName, IssueType, IssueCount, Severity, ActionTaken)
SELECT 
    'Business Rule', 'Discount', 'Discount outside [0,1]',
    COUNT(*), 'High',
    'Capped to valid range [0,1]'
FROM RawData
WHERE Discount < 0 OR Discount > 1;
GO

-- 6.4 Quantity must be > 0
INSERT INTO DataQualityLog (CheckType, ColumnName, IssueType, IssueCount, Severity, ActionTaken)
SELECT 
    'Business Rule', 'Quantity', 'Quantity <= 0',
    COUNT(*), 'High',
    'Excluded from analysis - invalid quantity'
FROM RawData
WHERE Quantity <= 0;
GO

-- 6.5 Ship Date must be >= Order Date
INSERT INTO DataQualityLog (CheckType, ColumnName, IssueType, IssueCount, Severity, ActionTaken)
SELECT 
    'Business Rule', 'ShipDate', 'ShipDate < OrderDate',
    COUNT(*), 'High',
    'Flagged - shipping date before order date'
FROM RawData
WHERE TRY_CONVERT(DATE, ShipDate, 101) IS NOT NULL
  AND TRY_CONVERT(DATE, OrderDate, 101) IS NOT NULL
  AND TRY_CONVERT(DATE, ShipDate, 101) < TRY_CONVERT(DATE, OrderDate, 101);
GO

-- 6.6 Shipping Cost must be >= 0
INSERT INTO DataQualityLog (CheckType, ColumnName, IssueType, IssueCount, Severity, ActionTaken)
SELECT 
    'Business Rule', 'ShippingCost', 'ShippingCost < 0',
    COUNT(*), 'High',
    'Set to 0 - negative shipping cost invalid'
FROM RawData
WHERE ShippingCost < 0;
GO

-- ============================================================================
-- 7. DATA TYPE VALIDATION
-- ============================================================================

-- Check if numeric columns contain non-numeric values
SELECT 
    'Sales Non-Numeric' AS CheckName,
    COUNT(*) AS IssueCount
FROM RawData
WHERE Sales IS NOT NULL
  AND TRY_CONVERT(DECIMAL(18,2), Sales) IS NULL;
GO

SELECT 
    'Quantity Non-Numeric' AS CheckName,
    COUNT(*) AS IssueCount
FROM RawData
WHERE Quantity IS NOT NULL
  AND TRY_CONVERT(INT, Quantity) IS NULL;
GO

SELECT 
    'Discount Non-Numeric' AS CheckName,
    COUNT(*) AS IssueCount
FROM RawData
WHERE Discount IS NOT NULL
  AND TRY_CONVERT(DECIMAL(5,4), Discount) IS NULL;
GO

-- ============================================================================
-- 8. CARDINALITY CHECKS
-- ============================================================================

-- Distinct counts for key dimensions
SELECT 
    'Distinct OrderIDs' AS Dimension,
    COUNT(DISTINCT OrderID) AS DistinctCount
FROM RawData
UNION ALL
SELECT 
    'Distinct CustomerIDs',
    COUNT(DISTINCT CustomerID)
FROM RawData
UNION ALL
SELECT 
    'Distinct ProductIDs',
    COUNT(DISTINCT ProductID)
FROM RawData
UNION ALL
SELECT 
    'Distinct Categories',
    COUNT(DISTINCT Category)
FROM RawData
UNION ALL
SELECT 
    'Distinct SubCategories',
    COUNT(DISTINCT SubCategory)
FROM RawData
UNION ALL
SELECT 
    'Distinct Segments',
    COUNT(DISTINCT Segment)
FROM RawData
UNION ALL
SELECT 
    'Distinct Regions',
    COUNT(DISTINCT Region)
FROM RawData
UNION ALL
SELECT 
    'Distinct Markets',
    COUNT(DISTINCT Market)
FROM RawData
UNION ALL
SELECT 
    'Distinct ShipModes',
    COUNT(DISTINCT ShipMode)
FROM RawData
UNION ALL
SELECT 
    'Distinct OrderPriorities',
    COUNT(DISTINCT OrderPriority)
FROM RawData;
GO

-- ============================================================================
-- 9. DATA QUALITY SUMMARY REPORT
-- ============================================================================

SELECT 
    'Quality Summary' AS ReportSection,
    (SELECT COUNT(*) FROM RawData) AS TotalRows,
    (SELECT COUNT(*) FROM DataQualityLog WHERE Severity = 'High') AS HighIssues,
    (SELECT COUNT(*) FROM DataQualityLog WHERE Severity = 'Medium') AS MediumIssues,
    (SELECT COUNT(*) FROM DataQualityLog WHERE Severity = 'Low') AS LowIssues,
    @OverallScore AS OverallScore
UNION ALL
SELECT 
    'Null Summary',
    COUNT(*),
    SUM(CASE WHEN ColumnName IS NOT NULL AND IssueType = 'NULL Values' AND Severity = 'High' THEN 1 ELSE 0 END),
    SUM(CASE WHEN ColumnName IS NOT NULL AND IssueType = 'NULL Values' AND Severity = 'Medium' THEN 1 ELSE 0 END),
    SUM(CASE WHEN ColumnName IS NOT NULL AND IssueType = 'NULL Values' AND Severity = 'Low' THEN 1 ELSE 0 END),
    NULL
FROM DataQualityLog;
GO

PRINT 'Data quality checks completed.';
GO

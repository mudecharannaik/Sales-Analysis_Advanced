-- ============================================================================
-- EXPLORATORY DATA ANALYSIS
-- ============================================================================
-- Initial exploration of the Superstore Sales dataset
-- ============================================================================

USE SalesAnalysisDB;
GO

-- ============================================================================
-- 1. SALES BY DIMENSIONS
-- ============================================================================

-- 1.1 Sales by Category
SELECT 
    Category,
    COUNT(*) AS OrderCount,
    SUM(Sales) AS TotalSales,
    AVG(Sales) AS AvgSales,
    SUM(Profit) AS TotalProfit,
    AVG(Profit) AS AvgProfit,
    SUM(Quantity) AS TotalQuantity
FROM CleanedData
GROUP BY Category
ORDER BY TotalSales DESC;
GO

-- 1.2 Sales by Sub-Category
SELECT 
    Category,
    SubCategory,
    COUNT(*) AS OrderCount,
    SUM(Sales) AS TotalSales,
    AVG(Sales) AS AvgSales,
    SUM(Profit) AS TotalProfit,
    AVG(Profit) AS AvgProfit
FROM CleanedData
GROUP BY Category, SubCategory
ORDER BY TotalSales DESC;
GO

-- 1.3 Sales by Segment
SELECT 
    Segment,
    COUNT(*) AS OrderCount,
    SUM(Sales) AS TotalSales,
    AVG(Sales) AS AvgSales,
    SUM(Profit) AS TotalProfit,
    AVG(Profit) AS AvgProfit,
    CAST(SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0) AS DECIMAL(10,2)) AS ProfitMarginPct
FROM CleanedData
GROUP BY Segment
ORDER BY TotalSales DESC;
GO

-- 1.4 Sales by Market
SELECT 
    Market,
    COUNT(*) AS OrderCount,
    SUM(Sales) AS TotalSales,
    AVG(Sales) AS AvgSales,
    SUM(Profit) AS TotalProfit,
    CAST(SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0) AS DECIMAL(10,2)) AS ProfitMarginPct
FROM CleanedData
GROUP BY Market
ORDER BY TotalSales DESC;
GO

-- 1.5 Sales by Region
SELECT 
    Region,
    Market,
    COUNT(*) AS OrderCount,
    SUM(Sales) AS TotalSales,
    AVG(Sales) AS AvgSales,
    SUM(Profit) AS TotalProfit,
    CAST(SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0) AS DECIMAL(10,2)) AS ProfitMarginPct
FROM CleanedData
GROUP BY Region, Market
ORDER BY TotalSales DESC;
GO

-- 1.6 Sales by Ship Mode
SELECT 
    ShipMode,
    COUNT(*) AS OrderCount,
    SUM(Sales) AS TotalSales,
    AVG(Sales) AS AvgSales,
    AVG(ShippingDays) AS AvgShippingDays,
    SUM(Profit) AS TotalProfit
FROM CleanedData
GROUP BY ShipMode
ORDER BY TotalSales DESC;
GO

-- ============================================================================
-- 2. PROFITABILITY ANALYSIS
-- ============================================================================

-- 2.1 Profit Margin by Category
SELECT 
    Category,
    SUM(Sales) AS TotalSales,
    SUM(Profit) AS TotalProfit,
    CAST(SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0) AS DECIMAL(10,2)) AS ProfitMarginPct,
    COUNT(DISTINCT ProductID) AS ProductCount,
    COUNT(*) AS TransactionCount
FROM CleanedData
GROUP BY Category
ORDER BY ProfitMarginPct DESC;
GO

-- 2.2 Profit Margin by Region
SELECT 
    Region,
    SUM(Sales) AS TotalSales,
    SUM(Profit) AS TotalProfit,
    CAST(SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0) AS DECIMAL(10,2)) AS ProfitMarginPct,
    COUNT(DISTINCT CustomerID) AS CustomerCount
FROM CleanedData
GROUP BY Region
ORDER BY ProfitMarginPct DESC;
GO

-- 2.3 Profit Margin by Segment
SELECT 
    Segment,
    SUM(Sales) AS TotalSales,
    SUM(Profit) AS TotalProfit,
    CAST(SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0) AS DECIMAL(10,2)) AS ProfitMarginPct,
    COUNT(DISTINCT CustomerID) AS CustomerCount,
    COUNT(DISTINCT OrderID) AS OrderCount
FROM CleanedData
GROUP BY Segment
ORDER BY ProfitMarginPct DESC;
GO

-- 2.4 Loss-making transactions
SELECT 
    Category,
    SubCategory,
    COUNT(*) AS LossCount,
    SUM(Sales) AS TotalSales,
    SUM(Profit) AS TotalLoss,
    AVG(Discount) AS AvgDiscount
FROM CleanedData
WHERE Profit < 0
GROUP BY Category, SubCategory
ORDER BY TotalLoss ASC;
GO

-- ============================================================================
-- 3. DISCOUNT IMPACT ANALYSIS
-- ============================================================================

-- 3.1 Average discount vs average profit by category
SELECT 
    Category,
    AVG(Discount) AS AvgDiscount,
    SUM(Sales) AS TotalSales,
    SUM(Profit) AS TotalProfit,
    CAST(SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0) AS DECIMAL(10,2)) AS ProfitMarginPct,
    COUNT(*) AS TransactionCount
FROM CleanedData
GROUP BY Category
ORDER BY AvgDiscount DESC;
GO

-- 3.2 Discount band analysis
SELECT 
    DiscountBand,
    COUNT(*) AS TransactionCount,
    SUM(Sales) AS TotalSales,
    AVG(Sales) AS AvgSales,
    SUM(Profit) AS TotalProfit,
    CAST(SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0) AS DECIMAL(10,2)) AS ProfitMarginPct
FROM CleanedData
GROUP BY DiscountBand
ORDER BY 
    CASE DiscountBand 
        WHEN 'None' THEN 1 
        WHEN 'Low' THEN 2 
        WHEN 'Medium' THEN 3 
        WHEN 'High' THEN 4 
        ELSE 5 
    END;
GO

-- 3.3 Discount impact by segment
SELECT 
    Segment,
    DiscountBand,
    COUNT(*) AS TransactionCount,
    AVG(Discount) AS AvgDiscount,
    SUM(Sales) AS TotalSales,
    SUM(Profit) AS TotalProfit,
    CAST(SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0) AS DECIMAL(10,2)) AS ProfitMarginPct
FROM CleanedData
GROUP BY Segment, DiscountBand
ORDER BY Segment, DiscountBand;
GO

-- ============================================================================
-- 4. TOP CUSTOMERS AND PRODUCTS
-- ============================================================================

-- 4.1 Top 10 customers by sales
SELECT TOP 10
    c.CustomerID,
    c.CustomerName,
    c.Segment,
    COUNT(DISTINCT cd.OrderID) AS OrderCount,
    SUM(cd.Sales) AS TotalSales,
    SUM(cd.Profit) AS TotalProfit,
    CAST(SUM(cd.Profit) * 100.0 / NULLIF(SUM(cd.Sales), 0) AS DECIMAL(10,2)) AS ProfitMarginPct
FROM CleanedData cd
JOIN Customers c ON cd.CustomerID = c.CustomerID
GROUP BY c.CustomerID, c.CustomerName, c.Segment
ORDER BY TotalSales DESC;
GO

-- 4.2 Top 10 customers by profit
SELECT TOP 10
    c.CustomerID,
    c.CustomerName,
    c.Segment,
    COUNT(DISTINCT cd.OrderID) AS OrderCount,
    SUM(cd.Sales) AS TotalSales,
    SUM(cd.Profit) AS TotalProfit,
    CAST(SUM(cd.Profit) * 100.0 / NULLIF(SUM(cd.Sales), 0) AS DECIMAL(10,2)) AS ProfitMarginPct
FROM CleanedData cd
JOIN Customers c ON cd.CustomerID = c.CustomerID
GROUP BY c.CustomerID, c.CustomerName, c.Segment
ORDER BY TotalProfit DESC;
GO

-- 4.3 Top 10 products by sales
SELECT TOP 10
    p.ProductID,
    p.ProductName,
    p.Category,
    p.SubCategory,
    SUM(cd.Sales) AS TotalSales,
    SUM(cd.Quantity) AS TotalQuantity,
    SUM(cd.Profit) AS TotalProfit,
    CAST(SUM(cd.Profit) * 100.0 / NULLIF(SUM(cd.Sales), 0) AS DECIMAL(10,2)) AS ProfitMarginPct
FROM CleanedData cd
JOIN Products p ON cd.ProductID = p.ProductID
GROUP BY p.ProductID, p.ProductName, p.Category, p.SubCategory
ORDER BY TotalSales DESC;
GO

-- ============================================================================
-- 5. MONTHLY TREND ANALYSIS
-- ============================================================================

-- 5.1 Monthly sales and profit trends
SELECT 
    OrderYear,
    OrderMonth,
    COUNT(DISTINCT OrderID) AS OrderCount,
    SUM(Sales) AS TotalSales,
    SUM(Profit) AS TotalProfit,
    CAST(SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0) AS DECIMAL(10,2)) AS ProfitMarginPct,
    AVG(Discount) AS AvgDiscount,
    SUM(Quantity) AS TotalQuantity
FROM CleanedData
GROUP BY OrderYear, OrderMonth
ORDER BY OrderYear, OrderMonth;
GO

-- 5.2 Monthly trend by category
SELECT 
    OrderYear,
    OrderMonth,
    Category,
    SUM(Sales) AS TotalSales,
    SUM(Profit) AS TotalProfit,
    CAST(SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0) AS DECIMAL(10,2)) AS ProfitMarginPct
FROM CleanedData
GROUP BY OrderYear, OrderMonth, Category
ORDER BY OrderYear, OrderMonth, TotalSales DESC;
GO

-- ============================================================================
-- 6. CUSTOMER RETENTION ANALYSIS
-- ============================================================================

-- 6.1 Repeat customers (customers with more than 1 order)
SELECT 
    COUNT(DISTINCT CustomerID) AS RepeatCustomers,
    COUNT(DISTINCT CASE WHEN OrderCount > 1 THEN CustomerID END) AS CustomersWithMultipleOrders,
    CAST(100.0 * COUNT(DISTINCT CASE WHEN OrderCount > 1 THEN CustomerID END) / 
         COUNT(DISTINCT CustomerID) AS DECIMAL(10,2)) AS RepeatRate
FROM (
    SELECT 
        CustomerID,
        COUNT(DISTINCT OrderID) AS OrderCount
    FROM CleanedData
    GROUP BY CustomerID
) t;
GO

-- 6.2 Customer order frequency distribution
SELECT 
    OrderCount,
    COUNT(*) AS CustomerCount,
    CAST(100.0 * COUNT(*) / SUM(COUNT(*)) OVER() AS DECIMAL(10,2)) AS Percentage
FROM (
    SELECT 
        CustomerID,
        COUNT(DISTINCT OrderID) AS OrderCount
    FROM CleanedData
    GROUP BY CustomerID
) t
GROUP BY OrderCount
ORDER BY OrderCount;
GO

-- 6.3 Cohort: customers by first purchase month
SELECT 
    DATEFROMPARTS(FirstOrderYear, FirstOrderMonth, 1) AS CohortMonth,
    COUNT(*) AS NewCustomers,
    SUM(TotalSales) AS CohortSales,
    SUM(TotalProfit) AS CohortProfit
FROM Customers
WHERE FirstOrderDate IS NOT NULL
GROUP BY DATEFROMPARTS(FirstOrderYear, FirstOrderMonth, 1)
ORDER BY CohortMonth;
GO

-- ============================================================================
-- 7. BASKET ANALYSIS (Products bought together)
-- ============================================================================

-- 7.1 Products frequently bought together in the same order
WITH ProductPairs AS (
    SELECT 
        o1.OrderID,
        o1.ProductID AS Product1,
        o2.ProductID AS Product2,
        COUNT(*) AS PairCount
    FROM OrderDetails o1
    INNER JOIN OrderDetails o2 ON o1.OrderID = o2.OrderID
        AND o1.ProductID < o2.ProductID  -- avoid self-join duplicates
    GROUP BY o1.OrderID, o1.ProductID, o2.ProductID
)
SELECT TOP 20
    p1.ProductName AS Product1,
    p2.ProductName AS Product2,
    SUM(pp.PairCount) AS TotalPairs,
    COUNT(DISTINCT pp.OrderID) AS OrdersWithBothProducts
FROM ProductPairs pp
JOIN Products p1 ON pp.Product1 = p1.ProductID
JOIN Products p2 ON pp.Product2 = p2.ProductID
GROUP BY p1.ProductName, p2.ProductName
ORDER BY TotalPairs DESC;
GO

-- 7.2 Top product combinations by category
WITH ProductPairs AS (
    SELECT 
        o1.OrderID,
        o1.ProductID AS Product1,
        o2.ProductID AS Product2
    FROM OrderDetails o1
    INNER JOIN OrderDetails o2 ON o1.OrderID = o2.OrderID
        AND o1.ProductID < o2.ProductID
)
SELECT TOP 20
    p1.Category AS Category1,
    p1.SubCategory AS SubCategory1,
    p2.Category AS Category2,
    p2.SubCategory AS SubCategory2,
    COUNT(DISTINCT pp.OrderID) AS OrderCount
FROM ProductPairs pp
JOIN Products p1 ON pp.Product1 = p1.ProductID
JOIN Products p2 ON pp.Product2 = p2.ProductID
GROUP BY p1.Category, p1.SubCategory, p2.Category, p2.SubCategory
ORDER BY OrderCount DESC;
GO

-- ============================================================================
-- 8. SUMMARY STATISTICS
-- ============================================================================

SELECT 
    'Overall Summary' AS SummarySection,
    COUNT(DISTINCT OrderID) AS TotalOrders,
    COUNT(DISTINCT CustomerID) AS TotalCustomers,
    COUNT(DISTINCT ProductID) AS TotalProducts,
    SUM(Sales) AS TotalSales,
    SUM(Profit) AS TotalProfit,
    AVG(Sales) AS AvgOrderValue,
    AVG(Profit) AS AvgProfitPerOrder,
    AVG(Discount) AS AvgDiscount,
    CAST(SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0) AS DECIMAL(10,2)) AS OverallProfitMargin,
    COUNT(*) AS TotalTransactions
FROM CleanedData;
GO

PRINT 'Exploratory analysis completed.';
GO

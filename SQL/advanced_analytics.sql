-- ============================================================================
-- ADVANCED ANALYTICS
-- ============================================================================
-- RFM, Cohort, Market Share, Moving Averages, Forecasting, CLV
-- ============================================================================

USE SalesAnalysisDB;
GO

-- ============================================================================
-- 1. COHORT ANALYSIS
-- ============================================================================
-- Customer cohorts based on first purchase month, retention over months

-- 1.1 Define customer cohorts
WITH CustomerCohorts AS (
    SELECT 
        CustomerID,
        DATEFROMPARTS(YEAR(FirstOrderDate), MONTH(FirstOrderDate), 1) AS CohortMonth
    FROM Customers
    WHERE FirstOrderDate IS NOT NULL
),
CustomerActivity AS (
    SELECT 
        cd.CustomerID,
        DATEFROMPARTS(YEAR(cd.OrderDate), MONTH(cd.OrderDate), 1) AS ActivityMonth,
        cc.CohortMonth
    FROM CleanedData cd
    JOIN CustomerCohorts cc ON cd.CustomerID = cc.CustomerID
    GROUP BY cd.CustomerID, DATEFROMPARTS(YEAR(cd.OrderDate), MONTH(cd.OrderDate), 1), cc.CohortMonth
)
SELECT 
    CohortMonth,
    ActivityMonth,
    DATEDIFF(MONTH, CohortMonth, ActivityMonth) AS MonthsSinceCohort,
    COUNT(DISTINCT CustomerID) AS ActiveCustomers,
    SUM(Sales) AS CohortSales
FROM CustomerActivity ca
JOIN CleanedData cd ON ca.CustomerID = cd.CustomerID 
    AND DATEFROMPARTS(YEAR(cd.OrderDate), MONTH(cd.OrderDate), 1) = ca.ActivityMonth
GROUP BY CohortMonth, ActivityMonth
ORDER BY CohortMonth, MonthsSinceCohort;
GO

-- 1.2 Cohort retention rates (pivot format)
WITH CustomerCohorts AS (
    SELECT 
        CustomerID,
        DATEFROMPARTS(YEAR(FirstOrderDate), MONTH(FirstOrderDate), 1) AS CohortMonth
    FROM Customers
    WHERE FirstOrderDate IS NOT NULL
),
CohortSizes AS (
    SELECT CohortMonth, COUNT(*) AS CohortSize
    FROM CustomerCohorts
    GROUP BY CohortMonth
),
CustomerActivity AS (
    SELECT 
        cc.CustomerID,
        cc.CohortMonth,
        DATEFROMPARTS(YEAR(cd.OrderDate), MONTH(cd.OrderDate), 1) AS ActivityMonth
    FROM CleanedData cd
    JOIN CustomerCohorts cc ON cd.CustomerID = cc.CustomerID
    GROUP BY cc.CustomerID, cc.CohortMonth, DATEFROMPARTS(YEAR(cd.OrderDate), MONTH(cd.OrderDate), 1)
),
ActivityCounts AS (
    SELECT 
        ca.CohortMonth,
        DATEDIFF(MONTH, ca.CohortMonth, ca.ActivityMonth) AS MonthNumber,
        COUNT(DISTINCT ca.CustomerID) AS ActiveUsers
    FROM CustomerActivity ca
    GROUP BY ca.CohortMonth, DATEDIFF(MONTH, ca.CohortMonth, ca.ActivityMonth)
)
SELECT 
    ac.CohortMonth,
    cs.CohortSize,
    ac.MonthNumber,
    ac.ActiveUsers,
    CAST(100.0 * ac.ActiveUsers / cs.CohortSize AS DECIMAL(10,2)) AS RetentionRate
FROM ActivityCounts ac
JOIN CohortSizes cs ON ac.CohortMonth = cs.CohortMonth
ORDER BY ac.CohortMonth, ac.MonthNumber;
GO

-- ============================================================================
-- 2. RFM ANALYSIS
-- ============================================================================

-- 2.1 Calculate RFM metrics
WITH RFM AS (
    SELECT 
        c.CustomerID,
        c.CustomerName,
        c.Segment,
        -- Recency: days since last order from max date in dataset
        DATEDIFF(DAY, MAX(cd.OrderDate), (SELECT MAX(OrderDate) FROM CleanedData)) AS RecencyDays,
        -- Frequency: number of distinct orders
        COUNT(DISTINCT cd.OrderID) AS Frequency,
        -- Monetary: total sales
        SUM(cd.Sales) AS Monetary,
        SUM(cd.Profit) AS TotalProfit
    FROM CleanedData cd
    JOIN Customers c ON cd.CustomerID = c.CustomerID
    GROUP BY c.CustomerID, c.CustomerName, c.Segment
)
SELECT 
    CustomerID,
    CustomerName,
    Segment,
    RecencyDays,
    Frequency,
    Monetary,
    TotalProfit
FROM RFM
ORDER BY Monetary DESC;
GO

-- 2.2 RFM Quartile Scoring (1-4 scale, 1=worst, 4=best)
WITH RFM AS (
    SELECT 
        c.CustomerID,
        c.CustomerName,
        c.Segment,
        DATEDIFF(DAY, MAX(cd.OrderDate), (SELECT MAX(OrderDate) FROM CleanedData)) AS RecencyDays,
        COUNT(DISTINCT cd.OrderID) AS Frequency,
        SUM(cd.Sales) AS Monetary,
        SUM(cd.Profit) AS TotalProfit
    FROM CleanedData cd
    JOIN Customers c ON cd.CustomerID = c.CustomerID
    GROUP BY c.CustomerID, c.CustomerName, c.Segment
),
RFM_Quartiles AS (
    SELECT *,
        -- Recency: lower is better, so invert quartile
        NTILE(4) OVER (ORDER BY RecencyDays DESC) AS R_Quartile,
        -- Frequency: higher is better
        NTILE(4) OVER (ORDER BY Frequency) AS F_Quartile,
        -- Monetary: higher is better
        NTILE(4) OVER (ORDER BY Monetary) AS M_Quartile
    FROM RFM
)
SELECT 
    CustomerID,
    CustomerName,
    Segment,
    RecencyDays,
    Frequency,
    Monetary,
    R_Quartile,
    F_Quartile,
    M_Quartile,
    -- Combined RFM score
    CAST(R_Quartile AS VARCHAR(1)) + CAST(F_Quartile AS VARCHAR(1)) + CAST(M_Quartile AS VARCHAR(1)) AS RFM_Score
FROM RFM_Quartiles
ORDER BY RFM_Score DESC;
GO

-- ============================================================================
-- 3. CUSTOMER SEGMENTATION
-- ============================================================================

-- 3.1 Segment customers based on RFM
WITH RFM AS (
    SELECT 
        c.CustomerID,
        c.CustomerName,
        c.Segment AS OriginalSegment,
        DATEDIFF(DAY, MAX(cd.OrderDate), (SELECT MAX(OrderDate) FROM CleanedData)) AS RecencyDays,
        COUNT(DISTINCT cd.OrderID) AS Frequency,
        SUM(cd.Sales) AS Monetary,
        SUM(cd.Profit) AS TotalProfit
    FROM CleanedData cd
    JOIN Customers c ON cd.CustomerID = c.CustomerID
    GROUP BY c.CustomerID, c.CustomerName, c.Segment
),
RFM_Scores AS (
    SELECT *,
        NTILE(4) OVER (ORDER BY RecencyDays DESC) AS R_Score,
        NTILE(4) OVER (ORDER BY Frequency) AS F_Score,
        NTILE(4) OVER (ORDER BY Monetary) AS M_Score
    FROM RFM
),
CustomerSegments AS (
    SELECT *,
        (R_Score + F_Score + M_Score) AS RFM_Total,
        CASE 
            WHEN R_Score >= 4 AND F_Score >= 4 AND M_Score >= 4 THEN 'Champions'
            WHEN R_Score >= 3 AND F_Score >= 3 AND M_Score >= 3 THEN 'Loyal'
            WHEN R_Score >= 3 AND F_Score <= 2 AND M_Score >= 3 THEN 'Potential Loyalists'
            WHEN R_Score <= 2 AND F_Score >= 4 AND M_Score >= 4 THEN 'At Risk'
            WHEN R_Score <= 2 AND F_Score <= 2 AND M_Score <= 2 THEN 'Lost'
            WHEN R_Score <= 2 AND F_Score >= 3 THEN 'Hibernating'
            WHEN R_Score >= 3 AND F_Score <= 2 THEN 'New Customers'
            ELSE 'Others'
        END AS CustomerSegment
    FROM RFM_Scores
)
SELECT 
    CustomerSegment,
    COUNT(*) AS CustomerCount,
    AVG(RecencyDays) AS AvgRecencyDays,
    AVG(Frequency) AS AvgFrequency,
    AVG(Monetary) AS AvgMonetary,
    SUM(Monetary) AS TotalRevenue,
    SUM(TotalProfit) AS TotalProfit,
    CAST(SUM(TotalProfit) * 100.0 / NULLIF(SUM(Monetary), 0) AS DECIMAL(10,2)) AS ProfitMargin
FROM CustomerSegments
GROUP BY CustomerSegment
ORDER BY TotalRevenue DESC;
GO

-- ============================================================================
-- 4. MARKET SHARE ANALYSIS
-- ============================================================================

-- 4.1 Market share by region
WITH MarketSummary AS (
    SELECT 
        Region,
        SUM(Sales) AS RegionalSales,
        SUM(Profit) AS RegionalProfit
    FROM CleanedData
    GROUP BY Region
)
SELECT 
    Region,
    RegionalSales,
    RegionalProfit,
    CAST(RegionalSales * 100.0 / SUM(RegionalSales) OVER() AS DECIMAL(10,2)) AS MarketSharePct,
    CAST(RegionalProfit * 100.0 / SUM(RegionalProfit) OVER() AS DECIMAL(10,2)) AS ProfitSharePct
FROM MarketSummary
ORDER BY RegionalSales DESC;
GO

-- 4.2 Market share by category within region
WITH RegionalCategory AS (
    SELECT 
        Region,
        Category,
        SUM(Sales) AS CategorySales,
        SUM(Profit) AS CategoryProfit
    FROM CleanedData
    GROUP BY Region, Category
)
SELECT 
    Region,
    Category,
    CategorySales,
    CategoryProfit,
    CAST(CategorySales * 100.0 / SUM(CategorySales) OVER(PARTITION BY Region) AS DECIMAL(10,2)) AS CategorySharePct
FROM RegionalCategory
ORDER BY Region, CategorySales DESC;
GO

-- ============================================================================
-- 5. YEAR-OVER-YEAR GROWTH
-- ============================================================================

-- 5.1 YoY sales and profit growth
WITH YearlyMetrics AS (
    SELECT 
        OrderYear,
        SUM(Sales) AS YearlySales,
        SUM(Profit) AS YearlyProfit,
        COUNT(DISTINCT OrderID) AS OrderCount,
        COUNT(DISTINCT CustomerID) AS CustomerCount
    FROM CleanedData
    GROUP BY OrderYear
)
SELECT 
    OrderYear,
    YearlySales,
    YearlyProfit,
    OrderCount,
    CustomerCount,
    LAG(YearlySales) OVER (ORDER BY OrderYear) AS PrevYearSales,
    LAG(YearlyProfit) OVER (ORDER BY OrderYear) AS PrevYearProfit,
    CAST((YearlySales - LAG(YearlySales) OVER (ORDER BY OrderYear)) * 100.0 / 
         NULLIF(LAG(YearlySales) OVER (ORDER BY OrderYear), 0) AS DECIMAL(10,2)) AS SalesGrowthPct,
    CAST((YearlyProfit - LAG(YearlyProfit) OVER (ORDER BY OrderYear)) * 100.0 / 
         NULLIF(LAG(YearlyProfit) OVER (ORDER BY OrderYear), 0) AS DECIMAL(10,2)) AS ProfitGrowthPct
FROM YearlyMetrics
ORDER BY OrderYear;
GO

-- 5.2 YoY growth by category
WITH YearlyCategory AS (
    SELECT 
        OrderYear,
        Category,
        SUM(Sales) AS CategorySales,
        SUM(Profit) AS CategoryProfit
    FROM CleanedData
    GROUP BY OrderYear, Category
)
SELECT 
    OrderYear,
    Category,
    CategorySales,
    CategoryProfit,
    LAG(CategorySales) OVER (PARTITION BY Category ORDER BY OrderYear) AS PrevYearSales,
    CAST((CategorySales - LAG(CategorySales) OVER (PARTITION BY Category ORDER BY OrderYear)) * 100.0 / 
         NULLIF(LAG(CategorySales) OVER (PARTITION BY Category ORDER BY OrderYear), 0) AS DECIMAL(10,2)) AS SalesGrowthPct
FROM YearlyCategory
ORDER BY Category, OrderYear;
GO

-- ============================================================================
-- 6. MOVING AVERAGES (3-month, 6-month)
-- ============================================================================

-- 6.1 3-month and 6-month moving average of sales
WITH MonthlySales AS (
    SELECT 
        DATEFROMPARTS(OrderYear, OrderMonth, 1) AS MonthDate,
        SUM(Sales) AS MonthlySales,
        SUM(Profit) AS MonthlyProfit
    FROM CleanedData
    GROUP BY DATEFROMPARTS(OrderYear, OrderMonth, 1)
)
SELECT 
    MonthDate,
    MonthlySales,
    MonthlyProfit,
    -- 3-month moving average
    AVG(MonthlySales) OVER (ORDER BY MonthDate ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS Sales_MA3,
    AVG(MonthlyProfit) OVER (ORDER BY MonthDate ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS Profit_MA3,
    -- 6-month moving average
    AVG(MonthlySales) OVER (ORDER BY MonthDate ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS Sales_MA6,
    AVG(MonthlyProfit) OVER (ORDER BY MonthDate ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS Profit_MA6
FROM MonthlySales
ORDER BY MonthDate;
GO

-- ============================================================================
-- 7. SEASONAL DECOMPOSITION
-- ============================================================================

-- 7.1 Seasonal patterns by month
WITH MonthlyPatterns AS (
    SELECT 
        OrderMonth,
        OrderYear,
        SUM(Sales) AS MonthlySales,
        SUM(Profit) AS MonthlyProfit
    FROM CleanedData
    GROUP BY OrderMonth, OrderYear
),
MonthlyAvg AS (
    SELECT 
        OrderMonth,
        AVG(MonthlySales) AS AvgSales,
        AVG(MonthlyProfit) AS AvgProfit,
        STDEV(MonthlySales) AS StdSales
    FROM MonthlyPatterns
    GROUP BY OrderMonth
)
SELECT 
    OrderMonth,
    AvgSales,
    AvgProfit,
    StdSales,
    CAST(AvgProfit * 100.0 / NULLIF(AvgSales, 0) AS DECIMAL(10,2)) AS ProfitMarginPct,
    CASE 
        WHEN AvgSales > (SELECT AVG(AvgSales) FROM MonthlyAvg) + (SELECT STDEV(AvgSales) FROM MonthlyAvg) THEN 'Peak'
        WHEN AvgSales < (SELECT AVG(AvgSales) FROM MonthlyAvg) - (SELECT STDEV(AvgSales) FROM MonthlyAvg) THEN 'Low'
        ELSE 'Normal'
    END AS SeasonalityFlag
FROM MonthlyAvg
ORDER BY OrderMonth;
GO

-- ============================================================================
-- 8. ANOMALY DETECTION
-- ============================================================================

-- 8.1 Detect anomalous sales days (Z-score > 2.5)
WITH DailySales AS (
    SELECT 
        OrderDate,
        SUM(Sales) AS DailySales,
        SUM(Profit) AS DailyProfit,
        COUNT(*) AS TransactionCount
    FROM CleanedData
    GROUP BY OrderDate
),
DailyStats AS (
    SELECT 
        AVG(DailySales) AS MeanSales,
        STDEV(DailySales) AS StdSales
    FROM DailySales
)
SELECT 
    ds.OrderDate,
    ds.DailySales,
    ds.DailyProfit,
    ds.TransactionCount,
    d.MeanSales,
    d.StdSales,
    ABS(ds.DailySales - d.MeanSales) / NULLIF(d.StdSales, 0) AS ZScore,
    CASE 
        WHEN ABS(ds.DailySales - d.MeanSales) / NULLIF(d.StdSales, 0) > 2.5 THEN 'Anomaly'
        ELSE 'Normal'
    END AS AnomalyFlag
FROM DailySales ds
CROSS JOIN DailyStats d
WHERE ABS(ds.DailySales - d.MeanSales) / NULLIF(d.StdSales, 0) > 2.5
ORDER BY ZScore DESC;
GO

-- ============================================================================
-- 9. FORECASTING (Simple Moving Average Forecast)
-- ============================================================================

-- 9.1 Forecast next 3 months using 3-month moving average
WITH MonthlySales AS (
    SELECT 
        DATEFROMPARTS(OrderYear, OrderMonth, 1) AS MonthDate,
        SUM(Sales) AS MonthlySales
    FROM CleanedData
    GROUP BY DATEFROMPARTS(OrderYear, OrderMonth, 1)
),
LastMonths AS (
    SELECT TOP 3 
        MonthDate,
        MonthlySales
    FROM MonthlySales
    ORDER BY MonthDate DESC
)
SELECT 
    DATEADD(MONTH, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)), 
            (SELECT MAX(MonthDate) FROM MonthlySales)) AS ForecastMonth,
    AVG(MonthlySales) AS ForecastedSales,
    'Moving Average' AS ForecastMethod
FROM LastMonths;
GO

-- ============================================================================
-- 10. CUSTOMER LIFETIME VALUE (CLV)
-- ============================================================================

-- 10.1 Simple CLV estimation
WITH CustomerMetrics AS (
    SELECT 
        c.CustomerID,
        c.CustomerName,
        c.Segment,
        COUNT(DISTINCT cd.OrderID) AS TotalOrders,
        SUM(cd.Sales) AS TotalRevenue,
        SUM(cd.Profit) AS TotalProfit,
        DATEDIFF(DAY, MIN(cd.OrderDate), MAX(cd.OrderDate)) AS CustomerLifespanDays,
        AVG(cd.Sales) AS AvgOrderValue
    FROM CleanedData cd
    JOIN Customers c ON cd.CustomerID = c.CustomerID
    GROUP BY c.CustomerID, c.CustomerName, c.Segment
)
SELECT 
    CustomerID,
    CustomerName,
    Segment,
    TotalOrders,
    TotalRevenue,
    TotalProfit,
    CustomerLifespanDays,
    AvgOrderValue,
    -- CLV = Average Order Value * Purchase Frequency * Customer Lifespan (in years)
    AvgOrderValue * 
    CAST(TotalOrders AS FLOAT) / NULLIF(CustomerLifespanDays / 365.0, 0) * 
    NULLIF(CustomerLifespanDays / 365.0, 0) AS EstimatedCLV,
    -- Alternative: simple total profit as CLV proxy
    TotalProfit AS ProfitBasedCLV
FROM CustomerMetrics
ORDER BY EstimatedCLV DESC;
GO

-- ============================================================================
-- 11. ADVANCED PROFITABILITY METRICS
-- ============================================================================

-- 11.1 Product profitability ranking with market share
WITH ProductProfit AS (
    SELECT 
        p.ProductID,
        p.ProductName,
        p.Category,
        p.SubCategory,
        SUM(cd.Sales) AS TotalSales,
        SUM(cd.Profit) AS TotalProfit,
        COUNT(*) AS TransactionCount,
        CAST(SUM(cd.Profit) * 100.0 / NULLIF(SUM(cd.Sales), 0) AS DECIMAL(10,2)) AS ProfitMargin
    FROM CleanedData cd
    JOIN Products p ON cd.ProductID = p.ProductID
    GROUP BY p.ProductID, p.ProductName, p.Category, p.SubCategory
)
SELECT 
    *,
    CAST(TotalSales * 100.0 / SUM(TotalSales) OVER() AS DECIMAL(10,2)) AS SalesSharePct,
    CAST(TotalProfit * 100.0 / SUM(TotalProfit) OVER() AS DECIMAL(10,2)) AS ProfitSharePct
FROM ProductProfit
ORDER BY TotalProfit DESC;
GO

PRINT 'Advanced analytics completed.';
GO

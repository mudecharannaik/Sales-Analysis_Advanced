-- ============================================================================
-- STORED PROCEDURES AND FUNCTIONS
-- ============================================================================
-- Reusable database objects for common calculations and operations
-- ============================================================================

USE SalesAnalysisDB;
GO

-- ============================================================================
-- 1. STORED PROCEDURE: sp_RefreshMonthlyAnalytics
-- ============================================================================
-- Refreshes the AnalyticsSummary table with latest monthly metrics

IF OBJECT_ID('sp_RefreshMonthlyAnalytics', 'P') IS NOT NULL
    DROP PROCEDURE sp_RefreshMonthlyAnalytics;
GO

CREATE PROCEDURE sp_RefreshMonthlyAnalytics
    @Period VARCHAR(20) = NULL  -- Optional period filter, NULL = all periods
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @MaxDate DATE = (SELECT MAX(OrderDate) FROM CleanedData);
    DECLARE @MinDate DATE = (SELECT MIN(OrderDate) FROM CleanedData);
    
    -- Clear existing summary for the period
    IF @Period IS NOT NULL
        DELETE FROM AnalyticsSummary WHERE Period = @Period;
    ELSE
        DELETE FROM AnalyticsSummary;
    
    -- 1. Total Sales
    INSERT INTO AnalyticsSummary (MetricName, MetricValue, Period, Category)
    SELECT 
        'Total Sales',
        SUM(Sales),
        FORMAT(OrderDate, 'yyyy-MM'),
        'Sales'
    FROM CleanedData
    WHERE @Period IS NULL OR FORMAT(OrderDate, 'yyyy-MM') = @Period
    GROUP BY FORMAT(OrderDate, 'yyyy-MM');
    
    -- 2. Total Profit
    INSERT INTO AnalyticsSummary (MetricName, MetricValue, Period, Category)
    SELECT 
        'Total Profit',
        SUM(Profit),
        FORMAT(OrderDate, 'yyyy-MM'),
        'Profit'
    FROM CleanedData
    WHERE @Period IS NULL OR FORMAT(OrderDate, 'yyyy-MM') = @Period
    GROUP BY FORMAT(OrderDate, 'yyyy-MM');
    
    -- 3. Total Orders
    INSERT INTO AnalyticsSummary (MetricName, MetricValue, Period, Category)
    SELECT 
        'Total Orders',
        COUNT(DISTINCT OrderID),
        FORMAT(OrderDate, 'yyyy-MM'),
        'Orders'
    FROM CleanedData
    WHERE @Period IS NULL OR FORMAT(OrderDate, 'yyyy-MM') = @Period
    GROUP BY FORMAT(OrderDate, 'yyyy-MM');
    
    -- 4. Total Customers
    INSERT INTO AnalyticsSummary (MetricName, MetricValue, Period, Category)
    SELECT 
        'Total Customers',
        COUNT(DISTINCT CustomerID),
        FORMAT(OrderDate, 'yyyy-MM'),
        'Customers'
    FROM CleanedData
    WHERE @Period IS NULL OR FORMAT(OrderDate, 'yyyy-MM') = @Period
    GROUP BY FORMAT(OrderDate, 'yyyy-MM');
    
    -- 5. Average Order Value
    INSERT INTO AnalyticsSummary (MetricName, MetricValue, Period, Category)
    SELECT 
        'Avg Order Value',
        AVG(OrderSales),
        FORMAT(OrderDate, 'yyyy-MM'),
        'Orders'
    FROM (
        SELECT OrderID, OrderDate, SUM(Sales) AS OrderSales
        FROM CleanedData
        WHERE @Period IS NULL OR FORMAT(OrderDate, 'yyyy-MM') = @Period
        GROUP BY OrderID, OrderDate
    ) o
    GROUP BY FORMAT(OrderDate, 'yyyy-MM');
    
    -- 6. Profit Margin
    INSERT INTO AnalyticsSummary (MetricName, MetricValue, Period, Category)
    SELECT 
        'Profit Margin %',
        CAST(SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0) AS DECIMAL(18,4)),
        FORMAT(OrderDate, 'yyyy-MM'),
        'Profit'
    FROM CleanedData
    WHERE @Period IS NULL OR FORMAT(OrderDate, 'yyyy-MM') = @Period
    GROUP BY FORMAT(OrderDate, 'yyyy-MM');
    
    -- 7. Average Discount
    INSERT INTO AnalyticsSummary (MetricName, MetricValue, Period, Category)
    SELECT 
        'Avg Discount',
        AVG(Discount),
        FORMAT(OrderDate, 'yyyy-MM'),
        'Pricing'
    FROM CleanedData
    WHERE @Period IS NULL OR FORMAT(OrderDate, 'yyyy-MM') = @Period
    GROUP BY FORMAT(OrderDate, 'yyyy-MM');
    
    -- 8. Category Sales
    INSERT INTO AnalyticsSummary (MetricName, MetricValue, Period, Category)
    SELECT 
        'Category Sales - ' + Category,
        SUM(Sales),
        FORMAT(OrderDate, 'yyyy-MM'),
        'Sales'
    FROM CleanedData
    WHERE @Period IS NULL OR FORMAT(OrderDate, 'yyyy-MM') = @Period
    GROUP BY FORMAT(OrderDate, 'yyyy-MM'), Category;
    
    -- 9. Region Sales
    INSERT INTO AnalyticsSummary (MetricName, MetricValue, Period, Category)
    SELECT 
        'Region Sales - ' + Region,
        SUM(Sales),
        FORMAT(OrderDate, 'yyyy-MM'),
        'Sales'
    FROM CleanedData
    WHERE @Period IS NULL OR FORMAT(OrderDate, 'yyyy-MM') = @Period
    GROUP BY FORMAT(OrderDate, 'yyyy-MM'), Region;
    
    PRINT 'Monthly analytics refreshed successfully.';
END;
GO

-- ============================================================================
-- 2. SCALAR FUNCTION: fn_CalculateProfitMargin
-- ============================================================================
-- Calculates profit margin percentage for given sales and profit values

IF OBJECT_ID('fn_CalculateProfitMargin', 'FN') IS NOT NULL
    DROP FUNCTION fn_CalculateProfitMargin;
GO

CREATE FUNCTION fn_CalculateProfitMargin(
    @Sales DECIMAL(18,2),
    @Profit DECIMAL(18,2)
)
RETURNS DECIMAL(10,4)
AS
BEGIN
    DECLARE @Margin DECIMAL(10,4);
    
    IF @Sales = 0 OR @Sales IS NULL
        SET @Margin = NULL;
    ELSE
        SET @Margin = CAST(@Profit * 100.0 / @Sales AS DECIMAL(10,4));
    
    RETURN @Margin;
END;
GO

-- Usage example:
-- SELECT dbo.fn_CalculateProfitMargin(1000, 200) AS ProfitMarginPct;
GO

-- ============================================================================
-- 3. SCALAR FUNCTION: fn_CategorizeCustomer
-- ============================================================================
-- Categorizes customers based on RFM scores

IF OBJECT_ID('fn_CategorizeCustomer', 'FN') IS NOT NULL
    DROP FUNCTION fn_CategorizeCustomer;
GO

CREATE FUNCTION fn_CategorizeCustomer(
    @CustomerID VARCHAR(50)
)
RETURNS VARCHAR(50)
AS
BEGIN
    DECLARE @Segment VARCHAR(50);
    DECLARE @RecencyDays INT;
    DECLARE @Frequency INT;
    DECLARE @Monetary DECIMAL(18,2);
    DECLARE @R_Score INT;
    DECLARE @F_Score INT;
    DECLARE @M_Score INT;
    DECLARE @MaxDate DATE;
    
    SET @MaxDate = (SELECT MAX(OrderDate) FROM CleanedData);
    
    -- Calculate RFM metrics
    SELECT 
        @RecencyDays = DATEDIFF(DAY, MAX(OrderDate), @MaxDate),
        @Frequency = COUNT(DISTINCT OrderID),
        @Monetary = SUM(Sales)
    FROM CleanedData
    WHERE CustomerID = @CustomerID;
    
    -- Calculate quartile scores (1-4)
    IF @RecencyDays IS NULL OR @Frequency IS NULL OR @Monetary IS NULL
    BEGIN
        RETURN 'Unknown';
    END;
    
    -- Recency score (inverted: lower recency = higher score)
    SET @R_Score = 
        CASE 
            WHEN @RecencyDays <= 30 THEN 4
            WHEN @RecencyDays <= 90 THEN 3
            WHEN @RecencyDays <= 180 THEN 2
            ELSE 1
        END;
    
    -- Frequency score
    SET @F_Score = 
        CASE 
            WHEN @Frequency >= 10 THEN 4
            WHEN @Frequency >= 5 THEN 3
            WHEN @Frequency >= 2 THEN 2
            ELSE 1
        END;
    
    -- Monetary score
    SET @M_Score = 
        CASE 
            WHEN @Monetary >= 5000 THEN 4
            WHEN @Monetary >= 2000 THEN 3
            WHEN @Monetary >= 500 THEN 2
            ELSE 1
        END;
    
    -- Segment based on scores
    SET @Segment = 
        CASE 
            WHEN @R_Score >= 4 AND @F_Score >= 4 AND @M_Score >= 4 THEN 'Champions'
            WHEN @R_Score >= 3 AND @F_Score >= 3 AND @M_Score >= 3 THEN 'Loyal'
            WHEN @R_Score >= 3 AND @F_Score <= 2 AND @M_Score >= 3 THEN 'Potential Loyalists'
            WHEN @R_Score <= 2 AND @F_Score >= 4 AND @M_Score >= 4 THEN 'At Risk'
            WHEN @R_Score <= 2 AND @F_Score <= 2 AND @M_Score <= 2 THEN 'Lost'
            WHEN @R_Score <= 2 AND @F_Score >= 3 THEN 'Hibernating'
            WHEN @R_Score >= 3 AND @F_Score <= 2 THEN 'New Customers'
            ELSE 'Others'
        END;
    
    RETURN @Segment;
END;
GO

-- Usage example:
-- SELECT CustomerID, dbo.fn_CategorizeCustomer(CustomerID) AS Segment
-- FROM Customers;
GO

-- ============================================================================
-- 4. TABLE-VALUED FUNCTION: fn_DetectOutliers
-- ============================================================================
-- Returns a table of outliers for a given column using IQR method

IF OBJECT_ID('fn_DetectOutliers', 'FN') IS NOT NULL
    DROP FUNCTION fn_DetectOutliers;
GO

CREATE FUNCTION fn_DetectOutliers(
    @ColumnName VARCHAR(50),
    @TableName VARCHAR(50) = 'CleanedData'
)
RETURNS @Outliers TABLE (
    RowID INT,
    Value DECIMAL(18,2),
    Q1 DECIMAL(18,2),
    Q3 DECIMAL(18,2),
    IQR DECIMAL(18,2),
    LowerFence DECIMAL(18,2),
    UpperFence DECIMAL(18,2),
    IsOutlier BIT
)
AS
BEGIN
    DECLARE @SQL NVARCHAR(MAX);
    DECLARE @Q1 DECIMAL(18,2);
    DECLARE @Q3 DECIMAL(18,2);
    DECLARE @IQR DECIMAL(18,2);
    DECLARE @LowerFence DECIMAL(18,2);
    DECLARE @UpperFence DECIMAL(18,2);
    
    -- Calculate quartiles
    SET @SQL = N'
        SELECT 
            @Q1 = PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY CAST(' + @ColumnName + ' AS FLOAT)),
            @Q3 = PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY CAST(' + @ColumnName + ' AS FLOAT))
        FROM ' + @TableName + '
        WHERE ' + @ColumnName + ' IS NOT NULL';
    
    EXEC sp_executesql @SQL, N'@Q1 DECIMAL(18,2) OUTPUT, @Q3 DECIMAL(18,2) OUTPUT', 
                       @Q1 = @Q1 OUTPUT, @Q3 = @Q3 OUTPUT;
    
    SET @IQR = @Q3 - @Q1;
    SET @LowerFence = @Q1 - 1.5 * @IQR;
    SET @UpperFence = @Q3 + 1.5 * @IQR;
    
    -- Insert outliers
    SET @SQL = N'
        INSERT INTO @Outliers
        SELECT 
            RowID,
            CAST(' + @ColumnName + ' AS DECIMAL(18,2)),
            @Q1, @Q3, @IQR, @LowerFence, @UpperFence,
            CASE WHEN ' + @ColumnName + ' < @LowerFence OR ' + @ColumnName + ' > @UpperFence 
                 THEN 1 ELSE 0 END
        FROM ' + @TableName + '
        WHERE ' + @ColumnName + ' IS NOT NULL
          AND (' + @ColumnName + ' < @LowerFence OR ' + @ColumnName + ' > @UpperFence)';
    
    EXEC sp_executesql @SQL, 
                       N'@Q1 DECIMAL(18,2), @Q3 DECIMAL(18,2), @IQR DECIMAL(18,2), 
                         @LowerFence DECIMAL(18,2), @UpperFence DECIMAL(18,2)',
                       @Q1 = @Q1, @Q3 = @Q3, @IQR = @IQR, 
                       @LowerFence = @LowerFence, @UpperFence = @UpperFence;
    
    RETURN;
END;
GO

-- Usage example:
-- SELECT * FROM fn_DetectOutliers('Sales');
GO

-- ============================================================================
-- 5. TABLE-VALUED FUNCTION: fn_GetTopProducts
-- ============================================================================
-- Returns top N products by specified metric

IF OBJECT_ID('fn_GetTopProducts', 'FN') IS NOT NULL
    DROP FUNCTION fn_GetTopProducts;
GO

CREATE FUNCTION fn_GetTopProducts(
    @TopN INT = 10,
    @Metric VARCHAR(50) = 'Sales',  -- 'Sales', 'Profit', 'Quantity'
    @CategoryFilter VARCHAR(100) = NULL
)
RETURNS @TopProducts TABLE (
    Rank INT,
    ProductID VARCHAR(50),
    ProductName VARCHAR(500),
    Category VARCHAR(100),
    SubCategory VARCHAR(100),
    MetricValue DECIMAL(18,2),
    TransactionCount INT
)
AS
BEGIN
    DECLARE @SQL NVARCHAR(MAX);
    DECLARE @MetricColumn VARCHAR(50);
    
    SET @MetricColumn = 
        CASE @Metric
            WHEN 'Sales' THEN 'SUM(cd.Sales)'
            WHEN 'Profit' THEN 'SUM(cd.Profit)'
            WHEN 'Quantity' THEN 'SUM(cd.Quantity)'
            ELSE 'SUM(cd.Sales)'
        END;
    
    SET @SQL = N'
        INSERT INTO @TopProducts
        SELECT TOP ' + CAST(@TopN AS VARCHAR(10)) + '
            ROW_NUMBER() OVER (ORDER BY ' + @MetricColumn + ' DESC) AS Rank,
            p.ProductID,
            p.ProductName,
            p.Category,
            p.SubCategory,
            ' + @MetricColumn + ' AS MetricValue,
            COUNT(*) AS TransactionCount
        FROM CleanedData cd
        JOIN Products p ON cd.ProductID = p.ProductID
        WHERE (@CategoryFilter IS NULL OR p.Category = @CategoryFilter)
        GROUP BY p.ProductID, p.ProductName, p.Category, p.SubCategory
        ORDER BY ' + @MetricColumn + ' DESC';
    
    EXEC sp_executesql @SQL, N'@CategoryFilter VARCHAR(100)', @CategoryFilter = @CategoryFilter;
    
    RETURN;
END;
GO

-- Usage examples:
-- SELECT * FROM fn_GetTopProducts(10, 'Sales');
-- SELECT * FROM fn_GetTopProducts(5, 'Profit', 'Technology');
GO

-- ============================================================================
-- 6. HELPER FUNCTION: fn_FormatCurrency
-- ============================================================================

IF OBJECT_ID('fn_FormatCurrency', 'FN') IS NOT NULL
    DROP FUNCTION fn_FormatCurrency;
GO

CREATE FUNCTION fn_FormatCurrency(
    @Value DECIMAL(18,2),
    @CurrencySymbol VARCHAR(10) = '$'
)
RETURNS VARCHAR(50)
AS
BEGIN
    DECLARE @Formatted VARCHAR(50);
    
    IF @Value IS NULL
        SET @Formatted = 'N/A';
    ELSE
        SET @Formatted = @CurrencySymbol + CAST(CAST(@Value AS MONEY) AS VARCHAR(20));
    
    RETURN @Formatted;
END;
GO

-- ============================================================================
-- 7. VALIDATION FUNCTION: fn_ValidateBusinessRules
-- ============================================================================
-- Returns validation results for a given row

IF OBJECT_ID('fn_ValidateBusinessRules', 'FN') IS NOT NULL
    DROP FUNCTION fn_ValidateBusinessRules;
GO

CREATE FUNCTION fn_ValidateBusinessRules(
    @Sales DECIMAL(18,2),
    @Profit DECIMAL(18,2),
    @Discount DECIMAL(5,4),
    @Quantity INT,
    @ShipDate DATE,
    @OrderDate DATE,
    @ShippingCost DECIMAL(18,2)
)
RETURNS @Validation TABLE (
    RuleName VARCHAR(100),
    IsValid BIT,
    ErrorMessage VARCHAR(200)
)
AS
BEGIN
    -- Rule 1: Sales >= 0
    INSERT INTO @Validation
    SELECT 'Sales >= 0', 
           CASE WHEN @Sales >= 0 THEN 1 ELSE 0 END,
           CASE WHEN @Sales < 0 THEN 'Sales cannot be negative' ELSE NULL END;
    
    -- Rule 2: Profit not NULL
    INSERT INTO @Validation
    SELECT 'Profit Not NULL',
           CASE WHEN @Profit IS NOT NULL THEN 1 ELSE 0 END,
           CASE WHEN @Profit IS NULL THEN 'Profit is NULL' ELSE NULL END;
    
    -- Rule 3: Discount between 0 and 1
    INSERT INTO @Validation
    SELECT 'Discount in [0,1]',
           CASE WHEN @Discount >= 0 AND @Discount <= 1 THEN 1 ELSE 0 END,
           CASE WHEN @Discount < 0 OR @Discount > 1 THEN 'Discount must be between 0 and 1' ELSE NULL END;
    
    -- Rule 4: Quantity > 0
    INSERT INTO @Validation
    SELECT 'Quantity > 0',
           CASE WHEN @Quantity > 0 THEN 1 ELSE 0 END,
           CASE WHEN @Quantity <= 0 THEN 'Quantity must be greater than 0' ELSE NULL END;
    
    -- Rule 5: ShipDate >= OrderDate
    INSERT INTO @Validation
    SELECT 'ShipDate >= OrderDate',
           CASE WHEN @ShipDate >= @OrderDate OR @ShipDate IS NULL THEN 1 ELSE 0 END,
           CASE WHEN @ShipDate < @OrderDate THEN 'Ship date cannot be before order date' ELSE NULL END;
    
    -- Rule 6: ShippingCost >= 0
    INSERT INTO @Validation
    SELECT 'ShippingCost >= 0',
           CASE WHEN @ShippingCost >= 0 THEN 1 ELSE 0 END,
           CASE WHEN @ShippingCost < 0 THEN 'Shipping cost cannot be negative' ELSE NULL END;
    
    RETURN;
END;
GO

-- Usage example:
-- SELECT * FROM fn_ValidateBusinessRules(1000, 200, 0.15, 5, '2024-01-10', '2024-01-05', 50);
GO

PRINT 'Stored procedures and functions created successfully.';
GO

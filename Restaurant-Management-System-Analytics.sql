USE RestaurantManagementSystem;
--1. مؤشرات الأداء الرئيسية (KPIs)
SELECT
    COUNT(*)                        AS TotalOrders,
    SUM(FinalAmount)                AS TotalRevenue,
    AVG(FinalAmount)                AS AvgOrderValue,
    COUNT(DISTINCT CustomerID)      AS TotalCustomers
FROM Orders;
-- توزيع حالات الطلبات
SELECT 
    OrderStatus,
    COUNT(*) AS OrderCount,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Orders), 2) AS Percentage
FROM Orders
GROUP BY OrderStatus
ORDER BY OrderCount DESC;
--طرق الدفع
SELECT 
    PaymentMethod,
    COUNT(*)          AS TotalPayments,
    SUM(PaidAmount)   AS TotalPaid
FROM Payments
GROUP BY PaymentMethod
ORDER BY TotalPayments DESC;
-- المبيعات حسب فئة المنيو
SELECT 
    c.CategoryName,
    COUNT(od.OrderDetailID)     AS TotalOrders,
    SUM(od.SubTotal)            AS TotalRevenue
FROM OrderDetails od
JOIN MenuItems m  ON od.ItemID     = m.ItemID
JOIN Categories c ON m.CategoryID  = c.CategoryID
GROUP BY c.CategoryName
ORDER BY TotalRevenue DESC;
-- الأصناف الأعلى مبيعاً
SELECT TOP 10
    m.ItemName,
    COUNT(od.OrderDetailID)  AS TimesOrdered,
    SUM(od.Quantity)         AS TotalQtySold,
    SUM(od.SubTotal)         AS TotalRevenue
FROM OrderDetails od
JOIN MenuItems m ON od.ItemID = m.ItemID
GROUP BY m.ItemName
ORDER BY TotalRevenue DESC;
-- تحليل هامش الربح لكل صنف
SELECT 
    ItemName,
    Price     AS SalePrice,
    CostPrice,
    (Price - CostPrice)    AS GrossProfit,
    ROUND((Price - CostPrice) * 100.0 / Price, 2)     AS ProfitMarginPct
FROM MenuItems
ORDER BY ProfitMarginPct DESC;
--العملاء حسب المدينة
SELECT 
    City,
    COUNT(*)         AS CustomerCount,
    SUM(LoyaltyPoints) AS TotalLoyaltyPoints,
    AVG(LoyaltyPoints) AS AvgLoyaltyPoints
FROM Customers
GROUP BY City
ORDER BY CustomerCount DESC;
--فاتورة الرواتب حسب الأدوار
SELECT 
    r.RoleName,
    COUNT(e.EmployeeID)      AS EmployeeCount,
    SUM(e.Salary)            AS TotalSalary,
    AVG(e.Salary)            AS AvgSalary
FROM Employees e
JOIN Roles r ON e.RoleID = r.RoleID
GROUP BY r.RoleName
ORDER BY TotalSalary DESC;
-- أداء موظفي التوصيل
SELECT 
    e.FullName,
    COUNT(d.DeliveryID)          AS TotalDeliveries,
    AVG(d.CustomerRating)        AS AvgRating,
    MIN(d.CustomerRating)        AS MinRating,
    MAX(d.CustomerRating)        AS MaxRating
FROM Deliveries d
JOIN Employees e ON d.DeliveryEmployeeID = e.EmployeeID
GROUP BY e.FullName
ORDER BY AvgRating DESC;
-- تحليل الضرائب والخصومات
SELECT
    SUM(TotalAmount)    AS SubTotal,
    SUM(Tax)            AS TotalTax,
    SUM(Discount)       AS TotalDiscount,
    SUM(DeliveryFee)    AS TotalDeliveryFees,
    SUM(FinalAmount)    AS NetRevenue
FROM Orders;
--تقييمات العملاء مقابل قيمة الطلبات
SELECT 
    r.Rating,
    COUNT(r.ReviewID)       AS ReviewCount,
    AVG(o.FinalAmount)      AS AvgOrderValue,
    AVG(o.Discount)         AS AvgDiscount
FROM Reviews r
JOIN Orders o ON r.OrderID = o.OrderID
GROUP BY r.Rating
ORDER BY r.Rating DESC;
-- حالة المخزون مقارنةً بحد إعادة الطلب
SELECT 
    i.IngredientName,
    i.QuantityAvailable,
    i.ReorderLevel,
    i.Unit,
    s.SupplierName,
    CASE 
        WHEN i.QuantityAvailable <= i.ReorderLevel 
        THEN 'Needs Reorder' 
        ELSE 'In Stock' 
    END AS StockStatus
FROM Inventory i
JOIN Suppliers s ON i.SupplierID = s.SupplierID
ORDER BY QuantityAvailable ASC;

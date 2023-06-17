---
author: Elad Oz Cohen
categories:
#- Theme Features
 - MSSQL
 - PowerBI
#- package
date: "2023-06-16"
draft: false
excerpt: Using MSSQL and PowerBI to explore an E-Commerce related dataset.

layout: single

links:
#- icon: door-open
#  icon_pack: fas
#  name: website
#  url: https://bakeoff.netlify.com/ 
#- icon: github
#  icon_pack: fab
#  name: code
#  url: https://github.com/EladOzCohen/SQL-Data-Exploartion---Covid-19
#subtitle: Add the discreption of the coidv19
tags:
- hugo-site
title: MSSQL & PowerBI E-Commerece Analysis (under construction)

---

---





### Q1: Which products have consistently increased in sales over the months?


```SQL
WITH MonthlySales AS (
    SELECT
        p.ProductName,
        YEAR(o.OrderDate) AS Year,
        MONTH(o.OrderDate) AS Month,
        SUM(od.Quantity) AS TotalQuantity
    FROM
        OrderDetails od
    JOIN
        Products p ON od.ProductID = p.ProductID
    JOIN
        Orders o ON od.OrderID = o.OrderID
    WHERE
        o.Status = 'Completed'
    GROUP BY
        p.ProductName,
        YEAR(o.OrderDate),
        MONTH(o.OrderDate)
), RankedSales AS (
    SELECT
        ProductName,
        Year,
        Month,
        TotalQuantity,
        ROW_NUMBER() OVER (PARTITION BY ProductName ORDER BY Year, Month) AS RowNum
    FROM
        MonthlySales
)
SELECT
    ProductName
FROM
    RankedSales
WHERE
    RowNum > 1
    AND TotalQuantity > LAG(TotalQuantity) OVER (PARTITION BY ProductName ORDER BY RowNum)
GROUP BY
    ProductName
HAVING
    COUNT(*) = MAX(RowNum) - 1;

```
<br>
<br>
<br>
<br>





### Q2:Which customers are likely to make a purchase next month based on their previous buying patterns?

```SQL
WITH CustomerMonthlyPurchases AS (
    SELECT
        c.CustomerID,
        c.FirstName,
        c.LastName,
        YEAR(o.OrderDate) AS Year,
        MONTH(o.OrderDate) AS Month,
        COUNT(*) AS TotalOrders
    FROM
        Customers c
    JOIN
        Orders o ON c.CustomerID = o.CustomerID
    WHERE
        o.Status = 'Completed'
    GROUP BY
        c.CustomerID,
        c.FirstName,
        c.LastName,
        YEAR(o.OrderDate),
        MONTH(o.OrderDate)
)
SELECT
    FirstName,
    LastName
FROM
    CustomerMonthlyPurchases
WHERE
    YEAR = YEAR(GETDATE())
    AND Month = MONTH(GETDATE()) - 1
    AND TotalOrders > (SELECT AVG(TotalOrders) FROM CustomerMonthlyPurchases)
GROUP BY
    FirstName,
    LastName;

```
<br>
<br>
<br>
<br>





### Q3: What is the monthly retention rate of customers?

```SQL
WITH MonthlyCustomers AS (
    SELECT
        DISTINCT CustomerID,
        YEAR(OrderDate) AS Year,
        MONTH(OrderDate) AS Month
    FROM
        Orders
    WHERE
        Status = 'Completed'
), MonthlyCustomerCounts AS (
    SELECT
        Year,
        Month,
        COUNT(*) AS NumberOfCustomers
    FROM
        MonthlyCustomers
    GROUP BY
        Year,
        Month
), RetainedCustomers AS (
    SELECT
        MC1.Year,
        MC1.Month,
        COUNT(*) AS NumberOfRetainedCustomers
    FROM
        MonthlyCustomers MC1
    JOIN
        MonthlyCustomers MC2 ON MC1.CustomerID = MC2.CustomerID
    WHERE
        MC1.Year = MC2.Year
        AND MC1.Month = MC2.Month + 1
    GROUP BY
        MC1.Year,
        MC1.Month
)
SELECT
    MCC.Year,
    MCC.Month,
    CAST(1.0 * RC.NumberOfRetainedCustomers / MCC.NumberOfCustomers AS DECIMAL(4, 2)) AS RetentionRate
FROM
    MonthlyCustomerCounts MCC
LEFT JOIN
    RetainedCustomers RC ON MCC.Year = RC.Year AND MCC.Month = RC.Month
ORDER BY
    MCC.Year,
    MCC.Month;

```
<br>
<br>
<br>
<br>



### Q4:What are the top 5 categories in terms of revenue, and how have they trended over time?



```SQL
WITH CategoryRevenue AS (
    SELECT
        p.Category,
        YEAR(o.OrderDate) AS Year,
        MONTH(o.OrderDate) AS Month,
        SUM(od.TotalPrice) AS Revenue
    FROM
        Products p
    JOIN
        OrderDetails od ON p.ProductID = od.ProductID
    JOIN
        Orders o ON od.OrderID = o.OrderID
    WHERE
        o.Status = 'Completed'
    GROUP BY
        p.Category,
        YEAR(o.OrderDate),
        MONTH(o.OrderDate)
), TopCategories AS (
    SELECT
        TOP 5 Category,
        SUM(Revenue) AS TotalRevenue
    FROM
        CategoryRevenue
    GROUP BY
        Category
    ORDER BY
        TotalRevenue DESC
)
SELECT
    CR.Category,
    CR.Year,
    CR.Month,
    CR.Revenue
FROM
    CategoryRevenue CR
WHERE
    CR.Category IN (SELECT Category FROM TopCategories)
ORDER BY
    CR.Category,
    CR.Year,
    CR.Month;


```

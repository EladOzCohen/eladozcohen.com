---
title: "Sub-Queries in MSSQL: Unleashing the Power of Nested Queries"
subtitle: ""
excerpt: "Take your SQL skills to the next level with the almighty window functions"
date: 2023-02-02
author: "Elad Oz Cohen"
draft: false
# layout options: single, single-sidebar
layout: single
categories:
---

Sub-queries, also known as nested queries, are an important feature in MSSQL that allow you to use the result of one query as the input for another query. This can be incredibly useful for complex queries that require multiple steps or when you need to retrieve data that depends on the results of another query.

There are two main types of sub-queries in MSSQL: simple sub-queries and correlated sub-queries.


## Simple Sub-Queries

A simple sub-query is a nested query that is completely independent of the outer query. That is, the sub-query can be executed independently of the outer query and will always return the same result, regardless of the outer query.

Here's an example of a simple sub-query:



```SQL
SELECT *
FROM Customers
WHERE CustomerID IN (
    SELECT CustomerID
    FROM Orders
    WHERE OrderDate BETWEEN '2022-01-01' AND '2022-12-31'
)


```
<br>

In this example, the outer query selects all columns from the Customers table, but only returns rows where the CustomerID is in the result set of the inner query. The inner query selects only the CustomerID column from the Orders table, but only returns rows where the OrderDate is between January 1, 2022 and December 31, 2022 


Another example of a simple sub-query is using the EXISTS operator:


```SQL
SELECT *
FROM Customers
WHERE EXISTS (
    SELECT *
    FROM Orders
    WHERE Orders.CustomerID = Customers.CustomerID
    AND OrderDate BETWEEN '2022-01-01' AND '2022-12-31'
)


```

In this example, the sub-query returns true or false depending on whether there are any orders for each customer during the specified time period. The outer query then returns all columns from the Customers table for those customers with at least one order during the specified time period.


## Correlated Sub-Queries


A correlated sub-query is a nested query that depends on the outer query for its result. That is, the sub-query is executed for each row of the outer query and can return different results depending on the values of the outer query.

Here's an example of a correlated sub-query:


```SQL
SELECT *
FROM Customers
WHERE EXISTS (
    SELECT *
    FROM Orders
    WHERE Orders.CustomerID = Customers.CustomerID
    AND OrderDate BETWEEN '2022-01-01' AND '2022-12-31'
)


```


In this example, the outer query selects all columns from the Customers table, but only returns rows where the sub-query returns at least one row. The sub-query selects all columns from the Orders table, but only returns rows where the CustomerID matches the CustomerID in the outer query and the OrderDate is between January 1, 2022 and December 31, 2022.




## Best Practices


When using sub-queries in MSSQL, there are a few best practices to keep in mind:

__1) Sub-quarries over correlated sub-quarries__

<ul>
<li> 
Simple sub-queries are faster than correlated sub-queries because they can be executed independently of the outer query. This means that MSSQL can optimize the execution plan of the query and reduce the number of scans required to retrieve the data. Correlated sub-queries, on the other hand, are executed for each row of the outer query and can lead to slow performance and high resource consumption. 
</li> 
</ul>



__2) Avoid using sub-queries in the SELECT clause__ 

<ul>
<li> 
Using sub-queries in the SELECT clause can cause performance issues because MSSQL has to execute the sub-query for each row returned by the outer query. This can result in a high number of scans and slow down the query. Instead, try to use JOINs or CTEs (Common Table Expressions) to retrieve the necessary data. 
</li> 
</ul>


__3) Sub-queries in the WHERE and JOIN__


<ul>
<li> 
The WHERE clause and JOIN clause are the most common places to use sub-queries in MSSQL. These clauses allow you to filter and join data based on the result of another query. When using sub-queries in these clauses, try to make them as simple as possible to improve performance.
</li> 
</ul>




__4) Use the EXISTS operator instead of IN or NOT IN if you only need to check for the existence of a row__


<ul>
<li> 
The EXISTS operator is generally faster than using the IN or NOT IN operators when checking for the existence of a row. This is because the EXISTS operator only needs to find one matching row to return a result, whereas the IN or NOT IN operators need to find all matching rows. If you only need to check for the existence of a row, consider using the EXISTS operator to improve performance.
</li> 
</ul>



## Conclusion

Sub-queries in MSSQL are a powerful tool for retrieving data that depends on the results of another query. Whether you're using simple sub-queries or correlated sub-queries, it's important to follow best practices and use sub-queries judiciously to ensure optimal performance go ahead and unleash the power of nested queries in your MSSQL queries, and take your data retrieval to the next level. But remember to follow best practices when using sub-queries, and always test your queries to ensure they are efficient. With a little practice, you'll be able to use sub-queries to their full potential and create complex queries with ease.

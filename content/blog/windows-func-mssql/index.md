---
title: "Windows Functions in MSSQL: How to Be the Life of the SQL Party"
subtitle: ""
excerpt: "Take your SQL skills to the next level with the almighty window functions"
date: 2023-01-21
author: "Elad Oz Cohen"
draft: false
# layout options: single, single-sidebar
layout: single
categories:
---

Are you tired of writing repetitive SQL queries that perform the same calculation over and over again? Do you want to be the life of the SQL party and impress your colleagues with your newfound SQL skills? Well, look no further than windows functions in MSSQL!

Windows functions, also known as windowed or analytic functions, are a powerful feature in MSSQL that allow you to perform calculations across a set of rows that are related to the current row. In other words, windows functions let you calculate a value based on a window of rows that surrounds the current row.



But don't let the name "windows functions" fool you - we're not talking about Microsoft Windows here. In fact, you don't even need a window to use windows functions. All you need is an SQL and a sense of humor (okay, maybe the sense of humor is optional).



To get started with windows functions, you'll need to know a few key terms. The first term is "partitioning", which refers to grouping rows together based on a specific criteria. The second term is "ordering", which refers to sorting the rows within each partition. The third term is "window frame", which refers to the subset of rows within a partition that is used to calculate the function.


The general syntax for using windows functions is as follows:

```SQL
<window function> OVER ( [ <PARTITION BY clause> ] [ <ORDER BY clause> ] [ <ROWS or RANGE clause> ] )

```
<br>

* The _window function_ is the name of the function you want to apply to the windowed set of rows (e.g. SUM, AVG, RANK).
* The _PARTITION BY_ clause is optional, and allows you to group rows together based on a specific criteria.
* The _ORDER BY_ clause is optional, and allows you to sort the rows within each partition.
* The _ROWS_ or _RANGE_ clause is optional, and specifies the subset of rows within a partition that is used to calculate the function.

Now, let's take a look at some examples of windows functions in action.

<br>

## Example 1: Running Total

Have you ever needed to calculate a running total in SQL? With windows functions, it's a breeze. Here's an example:

<br>

```SQL
SELECT OrderID, OrderDate, Quantity, 
       SUM(Quantity) OVER (ORDER BY OrderDate) AS RunningTotal
FROM Sales

```
<br>


In this example, we're calculating a running total of the Quantity column in the Sales table, ordered by the OrderDate column. The SUM function is used to calculate the running total, and the OVER clause specifies the window frame (in this case, all rows ordered by the OrderDate column).


<br>
<br>
<br>

## Example 2: Moving Average
<br>
If you want to calculate a moving average in SQL, windows functions have got you covered. Here's an example:

<br>

```SQL
SELECT OrderID, OrderDate, Quantity, 
       AVG(Quantity) OVER (ORDER BY OrderDate 
                           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS MovingAvg
FROM Sales


```
<br>

In this example, we're calculating a moving average of the Quantity column in the Sales table, ordered by the OrderDate column. The AVG function is used to calculate the moving average, and the ROWS BETWEEN 2 PRECEDING AND CURRENT ROW clause specifies the window frame (in this case, the current row and the two preceding rows).

<br>
<br>
<br>

## Example 3: Rank

Need to rank rows based on a specific criteria? Windows functions have got your back. Here's an example:

<br>

```SQL
SELECT CustomerID, OrderID, OrderDate, 
       RANK() OVER (PARTITION BY CustomerID 
                    ORDER BY OrderDate) AS OrderRank
FROM Sales

```
<br>

In this example, we're ranking the rows in the Sales table by the OrderDate column, within each partition of the CustomerID column. The RANK function is used to calculate the rank, and the PARTITION BY clause specifies the partitioning.

<br>
<br>
<br>


## Example 4: LEAD and LAG

The LEAD and LAG commands are windows functions that allow you to access the values of a column in a row that is a certain number of rows ahead (LEAD) or behind (LAG) the current row. These commands can be useful when you need to perform calculations that involve comparing data in different rows.

Here's an example of using the LEAD command:


```SQL
SELECT OrderID, OrderDate, Quantity,
       LEAD(Quantity, 1, 0) OVER (ORDER BY OrderDate) AS NextQuantity
FROM Sales

```



In this example, we're using the LEAD command to access the value of the Quantity column in the row that is one row ahead of the current row, ordered by the OrderDate column. The 1 in the LEAD function specifies the offset, which in this case is one row ahead of the current row. The 0 in the LEAD function specifies the default value to return if there is no next row.

Here's an example of using the LAG command:


```SQL
SELECT OrderID, OrderDate, Quantity,
       LAG(Quantity, 1, 0) OVER (ORDER BY OrderDate) AS PrevQuantity
FROM Sales

```




In this example, we're using the LAG command to access the value of the Quantity column in the row that is one row behind the current row, ordered by the OrderDate column. The 1 in the LAG function specifies the offset, which in this case is one row behind the current row. The 0 in the LAG function specifies the default value to return if there is no previous row.

<br>
<br>
<br>


## Conclusion

Windows functions in MSSQL are a powerful tool for performing calculations across a set of related rows. With windows functions, you can easily calculate running totals, moving averages, rankings, and access values from rows ahead or behind the current row. And with a sense of humor (and a little practice), you can become the life of the SQL party.

So, next time you find yourself writing a repetitive SQL query, remember the power of windows functions and use them to simplify your code and impress your colleagues. And who knows, maybe you'll even get a laugh or two out of your witty SQL skills.
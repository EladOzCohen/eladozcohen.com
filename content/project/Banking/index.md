---
author: Elad Oz Cohen
categories:
#- Theme Features
- SQL
#- package
date: "2023-04-10"
draft: false

#- sub-titles
excerpt: Analyzing and extracting valuable insights from large bank marketing campaign data set.

layout: single

links:
#- icon: door-open
#  icon_pack: fas
#  name: website
#  url: https://bakeoff.netlify.com/ 
#- icon: github
#  icon_pack: fab
#  name: code
#  url: 
subtitle: 
tags:
- hugo-site

#- the following is the main title.
title: SQL Marketing Campaign Analysis

---


---

## Q1

#### Investigating the conversion rate for both the continues and categorical variables in the data set.The goal is to to stop which features are associated with higher conversion rate (note: conversion rate is the ratio between the number of sales to leads)



 The continues variables:

```{SQL}

SELECT y, 
ROUND(AVG(age),2) 'Average Age', 
ROUND(AVG(emp_var_rate),2) 'Average Employee Varation Rate',
ROUND(AVG(CPI_index),2) 'CPI index', 
ROUND(AVG(cons_conf_index),2) 'Consumer confidence index'
FROM bank_data
GROUP BY y

```


The categorical variables:

```{SQL}

SELECT job, ROUND(AVG(y),2) 'Convertion Rate'
FROM bank_data
GROUP BY job
HAVING job != 'unknown'
ORDER BY 2 DESC



SELECT campaign, ROUND(AVG(y),2) 'Convertion Rate'
FROM bank_data
GROUP BY campaign
ORDER BY 1 DESC



SELECT contact, ROUND(AVG(y),2) 'Convertion Rate'
FROM bank_data
GROUP BY contact
ORDER BY 1 DESC



SELECT education, ROUND(AVG(y),2) 'Convertion Rate'
FROM bank_data
GROUP BY education
HAVING education != 'unknown'
ORDER BY 2 DESC



SELECT TOP 10 pdays, ROUND(AVG(y),2) 'Convertion Rate'
FROM bank_data
GROUP BY pdays
HAVING pdays != 0
ORDER BY 1 ASC

```

The result of the previous analysis indicates:

a) Conversion rate is not significantly effected by either age, employee variation rate, CPI index score, and    consumer confidence.

b) The campaign's should on: 
    (1) Focus on the students and illiterate population as these have the highest conversion rate.
    (2) Focus costumers that yielded a sale on previous campaigns.
    (3) Focus on customers who was has been contacted by the bank in the recent days.





## Q2 - Seasonal Effects

#### In this analysis I investigate the existence of seasonal effects in the campaign.To put more simply: whether the conversation rate was higher in a particular time period.



```{SQL}
SELECT month,COUNT(*) as 'Sampels',ROUND(AVG(y),2)  as '% yes'
FROM bank_data
GROUP BY month
ORDER BY 3




SELECT day_of_week,COUNT(*) as 'Sampels', ROUND(AVG(y),2)  as '% yes'
FROM bank_data
GROUP BY day_of_week
ORDER BY 3
```





It appears that although conversion rate is stable across all sampled days of the weeks,
conversion rate was high on the months: September, October, November, and March.
In addition, 


















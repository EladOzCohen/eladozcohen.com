/* Pre-processing stage where I change the dependent variable 'y' a numerical variable
with 1 and 0 instead of "yes" and "no".  


UPDATE bank_data
SET y = CASE WHEN y = 'yes' THEN 1 ELSE 0 END;


ALTER TABLE bank_data
ALTER COLUMN y FLOAT;

*/





/* Q1: The continues and categorical data analysis*/


SELECT y 'Campaign Result', 
ROUND(AVG(age),2) 'Average Age', 
ROUND(AVG(emp_var_rate),2) 'Average Employee Varation Rate',
ROUND(AVG(CPI_index),2) 'CPI index', 
ROUND(AVG(cons_conf_index),2) 'confidence index'
FROM bank_data
WHERE Duration > 10
GROUP BY y
/* Looks like emp_var_rate between [-3.4, -1.7] contributes to saying yes */






/* The Continues */


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












/* Conclusion: The banks should contact: students + people non-previosly contacted + via cellular + illiterates and people without education +
people who's previosly been campaigned  + few days past */




/* Q2 testing for seasonal effects */


SELECT day_of_week,COUNT(*) as 'Sampels', ROUND(AVG(y),2)  as 'Convertion Rate'
FROM bank_data
GROUP BY day_of_week
ORDER BY 3



SELECT month,COUNT(*) as 'Sampels',ROUND(AVG(y),2)  as 'Convertion Rate'
FROM bank_data
GROUP BY month
ORDER BY 3







/* Conclusion: it looks like the time around septemer-october was the msot fruitful for campaigning. */




/* Q3: What is the average campaign duration for customers who subscribed to a term deposit,
		and how does it differ by month and education level??*/

WITH term_subscribed AS (
	SELECT *
    FROM bank_data
    WHERE y = 1
	)

SELECT education, month, ROUND(AVG(Duration),2) as 'Campaign Duration'
FROM term_subscribed 
GROUP BY education, month
HAVING education != 'unknown'
ORDER BY education, month





/* Conclusion: overall,

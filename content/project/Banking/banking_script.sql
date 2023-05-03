/* Pre-processing stage where I change the dependent variable 'y' a numerical variable
with 1 and 0 instead of "yes" and "no".  


UPDATE bank_data
SET y = CASE WHEN y = 'yes' THEN 1 ELSE 0 END;


ALTER TABLE bank_data
ALTER COLUMN y FLOAT;

*/



/* Q1: */
/*cpi index
cons_conf_index
emp_var_rate*/

SELECT * 
FROM bank_data
ORDER BY age



--- Note that the percentage of responding 'yes' from all people was calcualted using the AVG.


/*Checking for education -- There isn't a clear effect for education */
SELECT education, COUNT(education) as 'num education', SUM(y) 'num yes', ROUND(AVG(y),2) '% of yes'
INTO  #education_table
FROM bank_data
GROUP BY education






/* Checking for age -- Overall, there isn't a clear effect for age */
SELECT age, COUNT(age) as 'num age', SUM(y) 'num yes', ROUND(AVG(y),2)
FROM bank_data
GROUP BY age
ORDER BY age










/*Checking for emp_var_rate -- Looks like emp_var_rate between [-3.4, -1.7] contributes to saying yes */
SELECT emp_var_rate, ROUND(AVG(y),2)
FROM bank_data
GROUP BY emp_var_rate
ORDER BY 2


/* Checking for marrige status - no effect */
SELECT marital, AVG(y)
FROM bank_data
GROUP BY marital

/* Checking for channel of communication - looks like cellular is better then telephone*/
SELECT contact,COUNT(contact), AVG(y)
FROM bank_data
GROUP BY contact


/* Checking for number of previous campaigns - customers who have been contacted max(3) times. */
SELECT campaign, AVG(y)
FROM bank_data
GROUP BY campaign
ORDER BY 2


/* Checking job types - studets, retired, and unemployed */
SELECT job, ROUND(AVG(y),2)
FROM bank_data
GROUP BY job
ORDER BY 2




SELECT emp_var_rate,CPI_index, cons_conf_index, ROUND(AVG(y),2)
FROM bank_data
GROUP BY emp_var_rate,CPI_index, cons_conf_index
ORDER BY 4





SELECT age,COUNT(y), AVG(y)
FROM bank_data
GROUP BY age
ORDER BY age

/* Q1: */


SELECT y 'Campaign Result', 
ROUND(AVG(age),2) 'Average Age', 
ROUND(AVG(emp_var_rate),2) 'Average Employee Varation Rate',
ROUND(AVG(CPI_index),2) 'CPI index', 
ROUND(AVG(cons_conf_index),2) 'confidence index'
FROM bank_data
WHERE Duration > 10
GROUP BY y
/* Looks like emp_var_rate between [-3.4, -1.7] contributes to saying yes */








/* Q2: */

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


/* Result of previous campaigns - previous success predicts future success */

SELECT poutcome, ROUND(AVG(y),2)
FROM bank_data
GROUP BY poutcome
ORDER BY 2





/* Conclusion: The banks should contact: students + people non-previosly contacted + via cellular + illiterates and people without education +
people who's previosly been campaigned  + few days past */








/* Q3: */



SELECT month,COUNT(*) as 'Sampels',ROUND(AVG(y),2)  as '% yes'
FROM bank_data
GROUP BY month
ORDER BY 3




SELECT day_of_week,COUNT(*) as 'Sampels', ROUND(AVG(y),2)  as '% yes'
FROM bank_data
GROUP BY day_of_week
ORDER BY 3


/* Conclusion: it looks like the time around septemer-october was the msot fruitful for campaigning. */




/* Q4: */
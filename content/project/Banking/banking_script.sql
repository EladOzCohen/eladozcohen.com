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


-- There isn't a clear effect for education....
SELECT education, COUNT(education) as 'num education', SUM(y) 'num yes', ROUND(AVG(y),2) '% of yes'
FROM bank_data
GROUP BY education






-- Overall, there isn't a clear effect for age... (notice that the yougn and old were disproportionaly UNDERSAMPELD)
SELECT age, COUNT(age) as 'num age', SUM(y) 'num yes', ROUND(AVG(y),2)
FROM bank_data
GROUP BY age
ORDER BY age




--- It kinda looks like that around septemer-october people are more inclined to 'yes' (seasonal effect??)
SELECT month, day_of_week, COUNT(y) 'count' ,AVG(y) '% yes'
FROM bank_data
GROUP BY month, day_of_week
ORDER BY 4




/* Q2: */

/* GPT ideas:
What factors are most strongly associated with a customer's decision to subscribe to a term deposit? For example, does age, education level, or employment status have a significant impact on whether or not a customer subscribes? This can be answered using SQL queries that analyze the relationship between various demographic and socioeconomic factors and the subscription outcome.

Are there any seasonal patterns in the success of the marketing campaign? For example, do customers tend to be more likely to subscribe during certain months of the year or during certain holidays or events? This can be answered using SQL queries that group the data by date and analyze the subscription rates over time.

How do the characteristics of the customers who subscribe to term deposits differ from those who do not? For example, are subscribers more likely to have higher incomes, larger account balances, or longer tenure with the bank? This can be answered using SQL queries that compare the demographic and socioeconomic characteristics of subscribers and non-subscribers.

How does the success of the marketing campaign vary by the communication channels used? For example, are customers more likely to subscribe if they are contacted by phone, email, or SMS? This can be answered using SQL queries that group the data by communication channel and analyze the subscription rates for each channel.

*/




/* Q3: */





/* Q4: */
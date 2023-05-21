---
author: Elad Oz Cohen
categories:
#- Theme Features
 - SQL
#- package
date: "2023-01-15"
draft: false
excerpt: Using MSSQL & Tableu, I extract intriguing insights on the relationship between infections rate, mortality and vaccinations. Skills used - CTE, DML, Joins, Group By, Unions.


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
title: SQL Data Analysis - Covid-19

---

---


Data used: https://ourworldindata.org/
<br>




### Q1: Exploring infections death rates both at a global scale and at a continent scale.



```SQL
/* Using CTE to create a derived table with the relevant data at the continent scale */
WITH continents_average AS (
    SELECT 'Continent Average' AS 'Location', 
           CONVERT(DATE,v.date,103) AS 'Date',
           ROUND(SUM(cd.new_cases)/COUNT(DISTINCT cd.continent),0) AS 'New Infections',
           ROUND(SUM(v.daily_vaccinations)/COUNT(DISTINCT cd.continent),0) AS 'Vaccinations',
           SUM(CAST(cd.new_deaths AS INT))/COUNT(DISTINCT cd.continent) AS 'New Deaths'
    FROM vaccinations v 
    INNER JOIN coviddeaths cd ON cd.date = v.date AND cd.iso_code = v.iso_code
    WHERE cd.Location NOT LIKE '%income%' AND cd.Location NOT LIKE '%world%' AND cd.Location != cd.continent
    GROUP BY CONVERT(DATE,v.date,103)
),

/* Creating another CTE to create a derived table with the relevant data for the global scale */
continents_cases AS (
    SELECT cd.continent AS 'Location',
           CONVERT(DATE,v.date,103) AS 'Date',
           SUM(cd.new_cases) AS 'New Infections',
           SUM(v.daily_vaccinations) AS 'Vaccinations',
           SUM(CAST (cd.new_deaths AS INT)) AS 'New Deaths'
    FROM vaccinations v 
    INNER JOIN coviddeaths cd ON cd.date = v.date AND cd.location = v.location
    WHERE cd.Location NOT LIKE '%income%' AND cd.Location NOT LIKE '%world%' AND cd.Location != cd.continent
    GROUP BY cd.continent, CONVERT(DATE,v.date,103)
)

/* Combining the two tables using UNION ALL */
SELECT 'Continent Average' AS 'Location', 
       [Date], 
       [New Infections], 
       [Vaccinations], 
       [New Deaths]
FROM continents_average
UNION ALL
SELECT [Location], 
       [Date], 
       [New Infections], 
       [Vaccinations], 
       [New Deaths]
FROM continents_cases;
```

### Visual Results
<img loading = "lazy" src ="https://camo.githubusercontent.com/76ac060345d562b724f2320c07806c1735d4cb917e6603dd53001857a4a3026e/68747470733a2f2f7075626c69632e7461626c6561752e636f6d2f7374617469632f696d616765732f51312f51315f576f726b426f6f6b2f44617368626f617264312f315f7273732e706e67">



<br>
<br>
<br>


### Q2: Investigating what are the top 10 countries with the highest percentage of their population fully vaccinated.

Note: The calculation was executed for large countries defined as countries with population over 3 million citizens 


```SQL
/* Creating a temporary table having the calculated column percentage of population fully vaccinated, along with some descriptive information */

DROP TABLE IF EXISTS my_fully_vac_table;

SELECT v.location AS 'Country/Territory',
       v.people_fully_vaccinated,
       v.date,
       cd.population,
       (v.people_fully_vaccinated/cd.population)* 100 AS 'Percent Population Fully Vaccinated'
INTO my_fully_vac_table
FROM  vaccinations v 
INNER JOIN coviddeaths cd ON cd.date = v.date AND cd.location = v.location
WHERE cd.location != cd.continent /* Removing duplicated rows from the dataset */
GROUP BY v.location, v.people_fully_vaccinated ,cd.population, v.date
HAVING cd.population > 3000000;


/* Creating another temporary table that contains the relevant information of the top 10 countries that were the first to reach herd immunity (70% of population fully vaccinated) */

DROP TABLE IF EXISTS top_10_vac;

SELECT TOP 10 [Country/Territory], 
             MAX(ROUND([Percent Population Fully Vaccinated],2)) AS 'Percent Vaccinated' 
INTO top_10_vac
FROM my_fully_vac_table
GROUP BY [Country/Territory]
HAVING MAX([Percent Population Fully Vaccinated]) <= 100 /* Note: due to vaccination of non-residence, some countries exceeded vaccinating 100% of their population, thus removed from output*/
ORDER BY 2 DESC;


SELECT * 
FROM top_10_vac;
```


<img loading = "lazy" src= https://camo.githubusercontent.com/989e42c74d2d5b15669078b40cf4f2314d1949a055c62d007a325843e9936d4c/68747470733a2f2f7075626c69632e7461626c6561752e636f6d2f7374617469632f696d616765732f51322f51325f576f726b426f6f6b2f44617368626f617264312f315f7273732e706e67>

<br>
<br>
<br>

#### Here I'm creating (and pre-processing) data i'll be using in the next questions.



```SQL
/*Creating a temporary table and inserting the relevent data + */
DROP TABLE IF EXISTS percent_table;

CREATE TABLE  percent_table (Country NVARCHAR(20), 
              fully_vaccinated BIGINT, 
              population_size BIGINT,
              date_time DATE, 
              percent_fully_vaccinated FLOAT);


INSERT INTO percent_table(Country, fully_vaccinated, population_size, date_time, percent_fully_vaccinated)

SELECT  v.location,
		v.people_fully_vaccinated,
		cd.population,
		cd.date,
	    (v.people_fully_vaccinated/cd.population)* 100 
FROM  vaccinations v INNER JOIN coviddeaths  cd ON cd.date = v.date AND cd.location = v.location
WHERE ((v.people_fully_vaccinated/cd.population)* 100) >= 70  /* This condition filters countries who vaccinated less then 70% of their population*/ 

     AND
     
	   cd.location NOT LIKE '%income%' AND cd.Location NOT LIKE '%world%' /* This condition removes irrelevent observations for the current analysis (mainly: global and regional data) */


GROUP BY v.location, cd.date, v.people_fully_vaccinated ,cd.population
HAVING cd.population > 3000000 




/* Finally, deleting countries with over 100% of population vaccintaed.
(note: these countries are small countries that also vaccinated non-residence people in their teritory.)*/

DELETE FROM percent_table
WHERE Country IN (
    SELECT Country
    FROM percent_table
    WHERE percent_fully_vaccinated > 100)


```





## Q3: Listing the first 10 countries that were the first to reach herd immunity.
Note: Although a controversial topic, for the sake of practice I choose to define herd immunity as countries that at least 70% of their population is fully vaccinated.


```SQL
WITH temp_table
AS(
SELECT *, ROW_NUMBER() OVER(PARTITION BY Country ORDER BY percent_fully_vaccinated) 'ranked'
FROM percent_table)


SELECT  TOP 10 Country,  date_time, percent_fully_vaccinated
FROM temp_table
WHERE ranked = 1
ORDER BY date_time
```



| Country | Date |
|---------|------|
|Uruguay | 2021-08-12|
|Singapore | 2021-08-14|
|Portugal | 2021-08-27|
|Belgium | 2021-08-30|
|Denmark | 2021-08-31|
|Spain	| 2021-08-31|
|Chile | 2021-09-02|
|Ireland | 2021-09-06|
|China | 2021-09-15|
|Wales |2021-09-24|


<br>
It appears that not all those who were to first to reach herd immunity also ended being the most (fully) vaccinated countries. Perhaps the rate of vaccinations in former countries reached a plateau upon reaching herd immunity. The next question investigates this hypothesis.

<br>
<br>
<br>



### Q4: Investegating how the vacination rates have changed across time for top countries who were among the first to reach herd immunity but weren't also the top countries who vaccinated most of their population.

```SQL

/*Using CTE and windows-functions, extracting the relevent data for those countries 
who were the first to reach herd immunity while not beign the top country to fully vaccinate their population. */


WITH ranked_countries
AS(
SELECT *, ROW_NUMBER() OVER(PARTITION BY Country ORDER BY percent_fully_vaccinated) 'ranked'
FROM percent_table),

herd_table
AS (
	SELECT  TOP 10 Country,  date_time, percent_fully_vaccinated
	FROM ranked_countries
	WHERE ranked = 1
	ORDER BY date_time),
	
	
top_vac
AS(
	SELECT v.location 'Country',
	v.people_fully_vaccinated,
	cd.population,
	(v.people_fully_vaccinated/cd.population)* 100 'Percent Population Fully Vacinated'
	FROM  vaccinations v INNER JOIN coviddeaths  cd 
	ON cd.date = v.date AND cd.location = v.location
	WHERE cd.location != cd.continent
	GROUP BY v.location, v.people_fully_vaccinated ,cd.population
	HAVING cd.population > 3000000)





SELECT *
FROM my_fully_vac_table
WHERE Country IN 
				(SELECT Country
				FROM herd_table 
				WHERE Country NOT IN (SELECT Country FROM top_10_vac))

ORDER BY Country, date
```

<br>


<img loading = "lazy" src = https://camo.githubusercontent.com/0f3d279f305391beceb0c2f8005f4a3fd52ca2aee66da686f560346f413442a6/68747470733a2f2f7075626c69632e7461626c6561752e636f6d2f7374617469632f696d616765732f436f2f436f7669642d31395175657374696f6e342f44617368626f617264312f315f7273732e706e67>

<br>
<br>

It appears my hypothesize is correct as the slope of the vaccination rate is reaching asymptotic around august, which is the month that most countries in Q2 have reached herd immunity.




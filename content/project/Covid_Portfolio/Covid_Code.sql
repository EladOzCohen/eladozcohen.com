/* Elad Oz cohen Portfolio Project */

SELECT * FROM CovidDeaths -- The data was last in 14/02/2023

/*  CovidDeaths:
1) continent 
2) location - country
3) date
4) total cases - CUMSUM of covid cases.
5) new cases - new cases in that day
6) total_deaths 
7) new_deaths
8) median_age
9) hosp_patients - patients hospitalized.
10) positivity_rate - share of tests that came out as positive. 
11) popultion - population size
10) diabetes_prevalence
11) hospital_bed_per_thousand */


/* Vaccinations:
1) location
2) date
3) total_vaccinations - CUMSUM of total SHOTS administerd
4) people vaccinated - CUMSUM total number of people who received at least one SHOT.
5) people_fully_vaccinated - CUMSUM people who recieved two shots.
6) daily_vaccinations -  total SHOTS administerd in that day.
*/



USE covidport
SELECT * FROM CovidDeaths 
SELECT * FROM vaccinations


/* Need to make new datasets, cleansed with values of continents and world (this creating duplicates */





-- Q1 Exploring infections the death rates globally and by continents. 


WITH continents_average 
AS (
SELECT  'Continent Average' as 'Location', 
	      CONVERT(DATE,v.date,103) 'Date',
		  ROUND(SUM(cd.new_cases)/COUNT(DISTINCT cd.continent),0) 'New Infections',
		  ROUND(SUM(v.daily_vaccinations)/COUNT(DISTINCT cd.continent),0) 'Vaccinations',
		  SUM(CAST(cd.new_deaths AS INT))/COUNT(DISTINCT cd.continent) 'New Deaths'
FROM vaccinations v INNER JOIN coviddeaths cd 
ON cd.date = v.date AND cd.iso_code = v.iso_code
WHERE cd.Location NOT LIKE '%income%' AND cd.Location NOT LIKE '%world%' AND cd.Location != cd.continent
GROUP BY CONVERT(DATE,v.date,103)),




continents_cases
AS (
SELECT cd.continent 'Location',
	   CONVERT(DATE,v.date,103) 'Date',
	   SUM(cd.new_cases) 'New Infections',
	   SUM(v.daily_vaccinations) 'Vaccinations',
	   SUM(CAST (cd.new_deaths AS INT)) 'New Deaths'
		FROM vaccinations v INNER JOIN coviddeaths  cd 
		ON cd.date = v.date AND cd.location = v.location
	WHERE cd.Location NOT LIKE '%income%' AND cd.Location NOT LIKE '%world%' AND cd.Location != cd.continent
		GROUP BY cd.continent, CONVERT(DATE,v.date,103))





SELECT *  FROM continents_average
UNION ALL
SELECT *  FROM continents_cases









-- Q2: Investigating what are the top 10 countries that fully vaccinated their population.
-- Note: The calculation was executed for large countries defined as countries with population over 3 million citizens.
DROP TABLE IF EXISTS my_fully_vac_table
SELECT v.location 'Country',
		v.people_fully_vaccinated,
		v.date,
		cd.population,
	   (v.people_fully_vaccinated/cd.population)* 100 'Percent Population Fully Vacinated'
	   INTO my_fully_vac_table -- Creating a temporary table 
FROM  vaccinations v INNER JOIN coviddeaths  cd 
ON cd.date = v.date AND cd.location = v.location
WHERE cd.location != cd.continent
GROUP BY v.location, v.people_fully_vaccinated ,cd.population, v.date
HAVING cd.population > 3000000


DROP TABLE IF EXISTS top_10_vac
SELECT TOP 10 Country, MAX(ROUND([Percent Population Fully Vacinated],2)) AS 'Percent Vaccinated' 
INTO top_10_vac
FROM my_fully_vac_table
GROUP BY Country
HAVING MAX([Percent Population Fully Vacinated]) <= 100 /*Note: due to vaccination of non-residentce, some contries
														exceded vacinating 100% of their population, thus removed from output*/
ORDER BY 2 DESC



SELECT * 
FROM top_10_vac






/* 
Creating and cleaning the table I'll be using in the next questions.
*/

DROP TABLE IF EXISTS percent_table
CREATE TABLE percent_table (Country NVARCHAR(20), fully_vaccinated BIGINT, population_size BIGINT ,date_time DATE, percent_fully_vaccinated FLOAT)


INSERT INTO percent_table(Country, fully_vaccinated, population_size, date_time, percent_fully_vaccinated)

SELECT v.location,
		v.people_fully_vaccinated,
		cd.population,
		cd.date,
	   (v.people_fully_vaccinated/cd.population)* 100 
FROM  vaccinations v INNER JOIN coviddeaths  cd ON cd.date = v.date AND cd.location = v.location
WHERE ((v.people_fully_vaccinated/cd.population)* 100) >= 70  AND -- keeping only those who crossed the "herd immunity" threshold.
	   cd.location NOT LIKE '%income%' AND cd.Location NOT LIKE '%world%' -- removing non-relevent observations.


GROUP BY v.location, cd.date, v.people_fully_vaccinated ,cd.population
HAVING cd.population > 3000000 


DELETE FROM percent_table
WHERE Country IN (
    SELECT Country
    FROM percent_table
    WHERE percent_fully_vaccinated > 100)








-- Q3) Listing the countries that were the first to reach herd immunity.
-- Note: Although a controversial topic, for the sake of practice I choose to define herd immunity as countries that at least 70% of their population is fully vaccinated.

WITH temp_table
AS(
SELECT *, ROW_NUMBER() OVER(PARTITION BY Country ORDER BY percent_fully_vaccinated) 'ranked'
FROM percent_table)



SELECT  TOP 10 Country,  date_time, percent_fully_vaccinated
FROM temp_table
WHERE ranked = 1
ORDER BY date_time







/* it appears that not all countries who reached herd immunity were also the top countries who vaccinated most of their population. 
I hypothesize suspect that once the countries reached herd immunity they relaxed the'ir vaccination effort 

Let's test it! */







-- Q4: Investegating how the vacination rates have changed across time for countries top countries who were first to reach herd immunity but weren't also th etop counttries who vaccinated most of their population.


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

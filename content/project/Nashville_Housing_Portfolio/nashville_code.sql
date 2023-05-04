
/* Q1: */
SELECT 
	[Land Use],
    YEAR([Sale Date]) AS [Year], 
    AVG([Sale Price]) AS Average_Sale_Price, 
    AVG([Sale Price]) OVER(PARTITION BY (YEAR([Sale Date]))) AS [Overall Average Sale Price]
    --CONCAT(ROUND(((AVG([Sale Price]) - AVG([Sale Price]) OVER(PARTITION BY [Sale Year]))/AVG([Sale Price]) OVER(PARTITION BY [Sale Year]))*100,2),'%') AS Difference
FROM 
    Housing
GROUP BY 
    [Sale Date], [Sale Price],[Land Use]
ORDER BY 
    [Sale Year]











/* Q2: */
WITH neighborhood_sale_price AS (
    SELECT 
        Neighborhood, 
        AVG(CASE WHEN YEAR([Sale Date]) = 2013 THEN [Sale Price] END) AS Avg_Sale_Price_2013, 
        AVG(CASE WHEN YEAR([Sale Date]) = 2016 THEN [Sale Price] END) AS Avg_Sale_Price_2016
    FROM Housing
    GROUP BY Neighborhood
)


SELECT 
    Neighborhood,
    Avg_Sale_Price_2013,
    Avg_Sale_Price_2016,
    CONCAT(ROUND(((Avg_Sale_Price_2016 - Avg_Sale_Price_2013)/Avg_Sale_Price_2013)*100,2),'%') AS Percentage_Increase,
    RANK() OVER (ORDER BY ((Avg_Sale_Price_2016 - Avg_Sale_Price_2013)/Avg_Sale_Price_2013) DESC) AS Rank1
FROM 
    neighborhood_sale_price
ORDER BY 
    Rank1;

	



SELECT * FROM Housing
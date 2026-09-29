-- Query 1: Top 10 Most Expensive Towns/Cities (Min 20 Transactions to avoid outliers)
SELECT 
    town_city,
    COUNT(*) AS total_sales,
    ROUND(AVG(price), 0) AS avg_price,
    CAST(MEDIAN(price) AS BIGINT) AS median_price,
    MIN(price) AS min_price,
    MAX(price) AS max_price
FROM sales
WHERE town_city IS NOT NULL AND town_city != ''
GROUP BY town_city
HAVING COUNT(*) >= 20
ORDER BY avg_price DESC
LIMIT 10;

-- Query 2: Price Breakdown by Property Type (Decoding Land Registry codes)
SELECT 
    CASE property_type
        WHEN 'D' THEN 'Detached'
        WHEN 'S' THEN 'Semi-Detached'
        WHEN 'T' THEN 'Terraced'
        WHEN 'F' THEN 'Flat / Maisonette'
        ELSE 'Other'
    END AS property_category,
    COUNT(*) AS total_transactions,
    ROUND(AVG(price), 0) AS avg_price,
    CAST(MEDIAN(price) AS BIGINT) AS median_price
FROM sales
GROUP BY property_type
ORDER BY median_price DESC;

-- Query 3: Window Function - Most Expensive Sale per District
WITH ranked_sales AS (
    SELECT 
        district,
        postcode,
        price,
        property_type,
        ROW_NUMBER() OVER (PARTITION BY district ORDER BY price DESC) as rank_in_district
    FROM sales
    WHERE district IS NOT NULL AND district != ''
)
SELECT 
    district,
    postcode,
    price AS top_price,
    property_type
FROM ranked_sales
WHERE rank_in_district = 1
ORDER BY top_price DESC
LIMIT 10;
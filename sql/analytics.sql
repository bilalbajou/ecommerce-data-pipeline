-- ==========================================
-- E-commerce ETL Pipeline - Analytics Queries
-- ==========================================
-- This file contains analytical queries to generate business insights 
-- from the 'products' table.

-- ------------------------------------------
-- 1. High-Level Summary Metrics
-- ------------------------------------------

-- Total number of products in the catalog
SELECT COUNT(*) AS total_products 
FROM products;

-- Total inventory stock across all products
SELECT SUM(stock) AS total_inventory_stock 
FROM products;

-- Average product price (Original Price)
SELECT ROUND(AVG(price)::numeric, 2) AS average_original_price 
FROM products;

-- Average discount percentage across the catalog
SELECT ROUND(AVG(discount_percentage)::numeric, 2) AS average_discount_percentage 
FROM products;

-- Average customer rating
SELECT ROUND(AVG(rating)::numeric, 2) AS average_rating 
FROM products;


-- ------------------------------------------
-- 2. Product Extremes & Rankings
-- ------------------------------------------

-- Products with the highest final price
SELECT id, title, category, price, discount_percentage, final_price 
FROM products 
ORDER BY final_price DESC 
LIMIT 5;

-- Products with the lowest final price
SELECT id, title, category, price, discount_percentage, final_price 
FROM products 
ORDER BY final_price ASC 
LIMIT 5;

-- Top 10 products by stock (Highest Inventory)
SELECT id, title, category, stock, final_price 
FROM products 
ORDER BY stock DESC 
LIMIT 10;


-- ------------------------------------------
-- 3. Category-Level Insights
-- ------------------------------------------

-- Number of products by category
SELECT category, COUNT(*) AS total_products 
FROM products 
GROUP BY category 
ORDER BY total_products DESC;

-- Average price by category
SELECT category, ROUND(AVG(price)::numeric, 2) AS average_price 
FROM products 
GROUP BY category 
ORDER BY average_price DESC;

-- Average rating by category
SELECT category, ROUND(AVG(rating)::numeric, 2) AS average_rating 
FROM products 
GROUP BY category 
ORDER BY average_rating DESC;

-- Total inventory value by category (final_price * stock)
SELECT category, 
       ROUND(SUM(final_price * stock)::numeric, 2) AS total_inventory_value 
FROM products 
GROUP BY category 
ORDER BY total_inventory_value DESC;


-- ------------------------------------------
-- 4. Actionable Business Segments
-- ------------------------------------------

-- Products with low stock (Threshold: less than 10 items)
-- Useful for re-ordering alerts
SELECT id, title, category, stock 
FROM products 
WHERE stock < 10 
ORDER BY stock ASC;

-- Products with high discount (Threshold: 15% or more)
-- Useful for promotional marketing
SELECT id, title, category, price, discount_percentage, final_price 
FROM products 
WHERE discount_percentage >= 15.0 
ORDER BY discount_percentage DESC;

-- Highly rated products (Rating >= 4.0)
-- Useful for featuring on the homepage
SELECT id, title, category, rating, final_price 
FROM products 
WHERE rating >= 4.0 
ORDER BY rating DESC;

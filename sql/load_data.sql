
-- Loading Dataset

\copy flights FROM 'data/flightsData1m.csv' WITH (FORMAT csv, HEADER true, NULL '');

-- Sanity check
SELECT COUNT(*) FROM flights;
CREATE DATABASE IF NOT EXISTS store;
CREATE TABLE store_status (
    store_id INT,
    timestamp_utc TIMESTAMP,
    status VARCHAR(10),
    PRIMARY KEY (store_id, timestamp_utc)
);

CREATE TABLE store_hours (
    store_id INT,
    day_of_week INT,
    start_time_local TIME,
    end_time_local TIME,
    PRIMARY KEY (store_id, day_of_week)
);

CREATE TABLE store_timezone (
    store_id INT,
    timezone_str VARCHAR(50),
    PRIMARY KEY (store_id)
);

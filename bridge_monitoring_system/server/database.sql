-- 1. Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS shm_db;

-- 2. Switch to the database
USE shm_db;

-- 3. Drop the old table to ensure a clean start with the new schema
DROP TABLE IF EXISTS shm_trend_log;

-- 4. Create the new table (Single MPU + Flex + Float + Vision Predictions)
CREATE TABLE shm_trend_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    natural_freq FLOAT NOT NULL,
    damage_index FLOAT NOT NULL,
    rms_val FLOAT NOT NULL,       -- Single RMS value (MPU6050)
    flex_val FLOAT NOT NULL,      -- Flex Sensor Value (Average)
    float_alert TINYINT NOT NULL, -- Float Sensor (0=Water/Alert, 1=Normal)
    predictions TEXT              -- Stores JSON output from Roboflow/Vision Model
);
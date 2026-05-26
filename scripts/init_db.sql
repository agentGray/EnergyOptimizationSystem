-- Initialize database with TimescaleDB extension and hypertables

-- Enable TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create sensor_readings hypertable after tables are created by SQLAlchemy
-- This will be run after alembic migrations or after init_db()
-- The following is a placeholder that runs on first connection:

DO $$
BEGIN
    -- Check if the sensor_readings table exists before converting
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'sensor_readings'
    ) THEN
        -- Convert to hypertable if not already
        PERFORM create_hypertable(
            'sensor_readings', 
            'timestamp',
            if_not_exists => TRUE,
            migrate_data => TRUE
        );
        
        -- Create continuous aggregate for hourly averages
        -- (uncomment after table exists)
        -- CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_readings_hourly
        -- WITH (timescaledb.continuous) AS
        -- SELECT 
        --     sensor_id,
        --     time_bucket('1 hour', timestamp) AS bucket,
        --     avg(value) AS avg_value,
        --     min(value) AS min_value,
        --     max(value) AS max_value,
        --     count(*) AS reading_count
        -- FROM sensor_readings
        -- GROUP BY sensor_id, bucket;
    END IF;
END $$;

-- Data retention policy: auto-drop data older than 90 days
-- SELECT add_retention_policy('sensor_readings', INTERVAL '90 days', if_not_exists => TRUE);

-- Compression policy: compress chunks older than 7 days
-- SELECT add_compression_policy('sensor_readings', INTERVAL '7 days', if_not_exists => TRUE);

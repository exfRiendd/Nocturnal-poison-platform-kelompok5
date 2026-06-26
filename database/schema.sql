DROP DATABASE IF EXISTS smartcity;
CREATE DATABASE smartcity;
USE smartcity;

-- 1. SHARED TABLES

CREATE TABLE zones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,          
    city_district VARCHAR(100),          
    coordinates VARCHAR(255),
    area_km2 DECIMAL(10,2)
) ENGINE=InnoDB;

-- 2. OAUTH TABLES

CREATE TABLE oauth_clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id VARCHAR(100) NOT NULL UNIQUE,
    client_secret VARCHAR(255) NOT NULL,
    grant_types VARCHAR(255),
    redirect_uris TEXT
) ENGINE=InnoDB;

CREATE TABLE oauth_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id VARCHAR(100) NULL,
    user_id INT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at DATETIME NOT NULL
) ENGINE=InnoDB;

-- 3. CITIZEN SERVICE
 
CREATE TABLE citizen_citizens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nik VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255) NOT NULL DEFAULT '$2b$10$WfZLgdNrLCjktxdOsskbAuU9OiKZD7.NMkQO3ErdUXvEmJmb.gHiG', -- Default hash 'password123'
    phone VARCHAR(20),
    zone_id INT,
    role ENUM('citizen', 'admin') DEFAULT 'citizen',
    age INT NULL CHECK(age BETWEEN 1 AND 120),
    weight_kg DECIMAL(5,2) CHECK(weight_kg BETWEEN 1 AND 500),
    mask_type ENUM('none', 'cloth', 'medical', 'n95') NOT NULL DEFAULT 'none',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_citizen_zone
        FOREIGN KEY (zone_id)
        REFERENCES zones(id)
        ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE citizen_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    citizen_id INT NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    zone_id INT,
    status ENUM('pending', 'investigating', 'resolved') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_report_citizen
        FOREIGN KEY (citizen_id)
        REFERENCES citizen_citizens(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_report_zone
        FOREIGN KEY (zone_id)
        REFERENCES zones(id)
        ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE citizen_notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    citizen_id INT,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    notification_type ENUM('general', 'anomaly_alert') DEFAULT 'general',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notification_citizen
        FOREIGN KEY (citizen_id)
        REFERENCES citizen_citizens(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE citizen_devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(100) NOT NULL UNIQUE,
    citizen_id INT NULL,
    device_label VARCHAR(100) NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM(
        'active',
        'inactive'
    ) DEFAULT 'active',
    last_seen_at TIMESTAMP NULL,

    CONSTRAINT fk_device_citizen
        FOREIGN KEY (citizen_id)
        REFERENCES citizen_citizens(id)
        ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE citizen_activity_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,

    citizen_id INT NOT NULL,
    citizen_device_id INT NULL,
    zone_id INT NOT NULL,
    activity_type ENUM(
        'rest',
        'walking',
        'running'
    ) NOT NULL,
    avg_heart_rate DECIMAL(5,2) NOT NULL,
    max_heart_rate DECIMAL(5,2) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP NULL,
    duration_minutes INT NULL,

    status ENUM(
        'active',
        'completed'
    ) NOT NULL DEFAULT 'active',

    CONSTRAINT fk_session_citizen
        FOREIGN KEY (citizen_id)
        REFERENCES citizen_citizens(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_session_zone
        FOREIGN KEY (zone_id)
        REFERENCES zones(id)
        ON DELETE NO ACTION,
    
    CONSTRAINT fk_session_device
        FOREIGN KEY (citizen_device_id)
        REFERENCES citizen_devices(id)
        ON DELETE SET NULL

) ENGINE=InnoDB;

CREATE TABLE citizen_health_exposures (
    id INT AUTO_INCREMENT PRIMARY KEY,

    citizen_id INT NOT NULL,
    session_id INT NOT NULL,
    zone_id INT NULL,

    predicted_aqi DECIMAL(10,2),
    total_air_inhaled_liters DECIMAL(10,2),
    pm25_retained_micrograms DECIMAL(10,4),
    co_exposure_index DECIMAL(10,2),
    cumulative_toxic_load_score DECIMAL(5,2),
    temporary_lung_capacity_drop_percentage DECIMAL(5,2),
    recovery_time_hours DECIMAL(5,1),
    clinical_guidance_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_exposure_citizen
        FOREIGN KEY (citizen_id)
        REFERENCES citizen_citizens(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_exposure_session
        FOREIGN KEY (session_id)
        REFERENCES citizen_activity_sessions(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_exposure_zone
        FOREIGN KEY (zone_id)
        REFERENCES zones(id)
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- 4. TRAFFIC SERVICE 

CREATE TABLE traffic_roads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,           
    zone_id INT,
    road_type VARCHAR(50),               
    length_km DECIMAL(10,2),
    CONSTRAINT fk_road_zone
        FOREIGN KEY (zone_id)
        REFERENCES zones(id)
        ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE traffic_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    road_id INT NOT NULL,                 
    vehicle_density DECIMAL(10,2) NOT NULL,
    avg_speed_kmh DECIMAL(10,2) NOT NULL,
    total_vehicles INT NOT NULL DEFAULT 0,
    incident_flag BOOLEAN DEFAULT FALSE,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_traffic_road
        FOREIGN KEY (road_id)
        REFERENCES traffic_roads(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE traffic_incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    road_id INT NOT NULL,
    type VARCHAR(100) NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    description TEXT,
    resolved_at TIMESTAMP NULL,
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_incident_road
        FOREIGN KEY (road_id)
        REFERENCES traffic_roads(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;


-- 5. ENVIRONMENT SERVICE & ML PREDICTIONS

CREATE TABLE env_sensor_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zone_id INT NOT NULL,
    pm25 DECIMAL(10,2),
    pm10 DECIMAL(10,2),
    no2 DECIMAL(10,2),
    co DECIMAL(10,2),
    o3 DECIMAL(10,2),
    temperature DECIMAL(10,2),
    humidity DECIMAL(10,2),
    wind_speed DECIMAL(10,2) NOT NULL DEFAULT 0.00, 
    aqi DECIMAL(10,2) NULL,                         
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sensor_zone
        FOREIGN KEY (zone_id)
        REFERENCES zones(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE env_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zone_id INT,
    alert_type VARCHAR(100) NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    message TEXT,
    value DECIMAL(10,2),
    threshold DECIMAL(10,2),
    resolved_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_alert_zone
        FOREIGN KEY (zone_id)
        REFERENCES zones(id)
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- Penyimpanan output prediksi ML
CREATE TABLE env_ml_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zone_id INT NOT NULL,
    inversion_height DECIMAL(10,2),      
    predicted_aqi DECIMAL(10,2),         
    risk_level ENUM('safe', 'warning', 'danger') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_prediction_zone
        FOREIGN KEY (zone_id)
        REFERENCES zones(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- 6. INDEXES 

CREATE INDEX idx_citizen_reports_status ON citizen_reports(status);
CREATE INDEX idx_citizen_reports_zone ON citizen_reports(zone_id);

CREATE INDEX idx_traffic_roads_zone ON traffic_roads(zone_id);
CREATE INDEX idx_traffic_readings_road ON traffic_readings(road_id);
CREATE INDEX idx_traffic_readings_recorded ON traffic_readings(recorded_at);
CREATE INDEX idx_traffic_incidents_road ON traffic_incidents(road_id);
CREATE INDEX idx_env_sensor_readings_zone ON env_sensor_readings(zone_id);
CREATE INDEX idx_env_sensor_readings_recorded ON env_sensor_readings(recorded_at);
CREATE INDEX idx_env_alerts_zone ON env_alerts(zone_id);
CREATE INDEX idx_env_ml_predictions_zone ON env_ml_predictions(zone_id);

-- Composite Indexes khusus akselerasi kueri ML Malam-Subuh hari
CREATE INDEX idx_nocturnal_traffic ON traffic_readings(road_id, recorded_at);
CREATE INDEX idx_nocturnal_env ON env_sensor_readings(zone_id, recorded_at);

CREATE INDEX idx_citizen_devices_citizen ON citizen_devices(citizen_id);
CREATE INDEX idx_activity_sessions_citizen ON citizen_activity_sessions(citizen_id);
CREATE INDEX idx_activity_sessions_device_status ON citizen_activity_sessions(citizen_device_id, status);
CREATE INDEX idx_health_exposures_citizen ON citizen_health_exposures(citizen_id);
CREATE INDEX idx_health_exposures_created ON citizen_health_exposures(created_at);
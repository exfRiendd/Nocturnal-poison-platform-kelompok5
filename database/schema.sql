DROP DATABASE IF EXISTS smartcity;
CREATE DATABASE smartcity;
USE smartcity;

-- SHARED TABLES

CREATE TABLE zones (
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(100) NOT NULL,
city_district VARCHAR(100),
coordinates VARCHAR(255),
area_km2 DECIMAL(10,2)
) ENGINE=InnoDB;

-- OAUTH TABLES

CREATE TABLE oauth_clients (
id INT AUTO_INCREMENT PRIMARY KEY,
client_id VARCHAR(100) NOT NULL UNIQUE,
client_secret VARCHAR(255) NOT NULL,
grant_types VARCHAR(255),
redirect_uris TEXT
) ENGINE=InnoDB;

CREATE TABLE oauth_tokens (
id INT AUTO_INCREMENT PRIMARY KEY,
client_id INT NOT NULL,
user_id INT NULL,
access_token TEXT NOT NULL,
refresh_token TEXT,
expires_at DATETIME NOT NULL,

CONSTRAINT fk_oauth_client
    FOREIGN KEY (client_id)
    REFERENCES oauth_clients(id)
    ON DELETE CASCADE


) ENGINE=InnoDB;

-- CITIZEN SERVICE

CREATE TABLE citizen_citizens (
id INT AUTO_INCREMENT PRIMARY KEY,
nik VARCHAR(20) NOT NULL UNIQUE,
name VARCHAR(100) NOT NULL,
email VARCHAR(100) UNIQUE,
phone VARCHAR(20),
zone_id INT,
role ENUM(
    'citizen',
    'admin'
) DEFAULT 'citizen',

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
status ENUM(
    'pending',
    'investigating',
    'resolved'
) DEFAULT 'pending',
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
is_read BOOLEAN DEFAULT FALSE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

CONSTRAINT fk_notification_citizen
    FOREIGN KEY (citizen_id)
    REFERENCES citizen_citizens(id)
    ON DELETE CASCADE


) ENGINE=InnoDB;

-- TRAFFIC SERVICE

CREATE TABLE traffic_readings (
id INT AUTO_INCREMENT PRIMARY KEY,
zone_id INT NOT NULL,
vehicle_density DECIMAL(10,2) NOT NULL,
avg_speed_kmh DECIMAL(10,2) NOT NULL,
incident_flag BOOLEAN DEFAULT FALSE,
recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

CONSTRAINT fk_traffic_zone
    FOREIGN KEY (zone_id)
    REFERENCES zones(id)
    ON DELETE CASCADE


) ENGINE=InnoDB;

CREATE TABLE traffic_incidents (
id INT AUTO_INCREMENT PRIMARY KEY,
zone_id INT NOT NULL,
type VARCHAR(100) NOT NULL,
severity ENUM(
    'low',
    'medium',
    'high',
    'critical'
) NOT NULL,
description TEXT,
resolved_at TIMESTAMP NULL,
reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

CONSTRAINT fk_incident_zone
    FOREIGN KEY (zone_id)
    REFERENCES zones(id)
    ON DELETE CASCADE


) ENGINE=InnoDB;

-- ENVIRONMENT SERVICE

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
severity ENUM(
    'low',
    'medium',
    'high',
    'critical'
) NOT NULL,
value DECIMAL(10,2),
threshold DECIMAL(10,2),
resolved_at TIMESTAMP NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

CONSTRAINT fk_alert_zone
    FOREIGN KEY (zone_id)
    REFERENCES zones(id)
    ON DELETE SET NULL


) ENGINE=InnoDB;


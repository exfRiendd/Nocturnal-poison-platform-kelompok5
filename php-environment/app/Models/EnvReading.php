<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class EnvReading extends Model
{
    protected $table = 'env_sensor_readings';
    protected $fillable = [
        'zone_id', 'pm25', 'pm10', 'no2', 'co', 'o3', 
        'temperature', 'humidity', 'wind_speed', 'aqi', 'recorded_at'
    ];
}
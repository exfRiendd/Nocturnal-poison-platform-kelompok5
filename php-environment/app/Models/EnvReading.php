<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class EnvReading extends Model
{
    protected $table = 'env_sensor_readings';

    public $timestamps = false; 

    protected $fillable = [
        'zone_id',
        'pm25',
        'pm10',
        'no2',
        'co',
        'o3',
        'temperature',
        'humidity',
        'wind_speed',
        'aqi',
        'recorded_at',
    ];

    protected $casts = [
        'pm25'        => 'decimal:2',
        'pm10'        => 'decimal:2',
        'no2'         => 'decimal:3',
        'co'          => 'decimal:3',
        'o3'          => 'decimal:3',
        'temperature' => 'decimal:2',
        'humidity'    => 'decimal:2',
        'wind_speed'  => 'decimal:2',
        'aqi'         => 'decimal:2',
        'recorded_at' => 'datetime',
    ];


    public function zone()
    {
        return $this->belongsTo(Zone::class, 'zone_id');
    }


    public function isAqiDangerous(): bool
    {
        return $this->aqi !== null && $this->aqi >= 200;
    }

    public function isAqiCritical(): bool
    {
        return $this->aqi !== null && $this->aqi >= 300;
    }

    public function getRiskLevel(): string
    {
        if ($this->aqi === null) return 'unknown';
        if ($this->aqi >= 300) return 'critical';
        if ($this->aqi >= 200) return 'danger';
        if ($this->aqi >= 150) return 'warning';
        return 'safe';
    }
}
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class TrafficReading extends Model
{
    protected $table = 'traffic_readings';

    public $timestamps = false;

    protected $fillable = [
        'road_id',
        'vehicle_density',
        'avg_speed_kmh',
        'total_vehicles',
        'incident_flag',
        'recorded_at'
    ];
}
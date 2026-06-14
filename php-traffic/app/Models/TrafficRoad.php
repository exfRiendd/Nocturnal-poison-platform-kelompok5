<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class TrafficRoad extends Model
{
    protected $table = 'traffic_roads';

    public $timestamps = false;

    protected $fillable = [
        'name',
        'zone_id',
        'road_type',
        'length_km'
    ];

    public function readings()
    {
        return $this->hasMany(TrafficReading::class, 'road_id', 'id');
    }

    public function incidents()
    {
        return $this->hasMany(TrafficIncident::class, 'road_id', 'id');
    }
}
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Zone extends Model
{


    public $timestamps = false; 

    protected $fillable = [
        'name',
        'city_district',
        'coordinates',
        'area_km2',
    ];

    protected $casts = [
        'area_km2' => 'decimal:2',
    ];

    

    public function envReadings()
    {
        return $this->hasMany(EnvReading::class, 'zone_id');
    }

    public function envAlerts()
    {
        return $this->hasMany(EnvAlert::class, 'zone_id');
    }
}
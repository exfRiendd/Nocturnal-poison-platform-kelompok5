<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Zone extends Model
{
    protected $table = 'zones';
    public $timestamps = false;

    protected $fillable = [
        'name',
        'city_district',
        'coordinates',
        'area_km2'
    ];

    public function citizens()
    {
        return $this->hasMany(
            Citizen::class,
            'zone_id'
        );
    }

    public function reports()
    {
        return $this->hasMany(
            CitizenReport::class,
            'zone_id'
        );
    }

    public function activitySessions()
    {
        return $this->hasMany(
            CitizenActivitySession::class,
            'zone_id'
        );
    }

    public function healthExposures()
    {
        return $this->hasMany(
            CitizenHealthExposure::class,
            'zone_id'
        );
    }
}

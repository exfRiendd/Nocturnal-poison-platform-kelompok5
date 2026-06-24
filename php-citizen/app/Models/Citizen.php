<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Laravel\Sanctum\HasApiTokens;

class Citizen extends Authenticatable
{
    use HasApiTokens;

    protected $table = 'citizen_citizens';

    public $timestamps = false;

    protected $fillable = [
        'nik',
        'name',
        'email',
        'password',
        'phone',
        'zone_id',
        'role',
        'age',
        'weight_kg',
        'mask_type'
    ];

    protected $hidden = [
        'password'
    ];

    public function zone()
    {
        return $this->belongsTo(
            Zone::class,
            'zone_id'
        );
    }

    public function reports()
    {
        return $this->hasMany(
            CitizenReport::class,
            'citizen_id'
        );
    }

    public function notifications()
    {
        return $this->hasMany(
            CitizenNotification::class,
            'citizen_id'
        );
    }

    public function devices()
    {
        return $this->hasMany(
            CitizenDevice::class,
            'citizen_id'
        );
    }

    public function activitySessions()
    {
        return $this->hasMany(
            CitizenActivitySession::class,
            'citizen_id'
        );
    }

    public function healthExposures()
    {
        return $this->hasMany(
            CitizenHealthExposure::class,
            'citizen_id'
        );
    }
}
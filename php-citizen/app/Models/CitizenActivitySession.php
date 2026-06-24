<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class CitizenActivitySession extends Model
{
    protected $table = 'citizen_activity_sessions';
    public $timestamps = false;

    protected $fillable = [
        'citizen_id',
        'citizen_device_id',
        'zone_id',
        'activity_type',
        'avg_heart_rate',
        'max_heart_rate',
        'started_at',
        'ended_at',
        'duration_minutes',
        'status'
    ];

    public function citizen()
    {
        return $this->belongsTo(
            Citizen::class,
            'citizen_id'
        );
    }

    public function device()
    {
        return $this->belongsTo(
            CitizenDevice::class,
            'citizen_device_id'
        );
    }

    public function zone()
    {
        return $this->belongsTo(
            Zone::class,
            'zone_id'
        );
    }

    public function exposures()
    {
        return $this->hasMany(
            CitizenHealthExposure::class,
            'session_id'
        );
    }
}

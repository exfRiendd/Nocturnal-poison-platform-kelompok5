<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class CitizenHealthExposure extends Model
{
    protected $table = 'citizen_health_exposures';
    public $timestamps = false;

    protected $fillable = [
        'citizen_id',
        'session_id',
        'zone_id',
        'predicted_aqi',
        'total_air_inhaled_liters',
        'pm25_retained_micrograms',
        'co_exposure_index',
        'cumulative_toxic_load_score',
        'temporary_lung_capacity_drop_percentage',
        'recovery_time_hours',
        'clinical_guidance_message'
    ];

    public function citizen()
    {
        return $this->belongsTo(
            Citizen::class,
            'citizen_id'
        );
    }

    public function session()
    {
        return $this->belongsTo(
            CitizenActivitySession::class,
            'session_id'
        );
    }

    public function zone()
    {
        return $this->belongsTo(
            Zone::class,
            'zone_id'
        );
    }
}

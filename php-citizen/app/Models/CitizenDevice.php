<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class CitizenDevice extends Model
{
    protected $table = 'citizen_devices';
    public $timestamps = false;

    protected $fillable = [
        'device_id',
        'citizen_id',
        'device_label',
        'status',
        'last_seen_at'
    ];

    public function citizen()
    {
        return $this->belongsTo(
            Citizen::class,
            'citizen_id'
        );
    }

    public function sessions()
    {
        return $this->hasMany(
            CitizenActivitySession::class,
            'citizen_device_id'
        );
    }
}

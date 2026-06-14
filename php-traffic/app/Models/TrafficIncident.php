<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class TrafficIncident extends Model
{
    protected $table = 'traffic_incidents';

    public $timestamps = false;

    protected $fillable = [
        'road_id',
        'type',
        'severity',
        'description'
    ];

    public function road()
    {
        return $this->belongsTo(TrafficRoad::class, 'road_id', 'id');
    }
}
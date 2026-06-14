<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class EnvAlert extends Model
{
    protected $table = 'env_alerts';

    public $timestamps = false; 

    const CREATED_AT = 'created_at';
    const UPDATED_AT = null;

    protected $fillable = [
        'zone_id',
        'alert_type',
        'severity',
        'value',       
        'threshold',   
        'resolved_at', 
    ];

    protected $casts = [
        'value'       => 'decimal:2',
        'threshold'   => 'decimal:2',
        'resolved_at' => 'datetime',
        'created_at'  => 'datetime',
    ];

    
    const SEVERITY_LOW      = 'low';
    const SEVERITY_MEDIUM   = 'medium';
    const SEVERITY_HIGH     = 'high';
    const SEVERITY_CRITICAL = 'critical';

    
    public function zone()
    {
        return $this->belongsTo(Zone::class, 'zone_id');
    }

   

    public function isResolved(): bool
    {
        return $this->resolved_at !== null;
    }

    public function isCritical(): bool
    {
        return $this->severity === self::SEVERITY_CRITICAL;
    }
}
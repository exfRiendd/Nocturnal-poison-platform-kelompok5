<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class CitizenReport extends Model
{
    protected $table = 'citizen_reports';
    public $timestamps = false;

    protected $fillable = [
        'citizen_id',
        'category',
        'description',
        'zone_id',
        'status'
    ];

    public function citizen()
    {
        return $this->belongsTo(
            Citizen::class,
            'citizen_id'
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

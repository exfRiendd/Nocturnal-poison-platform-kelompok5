<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class CitizenNotification extends Model
{
    protected $table = 'citizen_notifications';
    public $timestamps = false;

    protected $fillable = [
        'citizen_id',
        'title',
        'body',
        'notification_type',
        'is_read'
    ];

    public function citizen()
    {
        return $this->belongsTo(
            Citizen::class,
            'citizen_id'
        );
    }
}

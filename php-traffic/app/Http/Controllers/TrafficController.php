<?php

namespace App\Http\Controllers;

use App\Models\TrafficRoad;
use Illuminate\Http\Request;

class TrafficController extends Controller
{
    public function roads()
    {
        return response()->json(
            TrafficRoad::all()
        );
    }
}
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

    public function showRoad($id)
    {
        $road = TrafficRoad::find($id);
        if (!$road) {
            return response()->json([
                'status' => 'error',
                'message' => 'Data jalan tidak ditemukan'
            ], 404);
        }
        return response()->json($road);
    }
}
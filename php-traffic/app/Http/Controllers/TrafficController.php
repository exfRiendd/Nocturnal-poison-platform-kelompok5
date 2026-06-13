<?php

namespace App\Http\Controllers;

use App\Models\TrafficRoad;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class TrafficController extends Controller
{
    // 1. GET /api/roads
    public function roads()
    {
        return response()->json(
            TrafficRoad::all()
        );
    }

    // 2. GET /api/roads/{id}
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

    // 3. GET /api/traffic/latest
    public function latestTraffic()
    {
        $latestReadings = DB::table('traffic_readings as tr')
            ->join('traffic_roads as r', 'tr.road_id', '=', 'r.id')
            ->whereIn('tr.id', function ($query) {
                $query->select(DB::raw('MAX(id)'))
                    ->from('traffic_readings')
                    ->groupBy('road_id');
            })
            ->select(
                'r.name as road_name',
                'tr.vehicle_density',
                'tr.avg_speed_kmh',
                'tr.total_vehicles',
                'tr.incident_flag',
                'tr.recorded_at'
            )
            ->get();

        return response()->json($latestReadings, 200);
    }
    
    // 4. GET /api/traffic/history/{roadId}
    public function trafficHistory($roadId)
    {
        $roadExists = TrafficRoad::find($roadId);
        if (!$roadExists) {
            return response()->json([
                'status' => 'error',
                'message' => 'Data jalan tidak ditemukan'
            ], 404);
        }

        $history = DB::table('traffic_readings')
            ->where('road_id', $roadId)
            ->orderBy('recorded_at', 'desc')
            ->select('vehicle_density', 'avg_speed_kmh', 'total_vehicles', 'incident_flag', 'recorded_at')
            ->get();

        return response()->json($history, 200);
    }

    
}
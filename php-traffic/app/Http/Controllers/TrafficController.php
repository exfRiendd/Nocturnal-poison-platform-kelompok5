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

    // 5. GET /api/incidents
    public function incidents()
    {
        $incidents = DB::table('traffic_incidents as ti')
            ->join('traffic_roads as r', 'ti.road_id', '=', 'r.id')
            ->select(
                'ti.id',
                'r.name as road_name',
                'ti.type',
                'ti.severity',
                'ti.description',
                'ti.reported_at',
                'ti.resolved_at'
            )
            ->orderBy('ti.reported_at', 'desc')
            ->get();

        return response()->json($incidents, 200);
    }

    // 6. GET /api/dashboard/summary
    public function dashboardSummary()
    {
        $totalRoads = TrafficRoad::count();
        $totalReadings = DB::table('traffic_readings')->count();
        $totalIncidents = DB::table('traffic_incidents')->count();
        
        $activeIncidents = DB::table('traffic_incidents')
            ->whereNull('resolved_at')
            ->count();

        return response()->json([
            'status' => 'success',
            'data' => [
                'total_roads' => $totalRoads,
                'total_traffic_readings' => $totalReadings,
                'total_incidents' => $totalIncidents,
                'active_incidents' => $activeIncidents
            ]
        ], 200);
    }

    // 7. POST /api/traffic/readings
    public function storeReading(Request $request)
    {
        $validated = $request->validate([
            'road_id'         => 'required|integer|exists:traffic_roads,id',
            'vehicle_density' => 'required|numeric|min:0|max:100',
            'avg_speed_kmh'   => 'required|numeric|min:0',
            'total_vehicles'  => 'required|integer|min:0',
            'incident_flag'   => 'required|boolean',
        ]);

        $validated['recorded_at'] = now();

        DB::table('traffic_readings')->insert($validated);

        return response()->json([
            'status'  => 'success',
            'message' => 'Data pembacaan sensor IoT berhasil disimpan'
        ], 21);
    }

    //8. GET api/traffic/history
    public function trafficHistoryAll(Request $request)
    {
        $query = DB::table('traffic_readings as tr')
            ->join('traffic_roads as r', 'tr.road_id', '=', 'r.id')
            ->select(
                'tr.id',
                'r.name as road_name',
                'r.zone_id',
                'tr.vehicle_density',
                'tr.avg_speed_kmh',
                'tr.total_vehicles',
                'tr.incident_flag',
                'tr.recorded_at'
            );

        if ($request->filled('zone_id')) {
            $query->where('r.zone_id', $request->zone_id);
        }

        if ($request->filled('start_date')) {
            $query->where('tr.recorded_at', '>=', $request->start_date . ' 00:00:00');
        }

        if ($request->filled('end_date')) {
            $query->where('tr.recorded_at', '<=', $request->end_date . ' 23:59:59');
        }

        $historyData = $query->orderBy('tr.recorded_at', 'desc')->get();

        return response()->json($historyData, 200);
    }


}
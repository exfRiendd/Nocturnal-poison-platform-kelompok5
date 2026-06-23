<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use Carbon\Carbon;

class ActivitySessionController extends Controller
{
    public function startSession(Request $request)
    {
        $validated = $request->validate([
            'citizen_id' => 'required',
            'zone_id' => 'required|integer',
            'heart_rate' => 'required|numeric'
        ]);

        $sessionId = DB::table('activity_sessions')->insertGetId([
            'citizen_id' => $validated['citizen_id'],
            'zone_id' => $validated['zone_id'],
            'avg_heart_rate' => $validated['heart_rate'],
            'started_at' => Carbon::now(),
            'status' => 'active',
            'created_at' => Carbon::now(),
            'updated_at' => Carbon::now(),
        ]);

        return response()->json(['message' => 'Session started', 'session_id' => $sessionId], 201);
    }

    public function endSession(Request $request, $id)
    {
        $session = DB::table('activity_sessions')->where('id', $id)->first();
        
        if (!$session || $session->status === 'completed') {
            return response()->json(['message' => 'Session not found or already completed'], 400);
        }

        // Ngambil profil warga
        $citizen = DB::table('citizen_citizens')->where('id', $session->citizen_id)->first();
        if(!$citizen) {
             $citizen = DB::table('users')->where('id', $session->citizen_id)->first();
        }

        $durationMinutes = Carbon::parse($session->started_at)->diffInMinutes(Carbon::now());
        if ($durationMinutes < 1) $durationMinutes = 1;

        // Ngambil data polusi (AQI) dari php-environment
        try {
            $envResponse = Http::timeout(3)->get("http://php-environment:8002/api/readings/latest/{$session->zone_id}");
            $envData = $envResponse->successful() ? $envResponse->json('data') : [];
            $aqi = $envData['aqi'] ?? 50; 
        } catch (\Exception $e) {
            $aqi = 50; 
        }

        
        $mlPayload = [
            'age' => $citizen->age ?? 30,
            'weight_kg' => $citizen->weight_kg ?? 70,
            'mask_type' => $citizen->mask_type ?? 'none',
            'avg_heart_rate' => $session->avg_heart_rate,
            'duration_minutes' => $durationMinutes,
            'env_aqi' => $aqi
        ];

        try {
            $mlResponse = Http::timeout(5)->post("http://python-ml:5000/predict/full-exposure-iot", $mlPayload);
            $mlData = $mlResponse->successful() ? $mlResponse->json() : [];
        } catch (\Exception $e) {
            $mlData = [];
        }

        DB::table('activity_sessions')->where('id', $id)->update([
            'ended_at' => Carbon::now(),
            'status' => 'completed',
            'updated_at' => Carbon::now()
        ]);

        // simpen hasil prediksi
        DB::table('health_exposures')->insert([
            'citizen_id' => $session->citizen_id,
            'activity_session_id' => $id,
            'predicted_aqi' => $mlData['predicted_aqi'] ?? $aqi,
            'total_air_inhaled_liters' => $mlData['total_air_inhaled_liters'] ?? null,
            'cumulative_toxic_load_score' => $mlData['cumulative_toxic_load_score'] ?? null,
            'created_at' => Carbon::now(),
            'updated_at' => Carbon::now()
        ]);

        return response()->json([
            'message' => 'Session ended and exposure recorded successfully',
            'exposure_result' => $mlData
        ], 200);
    }
}
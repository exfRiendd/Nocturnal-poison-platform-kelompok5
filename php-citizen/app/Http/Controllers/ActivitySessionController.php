<?php

namespace App\Http\Controllers;

use App\Models\CitizenActivitySession;
use App\Models\CitizenDevice;
use App\Models\CitizenHealthExposure;
use Carbon\Carbon;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class ActivitySessionController extends Controller
{
    /**
     * POST /api/activity-sessions/start
     *
     * Dipanggil Node-RED ketika HR >= 90 bpm
     */
    public function start(Request $request)
    {
        $request->validate([
            'device_id'   => 'required|string',
            'zone_id'     => 'required|integer',
            'heart_rate'  => 'required|numeric|min:1',
            'recorded_at' => 'required|date'
        ]);

        $device = CitizenDevice::where(
            'device_id',
            $request->device_id
        )->first();

        if (!$device) {
            return response()->json([
                'message' => 'Device not found'
            ], 404);
        }

        $existingSession = CitizenActivitySession::where(
            'citizen_device_id',
            $device->id
        )
        ->where('status', 'active')
        ->first();

        if ($existingSession) {
            return response()->json([
                'message' => 'Session already active'
            ], 200);
        }

        $heartRate = (float) $request->heart_rate;

        if ($heartRate >= 130) {
            $activityType = 'running';
        } elseif ($heartRate >= 90) {
            $activityType = 'walking';
        } else {
            $activityType = 'rest';
        }

        $session = CitizenActivitySession::create([
            'citizen_id'         => $device->citizen_id,
            'citizen_device_id'  => $device->id,
            'zone_id'            => $request->zone_id,
            'activity_type'      => $activityType,
            'avg_heart_rate'     => $heartRate,
            'max_heart_rate'     => $heartRate,
            'started_at'         => $request->recorded_at,
            'status'             => 'active'
        ]);

        return response()->json([
            'message' => 'Session started',
            'session' => $session
        ], 201);
    }

    /**
     * POST /api/activity-sessions/end
     *
     * Dipanggil Node-RED ketika HR turun < 90 bpm
     */
    public function end(Request $request)
    {
        $request->validate([
            'device_id'      => 'required|string',
            'recorded_at'    => 'required|date',
            'avg_heart_rate' => 'nullable|numeric|min:1',
            'max_heart_rate' => 'nullable|numeric|min:1'
        ]);

        $device = CitizenDevice::where(
            'device_id',
            $request->device_id
        )->first();

        if (!$device) {
            return response()->json([
                'message' => 'Device not found'
            ], 404);
        }

        $session = CitizenActivitySession::where(
            'citizen_device_id',
            $device->id
        )
        ->where('status', 'active')
        ->first();

        if (!$session) {
            return response()->json([
                'message' => 'No active session'
            ], 404);
        }

        $startedAt = Carbon::parse($session->started_at);
        $endedAt   = Carbon::parse($request->recorded_at);

        $duration = max(
            1,
            $startedAt->diffInMinutes($endedAt)
        );

        $updateData = [
            'ended_at'         => $endedAt,
            'duration_minutes' => $duration,
            'status'           => 'completed'
        ];

        if ($request->filled('avg_heart_rate')) {
            $updateData['avg_heart_rate'] =
                $request->avg_heart_rate;
        }

        if ($request->filled('max_heart_rate')) {
            $updateData['max_heart_rate'] =
                $request->max_heart_rate;
        }

        $session->update($updateData);

        $session->refresh();
        $session->load('citizen');

        $citizen = $session->citizen;

        /*
        |--------------------------------------------------------------------------
        | Ambil data polusi terbaru dari php-environment
        |--------------------------------------------------------------------------
        |*/
        $aqi = null;
        $zoneReading = [
            'pm25' => 0, 'pm10' => 0, 'co' => 0, 'no2' => 0,
            'temperature' => 25, 'humidity' => 50, 'wind_speed' => 0
        ];

        try {
            $envUrl = rtrim(env('ENV_SERVICE_URL'), '/') . '/api/readings/latest';
            $envResponse = Http::timeout(5)->get($envUrl);

            if ($envResponse->successful()) {
                $allReadings = $envResponse->json('data') ?? [];

                $data = collect($allReadings)->firstWhere('zone_id', $session->zone_id);

                if ($data) {
                    $aqi = $data['aqi'] ?? null;
                    $zoneReading = [
                        'pm25'        => $data['pm25'] ?? 0,
                        'pm10'        => $data['pm10'] ?? 0,
                        'co'          => $data['co'] ?? 0,
                        'no2'         => $data['no2'] ?? 0,
                        'temperature' => $data['temperature'] ?? 25,
                        'humidity'    => $data['humidity'] ?? 50,
                        'wind_speed'  => $data['wind_speed'] ?? 0
                    ];
                }
            }
        } catch (\Exception $e) {
            Log::error('ENV Service Error: ' . $e->getMessage());
        }

        /*
        |--------------------------------------------------------------------------
        | Kirim ke Python ML
        |--------------------------------------------------------------------------
        |*/
        $mlData = [];
        try {
            $mlPayload = [
                'zone_id'    => (int) $session->zone_id,
                'citizen_id' => (int) $session->citizen_id,
                'device_id'  => (string) $device->device_id,
                'session_id' => (int) $session->id,

                'pm25' => (float) $zoneReading['pm25'],
                'pm10' => (float) $zoneReading['pm10'],
                'co'   => (float) $zoneReading['co'],
                'no2'  => (float) $zoneReading['no2'],

                'temperature' => (float) $zoneReading['temperature'],
                'humidity'    => (float) $zoneReading['humidity'],
                'wind_speed'  => (float) $zoneReading['wind_speed'],

                'heart_rate' => (float) $session->avg_heart_rate,
                'hour'       => (float) now()->format('H'),
                
                'duration_minutes' => (float) $duration,
                'mask_type'        => $citizen->mask_type ?? 'none',
                'age'              => (int) ($citizen->age ?? 22),
                'weight_kg'        => (float) ($citizen->weight_kg ?? 65),
                'asthma_history'   => false,
                'baseline_lung_capacity_pct' => 100
            ];

            $mlResponse = Http::timeout(10)
                ->post(
                    rtrim(
                        env('PYTHON_ML_URL'),
                        '/'
                    )
                    . '/predict/full-exposure-iot',
                    $mlPayload
                );

            if ($mlResponse->successful()) {

                $mlData =
                    $mlResponse->json('data') ?? [];
            }

        } catch (\Exception $e) {

            Log::error(
                'ML Service Error: '
                . $e->getMessage()
            );
        }

        /*
        |--------------------------------------------------------------------------
        | Extract numeric value dari
        | "+3.5% HbCO increase"
        |--------------------------------------------------------------------------
        */

        $coExposureIndex = null;

        $coString =
            $mlData['computed_exposure_analysis']
            ['co_blood_saturation_estimation']
            ?? null;

        if ($coString) {

            preg_match(
                '/([\d\.]+)/',
                $coString,
                $matches
            );

            $coExposureIndex =
                $matches[1] ?? null;
        }

        /*
        |--------------------------------------------------------------------------
        | Simpan exposure
        |--------------------------------------------------------------------------
        */

        $exposure = CitizenHealthExposure::create([

            'citizen_id' => $session->citizen_id,

            'session_id' => $session->id,

            'zone_id' => $session->zone_id,

            'predicted_aqi' => $aqi,

            'total_air_inhaled_liters' =>
                $mlData['computed_exposure_analysis']
                ['total_air_inhaled_liters']
                ?? null,

            'pm25_retained_micrograms' =>
                $mlData['computed_exposure_analysis']
                ['pm25_retained_micrograms']
                ?? null,

            'co_exposure_index' =>
                $coExposureIndex,

            'cumulative_toxic_load_score' =>
                $mlData['lung_function_impact']
                ['cumulative_toxic_load_score']
                ?? null,

            'temporary_lung_capacity_drop_percentage' =>
                $mlData['lung_function_impact']
                ['lung_function_temporary_drop_pct']
                ?? null,

            'recovery_time_hours' =>
                $mlData['lung_function_impact']
                ['alveoli_recovery_time_hours']
                ?? null,

            'clinical_guidance_message' =>
                $mlData['lung_function_impact']
                ['health_risk_category']
                ?? 'Exposure calculated'
        ]);

        return response()->json([
            'message' => 'Session completed',
            'session' => $session,
            'exposure' => $exposure
        ]);
    }
}

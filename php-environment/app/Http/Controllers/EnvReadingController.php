<?php

namespace App\Http\Controllers;

use App\Models\EnvReading;
use App\Models\Zone;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Validation\ValidationException;

class EnvReadingController extends Controller
{
    /**
     * GET /api/readings
     * List sensor readings dengan filter dan paginasi.
     *
     * Query params:
     *   zone_id  → filter by zone
     *   from     → timestamp mulai (ISO8601 / Y-m-d H:i:s)
     *   to       → timestamp akhir
     *   limit    → max records (default 50, max 500)
     *   page     → untuk paginasi
     */
    public function index(Request $request): JsonResponse
    {
        $limit = min((int) $request->get('limit', 50), 500);

        $query = EnvReading::with('zone:id,name,city_district')
            ->orderBy('recorded_at', 'desc');

        if ($request->filled('zone_id')) {
            $query->where('zone_id', $request->zone_id);
        }

        if ($request->filled('from')) {
            $query->where('recorded_at', '>=', $request->from);
        }

        if ($request->filled('to')) {
            $query->where('recorded_at', '<=', $request->to);
        }

        $readings = $query->paginate($limit);

        return response()->json([
            'success'    => true,
            'data'       => $readings->items(),
            'pagination' => [
                'total'        => $readings->total(),
                'per_page'     => $readings->perPage(),
                'current_page' => $readings->currentPage(),
                'last_page'    => $readings->lastPage(),
            ],
        ]);
    }

    /**
     * POST /api/readings
     * Ingestion endpoint — Node-RED POST data sensor IoT ke sini (Skenario S1).
     *
     * Body JSON:
     * {
     *   "zone_id": 1,
     *   "pm25": 45.3,
     *   "pm10": 80.1,
     *   "no2": 0.05,
     *   "co": 1.2,
     *   "o3": 0.03,
     *   "temperature": 28.5,
     *   "humidity": 75.0,
     *   "wind_speed": 2.1,
     *   "aqi": 125.0,
     *   "recorded_at": "2026-06-14T22:00:00+07:00"  (opsional, default NOW)
     * }
     */
    public function store(Request $request): JsonResponse
    {
        try {
            $validated = $request->validate([
                'zone_id'     => 'required|integer|exists:zones,id',
                'pm25'        => 'nullable|numeric|min:0',
                'pm10'        => 'nullable|numeric|min:0',
                'no2'         => 'nullable|numeric|min:0',
                'co'          => 'nullable|numeric|min:0',
                'o3'          => 'nullable|numeric|min:0',
                'temperature' => 'nullable|numeric',
                'humidity'    => 'nullable|numeric|min:0|max:100',
                'wind_speed'  => 'nullable|numeric|min:0',
                'aqi'         => 'nullable|numeric|min:0',
                'recorded_at' => 'nullable|date',
            ]);
        } catch (ValidationException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Validation failed',
                'errors'  => $e->errors(),
            ], 422);
        }

        // Default recorded_at ke waktu sekarang jika tidak dikirim
        $validated['recorded_at'] = $validated['recorded_at'] ?? now();

        $reading = EnvReading::create($validated);

        // Hitung risk level untuk response Node-RED / ML Service
        $riskLevel = $reading->getRiskLevel();

        return response()->json([
            'success'    => true,
            'message'    => 'Sensor reading recorded',
            'data'       => $reading,
            'risk_level' => $riskLevel,
        ], 201);
    }

    /**
     * GET /api/readings/latest
     * Data sensor terbaru per zona — untuk dashboard monitoring real-time.
     * Mengambil 1 record terbaru per zone_id.
     */
    public function latest(): JsonResponse
    {
        // Subquery: max recorded_at per zone
        $latestIds = EnvReading::selectRaw('MAX(id) as id')
            ->groupBy('zone_id')
            ->pluck('id');

        $readings = EnvReading::with('zone:id,name,city_district')
            ->whereIn('id', $latestIds)
            ->orderBy('recorded_at', 'desc')
            ->get()
            ->map(function ($r) {
                $r->risk_level = $r->getRiskLevel();
                return $r;
            });

        return response()->json([
            'success' => true,
            'data'    => $readings,
            'total'   => $readings->count(),
        ]);
    }

    /**
     * GET /api/readings/{id}
     * Detail satu sensor reading.
     */
    public function show(int $id): JsonResponse
    {
        $reading = EnvReading::with('zone:id,name,city_district')->find($id);

        if (! $reading) {
            return response()->json([
                'success' => false,
                'message' => 'Reading not found',
            ], 404);
        }

        $reading->risk_level = $reading->getRiskLevel();

        return response()->json([
            'success' => true,
            'data'    => $reading,
        ]);
    }
}

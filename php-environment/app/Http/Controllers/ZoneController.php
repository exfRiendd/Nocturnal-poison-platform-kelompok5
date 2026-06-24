<?php

namespace App\Http\Controllers;

use App\Models\Zone;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Validation\ValidationException;

class ZoneController extends Controller
{
    /**
     * GET /api/zones
     * List semua zona, bisa filter by city_district.
     */
    public function index(Request $request): JsonResponse
    {
        $query = Zone::query();

        if ($request->has('district')) {
            $query->where('city_district', 'like', '%' . $request->district . '%');
        }

        $zones = $query->orderBy('name')->get();

        return response()->json([
            'success' => true,
            'data'    => $zones,
            'total'   => $zones->count(),
        ]);
    }

    /**
     * POST /api/zones
     * Tambah zona baru.
     */
    public function store(Request $request): JsonResponse
    {
        try {
            $validated = $request->validate([
                'name'          => 'required|string|max:100|unique:zones,name',
                'city_district' => 'nullable|string|max:100',
                'coordinates'   => 'nullable|string|max:255',
                'area_km2'      => 'nullable|numeric|min:0',
            ]);
        } catch (ValidationException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Validation failed',
                'errors'  => $e->errors(),
            ], 422);
        }

        $zone = Zone::create($validated);

        return response()->json([
            'success' => true,
            'message' => 'Zone created successfully',
            'data'    => $zone,
        ], 201);
    }

    /**
     * GET /api/zones/{id}
     * Detail satu zona beserta jumlah readings & active alerts.
     */
    public function show(Zone $zone): JsonResponse
    {
        $zone->loadCount([
            'envReadings',
            'envAlerts',
            'envAlerts as active_alerts_count' => fn ($q) => $q->whereNull('resolved_at'),
        ]);

        return response()->json([
            'success' => true,
            'data'    => $zone,
        ]);
    }

    /**
     * PUT /api/zones/{id}
     * Update data zona.
     */
    public function update(Request $request, Zone $zone): JsonResponse
    {
        try {
            $validated = $request->validate([
                'name'          => 'sometimes|string|max:100|unique:zones,name,' . $zone->id,
                'city_district' => 'nullable|string|max:100',
                'coordinates'   => 'nullable|string|max:255',
                'area_km2'      => 'nullable|numeric|min:0',
            ]);
        } catch (ValidationException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Validation failed',
                'errors'  => $e->errors(),
            ], 422);
        }

        $zone->update($validated);

        return response()->json([
            'success' => true,
            'message' => 'Zone updated successfully',
            'data'    => $zone->fresh(),
        ]);
    }

    /**
     * DELETE /api/zones/{id}
     * Hapus zona (cascade ke readings & alerts via FK).
     */
    public function destroy(Zone $zone): JsonResponse
    {
        $zone->delete();

        return response()->json([
            'success' => true,
            'message' => 'Zone deleted successfully',
        ]);
    }
}

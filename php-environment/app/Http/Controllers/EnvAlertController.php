<?php

namespace App\Http\Controllers;

use App\Models\EnvAlert;
use App\Services\RabbitMQPublisher;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Validation\ValidationException;
use Illuminate\Validation\Rule;

class EnvAlertController extends Controller
{
    /**
     * GET /api/alerts
     * List alert dengan filter.
     *
     * Query params:
     *   zone_id    → filter by zone
     *   severity   → low | medium | high | critical
     *   active     → "true" = hanya yang belum resolved
     *   limit      → max records (default 50)
     */
    public function index(Request $request): JsonResponse
    {
        $limit = min((int) $request->get('limit', 50), 200);

        $query = EnvAlert::with('zone:id,name,city_district')
            ->orderBy('created_at', 'desc');

        if ($request->filled('zone_id')) {
            $query->where('zone_id', $request->zone_id);
        }

        if ($request->filled('severity')) {
            $query->where('severity', $request->severity);
        }

        // Filter hanya alert yang masih aktif (belum resolved)
        if ($request->get('active') === 'true') {
            $query->whereNull('resolved_at');
        }

        $alerts = $query->paginate($limit);

        return response()->json([
            'success'    => true,
            'data'       => $alerts->items(),
            'pagination' => [
                'total'        => $alerts->total(),
                'per_page'     => $alerts->perPage(),
                'current_page' => $alerts->currentPage(),
                'last_page'    => $alerts->lastPage(),
            ],
        ]);
    }

    /**
     * POST /api/alerts
     * Trigger alert baru.
     * Dipanggil oleh Python ML Service ketika mendeteksi anomali (Skenario S6).
     *
     * Body JSON:
     * {
     *   "zone_id": 1,
     *   "alert_type": "pm25_spike",           // atau "inversion_layer", "aqi_critical", dll
     *   "severity": "critical",
     *   "message": "PM2.5 mencapai 250μg/m³. Lapisan inversi aktif.",
     *   "value": 250.5,
     *   "threshold": 150.0
     * }
     */
    public function store(Request $request): JsonResponse
    {
        try {
            $validated = $request->validate([
                'zone_id'    => 'nullable|integer|exists:zones,id',
                'alert_type' => 'required|string|max:100',
                'severity'   => ['required', Rule::in(['low', 'medium', 'high', 'critical'])],
                'message'    => 'nullable|string',
                'value'      => 'nullable|numeric',
                'threshold'  => 'nullable|numeric',
            ]);
        } catch (ValidationException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Validation failed',
                'errors'  => $e->errors(),
            ], 422);
        }

        $alert = EnvAlert::create($validated);
        $alert->load('zone:id,name,city_district');

        // Publish ke RabbitMQ supaya Citizen Service bisa kirim notifikasi (S6)
        try {
            $publisher = new RabbitMQPublisher();
            $publisher->publish('env.alerts', [
                'alert_id'   => $alert->id,
                'zone_id'    => $alert->zone_id,
                'zone_name'  => $alert->zone?->name,
                'alert_type' => $alert->alert_type,
                'severity'   => $alert->severity,
                'message'    => $alert->message,
                'value'      => $alert->value,
                'created_at' => $alert->created_at,
            ]);
        } catch (\Exception $e) {
            // Jangan gagalkan request kalau RabbitMQ tidak tersedia
            // Log error saja, alert tetap tersimpan di DB
            \Log::warning('RabbitMQ publish gagal: ' . $e->getMessage());
        }

        return response()->json([
            'success' => true,
            'message' => 'Alert triggered successfully',
            'data'    => $alert,
        ], 201);
    }

    /**
     * GET /api/alerts/active
     * Shortcut: semua alert yang belum resolved, diurutkan severity tertinggi dulu.
     * Digunakan dashboard operator dan Node-RED untuk cek kondisi real-time.
     */
    public function active(): JsonResponse
    {
        $severityOrder = ['critical' => 0, 'high' => 1, 'medium' => 2, 'low' => 3];

        $alerts = EnvAlert::with('zone:id,name,city_district')
            ->whereNull('resolved_at')
            ->orderBy('created_at', 'desc')
            ->get()
            ->sortBy(fn ($a) => $severityOrder[$a->severity] ?? 99)
            ->values();

        return response()->json([
            'success' => true,
            'data'    => $alerts,
            'total'   => $alerts->count(),
        ]);
    }

    /**
     * GET /api/alerts/{id}
     * Detail satu alert.
     */
    public function show(int $id): JsonResponse
    {
        $alert = EnvAlert::with('zone:id,name,city_district')->find($id);

        if (! $alert) {
            return response()->json([
                'success' => false,
                'message' => 'Alert not found',
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data'    => $alert,
        ]);
    }

    /**
     * PUT /api/alerts/{id}/resolve
     * Tandai alert sebagai resolved (Skenario S6 — setelah notifikasi warga terkirim).
     *
     * Body JSON (opsional):
     * { "resolved_at": "2026-06-14T06:00:00+07:00" }   ← jika tidak diisi, pakai NOW()
     */
    public function resolve(int $id, Request $request): JsonResponse
    {
        $alert = EnvAlert::find($id);

        if (! $alert) {
            return response()->json([
                'success' => false,
                'message' => 'Alert not found',
            ], 404);
        }

        if ($alert->isResolved()) {
            return response()->json([
                'success' => false,
                'message' => 'Alert already resolved',
                'data'    => $alert,
            ], 409);
        }

        $alert->update([
            'resolved_at' => $request->input('resolved_at') ?? now(),
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Alert resolved successfully',
            'data'    => $alert->fresh()->load('zone:id,name,city_district'),
        ]);
    }
}

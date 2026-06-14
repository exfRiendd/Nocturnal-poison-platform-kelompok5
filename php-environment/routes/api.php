<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ZoneController;
use App\Http\Controllers\EnvReadingController;
use App\Http\Controllers\EnvAlertController;

/*
|--------------------------------------------------------------------------
| Environment Service API Routes
|--------------------------------------------------------------------------
|
| Base URL (via API Gateway): /api/environment/...
| Semua response dalam format JSON.
|
*/

// ── Health check ──────────────────────────────────────────────────────────
Route::get('/health', fn () => response()->json([
    'service' => 'php-environment',
    'status'  => 'ok',
    'ts'      => now()->toIso8601String(),
]));

// ── Zones ─────────────────────────────────────────────────────────────────
Route::apiResource('zones', ZoneController::class);

// ── Sensor Readings ────────────────────────────────────────────────────────
Route::prefix('readings')->group(function () {
    // GET /api/readings          → list (filter: zone_id, limit, from, to)
    // POST /api/readings         → IoT ingestion endpoint (Node-RED → di sini)
    Route::get('/',    [EnvReadingController::class, 'index']);
    Route::post('/',   [EnvReadingController::class, 'store']);

    // GET /api/readings/latest   → data terbaru tiap zone (untuk dashboard)
    Route::get('/latest', [EnvReadingController::class, 'latest']);

    // GET /api/readings/{id}     → detail satu record
    Route::get('/{id}', [EnvReadingController::class, 'show']);
});

// ── Alerts ─────────────────────────────────────────────────────────────────
Route::prefix('alerts')->group(function () {
    // GET /api/alerts            → list (filter: severity, zone_id, active)
    // POST /api/alerts           → trigger alert (dari ML Service anomaly S6)
    Route::get('/',    [EnvAlertController::class, 'index']);
    Route::post('/',   [EnvAlertController::class, 'store']);

    // GET /api/alerts/active     → alert yang belum resolved
    Route::get('/active', [EnvAlertController::class, 'active']);

    // GET /api/alerts/{id}
    Route::get('/{id}',  [EnvAlertController::class, 'show']);

    // PUT /api/alerts/{id}/resolve → tandai alert selesai (S6 flow)
    Route::put('/{id}/resolve', [EnvAlertController::class, 'resolve']);
});

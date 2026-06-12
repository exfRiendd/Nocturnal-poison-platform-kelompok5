<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\TrafficController;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

Route::get('/roads', [TrafficController::class, 'roads']);

Route::get('/roads/{id}', [TrafficController::class, 'showRoad']);

Route::get('/traffic/latest', [TrafficController::class, 'latestTraffic']);

<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\CitizenController;
use App\Http\Controllers\ReportController;
use App\Http\Controllers\NotificationController;
use App\Http\Controllers\ActivitySessionController;

Route::prefix('citizens')->group(function () {
    Route::get('/', [CitizenController::class, 'index']);
    Route::post('/', [CitizenController::class, 'store']);
    Route::get('/{id}', [CitizenController::class, 'show']);
});

Route::prefix('reports')->group(function () {
    Route::get('/', [ReportController::class, 'index']);
    Route::post('/', [ReportController::class, 'store']);
});

Route::prefix('notifications')->group(function () {
    Route::get('/', [NotificationController::class, 'index']);
    Route::patch('/{id}/read', [NotificationController::class, 'markAsRead']);
});

Route::prefix('activity-sessions')->group(function () {
    Route::post('/start', [ActivitySessionController::class, 'startSession']);
    Route::post('/{id}/end', [ActivitySessionController::class, 'endSession']);
});
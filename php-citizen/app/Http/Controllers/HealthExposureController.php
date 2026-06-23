<?php

namespace App\Http\Controllers;

use App\Models\CitizenHealthExposure;
use Illuminate\Http\Request;

class HealthExposureController extends Controller
{
    public function index(Request $request)
    {
        return response()->json(
            CitizenHealthExposure::with([
                'session',
                'zone'
            ])
            ->where(
                'citizen_id',
                $request->citizen_id
            )
            ->latest('created_at')
            ->get()
        );
    }

    public function latest(Request $request)
    {
        return response()->json(
            CitizenHealthExposure::with([
                'session',
                'zone'
            ])
            ->where(
                'citizen_id',
                $request->citizen_id
            )
            ->latest('created_at')
            ->first()
        );
    }
}
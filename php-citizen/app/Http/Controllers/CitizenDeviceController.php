<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\CitizenDevice;

class CitizenDeviceController extends Controller
{
    public function store(Request $request)
    {
        // 1. Validasi input dari user/wearable
        $validated = $request->validate([
            'device_id'    => 'required|string|max:100|unique:citizen_devices,device_id',
            'device_label' => 'nullable|string|max:100',
            'status'       => 'nullable|in:active,inactive'
        ]);

        // 2. Ambil citizen_id dari middleware
        $citizenId = $request->input('citizen_id');

        // 3. Simpan data device ke database
        $device = CitizenDevice::create([
            'device_id'    => $validated['device_id'],
            'citizen_id'   => $citizenId, 
            'device_label' => $validated['device_label'] ?? null,
            'status'       => $validated['status'] ?? 'active',
            'last_seen_at' => now(),
        ]);

        // 4. Respon Sukes
        return response()->json([
            'message' => 'Device registered successfully',
            'data'    => $device
        ], 201);
    }

    public function index(Request $request)
    {
        // 1. Ambil citizen_id yang sudah disisipkan oleh middleware JWT
        $citizenId = $request->input('citizen_id');

        // 2. Ambil data device milik citizen tertentu
        $devices = CitizenDevice::where('citizen_id', $citizenId)
            ->select('device_id', 'device_label', 'status') 
            ->get();

        // 3. Kembalikan respon JSON
        return response()->json([
            'message' => 'Success fetching citizen devices',
            'data'    => $devices
        ], 200);
    }
}
<?php

namespace App\Http\Controllers;

use App\Models\Citizen;
use Illuminate\Http\Request;

class CitizenController extends Controller
{
    public function index()
    {
        $citizens = Citizen::with('zone')->get();
        return response()->json(['message' => 'Success', 'data' => $citizens], 200);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'nik' => 'required|unique:citizen_citizens,nik|max:20',
            'name' => 'required|string|max:100',
            'email' => 'nullable|email|unique:citizen_citizens,email|max:100',
            'phone' => 'nullable|string|max:20',
            'zone_id' => 'nullable|exists:zones,id',
            'password' => 'nullable|string' 
        ]);

        $citizen = Citizen::create($validated);

        return response()->json(['message' => 'Citizen registered successfully', 'data' => $citizen], 201);
    }

    public function show($id)
    {
        $citizen = Citizen::with('zone')->find($id);
        if (!$citizen) {
            return response()->json(['message' => 'Citizen not found'], 404);
        }
        return response()->json(['message' => 'Success', 'data' => $citizen], 200);
    }
}
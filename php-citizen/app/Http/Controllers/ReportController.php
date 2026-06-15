<?php

namespace App\Http\Controllers;

use App\Models\CitizenReport;
use Illuminate\Http\Request;

class ReportController extends Controller
{
    public function index(Request $request)
    {
        $query = CitizenReport::with(['citizen', 'zone']);

        if ($request->has('citizen_id')) {
            $query->where('citizen_id', $request->citizen_id);
        }

        return response()->json(['message' => 'Success', 'data' => $query->get()], 200);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'citizen_id' => 'required|exists:citizen_citizens,id',
            'category' => 'required|string|max:50',
            'description' => 'required|string',
            'zone_id' => 'nullable|exists:zones,id'
        ]);

        $report = CitizenReport::create($validated);

        return response()->json(['message' => 'Report submitted successfully', 'data' => $report], 201);
    }
}
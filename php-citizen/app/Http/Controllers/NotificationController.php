<?php

namespace App\Http\Controllers;

use App\Models\CitizenNotification;
use Illuminate\Http\Request;

class NotificationController extends Controller
{
    public function index(Request $request)
    {
        $request->validate([
            'citizen_id' => 'required|exists:citizen_citizens,id'
        ]);

        $notifications = CitizenNotification::where('citizen_id', $request->citizen_id)
                                            ->orderBy('created_at', 'desc')
                                            ->get();

        return response()->json(['message' => 'Success', 'data' => $notifications], 200);
    }

    public function markAsRead($id)
    {
        $notification = CitizenNotification::find($id);
        
        if (!$notification) {
            return response()->json(['message' => 'Notification not found'], 404);
        }

        $notification->update(['is_read' => true]);

        return response()->json(['message' => 'Notification marked as read'], 200);
    }
}
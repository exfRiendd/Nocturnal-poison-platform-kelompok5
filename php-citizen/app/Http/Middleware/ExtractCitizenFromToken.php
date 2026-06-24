<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class ExtractCitizenFromToken
{
    public function handle(Request $request, Closure $next): Response
    {
        $authHeader = $request->header('Authorization');

        if (!$authHeader || !str_starts_with($authHeader, 'Bearer ')) {
            return response()->json(['message' => 'Unauthorized: Missing Token'], 401);
        }

        $token = explode(' ', $authHeader)[1];
        $tokenParts = explode('.', $token);

        if (count($tokenParts) === 3) {
            $payload = base64_decode($tokenParts[1]);
            $decoded = json_decode($payload, true);

            if (isset($decoded['user_id'])) {
                // Menyisipkan citizen_id ke request untuk dibaca Controller
                $request->merge(['citizen_id' => $decoded['user_id']]);
            } else {
                return response()->json(['message' => 'Unauthorized: Invalid token format'], 401);
            }
        } else {
            return response()->json(['message' => 'Unauthorized: Malformed JWT'], 401);
        }

        return $next($request);
    }
}
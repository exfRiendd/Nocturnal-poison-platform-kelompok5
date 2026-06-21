<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;

class CitizenSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::table('citizen_citizens')->insert([
            [
                'nik' => '3276010000000001',
                'name' => 'Admin Smart City',
                'email' => 'admin@smartcity.local',
                'password' => Hash::make('password123'),
                'phone' => '081111111111',
                'zone_id' => 1,
                'role' => 'admin',
                'age' => 30,
                'weight_kg' => 70,
                'mask_type' => 'n95'
            ],
            [
                'nik' => '3276010000000002',
                'name' => 'Citizen One',
                'email' => 'citizen1@smartcity.local',
                'password' => Hash::make('password123'),
                'phone' => '082222222222',
                'zone_id' => 2,
                'role' => 'citizen',
                'age' => 22,
                'weight_kg' => 65,
                'mask_type' => 'medical'
            ]
        ]);
    }
}

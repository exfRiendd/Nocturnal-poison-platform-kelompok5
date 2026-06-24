<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class CitizenDeviceSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::table('citizen_devices')->insert([
            [
                'device_id' => 'wearable-001',
                'citizen_id' => 1,
                'device_label' => 'Smart Band Admin',
                'status' => 'active'
            ],
            [
                'device_id' => 'wearable-002',
                'citizen_id' => 2,
                'device_label' => 'Smart Band Citizen',
                'status' => 'active'
            ]
        ]);
    }
}

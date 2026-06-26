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
                'device_id' => 'device_01',
                'citizen_id' => 1,
                'device_label' => 'Smart Band 1',
                'status' => 'active'
            ],
            [
                'device_id' => 'device_02',
                'citizen_id' => 2,
                'device_label' => 'Smart Band 2',
                'status' => 'active'
            ]
        ]);
    }
}

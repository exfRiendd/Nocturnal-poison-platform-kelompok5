<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        DB::table('zones')->insertOrIgnore([
            'id' => 1,
            'name' => 'Pusat Kota',
            'city_district' => 'Distrik Sentral',
        ]);

        DB::table('citizen_citizens')->insertOrIgnore([
            'id' => 1,
            'nik' => '1234567890123456',
            'name' => 'Budi Smartwatch Demo',
            'email' => 'budi@demo.com',
            'password' => Hash::make('password123'),
            'phone' => '081234567890',
            'zone_id' => 1,
            'role' => 'citizen',
            
            'age' => 28,
            'weight_kg' => 70.5,
            'mask_type' => 'N95',
        ]);

        DB::table('citizen_devices')->insertOrIgnore([
            'citizen_id' => 1,
            'device_id' => 'wearable-001', 
            'device_type' => 'smartwatch',
            'status' => 'active',
        ]);

        $this->command->info('✅ Data Seeder Demo (Budi & wearable-001) berhasil disiapkan!');
    }
}
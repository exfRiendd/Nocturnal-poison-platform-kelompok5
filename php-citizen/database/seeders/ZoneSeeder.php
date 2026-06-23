<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class ZoneSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::table('zones')->insert([
            [
                'name' => 'Margonda',
                'city_district' => 'Depok',
                'coordinates' => '-6.3900,106.8300',
                'area_km2' => 5.50
            ],
            [
                'name' => 'Beji',
                'city_district' => 'Depok',
                'coordinates' => '-6.3700,106.8200',
                'area_km2' => 7.20
            ],
            [
                'name' => 'Pancoran Mas',
                'city_district' => 'Depok',
                'coordinates' => '-6.4000,106.8100',
                'area_km2' => 6.10
            ]
        ]);
    }
}

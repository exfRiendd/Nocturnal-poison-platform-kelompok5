<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    
    public function up(): void
    {
        if (Schema::hasTable('zones')) {
            return;
        }

        Schema::create('zones', function (Blueprint $table) {
            $table->id();
            $table->string('name', 100);
            $table->string('city_district', 100)->nullable(); 
            $table->string('coordinates', 255)->nullable();   
            $table->decimal('area_km2', 10, 2)->nullable();   
            
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('zones');
    }
};
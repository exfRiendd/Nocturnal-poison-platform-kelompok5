<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('env_sensor_readings', function (Blueprint $table) {
            $table->integer('id', true);
            
            $table->integer('zone_id');
            $table->foreign('zone_id')->references('id')->on('zones')->onDelete('cascade');
            
            $table->decimal('pm25', 10, 2)->nullable();
            $table->decimal('pm10', 10, 2)->nullable();
            $table->decimal('no2', 10, 2)->nullable();
            $table->decimal('co', 10, 2)->nullable();
            $table->decimal('o3', 10, 2)->nullable();
            $table->decimal('temperature', 10, 2)->nullable();
            $table->decimal('humidity', 10, 2)->nullable();
            $table->decimal('wind_speed', 10, 2)->default(0.00); 
            $table->decimal('aqi', 10, 2)->nullable();
            
            $table->timestamp('recorded_at')->useCurrent();

            $table->index(['zone_id', 'recorded_at']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('env_sensor_readings');
    }
};
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
            $table->id();
            $table->foreignId('zone_id')->constrained('shared_zones');
            $table->decimal('pm25', 8, 2)->nullable();
            $table->decimal('pm10', 8, 2)->nullable();
            $table->decimal('no2', 8, 3)->nullable();
            $table->decimal('co', 8, 3)->nullable();
            $table->decimal('o3', 8, 3)->nullable();
            $table->decimal('temperature', 5, 2)->nullable();
            $table->decimal('humidity', 5, 2)->nullable();
            $table->decimal('wind_speed', 5, 2)->nullable();
            $table->decimal('aqi', 8, 2)->nullable();
            $table->timestamp('recorded_at');
            $table->timestamps();

            // Index biar query di Grafana nanti cepet
            $table->index(['zone_id', 'recorded_at']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('env_readings');
    }
};

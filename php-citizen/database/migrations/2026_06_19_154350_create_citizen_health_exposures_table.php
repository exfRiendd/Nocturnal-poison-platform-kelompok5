<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('citizen_health_exposures', function (Blueprint $table) {

            $table->id();

            $table->foreignId('citizen_id')
                ->constrained('citizen_citizens')
                ->cascadeOnDelete();

            $table->foreignId('session_id')
                ->constrained('citizen_activity_sessions')
                ->cascadeOnDelete();

            $table->foreignId('zone_id')
                ->nullable()
                ->constrained('zones')
                ->nullOnDelete();

            $table->decimal('predicted_aqi', 10, 2)
                ->nullable();

            $table->decimal('total_air_inhaled_liters', 10, 2)
                ->nullable();

            $table->decimal('pm25_retained_micrograms', 10, 4)
                ->nullable();

            $table->decimal('co_exposure_index', 10, 2)
                ->nullable();

            $table->decimal('cumulative_toxic_load_score', 5, 2)
                ->nullable();

            $table->decimal(
                'temporary_lung_capacity_drop_percentage',
                5,
                2
            )->nullable();

            $table->decimal(
                'recovery_time_hours',
                5,
                1
            )->nullable();

            $table->text('clinical_guidance_message')
                ->nullable();

            $table->timestamp('created_at')
                ->useCurrent();

            $table->index(
                'citizen_id',
                'idx_health_exposures_citizen'
            );

            $table->index(
                'created_at',
                'idx_health_exposures_created'
            );
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('citizen_health_exposures');
    }
};
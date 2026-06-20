<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('citizen_health_exposures', function (Blueprint $table) {
            $table->integer('id', true);

            $table->integer('citizen_id');
            $table->foreign('citizen_id')
                ->references('id')
                ->on('citizen_citizens')
                ->cascadeOnDelete();

            $table->integer('session_id');
            $table->foreign('session_id')
                ->references('id')
                ->on('citizen_activity_sessions')
                ->cascadeOnDelete();

            $table->integer('zone_id')->nullable();
            $table->foreign('zone_id')
                ->references('id')
                ->on('zones')
                ->nullOnDelete();

            $table->decimal('predicted_aqi', 10, 2)->nullable();
            $table->decimal('total_air_inhaled_liters', 10, 2)->nullable();
            $table->decimal('pm25_retained_micrograms', 10, 4)->nullable();
            $table->decimal('co_exposure_index', 10, 2)->nullable();
            $table->decimal('cumulative_toxic_load_score', 5, 2)->nullable();
            $table->decimal('temporary_lung_capacity_drop_percentage', 5, 2)->nullable();
            $table->decimal('recovery_time_hours', 5, 1)->nullable();
            $table->text('clinical_guidance_message')->nullable();
            $table->timestamp('created_at')->useCurrent();

            $table->index('citizen_id', 'idx_health_exposures_citizen');
            $table->index('created_at', 'idx_health_exposures_created');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('citizen_health_exposures');
    }
};
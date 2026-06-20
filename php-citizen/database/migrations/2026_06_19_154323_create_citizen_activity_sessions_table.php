<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('citizen_activity_sessions', function (Blueprint $table) {
            $table->integer('id', true);

            $table->integer('citizen_id');
            $table->foreign('citizen_id')
                ->references('id')
                ->on('citizen_citizens')
                ->cascadeOnDelete();

            $table->integer('citizen_device_id')->nullable();
            $table->foreign('citizen_device_id')
                ->references('id')
                ->on('citizen_devices')
                ->nullOnDelete();

            $table->integer('zone_id');
            $table->foreign('zone_id')
                ->references('id')
                ->on('zones');

            $table->enum('activity_type', ['rest', 'walking', 'running']);
            $table->decimal('avg_heart_rate', 5, 2);
            $table->decimal('max_heart_rate', 5, 2);
            $table->timestamp('started_at');
            $table->timestamp('ended_at')->nullable();
            $table->integer('duration_minutes')->nullable();
            $table->enum('status', ['active', 'completed'])->default('active');

            $table->index('citizen_id', 'idx_activity_sessions_citizen');
            $table->index(['citizen_device_id', 'status'], 'idx_activity_sessions_device_status');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('citizen_activity_sessions');
    }
};
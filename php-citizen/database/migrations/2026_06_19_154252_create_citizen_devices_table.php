<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('citizen_devices', function (Blueprint $table) {

            $table->id();

            $table->string('device_id', 100)
                ->unique();

            $table->foreignId('citizen_id')
                ->nullable()
                ->constrained('citizen_citizens')
                ->nullOnDelete();

            $table->string('device_label', 100)
                ->nullable();

            $table->timestamp('registered_at')
                ->useCurrent();

            $table->enum('status', [
                'active',
                'inactive'
            ])->default('active');

            $table->timestamp('last_seen_at')
                ->nullable();

            $table->index('citizen_id', 'idx_citizen_devices_citizen');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('citizen_devices');
    }
};
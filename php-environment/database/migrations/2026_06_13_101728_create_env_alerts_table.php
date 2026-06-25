<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('env_alerts', function (Blueprint $table) {
            $table->integer('id', true);
            $table->integer('zone_id')->nullable();
            $table->foreign('zone_id')->references('id')->on('zones')->nullOnDelete();

            $table->string('alert_type', 100);

            $table->enum('severity', ['low', 'medium', 'high', 'critical']);

            $table->text('message')->nullable(); // deskripsi untuk notifikasi warga (S6)

            $table->decimal('value', 10, 2)->nullable();
            $table->decimal('threshold', 10, 2)->nullable();
            $table->timestamp('resolved_at')->nullable();

          
            $table->timestamp('created_at')->useCurrent();

            $table->index('zone_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('env_alerts');
    }
};
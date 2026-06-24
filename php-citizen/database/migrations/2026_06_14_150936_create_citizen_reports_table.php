<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::create('citizen_reports', function (Blueprint $table) {
            $table->integer('id', true);
            $table->integer('citizen_id');
            $table->string('category', 50);
            $table->text('description');
            $table->integer('zone_id')->nullable();
            $table->enum('status', ['pending', 'investigating', 'resolved'])->default('pending');
            $table->timestamp('created_at')->useCurrent();

            $table->foreign('citizen_id', 'fk_report_citizen')->references('id')->on('citizen_citizens')->cascadeOnDelete();
            $table->foreign('zone_id', 'fk_report_zone')->references('id')->on('zones')->nullOnDelete();
            
            $table->index('status', 'idx_citizen_reports_status');
            $table->index('zone_id', 'idx_citizen_reports_zone');
        });
    }
    public function down(): void {
        Schema::dropIfExists('citizen_reports');
    }
};
<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::create('citizen_notifications', function (Blueprint $table) {
            $table->integer('id', true);
            $table->integer('citizen_id')->nullable();
            $table->string('title', 255);
            $table->text('body');
            $table->enum('notification_type', ['general', 'anomaly_alert'])->default('general');
            $table->boolean('is_read')->default(false);
            $table->timestamp('created_at')->useCurrent();

            $table->foreign('citizen_id', 'fk_notification_citizen')->references('id')->on('citizen_citizens')->cascadeOnDelete();
        });
    }
    public function down(): void {
        Schema::dropIfExists('citizen_notifications');
    }
};
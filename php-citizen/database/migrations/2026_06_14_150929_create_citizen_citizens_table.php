<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::create('citizen_citizens', function (Blueprint $table) {
            $table->integer('id', true);
            $table->string('nik', 20)->unique();
            $table->string('name', 100);
            $table->integer('age')->nullable();
            $table->decimal('weight_kg', 5, 2)->nullable();
            $table->string('mask_type')->nullable();
            $table->string('email', 100)->nullable()->unique();
            $table->string('password', 255)->default('$2b$10$EPF96bA/f.ZqE7nfxbN7E.S1S0P3E8yM1kQ2w3e4r5t6y7u8i9o0p');
            $table->string('phone', 20)->nullable();
            $table->integer('zone_id')->nullable();
            $table->enum('role', ['citizen', 'admin'])->default('citizen');
            $table->timestamp('created_at')->useCurrent();
            

            $table->foreign('zone_id', 'fk_citizen_zone')->references('id')->on('zones')->nullOnDelete();
        });
    }
    public function down(): void {
        Schema::dropIfExists('citizen_citizens');
    }
};
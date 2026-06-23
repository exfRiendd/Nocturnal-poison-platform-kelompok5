<?php

// use Illuminate\Database\Migrations\Migration;
// use Illuminate\Database\Schema\Blueprint;
// use Illuminate\Support\Facades\Schema;

// return new class extends Migration
// {
//     public function up(): void
//     {
//         Schema::create('activity_sessions', function (Blueprint $table) {
//             $table->id();
//             $table->unsignedBigInteger('citizen_id');
//             $table->integer('zone_id');
//             $table->integer('avg_heart_rate');
//             $table->timestamp('started_at')->useCurrent();
//             $table->timestamp('ended_at')->nullable();
//             $table->string('status')->default('active'); // active, completed
//             $table->timestamps();
//         });
//     }

//     public function down(): void
//     {
//         Schema::dropIfExists('activity_sessions');
//     }
// };
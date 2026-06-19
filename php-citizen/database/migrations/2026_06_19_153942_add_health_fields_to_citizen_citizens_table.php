<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('citizen_citizens', function (Blueprint $table) {

            $table->integer('age')->nullable();

            $table->decimal('weight_kg', 5, 2)
                ->nullable();

            $table->enum('mask_type', [
                'none',
                'cloth',
                'medical',
                'n95'
            ])->default('none');
        });
    }

    public function down(): void
    {
        Schema::table('citizen_citizens', function (Blueprint $table) {

            $table->dropColumn([
                'age',
                'weight_kg',
                'mask_type'
            ]);
        });
    }
};
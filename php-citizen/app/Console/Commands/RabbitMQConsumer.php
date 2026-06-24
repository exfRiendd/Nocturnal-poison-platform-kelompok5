<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Http;
use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

class RabbitMQConsumer extends Command
{
    // Menyamakan signature dengan yang dipanggil di Dockerfile CMD
    protected $signature   = 'rabbitmq:consume';
    protected $description = 'Mendengarkan alert anomali lingkungan dari queue env.alerts untuk disebarkan ke warga';

    public function handle(): void
    {
        $this->info('Consumer Citizen Service Aktif. Menunggu pesan alert...');

        try {
            // Membuka koneksi ke broker RabbitMQ kelompok
            $connection = new AMQPStreamConnection(
                env('RABBITMQ_HOST', 'rabbitmq'),
                env('RABBITMQ_PORT', 5672),
                env('RABBITMQ_USER', 'guest'),
                env('RABBITMQ_PASS', 'guest'),
                env('RABBITMQ_VHOST', '/')
            );

            $channel = $connection->channel();
            
            // Mendaftarkan antrean sesuai target forward dari php-environment
            $channel->queue_declare('env.alerts', false, true, false, false);
            $channel->basic_qos(null, 1, null);

            $this->info('Mendengarkan pada queue: env.alerts');

            $channel->basic_consume(
                'env.alerts', '', false, false, false, false,
                fn(AMQPMessage $msg) => $this->processAlert($msg)
            );

            while ($channel->is_consuming()) {
                $channel->wait();
            }

            $channel->close();
            $connection->close();

        } catch (\Exception $e) {
            $this->error('Gagal menjalankan consumer RabbitMQ: ' . $e->getMessage());
            Log::error('RabbitMQ Consumer Error: ' . $e->getMessage());
        }
    }

    /**
     * Memproses pesan alert polusi berbahaya dari RabbitMQ
     */
    private function processAlert(AMQPMessage $msg): void
    {
        $data = json_decode($msg->body, true);

        if (!$data) {
            $this->warn('Pesan kosong atau format JSON tidak valid. Dilewati.');
            $msg->ack();
            return;
        }

        $zoneId   = $data['zone_id'] ?? 'Unknown';
        $zoneName = $data['zone_name'] ?? 'Tidak Diketahui';
        $severity = $data['severity'] ?? 'high';
        $message  = $data['message'] ?? 'Kualitas udara memburuk!';

        $this->line("\n========================================================");
        $this->line("[" . now()->format('H:i:s') . "] 🚨 ALERT DITERIMA UNTUK WARGA!");
        $this->line("Lokasi   : Zone {$zoneId} ({$zoneName})");
        $this->line("Bahaya   : Status " . strtoupper($severity));
        $this->line("Pesan    : {$message}");
        $this->line("========================================================");

        /*
        |--------------------------------------------------------------------------
        | SKENARIO 6 - Simulasi Mengirim Notifikasi ke Warga
        |--------------------------------------------------------------------------
        */
        Log::info("NOTIFIKASI WARGA TERKIRIM: Bahaya polusi di {$zoneName}. Pesan: {$message}");
        $this->info("✔ Notifikasi mitigasi bahaya berhasil disebarkan ke gawai warga di Zone {$zoneId}.");

        // Hubungi endpoint resolve temanmu setelah notifikasi sukses disebarkan (Skenario S6 opsional)
        $this->resolveAlertInEnvironment($data['alert_id'] ?? null);

        // Beritahu RabbitMQ bahwa pesan berhasil diproses sepenuhnya (hapus dari antrean)
        $msg->ack();
    }

    /**
     * Mengubah status alert menjadi resolved di service environment setelah sukses diproses warga
     */
    private function resolveAlertInEnvironment(?int $alertId): void
    {
        if (!$alertId) return;

        try {
            $envUrl = rtrim(env('ENV_SERVICE_URL', 'http://php-environment:8002'), '/') . "/api/alerts/{$alertId}/resolve";
            $response = Http::timeout(3)->put($envUrl);

            if ($response->successful()) {
                $this->info("  -> Status Alert #{$alertId} di php-environment berhasil diubah menjadi RESOLVED.");
            }
        } catch (\Exception $e) {
            Log::warning("Gagal memicu otomatis resolve ke php-environment: " . $e->getMessage());
        }
    }
}
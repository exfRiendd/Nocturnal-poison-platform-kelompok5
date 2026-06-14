<?php

namespace App\Console\Commands;

use App\Models\EnvAlert;
use App\Services\RabbitMQPublisher;
use Illuminate\Console\Command;
use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

class ConsumeMLAlerts extends Command
{
    protected $signature   = 'rabbitmq:consume';
    protected $description = 'Consume hasil prediksi anomali dari ML Service';

    public function handle(): void
    {
        $this->info('Consumer aktif. Ctrl+C untuk berhenti.');

        $connection = new AMQPStreamConnection(
            env('RABBITMQ_HOST', 'rabbitmq'),
            env('RABBITMQ_PORT', 5672),
            env('RABBITMQ_USER', 'guest'),
            env('RABBITMQ_PASS', 'guest'),
            env('RABBITMQ_VHOST', '/')
        );

        $channel = $connection->channel();
        $channel->queue_declare('ml.predictions', false, true, false, false);
        $channel->basic_qos(null, 1, null);

        $this->info('Mendengarkan queue: ml.predictions');

        $channel->basic_consume(
            'ml.predictions', '', false, false, false, false,
            fn(AMQPMessage $msg) => $this->processMessage($msg)
        );

        while ($channel->is_consuming()) {
            $channel->wait();
        }

        $channel->close();
        $connection->close();
    }

    private function processMessage(AMQPMessage $msg): void
    {
        $data = json_decode($msg->body, true);

        if (!$data) {
            $this->warn('Pesan tidak valid, dilewati.');
            $msg->ack();
            return;
        }

        $severity = $data['severity'] ?? 'low';
        $zoneId   = $data['zone_id']  ?? null;

        $this->line("[" . now()->format('H:i:s') . "] Zone {$zoneId} | severity: {$severity}");

        // Hanya proses kalau ML deteksi anomali berbahaya
        if (!in_array($severity, ['high', 'critical'])) {
            $this->line('  -> Normal, tidak perlu alert.');
            $msg->ack();
            return;
        }

        // Simpan alert ke database
        $alert = EnvAlert::create([
            'zone_id'    => $zoneId,
            'alert_type' => $data['alert_type'] ?? 'ml_prediction',
            'severity'   => $severity,
            'message'    => $data['message']    ?? 'Anomali terdeteksi oleh ML Service',
            'value'      => $data['value']      ?? null,
            'threshold'  => $data['threshold']  ?? null,
        ]);

        $this->info("  -> Alert #{$alert->id} disimpan.");

        // Forward ke env.alerts supaya Citizen Service bisa kirim notifikasi warga
        try {
            $publisher = new RabbitMQPublisher();
            $publisher->publish('env.alerts', [
                'alert_id'   => $alert->id,
                'zone_id'    => $alert->zone_id,
                'alert_type' => $alert->alert_type,
                'severity'   => $alert->severity,
                'message'    => $alert->message,
                'created_at' => $alert->created_at,
            ]);
            $this->info("  -> Diteruskan ke queue env.alerts.");
        } catch (\Exception $e) {
            $this->warn("  -> Gagal forward: " . $e->getMessage());
        }

        $msg->ack();
    }
}

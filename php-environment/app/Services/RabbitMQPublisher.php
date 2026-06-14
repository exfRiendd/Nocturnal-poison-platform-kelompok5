<?php

namespace App\Services;

use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

class RabbitMQPublisher
{
    private $connection;
    private $channel;

    public function __construct()
    {
        $this->connection = new AMQPStreamConnection(
            env('RABBITMQ_HOST', 'rabbitmq'),
            env('RABBITMQ_PORT', 5672),
            env('RABBITMQ_USER', 'guest'),
            env('RABBITMQ_PASS', 'guest'),
            env('RABBITMQ_VHOST', '/')
        );
        $this->channel = $this->connection->channel();
    }

    // Kirim pesan ke queue tertentu
    public function publish(string $queue, array $data): void
    {
        // Pastikan queue ada (durable supaya tidak hilang kalau RabbitMQ restart)
        $this->channel->queue_declare($queue, false, true, false, false);

        $message = new AMQPMessage(
            json_encode($data),
            ['delivery_mode' => AMQPMessage::DELIVERY_MODE_PERSISTENT]
        );

        $this->channel->basic_publish($message, '', $queue);
    }

    public function __destruct()
    {
        $this->channel->close();
        $this->connection->close();
    }
}

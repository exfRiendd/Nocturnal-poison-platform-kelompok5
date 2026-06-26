FROM php:8.2-cli

# Install system dependencies + PHP extensions (di-cache setelah build pertama)
RUN apt-get update && apt-get install -y -qq \
    libzip-dev zip unzip curl git \
    && docker-php-ext-install pdo pdo_mysql zip sockets \
    && curl -sS https://getcomposer.org/installer | php -- \
       --install-dir=/usr/local/bin --filename=composer \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /var/www

# Copy composer files dulu (supaya layer di-cache kalau kode berubah)
COPY composer.json composer.lock ./

# Install dependencies (vendor/ sudah ada, tapi --no-scripts lebih aman)
RUN composer install --no-interaction --prefer-dist --no-scripts

# Copy semua source code
COPY . .

# Pastikan storage & cache bisa ditulis
RUN chmod -R 775 storage bootstrap/cache

EXPOSE 8002

# Saat container start: migrate + serve
CMD php artisan migrate --force && \
    php -S 0.0.0.0:8002 -t public

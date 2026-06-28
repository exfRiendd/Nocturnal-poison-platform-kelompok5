# Nocturnal Poison Platform
**Smart City Integrated Platform — Tugas Besar Pembangunan Perangkat Lunak Orientasi Service**
**Kelompok 5 | Semester VI | S1 Informatika**

| Nama | NIM | Peran |
|---|---|---|
| Alysha Ananda Shafa | 2410511087 | IoT Engineer & System Integrator |
| Syahdewa Maulana | 2410511095 | ML Engineer (Ketua Kelompok) |
| Muhammad Fachri Wiryansyah | 2410511096 | Backend Developer (PHP/Laravel) |
| Rakha Dwi Prayoga | 2410511072 | Backend Developer (API Gateway & Auth) |
| Valkryie | 24105110**__** | Backend Developer (Citizen Service) |


---

## ⚙️ Prerequisites

Sebelum menjalankan proyek ini, pastikan mesin Anda sudah ter-install:

1. **Docker** & **Docker Compose**
2. **Git**
3. Browser untuk membuka simulator [Wokwi](https://wokwi.com) (IoT Simulator)

---

## 🔑 Cara Setup `.env`

Setiap *service* memiliki file `.env.example`. Sebelum menjalankan sistem, Anda wajib menduplikasi file tersebut menjadi `.env` di masing-masing folder service.

1. Buka terminal di root folder proyek.
2. Copy template `.env` untuk service Gateway, OAuth, dan ML:

   ```bash
   cp express-gateway/.env.example express-gateway/.env
   cp oauth-server/.env.example oauth-server/.env
   cp python-ml/.env.example python-ml/.env
   ```

3. Untuk service berbasis Laravel (`php-citizen` dan `php-environment`), salin `.env.example` bawaan Laravel, lalu generate key:

   ```bash
   cp php-citizen/.env.example php-citizen/.env
   php artisan key:generate --working-dir=php-citizen

   cp php-environment/.env.example php-environment/.env
   php artisan key:generate --working-dir=php-environment
   ```

> Catatan: Konfigurasi default di dalam `.env` sudah disesuaikan untuk berjalan di dalam Docker/Kubernetes network, tidak perlu diubah kecuali ada konfigurasi spesifik.

---

##  Cara Menjalankan — Lokal (Docker Compose)

Untuk testing di komputer lokal, jalankan perintah berikut:

1. Build dan jalankan seluruh container secara background:

   ```bash
   docker compose up --build -d
   ```

2. Jalankan migrasi dan seeder database untuk service Laravel:

   ```bash
   docker compose exec php-citizen php artisan migrate --seed
   docker compose exec php-environment php artisan migrate --force
   ```

3. Cek apakah semua service (MySQL, RabbitMQ, Node-RED, API, ML) berstatus *healthy*:

   ```bash
   docker compose ps
   ```

---

## ☁️ Cara Menjalankan — Server Production (103.169.206.139)

Kami menggunakan server VPS mandiri untuk keperluan presentasi dan demo langsung. Berikut cara menjalankan aplikasi di server produksi kami:

1. Remote ke dalam server melalui SSH:

   ```bash
   ssh root@103.169.206.139
   ```

2. Tarik kode terbaru dari repositori GitHub utama:

   ```bash
   cd /path/to/Nocturnal-poison-platform-kelompok5
   git pull origin main
   ```

3. Jika ada perubahan konfigurasi, pastikan `.env` sudah terisi dengan benar, lalu build ulang dan jalankan container:

   ```bash
   docker compose up --build -d
   ```

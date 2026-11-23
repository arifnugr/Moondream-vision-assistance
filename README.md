# Moondream Vision Assistance

Sistem **vision assistance** berbasis kamera untuk membantu pengguna memahami kondisi di depan mereka. Sistem mengambil gambar dari kamera ketika tombol GPIO ditekan, menganalisis gambar menggunakan model vision **Moondream** melalui Ollama, menerjemahkan hasilnya ke bahasa Indonesia, lalu membacakan deskripsi tersebut menggunakan **Piper TTS**.

Proyek ini ditujukan untuk dijalankan pada perangkat **NVIDIA Jetson** dengan kamera USB, tombol fisik, speaker, Ollama, dan model-model lokal.

## Fitur

- Capture frame terbaru dari kamera USB dengan resolusi target `1280x720` dan `30 FPS`.
- Pemrosesan berdasarkan tombol fisik pada pin BOARD `37`.
- Deteksi dan deskripsi singkat objek, rintangan, serta bahaya.
- Inferensi lokal menggunakan `moondream:latest` melalui Ollama.
- Terjemahan bahasa Inggris ke bahasa Indonesia menggunakan Argos Translate.
- Sintesis suara bahasa Indonesia menggunakan Piper TTS.
- Pemutaran audio WAV secara non-blocking menggunakan `aplay`.
- Penyimpanan frame, hasil deskripsi, hasil terjemahan, dan laporan latency.

## Arsitektur Pipeline

```text
Kamera USB
    ↓
Tombol GPIO ditekan
    ↓
Capture frame terbaru
    ↓
Moondream melalui Ollama
    ↓
Pembersihan teks bahasa Inggris
    ↓
Argos Translate (English → Indonesian)
    ↓
Piper TTS
    ↓
Audio WAV → Speaker
```

## Struktur Proyek

```text
.
├── main.py                    # Program utama dan kontrol GPIO/kamera
├── ollama_moondream.py        # Koneksi dan prompt untuk Ollama-Moondream
├── translator_argos.py        # Terjemahan dan post-processing bahasa Indonesia
├── tts_piper.py               # Sintesis suara menggunakan Piper
├── models/
│   ├── translate-en_id-1_9.argosmodel
│   ├── id_ID-news_tts-medium.onnx
│   └── id_ID-news_tts-medium.onnx.json
├── dataset-testing/           # Dataset gambar pengujian
├── latency_results.csv         # Hasil pengukuran waktu pipeline
├── metrics_results.json        # Metrik BLEU-1 dan METEOR
├── preds_final.json            # Prediksi sistem
└── refs_final.json             # Referensi evaluasi
```

## Persyaratan

- NVIDIA Jetson dengan JetPack/Linux.
- Python 3.8 atau lebih baru.
- Kamera USB yang dapat diakses OpenCV.
- Tombol GPIO yang terhubung ke pin BOARD 37 dan GND.
- Speaker atau perangkat audio yang didukung `aplay`.
- Ollama yang sedang berjalan.
- Model Ollama `moondream:latest`.

Dependensi Python utama:

```bash
pip install opencv-python requests argostranslate piper-tts Jetson.GPIO
```

> Instalasi `Jetson.GPIO`, OpenCV, dan Piper dapat berbeda tergantung versi JetPack serta arsitektur perangkat. Gunakan paket yang sesuai dengan environment Jetson Anda.

## Instalasi dan Konfigurasi

### 1. Clone repository

```bash
git clone https://github.com/arifnugr/Moondream-vision-assistance.git
cd Moondream-vision-assistance
```

### 2. Siapkan Ollama dan Moondream

Pastikan Ollama aktif, kemudian unduh model:

```bash
ollama pull moondream:latest
```

Verifikasi endpoint Ollama:

```bash
curl http://localhost:11434/api/tags
```

### 3. Sesuaikan path model lokal

Sebelum menjalankan program, ubah nilai berikut agar sesuai dengan lokasi repository pada perangkat:

- `ARGOS_MODEL_PATH` pada `translator_argos.py`
- `PIPER_MODEL_PATH` pada `tts_piper.py`
- `PIPER_CONFIG_PATH` pada `tts_piper.py`

Secara default, dua file Python tersebut masih menggunakan path absolut dari environment pengembangan. Contoh konfigurasi:

```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ARGOS_MODEL_PATH = os.path.join(
    BASE_DIR, "models", "translate-en_id-1_9.argosmodel"
)
PIPER_MODEL_PATH = os.path.join(
    BASE_DIR, "models", "id_ID-news_tts-medium.onnx"
)
PIPER_CONFIG_PATH = os.path.join(
    BASE_DIR, "models", "id_ID-news_tts-medium.onnx.json"
)
```

### 4. Hubungkan kamera dan tombol

- Kamera digunakan pada index OpenCV `0`.
- Tombol menggunakan mode `GPIO.BOARD`.
- Pin tombol default adalah pin fisik `37`.
- Input menggunakan pull-up internal; tombol dipicu saat sinyal berubah ke `FALLING`.

Jika perangkat menggunakan konfigurasi berbeda, ubah `CAMERA_INDEX` dan `BUTTON_PIN` pada `main.py`.

## Menjalankan Program

Jalankan program dari root repository:

```bash
python3 main.py
```

Setelah program aktif:

1. Pastikan kamera mengarah ke area yang ingin dianalisis.
2. Tekan tombol fisik.
3. Program mengambil frame terbaru dari kamera.
4. Hasil analisis diterjemahkan dan dikonversi menjadi audio.
5. Audio diputar melalui speaker.

Tekan `Ctrl+C` untuk menghentikan program dengan aman.

## Output

Setiap pemrosesan menyimpan file di direktori `Output/`:

```text
Output/
├── frames/
│   └── frame_YYYYMMDD_HHMMSS_microseconds.jpg
├── frame_..._en.txt
├── frame_..._id.txt
└── frame_..._latency.txt
```

- `*_en.txt`: hasil deskripsi dari Moondream setelah dibersihkan.
- `*_id.txt`: hasil terjemahan bahasa Indonesia.
- `*_latency.txt`: waktu setiap tahap pipeline.
- `frames/`: frame yang digunakan untuk inferensi.

File audio WAV dibuat sebagai file temporary oleh Piper dan kemudian diputar menggunakan `aplay`.

## Hasil Evaluasi

Berdasarkan file evaluasi yang tersedia di repository:

| Metrik | Rata-rata |
|---|---:|
| BLEU-1 | 0.3555 |
| METEOR | 0.3509 |
| Total latency rata-rata | 13.6506 detik |

Latency dapat berubah tergantung model yang sedang dimuat, performa Jetson, kamera, dan waktu proses terjemahan.

## Troubleshooting

### Kamera tidak terbuka

- Pastikan kamera terhubung.
- Periksa device kamera dengan `ls /dev/video*`.
- Ubah `CAMERA_INDEX` jika kamera tidak berada pada index `0`.

### Ollama tidak merespons

- Pastikan service Ollama aktif.
- Pastikan model tersedia dengan `ollama list`.
- Pastikan endpoint menggunakan `http://localhost:11434`.

### Model Argos atau Piper tidak ditemukan

- Periksa kembali path model pada `translator_argos.py` dan `tts_piper.py`.
- Pastikan file model dan file konfigurasi Piper tersedia di direktori `models/`.

### Audio tidak terdengar

- Pastikan speaker terdeteksi oleh sistem.
- Uji audio dengan `aplay`.
- Periksa permission perangkat audio dan konfigurasi output suara Jetson.

### GPIO gagal diakses

- Jalankan program dengan permission yang sesuai untuk GPIO.
- Pastikan `Jetson.GPIO` terpasang.
- Periksa kembali nomor pin fisik dan koneksi tombol.

## Catatan Pengembangan

Pemrosesan dilakukan secara lokal sehingga gambar dan teks tidak perlu dikirim ke layanan cloud. Namun, sistem tetap membutuhkan resource komputasi Jetson yang memadai untuk inferensi Moondream dan sintesis suara.

Proyek ini adalah prototipe penelitian. Deskripsi model tidak selalu sempurna, sehingga hasilnya sebaiknya digunakan sebagai bantuan tambahan dan tidak menggantikan kewaspadaan pengguna terhadap lingkungan.

## Lisensi

Belum ada file lisensi yang ditentukan di repository ini. Tambahkan file `LICENSE` jika proyek akan didistribusikan secara publik.

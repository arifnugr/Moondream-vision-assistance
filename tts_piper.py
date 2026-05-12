import os
import io
import wave
import tempfile
from typing import Optional
from piper import SynthesisConfig, PiperVoice

# ===== KONFIGURASI =====
PIPER_MODEL_PATH  = "/home/skripsibro/Skripsi/Arif/Projek-Moondream/models/id_ID-news_tts-medium.onnx"
PIPER_CONFIG_PATH = "/home/skripsibro/Skripsi/Arif/Projek-Moondream/models/id_ID-news_tts-medium.onnx.json"


# ===== FUNGSI UTAMA =====
def load_tts_model():

    print("=== Memuat model Piper TTS ===")
    if not os.path.exists(PIPER_MODEL_PATH):
        raise FileNotFoundError(f"Model tidak ditemukan: {PIPER_MODEL_PATH}")
    if not os.path.exists(PIPER_CONFIG_PATH):
        raise FileNotFoundError(f"Config tidak ditemukan: {PIPER_CONFIG_PATH}")

    # Load model suara
    tts = PiperVoice.load(PIPER_MODEL_PATH, PIPER_CONFIG_PATH)

    # Konfigurasi sintesis (atur volume, panjang, dan noise)
    cfg = SynthesisConfig(
        volume=0.8,
        length_scale=1.0,
        noise_scale=0.667,
        noise_w_scale=0.8,
        normalize_audio=True,
    )
    print("✓ Model Piper berhasil dimuat.")
    return tts, cfg


def tts_piper_to_wav(
    text_id: str,
    output_wav_path: Optional[str] = None,
    sample_rate: int = 22050,
) -> Optional[str]:
    """
    text_id         : Teks bahasa Indonesia yang akan dibacakan.
    output_wav_path : Path file .wav tujuan. Jika None -> dibuat file temp.
    sample_rate     : Sample rate output (default 22050).

    Return:
        path file WAV (string) jika sukses, None jika gagal.
    """
    if not text_id.strip():
        print("[PiperTTS] Warning: teks kosong, tidak ada audio dibuat.")
        return None

    # Load TTS model
    try:
        tts, cfg = load_tts_model()
    except Exception as e:
        print(f"[PiperTTS] Gagal memuat model: {e}")
        return None

    # Siapkan path output
    if output_wav_path is None:
        fd, tmp_path = tempfile.mkstemp(suffix=".wav", prefix="tts_", text=False)
        os.close(fd)
        output_wav_path = tmp_path

    # Synthesize ke bytes buffer
    try:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav:
            tts.synthesize_wav(text_id, wav, syn_config=cfg)
        wav_bytes = buf.getvalue()

        # Simpan ke file .wav
        with open(output_wav_path, "wb") as f:
            f.write(wav_bytes)

        print(f"[PiperTTS] Audio berhasil dibuat: {output_wav_path}")
        return output_wav_path

    except Exception as e:
        print(f"[PiperTTS] Error saat membuat audio: {e}")
        return None


def speak_id(text_id: str):

    wav_path = tts_piper_to_wav(text_id)
    if wav_path:
        # Jika Windows, pakai winsound
        if os.name == "nt":
            try:
                import winsound
                winsound.PlaySound(wav_path, winsound.SND_FILENAME)
            except Exception as e:
                print(f"[PiperTTS] Tidak bisa memutar otomatis di Windows: {e}")
        # Jika Linux, pakai sounddevice
        elif os.name == "posix":
            try:
                import sounddevice as sd
                import soundfile as sf
                data, sr = sf.read(wav_path)
                sd.play(data, sr)
                sd.wait()  # Tunggu sampai selesai
                print(f"[PiperTTS] Audio diputar di Linux: {wav_path}")
            except Exception as e:
                print(f"[PiperTTS] Tidak bisa memutar otomatis di Linux: {e}")
        else:
            print(f"[PiperTTS] Sistem operasi tidak didukung untuk pemutaran otomatis: {os.name}")
    return wav_path

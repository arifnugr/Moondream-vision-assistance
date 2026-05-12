import os
import re
_argos_ready = False

ARGOS_MODEL_PATH = "/home/skripsibro/Skripsi/Arif/Projek-Moondream/models/translate-en_id-1_9.argosmodel"


def _ensure_argos_loaded():

    global _argos_ready
    if _argos_ready:
        return
    try:
        import argostranslate.package
        if os.path.exists(ARGOS_MODEL_PATH):
            argostranslate.package.install_from_path(ARGOS_MODEL_PATH)
        else:
            print(f"[ArgosTranslate] Warning: model file not found at {ARGOS_MODEL_PATH}")
        _argos_ready = True
    except Exception as e:
        print(f"[ArgosTranslate] Warning: failed to load Argos model: {e}")
        _argos_ready = False


def preprocess_english(text_en: str) -> str:

    t = text_en.strip()
    
    # Pattern umum yang bikin kaku
    patterns = [
        # Lokasi & posisi
        (r'\bin the foreground\b', 'in front'),
        (r'\bin the background\b', 'behind'),
        (r'\bis located\b', 'is'),
        (r'\bis positioned\b', 'is'),
        (r'\bis situated\b', 'is'),
        (r'\bcan be seen\b', 'is visible'),
        
        # Keberadaan
        (r'\bthere is a\b', 'a'),
        (r'\bthere are\b', ''),
        (r'\bthere\'s a\b', 'a'),
        
        # Kata sambung & transisi
        (r'\bindicating that\b', 'showing'),
        (r'\bsuggesting that\b', 'showing'),
        (r'\bappears to be\b', 'looks like'),
        (r'\bseems to be\b', 'looks like'),
        
        # Kata sifat berlebihan
        (r'\bapproximately\b', 'about'),
        (r'\bvarious\b', 'several'),
        (r'\bnumerous\b', 'many'),
        
        # Frasa pasif -> aktif
        (r'\bis parked at\b', 'is at'),
        (r'\bis placed on\b', 'is on'),
    ]
    
    for pattern, replacement in patterns:
        t = re.sub(pattern, replacement, t, flags=re.IGNORECASE)
    
    return t.strip()


def postprocess_indonesian(text_id: str) -> str:

    t = text_id.strip()
    
    # Pola umum formal -> casual
    replacements = [
        # Kata kerja formal
        ("terdapat", "ada"),
        ("terlihat", "ada"),
        ("terletak", "berada"),
        ("berada di", "di"),
        ("ditempatkan", "ada"),
        
        # Frasa deskriptif
        ("yang menampilkan", "dengan"),
        ("yang memiliki", "dengan"),
        ("yang dilengkapi", "dengan"),
        ("menunjukkan bahwa", "menunjukkan"),
        ("menandakan bahwa", "menandakan"),
        ("tampaknya", "sepertinya"),
        ("nampaknya", "sepertinya"),
        
        # Kata sambung
        ("sementara itu", "sedangkan"),
        ("di samping itu", "selain itu"),
        ("kemudian", "lalu"),
        
        # Kuantitas
        ("sejumlah", "beberapa"),
        ("berbagai macam", "berbagai"),
        ("beraneka ragam", "berbagai"),
        
        # Posisi & arah
        ("di bagian depan", "di depan"),
        ("di bagian belakang", "di belakang"),
        ("di bagian atas", "di atas"),
        ("di bagian bawah", "di bawah"),
        ("di sebelah kiri", "di kiri"),
        ("di sebelah kanan", "di kanan"),
        ("pada sisi", "di sisi"),
        
        # Hapus kata berlebihan
        ("yang berada", "yang"),
        ("yang terletak", "yang"),
        ("yang ada", "yang"),
    ]
    
    for src, dst in replacements:
        t = t.replace(src, dst)
    
    # Hapus pengulangan kata (umum dari hasil translate)
    words = t.split()
    cleaned_words = []
    prev_word = ""
    for word in words:
        # Skip kata yang sama berturut-turut
        if word.lower() != prev_word.lower():
            cleaned_words.append(word)
        prev_word = word
    t = " ".join(cleaned_words)
    
    # Bersihkan spasi ganda
    t = re.sub(r'\s+', ' ', t)
    
    # Kapitalisasi kalimat
    sentences = re.split(r'([.!?])', t)
    result = []
    for i, part in enumerate(sentences):
        part = part.strip()
        if part and i % 2 == 0 and part[0].islower():
            part = part[0].upper() + part[1:]
        if part:
            result.append(part)
    t = " ".join(result)
    
    # Pastikan ada tanda titik di akhir
    t = t.strip()
    if t and not t[-1] in '.!?':
        t += '.'
    
    return t


def argos_translate_en_id(text_en: str) -> str:

    _ensure_argos_loaded()
    
    if not text_en or not text_en.strip():
        return ""
    
    try:
        # Step 1: Preprocess English
        text_preprocessed = preprocess_english(text_en)
        
        # Step 2: Translate dengan Argos
        from argostranslate import translate as argos_translate
        text_id_raw = argos_translate.translate(text_preprocessed, "en", "id")
        
        # Step 3: Postprocess Indonesian
        text_id_final = postprocess_indonesian(text_id_raw)
        
        return text_id_final
        
    except Exception as e:
        print(f"[ArgosTranslate] Warning: translation failed: {e}")
        # Fallback: coba postprocess saja tanpa preprocess
        try:
            from argostranslate import translate as argos_translate
            text_id_raw = argos_translate.translate(text_en, "en", "id")
            return postprocess_indonesian(text_id_raw)
        except:
            return text_en.strip()


def translate_id(text_en: str) -> str:

    return argos_translate_en_id(text_en)


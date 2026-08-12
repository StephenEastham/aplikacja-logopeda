import asyncio
import html
import re
import subprocess
import tempfile
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
ASSETS_MD = ROOT / "assets" / "assets.md"
IMAGES_DIR = ROOT / "assets" / "images"
SOUNDS_DIR = ROOT / "assets" / "sounds"
SYLLABLE_SOUNDS_DIR = SOUNDS_DIR / "syllables"
VOICE = "pl-PL-ZofiaNeural"
CUSTOM_SVG = "CUSTOM_SVG"
SYLLABLE_PADDING_SECONDS = 0.05
CARRIER_SYLLABLE_RANGES = {
    "ca": (0.0, 0.24, 0),
    "ce": (0.0, 0.18, 0),
    "co": (0.0, 0.19, 0),
    "cu": (0.0, 0.19, 0),
    "cy": (0.0, 0.22, 0),
    "cia": (0.0, 0.32, 0),
    "ba": (0.00, 0.20, 0),
    "be": (0.00, 0.23, 0),
    "bo": (0.00, 0.18, 0),
    "bu": (0.00, 0.23, 0),
    "bi": (0.00, 0.22, 0),
    "by": (0.00, 0.23, 0),
    "cie": (0.00, 0.28, 0),
    "cio": (0.00, 0.25, 0),
    "ciu": (0.00, 0.24, 0),
    "ci": (0.00, 0.23, 0),
    "da": (0.00, 0.24, 0),
    "de": (0.00, 0.23, 0),
    "do": (0.00, 0.23, 0),
    "du": (0.00, 0.23, 0),
    "dy": (0.00, 0.20, 0),
    "fa": (0.00, 0.20, 0),
    "fe": (0.00, 0.19, 0),
    "fo": (0.00, 0.21, 0),
    "fu": (0.00, 0.18, 0),
    "fi": (0.00, 0.18, 0),
    "fy": (0.44, 0.66, 0),
    "ga": (0.00, 0.22, 0),
    "ge": (0.00, 0.20, 0),
    "go": (0.00, 0.23, 0),
    "gu": (0.00, 0.22, 0),
    "gi": (0.00, 0.22, 0),
    "ha": (0.00, 0.21, 0),
    "he": (0.00, 0.17, 0),
    "ho": (0.00, 0.18, 0),
    "hu": (0.00, 0.17, 0),
    "hi": (0.00, 0.17, 0),
    "hy": (0.00, 0.18, 0),
    "ja": (0.00, 0.20, 0),
    "je": (0.00, 0.21, 0),
    "jo": (0.00, 0.19, 0),
    "ju": (0.00, 0.22, 0),
    "ka": (0.00, 0.21, 0),
    "ke": (0.00, 0.19, 0),
    "ko": (0.00, 0.20, 0),
    "ku": (0.00, 0.19, 0),
    "ki": (0.00, 0.20, 0),
    "la": (0.00, 0.24, 0),
    "le": (0.00, 0.22, 0),
    "lo": (0.00, 0.22, 0),
    "lu": (0.00, 0.22, 0),
    "li": (0.00, 0.28, 0),
    "ła": (0.00, 0.23, 0),
    "łe": (0.00, 0.21, 0),
    "ło": (0.00, 0.26, 0),
    "łu": (0.00, 0.25, 0),
    "ły": (0.00, 0.22, 0),
    "ma": (0.00, 0.22, 0),
    "me": (0.00, 0.19, 0),
    "mo": (0.00, 0.21, 0),
    "mu": (0.00, 0.24, 0),
    "mi": (0.00, 0.25, 0),
    "my": (0.00, 0.24, 0),
    "na": (0.00, 0.19, 0),
    "ne": (0.00, 0.23, 0),
    "no": (0.00, 0.26, 0),
    "nu": (0.00, 0.19, 0),
    "ny": (0.42, 0.63, 0),
    "nia": (0.00, 0.26, 0),
    "nie": (0.00, 0.23, 0),
    "nio": (0.09, 0.36, 0),
    "niu": (0.00, 0.24, 0),
    "ni": (0.00, 0.20, 0),
    "pa": (0.00, 0.19, 0),
    "pe": (0.00, 0.17, 0),
    "po": (0.00, 0.18, 0),
    "pu": (0.00, 0.18, 0),
    "pi": (0.00, 0.20, 0),
    "py": (0.00, 0.18, 0),
    "ra": (0.00, 0.24, 0),
    "re": (0.00, 0.21, 0),
    "ro": (0.00, 0.19, 0),
    "ru": (0.00, 0.19, 0),
    "ry": (0.00, 0.22, -10),
    "sa": (0.00, 0.19, 0),
    "se": (0.00, 0.24, 0),
    "so": (0.00, 0.23, 0),
    "su": (0.00, 0.21, 0),
    "sy": (0.00, 0.21, 0),
    "sia": (0.00, 0.28, 0),
    "sie": (0.00, 0.25, 0),
    "sio": (0.00, 0.27, 0),
    "siu": (0.00, 0.28, 0),
    "si": (0.00, 0.21, 0),
    "ta": (0.00, 0.22, 0),
    "te": (0.00, 0.18, 0),
    "to": (0.00, 0.19, 0),
    "tu": (0.00, 0.16, 0),
    "ty": (0.00, 0.17, 0),
    "wa": (0.00, 0.19, 0),
    "we": (0.00, 0.17, 0),
    "wo": (0.00, 0.22, 0),
    "wu": (0.00, 0.21, 0),
    "wi": (0.00, 0.20, 0),
    "wy": (0.00, 0.21, 0),
    "za": (0.00, 0.23, 0),
    "ze": (0.00, 0.20, 0),
    "zo": (0.00, 0.27, 0),
    "zu": (0.00, 0.24, 0),
    "zy": (0.17, 0.34, 0),
    "zia": (0.00, 0.27, 0),
    "zie": (0.00, 0.25, 0),
    "zio": (0.00, 0.30, 0),
    "ziu": (0.19, 0.47, 0),
    "zi": (0.00, 0.24, 0),
    "ża": (0.00, 0.26, 0),
    "że": (0.00, 0.20, 0),
    "żo": (0.00, 0.20, 0),
    "żu": (0.00, 0.26, 0),
    "ży": (0.00, 0.21, 0),
    "cha": (0.00, 0.23, 0),
    "che": (0.00, 0.20, 0),
    "cho": (0.00, 0.20, 0),
    "chu": (0.00, 0.18, 0),
    "chi": (0.22, 0.43, 0),
    "chy": (0.00, 0.20, 0),
    "cza": (0.00, 0.23, 0),
    "cze": (0.00, 0.19, 0),
    "czo": (0.00, 0.20, 0),
    "czu": (0.00, 0.22, 0),
    "czy": (0.00, 0.18, 0),
    "dza": (0.59, 0.78, 0),
    "dze": (0.50, 0.66, 0),
    "dzo": (0.32, 0.53, 0),
    "dzu": (0.24, 0.49, 0),
    "dzy": (0.40, 0.60, 0),
    "dzia": (0.00, 0.30, 0),
    "dzie": (0.00, 0.28, 0),
    "dzio": (0.00, 0.28, 0),
    "dziu": (0.00, 0.27, 0),
    "dzi": (0.00, 0.26, 0),
    "dża": (0.00, 0.22, 0),
    "dże": (0.00, 0.23, 0),
    "dżo": (0.00, 0.21, 0),
    "dżu": (0.00, 0.19, 0),
    "dży": (0.10, 0.31, 0),
    "rza": (0.19, 0.39, 0),
    "rze": (0.00, 0.24, 0),
    "rzo": (0.00, 0.17, 0),
    "rzu": (0.00, 0.23, 0),
    "rzy": (0.10, 0.31, 0),
    "sza": (0.00, 0.25, 0),
    "sze": (0.00, 0.24, 0),
    "szo": (0.00, 0.22, 0),
    "szu": (0.00, 0.21, 0),
    "szy": (0.00, 0.22, 0),
}

ENTRIES = [
    ("ba", "-ba-lon", "balon", "🎈"), ("be", "-be-czka", "beczka", "🛢️"), ("bo", "-bo-cian", "bocian", CUSTOM_SVG),
    ("bu", "-bu-t", "but", "👟"), ("bi", "-bi-let", "bilet", "🎫"), ("by", "-by-k", "byk", "🐂"),
    ("ca", "-ca-łus", "całus", "💋"), ("ce", "-ce-bula", "cebula", "🧅"), ("co", "-co-kół", "cokół", "🏛️"),
    ("cu", "-cu-kierek", "cukierek", "🍬"), ("cy", "-cy-tryna", "cytryna", "🍋"),
    ("cia", "-cia-stko", "ciastko", "🍪"), ("cie", "-cie-lę", "cielę", "🐄"), ("cio", "-cio-cia", "ciocia", "👩"),
    ("ciu", "-ciu-chcia", "ciuchcia", "🚂"), ("ci", "-ci-chy", "cichy", "🤫"),
    ("da", "-da-ch", "dach", "🏠"), ("de", "-de-ska", "deska", CUSTOM_SVG), ("do", "-do-m", "dom", "🏡"),
    ("du", "-du-ch", "duch", "👻"), ("dy", "-dy-nia", "dynia", "🎃"),
    ("fa", "-fa-rby", "farby", "🎨"), ("fe", "-fe-rie", "ferie", "⛷️"), ("fo", "-fo-ka", "foka", "🦭"),
    ("fu", "-fu-tbol", "futbol", "⚽"), ("fi", "-fi-liżanka", "filiżanka", "☕"), ("fy", "żyra-fy-", "żyrafy", "🦒"),
    ("ga", "-ga-rnek", "garnek", "🍲"), ("ge", "-ge-pard", "gepard", "🐆"), ("go", "-go-łąb", "gołąb", "🕊️"),
    ("gu", "-gu-zik", "guzik", "🔘"), ("gi", "-gi-tara", "gitara", "🎸"),
    ("ha", "-ha-mak", "hamak", CUSTOM_SVG), ("he", "-he-likopter", "helikopter", "🚁"), ("ho", "-ho-tel", "hotel", "🏨"),
    ("hu", "-hu-lajnoga", "hulajnoga", "🛴"), ("hi", "-hi-popotam", "hipopotam", "🦛"), ("hy", "-hy-bryda", "hybryda", "🚗"),
    ("ja", "-ja-błko", "jabłko", "🍎"), ("je", "-je-ż", "jeż", "🦔"), ("jo", "-jo-gurt", "jogurt", "🥣"),
    ("ju", "-ju-do", "judo", "🥋"),
    ("ka", "-ka-czka", "kaczka", "🦆"), ("ke", "-ke-lner", "kelner", CUSTOM_SVG), ("ko", "-ko-t", "kot", "🐈"),
    ("ku", "-ku-ra", "kura", "🐔"), ("ki", "-ki-no", "kino", "🎬"),
    ("la", "-la-lka", "lalka", "🪆"), ("le", "-le-w", "lew", "🦁"), ("lo", "-lo-dy", "lody", "🍦"),
    ("lu", "-lu-pa", "lupa", "🔍"), ("li", "-li-s", "lis", "🦊"),
    ("ła", "-ła-pa", "łapa", "🐾"), ("łe", "-łe-zka", "łezka", "😢"), ("ło", "-ło-ś", "łoś", "🫎"),
    ("łu", "-łu-k", "łuk", "🏹"), ("ły", "-ły-żka", "łyżka", "🥄"),
    ("ma", "-ma-ma", "mama", "👩"), ("me", "-me-dal", "medal", "🏅"), ("mo", "-mo-tyl", "motyl", "🦋"),
    ("mu", "-mu-cha", "mucha", "🪰"), ("mi", "-mi-ś", "miś", "🧸"), ("my", "-my-sz", "mysz", "🐁"),
    ("na", "-na-miot", "namiot", "⛺"), ("ne", "-ne-on", "neon", "💡"), ("no", "-no-s", "nos", "👃"),
    ("nu", "-nu-rek", "nurek", "🤿"), ("ny", "balo-ny-", "balony", "🎈"),
    ("nia", "-nia-nia", "niania", "👩‍🍼"), ("nie", "-nie-dźwiedź", "niedźwiedź", "🐻"), ("nio", "a-nio-ł", "anioł", "👼"),
    ("niu", "-niu-nia", "niunia", "👧"), ("ni", "-ni-tka", "nitka", "🧵"),
    ("pa", "-pa-puga", "papuga", "🦜"), ("pe", "-pe-leryna", "peleryna", "🦸"), ("po", "-po-ciąg", "pociąg", "🚆"),
    ("pu", "-pu-dełko", "pudełko", "📦"), ("pi", "-pi-łka", "piłka", "⚽"), ("py", "-py-tajnik", "pytajnik", "❓"),
    ("ra", "-ra-k", "rak", "🦀"), ("re", "-re-kin", "rekin", "🦈"), ("ro", "-ro-wer", "rower", "🚲"),
    ("ru", "-ru-ra", "rura", CUSTOM_SVG), ("ry", "-ry-ba", "ryba", "🐟"),
    ("sa", "-sa-molot", "samolot", "✈️"), ("se", "-se-r", "ser", "🧀"), ("so", "-so-wa", "sowa", "🦉"),
    ("su", "-su-wak", "suwak", CUSTOM_SVG), ("sy", "-sy-rena", "syrena", "🧜‍♀️"),
    ("sia", "-sia-tka", "siatka", "🥅"), ("sie", "-sie-kiera", "siekiera", "🪓"), ("sio", "-sio-dło", "siodło", "🐎"),
    ("siu", "-siu-p", "siup", "🤸"), ("si", "-si-to", "sito", CUSTOM_SVG),
    ("ta", "-ta-ta", "tata", "👨"), ("te", "-te-lefon", "telefon", "📱"), ("to", "-to-rt", "tort", "🎂"),
    ("tu", "-tu-lipan", "tulipan", "🌷"), ("ty", "-ty-grys", "tygrys", "🐅"),
    ("wa", "-wa-lizka", "walizka", "🧳"), ("we", "-we-ntylator", "wentylator", CUSTOM_SVG), ("wo", "-wo-rek", "worek", CUSTOM_SVG),
    ("wu", "-wu-jek", "wujek", "👨"), ("wi", "-wi-delec", "widelec", "🍴"), ("wy", "-wy-spa", "wyspa", "🏝️"),
    ("za", "-za-mek", "zamek", "🏰"), ("ze", "-ze-bra", "zebra", "🦓"), ("zo", "-zo-o", "zoo", "🦁"),
    ("zu", "-zu-pa", "zupa", "🍲"), ("zy", "po-zy-tywka", "pozytywka", "🎵"),
    ("zia", "-zia-rno", "ziarno", "🌾"), ("zie", "-zie-mniak", "ziemniak", "🥔"), ("zio", "-zio-ła", "zioła", "🌿"),
    ("ziu", "Jó-ziu-", "Józiu", "👦"), ("zi", "-zi-ma", "zima", "❄️"),
    ("ża", "-ża-ba", "żaba", "🐸"), ("że", "-że-glarz", "żeglarz", "⛵"), ("żo", "-żo-nkil", "żonkil", "🌼"),
    ("żu", "-żu-k", "żuk", "🪲"), ("ży", "-ży-rafa", "żyrafa", "🦒"),
    ("cha", "-cha-ta", "chata", "🛖"), ("che", "-che-mik", "chemik", "🧪"), ("cho", "-cho-inka", "choinka", "🎄"),
    ("chu", "-chu-stka", "chustka", "🧣"), ("chi", "or-chi-dea", "orchidea", "🌸"), ("chy", "-chy-try", "chytry", "🦊"),
    ("cza", "-cza-pka", "czapka", "🧢"), ("cze", "-cze-kolada", "czekolada", "🍫"), ("czo", "-czo-ło", "czoło", "🙂"),
    ("czu", "-czu-łki", "czułki", "🐌"), ("czy", "-czy-tanie", "czytanie", "📖"),
    ("dza", "kukury-dza-", "kukurydza", "🌽"), ("dze", "pienią-dze-", "pieniądze", "🪙"), ("dzo", "bar-dzo-", "bardzo", "👍"),
    ("dzu", "wo-dzu-", "wodzu", "👑"), ("dzy", "kole-dzy-", "koledzy", "🧒"),
    ("dzia", "-dzia-dek", "dziadek", "👴"), ("dzie", "-dzie-cko", "dziecko", "🧒"), ("dzio", "-dzio-bak", "dziobak", CUSTOM_SVG),
    ("dziu", "-dziu-ra", "dziura", "🕳️"), ("dzi", "-dzi-k", "dzik", "🐗"),
    ("dża", "-dża-karta", "Dżakarta", "🏙️"), ("dże", "-dże-m", "dżem", "🍓"), ("dżo", "-dżo-kej", "dżokej", "🏇"),
    ("dżu", "-dżu-ngla", "dżungla", "🌴"), ("dży", "dż-dży-sty", "dżdżysty", "🌧️"),
    ("rza", "Ma-rza-nna", "Marzanna", "🎎"), ("rze", "-rze-ka", "rzeka", "🏞️"), ("rzo", "-rzo-dkiewka", "rzodkiewka", CUSTOM_SVG),
    ("rzu", "-rzu-tka", "rzutka", "🎯"), ("rzy", "g-rzy-b", "grzyb", "🍄"),
    ("sza", "-sza-fa", "szafa", "🚪"), ("sze", "-sze-lki", "szelki", "🦺"), ("szo", "-szo-p", "szop", "🦝"),
    ("szu", "-szu-flada", "szuflada", "🗄️"), ("szy", "-szy-szka", "szyszka", CUSTOM_SVG),
]

PALETTES = [
    ("#ffd166", "#fff8df", "#173f3a"),
    ("#a8dadc", "#f1fcfc", "#1d3557"),
    ("#ffb4a2", "#fff2ee", "#5c2b29"),
    ("#b7e4c7", "#f2fff6", "#174d45"),
    ("#f6bd60", "#fff7e7", "#49351b"),
]


def slug(word: str) -> str:
    return word.lower().replace(" ", "-")


def svg_content(word: str, emoji: str, index: int) -> str:
    accent, surface, ink = PALETTES[index % len(PALETTES)]
    label = word
    font_size = 42 if len(label) <= 8 else 34 if len(label) <= 11 else 28
    escaped_word = html.escape(word)
    escaped_label = html.escape(label)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-labelledby="title description">
  <title id="title">{escaped_word}</title>
  <desc id="description">Ilustracja przedstawiająca: {escaped_word}.</desc>
  <rect width="512" height="512" rx="48" fill="{surface}"/>
  <circle cx="84" cy="82" r="54" fill="{accent}" opacity="0.72"/>
  <circle cx="438" cy="150" r="34" fill="{accent}" opacity="0.48"/>
  <path d="M0 386 Q128 330 256 386 T512 386 V512 H0Z" fill="{accent}" opacity="0.58"/>
  <text x="256" y="292" font-family="Segoe UI Emoji, Apple Color Emoji, sans-serif" font-size="176" text-anchor="middle">{emoji}</text>
  <rect x="48" y="400" width="416" height="76" rx="20" fill="#ffffff" opacity="0.9"/>
  <text x="256" y="451" fill="{ink}" font-family="Trebuchet MS, sans-serif" font-size="{font_size}" font-weight="700" text-anchor="middle">{escaped_label}</text>
</svg>
'''


def update_markdown() -> None:
    mapping = {syllable: word for syllable, _, word, _ in ENTRIES}
    lines = ASSETS_MD.read_text(encoding="utf-8").splitlines()
    output = []
    row_pattern = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|.*\|.*\|$")
    for line in lines:
        match = row_pattern.match(line)
        if not match or match.group(1).strip() in {"Consonant", "---"}:
            output.append(line)
            continue
        consonant, vowel, syllable = (value.strip() for value in match.groups())
        word = mapping[syllable]
        filename = f"{syllable}_{slug(word)}"
        image = f"![{filename}.svg](./images/{filename}.svg) [./images/{filename}.svg](./images/{filename}.svg)"
        syllable_sound = f"[{syllable}.wav](./sounds/syllables/{syllable}.wav)"
        word_sound = f"[{filename}.wav](./sounds/{filename}.wav)"
        output.append(
            f"| {consonant} | {vowel} | {syllable} | {syllable_sound} | {word_sound} | {image} |"
        )
    output[4] = "| Consonant | Vowel | Syllable | Syllable sound | Word sound | Image |"
    output[5] = "| --- | --- | --- | --- | --- | --- |"
    ASSETS_MD.write_text("\n".join(output) + "\n", encoding="utf-8")


def create_svgs() -> None:
    for index, (syllable, _, word, emoji) in enumerate(ENTRIES):
        if syllable == "pa" or emoji == CUSTOM_SVG:
            continue
        filename = f"{syllable}_{slug(word)}.svg"
        (IMAGES_DIR / filename).write_text(svg_content(word, emoji, index), encoding="utf-8")


async def synthesize_audio(text, output_path, semaphore, temp_dir):
    if output_path.exists():
        return False

    mp3_path = temp_dir / f"{output_path.stem}.mp3"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    async with semaphore:
        for attempt in range(3):
            try:
                communicate = edge_tts.Communicate(text, VOICE, rate="-10%")
                await communicate.save(str(mp3_path))
                break
            except Exception:
                if attempt == 2:
                    raise
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", str(mp3_path),
            "-af", "silenceremove=start_periods=1:start_duration=0.03:start_threshold=-45dB:stop_periods=1:stop_duration=0.12:stop_threshold=-45dB,apad=pad_dur=0.08",
            "-ar", "22050", "-ac", "1", "-c:a", "pcm_s16le", str(output_path),
        ], check=True)
    return True


def extract_syllable(source_path, output_path, start_time, end_time, end_offset_milliseconds):
    if output_path.exists():
        return False

    fade_duration = 0.02
    adjusted_end_time = end_time + end_offset_milliseconds / 1000
    duration = adjusted_end_time - start_time
    padding_milliseconds = round(SYLLABLE_PADDING_SECONDS * 1000)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(source_path),
        "-af", f"atrim=start={start_time}:end={adjusted_end_time},asetpts=PTS-STARTPTS,afade=t=out:st={duration - fade_duration}:d={fade_duration},adelay={padding_milliseconds}:all=1,apad=pad_dur={SYLLABLE_PADDING_SECONDS}",
        "-ar", "22050", "-ac", "1", "-c:a", "pcm_s16le", str(output_path),
    ], check=True)
    return True


async def create_audio(entry, semaphore, temp_dir):
    syllable, tts_syllable, word, _ = entry
    generated_audio_count = 0
    word_output_path = SOUNDS_DIR / f"{syllable}_{slug(word)}.wav"
    if syllable != "pa":
        generated_audio_count += await synthesize_audio(
            word, word_output_path, semaphore, temp_dir
        )

    syllable_output_path = SYLLABLE_SOUNDS_DIR / f"{syllable}.wav"
    generated_audio_count += extract_syllable(
        word_output_path,
        syllable_output_path,
        *CARRIER_SYLLABLE_RANGES[syllable],
    )
    return generated_audio_count


async def main() -> None:
    syllables = [entry[0] for entry in ENTRIES]
    if len(ENTRIES) != 156 or len(set(syllables)) != 156:
        raise RuntimeError(f"Expected 156 unique syllables, found {len(ENTRIES)} / {len(set(syllables))}")
    marked_entries = {
        syllable: (tts_syllable, word)
        for syllable, tts_syllable, word, _ in ENTRIES
        if "-" in tts_syllable
    }
    if len(marked_entries) != len(ENTRIES):
        raise RuntimeError("Every entry must mark its syllable with two hyphens")
    if set(CARRIER_SYLLABLE_RANGES) != set(marked_entries):
        raise RuntimeError("Every marked entry must have an extraction range")
    for syllable, (tts_syllable, word) in marked_entries.items():
        parts = tts_syllable.split("-")
        if (
            len(parts) != 3
            or parts[1].casefold() != syllable.casefold()
            or "".join(parts).casefold() != word.casefold()
        ):
            raise RuntimeError(f"Invalid carrier notation for {syllable}: {tts_syllable} / {word}")
    for syllable in CARRIER_SYLLABLE_RANGES:
        start_time, end_time, end_offset_milliseconds = CARRIER_SYLLABLE_RANGES[syllable]
        adjusted_end_time = end_time + end_offset_milliseconds / 1000
        if not isinstance(end_offset_milliseconds, int):
            raise RuntimeError(f"End offset for {syllable} must be an integer number of milliseconds")
        if start_time < 0 or adjusted_end_time <= start_time:
            raise RuntimeError(
                f"Invalid extraction range for {syllable}: "
                f"{start_time}–{end_time} {end_offset_milliseconds:+d} ms"
            )
    generated_svg_count = sum(
        syllable != "pa" and emoji != CUSTOM_SVG for syllable, _, _, emoji in ENTRIES
    )
    update_markdown()
    create_svgs()
    semaphore = asyncio.Semaphore(4)
    with tempfile.TemporaryDirectory(prefix="logopeda-audio-") as directory:
        generated_audio_count = sum(await asyncio.gather(
            *(create_audio(entry, semaphore, Path(directory)) for entry in ENTRIES)
        ))
    print(
        f"Generated mappings for {len(ENTRIES)} rows, {generated_svg_count} SVGs, "
        f"and {generated_audio_count} new WAVs."
    )


if __name__ == "__main__":
    asyncio.run(main())

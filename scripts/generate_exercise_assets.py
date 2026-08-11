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
VOICE = "pl-PL-ZofiaNeural"
CUSTOM_SVG = "CUSTOM_SVG"

ENTRIES = [
    ("ba", "balon", "🎈"), ("be", "beczka", "🛢️"), ("bo", "bocian", "🐦"),
    ("bu", "but", "👟"), ("bi", "bilet", "🎫"), ("by", "byk", "🐂"),
    ("ca", "całus", "💋"), ("ce", "cebula", "🧅"), ("co", "corgi", "🐕"),
    ("cu", "cukierek", "🍬"), ("cy", "cytryna", "🍋"),
    ("cia", "ciastko", "🍪"), ("cie", "cielę", "🐄"), ("cio", "ciocia", "👩"),
    ("ciu", "ciuchcia", "🚂"), ("ci", "cichy", "🤫"),
    ("da", "dach", "🏠"), ("de", "deska", "🪵"), ("do", "dom", "🏡"),
    ("du", "duch", "👻"), ("dy", "dynia", "🎃"),
    ("fa", "farby", "🎨"), ("fe", "ferie", "⛷️"), ("fo", "foka", "🦭"),
    ("fu", "futbol", "⚽"), ("fi", "filiżanka", "☕"), ("fy", "żyrafy", "🦒"),
    ("ga", "garnek", "🍲"), ("ge", "gepard", "🐆"), ("go", "gołąb", "🕊️"),
    ("gu", "guzik", "🔘"), ("gi", "gitara", "🎸"),
    ("ha", "hamak", CUSTOM_SVG), ("he", "helikopter", "🚁"), ("ho", "hotel", "🏨"),
    ("hu", "hulajnoga", "🛴"), ("hi", "hipopotam", "🦛"), ("hy", "hybryda", "🚗"),
    ("ja", "jabłko", "🍎"), ("je", "jeż", "🦔"), ("jo", "jogurt", "🥣"),
    ("ju", "judo", "🥋"),
    ("ka", "kaczka", "🦆"), ("ke", "kelner", "🧑‍🍳"), ("ko", "kot", "🐈"),
    ("ku", "kura", "🐔"), ("ki", "kino", "🎬"),
    ("la", "lalka", "🪆"), ("le", "lew", "🦁"), ("lo", "lody", "🍦"),
    ("lu", "lupa", "🔍"), ("li", "lis", "🦊"),
    ("ła", "łapa", "🐾"), ("łe", "łezka", "😢"), ("ło", "łoś", "🫎"),
    ("łu", "łuk", "🏹"), ("ły", "łyżka", "🥄"),
    ("ma", "mama", "👩"), ("me", "medal", "🏅"), ("mo", "motyl", "🦋"),
    ("mu", "mucha", "🪰"), ("mi", "miś", "🧸"), ("my", "mysz", "🐁"),
    ("na", "namiot", "⛺"), ("ne", "neon", "💡"), ("no", "nos", "👃"),
    ("nu", "nurek", "🤿"), ("ny", "balony", "🎈"),
    ("nia", "niania", "👩‍🍼"), ("nie", "niedźwiedź", "🐻"), ("nio", "anioł", "👼"),
    ("niu", "niunia", "👧"), ("ni", "nitka", "🧵"),
    ("pa", "papuga", "🦜"), ("pe", "peleryna", "🦸"), ("po", "pociąg", "🚆"),
    ("pu", "pudełko", "📦"), ("pi", "piłka", "⚽"), ("py", "pytajnik", "❓"),
    ("ra", "rak", "🦀"), ("re", "rekin", "🦈"), ("ro", "rower", "🚲"),
    ("ru", "rura", "🔧"), ("ry", "ryba", "🐟"),
    ("sa", "samolot", "✈️"), ("se", "ser", "🧀"), ("so", "sowa", "🦉"),
    ("su", "suwak", "🤐"), ("sy", "syrena", "🧜‍♀️"),
    ("sia", "siatka", "🥅"), ("sie", "siekiera", "🪓"), ("sio", "siodło", "🐎"),
    ("siu", "siup", "🤸"), ("si", "sito", "🥣"),
    ("ta", "tata", "👨"), ("te", "telefon", "📱"), ("to", "tort", "🎂"),
    ("tu", "tulipan", "🌷"), ("ty", "tygrys", "🐅"),
    ("wa", "walizka", "🧳"), ("we", "wentylator", "🪭"), ("wo", "worek", "🎒"),
    ("wu", "wujek", "👨"), ("wi", "widelec", "🍴"), ("wy", "wyspa", "🏝️"),
    ("za", "zamek", "🏰"), ("ze", "zebra", "🦓"), ("zo", "zoo", "🦁"),
    ("zu", "zupa", "🍲"), ("zy", "pozytywka", "🎵"),
    ("zia", "ziarno", "🌾"), ("zie", "ziemniak", "🥔"), ("zio", "zioła", "🌿"),
    ("ziu", "Józiu", "👦"), ("zi", "zima", "❄️"),
    ("ża", "żaba", "🐸"), ("że", "żeglarz", "⛵"), ("żo", "żonkil", "🌼"),
    ("żu", "żuk", "🪲"), ("ży", "żyrafa", "🦒"),
    ("cha", "chata", "🛖"), ("che", "chemik", "🧪"), ("cho", "choinka", "🎄"),
    ("chu", "chustka", "🧣"), ("chi", "orchidea", "🌸"), ("chy", "chytry", "🦊"),
    ("cza", "czapka", "🧢"), ("cze", "czekolada", "🍫"), ("czo", "czoło", "🙂"),
    ("czu", "czułki", "🐌"), ("czy", "czytanie", "📖"),
    ("dza", "kukurydza", "🌽"), ("dze", "pieniądze", "🪙"), ("dzo", "bardzo", "👍"),
    ("dzu", "wodzu", "👑"), ("dzy", "koledzy", "🧒"),
    ("dzia", "dziadek", "👴"), ("dzie", "dziecko", "🧒"), ("dzio", "dziobak", "🦆"),
    ("dziu", "dziura", "🕳️"), ("dzi", "dzik", "🐗"),
    ("dża", "Dżakarta", "🏙️"), ("dże", "dżem", "🍓"), ("dżo", "dżokej", "🏇"),
    ("dżu", "dżungla", "🌴"), ("dży", "dżdżysty", "🌧️"),
    ("rza", "Marzanna", "🎎"), ("rze", "rzeka", "🏞️"), ("rzo", "rzodkiewka", "🥕"),
    ("rzu", "rzutka", "🎯"), ("rzy", "grzyb", "🍄"),
    ("sza", "szafa", "🚪"), ("sze", "szelki", "🦺"), ("szo", "szop", "🦝"),
    ("szu", "szuflada", "🗄️"), ("szy", "szyszka", "🌲"),
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
    label = word.lower()
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
    mapping = {syllable: word for syllable, word, _ in ENTRIES}
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
        sound = f"[{filename}.wav](./sounds/{filename}.wav)"
        output.append(f"| {consonant} | {vowel} | {syllable} | {image} | {sound} |")
    ASSETS_MD.write_text("\n".join(output) + "\n", encoding="utf-8")


def create_svgs() -> None:
    for index, (syllable, word, emoji) in enumerate(ENTRIES):
        if syllable == "pa" or emoji == CUSTOM_SVG:
            continue
        filename = f"{syllable}_{slug(word)}.svg"
        (IMAGES_DIR / filename).write_text(svg_content(word, emoji, index), encoding="utf-8")


async def create_audio(entry, semaphore, temp_dir):
    syllable, word, _ = entry
    if syllable == "pa":
        return None
    filename = f"{syllable}_{slug(word)}"
    output_path = SOUNDS_DIR / f"{filename}.wav"
    if output_path.exists():
        return None
    mp3_path = temp_dir / f"{filename}.mp3"
    async with semaphore:
        for attempt in range(3):
            try:
                communicate = edge_tts.Communicate(word, VOICE, rate="-10%")
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
    return filename


async def main() -> None:
    syllables = [entry[0] for entry in ENTRIES]
    if len(ENTRIES) != 156 or len(set(syllables)) != 156:
        raise RuntimeError(f"Expected 156 unique syllables, found {len(ENTRIES)} / {len(set(syllables))}")
    generated_svg_count = sum(
        syllable != "pa" and emoji != CUSTOM_SVG for syllable, _, emoji in ENTRIES
    )
    update_markdown()
    create_svgs()
    semaphore = asyncio.Semaphore(4)
    with tempfile.TemporaryDirectory(prefix="logopeda-audio-") as directory:
        await asyncio.gather(*(create_audio(entry, semaphore, Path(directory)) for entry in ENTRIES))
    print(f"Generated mappings for {len(ENTRIES)} rows, {generated_svg_count} SVGs, and {len(ENTRIES) - 1} WAVs.")


if __name__ == "__main__":
    asyncio.run(main())

Aplikacja została zaprojektowana tak, aby można było korzystać z niej za pomocą ekranu dotykowego, myszy, klawiatury oraz czytnika ekranu.

## Obsługa klawiaturą

- Naciśnij Tab, aby przejść do następnego przycisku lub odnośnika.
- Naciśnij Shift+Tab, aby wrócić do poprzedniego elementu.
- Naciśnij Enter lub spację, aby uruchomić wybrane ćwiczenie.
- Zielony kontur wskazuje element, który jest aktualnie wybrany za pomocą klawiatury.

## Dźwięk

- Naciśnij obraz w kafelku, aby odtworzyć nagranie przykładowego słowa.
- Naciśnij żółto podkreśloną sylabę pod obrazem, aby odtworzyć nagranie samej sylaby.
- Nagranie sylaby jest wycinane z nagrania przykładowego słowa, dlatego zachowuje jej naturalną polską wymowę. Krótka cisza przed sylabą i po niej zapobiega zbyt gwałtownemu rozpoczęciu i zakończeniu dźwięku.
- Naciśnij dużą, żółto podkreśloną literę, aby odtworzyć po kolei wszystkie nagrania na stronie. Nagrania są odtwarzane zgodnie z aktualnie wybraną kolejnością.
- Naciśnij literę ponownie podczas odtwarzania lub pauzy, aby anulować pozostałe nagrania.
- Naciśnij przycisk Litery, aby wrócić do indeksu liter.

W ustawieniach można wyłączyć dźwięk, zmienić jego głośność oraz ustawić długość pauzy między nagraniami od 400 do 700 ms. Domyślna pauza wynosi 500 ms. Każdy przycisk ćwiczenia ma opis, który podaje sylabę oraz słowo odtwarzane w nagraniu.

## Czytniki ekranu

Przyciski, odnośniki i obszary nawigacji mają polskie etykiety opisujące ich działanie. Po otwarciu nowego widoku fokus jest przenoszony na jego nagłówek, co ułatwia rozpoznanie bieżącej strony.

## Czytelność i ruch

- Duże przyciski ułatwiają obsługę dotykową i wybieranie elementów.
- Widoczny zielony kontur ułatwia śledzenie fokusu klawiatury.
- Układ dopasowuje się do mniejszych ekranów i powiększonego tekstu.
- Gdy urządzenie ma włączone ograniczenie animacji, aplikacja wyłącza przejścia ruchowe.

## Pochodzenie zasobów i praca deweloperska

Plik `scripts/generate_exercise_assets.py` zawiera źródłową listę `ENTRIES`. Każda pozycja określa wyświetlaną sylabę, słowo z zaznaczonym fragmentem, przykładowe słowo oraz emoji albo wartość `CUSTOM_SVG`. Dwa łączniki w drugim polu wyznaczają fragment słowa używany jako sylaba:

```python
("ca", "-ca-łus", "całus", "💋")
("nio", "a-nio-ł", "anioł", "👼")
("ny", "balo-ny-", "balony", "🎈")
```

### Skąd pochodzą pliki

- Nagrania słów w `assets/sounds` tworzy usługa Edge TTS głosem `pl-PL-ZofiaNeural` z szybkością `-10%`.
- Pliki `assets/sounds/pa_papuga.wav` i `assets/images/pa_papuga.svg` są ręcznie dostarczonymi wyjątkami przechowywanymi w repozytorium; generator ich nie zastępuje.
- Nagrania sylab w `assets/sounds/syllables` są wycinane z nagrań odpowiednich słów. Nie są syntezowane osobno.
- Słownik `CARRIER_SYLLABLE_RANGES` zapisuje dla każdej sylaby czas początku, automatycznie wyznaczony czas końca i ręczną korektę końca w milisekundach.
- Generator dodaje 50 ms ciszy przed wyciętym fragmentem i 50 ms po nim, a następnie zapisuje WAV jako mono, 22050 Hz, 16-bit PCM.
- Standardowe obrazy SVG w `assets/images` są generowane z przykładowego słowa, emoji i palet zdefiniowanych w skrypcie. Pozycje oznaczone `CUSTOM_SVG` są osobnymi, przygotowanymi przez dewelopera ilustracjami i nie są nadpisywane przez generator.
- Obecne ilustracje `CUSTOM_SVG` utworzono 11 sierpnia 2026 roku. Znane problemy z ich rozpoznawalnością i wymagane poprawki są zapisane w `assets/images/images-to-improve/candidates-to-improve.md`. Ten plik jest rejestrem kontroli jakości, a nie katalogiem obrazów używanym bezpośrednio przez aplikację.
- Plik `assets/assets.md` jest generowanym indeksem używanym przez aplikację. Zawiera sylabę, odnośnik do dźwięku sylaby, odnośnik do dźwięku słowa i odnośnik do obrazu. Nie należy ręcznie poprawiać wygenerowanych wierszy, ponieważ kolejny przebieg skryptu je odtworzy.

### Dodawanie nowego zasobu

1. Dodaj czteroelementową pozycję do `ENTRIES` i zaznacz docelową sylabę dwoma łącznikami.
2. Dodaj dla tej samej sylaby pozycję `(start_seconds, end_seconds, end_offset_ms)` do `CARRIER_SYLLABLE_RANGES`.
3. Dodaj odpowiedni wiersz spółgłoski, samogłoski i sylaby do `assets/assets.md`; pozostałe kolumny uzupełni generator.
4. Uruchom `.\.venv\Scripts\python.exe .\scripts\generate_exercise_assets.py` z katalogu głównego projektu. Skrypt tworzy tylko brakujące pliki.
5. Sprawdź wymowę słowa i sylaby w aplikacji. Jeżeli zmieniły się pliki dostępne pod istniejącymi adresami, zwiększ numer `CACHE_NAME` w `service-worker.js`.

### Ręczna korekta końca sylaby

Trzecia liczba w zakresie przesuwa tylko koniec wycinanego fragmentu. Wartość jest podawana w milisekundach:

```python
"ry": (0.00, 0.22, 0),    # bez korekty
"ry": (0.00, 0.22, -10),  # zakończ 10 ms wcześniej
"ry": (0.00, 0.22, 10),   # zakończ 10 ms później
```

Po zmianie korekty usuń tylko odpowiadający jej plik, na przykład `assets/sounds/syllables/ry.wav`, i uruchom generator ponownie. Istniejące pliki WAV są pomijane, dlatego sama zmiana liczby nie przebuduje nagrania.

### Niestandardowy obraz ćwiczenia

To mechanizm deweloperski służący do zastępowania nieodpowiedniego obrazu wygenerowanego z emoji. Aplikacja nie udostępnia użytkownikowi funkcji przesyłania własnych obrazów.

1. Sprawdź `assets/images/images-to-improve/candidates-to-improve.md`. Rejestr podaje aktualny problem i oczekiwaną poprawkę dla każdej zakwestionowanej ilustracji.
2. Przygotuj poprawiony plik SVG przedstawiający dokładnie wskazane słowo. Obraz powinien być jednoznaczny dla dziecka i nie może przedstawiać podobnego, ale innego przedmiotu, zwierzęcia ani zawodu.
3. W pozycji `ENTRIES` ustaw czwarte pole na `CUSTOM_SVG`. Zapobiega to zastąpieniu ręcznie przygotowanego pliku przez standardowy generator emoji.
4. Umieść plik pod dokładną nazwą `assets/images/<sylaba>_<słowo>.svg`, zgodną z odnośnikiem w `assets/assets.md`.
5. Otwórz ćwiczenie na dużym i małym ekranie oraz sprawdź rozpoznawalność obrazu, jego kadrowanie, czytelność podpisu i zgodność ze słowem.
6. Po zaakceptowaniu poprawki usuń odpowiedni wiersz z `candidates-to-improve.md` albo zaktualizuj opis, jeżeli ilustracja nadal wymaga pracy.
7. Uruchom generator i potwierdź, że plik `CUSTOM_SVG` nie został zmieniony. Następnie zwiększ numer `CACHE_NAME` w `service-worker.js`.

Aktualny rejestr obejmuje niestandardowe ilustracje słów: bocian, deska, dziobak, kelner, rura, suwak, sito, rzodkiewka, szyszka, wentylator i worek.

### Własne nagranie sylaby

1. Przygotuj plik WAV mono, 22050 Hz, 16-bit PCM.
2. Umieść go jako `assets/sounds/syllables/<sylaba>.wav`, zastępując plik wygenerowany.
3. Nie usuwaj własnego pliku przed uruchomieniem generatora. Generator pomija istniejące WAV-y, więc zachowa wersję niestandardową.
4. Zwiększ numer `CACHE_NAME` w `service-worker.js`, aby zainstalowana aplikacja pobrała nową wersję nagrania.

# lista-detali
Generator plików PDF z listą składowych detalu

## Opis projektu
Projekt `lista-detali` służy do generowania plików PDF, które zawierają listę składowych elementów detalu. Skrypty wykorzystują dane wejściowe i tworzą estetycznie przygotowane raporty w formacie PDF.

## Wymagania systemowe
- Windows 8 lub nowszy

## Instalacja

1. a) Sklonuj repozytorium:
    ```bash
    git clone <url-repozytorium>
    ```
    b) Pobierz kopię repozytorium - `Code -> Download ZIP`


2. Ustaw folder z obrazkami wykorzystywany w kartach identyfikacyjnych w `.env`, utworzonym przez skopiowanie istniejącego `.env.example` w folderze głównym.

## Użycie

1. Uruchom plik `lista-detali\dist\Lista Detali\Lista Detali.exe`

2. Wprowadź numer SN detalu.

## Struktura projektu

- `app.py` – główny skrypt generujący PDF.
- `requirements.txt` – lista wymaganych bibliotek.
- `dist/` - folder ze skompilowanym programem.
- `resources` - folder z dodatkowymi plikami wykorzystywanymi przez program.
- `output/` – folder, do którego zostaną zapisane wygenerowane pliki PDF.


## Licencja

Projekt jest dostępny na licencji MIT.

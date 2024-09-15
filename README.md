# lista-detali
Generator plików PDF z listą składowych detalu

## Opis projektu
Projekt `lista-detali` służy do generowania plików PDF, które zawierają listę składowych elementów detalu. Skrypty wykorzystują dane wejściowe i tworzą estetycznie przygotowane raporty w formacie PDF.

## Wymagania systemowe
- Python 3.12 lub nowszy
- Biblioteki z pliku `requirements.txt`

## Instalacja

1. Sklonuj repozytorium:
    ```bash
    git clone <url-repozytorium>
    ```

2. Przejdź do folderu projektu:
    ```bash
    cd lista-detali
    ```

3. Zainstaluj wymagane zależności:
    ```bash
    pip install -r requirements.txt
    ```

4. Ustaw folder z obrazkami wykorzystywany w kartach identyfikacyjnych w `.env`, utworzonym przez skopiowanie istniejącego `.env.example`.

## Użycie

1. Uruchom skrypt generujący pliki PDF:
    ```bash
    python app.py
    ```

2. Wprowadź numer SN detalu.

## Struktura projektu

- `app.py` – główny skrypt generujący PDF.
- `requirements.txt` – lista wymaganych bibliotek.
- `output/` – folder, do którego zostaną zapisane wygenerowane pliki PDF.


## Licencja

Projekt jest dostępny na customowej licencji.

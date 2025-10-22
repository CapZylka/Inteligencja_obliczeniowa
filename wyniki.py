import json
import argparse
import sys
import os
import matplotlib.pyplot as plt

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Błąd: Wymagana biblioteka 'matplotlib' nie jest zainstalowana.", file=sys.stderr)
    print("Uruchom: pip install matplotlib", file=sys.stderr)
    sys.exit(1)


def wczytaj_wyniki(filepath):
    """Wczytuje plik JSON z wynikami."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Błąd: Plik {filepath} nie jest poprawnym plikiem JSON.", file=sys.stderr)
        sys.exit(1)

def generuj_okno_tabeli(data):
    """Tworzy okno Matplotlib z tabelą wyników."""
    
    strategie = data.get("wyniki_strategii", [])
    if not strategie:
        print("Brak wyników strategii do wyświetlenia w tabeli.", file=sys.stderr)
        return

    # Wczytanie danych do tabeli
    col_labels = ["Nazwa Strategii", "PK", "PM", "Najlepszy Wynik", "Śr. Konfliktów"]
    cell_data = []
    
    try:
        najlepsza_srednia = min(s["srednia_konfliktow_finalna"] for s in strategie)
    except (ValueError, KeyError):
        najlepsza_srednia = float('inf')

    for s in strategie:
        srednia = s.get('srednia_konfliktow_finalna', float('inf'))
        srednia_str = f"{srednia:.2f}"
        
        # Najlepszy wynik
        if srednia == najlepsza_srednia:
            srednia_str = f"{srednia_str} zwycięzca"
            
        cell_data.append([
            s.get('nazwa', '?'),
            s.get('pk', '?'),
            s.get('pm', '?'),
            s.get('najlepszy_wynik', '?'),
            srednia_str
        ])

    # Informacje o eksperymencie
    info = data.get("info_eksperymentu", {})
    info_title = (
        f"Eksperyment: {os.path.basename(info.get('graf', ''))} "
        f"({info.get('liczba_wierzcholkow')}w, {info.get('liczba_krawedzi')}k, {info.get('liczba_kolorow')}c)\n"
        f"Parametry: {info.get('liczba_generacji')} generacji, populacja {info.get('rozmiar_populacji')}, "
        f"{info.get('liczba_uruchomien_na_zestaw')} uruchomień/zestaw"
    )

    # Stworzenie okna dla tabeli
    fig_table, ax_table = plt.subplots(figsize=(12, 4)) # Rozmiar okna
    ax_table.axis('tight')
    ax_table.axis('off')

    # Zzerokości kolumn
    col_widths = [0.4, 0.1, 0.1, 0.2, 0.2] 

    # Tworzenie obiektu tabeli
    tabelka = ax_table.table(
        cellText=cell_data,
        colLabels=col_labels,
        colWidths=col_widths,
        loc='center',
        cellLoc='left'
    )
    
    # Ustawienia stylu
    tabelka.auto_set_font_size(False)
    tabelka.set_fontsize(10)
    tabelka.scale(1, 1.5) # Skalowanie komórek

    # Ustawienie tytułu
    ax_table.set_title(info_title, fontsize=14, pad=20)
    fig_table.tight_layout() # Dopasowanie, by nic się nie obcięło


def generuj_wykres_zbieznosci(data):
    """Tworzy okno Matplotlib z wykresem zbieżności."""
    
    strategie = data.get("wyniki_strategii", [])
    if not strategie:
        print("Brak danych do wygenerowania wykresu.", file=sys.stderr)
        return

    # Tworzenie okna dla wykresu
    plt.figure(figsize=(14, 8))
    
    for s in strategie:
        historia = s.get("srednia_historia_zbieznosci")
        if historia:
            plt.plot(historia, label=f"{s.get('nazwa')} (PK={s.get('pk')}, PM={s.get('pm')})", linewidth=2)

    # Dodanie info
    info = data.get("info_eksperymentu", {})
    graf_name = os.path.basename(info.get('graf', ''))
    title = f"Zbieżność Algorytmu dla Grafu: {graf_name}\n({info.get('liczba_wierzcholkow')} wierzchołków, {info.get('liczba_kolorow')} kolorów)"
    
    plt.title(title, fontsize=16)
    plt.xlabel("Numer Generacji", fontsize=12)
    plt.ylabel("Średnia liczba konfliktów", fontsize=12)
    plt.legend(loc='upper right', fontsize=10)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.minorticks_on()
    plt.tight_layout()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generator wizualizacji z plików wyników GA.")
    parser.add_argument("sciezka_do_wynikow", type=str, 
                        help="Ścieżka do pliku .json z wynikami (np. wyniki/wyniki_graph_1_k3.json)")
    
    args = parser.parse_args()

    # Wczytanie danych
    dane = wczytaj_wyniki(args.sciezka_do_wynikow)

    # Generowanie okna tabeli
    generuj_okno_tabeli(dane)

    # Generowanie oknawykresu
    generuj_wykres_zbieznosci(dane)

    # Otwieranie okien
    print("Otwieranie okien z wynikami...")
    plt.show()
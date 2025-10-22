import random
import argparse
import json
import sys
import os

KATALOG_WYNIKOW = "wyniki"

def wczytaj_graf_z_pliku(filepath):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            if "liczba_wierzcholkow" not in data or "krawedzie" not in data:
                print(f"Błąd: Plik {filepath} ma niepoprawny format.", file=sys.stderr)
                sys.exit(1)
            data["krawedzie"] = [tuple(krawedz) for krawedz in data["krawedzie"]]
            return data
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Błąd: Plik {filepath} nie jest poprawnym plikiem JSON.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd przy wczytywaniu pliku: {e}", file=sys.stderr)
        sys.exit(1)

# FUNKCJE ALGORYTMU GENETYCZNEGO

def stworz_osobnika(liczba_wierzcholkow, liczba_kolorow):

    # Tworzy losowego osobnika (chromosom).
    # W losowy sposób koloruje każdy wierzchołek grafu.

    return [random.randint(0, liczba_kolorow - 1) for _ in range(liczba_wierzcholkow)]

def oblicz_przystosowanie(osobnik, krawedzie):

    # Oblicza funkcję przystosowania dla osobnika.
    # Sprawdza ilość konfilktów (takich samych kolorów obok siebie).

    liczba_konfliktow = 0
    for u, v in krawedzie:
        if osobnik[u] == osobnik[v]:
            liczba_konfliktow += 1

    # Zwracamy wskaźnik przystosowania (1.0 = 0 konfliktów)
    return 1.0 / (1.0 + liczba_konfliktow)

def selekcja_turniejowa(populacja, przystosowania, rozmiar_turnieju):

    # Wybiera najlepszego osobnika z losowo wybranej grupy turniejowej.

    # Losowanie uczestników
    indeksy_uczestnikow = random.sample(range(len(populacja)), rozmiar_turnieju)
    
    najlepszy_indeks = -1
    najlepsze_przystosowanie = -1.0
    
    # Szukanie zwycięzcy
    for indeks in indeksy_uczestnikow:
        if przystosowania[indeks] > najlepsze_przystosowanie:
            najlepsze_przystosowanie = przystosowania[indeks]
            najlepszy_indeks = indeks
            
    return populacja[najlepszy_indeks]

def krzyzowanie(rodzic1, rodzic2, p_krzyzowania):

    # Wykonuje krzyżowanie jednopunktowe.

    # Kopia rodziców żeby nie zmieniać orginału
    dziecko1, dziecko2 = list(rodzic1), list(rodzic2)
    
    if random.random() < p_krzyzowania:
        if len(rodzic1) > 1:
            punkt_ciecia = random.randint(1, len(rodzic1) - 1)
            
            # Tworzy dzieci łącząc "geny" rodziców oddzielone w miejscu cięcia
            dziecko1 = rodzic1[:punkt_ciecia] + rodzic2[punkt_ciecia:]
            dziecko2 = rodzic2[:punkt_ciecia] + rodzic1[punkt_ciecia:]
        
    return dziecko1, dziecko2

def mutacja(osobnik, p_mutacji, liczba_kolorow):

    # Wykonuje mutację - losowo zmienia kolor jednego wierzchołka.

    # Kopia, żeby nie modyfikować orginału
    zmutowany_osobnik = list(osobnik)
    
    for i in range(len(zmutowany_osobnik)):
        if random.random() < p_mutacji:
            # Zmiana kolru na losowy
            zmutowany_osobnik[i] = random.randint(0, liczba_kolorow - 1)
            
    return zmutowany_osobnik

# GŁÓWNA FUNKCJA URUCHOMIENIOWA

def uruchom_ga(graf, liczba_kolorow, rozmiar_populacji, liczba_generacji, p_krzyzowania, p_mutacji, rozmiar_turnieju):

    # Główna pętla algorytmu genetycznego.

    liczba_wierzcholkow = graf["liczba_wierzcholkow"]
    krawedzie = graf["krawedzie"]
    
    # Lista do śledzenia najlepszego wyniku w każdej generacji
    historia_postepow = []
    
    # 1. Inicjalizacja
    populacja = [stworz_osobnika(liczba_wierzcholkow, liczba_kolorow) for _ in range(rozmiar_populacji)]
    
    najlepszy_osobnik_globalnie = None
    najlepsze_przystosowanie_globalnie = -1.0
    
    # 2. Pętla ewolucji
    for generacja in range(liczba_generacji):
        
        # 3. Ocena
        przystosowania = [oblicz_przystosowanie(osobnik, krawedzie) for osobnik in populacja]
        
        aktualne_najlepsze_przystosowanie_w_populacji = max(przystosowania)
        
        # Aktualizacja najlepszego globalnego rozwiązania
        if aktualne_najlepsze_przystosowanie_w_populacji > najlepsze_przystosowanie_globalnie:

            najlepsze_przystosowanie_globalnie = aktualne_najlepsze_przystosowanie_w_populacji
            
            indeks_najlepszego = przystosowania.index(najlepsze_przystosowanie_globalnie)
            najlepszy_osobnik_globalnie = list(populacja[indeks_najlepszego])
            
        # Zapisywanie najlepszego wyniku do tej pory
        aktualne_konflikty = (1.0 / najlepsze_przystosowanie_globalnie) - 1.0
        historia_postepow.append(int(round(aktualne_konflikty)))
            
        # Break zakomentowany na potrzeby prezentacji wyników
        # if najlepsze_przystosowanie_globalnie == 1.0:
        #     break
        
        # 4. Tworzenie nowej populacji
        nowa_populacja = []
        while len(nowa_populacja) < rozmiar_populacji:
            
            # 5. Selekcja
            rodzic1 = selekcja_turniejowa(populacja, przystosowania, rozmiar_turnieju)
            rodzic2 = selekcja_turniejowa(populacja, przystosowania, rozmiar_turnieju)
            
            # 6. Krzyżowanie
            dziecko1, dziecko2 = krzyzowanie(rodzic1, rodzic2, p_krzyzowania)
            
            # 7. Mutacja
            dziecko1 = mutacja(dziecko1, p_mutacji, liczba_kolorow)
            dziecko2 = mutacja(dziecko2, p_mutacji, liczba_kolorow)
            
            nowa_populacja.append(dziecko1)
            if len(nowa_populacja) < rozmiar_populacji:
                nowa_populacja.append(dziecko2)
                
        # Zastąpienie starej populacji nową
        populacja = nowa_populacja
        
    finalne_konflikty = historia_postepow[-1]
    
    return najlepszy_osobnik_globalnie, finalne_konflikty, historia_postepow


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Algorytm Genetyczny dla Kolorowania Grafu.")
    parser.add_argument("sciezka_do_grafu", type=str, 
                        help="Ścieżka do pliku .json z definicją grafu.")
    parser.add_argument("-k", "--kolory", type=int, default=3, 
                        help="Liczba kolorów do testu (default: 3)")
    
    args = parser.parse_args()
    
    print("Start eksperymentu")
    
    # Konfiguracja
    WYBRANY_GRAF = wczytaj_graf_z_pliku(args.sciezka_do_grafu)
    LICZBA_KOLOROW_DO_TESTU = args.kolory
    LICZBA_URUCHOMIEN_NA_ZESTAW = 10
    
    # Parametry algorytmu
    PODSTAWOWE_PARAMETRY = {
        "rozmiar_populacji": 50,  
        "liczba_generacji": 200, 
        "rozmiar_turnieju": 5    
    }

    # Zestawy parametrów do porównania
    zestawy_parametrow = [
        {"nazwa": "Niska mutacja", "p_krzyzowania": 0.9, "p_mutacji": 0.01},
        {"nazwa": "Średnia mutacja", "p_krzyzowania": 0.9, "p_mutacji": 0.1},
        {"nazwa": "Wysoka mutacja", "p_krzyzowania": 0.9, "p_mutacji": 0.2},
        {"nazwa": "Niskie krzyżowanie", "p_krzyzowania": 0.1, "p_mutacji": 0.1},
        {"nazwa": "Tylko krzyżowanie 100%", "p_krzyzowania": 1, "p_mutacji": 0},
        {"nazwa": "Sama mutacja 10%", "p_krzyzowania": 0, "p_mutacji": 0.1},
    ]

    print(f"Testowany Graf: {args.sciezka_do_grafu}")
    print(f"  > {WYBRANY_GRAF['liczba_wierzcholkow']} wierzchołków, {len(WYBRANY_GRAF['krawedzie'])} krawędzi.")
    print(f"Liczba kolorów: {LICZBA_KOLOROW_DO_TESTU}")
    
    # ZAPISYWANIE WYNIKÓW 
    wszystkie_wyniki = {
        "info_eksperymentu": {
            "graf": args.sciezka_do_grafu,
            "liczba_wierzcholkow": WYBRANY_GRAF['liczba_wierzcholkow'],
            "liczba_krawedzi": len(WYBRANY_GRAF['krawedzie']),
            "liczba_kolorow": LICZBA_KOLOROW_DO_TESTU,
            "liczba_uruchomien_na_zestaw": LICZBA_URUCHOMIEN_NA_ZESTAW,
            "rozmiar_populacji": PODSTAWOWE_PARAMETRY["rozmiar_populacji"],
            "liczba_generacji": PODSTAWOWE_PARAMETRY["liczba_generacji"]
        },
        "wyniki_strategii": []
    }
    
    # PĘTLA EKSPERYMENTU
    for zestaw in zestawy_parametrow:
        print(f"\n--- TEST: {zestaw['nazwa']} (PK={zestaw['p_krzyzowania']}, PM={zestaw['p_mutacji']}) ---")
        
        wyniki_konfliktow = []
        historie_uruchomien = [] # Zapisywanie historycznych wyników
        
        for i in range(LICZBA_URUCHOMIEN_NA_ZESTAW):
            # Uruchamianie głównego skryptu
            najlepszy, konflikty, historia = uruchom_ga(
                graf=WYBRANY_GRAF,
                liczba_kolorow=LICZBA_KOLOROW_DO_TESTU,
                rozmiar_populacji=PODSTAWOWE_PARAMETRY["rozmiar_populacji"],
                liczba_generacji=PODSTAWOWE_PARAMETRY["liczba_generacji"],
                p_krzyzowania=zestaw["p_krzyzowania"],
                p_mutacji=zestaw["p_mutacji"],
                rozmiar_turnieju=PODSTAWOWE_PARAMETRY["rozmiar_turnieju"]
            )
            
            print(f"Uruchomienie {i+1}: Znaleziono rozwiązanie z {konflikty} konfliktami.")
            if konflikty == 0:
                print(f"-> Idealne rozwiązanie: {najlepszy}")
            
            wyniki_konfliktow.append(konflikty)
            historie_uruchomien.append(historia) # Zapisz historię z tego uruchomienia
            
        # Obliczanie średniej zbieżności
        srednia_historia = []
        liczba_generacji = PODSTAWOWE_PARAMETRY["liczba_generacji"]
        for gen in range(liczba_generacji):
            suma_dla_generacji = sum(historia[gen] for historia in historie_uruchomien if len(historia) > gen)
            srednia_dla_generacji = suma_dla_generacji / LICZBA_URUCHOMIEN_NA_ZESTAW
            srednia_historia.append(round(srednia_dla_generacji, 2))
            
        # Podsumowanie dla zestawu parametrów
        srednia_konfliktow_final = sum(wyniki_konfliktow) / len(wyniki_konfliktow)
        najlepszy_wynik = min(wyniki_konfliktow)
        
        print(f"Podsumowanie dla '{zestaw['nazwa']}':")
        print(f"> Najlepszy wynik (min. konfliktów): {najlepszy_wynik}")
        print(f"> Średnia liczba konfliktów: {srednia_konfliktow_final:.2f}")
        
        # Dodaj do wyników strategii
        wszystkie_wyniki["wyniki_strategii"].append({
            "nazwa": zestaw['nazwa'],
            "pk": zestaw['p_krzyzowania'],
            "pm": zestaw['p_mutacji'],
            "najlepszy_wynik": najlepszy_wynik,
            "srednia_konfliktow_finalna": srednia_konfliktow_final,
            "srednia_historia_zbieznosci": srednia_historia # Dodaj uśredniony wykres
        })

    # ZAPIS WYNIKÓW DO PLIKU
    
    # Tworzenie nazwy odpowiedniej dla testu
    basename_grafu = os.path.basename(args.sciezka_do_grafu)
    nazwa_pliku_grafu_bez_rozszerzenia = os.path.splitext(basename_grafu)[0]
    nazwa_pliku_wynikow = f"wyniki_{nazwa_pliku_grafu_bez_rozszerzenia}_k{LICZBA_KOLOROW_DO_TESTU}.json"
    
    # Sprawdzanie czy katalog "wyniki" istenieje
    os.makedirs(KATALOG_WYNIKOW, exist_ok=True)
    
    sciezka_zapisu = os.path.join(KATALOG_WYNIKOW, nazwa_pliku_wynikow)
    
    try:
        with open(sciezka_zapisu, 'w') as f:
            json.dump(wszystkie_wyniki, f, indent=4)
        print(f"\nPomyślnie zapisano wyniki do pliku: {sciezka_zapisu}")
    except Exception as e:
        print(f"\nBłąd podczas zapisu wyników do pliku: {e}")
import os
import json
import random
import re
import argparse

# Katalog do zapisywania grafów
GRAPH_DIR = "grafy"

def find_next_graph_number(directory):
    """Przeszukuje katalog i znajduje następny wolny numer dla grafu."""
    
    # Upewnij się, że katalog istnieje
    os.makedirs(directory, exist_ok=True)
    
    pattern = re.compile(r'graph_(\d+)\.json')
    max_num = 0
    
    try:
        for filename in os.listdir(directory):
            match = pattern.match(filename)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
    except FileNotFoundError:
        # Katalog jeszcze nie istnieje, co jest ok
        pass
        
    return max_num + 1

def generate_random_graph(n, p):

    # Generuje graf losowy G(n, p) - n wierzchołków, p-prawdopodobieństwo krawędzi.

    krawedzie = []
    for i in range(n):
        for j in range(i + 1, n):
            # Dla każdej możliwej pary wierzchołków, losuj czy istnieje krawędź
            if random.random() < p:
                krawedzie.append((i, j))
                
    return {
        "liczba_wierzcholkow": n,
        "krawedzie": krawedzie
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generator skomplikowanych grafów losowych.")
    parser.add_argument("-n", "--wierzcholki", type=int, default=25, 
                        help="Liczba wierzchołków (default: 25)")
    parser.add_argument("-p", "--prawdopodobienstwo", type=float, default=0.2, 
                        help="Prawdopodobieństwo krawędzi (default: 0.2)")
    
    args = parser.parse_args()
    
    # Generowanie grafu
    graph_data = generate_random_graph(args.wierzcholki, args.prawdopodobienstwo)
    
    # Szukanie odpowiedniej nazwy dla pliku
    next_num = find_next_graph_number(GRAPH_DIR)
    filepath = os.path.join(GRAPH_DIR, f'graph_{next_num}.json')
    
    # Zapisywanie grafu do pliku JSON
    try:
        with open(filepath, 'w') as f:
            json.dump(graph_data, f, indent=2)
            
        print(f"   Wygenerowano graf:")
        print(f"   Wierzchołki: {args.wierzcholki}")
        print(f"   Krawędzie:   {len(graph_data['krawedzie'])}")
        print(f"   Zapisano w:  {filepath}")
        
    except IOError as e:
        print(f"Błąd zapisu pliku: {e}")
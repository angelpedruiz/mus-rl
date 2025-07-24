from mus_rl.envs.game_utils import build_deck, hand_str, evaluate_grande, evaluate_chica, evaluate_pares, evaluate_juego, evaluate_punto
import random

def main():
    
    # juego = 30/40 puntos
    # 1 vaca = 4 juegos
    '''
    4 cartas por jugador
    4 reyes
    4 ases
    4 treses - 4 reyes
    4 doses - ases (pitos)
    
    REPARTIR
    el que reparte se llama postre
    y es el ultimo en hablar
    el mano es el primero en hablar y en caso de empate gana. el suiguente en la cadena tiene la sugiunte preferencia 
    
    MUS
    si todos dicen mus hay que descartar al menos uno carta, puedes comunicarte con tu companero es decir esperar a que el otro diga mus y luego decirlo tu
    si alguno corta se empieza a jugar
    
    GRANDE
    tener las cartas mas altas, se ordenan de mayor a menor y se comparan una a una
    
    CHICA
    tener las cartas mas bajas, se ordenan de menor a mayor y se comparan una a una
      
    PARES
    cada jugador dice si tiene pares. 
    
    
    JUEGO/PUNTO
    se tiene en cuenta el valor de las cartas. para llegar a juego se necesitan 31 o mas
    los jugadores dicen si tienen juego o no.
    si al menos dos jugadores tienen juego, se comparan los valores de las cartas.
    el mejor juego es el 31,32,40,39,...,33
    
    /PUNTO
    el mejor punto es 30, 29, ...,
    
    PARES
    pares, triples/medias, duples(mas altos/bajos/gallegos)
    
    '''
    



    print("Welcome to Mus Simulator (Manual Mode)")
    num_players = 4
    cards_per_player = 4
    mano_index = 0
    print(f"(Mano is Player {mano_index + 1})")

    # Build full deck and deal hands
    full_deck = build_deck()
    random.shuffle(full_deck)

    hands = [full_deck[i * cards_per_player:(i + 1) * cards_per_player] for i in range(num_players)]
    deck_pointer = num_players * cards_per_player

    # Display initial hands
    for i, hand in enumerate(hands):
        print(f"\nPlayer {i + 1}'s hand:")
        for j, card in enumerate(hand):
            print(f"{j + 1}: {card}")  # numbered for discarding

    # --- Mus phase ---
    print("\n--- Mus Phase ---")

    while True:
        mus = True
        for i in range(num_players):
            choice = input(f'Player {i + 1}, do you want "mus"? (y/n): ').strip().lower()
            if choice != 'y':
                mus = False
                print(f"Player {i + 1} said no: CORTA. Proceeding to betting phase...\n")
                break

        if not mus:
            break

        print("\nAll players agreed: MUS! Discarding cards...")

        for i in range(num_players):
            while True:
                discard_input = input(
                    f'Player {i + 1}, enter card numbers to discard (comma-separated, e.g., "1,3"): '
                ).strip()
                try:
                    discard_indices = [int(x) - 1 for x in discard_input.split(',')]
                    if not (1 <= len(discard_indices) <= 4):
                        raise ValueError("You must discard between 1 and 4 cards.")
                    if any(idx < 0 or idx >= 4 for idx in discard_indices):
                        raise ValueError("Invalid card number.")
                    break
                except Exception as e:
                    print(f"Error: {e}. Try again.")

            # Discard and replace cards
            for idx in discard_indices:
                if deck_pointer >= len(full_deck):
                    print("Deck is empty! Cannot replace more cards.")
                    break
                hands[i][idx] = full_deck[deck_pointer]
                deck_pointer += 1

        # Show updated hands
        for i, hand in enumerate(hands):
            print(f"\nPlayer {i + 1}'s new hand:")
            for j, card in enumerate(hand):
                print(f"{j + 1}: {card}")
        print("\n--- Another round of Mus ---")
    
    # --- Grande phase ---
    print("--- Grande Phase ---")
    grande_winner = evaluate_grande(hands, mano_index)
    print(f"Player {grande_winner + 1} wins Grande!")
    
    # --- Chica phase ---
    print("\n--- Chica Phase ---")
    chica_winner = evaluate_chica(hands, mano_index)
    print(f"Player {chica_winner + 1} wins Chica!")
    
    # --- Pares phase ---
    print("\n--- Pares Phase ---")
    pares_winner = evaluate_pares(hands, mano_index)

    if pares_winner is not None:
        print(f"Player {pares_winner + 1} wins Pares!")
    else:
        print("No one has pares.")
        
    # --- Juego phase ---
    print("\n--- Juego Phase ---")
    juego_winner = evaluate_juego(hands, mano_index)

    if juego_winner is not None:
        print(f"Player {juego_winner + 1} wins Juego!")
    else:
        print("No one has juego (less than 31 points). Proceeding to Punto...")

        # --- Punto phase ---
        print("\n--- Punto Phase ---")
        punto_winner = evaluate_punto(hands, mano_index)
        print(f"Player {punto_winner + 1} wins Punto!")

        
if __name__ == "__main__":
    main()
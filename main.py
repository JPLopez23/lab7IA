import math
from game_loop import GameLoop
from experiments import experiment_3x3, experiment_4x4, ia_duel


def print_menu():
    print("\n" + "="*50)
    print("  LAB 07 — Búsqueda Adversaria")
    print("="*50)
    print("  1. Jugar Tic-Tac-Toe (Humano vs IA)")
    print("  2. Jugar Tic-Tac-Toe (IA vs IA, demo)")
    print("  3. Exp. 2a: Explosión combinatoria 3×3")
    print("  4. Exp. 2b: Explosión combinatoria 4×4 (α-β)")
    print("  5. Exp. 3:  Duelo IA-IA (20 partidas)")
    print("  0. Salir")
    print("="*50)


def choose_ia_config(label="IA"):
    """Menú para configurar una IA."""
    print(f"\n  Configuración {label}:")
    print("    1. Alpha-Beta (recomendado)")
    print("    2. Minimax limitado")
    print("    3. MCTS")
    opt = input("  Opción [1]: ").strip() or "1"

    if opt == "2":
        d = int(input("    Depth [4]: ").strip() or "4")
        return {'algo': 'minimax_limit', 'depth': d}
    elif opt == "3":
        n = int(input("    Simulaciones N [500]: ").strip() or "500")
        c = float(input(f"    Constante C [{math.sqrt(2):.4f}]: ").strip() or str(math.sqrt(2)))
        return {'algo': 'mcts', 'N': n, 'C': c}
    else:
        d = int(input("    Depth [4]: ").strip() or "4")
        return {'algo': 'alpha_beta', 'depth': d}


def main():
    while True:
        print_menu()
        choice = input("\n  Opción: ").strip()

        if choice == "0":
            print("  ¡Hasta luego!")
            break

        elif choice == "1":
            size = int(input("  Tamaño del tablero (3 o 4) [3]: ").strip() or "3")
            sp = input("  ¿Quién empieza? H=Humano, IA=IA [H]: ").strip().upper() or "H"
            cfg = choose_ia_config()
            gl = GameLoop(size=size, mode="H-IA", starting_player=sp, ia_configs=cfg)
            gl.play()

        elif choice == "2":
            size = int(input("  Tamaño del tablero (3 o 4) [4]: ").strip() or "4")
            cfg_ia1 = choose_ia_config("IA-1")
            cfg_ia2 = choose_ia_config("IA-2")
            ia_configs = {'IA1': cfg_ia1, 'IA2': cfg_ia2}
            gl = GameLoop(size=size, mode="IA-IA", starting_player='IA',
                          ia_configs=ia_configs)
            gl.play()

        elif choice == "3":
            experiment_3x3()

        elif choice == "4":
            experiment_4x4()

        elif choice == "5":
            n = int(input("  Número de partidas [20]: ").strip() or "20")
            size = int(input("  Tamaño del tablero (3 o 4) [4]: ").strip() or "4")
            ia_duel(n_games=n, board_size=size)

        else:
            print("  Opción inválida.")


if __name__ == "__main__":
    main()

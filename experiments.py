import math
import time
import copy
from tictactoe_engine import TicTacToeEngine
from game_loop import GameLoop


# ======================================================================
#  Sección 2a — Explosión combinatoria en 3×3
# ======================================================================

def experiment_3x3():
    print("\n" + "="*60)
    print("  SECCIÓN 2a: Explosión Combinatoria — Tic-Tac-Toe 3×3")
    print("="*60)
    print(f"\n{'Depth':>6} | {'Minimax Nodos':>14} | {'Minimax Tiempo':>14} | "
          f"{'AlphaBeta Nodos':>16} | {'AlphaBeta Tiempo':>16}")
    print("-"*75)

    results = []
    for depth in range(1, 10):
        # -- Minimax limitado --
        eng_mm = TicTacToeEngine(3)
        eng_mm.nodes_visited = 0
        t0 = time.time()
        if depth == 9:
            # Minimax puro solo para depth máximo (exhaustivo 3×3)
            eng_mm.minimax_pure(True)
        else:
            eng_mm.minimax_limit(depth, True)
        t_mm = time.time() - t0
        nodes_mm = eng_mm.nodes_visited

        # -- Alpha-Beta --
        eng_ab = TicTacToeEngine(3)
        eng_ab.nodes_visited = 0
        t0 = time.time()
        eng_ab.alpha_beta(depth, -math.inf, math.inf, True)
        t_ab = time.time() - t0
        nodes_ab = eng_ab.nodes_visited

        results.append((depth, nodes_mm, t_mm, nodes_ab, t_ab))
        print(f"{depth:>6} | {nodes_mm:>14,} | {t_mm:>13.4f}s | "
              f"{nodes_ab:>16,} | {t_ab:>15.4f}s")

    return results


# ======================================================================
#  Sección 2b — Explosión combinatoria en 4×4 con α-β
# ======================================================================

def experiment_4x4():
    print("\n" + "="*60)
    print("  SECCIÓN 2b: Explosión Combinatoria — Tic-Tac-Toe 4×4 (α-β)")
    print("="*60)
    print(f"\n{'Depth':>6} | {'Nodos':>12} | {'Tiempo':>10} | {'Factor Ramif.':>14}")
    print("-"*50)

    results = []
    for depth in range(1, 7):
        eng = TicTacToeEngine(4)
        eng.nodes_visited = 0
        t0 = time.time()
        eng.alpha_beta(depth, -math.inf, math.inf, True)
        elapsed = time.time() - t0
        nodes = eng.nodes_visited
        factor = nodes ** (1.0 / depth) if depth > 0 and nodes > 0 else 0
        results.append((depth, nodes, elapsed, factor))
        print(f"{depth:>6} | {nodes:>12,} | {elapsed:>9.4f}s | {factor:>14.2f}")

    return results


# ======================================================================
#  Sección 3 — Duelo IA-IA (20 partidas)
# ======================================================================

def ia_duel(n_games=20, board_size=4):
    """
    IA-1: MCTS con N=500 y C=√2
    IA-2: Minimax limitado depth=4 con poda α-β
    """
    print("\n" + "="*60)
    print(f"  SECCIÓN 3: Duelo IA-IA — {n_games} partidas en {board_size}×{board_size}")
    print("  IA-1: MCTS  (N=500, C=√2)")
    print("  IA-2: Alpha-Beta (depth=4)")
    print("="*60)

    ia_configs = {
        'IA1': {'algo': 'mcts',       'N': 500, 'C': math.sqrt(2)},
        'IA2': {'algo': 'alpha_beta', 'depth': 4}
    }

    wins = {'X': 0, 'O': 0, 'draw': 0}
    # IA1 juega como X en partidas impares, O en pares (alternamos)
    ia1_wins = 0
    ia2_wins = 0
    draws = 0

    times_ia1 = []
    times_ia2 = []

    for game_num in range(1, n_games + 1):
        # Alternamos quién empieza para evitar sesgo
        if game_num % 2 == 1:
            ia1_symbol, ia2_symbol = 'X', 'O'
            cfg = {
                'IA1': ia_configs['IA1'],
                'IA2': ia_configs['IA2']
            }
        else:
            ia1_symbol, ia2_symbol = 'O', 'X'
            cfg = {
                'IA1': ia_configs['IA2'],  # IA2 juega de X (primero)
                'IA2': ia_configs['IA1']   # IA1 juega de O
            }

        engine = TicTacToeEngine(board_size)
        turn = 'X'
        move_times = {'X': [], 'O': []}

        while not engine.is_terminal():
            is_max = (turn == 'X')
            engine.nodes_visited = 0

            # Determinar config según turno
            if game_num % 2 == 1:
                active_cfg = ia_configs['IA1'] if turn == 'X' else ia_configs['IA2']
            else:
                active_cfg = ia_configs['IA2'] if turn == 'X' else ia_configs['IA1']

            algo = active_cfg.get('algo')
            depth = active_cfg.get('depth', 4)
            N = active_cfg.get('N', 500)
            C = active_cfg.get('C', math.sqrt(2))

            t0 = time.time()
            if algo == 'mcts':
                move = engine.mcts(N, C, turn)
            elif algo == 'alpha_beta':
                _, move = engine.alpha_beta(depth, -math.inf, math.inf, is_max)
            elapsed = time.time() - t0
            move_times[turn].append(elapsed)

            engine.make_move(move[0], move[1], turn)
            turn = 'O' if turn == 'X' else 'X'

        # Resultado
        if engine.is_winner('X'):
            winner = 'X'
        elif engine.is_winner('O'):
            winner = 'O'
        else:
            winner = 'draw'

        # Calcular tiempos promedio por jugada para esta partida
        avg_x = sum(move_times['X']) / len(move_times['X']) if move_times['X'] else 0
        avg_o = sum(move_times['O']) / len(move_times['O']) if move_times['O'] else 0

        if game_num % 2 == 1:
            # IA1=X, IA2=O
            times_ia1.append(avg_x)
            times_ia2.append(avg_o)
            if winner == 'X':
                ia1_wins += 1
            elif winner == 'O':
                ia2_wins += 1
            else:
                draws += 1
        else:
            # IA1=O, IA2=X
            times_ia1.append(avg_o)
            times_ia2.append(avg_x)
            if winner == 'O':
                ia1_wins += 1
            elif winner == 'X':
                ia2_wins += 1
            else:
                draws += 1

        result_str = f"IA1" if (winner == ia1_symbol) else ("IA2" if winner != 'draw' else "draw")
        print(f"  Partida {game_num:>2} | Ganó: {result_str:<4} | "
              f"t_IA1/jugada: {times_ia1[-1]:.4f}s | t_IA2/jugada: {times_ia2[-1]:.4f}s")

    avg_t1 = sum(times_ia1) / len(times_ia1) if times_ia1 else 0
    avg_t2 = sum(times_ia2) / len(times_ia2) if times_ia2 else 0

    print("\n" + "-"*60)
    print(f"  RESULTADOS FINALES ({n_games} partidas):")
    print(f"    IA-1 (MCTS)       wins: {ia1_wins}  |  t promedio/jugada: {avg_t1:.4f}s")
    print(f"    IA-2 (Alpha-Beta) wins: {ia2_wins}  |  t promedio/jugada: {avg_t2:.4f}s")
    print(f"    Empates:          {draws}")
    print("-"*60)

    inteligente = "IA-1 (MCTS)" if ia1_wins > ia2_wins else ("IA-2 (Alpha-Beta)" if ia2_wins > ia1_wins else "Empate")
    eficiente   = "IA-1 (MCTS)" if avg_t1 < avg_t2 else "IA-2 (Alpha-Beta)"
    print(f"\n  ► Más inteligente (más victorias): {inteligente}")
    print(f"  ► Más eficiente  (menos tiempo):   {eficiente}")
    print("="*60 + "\n")

    return ia1_wins, ia2_wins, draws, avg_t1, avg_t2


# ======================================================================
#  Punto de entrada
# ======================================================================

if __name__ == "__main__":
    print("\n  LAB 07 — BÚSQUEDA ADVERSARIA")
    print("  Tic-Tac-Toe: Minimax / Alpha-Beta / MCTS\n")

    # Sección 2a
    experiment_3x3()

    # Sección 2b
    experiment_4x4()

    # Sección 3
    ia_duel(n_games=20, board_size=4)

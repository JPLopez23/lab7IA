import math
import time
from tictactoe_engine import TicTacToeEngine


class GameLoop:
    """
    Parámetros del constructor:
      size          : 3 o 4
      mode          : "H-H" | "H-IA" | "IA-IA"
      starting_player: 'H' o 'IA'
      ia_configs    : dict con configuración de cada IA.
                      Ejemplo para un solo agente:
                        {'algo': 'alpha_beta', 'depth': 4, 'N': 500, 'C': sqrt(2)}
                      Ejemplo para IA-IA:
                        {
                          'IA1': {'algo': 'mcts',       'N': 500, 'C': sqrt(2)},
                          'IA2': {'algo': 'alpha_beta', 'depth': 4}
                        }
    """

    def __init__(self, size=3, mode="H-IA", starting_player='H', ia_configs=None):
        assert size in (3, 4)
        assert mode in ("H-H", "H-IA", "IA-IA")
        assert starting_player in ('H', 'IA')

        self.size = size
        self.mode = mode
        self.starting_player = starting_player

        # ia_configs por defecto
        if ia_configs is None:
            ia_configs = {'algo': 'alpha_beta', 'depth': 4, 'N': 500, 'C': math.sqrt(2)}
        self.ia_configs = ia_configs

        self.engine = TicTacToeEngine(size)
        # 'X' siempre es el primer jugador, 'O' el segundo
        self.turn = 'X'

    # ------------------------------------------------------------------ #
    #  Bucle principal                                                     #
    # ------------------------------------------------------------------ #

    def play(self):
        """Ejecuta una partida completa."""
        print(f"\n{'='*40}")
        print(f"  Tic-Tac-Toe {self.size}×{self.size} | Modo: {self.mode}")
        print(f"{'='*40}\n")
        self.engine.reset()
        self.engine.print_board()

        while not self.engine.is_terminal():
            print(f"\n  Turno de: {'X' if self.turn == 'X' else 'O'}")

            if self._is_human_turn():
                move = self._human_move()
            else:
                move = self._ia_move()

            if move:
                self.engine.make_move(move[0], move[1], self.turn)
                self.engine.print_board()
                self.turn = 'O' if self.turn == 'X' else 'X'

        self._print_result()

    def _is_human_turn(self):
        """Determina si el turno actual es humano."""
        if self.mode == "H-H":
            return True
        if self.mode == "IA-IA":
            return False
        # H-IA
        if self.starting_player == 'H':
            return self.turn == 'X'
        else:
            return self.turn == 'O'

    # ------------------------------------------------------------------ #
    #  Movimiento humano                                                   #
    # ------------------------------------------------------------------ #

    def _human_move(self):
        valid = self.engine.get_moves()
        while True:
            try:
                raw = input(f"  Ingresa tu movimiento (fila col, 0-indexed, máx {self.size-1}): ")
                r, c = map(int, raw.strip().split())
                if (r, c) in valid:
                    return (r, c)
                print("  Celda ocupada o fuera de rango.")
            except (ValueError, IndexError):
                print("  Formato inválido. Ejemplo: 1 2")

    # ------------------------------------------------------------------ #
    #  Movimiento IA                                                       #
    # ------------------------------------------------------------------ #

    def _ia_move(self):
        """Selecciona el algoritmo según ia_configs."""
        # Si hay dos IAs
        if self.mode == "IA-IA":
            if self.turn == 'X':
                cfg = self.ia_configs.get('IA1', self.ia_configs)
            else:
                cfg = self.ia_configs.get('IA2', self.ia_configs)
        else:
            cfg = self.ia_configs

        algo = cfg.get('algo', 'alpha_beta')
        depth = cfg.get('depth', 4)
        N = cfg.get('N', 500)
        C = cfg.get('C', math.sqrt(2))

        self.engine.nodes_visited = 0
        is_max = (self.turn == 'X')

        t0 = time.time()

        if algo == 'minimax_pure':
            _, move = self.engine.minimax_pure(is_max)
        elif algo == 'minimax_limit':
            _, move = self.engine.minimax_limit(depth, is_max)
        elif algo == 'alpha_beta':
            _, move = self.engine.alpha_beta(depth, -math.inf, math.inf, is_max)
        elif algo == 'mcts':
            move = self.engine.mcts(iterations=N, C=C, player=self.turn)
        else:
            raise ValueError(f"Algoritmo desconocido: {algo}")

        elapsed = time.time() - t0
        label = "IA1" if self.turn == 'X' else "IA2"
        print(f"  [{label} | {algo}] Movimiento: {move} | "
              f"Nodos: {self.engine.nodes_visited} | Tiempo: {elapsed:.4f}s")

        return move

    # ------------------------------------------------------------------ #
    #  Resultado                                                           #
    # ------------------------------------------------------------------ #

    def _print_result(self):
        print("\n" + "="*40)
        if self.engine.is_winner('X'):
            print("  Ganó: X")
        elif self.engine.is_winner('O'):
            print("  Ganó: O")
        else:
            print("  Empate")
        print("="*40 + "\n")

    def get_result(self):
        """Retorna 'X', 'O', o 'draw'."""
        if self.engine.is_winner('X'):
            return 'X'
        if self.engine.is_winner('O'):
            return 'O'
        return 'draw'

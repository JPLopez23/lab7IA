import math
import random
import time
from copy import deepcopy


class TicTacToeEngine:
    def __init__(self, size=3):
        assert size in (3, 4), "El tablero debe ser 3x3 o 4x4."
        self.size = size
        self.board = [[' '] * size for _ in range(size)]
        self.current_player = 'X'
        self.nodes_visited = 0 

    # ------------------------------------------------------------------ #
    #  Métodos de estado                                                   #
    # ------------------------------------------------------------------ #

    def is_empty(self, row, col):
        """Retorna True si la celda (row, col) está disponible."""
        return self.board[row][col] == ' '

    def get_moves(self):
        """Retorna lista de coordenadas (r, c) disponibles."""
        return [(r, c) for r in range(self.size) for c in range(self.size)
                if self.is_empty(r, c)]

    def make_move(self, row, col, player):
        """Realiza un movimiento. Retorna True si fue válido."""
        if self.is_empty(row, col):
            self.board[row][col] = player
            return True
        return False

    def undo_move(self, row, col):
        """Deshace un movimiento."""
        self.board[row][col] = ' '

    def is_winner(self, player):
        """Verifica si el jugador ha ganado."""
        n = self.size
        b = self.board
        # Filas
        for r in range(n):
            if all(b[r][c] == player for c in range(n)):
                return True
        # Columnas
        for c in range(n):
            if all(b[r][c] == player for r in range(n)):
                return True
        # Diagonal principal
        if all(b[i][i] == player for i in range(n)):
            return True
        # Diagonal inversa
        if all(b[i][n - 1 - i] == player for i in range(n)):
            return True
        return False

    def is_draw(self):
        """Retorna True si el tablero está lleno y no hay ganador."""
        return not self.get_moves() and not self.is_winner('X') and not self.is_winner('O')

    def is_terminal(self):
        """Retorna True si el juego terminó."""
        return self.is_winner('X') or self.is_winner('O') or not self.get_moves()

    # ------------------------------------------------------------------ #
    #  Función heurística                                                  #
    # ------------------------------------------------------------------ #

    def evaluate(self):
        """
        Heurística para tableros no terminados.
        Cuenta líneas que solo contienen piezas propias (sin bloqueo adversario).
        Devuelve un valor positivo si favorece a MAX ('X') y negativo si favorece a MIN ('O').
        """
        if self.is_winner('X'):
            return 1000
        if self.is_winner('O'):
            return -1000

        score = 0
        n = self.size

        def line_score(cells):
            xs = cells.count('X')
            os = cells.count('O')
            if xs > 0 and os > 0:
                return 0
            if xs > 0:
                return 10 ** (xs - 1)
            if os > 0:
                return -(10 ** (os - 1))
            return 0

        lines = []
        # Filas y columnas
        for i in range(n):
            lines.append([self.board[i][c] for c in range(n)])
            lines.append([self.board[r][i] for r in range(n)])
        # Diagonales
        lines.append([self.board[i][i] for i in range(n)])
        lines.append([self.board[i][n - 1 - i] for i in range(n)])

        for line in lines:
            score += line_score(line)

        return score

    # ------------------------------------------------------------------ #
    #  Minimax puro (solo 3×3)                                            #
    # ------------------------------------------------------------------ #

    def minimax_pure(self, is_maximizing=True):
        """
        Minimax exhaustivo. Solo recomendado para 3×3.
        Retorna (score, best_move).
        """
        self.nodes_visited += 1

        if self.is_winner('X'):
            return 10, None
        if self.is_winner('O'):
            return -10, None
        moves = self.get_moves()
        if not moves:
            return 0, None

        best_move = None

        if is_maximizing:
            best_score = -math.inf
            for (r, c) in moves:
                self.board[r][c] = 'X'
                score, _ = self.minimax_pure(False)
                self.board[r][c] = ' '
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
            return best_score, best_move
        else:
            best_score = math.inf
            for (r, c) in moves:
                self.board[r][c] = 'O'
                score, _ = self.minimax_pure(True)
                self.board[r][c] = ' '
                if score < best_score:
                    best_score = score
                    best_move = (r, c)
            return best_score, best_move

    # ------------------------------------------------------------------ #
    #  Minimax con horizonte limitado                                      #
    # ------------------------------------------------------------------ #

    def minimax_limit(self, depth, is_maximizing=True):
        """
        Minimax con horizonte fijo. Usa evaluate() al llegar al límite.
        Retorna (score, best_move).
        """
        self.nodes_visited += 1

        if self.is_winner('X'):
            return 1000, None
        if self.is_winner('O'):
            return -1000, None
        moves = self.get_moves()
        if not moves:
            return 0, None
        if depth == 0:
            return self.evaluate(), None

        best_move = None

        if is_maximizing:
            best_score = -math.inf
            for (r, c) in moves:
                self.board[r][c] = 'X'
                score, _ = self.minimax_limit(depth - 1, False)
                self.board[r][c] = ' '
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
            return best_score, best_move
        else:
            best_score = math.inf
            for (r, c) in moves:
                self.board[r][c] = 'O'
                score, _ = self.minimax_limit(depth - 1, True)
                self.board[r][c] = ' '
                if score < best_score:
                    best_score = score
                    best_move = (r, c)
            return best_score, best_move

    # ------------------------------------------------------------------ #
    #  Alpha-Beta Pruning                                                  #
    # ------------------------------------------------------------------ #

    def alpha_beta(self, depth, alpha, beta, is_maximizing=True):
        """
        Minimax con poda α-β.
        Retorna (score, best_move).
        """
        self.nodes_visited += 1

        if self.is_winner('X'):
            return 1000, None
        if self.is_winner('O'):
            return -1000, None
        moves = self.get_moves()
        if not moves:
            return 0, None
        if depth == 0:
            return self.evaluate(), None

        best_move = None

        if is_maximizing:
            best_score = -math.inf
            for (r, c) in moves:
                self.board[r][c] = 'X'
                score, _ = self.alpha_beta(depth - 1, alpha, beta, False)
                self.board[r][c] = ' '
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
                alpha = max(alpha, best_score)
                if alpha >= beta:
                    break  # poda β
            return best_score, best_move
        else:
            best_score = math.inf
            for (r, c) in moves:
                self.board[r][c] = 'O'
                score, _ = self.alpha_beta(depth - 1, alpha, beta, True)
                self.board[r][c] = ' '
                if score < best_score:
                    best_score = score
                    best_move = (r, c)
                beta = min(beta, best_score)
                if alpha >= beta:
                    break  # poda α
            return best_score, best_move

    # ------------------------------------------------------------------ #
    #  Monte Carlo Tree Search (MCTS)                                      #
    # ------------------------------------------------------------------ #

    def mcts(self, iterations=500, C=math.sqrt(2), player='X'):
        """
        Monte Carlo Tree Search con UCT.
        Retorna el mejor movimiento (r, c) para `player`.
        """
        root = MCTSNode(
            board=deepcopy(self.board),
            size=self.size,
            player=player
        )

        for _ in range(iterations):
            node = self._mcts_select(root, C)
            if not node.is_terminal():
                node = self._mcts_expand(node)
            result = self._mcts_simulate(node)
            self._mcts_backpropagate(node, result)

        best = max(root.children, key=lambda n: n.visits)
        return best.move

    def _mcts_select(self, node, C):
        """Selección: bajar por el árbol usando UCT hasta hoja o no expandido."""
        while node.children and not node.is_terminal():
            unvisited = [c for c in node.children if c.visits == 0]
            if unvisited:
                return random.choice(unvisited)
            node = max(node.children, key=lambda n: n.uct(C))
        return node

    def _mcts_expand(self, node):
        """Expansión: añadir todos los hijos del nodo si aún no se hizo."""
        if not node.children:
            moves = node.get_moves()
            for move in moves:
                child_board = deepcopy(node.board)
                child_board[move[0]][move[1]] = node.player
                child = MCTSNode(
                    board=child_board,
                    size=node.size,
                    player='O' if node.player == 'X' else 'X',
                    parent=node,
                    move=move
                )
                node.children.append(child)
            if node.children:
                return random.choice(node.children)
        return node

    def _mcts_simulate(self, node):
        """
        Simulación (rollout): jugar aleatoriamente hasta el final.
        Retorna 1 (X gana), -1 (O gana), 0 (empate).
        """
        board = deepcopy(node.board)
        current = node.player
        size = node.size

        def get_free():
            return [(r, c) for r in range(size) for c in range(size) if board[r][c] == ' ']

        def check_win(p):
            n = size
            for r in range(n):
                if all(board[r][c] == p for c in range(n)):
                    return True
            for c in range(n):
                if all(board[r][c] == p for r in range(n)):
                    return True
            if all(board[i][i] == p for i in range(n)):
                return True
            if all(board[i][n - 1 - i] == p for i in range(n)):
                return True
            return False

        while True:
            if check_win('X'):
                return 1
            if check_win('O'):
                return -1
            free = get_free()
            if not free:
                return 0
            r, c = random.choice(free)
            board[r][c] = current
            current = 'O' if current == 'X' else 'X'

    def _mcts_backpropagate(self, node, result):
        """Retropropagación: actualizar wins/visits subiendo al root."""
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent

    # ------------------------------------------------------------------ #
    #  Utilidades de visualización                                         #
    # ------------------------------------------------------------------ #

    def print_board(self):
        n = self.size
        sep = '+' + ('---+' * n)
        print(sep)
        for r in range(n):
            row_str = '|'
            for c in range(n):
                row_str += f' {self.board[r][c]} |'
            print(row_str)
            print(sep)

    def reset(self):
        self.board = [[' '] * self.size for _ in range(self.size)]
        self.current_player = 'X'
        self.nodes_visited = 0

    def clone(self):
        clone = TicTacToeEngine(self.size)
        clone.board = deepcopy(self.board)
        clone.current_player = self.current_player
        return clone


# ------------------------------------------------------------------ #
#  Nodo para MCTS                                                      #
# ------------------------------------------------------------------ #

class MCTSNode:
    def __init__(self, board, size, player, parent=None, move=None):
        self.board = board
        self.size = size
        self.player = player     
        self.parent = parent
        self.move = move          
        self.children = []
        self.visits = 0
        self.wins = 0.0

    def uct(self, C):
        if self.visits == 0:
            return math.inf
        exploitation = self.wins / self.visits
        exploration = C * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration

    def get_moves(self):
        return [(r, c) for r in range(self.size) for c in range(self.size)
                if self.board[r][c] == ' ']

    def is_terminal(self):
        n = self.size
        b = self.board

        def win(p):
            for r in range(n):
                if all(b[r][c] == p for c in range(n)):
                    return True
            for c in range(n):
                if all(b[r][c] == p for r in range(n)):
                    return True
            if all(b[i][i] == p for i in range(n)):
                return True
            if all(b[i][n - 1 - i] == p for i in range(n)):
                return True
            return False

        return win('X') or win('O') or not self.get_moves()

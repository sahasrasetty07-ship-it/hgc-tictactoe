"""
Tic-Tac-Toe state engine.
"""

import random

class TicTacToe:
    def __init__(self):
        # Initialize an empty 3x3 board ('', 'X', 'O')
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        
        # Cumulative score tracker (persists across play-again restarts)
        self.score = {'X': 0, 'O': 0}
        
        # Details of the winning path (e.g. ('row', 0), ('col', 1), ('diag', 0))
        self.winning_line = None

    def make_move(self, row, col):
        """
        Attempts to place the current player's mark at (row, col).
        Returns True if successful, False otherwise.
        """
        # Block moves if game is already over
        if self.game_over:
            return False

        if self.board[row][col] == '':
            self.board[row][col] = self.current_player
            
            # Run win-checking evaluation
            self.check_winner()
            
            # Switch turn only if game is still active
            if not self.game_over:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
            return True
        return False

    def check_winner(self):
        """
        Scans horizontal rows, vertical columns, and diagonals for a winning mark.
        Also handles board capacity checks for draws.
        """
        # 1. Scan Rows
        for r in range(3):
            if self.board[r][0] == self.board[r][1] == self.board[r][2] != '':
                self.winner = self.board[r][0]
                self.game_over = True
                self.winning_line = ('row', r)
                self.score[self.winner] += 1
                return

        # 2. Scan Columns
        for c in range(3):
            if self.board[0][c] == self.board[1][c] == self.board[2][c] != '':
                self.winner = self.board[0][c]
                self.game_over = True
                self.winning_line = ('col', c)
                self.score[self.winner] += 1
                return

        # 3. Scan Diagonals
        # Main diagonal (top-left to bottom-right)
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            self.winner = self.board[1][1]
            self.game_over = True
            self.winning_line = ('diag', 0)
            self.score[self.winner] += 1
            return
        # Anti-diagonal (top-right to bottom-left)
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            self.winner = self.board[1][1]
            self.game_over = True
            self.winning_line = ('diag', 1)
            self.score[self.winner] += 1
            return

        # 4. Scan for Draw (Board full and no winner)
        is_full = True
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == '':
                    is_full = False
                    break
        if is_full:
            self.winner = 'Draw'
            self.game_over = True
            self.winning_line = None

    def reset(self):
        """Resets the board grid for a new match, leaving scoreboard tallies intact."""
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        self.winning_line = None

    def get_ai_move(self, difficulty):
        """
        Determines the AI's move based on difficulty setting.
        Returns a tuple (row, col) of the chosen cell.
        """
        empty_cells = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == '']
        if not empty_cells:
            return None

        if difficulty == "Easy":
            return random.choice(empty_cells)
            
        elif difficulty == "Medium":
            # 70% optimal Minimax move, 30% random choice
            if random.random() < 0.70:
                return self._find_best_move()
            else:
                return random.choice(empty_cells)
                
        else: # "Hard" (Pure Minimax)
            return self._find_best_move()

    def _evaluate(self, board):
        """Helper to score board win states for O (+10) and X (-10)."""
        # Rows
        for r in range(3):
            if board[r][0] == board[r][1] == board[r][2] != '':
                return 10 if board[r][0] == 'O' else -10
        # Columns
        for c in range(3):
            if board[0][c] == board[1][c] == board[2][c] != '':
                return 10 if board[0][c] == 'O' else -10
        # Diagonals
        if board[0][0] == board[1][1] == board[2][2] != '':
            return 10 if board[1][1] == 'O' else -10
        if board[0][2] == board[1][1] == board[2][0] != '':
            return 10 if board[1][1] == 'O' else -10
        return 0

    def _is_moves_left(self, board):
        """Helper checking if board has vacant spaces."""
        for r in range(3):
            for c in range(3):
                if board[r][c] == '':
                    return True
        return False

    def _minimax_score(self, board, depth, is_max):
        """Recursive minimax scoring algorithm."""
        score = self._evaluate(board)
        
        # Return points, adjusting by depth to favor faster wins
        if score == 10:
            return score - depth
        if score == -10:
            return score + depth
        if not self._is_moves_left(board):
            return 0

        if is_max:
            best = -1000
            for r in range(3):
                for c in range(3):
                    if board[r][c] == '':
                        board[r][c] = 'O'
                        best = max(best, self._minimax_score(board, depth + 1, False))
                        board[r][c] = ''
            return best
        else:
            best = 1000
            for r in range(3):
                for c in range(3):
                    if board[r][c] == '':
                        board[r][c] = 'X'
                        best = min(best, self._minimax_score(board, depth + 1, True))
                        board[r][c] = ''
            return best

    def _find_best_move(self):
        """Finds the optimal minimax move for computer ('O')."""
        best_val = -1000
        best_move = (-1, -1)
        
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == '':
                    self.board[r][c] = 'O'
                    move_val = self._minimax_score(self.board, 0, False)
                    self.board[r][c] = ''
                    
                    if move_val > best_val:
                        best_val = move_val
                        best_move = (r, c)
                        
        # If no move was chosen (fallback), pick first available
        if best_move == (-1, -1):
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] == '':
                        return (r, c)
        return best_move

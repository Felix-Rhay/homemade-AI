import random

class TicTacToe:
    def __init__(self):
        self.board = [" "] * 9
        self.current_player = "X"

    def display(self):
        print()
        for i in range(0, 9, 3):
            print(f" {self.board[i]} | {self.board[i+1]} | {self.board[i+2]} ")
            if i < 6:
                print("---+---+---")
        print()

    def is_valid_move(self, position):
        return 0 <= position < 9 and self.board[position] == " "

    def play_move(self, position):
        if not self.is_valid_move(position):
            return False

        self.board[position] = self.current_player
        return True

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"

    def check_winner(self):
        win_conditions = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # lignes
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # colonnes
            (0, 4, 8), (2, 4, 6)              # diagonales
        ]

        for a, b, c in win_conditions:
            if self.board[a] == self.board[b] == self.board[c] != " ":
                return self.board[a]

        return None

    def is_draw(self):
        return " " not in self.board and self.check_winner() is None

    def is_game_over(self):
        return self.check_winner() is not None or self.is_draw()
    
def human_player_move(game):
    while True:
        try:
            pos = int(input(f"Joueur {game.current_player}, choisis une case (1-9): ")) -1
            if game.play_move(pos):
                break
            else:
                print("Coup invalide.")
        except ValueError:
            print("Entre un nombre valide.")



def available_moves(board):
    return [i for i, cell in enumerate(board) if cell == " "]

def main():
    game = TicTacToe()

    while not game.is_game_over():
        game.display()
        if game.current_player == "X":
            moves = available_moves(game.board)
            
        else:
            ai_move(game)

        if game.is_game_over():
            break

        game.switch_player()

    game.display()
    winner = game.check_winner()

    if winner:
        print(f"🎉 Le joueur {winner} a gagné!")
    else:
        print("🤝 Match nul!")


if __name__ == "__main__":
    main()

import random
from enum import IntEnum

class EtatCase(IntEnum):
    EXPLOSION = -5
    X         = -4
    BOMBE     = -3
    CACHEE    = -2
    DRAPEAU   = -1

class Game:
    def __init__(self, board:Board):
        self.board = board;
        self.game_ended = False
        self.bombs_left = board.n_bombs

    @staticmethod
    def demander_choix():
        choix = input("faire votre chois de case \"X,Y\": ")
        x,y = choix.split(",")
        action = input("choisir clic (l,r): ")
        return Choix(int(x)-1,int(y)-1, action)

    def reveal_board(self):
        for y in range(len(self.board.visible)):
            for x in range(len(self.board.visible[y])):
                if(self.board.visible[y][x] == EtatCase.DRAPEAU and self.board.hidden[y][x] != -1):#si un drapeau est mal placé
                    self.board.visible[y][x] = EtatCase.X
                elif self.board.visible == EtatCase.DRAPEAU and self.board.hidden[y][x] == -1:#si un drapeau est bien placé
                    self.board.visible[y][x] = EtatCase.DRAPEAU
                elif self.board.visible[y][x] == EtatCase.CACHEE and self.board.hidden[y][x] == -1:#si une case non révélée avait une bombe
                    self.board.visible[y][x] = EtatCase.BOMBE
                
    def appliquer_choix(self, choix:Choix):
        if choix.action == "r":
            if self.board.visible[choix.y][choix.x] == EtatCase.CACHEE:
                self.board.visible[choix.y][choix.x] = EtatCase.DRAPEAU
                self.bombs_left -= 1
            elif self.board.visible[choix.y][choix.x] == EtatCase.DRAPEAU:
                self.board.visible[choix.y][choix.x] = EtatCase.CACHEE
        else:
            if self.board.hidden[choix.y][choix.x] == -1: 
                self.reveal_board()
                self.board.visible[choix.y][choix.x] = -5
                self.game_ended = True
            elif self.board.visible[choix.y][choix.x] != EtatCase.CACHEE and self.board.compter_drapeaux(choix.x, choix.y) == self.board.visible[choix.y][choix.x]:
                self.board.reveal_adjacent(choix.x, choix.y)
            else:
                self.board.reveal_cells(choix.x, choix.y)

    def verify_win(self)->bool:
        if self.bombs_left <= 0:
            for y in range(len(self.board.visible)):
                for x in range(len(self.board.visible[y])):
                    if self.board.visible[y][x] == EtatCase.CACHEE: 
                        return False
            return self.bombs_left == 0
        return False
        

    @staticmethod
    def afficher_board(board:list[int]):
        print("      2       4       6       8")
        print("---------------------------------")
        for y in range(len(board)):
            for x in range(len(board[y])):
                if board[y][x] < 0:
                    if board[y][x] == EtatCase.CACHEE:
                        print("|   ", end="")
                    elif board[y][x] == EtatCase.DRAPEAU:
                        print(f"|🚩 ", end="")
                    elif board[y][x] == EtatCase.BOMBE:
                        print("|💣 ", end="")
                    elif board[y][x] == EtatCase.X:
                        print("|❌ ", end="")
                    elif board[y][x] == -5:
                        print("|💥 ", end="")
                else:
                    print(f"| {board[y][x]} ", end="")
            print(f"| {y+1}\n+---+---+---+---+---+---+---+---+")
class Board:
    def __init__(self, width, height, n_bombs):
        self.width = width
        self.height = height
        self.n_bombs = n_bombs
        self.visible = self.remplir_board(EtatCase.CACHEE)
        self.hidden = []
    
    def generate_board(self, safe_x, safe_y):
        self.hidden = self.remplir_board(0)

        forbidden = set()
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = safe_x + dx, safe_y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    forbidden.add((nx, ny))

        for _ in range(self.n_bombs):
            x, y = self.get_random_position(forbidden)
            self.hidden[y][x] = -1

        for y in range(self.width):
            for x in range(self.height):
                if self.hidden[y][x] >= 0:
                    self.hidden[y][x] = self.compter_bombes(x, y)
    
    def reveal_adjacent(self,x,y):
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                self.reveal_cells(dx+x,dy+y)

    def remplir_board(self, cell_value)->list[list[int]]:
        board:list[list[int]] = []
        for _ in range(self.height):
            board.append([cell_value]*self.width)
        return board
    
    def reveal_cells(self, x, y):
        # 1. hors limites
        if self.is_out_of_bounds(x, y):
            return

        # 2. drapeau ou déjà révélée
        if self.visible[y][x] != EtatCase.CACHEE:
            return

        # 3. bombe → on ne révèle jamais
        if self.hidden[y][x] == -1:
            return

        # 4. révéler la case
        self.visible[y][x] = self.hidden[y][x]

        # 5. si ce n'est pas un zéro, on s'arrête
        if self.hidden[y][x] != 0:
            return

        # 6. flood fill autour
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                self.reveal_cells(x + dx, y + dy)

    def is_out_of_bounds(self, nx, ny):
        return nx >= self.width or nx < 0 or ny >= self.height or ny < 0

    def compter_bombes(self, x, y):
        compte = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue  # on ignore la case centrale

                nx = x + dx
                ny = y + dy

                if 0 <= nx < self.width and 0 <= ny < self.height :
                    if self.hidden[ny][nx] == -1:
                        compte += 1

        return compte

    def compter_drapeaux(self, x, y):
        compte = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue  # on ignore la case centrale

                nx = x + dx
                ny = y + dy

                if 0 <= nx < self.width and 0 <= ny < self.height :
                    if self.visible[ny][nx] == -1:
                        compte += 1

        return compte
    
    def get_random_position(self, forbidden):
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

            if (x, y) in forbidden:
                continue
            if self.hidden[y][x] == 0:
                return x, y


class Choix:
    def __init__(self, x, y, action):
        self.x = x
        self.y = y
        self.action = action


        
def main():
    board = Board(8,8, 10)
    game = Game(board)
    #board = [[-1,0,-1,0,0,0,0,0],[0,0,0,0,0,0,0,0,],[0,0,0,0,0,0,0,0,],[0,0,0,0,0,0,0,0,],[0,0,0,0,0,0,0,0,],[ 0,0,0,0,0,0,0,0,],[0,0,0,0,0,0,0,0,],[0,0,0,0,0,0,0,0]]
    #game.board.visible = [row[:] for row in game.board.hidden]
    #game.board.visible[1][1] = -2
    game.afficher_board(game.board.visible)
    first_move_done = False

    while not game.game_ended:
        choix = game.demander_choix()
        if not first_move_done:
            game.board.generate_board(choix.x, choix.y)
            first_move_done = True
        game.appliquer_choix(choix)
        print(f"{game.bombs_left} bombes restantes")
        game.afficher_board(game.board.visible)
        if not game.game_ended: game.game_ended = game.verify_win()

    if game.verify_win() : 
        print("Vous avez gagné!")
    else:
        print(f"Vous avez perdu, il vous restait {game.bombs_left} bombes")

if __name__ == "__main__":
    main()
    

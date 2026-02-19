from minesweeper import minesweeper as ms
from datetime import datetime
from ai import neural_network as net, layer
import copy
import random

def adjust_weights(network, memory, reward):
    if not memory:
        return

    state, predicted, reward = memory[-1]
    error = reward - predicted
    network.backward([error])


def encode_case(val):
    if val == ms.EtatCase.CACHEE:
        return -1.0
    if val == ms.EtatCase.DRAPEAU:
        return -0.5
    if val >= 0:
        return float(val)
    return -2.0

def get_window_3x3(board:ms.Board, x, y):
    inputs = []

    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            nx = x + dx
            ny = y + dy

            if 0 <= nx < board.width and 0 <= ny < board.height:
                inputs.append(encode_case(board.visible[ny][nx]))
            else:
                inputs.append(-2.0)

    return inputs

def evaluer_toutes_les_cases(network, game:ms.Game):
    coups = []

    for y in range(game.board.height):
        for x in range(game.board.width):
            if game.board.visible[y][x] != ms.EtatCase.CACHEE:
                continue

            inputs = get_window_3x3(game.board, x, y)
            score = network.forward(inputs)[0]

            coups.append((score, x, y, inputs))

    return coups

def choisir_coup(network, game, epsilon=0.1):
    coups = evaluer_toutes_les_cases(network, game)

    if not coups:
        return None

    if random.random() < epsilon:
        score, x, y, inputs = random.choice(coups)
    else:
        score, x, y, inputs = max(coups, key=lambda c: c[0])

    return ms.Choix(x, y, "l"), inputs, score

def calculer_reward(game_avant: ms.Game, game_apres: ms.Game):
    # cas terminal PRIORITAIRE
    if game_apres.game_ended:
        if game_apres.verify_win():
            return +10.0
        else:
            return -10.0

    reward = 0.0

    for y in range(len(game_apres.board.visible)):
        for x in range(len(game_apres.board.visible[y])):
            before = game_avant.board.visible[y][x]
            after  = game_apres.board.visible[y][x]

            if before == after:
                continue

            # case révélée
            if after >= 0:
                reward += 0.2

            # explosion (normalement jamais ici car game_ended)
            elif after == ms.EtatCase.EXPLOSION:
                reward -= 5.0

            # drapeau posé
            elif after == ms.EtatCase.DRAPEAU:
                correct = game_apres.board.hidden[y][x] == -1
                reward += 0.5 if correct else -1.0

    if reward == 0:
        reward = -0.05

    return reward

def voisins(board, x, y):
    res = []
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < board.width and 0 <= ny < board.height:
                res.append((nx, ny))
    return res

def logique_sure(game: ms.Game):
    board = game.board

    coups_open = []
    coups_flag = []

    for y in range(board.height):
        for x in range(board.width):
            val = board.visible[y][x]

            if not isinstance(val, int) or val <= 0:
                continue

            v = voisins(board, x, y)
            caches = []
            drapeaux = 0

            for nx, ny in v:
                if board.visible[ny][nx] == ms.EtatCase.CACHEE:
                    caches.append((nx, ny))
                elif board.visible[ny][nx] == ms.EtatCase.DRAPEAU:
                    drapeaux += 1

            # RÈGLE A : poser drapeaux
            if val == len(caches) + drapeaux and caches:
                for c in caches:
                    coups_flag.append(ms.Choix(c[0], c[1], "r"))

            # RÈGLE B : ouvrir
            if val == drapeaux and caches:
                for c in caches:
                    coups_open.append(ms.Choix(c[0], c[1], "l"))

    return coups_open, coups_flag

def main(net_open, net_flag, iteration:int, epsilon=0.1, afficher=False, game_sans_apprentissage=[0]):
    game = ms.Game(ms.Board(8, 8, 10))
    memory_open = []
    memory_flag = []
    first_move_done = False

    while not game.game_ended:
        if not first_move_done:
            game.board.generate_board(0,0)
            first_move_done = True
            game.appliquer_choix(ms.Choix(0,0, "l"))
            if afficher:game.afficher_board(game.board.visible)
            continue

        coups_open, coups_flag = logique_sure(game)

        if coups_open:
            choix = coups_open[0]
            game.appliquer_choix(choix)
            n_coups[iteration] += 1
            game_sans_apprentissage[0] += 1
            if afficher:
                print(f"Choix: {choix.x+1},{choix.y+1},{choix.action}  reward=rien")
                game.afficher_board(game.board.visible)
            continue

        if coups_flag:
            choix = coups_flag[0]
            game.appliquer_choix(choix)
            n_coups[iteration] += 1
            game_sans_apprentissage[0] += 1
            if afficher:
                print(f"Choix: {choix.x+1},{choix.y+1},{choix.action}  reward=rien")
                game.afficher_board(game.board.visible)
            continue

        game_sans_apprentissage[1] += 1
        game_before = copy.deepcopy(game)
       
        result_open = choisir_coup(net_open, game, epsilon)
        result_flag = choisir_coup(net_flag, game, epsilon)
        if result_flag is None or result_open is None:
            break

        choix_open, inputs_open, score_open = result_open
        choix_flag, inputs_flag, score_flag = result_flag
        choix_flag.action = "r"

        #print(f"choix_open: {choix_open.x}, {choix_open.y}, score: {score_open}")
        #print(f"choix_flag: {choix_flag.x}, {choix_flag.y}, score: {score_flag}")

        if score_flag > score_open:
            if afficher: print("flag")
            choix = choix_flag
            inputs = inputs_flag    
            network = net_flag
            memory = memory_flag
            score = score_flag
        else: 
            choix = choix_open
            inputs = inputs_open
            network = net_open
            memory = memory_open
            score = score_open

        n_coups[iteration] += 1

        game.appliquer_choix(choix)

        reward = calculer_reward(game_before, game)

        # mémoire minimale (state + reward)
        memory.append((inputs, score, reward))

        adjust_weights(network, memory, reward)

        if afficher:
            print(f"Choix: {choix.x+1},{choix.y+1},{choix.action}  reward={reward}")
            game.afficher_board(game.board.visible)
            if game.verify_win(): print("Partie gagnée!")

        if not game.game_ended:
            game.game_ended = game.verify_win()
    
    return game.verify_win()

if __name__ == "__main__":
    game_sans_apprentissage = [0] * 2
    net_flag = net.Network()
    net_open = net.Network()
    try:
        net_open.load("minesweeper/net_open.json")
        net_flag.load("minesweeper/net_flag.json")
    except FileNotFoundError as e:
        print(e.filename, " n'existe pas")

    net_flag.add_layer(layer.Layer(9, 32, lr=0.001))
    net_flag.add_layer(layer.Layer(32, 32, lr=0.001))
    net_flag.add_layer(layer.Layer(32, 1, lr=0.001))

    net_open.add_layer(layer.Layer(9, 32, lr=0.001))
    net_open.add_layer(layer.Layer(32, 32, lr=0.001))
    net_open.add_layer(layer.Layer(32, 1, lr=0.001))

    wins = 0
    n_games = 1
    n_coups = [0] * n_games

    start = datetime.now()

    for i in range(n_games):
        win = main(net_open, net_flag, epsilon=0.2, afficher=True, iteration=i, game_sans_apprentissage=game_sans_apprentissage)
        if win:
            wins += 1

        if (i+1) % (n_games / 10) == 0:
            print(f"{i+1} parties – win rate: {wins/(i+1):.2%}", end="")
            print(f"  ({datetime.now() - start})")

    print(datetime.now() - start)
    print(f"nombre de parties gagnées: {wins}")
    print(f"nombre de coups moyen: {sum(n_coups)/len(n_coups)}")
    print(f"Coups sans apprentissage: {game_sans_apprentissage[0]}")
    print(f"Coups avec apprentissage: {game_sans_apprentissage[1]}")

    net_open.save("minesweeper/net_open.json")
    net_flag.save("minesweeper/net_flag.json")

from minesweeper import minesweeper as ms
from datetime import datetime
from ai import neural_network as net, layer
import copy

def compute_reward(game_before, game_after, choix):
    # 1. Perdre
    if game_after.game_ended and not game_after.verify_win():
        return -1.0

    # 2. Gagner
    if game_after.verify_win():
        return +1.0

    # 3. Ouvrir une case sûre
    if choix.action == "l":
        return +0.1

    # 4. Poser un drapeau, "/10"
    if choix.action == "r":
        return +0.05

    return 0.0


def flatten_with_pos(array):
    values:list[int] = []
    positions = []

    for i in range(len(array)):
        for j in range(len(array[i])):
            values.append(array[i][j])   # ex: 10
            positions.append((i, j))     # ex: (0,0)

    return values, positions


def calculer_outputs_possibles(flat_board: list[int], outputs: list, done_actions, bombs_left) -> list:
    retour = outputs.copy()

    for i, val in enumerate(flat_board):
        #premier coup
        if len(done_actions) <= 0:
            retour[i*2 + 1] = -1e9

        # 🚩 case avec drapeau
        elif val == ms.EtatCase.DRAPEAU:
            retour[i*2] = -1e9       # pas de clic gauche
            #retour[i*2 + 1] = -1e9   # pas de clic droit

        # 📖 case révélée
        elif val >= 0:
            retour[i*2 + 1] = -1e9   # pas de clic droit
            retour[i*2] = -1e9       #pas de clic gauche

        # ❓ case non révélée (-2)
        # tout est autorisé → rien à masquer
        elif bombs_left <= 0: 
            retour[i*2 + 1] = -1e9

    for a in done_actions:
        retour[a] = -1e9

    return retour


def ai_make_action(network:net.Network, game:ms.Game, memory)->ms.Choix:
    flat_board, positions = flatten_with_pos(game.board.visible)

    outputs = network.forward(flat_board)
    done_actions = [action for _, action in memory]
    possible_outputs = calculer_outputs_possibles(flat_board, outputs, done_actions, game.bombs_left)

    action_case = possible_outputs.index(max(possible_outputs))
    memory.append((flat_board.copy(), action_case))

    case = action_case//2
    action_type = action_case%2
    x,y = positions[case]
    action = "l" if action_type == 0 else "r"
    
    return ms.Choix(x,y,action)

def adjust_weights(network: net.Network, memory, reward):
    # sécurité
    if not memory:
        return

    # 👉 on ne prend QUE la dernière action
    state, action = memory[-1]

    # 1. forward
    outputs = network.forward(state)

    # 2. target = outputs actuels
    target = outputs.copy()
    target[action] = reward

    # 3. erreur (gradient de la loss MSE)
    errors = [
        target[i] - outputs[i]
        for i in range(len(outputs))
    ]

    # 4. backprop
    network.backward(errors)


def calculer_reward(game_avant: ms.Game, game_apres: ms.Game):
    reward = 0.0

    if game_apres.game_ended:
        if game_apres.verify_win():
            reward += 20
        #else: reward = 20.0

    for i in range(len(game_apres.board.visible)):
        for j in range(len(game_apres.board.visible[i])):
            before = game_avant.board.visible[i][j]
            after  = game_apres.board.visible[i][j]

            if before == after:
                continue

            if after == ms.EtatCase.EXPLOSION:
                reward -= 5
            elif after == ms.EtatCase.X:
                reward -= 2
            elif after == ms.EtatCase.DRAPEAU:
                if game_apres.board.hidden[i][j] == -1: reward += 8
                else:reward -= 2
            elif after >= 0:
                reward += 0.5

    return reward

def main(network:net.Network):
    game = ms.Game(ms.Board(8,8,10))
    memory = []
    reward = 0.0
    #game.afficher_board(game.board.visible)
    n_clics = 0
    first_move_done = False

    while not game.game_ended:
        game_before = copy.deepcopy(game)

        choix:ms.Choix = ai_make_action(network, game, memory)

        if not first_move_done:
            game.board.generate_board(choix.x, choix.y)
            first_move_done = True
            game.appliquer_choix(choix)
            continue

        if afficher: print(f"{choix.x+1}, {choix.y+1}, {choix.action}")

        game.appliquer_choix(choix)
        n_clics += 1

        reward = calculer_reward(game_before, game)
        adjust_weights(network, memory, reward)
        rewards.append(reward)

        if afficher: print(f"reward: {reward}")
        if afficher: print(f"{game.bombs_left} bombes restantes")
        if afficher: game.afficher_board(game.board.visible)

        if not game.game_ended: game.game_ended = game.verify_win()

    if game.verify_win() : 
        #reward += 10
        stats[0] += 1
        #print(f"Vous avez gagné!({n_clics} clics)")
    else:
        #reward -= 10
        stats[1] += 1
        #print(f"Vous avez perdu, il vous restait {game.bombs_left} bombes ({n_clics} clics)")
    if afficher: print(f"reward: {reward}")
    #adjust_weights(network, memory, reward)
    
    
stats = [0,0]
rewards = []
afficher = False

if __name__ == "__main__":

    network = net.Network()
    try:
        network.load("minesweeper/ai_corrige.json")
    except FileNotFoundError as e:
        print(e.filename, " n'existe pas")

    network.add_layer(layer.Layer(64, 128, lr=0.005))
    network.add_layer(layer.Layer(128, 128, lr=0.005))
    network.add_layer(layer.Layer(128, 128, lr=0.005))  # output

    
    start = datetime.now()

    n_epochs = 1000
    # entraîne sur plusieurs parties
    for i in range(n_epochs):
        main(network)
        if n_epochs>= 100 and i%(n_epochs//10) == 0: print(i//(n_epochs//10), "/10 (", datetime.now()-start, ")")
    
    print(datetime.now() - start)
    
    network.save("minesweeper/ai_corrige.json")
    #network.save("minesweeper/ai_test.json")
    #network.save("minesweeper/ai1.json")
    #network.save("minesweeper/ai2.json")

    print("Entraînement terminé")
    print(f"{stats[0]} wins; {stats[1]} losses; {stats[0]/(stats[0]+stats[1])*100}% win")
    print("average reward: ", sum(rewards) / len(rewards))
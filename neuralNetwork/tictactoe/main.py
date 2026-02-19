import random
from ai import neural_network as net, layer
from . import tic_tac_toe as g 
from datetime import datetime
 
stats = [0] * 3

def transformToAiBoard(board):
    aiBoard = []
    for cell in board:
        if cell == " ":
            aiBoard.append(0)
        elif cell == "X":
            aiBoard.append(1)
        elif cell == "O":
            aiBoard.append(-1)
    return aiBoard


def transformToEnemyAiBoard(board):
    aiBoard = []
    for cell in board:
        if cell == " ":
            aiBoard.append(0)
        elif cell == "X":
            aiBoard.append(-1)
        elif cell == "O":
            aiBoard.append(1)
    return aiBoard

def calculerOutputsPossibles(outputs, moves):
    retour = outputs.copy()
    for i in range(len(retour)):
        if i not in moves:
            retour[i] = -1e9  # interdit vraiment le coup
    return retour

def dummy_move(game:g.TicTacToe):
    # exemple ultra simple : premier coup disponible
    choix = random.randint(0, 8)
    if game.board[choix] == " ":
        game.play_move(choix)
    else:
        dummy_move(game)

def ai_move(network, game:g.TicTacToe, memory, useMemory:bool=True):
    moves = g.available_moves(game.board)
    aiBoard = []
    if game.current_player == "X":
        aiBoard = transformToAiBoard(game.board)
    else:
        aiBoard = transformToEnemyAiBoard(game.board)

    outputs = network.forward(aiBoard)
    possible_outputs = calculerOutputsPossibles(outputs, moves)
           
    action = possible_outputs.index(max(possible_outputs))

    if useMemory: memory.append((aiBoard.copy(), action))
    game.play_move(action)

def adjust_weights(network, memory, reward):
    for state, action in memory:
        outputs = network.forward(state)
        errors = [0.0] * 9
        errors[action] = reward - outputs[action]
        network.backward(errors)

def main(network:net.Network, enemy_network:net.Network):
    game = g.TicTacToe()
    
    memory = []  # mémorise les coups de X  
    enemy_memory = []

    while not game.is_game_over():
        #game.display()  # optionnel, enlève pour entraîner plus vite

        if game.current_player == "X":
            #ai_move(network, game, memory)
            dummy_move(game)
        else:
            #game.display()
            #g.human_player_move(game)
            ai_move(enemy_network, game, enemy_memory)

        if game.is_game_over():
            #game.display()

            break

        game.switch_player()

    # game.display()
    winner = game.check_winner()

    if winner == "X":
        reward = 1.0
        enemy_reward = -1.0
        stats[0] += 1
        # print("🎉 X gagne")
    elif winner == "O":
        reward = -1.0
        enemy_reward = 1.0
        stats[1] += 1
        # print("❌ X perd")
    else:
        reward = 0.0
        enemy_reward = 0.0
        stats[2] += 1
        # print("🤝 Match nul")
    
    # 🔥 APPRENTISSAGE 🔥
    adjust_weights(network, memory, reward)

    adjust_weights(enemy_network, enemy_memory, enemy_reward)


if __name__ == "__main__":
    network = net.Network()

    network.add_layer(layer.Layer(input_size=9, neuron_count=32, lr=0.1))
    network.add_layer(layer.Layer(input_size=32, neuron_count=9, lr=0.1))

    #network.load("tictactoe/ai1.json")

    enemy_network = net.Network()
    enemy_network.add_layer(layer.Layer(input_size=9, neuron_count=32, lr=0.1))
    enemy_network.add_layer(layer.Layer(input_size=32, neuron_count=9, lr=0.1))
    enemy_network.load("tictactoe/ai2.json")
    
    start = datetime.now()
    # entraîne sur plusieurs parties
    for i in range(1000000):
        main(network, enemy_network)
        #print("Entrainement terminé ---------------------------")
    
    print(datetime.now() - start)
    #network.save("tictactoe/ai1.json")
    enemy_network.save("tictactoe/ai2.json")

    print("Entraînement terminé")
    print(f"{stats[0]} wins ; {stats[1]} losses ; {stats[2]} ties")
    print(f"{stats[0]/(stats[0]+stats[1]+stats[2])*100} % win")
    print(f"{stats[1]/(stats[0]+stats[1]+stats[2])*100} % losses")
    print(f"{stats[2]/(stats[0]+stats[1]+stats[2])*100} % ties")
import math

board = [' ' for _ in range(9)]

def print_board():
    for row in [board[i*3:(i+1)*3] for i in range(3)]:
        print('| ' + ' | '.join(row) + ' |')

def check_winner(b, p):
    win_states = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
    return any(all(b[i] == p for i in state) for state in win_states)

def get_empty_cells(state):
    return [i for i, cell in enumerate(state) if cell == ' ']

def minimax(state, depth, is_maximizing):
    if check_winner(state, 'O'): return 10 - depth
    if check_winner(state, 'X'): return depth - 10
    if ' ' not in state: return 0

    if is_maximizing:
        best_score = -math.inf
        for move in get_empty_cells(state):
            state[move] = 'O'
            score = minimax(state, depth + 1, False)
            state[move] = ' '
            best_score = max(score, best_score)
        return best_score
    else:
        best_score = math.inf
        for move in get_empty_cells(state):
            state[move] = 'X'
            score = minimax(state, depth + 1, True)
            state[move] = ' '
            best_score = min(score, best_score)
        return best_score

def ai_move():
    best_score = -math.inf
    move = -1
    for i in get_empty_cells(board):
        board[i] = 'O'
        score = minimax(board, 0, False)
        board[i] = ' '
        if score > best_score:
            best_score = score
            move = i
    board[move] = 'O'

# Simple Game Loop
print("Tic-Tac-Toe: You (X) vs AI (O)")
while ' ' in board:
    print_board()
    human_move = int(input("Enter move (0-8): "))
    if board[human_move] != ' ': continue
    board[human_move] = 'X'
    
    if check_winner(board, 'X'):
        print_board(); print("You win!"); break
    if ' ' not in board: break
    
    ai_move()
    if check_winner(board, 'O'):
        print_board(); print("AI wins!"); break

if not check_winner(board, 'X') and not check_winner(board, 'O'):
    print_board(); print("It's a draw!")
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

def is_winner(board, player):
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]  # Diagonals
    ]
    return any(all(board[i] == player for i in combo) for combo in winning_combinations)

def is_board_full(board):
    return ' ' not in board

def get_empty_squares(board):
    return [i for i, x in enumerate(board) if x == ' ']

def is_possible_win(board):
    # Check if there's any possible way to win for either player
    empty_positions = get_empty_squares(board)
    
    # Try each empty position for both X and O
    for pos in empty_positions:
        # Try X
        board[pos] = 'X'
        if is_winner(board, 'X'):
            board[pos] = ' '
            return True
        
        # Try O
        board[pos] = 'O'
        if is_winner(board, 'O'):
            board[pos] = ' '
            return True
            
        board[pos] = ' '
    
    return False

def minimax(board, depth, is_maximizing):
    if is_winner(board, 'O'):
        return 1
    if is_winner(board, 'X'):
        return -1
    if is_board_full(board):
        return 0
    
    if is_maximizing:
        best_score = float('-inf')
        for move in get_empty_squares(board):
            board[move] = 'O'
            score = minimax(board, depth + 1, False)
            board[move] = ' '
            best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for move in get_empty_squares(board):
            board[move] = 'X'
            score = minimax(board, depth + 1, True)
            board[move] = ' '
            best_score = min(score, best_score)
        return best_score

def get_best_move(board):
    best_score = float('-inf')
    best_move = None
    
    for move in get_empty_squares(board):
        board[move] = 'O'
        score = minimax(board, 0, False)
        board[move] = ' '
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/make_move', methods=['POST'])
def make_move():
    data = request.get_json()
    board = data['board']
    
    # Check if game is already won
    if is_winner(board, 'X'):
        return jsonify({
            'board': board,
            'status': 'player_wins'
        })
    
    # Check if it's already a draw (no possible wins)
    if not is_possible_win(board):
        return jsonify({
            'board': board,
            'status': 'draw'
        })
    
    # Make computer's move
    computer_move = get_best_move(board)
    if computer_move is not None:
        board[computer_move] = 'O'
    
    # Check game status after computer's move
    status = 'ongoing'
    if is_winner(board, 'O'):
        status = 'computer_wins'
    elif not is_possible_win(board):
        status = 'draw'
    
    return jsonify({
        'board': board,
        'status': status,
        'computer_move': computer_move
    })

@app.route('/get_hint', methods=['POST'])
def get_hint():
    data = request.get_json()
    board = data['board']
    
    # Get best move for player (X)
    best_score = float('-inf')
    best_move = None
    
    for move in get_empty_squares(board):
        board[move] = 'X'
        score = minimax(board, 0, True)  # True because next move would be O's turn
        board[move] = ' '
        if score > best_score:
            best_score = score
            best_move = move
    
    return jsonify({
        'recommended_move': best_move
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

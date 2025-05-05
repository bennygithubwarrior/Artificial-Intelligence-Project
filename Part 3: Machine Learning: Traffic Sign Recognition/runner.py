import time  # to pause during replay
from tictactoe import (
    initial_state, player, actions, result,
    winner, terminal, ai_move, X, O, EMPTY
)

def print_board(board):
    """Display the board in the terminal."""
    sym = {X: "X", O: "O", EMPTY: " "}
    for row in board:
        print(" " + " | ".join(sym[cell] for cell in row))
    print()

def choose(prompt, options):
    """Prompt until user picks one of the given options."""
    opt = "/".join(options)
    while True:
        ans = input(f"{prompt} ({opt}): ").strip().lower()
        if ans in options:
            return ans
        print(f"Invalid choice – please enter one of: {opt}")

def human_move(board):
    """Ask human for a row,col move and validate it."""
    moves = actions(board)
    while True:
        inp = input(
            "Your move – type row,col (e.g. 1,2 for middle-right).\n"
            " Rows: 0=top,1=middle,2=bottom; Cols: 0=left,1=center,2=right.\n> "
        ).strip()
        try:
            i, j = map(int, inp.split(","))
            if (i, j) in moves:
                return (i, j)
        except:
            pass
        print("Invalid move – pick two numbers 0–2, comma-separated, on an empty cell.")

def replay(moves):
    """Replay all moves in sequence with a short delay."""
    print("\nReplaying the game:")
    b = initial_state()
    for idx, mv in enumerate(moves, 1):
        time.sleep(0.8)
        b = result(b, mv)
        print(f"Move {idx}: {mv}")
        print_board(b)

def main():
    """Main loop: set up game mode, play until terminal, then offer replay."""
    print("\n=== Welcome to Tic-Tac-Toe ===")
    print("This is a 3×3 grid game. Get three in a row to win.")
    print()

    while True:
        # Choose human vs AI or AI vs AI
        mode = choose(
            "Choose game mode: 1 = You vs Computer, 2 = Computer vs Computer",
            ["1", "2"]
        )

        if mode == "1":
            # Human picks symbol and AI difficulty
            user_sym = choose("Which symbol do you want? X goes first, O goes second", ["x", "o"]).upper()
            ai_diff = choose("Select computer strength", ["easy", "medium", "hard"])
        else:
            # Set difficulty for both AIs
            user_sym = None
            ai_diff = {
                X: choose("Select strength for computer X", ["easy", "medium", "hard"]),
                O: choose("Select strength for computer O", ["easy", "medium", "hard"])
            }

        moves = []
        state = initial_state()

        # Play until game over
        while not terminal(state):
            print_board(state)
            cur = player(state)

            if mode == "1" and cur == user_sym:
                mv = human_move(state)
            else:
                print(f"Computer ({cur}) is thinking...", end="", flush=True)
                diff = ai_diff if mode == "1" else ai_diff[cur]
                mv = ai_move(state, diff)
                print(f" chooses {mv}")

            state = result(state, mv)
            moves.append(mv)

        # Show final board and result
        print_board(state)
        w = winner(state)
        if w:
            if mode == "1":
                if w == user_sym:
                    print("🎉 Congratulations! You beat the computer! 🎉")
                else:
                    print("😞 The computer wins. Better luck next time. 😞")
            else:
                print(f"🤖 Game over: computer {w} wins! 🤖")
        else:
            print("🤝 It's a tie! Well played! 🤝")

        # Offer replay
        if choose("Would you like to see a replay? yes/no", ["yes", "no"]) == "yes":
            replay(moves)

        # Play again?
        if choose("Do you want to play again? yes/no", ["yes", "no"]) == "no":
            print("Thanks for playing! Hope you enjoyed it. Goodbye! 👋")
            break
        print()

if __name__ == "__main__":
    main()

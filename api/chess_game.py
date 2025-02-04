# chess_game.py
import os
import chess
import chess.engine
import tkinter as tk
from tkinter import font, messagebox
import random
from anthropic import Anthropic
from tkfontchooser import askfont
import utilities  # Ensure this module is bundled

class ChessGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Chess Game")
        
        # Get the default background color
        default_bg = self.window.cget('bg')
        
        # Create the fonts first
        self.window.tk.call('font', 'create', 'ElectraLTStd')
        self.window.tk.call('font', 'create', 'ElectraLTStdLarge')
        
        # Now configure them
        self.window.tk.call('font', 'configure', 'ElectraLTStd', '-family', 'Electra LT Std', '-size', 13)
        self.window.tk.call('font', 'configure', 'ElectraLTStdLarge', '-family', 'Electra LT Std', '-size', 18)
        
        # Create italic version of the font
        self.window.tk.call('font', 'create', 'ElectraLTStdItalic')
        self.window.tk.call('font', 'configure', 'ElectraLTStdItalic', 
                           '-family', 'Electra LT Std',
                           '-size', 18,
                           '-slant', 'italic')
        
        # Create larger font for chess pieces
        self.window.tk.call('font', 'create', 'ElectraLTStdPieces')
        self.window.tk.call('font', 'configure', 'ElectraLTStdPieces', 
                           '-family', 'Electra LT Std',
                           '-size', 27)
        
        # Define font references
        self.electra_font = 'ElectraLTStd'
        self.electra_font_large = 'ElectraLTStdLarge'
        
        # Initialize Anthropic client with API key
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("Warning: ANTHROPIC_API_KEY environment variable not set. Hints will not be available.")
            self.anthropic = None
        else:
            self.anthropic = Anthropic(api_key=api_key)
        
        # Set minimum window size
        self.window.geometry("1200x900")
        self.window.minsize(1200, 600)
        
        # Create main frame with padding and center it
        self.main_frame = tk.Frame(self.window, bg=default_bg)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create game area frame to hold board and message box
        self.game_area = tk.Frame(self.main_frame, bg=default_bg)
        self.game_area.pack(expand=True, fill='both')
        
        self.board = chess.Board()
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        self.selected_square = None
        self.difficulty = "easy"
        
        # Initialize chess engine
        try:
            # Try different common Stockfish paths
            stockfish_paths = [
                "/opt/homebrew/bin/stockfish",  # Mac ARM (Apple Silicon)
                "/usr/local/bin/stockfish",    # Mac Intel
                "stockfish"                    # System PATH
            ]
            
            for path in stockfish_paths:
                try:
                    self.engine = chess.engine.SimpleEngine.popen_uci(path)
                    break
                except FileNotFoundError:
                    continue
            else:
                raise FileNotFoundError("Could not find Stockfish in any standard location")
            self.engine.configure({"Skill Level": 3})  # Start with easy mode
        except Exception as e:
            print(f"Error initializing chess engine: {e}"
                  "\nPlease install Stockfish with: brew install stockfish")
            self.engine = None
        self.player_color = chess.WHITE
        
        # Create board frame
        board_container = tk.Frame(self.game_area)
        board_container.pack(side=tk.LEFT, expand=True)
        
        # Add instruction text above board
        instruction_frame = tk.Frame(board_container, bg=default_bg)
        instruction_frame.pack(pady=(40,20))
        instruction_label = tk.Label(instruction_frame,
                                   text="Solve the riddle on the right to reveal your best move.",
                                   font='ElectraLTStdItalic',
                                   bg=default_bg)
        instruction_label.pack()
        
        self.board_frame = tk.Frame(board_container)
        self.board_frame.pack(pady=(20,0))
        
        # Create message frame on the right with increased width
        self.message_frame = tk.Frame(self.game_area, width=400, bg=default_bg)
        self.message_frame.pack(side=tk.RIGHT, fill='both', padx=20, pady=20)
        self.message_frame.pack_propagate(False)
        
        # Create a container for the hint section
        hint_container = tk.Frame(self.message_frame, bg=default_bg)
        hint_container.pack(fill='both', expand=True)
        
        # Create title label
        tk.Label(hint_container, text="Hint:", font=self.electra_font_large, bg=default_bg).pack(anchor='center', padx=5, pady=(0, 5))
        
        # Create text widget for hint with scrollbar
        self.hint_text = tk.Text(hint_container, 
                               font=self.electra_font_large,
                               wrap=tk.WORD,
                               height=1,
                               width=40,  # Increased width for smaller font
                               borderwidth=0,
                               highlightthickness=0,
                               bg=default_bg)
        self.hint_text.pack(fill='both', expand=True, padx=5)
        
        # Make text widget read-only
        self.hint_text.config(state=tk.DISABLED)
        
        # Create a frame for the new game button at the bottom of message_frame
        button_frame = tk.Frame(self.message_frame, bg=default_bg)
        button_frame.pack(side=tk.BOTTOM, pady=(0, 80))
        
        # Create new game button
        self.new_game_button = tk.Label(button_frame, 
                                      text="New Game", 
                                      font=self.electra_font_large,
                                      bg=default_bg,
                                      cursor="hand2")
        self.new_game_button.pack()
        self.new_game_button.bind("<Button-1>", lambda e: self.new_game())
        
        # Create controls frame below the board
        self.controls_frame = tk.Frame(board_container, bg=default_bg)
        self.controls_frame.pack(pady=20)
        
        # Create difficulty selection
        self.create_difficulty_selector()
        
        self.window.resizable(True, True)
        
    def create_difficulty_selector(self):
        controls_container = tk.Frame(self.controls_frame, bg=self.window.cget('bg'))
        controls_container.pack()
        
        tk.Label(controls_container, 
                text="Difficulty:", 
                font=self.electra_font_large,
                bg=self.window.cget('bg')).pack(side=tk.LEFT, padx=10)
        
        difficulties = ["Easy", "Medium", "Hard"]
        self.difficulty_var = tk.StringVar(value="Easy")
        
        for diff in difficulties:
            tk.Radiobutton(controls_container, 
                          text=diff, 
                          variable=self.difficulty_var,
                          value=diff, 
                          command=self.change_difficulty,
                          font=self.electra_font_large,
                          bg=self.window.cget('bg')).pack(side=tk.LEFT, padx=10)

    def create_board(self):
        square_size = 80  # Slightly larger square size
        
        # Configure board frame to be larger
        self.board_frame.configure(width=square_size * 8, height=square_size * 8)
        self.board_frame.grid_propagate(False)  # Prevent frame from shrinking
        
        for i in range(8):
            self.board_frame.grid_rowconfigure(i, weight=1)
            self.board_frame.grid_columnconfigure(i, weight=1)
        
        for row in range(8):
            for col in range(8):
                i = 7 - row
                color = "white" if (i + col) % 2 == 0 else "gray"
                button = tk.Button(self.board_frame, 
                                 bg=color,
                                 width=4,
                                 height=2,
                                 font=self.electra_font_large)
                button.grid(row=row, column=col, sticky="nsew")
                self.buttons[row][col] = button
                button.configure(command=lambda r=row, c=col: self.square_clicked(r, c))
        
        self.update_board_display()

    def change_difficulty(self):
        self.difficulty = self.difficulty_var.get().lower()
        if self.engine:
            # Adjust engine skill level based on difficulty
            if self.difficulty == "easy":
                self.engine.configure({"Skill Level": 3})
            elif self.difficulty == "medium":
                self.engine.configure({"Skill Level": 10})
            else:  # hard
                self.engine.configure({"Skill Level": 20})

    def square_clicked(self, row, col):
        board_row = 7 - row
        board_square = board_row * 8 + col
        
        if self.selected_square is None:
            piece = self.board.piece_at(board_square)
            if piece and piece.color == self.player_color:
                self.selected_square = board_square
                self.buttons[row][col].config(bg='lightblue')
        else:
            move = chess.Move(self.selected_square, board_square)
            
            prev_square = self.selected_square
            prev_row = 7 - (prev_square // 8)
            prev_col = prev_square % 8
            self.buttons[prev_row][prev_col].config(bg='white' if (prev_row + prev_col) % 2 == 0 else 'gray')
            self.selected_square = None
            
            if move in self.board.legal_moves:
                self.board.push(move)
                self.update_board_display()
                
                if self.board.is_game_over():
                    self.show_game_over()
                else:
                    self.make_ai_move()

    def make_ai_move(self):
        if self.board.is_game_over() or not self.engine:
            return
            
        try:
            # Configure engine based on difficulty
            if self.difficulty == "easy":
                self.engine.configure({"Skill Level": 3})
                time_limit = 0.1
            elif self.difficulty == "medium":
                self.engine.configure({"Skill Level": 10})
                time_limit = 0.3
            else:  # hard
                self.engine.configure({"Skill Level": 20})
                time_limit = 0.5
            
            # Get engine's best move
            result = self.engine.play(self.board, 
                                    chess.engine.Limit(time=time_limit),
                                    info=chess.engine.INFO_ALL)
            self.board.push(result.move)
            self.update_board_display()
            
            if self.board.is_game_over():
                self.show_game_over()
            else:
                # After AI moves, analyze the position and generate a hint for the player's best move
                self.window.after(200, self.generate_player_hint)
        except Exception as e:
            print(f"Error making AI move: {e}")

    def generate_player_hint(self):
        if not self.anthropic:
            return
            
        try:
            # Analyze current position for best player moves
            legal_moves = list(self.board.legal_moves)
            if not legal_moves:
                return
                
            # Select a strong move for the player (in a real implementation, 
            # you might want to use a chess engine here)
            suggested_move = random.choice(legal_moves)
            
            # Get the piece making the suggested move
            piece = self.board.piece_at(suggested_move.from_square)
            if not piece:
                return
                
            piece_type = chess.piece_name(piece.piece_type).capitalize()
            from_square = chess.square_name(suggested_move.from_square)
            to_square = chess.square_name(suggested_move.to_square)
            
            # Get the target square's piece (if any)
            target_piece = self.board.piece_at(suggested_move.to_square)
            is_capture = target_piece is not None
            
            # Analyze the position
            is_check = self.board.is_check()
            attacked_squares = [chess.square_name(sq) for sq in chess.SQUARES 
                              if self.board.is_attacked_by(not self.board.turn, sq)]
            defended_squares = [chess.square_name(sq) for sq in chess.SQUARES 
                              if self.board.is_attacked_by(self.board.turn, sq)]
            
            # Get all pieces positions for more complex riddles
            all_pieces = []
            for sq in chess.SQUARES:
                p = self.board.piece_at(sq)
                if p:
                    all_pieces.append((chess.square_name(sq), chess.piece_name(p.piece_type), p.color))

            # Get potential tactical themes
            is_pin = any(self.board.is_pinned(self.board.turn, sq) for sq in chess.SQUARES)
            material_count = sum(len(self.board.pieces(piece_type, True)) for piece_type in chess.PIECE_TYPES)
            is_endgame = material_count <= 10
            
            difficulty_prompts = {
                "easy": f"Create a chess riddle about a critical {piece_type} move. Reference the current position with {piece_type} on {from_square} and potential destination {to_square}. Include these tactical elements: capture={is_capture}, check={is_check}. Make it challenging but solvable.",
                
                "medium": f"Create a sophisticated chess riddle involving a {piece_type} on {from_square}. Include these positional elements: attacked squares={attacked_squares[:3]}, defended squares={defended_squares[:3]}, pins present={is_pin}. The solution involves square {to_square}. Use chess terminology and make it require deep tactical understanding.",
                
                "hard": f"Create an expert-level chess riddle about a critical {piece_type} move from {from_square}. Consider these elements: captures={is_capture}, checks={is_check}, pins={is_pin}, phase={('endgame' if is_endgame else 'middlegame')}, piece positions={all_pieces[:5]}. The key square is {to_square}. Create a multi-layered puzzle that requires understanding of positional chess, tactical patterns, and strategic planning. Include multiple red herrings and intermediate objectives before revealing the final solution. Reference concrete squares and pieces in the position."
            }
            
            prompt = difficulty_prompts[self.difficulty.lower()]
            
            message = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=300,
                temperature=0.9,
                system="You are a friendly chess riddle composer who creates engaging and clear chess puzzles. Your riddles use chess terminology and tactical themes while remaining concise and approachable. Create riddles that hint at the key moves using simple metaphors and clear references to the position. Keep the riddles focused on one main tactical idea, using 2-3 lines of text. Use chess terminology naturally but avoid making the riddles overly complex. Your riddles should be fun and solvable for players of all skill levels. Only output the riddle text.",
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            hint = message.content[0].text.strip()
            self.hint_text.config(state=tk.NORMAL)
            self.hint_text.delete(1.0, tk.END)
            self.hint_text.insert(tk.END, hint)
            self.hint_text.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error generating hint: {e}")

    def update_board_display(self):
        piece_symbols = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
        }
        
        for row in range(8):
            for col in range(8):
                square = (7 - row) * 8 + col
                piece = self.board.piece_at(square)
                text = piece_symbols.get(str(piece), ' ') if piece else ' '
                self.buttons[row][col].config(
                    text=text,
                    font='ElectraLTStdPieces',
                    bg="white" if ((7 - row) + col) % 2 == 0 else "gray"
                )

    def new_game(self):
        self.board.reset()
        self.selected_square = None
        self.player_color = chess.WHITE
        for row in range(8):
            for col in range(8):
                color = "white" if ((7 - row) + col) % 2 == 0 else "gray"
                self.buttons[row][col].config(bg=color)
        self.update_board_display()
        self.hint_text.config(state=tk.NORMAL)
        self.hint_text.delete(1.0, tk.END)
        self.hint_text.config(state=tk.DISABLED)
        self.hint_text.config(height=1)

    def show_game_over(self):
        result = "Draw"
        if self.board.is_checkmate():
            result = "Black wins!" if self.board.turn == chess.WHITE else "White wins!"
        elif self.board.is_stalemate():
            result = "Stalemate!"
        
        messagebox.showinfo("Game Over", result, font=self.electra_font)

    def run(self):
        self.create_board()
        try:
            self.window.mainloop()
        finally:
            # Clean up chess engine when the window is closed
            if hasattr(self, 'engine') and self.engine:
                self.engine.quit()

if __name__ == "__main__":
    from welcome_screen import WelcomeScreen
    welcome = WelcomeScreen()
    welcome.run()

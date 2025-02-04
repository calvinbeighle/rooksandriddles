# tests/test_chess_game.py
import unittest
import chess
import tkinter as tk
from unittest.mock import MagicMock, patch
from chess_game import ChessGame

class TestChessGame(unittest.TestCase):
    def setUp(self):
        # Instantiate ChessGame and withdraw the Tkinter window to avoid GUI pop-ups.
        self.game = ChessGame()
        self.game.window.withdraw()  # Hide the window during tests
        self.game.board.reset()      # Ensure the board is in the initial state

    def tearDown(self):
        # Destroy the Tkinter window after each test.
        self.game.window.destroy()

    def test_initial_board_state(self):
        """Test that the game board starts in the standard initial chess position."""
        self.assertEqual(
            self.game.board.fen(), 
            chess.Board().fen(), 
            "Initial board state should match the standard starting position."
        )

    def test_new_game_resets_board(self):
        """Test that making a move and then starting a new game resets the board."""
        # Make a move to change the board state.
        move = list(self.game.board.legal_moves)[0]
        self.game.board.push(move)
        self.assertNotEqual(
            self.game.board.fen(), 
            chess.Board().fen(), 
            "Board state should change after a move."
        )
        # Call new_game and verify the board resets.
        self.game.new_game()
        self.assertEqual(
            self.game.board.fen(), 
            chess.Board().fen(), 
            "Board state should be reset to the initial position after starting a new game."
        )

    def test_make_ai_move(self):
        """Test that the AI move changes the turn on the board."""
        self.game.board.reset()
        current_turn = self.game.board.turn
        self.game.make_ai_move()
        # After the AI makes a move, the board turn should switch.
        self.assertNotEqual(
            self.game.board.turn, 
            current_turn, 
            "AI move should change the board's turn."
        )

    def test_change_difficulty(self):
        """Test that the change_difficulty method properly updates the difficulty setting."""
        # Set the difficulty variable to different values and verify the update.
        self.game.difficulty_var.set("Medium")
        self.game.change_difficulty()
        self.assertEqual(
            self.game.difficulty, 
            "medium", 
            "Difficulty should be set to 'medium'."
        )

        self.game.difficulty_var.set("Hard")
        self.game.change_difficulty()
        self.assertEqual(
            self.game.difficulty, 
            "hard", 
            "Difficulty should be set to 'hard'."
        )

        self.game.difficulty_var.set("Easy")
        self.game.change_difficulty()
        self.assertEqual(
            self.game.difficulty, 
            "easy", 
            "Difficulty should be set to 'easy'."
        )

    @patch.object(ChessGame, 'generate_riddle')
    def test_square_clicked_and_ai_move(self, mock_generate_riddle):
        """
        Simulate a player's move by clicking on a square with a white piece (selecting it)
        and then clicking on a destination square to complete a legal move.
        Verify that after the move, the AI's riddle generation is triggered.
        """
        # For the initial board, white's pawn at a2 is present.
        # In our mapping, a2 corresponds to row=6, col=0.
        self.game.square_clicked(6, 0)
        self.assertIsNotNone(
            self.game.selected_square, 
            "A valid piece click should set selected_square."
        )
        
        # For a pawn on a2, a forward move to a3 should be legal.
        # a3 corresponds to row=5, col=0.
        self.game.square_clicked(5, 0)
        self.assertIsNone(
            self.game.selected_square, 
            "After completing a move, selected_square should be reset."
        )
        mock_generate_riddle.assert_called_once()

    def test_update_board_display(self):
        """
        Test that update_board_display properly updates the button labels to reflect the board state.
        Here, we clear the board and place a white king on e1, then check that the corresponding button
        shows the correct chess symbol.
        """
        # Clear the board and place a white king on e1.
        self.game.board.clear()
        self.game.board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
        
        # Ensure the board has been created.
        if not hasattr(self.game, 'buttons') or not self.game.buttons[0]:
            self.game.create_board()
        self.game.update_board_display()
        
        # In the mapping, e1 (chess.E1) is at index 4.
        # With the update_board_display mapping: square = (7 - row)*8 + col,
        # e1 should be in the button at row 7, column 4.
        row, col = 7, 4
        button_text = self.game.buttons[row][col].cget("text")
        self.assertEqual(
            button_text, 
            '♔', 
            "The button corresponding to e1 should display the white king symbol."
        )

    def test_generate_riddle(self):
        """
        Test the generate_riddle function by mocking the Anthropic API call.
        This test ensures that after a move, the hint_text widget is updated with the generated riddle.
        """
        # Create a dummy response to simulate the Anthropic API.
        dummy_message = MagicMock()
        # Create a dummy object to simulate the content element with a text attribute.
        DummyContent = type("DummyContent", (), {"text": "Test riddle"})  
        dummy_message.content = [DummyContent()]
        
        # Set the Anthropic API client to a dummy object.
        self.game.anthropic = MagicMock()
        self.game.anthropic.messages.create.return_value = dummy_message
        
        # Set the difficulty (affects the prompt generated).
        self.game.difficulty = "easy"
        # Use a legal move from the current board.
        move = list(self.game.board.legal_moves)[0]
        self.game.generate_riddle(move)
        
        # Retrieve the text from the hint_text widget.
        riddle_text = self.game.hint_text.get("1.0", tk.END).strip()
        self.assertEqual(
            riddle_text, 
            "Test riddle", 
            "The hint text should be updated with the dummy riddle text."
        )

if __name__ == '__main__':
    unittest.main()

# Chess Game with AI Hints

This is a Python-based chess game that uses a GUI (Tkinter) and a chess engine (Stockfish) to provide a nontrivial computer play algorithm along with AI-generated hints via the Anthropic API.

## Features
- Graphical chess board with clickable squares.
- Multiple difficulty levels that adjust the engine's skill.
- AI-generated chess riddles/hints using Anthropic.
- Basic unit tests to verify functionality.
  
## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/calvinbeighle/rooksandriddles.git
   cd rooksandriddles
   ```

2. **Set up a virtual environment and install requirements:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r api/requirements.txt
   ```

3. **Configure Anthropic API Key:**

   Create an account on [Anthropic](https://www.anthropic.com/) to obtain your API key. Set your key by adding the following line to your shell profile (e.g. `~/.bash_profile` or `~/.zshrc`):

   ```bash
   export ANTHROPIC_API_KEY="your_api_key_here"
   ```

   Note: Generating AI-based chess riddles/hints may take a little while, so please be patient while the hints are being computed.

4. **Run the game:**

   ```bash
   python api/welcome_screen.py
   ```
5. **Run unit tests:**

   ```bash
   python -m unittest discover tests
   ```
## Contact

For any questions or issues, please contact:

calvin@angusmadethis.com

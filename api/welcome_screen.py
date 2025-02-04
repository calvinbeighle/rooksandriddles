# welcome_screen.py
import tkinter as tk
import os
import PIL.Image
from PIL import ImageTk
from chess_game import ChessGame
from utilities import resource_path

class WelcomeScreen:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Welcome")

        default_bg = self.window.cget('bg')

        self.window.geometry("1200x900")
        self.window.minsize(1200, 600)

        self.main_frame = tk.Frame(self.window, bg=default_bg)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        try:
            # Load the image and render it in memory
            image_path = resource_path("frenchbulldog.png")
            print(f"Loading image from: {image_path}")
            
            if not os.path.exists(image_path):
                raise FileNotFoundError(
                    f"Image file not found at: {image_path}\nPlease make sure 'frenchbulldog.png' is in the proper directory."
                )

            image = PIL.Image.open(image_path)
            original_width, original_height = image.size
            scale_factor = 1.0
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            image = image.resize((new_width, new_height), PIL.Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(image)

            # Add extra space at the bottom of the canvas to allow the Play button to be placed lower.
            extra_space = 150  # You can adjust this value as needed.
            canvas_height = new_height + 20 + extra_space  # 20 is the margin added earlier

            self.canvas = tk.Canvas(
                self.main_frame,
                width=new_width + 20,
                height=canvas_height,
                bg=default_bg,
                highlightthickness=0
            )
            self.canvas.pack(expand=True, pady=(0, 5))
            
            # Draw the image centered on the canvas (it occupies only the top portion)
            self.canvas.create_image(new_width / 2 + 10, new_height / 2 + 10, image=self.photo)
            print("Added image to canvas as a rendered image")

        except Exception as e:
            print(f"Error loading image: {e}")
            extra_space = 50  # still reserve some extra space
            canvas_height = 400 + 20 + extra_space
            self.canvas = tk.Canvas(self.main_frame, width=400, height=canvas_height, bg=default_bg, highlightthickness=0)
            self.canvas.pack(expand=True, pady=(0, 20))
            self.canvas.create_text(200, 200, text="[Image placeholder]")

        # Configure custom font
        self.window.tk.call('font', 'create', 'ElectraLTStd')
        self.window.tk.call('font', 'configure', 'ElectraLTStd', '-family', 'Electra LT Std', '-size', 18)

        # Create the "Play" label and bind its click event.
        self.enter_label = tk.Label(self.main_frame, text="Play", font='ElectraLTStd', bg=default_bg, cursor="hand2")
        self.enter_label.bind("<Button-1>", self.start_game)
        self.canvas.bind("<Button-1>", self.start_game)
        
        # Place the Play button in the canvas.
        # We set the x-coordinate to center it horizontally,
        # and the y-coordinate near the bottom of the canvas.
        play_x = new_width / 2 + 10
        # Position the button 95% of the way down the canvas (you can adjust the factor as needed)
        play_y = canvas_height * 0.95  
        self.canvas.create_window(play_x, play_y, window=self.enter_label)

        # Add copyright text below (packed normally in the main_frame)
        copyright_label = tk.Label(
            self.main_frame,
            text="© ANGUS MADE THIS LLC. ALL RIGHTS RESERVED.",
            font=("Electra LT Std", 10),
            bg=default_bg
        )
        copyright_label.pack(pady=(0,10))

    def start_game(self, event=None):
        self.window.destroy()
        game = ChessGame()
        game.run()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    welcome = WelcomeScreen()
    welcome.run()

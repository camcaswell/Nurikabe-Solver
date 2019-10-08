import tkinter as tk

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
WINDOW_BUFFER = 10
LINE_WIDTH = 2

class Board_Display:
    def __init__(self, master, board):
        self.master = master
        master.title("Nurikabe Board")

        canvas = tk.Canvas(master, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        canvas.pack()

        cell_width = (WINDOW_WIDTH-LINE_WIDTH-1-(2*WINDOW_BUFFER))//board.width
        cell_height = (WINDOW_HEIGHT-LINE_WIDTH-1-(2*WINDOW_BUFFER))//board.height

        def shift(j):
            return WINDOW_BUFFER+LINE_WIDTH+1+j

        cmap = {0:'white', 1:'white', 2:'black'}

        for cell in board.cells.values():
            canvas.create_rectangle(
                                    shift(cell.x*cell_width),
                                    shift(cell.y*cell_height),
                                    shift((cell.x+1)*cell_width),
                                    shift((cell.y+1)*cell_height),
                                    width=LINE_WIDTH,
                                    fill=cmap[cell.color],
                                )
            if cell.label is not '':
                canvas.create_text(
                                    shift((cell.x+.5)*cell_width),
                                    shift((cell.y+.5)*cell_height),
                                    text=cell.label,
                                    font=('Arial', cell_width//3),
                                )





def show_board(board):
    window = tk.Tk()
    Board_Display(window, board)
    window.mainloop()


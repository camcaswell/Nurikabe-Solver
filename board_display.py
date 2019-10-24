import tkinter as tk
import threading

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400
WINDOW_BUFFER = 10
LINE_WIDTH = 2
COORDS = True

class Board_Display:
    def __init__(self, master, board, title):
        self.master = master
        master.title(title)

        canvas = tk.Canvas(master, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        canvas.pack()

        edge_buffer = WINDOW_BUFFER+LINE_WIDTH+1
        shift = edge_buffer + (20 if COORDS else 0)

        cell_width = (WINDOW_WIDTH-(edge_buffer + shift))//board.width
        cell_height = (WINDOW_HEIGHT-(edge_buffer + shift))//board.height

        cmap = {0:'white', 1:'white', 2:'black'}

        for cell in board.cells.values():
            canvas.create_rectangle(
                                    shift + cell.x*cell_width,
                                    shift + cell.y*cell_height,
                                    shift + (cell.x+1)*cell_width,
                                    shift + (cell.y+1)*cell_height,
                                    width=LINE_WIDTH,
                                    fill=cmap[cell.color],
                                )
            if cell.label is not '':
                canvas.create_text(
                                    shift + (cell.x+.5)*cell_width,
                                    shift + (cell.y+.5)*cell_height,
                                    text=cell.label,
                                    font=('Arial', cell_width//3),
                                )

        if COORDS:
            for row in range(board.height):
                canvas.create_text(
                                    WINDOW_BUFFER+10,
                                    shift + (row+0.5)*cell_height,
                                    text=str(row),
                                    font=('Arial', 10)
                                )
            for col in range(board.width):
                canvas.create_text(
                                    shift + (col+0.5)*cell_width,
                                    WINDOW_BUFFER+10,
                                    text=str(col),
                                    font=('Arial', 10)
                                )


def show_board(board, title):
    board_copy = board.copy()
    th = threading.Thread(target=_show_board, args=(board_copy, title))
    th.start()

def _show_board(board, title):
    window = tk.Tk()
    Board_Display(window, board, title)
    window.mainloop()

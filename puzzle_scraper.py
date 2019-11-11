from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from math import sqrt
from json import dump

def download_puzzles(count=5, size=5, difficulty='Normal'):

    encode = {
                (5, 'normal'): 999,    # This is the default, so any unused number will work
                (5, 'hard'): 6,
                (7, 'normal'): 1,
                (7, 'hard'): 7,
                (10, 'normal'): 2,
                (10, 'hard'): 8,
                (12, 'normal'): 5,
                (12, 'hard'): 9,
                (15, 'normal'): 3,
                (15, 'hard'): 10,
                (20, 'normal'): 4
            }

    try:
        url_query = f'?size={encode[(size, difficulty.lower())]}'
    except KeyError:
        raise ValueError("Invalid size/difficulty combination.")


    board_lists = []
    with webdriver.Firefox(executable_path=r'M:\\Program Files\\geckodriver.exe') as driver:
        for _ in range(count):
            driver.get(f'https://www.puzzle-nurikabe.com/{url_query}')
            board = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "board-back")))
            board = driver.find_elements_by_class_name('board-back')[0]
            cell_elements = board.find_elements_by_xpath(".//*")

            board_size = sqrt(len(cell_elements))
            assert board_size == int(board_size), "Expected a square number"
            board_size = int(board_size)

            cell_elements_square = [cell_elements[board_size*i:board_size*(i+1)] for i in range(board_size)]

            board_list = []
            for row in cell_elements_square:
                board_row = []
                for cell_element in row:
                    if cell_element.get_attribute("class") == "cell selectable cell-off":
                        board_row.append(0)
                    elif cell_element.get_attribute("class") == "nurikabe-task-cell cell-off":
                        board_row.append(int(cell_element.get_attribute("innerText")))
                    else:
                        raise Exception(f"Unrecognized cell element: {cell_element}")
                board_list.append(board_row)
            board_lists.append(board_list)
    return board_lists

def save_puzzle_cases(count=5, size=5, difficulty='Normal'):
    with open('puzzles.json', 'w') as write_file:
        dump(download_puzzles(count, size, difficulty), write_file)

if __name__ == '__main__':
    save_puzzle_cases(size=10, difficulty='Hard')
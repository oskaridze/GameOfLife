# Imports
import dearpygui.dearpygui as dpg # GUI library
from pynput import keyboard
import win32gui
import win32con
import random
import time
# import params - no need

# Constants
ROWS = 10
COLS = 10
PROBABILITYTOLIVE = 15
ALIVESIGN = ' ■ '
DEADSIGN = ' □ '
ENERGY = 10
ALLDEAD = False
GEN = 0

rows = ROWS #params.ROWS
cols = COLS #params.COLS
probabilityToLive = PROBABILITYTOLIVE #params.PROBABILITYTOLIVE
defEnergy = ENERGY #params.ENERGY
defGen = GEN #params.GEN
defAllDead = ALLDEAD #params.ALLDEAD
# aliveSign = params.ALIVESIGN
# deadSign = params.DEADSIGN

#Screen coords
screenX = 3735
screenY = 20

# Colors
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
RED = (255, 0, 0, 255)

class Cell:
    def __init__(self, x, y, isAlive=False, isRegenerated=False):
        self.x = x
        self.y = y
        self.isAlive = isAlive
        self.isRegenerated = isRegenerated

def neighboursCount(Cell) -> int:
    count = 0
    x, y = Cell.x, Cell.y

    # not diagonally
    if y != 0:
        if cells[x][y-1].isAlive:
            count += 1
    if y != cols-1:        
        if cells[x][y+1].isAlive:
            count += 1
    if x != 0:
        if cells[x-1][y].isAlive:
            count += 1
    if x != rows-1:
        if cells[x+1][y].isAlive:
            count += 1
    
    # diagonally
    if x != 0 and y != 0:
        if cells[x-1][y-1].isAlive:
            count += 1
    if x != rows-1 and y != 0:        
        if cells[x+1][y-1].isAlive:
            count += 1
    if x != 0 and y != cols-1:
        if cells[x-1][y+1].isAlive:
            count += 1
    if x != rows-1 and y != cols-1:
        if cells[x+1][y+1].isAlive:
            count += 1

    return count

def onStart() -> None:
    global energy
    global gen
    global allDead
    energy = defEnergy
    gen = defGen
    allDead = defAllDead
    for i in range(rows):
        for j in range(cols):
            cell = Cell(i, j)
            state = random.randint(1, 100)
            if state > probabilityToLive:
                cell.isAlive = False
                # grid[i][j] = deadSign
                cell.x = i
                cell.y = j
            else:
                cells[i][j].isAlive = True
                # grid[i][j] = aliveSign
                cell.x = i
                cell.y = j

def chooseRandomDeadCell(cells: list):
    cell = random.choice(cells[random.randint(0, rows-1)])
    while not cell.isAlive:
        cell = random.choice(cells[random.randint(0, rows-1)])
    return cell

def onRelease() -> None:
    global energy
    energy += 1

def hideFromTaskbar(window_title) -> None:
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style | win32con.WS_EX_TOOLWINDOW)

# grid = [[deadSign for _ in range(rows)] for _ in range(cols)]
cells = [[Cell(i, j) for i in range(rows)] for j in range(cols)]

listener = keyboard.Listener(on_release=onRelease)
listener.start()

onStart()


dpg.create_context()
dpg.create_viewport(title='Game Of Life', width=100, height=100, x_pos=screenX, y_pos=screenY, always_on_top=True, min_width=100, min_height=100, decorated=False)
dpg.setup_dearpygui()
dpg.show_viewport()

with dpg.window(autosize=True, no_title_bar=True, no_scrollbar=True, pos=[0, 0]):
    hideFromTaskbar("Game Of Life")
    with dpg.drawlist(width=100, height=100):     
        while dpg.is_dearpygui_running():
            itemsToDelete = []
            died = 0
            gen += 1
            energy -= 1
            color = ()

            # print(f"Gen: {gen}")
            # print(f"Energy: {energy}")

            genText = dpg.draw_text((0, 0), f"Gen: {gen}", color=(250, 250, 250, 255), size=12)
            energyText = dpg.draw_text((0, 15), f"Energy: {energy}", color=(250, 250, 250, 255), size=12)
            itemsToDelete.append(genText)
            itemsToDelete.append(energyText)

            for _ in range(2):
                rCell = chooseRandomDeadCell(cells)
                cells[rCell.x][rCell.y].isAlive = True
                cells[rCell.x][rCell.y].isRegenerated = True
                energy -= 1

            for i in range(rows):
                for j in range(cols):
                    cell = cells[i][j]
                    if cell:
                        count = neighboursCount(cell)
                        if cell.isAlive:
                            if count < 2:
                                cell.isAlive = False
                                # grid[i][j] = deadSign
                                died += 1
                                color = BLACK
                            elif count == 2 or count == 3:
                                cell.isAlive = True
                                # grid[i][j] = aliveSign
                                died -= 1
                                color = WHITE
                            elif count > 3:
                                cell.isAlive = False
                                # grid[i][j] = deadSign
                                died += 1
                                color = BLACK
                        
                        if cell.isRegenerated:
                            # grid[i][j] = ' 0 '
                            cell.isRegenerated = False
                            color = WHITE
                            energy += 0.5
                        
                        if not cell.isAlive:
                            if count == 3:
                                # grid[i][j] = aliveSign
                                cell.isAlive = True
                                cell.isRegenerated = True
                                died -= 1
                                color = RED
                            else:
                                # grid[i][j] = deadSign
                                died += 1
                                color = BLACK


                    rect = dpg.draw_rectangle((5*j+5, 5*i+30), (5*j+10-1, 5*i+30+5-1), color=color, fill=color)
                    itemsToDelete.append(rect)
                #     print(grid[i][j], end="")
                # print("\n")


                if died >= rows * cols or energy <= 0:
                    # print("All Died!")
                    onStart()

            dpg.render_dearpygui_frame()
            time.sleep(0.5)

            for item_id in itemsToDelete:
                dpg.delete_item(item_id)

        dpg.destroy_context()
        listener.stop()
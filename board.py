
class Cell:
  def __init__(self, x, y, color):
    self.x = x
    self.y = y
    self.color = color
    self.region = None
    # 0-unknown 1-white 2-black

class Region:
  def __init__(self, size, color, firstMember):
    self.color = color
    self.size = size
    self.members = [firstMember]
    firstMember.region = self

class Board:
  def __init__(self, grid):
    self.height = len(grid)
    self.width = len(grid[0])
    self.regions = []
    self.cells = {}
    for y, row in enumerate(grid):
      for x, val in enumerate(row):
        if val == 0:
          self.cells[(x,y)] = Cell(x, y, 0)
        else:
          newCell = Cell(x, y, 1)
          newRegion = Region(val, 1, newCell)
          self.cells[(x,y)] = newCell
          self.regions.append(newRegion)
  
  def annex(self, region1, region2):
    region1.members += region2.members
    self.regions.remove(region2)

  def _get_list_form(self):
    l = []
    for y in range(self.height):
      for x in range(self.width):
        l[y][x] = self.cells[(x,y)].color
    return l
  
  def is_solved(self):
    for cell in self.cells.items():
      if cell.color == 0:
        return False
    return True
  
  def neighbors(self, cell):
      nbors = [(cell.x+1, cell.y),
               (cell.x-1, cell.y),
               (cell.x, cell.y+1),
               (cell.x, cell.y-1)
              ]
      for x,y in nbors:
        if x<0 or x>self.width or y<0 or y>self.height:
          nbors.remove((x,y))
      return [self.cells[coords] for coords in nbors]
  
  def __str__(self):
    return str(self._get_list_form())

  # inferences

  # put black squares between distinct white regions
  # test hori and vert pairs
  def create_fences(self, region):
    for cell in region.members:
      for nbor in self.neighbors(cell):
        if nbor.region and nbor.region.color == 1 and nbor.region != region:


def solve(grid):
  board = Board(grid)

  while not board.is_solved():
  

def main():
  grid = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [3, 0, 0, 2, 0],
        [0, 0, 0, 0, 1],
        [3, 0, 0, 0, 0]
      ]
  
  sol = [
          [2, 2, 2, 2, 2],
          [2, 1, 2, 1, 2],
          [1, 1, 2, 1, 2],
          [2, 2, 2, 2, 1],
          [1, 1, 1, 2, 2]
        ]
  
  b = solve(grid)
  print(b)
  print(b._get_list_form() == sol)


if __name__ == '__main__':
  c = Cell(1,2,0)
  c.region = 4
  print(c.region)


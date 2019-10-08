
class Cell:
  def __init__(self, x, y, color):
    self.x = x
    self.y = y
    self.color = color
    self.region = None
    # 0-unknown 1-white 2-black

  def __repr__(self):
    #return f'C[{self.x},{self.y}]-{self.color}-{int(bool(self.region))}'
    return f'({self.x},{self.y})'


class Region:
  def __init__(self, size, color, firstMember):
    self.color = color
    self.size = size
    self.members = [firstMember]
    firstMember.region = self

class Board:
  def __init__(self):
    self.regions = []
    self.cells = {}


  def build(self, grid):
    self.height = len(grid)
    self.width = len(grid[0])
    for y, row in enumerate(grid):
      for x, val in enumerate(row):
        if val == 0:
          self.cells[(x,y)] = Cell(x, y, 0)
        else:
          newCell = Cell(x, y, 1)
          newRegion = Region(val, 1, newCell)
          self.cells[(x,y)] = newCell
          self.regions.append(newRegion)

  def manual_build(self, cell_colors):
    self.height = len(cell_colors)
    self.width = len(cell_colors[0])
    for y, row in enumerate(cell_colors):
      for x, color in enumerate(row):
        self.cells[(x,y)] = Cell(x, y, color)
  
  def annex(self, region1, region2):
    region1.members += region2.members
    self.regions.remove(region2)

  def _get_list_form(self):
    l = []
    for y in range(self.height):
      l.append([])
      for x in range(self.width):
        l[y].append(self.cells[(x,y)].color)
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
      return [self.cells[coords] for coords in nbors if 0<=coords[0]<self.width and 0<=coords[1]<self.height]

  def find_paths(self, start, end, used=[], color=None):
    if color == None:
      color = start.color
    used = used[:]
    used.append(start)
    nbors = [nbor for nbor in self.neighbors(start) if nbor not in used and nbor.color in [0, color]]
    if end in nbors:
      return [[start, end]]
    else:
      used += nbors
      paths = []
      for nbor in nbors:
        for path in self.find_paths(nbor, end, used, color):
          paths.append([start]+path)
      return paths
  
  def __str__(self):
    return str(self._get_list_form())

  # inferences

  # put black squares between distinct white regions
  def create_fences(self, region):
    changeFlag = False
    # horizontal pairs
    for x in range(self.width-2):
      for y in range(self.height-2):
        cell = self.cells[(x,y)]
        if cell.region and cell.region.color == 1:
          potential_fence = self.cells[(x+1,y)]
          if potentional_fence.color == 0:
            nbor = self.cells[(x+2,y)]
            if nbor.region and nbor.region.color == 1 and nbor.region != cell.region:
              pass


  def solve(self):
    while not board.is_solved():
      # apply inferences
      pass



  

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

  maze = [
          [0, 0, 0, 0, 1],
          [0, 0, 0, 1, 0],
          [0, 2, 2, 2, 2],
          [0, 0, 0, 0, 1],
          [2, 0, 0, 0, 0]
        ]
  
  b = Board()
  b.manual_build(maze)
  cell1 = b.cells[(3,1)]
  cell2 = b.cells[(4,3)]
  paths = b.find_paths(cell1, cell2)

  print()
  for path in paths:
    print(path)


if __name__ == '__main__':
    main()



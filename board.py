
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
  def __init__(self, color, firstMember, size=None):
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
      for x, size in enumerate(row):
        if size == 0:
          self.cells[(x,y)] = Cell(x, y, 0)
        else:
          newCell = Cell(x, y, 1)
          newRegion = Region(1, newCell, size)
          self.cells[(x,y)] = newCell
          self.regions.append(newRegion)
    return self

  def manual_build(self, cell_colors):
    self.height = len(cell_colors)
    self.width = len(cell_colors[0])
    for y, row in enumerate(cell_colors):
      for x, color in enumerate(row):
        self.cells[(x,y)] = Cell(x, y, color)
    return self

  def _get_list_form(self):
    l = []
    for y in range(self.height):
      l.append([])
      for x in range(self.width):
        l[y].append(self.cells[(x,y)].color)
    return l
  
  def is_solved(self):
    for cell in self.cells.values():
      if cell.color == 0:
        return False
    return True

  def annex(self, region1, region2):
    if region1.size is not None and region2.size is not None:
      raise Exception("Cannot merge two regions with defined sizes.")
    region1.members += region2.members
    if region2.size is not None:
      region1.size = region2.size
    self.regions.remove(region2)

  def set_color(self, cell, color):
    # sets the color and annexes any newly-adjacent regions
    if cell.color != 0:
      raise Exception("Can only set unknown cells.")
    new_region = Region(color, cell)
    cell.region = new_region
    cell.color = color
    for nbor_region in [nbor.region for nbor in self.neighbors(cell) if nbor.region is not None and nbor.color == color]:
      self.annex(new_region, nbor_region)
  
  def neighbors(self, cell, d=1, interior=False):
      if d<1:
        return set()
      coords = {(cell.x+(n1*(d-i)), cell.y+(n2*i)) for i in range(d+1) for n1 in (1,-1) for n2 in (1,-1)}
      nbors = {self.cells[pos] for pos in coords if 0<=pos[0]<self.width and 0<=pos[1]<self.height}
      if interior:
        nbors = nbors.union(self.neighbors(cell, d-1, True))
      return nbors

  def find_paths(self, start, end, used=[], color=None):
    if color is None:
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
    return '\n'.join([str(row) for row in self._get_list_form()])



  # inferences

  # put black squares between distinct white regions
  def create_fences(self):
    for region in self.regions:
      for cell in region.members:
        for potential_fence in self.neighbors(cell, 1):
          if potential_fence.color == 0:
            for nbor in self.neighbors(potential_fence, 1):
              if nbor.color == 1 and nbor.region and nbor.region != region:
                self.set_color(potential_fence, 2)
                #return True
    return False



  def solve(self):
    while not self.is_solved():
      # apply inferences
      self.create_fences()
      break
    return self



  

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
    grid = [
          [0, 0, 0, 0, 0],
          [0, 0, 4, 0, 0],
          [3, 0, 0, 2, 0],
          [0, 0, 0, 0, 1],
          [3, 0, 0, 0, 0]
        ]
    b = Board()
    print(b.build(grid).solve())



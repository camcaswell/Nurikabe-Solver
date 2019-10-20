from board_display import *

class Cell:
  def __init__(self, x, y, color, label=''):
    self.x = x
    self.y = y
    self.color = color     # 0-unknown 1-white 2-black
    self.label = str(label)
    self.region = None
    self.potential_regions = set()  # Unknown cells next to a white region are either part of that region or black. Multiple regions can be adjacent without knowing whether they're the same region.


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
    self.white_regions = set()
    self.black_regions = set()
    self.cells = {}

  def __eq__(self, other):
    return self.get_list_form() == other.get_list_form()


  def build(self, grid):
    self.height = len(grid)
    self.width = len(grid[0])
    for y, row in enumerate(grid):
      for x, size in enumerate(row):
        if size == 0:
          self.cells[(x,y)] = Cell(x, y, 0)
        else:
          newCell = Cell(x, y, 1, label=size)
          newRegion = Region(1, newCell, size)
          self.cells[(x,y)] = newCell
          self.white_regions.add(newRegion)
    for region in self.white_regions:
      for cell in region.members:
        for nbor in [n for n in self.neighbors(cell) if n.color==0]:
          nbor.potential_regions.add(region)
    return self

  def manual_build(self, cell_colors):
    self.height = len(cell_colors)
    self.width = len(cell_colors[0])
    for y, row in enumerate(cell_colors):
      for x, color in enumerate(row):
        self.cells[(x,y)] = Cell(x, y, color)
    return self

  def get_list_form(self):
    return [ [self.cells[(x,y)].color for x in range(self.width)] for y in range(self.height) ]

  def __str__(self):
    return '\n'.join([str(row) for row in self.get_list_form()])

  def show(self, title="Nurikabe Board"):
    show_board(self, title)
  

  def is_solved(self):
    for cell in self.cells.values():
      if cell.color == 0:
        return False
    return True

  def annex(self, region1, region2):
    # incorporates region2 into region 1

    # print("\nRegions:")
    # print('\n'.join([str(r.members) for r in self.regions]))


    assert region1.size is None or region2.size is None, "Cannot merge two regions with defined sizes."
    assert region2.color == region2.color, "Cannot merge two regions of different colors."

    region1.members += region2.members
    if region2.size is not None:
      region1.size = region2.size
    for cell in region2.members:
      cell.region = region1
      for nbor in [n for n in self.neighbors(cell) if n.color==0]:
        nbor.potential_regions.discard(region2)
        nbor.potential_regions.add(region1)
    self.regions.remove(region2)

  def set_color(self, cell, color):
    # sets the color and annexes any newly-adjacent regions

    assert cell.color == 0, "Can only set unknown cells."
    assert color in [1,2], "Can only set color to be black or white."

    cell.potential_regions.clear()
    new_region = Region(color, cell)
    if color == 1:
      self.white_regions.add(new_region)
    else:
      self.black_regions.add(new_region)
    cell.region = new_region
    cell.color = color
    if color == 1:
      cell.label = u"\u22C5"    # dot operator
    for nbor_region in {nbor.region for nbor in self.neighbors(cell) if nbor.region is not None and nbor.color == color}:
      try:
        self.annex(new_region, nbor_region)
      except Exception as err:
        self.show("Failed to annex")
        print("\nFailed to annex:")
        print(new_region.members)
        print(nbor_region.members)
        raise

  
  def neighbors(self, cell, d=1, interior=False):
    if d<1:
      return set()
    coords = {(cell.x+(n1*(d-i)), cell.y+(n2*i)) for i in range(d+1) for n1 in (1,-1) for n2 in (1,-1)}
    nbors = {self.cells[pos] for pos in coords if 0<=pos[0]<self.width and 0<=pos[1]<self.height}
    if interior:
      nbors.update(self.neighbors(cell, d-1, True))
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

  def expand_white(self, region, open_layer=None, used=set(), shell=0, depth_limit=1):
    # expand *region* to *depth_limit* by adding successive shells of possible cells
    # returns set of all cells that could belong to region
    if open_layer is None:
      open_layer = set(region.members)
    next_open = set()
    for cell in open_layer:
      for nbor in self.neighbors(cell):
        if nbor not in next_open|open_layer|used:
          if nbor.color==0 and all([r.size is None for r in nbor.potential_regions-{region}]):       # if nbor isn't adjacent to any other regions with defined size (i.e. a separate island)
            if sum([len(r.members) for r in nbor.potential_regions-{region}]) + shell < region.size: # if this region can annex all regions adjacent to *nbor* w/o violating its size
              next_open.add(nbor)
          elif nbor.color==1:   # Assuming that the region has already expanded over an unknown cell on the border, and thus checked that this white cell is OK to expand into
            next_open.add(nbor)
    used.update(open_layer)
    if shell+1<depth_limit:
      return self.expand_white(region, next_open, used, shell+1, depth_limit)
    else:
      return used|next_open







  # inferences

  # put black squares between distinct white regions
  # made redundant by find_unreachable
  def create_fences(self):
    for region in self.white_regions:
      for cell in region.members:
        for potential_fence in [pf for pf in self.neighbors(cell, 1) if pf.color==0]:
          for nbor in self.neighbors(potential_fence, 1):
            if nbor.color == 1 and nbor.region != region:
              self.set_color(potential_fence, 2)
              return True
    return False

  # put black squres around finished islands
  def surround_islands(self):
    for region in self.white_regions:
      if region.size is not None and region.size == len(region.members):
        for cell in region.members:
          for nbor in self.neighbors(cell):
            if nbor.color == 0:
              self.set_color(nbor, 2)

  # set all cells that can't be reached by any islands to black 
  def find_unreachable(self):
    reachable = set()
    for region in [r for r in self.white_regions if r.size is not None]:
      reachable.update(self.expand_white(region, depth_limit=region.size-len(region.members)))
    for cell in set(self.cells.values())-reachable:
      if cell.color == 0:
        self.set_color(cell, 2)


  def solve(self):
    while not self.is_solved():
      # apply inferences
      self.find_unreachable()
      print("\nBREAK")
      print(self)
      self.find_unreachable()

      # self.surround_islands()
      # self.create_fences()
      break
    return self

 

if __name__ == '__main__':
    grid = [
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [3, 0, 0, 2, 0],
          [0, 0, 0, 0, 1],
          [3, 0, 0, 0, 0]
        ]
    b = Board()
    b.build(grid)
    try:
      b.solve().show("FINISHED")
    except Exception as err:
      print(err)



from copy import deepcopy
from math import inf as INF
from board_display import *

class Cell:
  def __init__(self, x, y, color, label=''):
    self.x = x
    self.y = y
    self.color = color     # 0-unknown 1-white 2-black
    self.label = str(label)
    self.region = None
    self.potential_regions = set()  # Unknown cells next to a white region are either part of that region or black. Multiple regions can be adjacent without knowing whether they're the same region.

  @property
  def coords(self):
    return (self.x, self.y)

  @coords.setter
  def coords(self, coords):
    self.x, self.y = coords

  def __repr__(self):
    #return f'C[{self.x},{self.y}]-{self.color}-{int(bool(self.region))}'
    return f'C<{self.x},{self.y}>'

  def __lt__(self, other):
    return self.coords < other.coords

  def tcd(self, other):
    return abs(self.x-other.x) + abs(self.y-other.y)


class Region:
  def __init__(self, board, color, *members, size=None):
    assert len(members) > 0, "Cannot create Region with no members."
    assert all([member.color == color for member in members]), "Color mismatch."
    self.color = color
    self.size = size
    self.members = members
    self.board = board
    for member in members:
      member.region = self
    if color == 1:
      board.white_regions.add(self)
    else:
      board.black_regions.add(self)
    if self.is_master():
      self.remote_parts = set()   #It's possible to know that a white region is part of an island without knowing how they're connected. They are modeled as separate regions: the master and the remote part.

  def __repr__(self):
    return f'<R:{self.color}:{self.size} {sorted(self.members)}>'

  def is_done(self):
    return self.size == len(self.members)

  def is_master(self):
    return not self.size is None

  def annex(self, other):
    # Merge *other* into *self*.
    assert not self.is_master() or not other.is_master(), "Cannot merge two regions with defined sizes."
    assert self.color == other.color, "Cannot merge two regions of different colors."

    self.members += other.members
    if other.is_master():
      self.size = other.size
    for cell in other.members:
      cell.region = self
      if self.color == 1:
        for nbor in [n for n in self.board.neighbors(cell) if n.color==0]:
          nbor.potential_regions.discard(other)
          nbor.potential_regions.add(self)
    self.board.white_regions.discard(other)
    self.board.black_regions.discard(other)



class Board:
  def __init__(self):
    self.white_regions = set()
    self.black_regions = set()
    self.cells = {}

  def __str__(self):
    return '\n'.join([str(row) for row in self.get_list_form()])

  def __eq__(self, other):
    return self.get_list_form() == other.get_list_form()

  def copy(self):
    return deepcopy(self)

  def get_list_form(self):
    return [ [self.cells[(x,y)].color for x in range(self.width)] for y in range(self.height) ]

  def show(self, title="Nurikabe Board"):
    show_board(self, title)
    return self


  def build(self, grid):
    # Build out model of a new Nurikabe board.
    self.height = len(grid)
    self.width = len(grid[0])
    for y, row in enumerate(grid):
      for x, size in enumerate(row):
        if size == 0:
          self.cells[(x,y)] = Cell(x, y, 0)
        else:
          newCell = Cell(x, y, 1, label=size)
          newRegion = Region(self, 1, newCell, size=size)
          self.cells[(x,y)] = newCell
          self.white_regions.add(newRegion)
    for region in self.white_regions:
      for cell in region.members:
        for nbor in [n for n in self.neighbors(cell) if n.color==0]:
          nbor.potential_regions.add(region)
    return self

  def manual_build(self, cell_colors):
    # Use to explicitly set the colors of every cell.
    # Mostly for testing.
    self.height = len(cell_colors)
    self.width = len(cell_colors[0])
    for y, row in enumerate(cell_colors):
      for x, color in enumerate(row):
        self.cells[(x,y)] = Cell(x, y, color)
    return self
  

  def is_solved(self):
    for cell in self.cells.values():
      if cell.color == 0:
        return False
    return True

  def set_color(self, cell, color):
    # Set the color of a cell and annex any newly-adjacent regions.
    assert cell.color == 0, "Can only set unknown cells."
    assert color in (1,2), "Can only set color to be black or white."

    cell.potential_regions.clear()
    new_region = Region(self, color, cell)
    if color == 1:
      self.white_regions.add(new_region)
      for nbor in [nbor for nbor in self.neighbors(cell) if nbor.color == 0]:
        nbor.potential_regions.add(new_region)
    else:
      self.black_regions.add(new_region)
    cell.region = new_region
    cell.color = color
    if color == 1:
      cell.label = u"\u22C5"    # dot operator
    for nbor_region in {nbor.region for nbor in self.neighbors(cell) if nbor.region is not None and nbor.color == color}:
      new_region.annex(nbor_region)


  def neighbors(self, cell, d=1, interior=False):
    # Get set of cells that are taxicab distance *d* away from *cell*.
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
    nbors = [nbor for nbor in self.neighbors(start) if nbor not in used and nbor.color in (0,color)]
    if end in nbors:
      return [[start, end]]
    else:
      used += nbors
      paths = []
      for nbor in nbors:
        for path in self.find_paths(nbor, end, used, color):
          paths.append([start]+path)
      return paths

  def find_reach_white(self, region, open_layer=None, used=None, depth=0, depth_limit=None):
    # Find the reach of *region* to *depth_limit* by adding successive shells of possible cells.
    # Returns set of all cells that could belong to region.
    if open_layer is None:
      open_layer = {cell:len(region.members) for cell in set(region.members)}   # the *min_req_size* for *cell* is the number of cells it would take to connect *region* to *cell*, including itself and the cells already in *region*
    if used is None:
      used = set()
    if depth_limit is None:
      depth_limit = region.size - len(region.members)
    # print(f'OL: {sorted(open_layer)}')
    # print(f'US: {sorted(used)}')
    # print()
    if depth >= depth_limit:
      return used|set(open_layer)
    else:
      next_open = {}
      for cell, min_req_size in open_layer.items():
        for nbor in [n for n in self.neighbors(cell) if n not in set(next_open)|set(open_layer)|used]:    # nbors that haven't already been accounted for
          if nbor.color==0 and all([r.size is None for r in nbor.potential_regions-{region}]):  # if nbor isn't adjacent to any other regions with defined size (i.e. a separate island)
            connected_cells = {cell for r in nbor.potential_regions-{region} for cell in r.members}|{nbor}
            if len(connected_cells) + min_req_size <= region.size:                          # if this region can annex all regions adjacent to *nbor* w/o violating its size
              for cell in connected_cells:
                next_open[cell] = min(next_open.get(cell, INF), min_req_size+len(connected_cells))
      used.update(open_layer)
      return self.find_reach_white(region, next_open, used, depth+1, depth_limit)


  # INFERENCES

  def create_fences(self):
    # Put black squares between distinct white regions.
    # Made redundant by find_unreachable.
    for region in self.white_regions:
      for cell in region.members:
        for potential_fence in [pf for pf in self.neighbors(cell, 1) if pf.color==0]:
          for nbor in self.neighbors(potential_fence, 1):
            if nbor.color == 1 and nbor.region != region:
              self.set_color(potential_fence, 2)
              return True
    return False

  def surround_islands(self):
    # Put black squres around finished islands.
    # Made redundant by find_unreachable.
    for region in self.white_regions:
      if region.is_master() and region.size == len(region.members):
        for cell in region.members:
          for nbor in self.neighbors(cell):
            if nbor.color == 0:
              self.set_color(nbor, 2)

  def find_unreachable(self):
    # Set all cells that can't be reached by any islands to black.
    reachable = set()
    for region in [r for r in self.white_regions if r.is_master()]:
      reachable.update(self.find_reach_white(region))
    for cell in set(self.cells.values())-reachable:
      if cell.color == 0:
        self.set_color(cell, 2)

  def prevent_pools(self):
    # Find any unknown cells that are part of a 2x2 square where the other cells are black and set them to white.
    for x in range(self.width-1):
      for y in range(self.height-1):
        nonblack = [self.cells[(x+i,y+j)] for i in (0,1) for j in (0,1) if self.cells[(x+i,y+j)].color!=2]    # The non-black cells in the square
        if len(nonblack) == 1 and nonblack[0].color == 0:
          self.set_color(nonblack[0], 1)

  def expand_white(self):
    # Calculate all the ways that each white island can expand to their size limit, and then find any cells that they all have in common and set those to white.
    for region in [r for r in self.white_regions if r.is_master()]:
      expansions = self.white_expansions(region)


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
    b.build(grid).find_unreachable()
    b.show(1)
    b.prevent_pools()
    b.show(2)
    b.find_unreachable()
    b.show(3)




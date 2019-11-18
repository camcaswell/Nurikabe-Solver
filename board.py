from copy import deepcopy
from math import inf as INF
import json
from ordered_set import OrderedSet

from board_display import *
from pathtree import *
from uniquequeue import UniqueQueue

LAST_BOARD_FILE = 'last_board.json'

class Cell:
  def __init__(self, x, y, color, label=''):
    self.x = x
    self.y = y
    self.color = color     # 0-unknown 1-white 2-black
    self.label = str(label)
    self.region = None
    self.potential_regions = OrderedSet()  # Unknown cells next to a white region are either part of that region or black.
                                           # Multiple regions can be adjacent without knowing whether they're the same region.

  @property
  def coords(self):
    return (self.x, self.y)

  @coords.setter
  def coords(self, coords):
    self.x, self.y = coords

  def __repr__(self):
    return f'C<{self.coords}-{self.color}-{int(bool(self.region))}>'
    #return f'C<{self.x},{self.y}>'

  def __lt__(self, other):
    return self.coords < other.coords

  def tcd(self, other):
    return abs(self.x-other.x) + abs(self.y-other.y)

  def simple(self):
    if self.region is None:
      region_idx = None
    else:
      region_idx = self.region.get_index()
    return {
              'coords': self.coords,
              'color': self.color,
              'label': self.label,
              'region_idx': region_idx,
              'p_region_idxs': [region.get_index() for region in self.potential_regions]
          }



class Region:
  def __init__(self, board, color, *members, size_limit=INF):
    assert all([member.color == color for member in members]), "Color mismatch."
    self.color = color
    self.size_limit = size_limit
    self.members = set(members)
    self.board = board
    for member in members:
      member.potential_regions.clear()
      member.region = self
    if color == 1:
      board.white_regions.add(self)
    else:
      board.black_regions.add(self)
    if self.is_master():
      self.remote_parts = set()   #It's possible to know that a white region is part of an island without knowing how they're connected. They are modeled as separate regions: the master and the remote part.

  def __repr__(self):
    return f'<R:{self.color}:{self.size_limit} {sorted(self.members)}>'

  def is_done(self):
    return self.size_limit == len(self.members)

  def is_master(self):
    return self.size_limit is not INF

  def get_index(self):
    if self.color == 1:
      region_idx = self.board.white_regions.index(self)
    elif self.color == 2:
      region_idx = self.board.black_regions.index(self)
    else:
      region_idx = None
    return region_idx

  def simple(self):
    return {
              'size_limit': self.size_limit,
          }


  def annex(self, other):
    # Merge *other* into *self*.
    if self is other:
      return
    assert not self.is_master() or not other.is_master(), "Cannot merge two regions with defined size_limits."
    assert self.color == other.color, "Cannot merge two regions of different colors."

    self.members |= other.members
    if other.is_master():
      self.size_limit = other.size_limit
    for cell in other.members:
      cell.region = self
      if self.color == 1:
        for nbor in [n for n in self.board.neighbors(cell) if n.color==0]:
          nbor.potential_regions.discard(other)
          nbor.potential_regions.add(self)
    self.board.white_regions.discard(other)
    self.board.black_regions.discard(other)









class Board:

  def __init__(self, board_list=None, manual_list=None):
    self.white_regions = OrderedSet()
    self.black_regions = OrderedSet()
    self.cells = {}
    if board_list is not None:
      self.build(board_list)
    elif manual_list is not None:
      self.manual_build(manual_list)

  @property
  def height(self):
    return max([cell.y for cell in self.cells.values()])+1

  @property
  def width(self):
    return max([cell.x for cell in self.cells.values()])+1

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


  def simple(self):
    return {
              'white_regions': [region.simple() for region in self.white_regions],
              'black_regions': [region.simple() for region in self.black_regions],
              'cells': [cell.simple() for cell in self.cells.values()]
          }

  def dump(self, filename=LAST_BOARD_FILE):
    with open(filename, 'w') as logfile:
      json.dump(self.simple(), logfile)



  def build(self, grid):
    # Build out model of a new Nurikabe board.
    for y, row in enumerate(grid):
      for x, size_limit in enumerate(row):
        if size_limit == 0:
          self.cells[(x,y)] = Cell(x, y, 0)
        else:
          newCell = Cell(x, y, 1, label=size_limit)
          newRegion = Region(self, 1, newCell, size_limit=size_limit)
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
    for y, row in enumerate(cell_colors):
      for x, color in enumerate(row):
        self.cells[(x,y)] = Cell(x, y, color)
    return self

  def rebuild(self, filename=LAST_BOARD_FILE):
    with open(filename, 'r') as logfile:
      jobj = json.load(logfile)

    self.white_regions = OrderedSet([Region(self, 1, size_limit=region['size_limit']) for region in jobj['white_regions']])
    self.black_regions = OrderedSet([Region(self, 2, size_limit=INF) for region in jobj['black_regions']])
    for region in self.white_regions|self.black_regions:
      region.board = self

    for cell in jobj['cells']:
      new_cell = Cell(*cell['coords'], cell['color'], cell['label'])
      if cell['region_idx'] is not None:
        if new_cell.color == 1:
          new_cell.region = self.white_regions[cell['region_idx']]
        elif new_cell.color == 2:
          new_cell.region = self.black_regions[cell['region_idx']]
        new_cell.region.members.add(new_cell)
      new_cell.potential_regions = {self.white_regions[pri] for pri in cell['p_region_idxs']}
      self.cells[new_cell.coords] = new_cell

    return self
  

  def is_solved(self):
    return all([cell.color for cell in self.cells.values()])













  def set_color(self, color, *cells):
    # Set the color of a Cell and annex any newly-adjacent Regions.
    assert all((cell.color == 0 for cell in cells)), f"Can only set unknown cells. {[cell for cell in cells if cell.color != 0]}"
    assert color != 0, "Can only set color to be black or white."

    for cell in cells:
      cell.color = color
      cell.potential_regions.clear()
      if color == 1:
        cell.label = u"\u2022" # bullet

    for unit in self.gather(cells):
      new_region = Region(self, color, *unit)
      if color == 1:
        self.white_regions.add(new_region)
        for nbor in self.group_neighbors(unit):
          if nbor.color == 0:
            nbor.potential_regions.add(new_region)
      else:
        self.black_regions.add(new_region)
      for nbor in self.group_neighbors(unit):
        if nbor.region is not None and nbor.color == color:
          new_region.annex(nbor.region)

  def neighbors(self, cell, d=1):
    # Get set of Cells that are at most taxicab distance *d* away from *cell*.
    # Excludes *cell*.
    if d<1:
      return set()
    coords = {(cell.x+(n1*(d-i)), cell.y+(n2*i)) for i in range(d+1) for n1 in (1,-1) for n2 in (1,-1)}
    nbors = {self.cells[pos] for pos in coords if 0<=pos[0]<self.width and 0<=pos[1]<self.height}
    return nbors | self.neighbors(cell, d=d-1)

  def group_neighbors(self, group, d=1):
    # Get set of Cells that are at most taxicab distance *d* away from a Cell in *group*.
    # Excludes Cells in *group*.
    return set.union(*(self.neighbors(cell, d=d) for cell in group)) - group

  def squares(self, cell):
    # Return the sets of Cells that make up the four 2x2 squares that include *cell*
    return [
            {cell, self.cells[(cell.x, cell.y+1)], self.cells[(cell.x+1, cell.y)], self.cells[(cell.x+1, cell.y+1)]},
            {cell, self.cells[(cell.x, cell.y+1)], self.cells[(cell.x-1, cell.y)], self.cells[(cell.x-1, cell.y+1)]},
            {cell, self.cells[(cell.x, cell.y-1)], self.cells[(cell.x+1, cell.y)], self.cells[(cell.x+1, cell.y-1)]},
            {cell, self.cells[(cell.x, cell.y-1)], self.cells[(cell.x-1, cell.y)], self.cells[(cell.x-1, cell.y-1)]},
          ]

  def find_pathtree(self, start_unit, region=None, end_unit=None, size_limit=None, color=None):
    if type(start_unit) is Cell:
      start_unit = {start_unit}
    elif type(start_unit) is Region:
      region = start_unit
      start_unit = start_unit.members
    else:
      start_unit = set(start_unit)

    if type(end_unit) is Cell:
      end_unit = {end_unit}
    elif type(end_unit) is Region:
      end_unit = end_unit.members
    else:
      end_unit = set(end_unit)

    if size_limit is None:
      if region is not None:
        size_limit = region.size_limit
      else:
        size_limit = INF

    if color is None:
      color = list(start_unit[0]).color    # color of arbitrary Cell in *start_unit*

    if color == 1:
      return self._find_pathtree_white(start_unit, set(), region, end_unit, size_limit-len(start_unit))


  def _find_pathtree_white(self, start_unit, used, region, end_unit, allowance):
    pt = Pathtree(start_unit)
    if start_unit&end_unit is not set() or allowance<=0:
      return pt

    used = used | start_unit
    nbors = {nbor for nbor in self.group_neighbors(start_unit) if nbor not in used and nbor.color in (0,1)}
    for nbor in nbors:
      new_unit = set.union({nbor}, *(pr.members for pr in nbor.potential_regions-{region}))
      if len(new_unit) <= allowance:
        pt.add_kid(self._find_pathtree_white(new_unit, used, region, end_unit, allowance-len(new_unit)))

    return pt

  def _find_pathtree_black(self, start_unit, used, end_unit):
    pt = Pathtree(start_unit)
    if start_unit&end_unit is not set():
      return pt

    used = used | start_unit
    nbors = {nbor for nbor in self.group_neighbors(start_unit) if nbor not in used}
    for nbor in nbors:
      if nbor.color == 1:
        continue
      elif nbor.color == 0 and any( [all([cell.color==2 or (cell in used) for cell in square-{nbor}]) for square in self.squares(nbor)] ):    # If it is the last unknown cell in a 2x2 square of black or already used cells
          continue
      pt.add_kid(self._find_pathtree_black({nbor}, used, end_unit))

    return pt

  def find_expansions_white(self, region):
    complete_exps = set()
    partial_exps = UniqueQueue([frozenset(region.members)])

    while partial_exps:
      current = partial_exps.pop()
      if len(current) == region.size_limit:
        complete_exps.add(current)
      else:
        for nbor in self.group_neighbors(current):
          potential_regions = nbor.potential_regions-{region}
          if nbor.color != 2 and not any([pr.is_master() for pr in potential_regions]):
            nbor_unit = set.union({nbor}, *(pr.members for pr in potential_regions))
            if len(nbor_unit) + len(current) <= region.size_limit:
              partial_exps.push(current|nbor_unit)

    return [set(exp) for exp in complete_exps]
            


  def gather(self, collection):
    # Group a collection of cells into contiguous sets
    collection = list(collection)
    c_sets = []
    while collection:
      c_set = set()
      to_process = {collection.pop()}
      while to_process:
        current = to_process.pop()
        c_set.add(current)
        for nbor in [n for n in self.neighbors(current) if n in collection]:
          to_process.add(nbor)
      c_sets.append(c_set)
    return c_sets


  def find_reach_white(self, region, open_layer=None, used=None, depth=0, depth_limit=None):
    # Find the reach of *region* to *depth_limit* by adding successive shells of possible cells.
    # Returns set of all Cells that could belong to Region.
    # Should be faster than find_pathtree().union()
    if open_layer is None:
      open_layer = {cell:len(region.members) for cell in set(region.members)}   # the *min_req_size* for *cell* is the number of cells it would take to connect *region* to *cell*, including itself and the cells already in *region*
    if used is None:
      used = set()
    if depth_limit is None:
      depth_limit = region.size_limit - len(region.members)
    if depth >= depth_limit:
      return used|set(open_layer)
    else:
      next_open = {}
      for cell, min_req_size in open_layer.items():
        for nbor in [n for n in self.neighbors(cell) if n not in set(next_open)|set(open_layer)|used]:    # nbors that haven't already been accounted for
          if nbor.color==0 and not any([r.is_master() for r in nbor.potential_regions-{region}]):  # if nbor isn't adjacent to any other regions with defined size_limit (i.e. a separate island)
            connected_cells = {cell for r in nbor.potential_regions-{region} for cell in r.members}|{nbor}
            if len(connected_cells) + min_req_size <= region.size_limit:                          # if this region can annex all regions adjacent to *nbor* w/o violating its size_limit
              for cell in connected_cells:
                next_open[cell] = min(next_open.get(cell, INF), min_req_size+len(connected_cells))
      used.update(open_layer)
      return self.find_reach_white(region, next_open, used, depth+1, depth_limit)









  # INFERENCES

  def create_fences(self):
    # Put black squares between distinct white Regions.
    # Made redundant by find_unreachable.
    for region in self.white_regions:
      for cell in region.members:
        for potential_fence in [pf for pf in self.neighbors(cell) if pf.color==0]:
          for nbor in self.neighbors(potential_fence):
            if nbor.color == 1 and nbor.region != region:
              self.set_color(2, potential_fence)
              print(f"create_fences\t{potential_fence.coords}\tblack")

  def surround_islands(self):
    # Put black squares around finished islands.
    # Made redundant by find_unreachable.
    for region in self.white_regions:
      if region.is_done():
        for cell in region.members:
          for nbor in self.neighbors(cell):
            if nbor.color == 0:
              self.set_color(2, nbor)
              print(f"surround_islands\t{nbor.coords}\tblack")

  def find_unreachable(self):
    # Set all Cells that can't be reached by any islands to black.
    reachable = set()
    for region in [r for r in self.white_regions if r.is_master()]:
      reachable.update(self.find_reach_white(region))
    for cell in set(self.cells.values())-reachable:
      if cell.color == 0:
        self.set_color(2, cell)
        print(f"find_unreachable\t{cell.coords}\tblack")

  def prevent_pools(self):
    # Find any unknown Cells that are part of a 2x2 square where the other Cells are black and set them to white.
    for x in range(self.width-1):
      for y in range(self.height-1):
        square = {self.cells[(x, y)], self.cells[(x, y+1)], self.cells[(x+1, y)], self.cells[(x+1, y+1)]}
        nonblack = [cell for cell in square if cell.color!=2]
        if len(nonblack) == 1 and nonblack[0].color == 0:
          self.set_color(1, nonblack[0])
          print(f"prevent_pools\t\t{nonblack[0].coords}\twhite")

  def expand_white(self):
    # Calculate all the ways that each white island can expand to their size_limit, and then find any Cells that they all have in common and set those to white.
    for region in [r for r in self.white_regions if r.is_master()]:
      if expansions := self.find_expansions_white(region):
        if intersection := set.intersection(*expansions):
          self.set_color(1, *(cell for cell in intersection if cell.color==0))
          print(f"expand_white\t{[cell.coords for cell in intersection]}")


  def solve(self):
    cycles = 0
    while cycles < len(self.cells)+5:
      cycles += 1
      self.find_unreachable()
      self.prevent_pools()
      self.expand_white()
      if self.is_solved():
        break
    else:
      print(f"Unsolved after {cycles} cycles.")
      self.dump()

    print(f"Solved in {cycles} cycles.")
    return self

 

if __name__ == '__main__':
    grid = [
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [3, 0, 0, 2, 0],
          [0, 0, 0, 0, 1],
          [3, 0, 0, 0, 0]
        ]
    b = Board(grid)
    
    b.solve().show()

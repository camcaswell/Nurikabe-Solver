
class Pathtree:

    def __init__(self, unit, parent=None):
        # A unit can be a single cell or a set of contiguous cells in a Region.
        self.unit = unit
        self.parent = parent
        self.kids = set()

    def add_kid(self, new_kid):
        if isinstance(new_kid, Pathtree):
            if new_kid.unit not in {kid.unit for kid in self.kids}:
                self.kids.add(new_kid)
        else:
            if new_kid not in {kid.unit for kid in self.kids}:
                self.kids.add(Pathtree(new_kid, self))
        return self



    # These methods work on the level of the unit/node, NOT on the level of cells

    def get_path(self):
        # Return path from root to here
        if parent is None:
            return (self,)
        else:
            return parent.get_path() + (self,) 

    def get_leaves(self):
        if not self.kids:
            return {self}
        else:
            return set.union(*[kid.get_leaves() for kid in self.kids])

    def intersection(self):
        return set.intersection(*[kid.intersection() for kid in self.kids])|{self}

    def union(self):
        return set.union(*[kid.union() for kid in self.kids])|{self}


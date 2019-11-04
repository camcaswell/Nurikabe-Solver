
class Pathtree:

    def __init__(self, cell, parent=None):
        self.cell = cell
        self.parent = parent
        self.kids = set()

    def add_kid(self, kid):
        self.kids.add(kid)
        kid.parent = self

    def get_path(self):
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


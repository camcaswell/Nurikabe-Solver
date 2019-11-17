from ordered_set import OrderedSet

class UniqueQueue(OrderedSet):

    # LIFO with unique elements
    # Not threadsafe

    def pop(self):
        x = self[0]
        self.remove(x)
        return x

    def push(self, *items):
        for item in items:
            self.add(item)

            
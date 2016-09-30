from user import User

class Graph:
    def resize(self, n):
        if n < len(self.graph):
            raise ValueError()
        for row in self.graph:
            row += [0]*(n - len(row))
        for i in range(n - len(self.graph)):
            graph.append([0 for i in range(n)])

    def __init__(self, n):
        self.graph = [[0 for i in range(n)] for j in range(n)]

    def add(self, origin, target, amount):
        if isinstance(origin, User):
            origin = origin.id
        if isinstance(target, User):
            target = target.id
        self.graph[origin][target] += amount
        self.graph[target][origin] -= amount

    def optimize(self):
        while True:
            optimized = False
            for center in range(len(self.graph)):
                origin = None
                target = None
                for j in range(len(self.graph)):
                    if self.graph[center][j] > 0:
                        target = j
                    if self.graph[center][j] < 0:
                        origin = j
                    if target is not None and origin is not None:
                        amount = min(self.graph[origin][center], self.graph[center][target])
                        self.add(origin, center, -amount)
                        self.add(center, target, -amount)
                        self.add(origin, target, amount)
                        optimized = True
                        break
            if not optimized:
                break


class Debt:
    def __init__(self, origin, target, amount, comment=""):
        self.origin = origin
        self.target = target
        self.amount = amount
        self.comment = comment

    def __str__(self):
        return "{origin} должен {target} {amount}руб {comment}".format(**self.__dict__)
    
    def apply(self, graph):
        graph.add(self.origin, self.target, self.amount)
        graph.optimize()

    def cancel(self, graph):
        graph.add(self.origin, self.target, -self.amount)
        graph.optimize()

class Cheque:
    def __init__(self, payer, participants, value, comment):
        self.payer = payer
        self.participants = participants
        self.value = value
        self.comment = comment

    def __str__(self):
        return "{payer} заплатил за чек с {participants} суммой {value}руб {comment}".format(**self.__dict__)

    def apply(self, graph):
        pass

    def cancel(self, graph):
        pass

class Cancel:
    def __init__(self, operation, comment=""):
        self.operation = operation
        self.comment = comment

    def __str__(self):
        return "отмена операции <{operation}> {comment}".format(**self.__dict__)

    def apply(self, graph):
        self.operation.cancel(graph)

    def cancel(self, graph):
        self.operation.apply(graph)


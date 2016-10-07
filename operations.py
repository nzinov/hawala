from datetime import date
class Operation:
    def __init__(self, user, comment):
        self.user = user
        self.date = str(date.today())
        self.comment = comment

    def message(self):
        return ""

    def __str__(self):
        return "{} {}: {}{}".format(self.user,
                                    self.date,
                                    self.message(),
                                    " ({})".format(self.comment) if self.comment else "")

class Debt:
    def __init__(self, origin, target, amount, user, comment):
        self.origin = origin
        self.target = target
        self.amount = amount
        super(Debt, self).__init__(user, comment)

    def message(self):
        return "{origin} должен {target} {amount}руб".format(**self.__dict__)
    
    def _add(self, context, amount):
        context.graph.add(self.origin, self.target, amount)
        context.graph.optimize()

    def apply(self, context):
        self._add(context, self.amount)

    def cancel(self, context):
        self._add(context, -self.amount)

class Cheque:
    def __init__(self, payer, participants, value, user, comment):
        self.payer = payer
        self.participants = participants
        self.value = value
        super(Cheque, self).__init__(user, comment)

    def message(self):
        return "{payer} заплатил за чек с {participants} суммой {value}руб".format(**self.__dict__)

    def apply(self, graph):
        pass

    def cancel(self, graph):
        pass

class Cancel:
    def __init__(self, operation, user, comment):
        self.operation = operation
        super(Cancel, self).__init__(user, comment)

    def message(self):
        return "отмена операции <{operation}>".format(**self.__dict__)

    def apply(self, graph):
        self.operation.cancel(graph)

    def cancel(self, graph):
        self.operation.apply(graph)


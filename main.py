from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import shelve
from graph import Graph
from user import User
from operations import *
from settings import TOKEN


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_name(name):
    if name[0] == "@":
        return name[1:]
    return name


help_lines = {}
handlers = []


class handler:
    def __init__(self, func):
        self.command = func.__name__
        help_lines[self.command] = func.__doc__
        handlers.append(self.command)
        self.func = func

    def __call__(self, bot, update):
        name = update.message.from_user.username
        user = self.context.users.get(name, name)
        param = update.message.text.split()[1:]
        try:
            reply = list(self.func(self.context, user, *param))
        except (TypeError, ValueError) as e:
            logger.warn(e.args)
            update.message.reply_text("Недопустимые аргументы. Использование: {}".format(help_lines[self.command]))
        else:
            update.message.reply_text("\n".join(reply))
        self.context.shelf.sync()

    def __get__(self, obj, cls):
        self.context = obj
        return self


class Context:
    def __init__(self, shelf):
        self.shelf = shelf
        if not "users" in shelf:
            shelf["users"] = {}
            shelf["log"] = []
            shelf["graph"] = Graph(0)
            shelf.sync()
        self.users = shelf["users"]
        self.log = shelf["log"]
        self.graph = shelf["graph"]
        self.updater = Updater(TOKEN)
        for command in handlers:
            self.updater.dispatcher.add_handler(CommandHandler(command, getattr(self, command)))

    def idle(self):
        self.updater.start_polling()
        self.updater.idle()

    def add_operation(self, operation):
        self.log.append(operation)
        operation.apply(self)
        shelf.sync()

    @handler
    def start(self, user):
        "вступить в Хавалу"
        if isinstance(user, User):
            yield "Вы уже зарегистрированы"
            return
        self.graph.enlarge()
        self.users[user] = User(len(self.users), user)
        yield "Пользователь добавлен!"
        yield "Чтобы получить список команд, пишите /help"

    @handler
    def help(self, user):
        "показать эту справку"
        for command, info in help_lines.items():
            yield "/{} - {}".format(command, info)

    @handler
    def debt(self, user, target, amount, comment=""):
        "записать ваш долг <пользователю> <величиной> рублей с опциональным <комментарием>"
        target = self.users[normalize_name(target)]
        self.add_operation(Debt(user, target, int(amount), user, comment))
        yield 'Готово!'

    @handler
    def show(self, user, count=10):
        "показать последние <число> операций (по умолчанию 10)"
        for el in enumerate(reversed(self.log[-int(count):])):
            yield "{}: {}".format(*el)


    @handler
    def cancel(self, user, number, comment=""):
        "отменить операцию <номер> с конца"
        self.add_operation(Cancel(self.log[-int(number)], user, comment))
        yield 'Отменено!'

    @handler
    def my(self, user):
        "показать ваши долги"
        data = [(name, self.graph.get(user, self.users[name])) for name in self.users]
        yield "Ваши долги:"
        for el in data:
            if el[1] != 0:
                yield "{}: {}".format(*el)

    @handler
    def list(self, user):
        "показать список пользователей"
        yield "Список пользователей:"
        for el in self.users:
            yield str(el)


if __name__ == '__main__':
    shelf = shelve.open("data.db", writeback=True)
    Context(shelf).idle()

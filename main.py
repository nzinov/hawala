from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import shelve
from graph import Graph
from user import User
from operations import *
from settings import TOKEN

shelf = shelve.open("data.db", writeback=True)
if "users" not in shelf:
    shelf["users"] = {}
    shelf["log"] = []
    shelf["graph"] = Graph(0)
    shelf.sync()
USERS = shelf["users"]
LOG = shelf["log"]
GRAPH = shelf["graph"]


def normalize_name(name):
    if name[0] == "@":
        return name[1:]
    return name


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def add_operation(operation):
    LOG.append(operation)
    operation.apply(GRAPH)
    shelf.sync()

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Чтобы получить список команд, пишите /help')


def help(bot, update):
    update.message.reply_text("""/register - вступить в Хавалу
/list - список пользователей
/debt <пользователь> <сумма> -записать, что вы должны
/show - список ваших долгов
/log - журнал операций
/cancel <номер> - отменить операцию""")


def debt(bot, update):
    param = update.message.text.split()
    user = USERS[update.message.from_user.username]
    if len(param) < 3:
        update.message.reply_text('Слишком мало аргументов: /debt <пользователь> <сумма>')
        return
    target = USERS[normalize_name(param[1])]
    add_operation(Debt(user, target, int(param[2])))
    update.message.reply_text('Готово!')


def log(bot, update):
    param = update.message.text.split()
    count = 10
    if len(param) > 1:
        count = int(param[1])
    update.message.reply_text('\n'.join(["{}: {}".format(*el) for el in enumerate(reversed(LOG[-count:]))]))


def cancel(bot, update):
    param = update.message.text.split()
    if len(param) < 2:
        update.message.reply_text('Слишком мало аргументов: /cancel <номер операции>')
        return
    add_operation(Cancel(LOG[-int(param[1])]))
    update.message.reply_text('Отменено!')


def show(bot, update):
    user = update.message.from_user.username
    user = USERS[user]
    data = [(name, GRAPH.get(user, USERS[name])) for name in USERS]
    update.message.reply_text("Ваши долги:\n"+'\n'.join(["{}: {}".format(*el) for el in data if el[1] != 0]))


def register(bot, update):
    user = update.message.from_user.username
    if user in USERS:
        update.message.reply_text('Вы уже зарегистрированы')
        return
    GRAPH.enlarge()
    USERS[user] = User(len(USERS), user)
    update.message.reply_text('Пользователь добавлен!')
    shelf.sync()


def list_users(bot, update):
    update.message.reply_text(', '.join(USERS.keys()))

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("debt", debt))
    dp.add_handler(CommandHandler("log", log))
    dp.add_handler(CommandHandler("cancel", cancel))
    dp.add_handler(CommandHandler("register", register))
    dp.add_handler(CommandHandler("show", show))
    dp.add_handler(CommandHandler("list", list_users))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    print("Start")
    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    shelf.close()


if __name__ == '__main__':
    main()

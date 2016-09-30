from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import shelve
from graph import Graph
from user import User
from operations import *
from settings import TOKEN

shelf = shelve.open("data.db", writeback=True)
if "users" not in shelf:
    shelf["users"] = []
    shelf["ids"] = {}
    shelf["log"] = []
    shelf["graph"] = Graph(0)
    shelf.sync()
USERS = shelf["users"]
IDS = shelf["ids"]
LOG = shelf["log"]
GRAPH = shelf["graph"]

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def add_operation(operation):
    log.append(operation)
    operation.apply(GRAPH)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Чтобы получить список команд, пишите /help')


def help(bot, update):
    update.message.reply_text('Help!')


def debt(bot, update):
    param = update.message.split()
    if len(param) < 4:
        return
    origin, target = [USERS[IDS[el]] for el in param[1:3]]
    add_operation(Debt(origin, target, int(param[3])))
    update.message.reply_text('Готово!')


def log(bot, update):
    param = update.message.split()
    count = 10
    if len(param) > 1:
        count = int(param[1])
    update.message.reply_text('\n'.join(["{}: {}".format(*el) for el in enumerate(LOG[-count:])]))

def cancel(bot, update):
    param = update.message.split()
    if len(param) < 2:
        return
    add_operation(Cancel(LOG[-int(param[1])]))

def show(bot, update):
    param = update.message.split()
    if len(param) < 2:
        return
    user = USERS[IDS[param[1]]]
    update.message.reply_text('\n'.join(["{}: {}".format(USERS[i], GRAPH.graph[user.id][i]) for i in range(len(GRAPH.graph))]))

def add(bot, update):
    param = update.message.split()
    if len(param) < 2:
        return
    GRAPH.resize(len(GRAPH.graph) + 1)
    USERS.append(User(len(USERS), param[1]))

    






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
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("show", show))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    SHELF.close()


if __name__ == '__main__':
    main()

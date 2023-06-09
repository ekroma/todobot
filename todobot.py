import telebot
from telebot import types
from match import match
from datetime import datetime


bot = telebot.TeleBot('Ваш токен') #!


def get_unique_id():
    return datetime.now().strftime("%Y%m%d%H%M%S")

class Task:
    def __init__(self, title, description=None):
        self.id = get_unique_id()
        self.title = title
        self.description = description
        self.status = '✗'

    def __str__(self) -> str:
        return self.title

    def mark_as_complete(self):
        self.status = '✓'


class TodoBot:
    def __init__(self, bot):
        self.bot = bot 
        self.tasks = []
        self.start_handler()

    def start_handler(self):
        @self.bot.message_handler(commands=['start'])
        def start_message(message):
            self.bot.send_message(message.chat.id, 'Привет я TodolistBot помогу тебе с организацией задач\nВыбери действие', reply_markup=self.actions())

        @self.bot.message_handler(content_types=['text'])
        def get_action(message):
            if message.text == 'список задач':
                self.bot.delete_message(message.chat.id, message.id)
                self.list_of_tasks(message.chat.id)

            elif message.text == 'добавить задачу':
                self.bot.delete_message(message.chat.id, message.id)
                self.bot.send_message(message.chat.id, 'Введите задачу')
                self.bot.register_next_step_handler_by_chat_id(message.chat.id, self.create)

        @self.bot.callback_query_handler(func=lambda call: True)
        def task_actions(call):
            action, task_id = call.data.split('*')
            task = self.find_task_by_id(task_id)

            if not task:
                self.bot.send_message(call.message.chat.id, 'Этой задачи нет')

            match action:
                case 'delete':
                    self.tasks.remove(task)
                    self.bot.send_message(call.message.chat.id, 'Задача удалена')
                case 'complete':
                    task.mark_as_complete()
                    self.bot.send_message(call.message.chat.id, 'Задача завершена')
                case 'patch':
                    self.bot.send_message(call.message.chat.id, 'введите изменения')
                    self.bot.register_next_step_handler_by_chat_id(call.message.chat.id, lambda message: self.patch(message, task))


    def find_task_by_id(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def actions(self):
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        add_task = types.KeyboardButton(text='добавить задачу') 
        task_list = types.KeyboardButton(text='список задач')
        return kb.add(add_task,task_list)

    def create(self, message):
        self.tasks.append(Task(message.text))
        self.bot.send_message(message.chat.id, 'Задача добавлена')
        return

    def patch(self, message, task):
        task.title = message.text
        self.bot.send_message(message.chat.id, 'Задача изменена')

    def list_of_tasks(self, message):
        if not self.tasks:
            self.bot.send_message(message, 'Список пуст')
            return

        for i in self.tasks:
            markup_inline = types.InlineKeyboardMarkup(row_width=3)
            complete = types.InlineKeyboardButton(text=f'Завершить', callback_data=f'complete*{i.id}')
            update = types.InlineKeyboardButton(text='Изменить',callback_data=f'patch*{i.id}')
            delete = types.InlineKeyboardButton(text='Удалить', callback_data=f'delete*{i.id}')
            markup_inline.row(complete, update, delete)
            self.bot.send_message(message, f'[{i.status}] {i}',
                reply_markup=markup_inline)

    def start(self):
        self.bot.infinity_polling()


if __name__ == '__main__':
    todo = TodoBot(bot)
    todo.start()
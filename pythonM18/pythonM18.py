import telebot
from extensions import ExchangeException, CurrencyExchange
from config import TOKEN, currency

#создание объекта телеграм-бот
bot = telebot.TeleBot(TOKEN)

# Обрабатываются все сообщения, содержащие команды '/start'.
@bot.message_handler(commands=['start'])
def handle_start(message: telebot.types.Message):
    text=f'Здравствуйте, {message.chat.username}! \n Добро пожаловать в калькулятор обмена валют. \n' \
         f'Для рассчёта обменного курса укажите сообщение в формате \n' \
         f'<валюта продажи> <валюта покупки> <количество> \n' \
         f'Для более детальной информации введите /help'
    bot.send_message(message.chat.id, text)

# Обрабатываются все сообщения, содержащие команды '/help'.
@bot.message_handler(commands=['help'])
def handle_help(message: telebot.types.Message):
    text=f'Для рассчёта обменного курса укажите сообщение в формате \n' \
         f'<валюта продажи> <валюта покупки> <количество> \n' \
         f'Для вывода списка известных мне валют отправьте комманду  /values \n' \
         f'Для вывода таблицы курсов всех валют введите /exchange_rates'
    bot.send_message(message.chat.id, text)

# Обрабатываются все сообщения, содержащие команды '/values'
# Команда выдаёт информацию о всех известных программе валютах.
@bot.message_handler(commands=['values'])
def cur_list(message: telebot.types.Message):
    #проверяем внесение данных о валютах в программу
    if len(currency)==0:
        text = "К сожалению курсы валют мне пока недоступны"
    else:
        text_add=''
        # по каждой из валют, которые внесены в программу, добавляем данные в сообщение
        for key in currency.keys():
            text_add+=f'\n{key} ({currency[key]})'
        # формируем итоговое сообщение
        text = f"Я знаю курсы валют:{text_add}\n Вы можете использовать любой из форматов"
    bot.send_message(message.chat.id, text)

# Обрабатываются все сообщения, содержащие команды '/exchange_rates'
# Команда выдаёт перекрёстные курсы всех известных программе валют.
@bot.message_handler(commands=['exchange_rates'])
def cur_list(message: telebot.types.Message):
    text = "На данный момент курс валют следующий: \n"
    result=''
    try:
        for key1 in currency.keys():
            #перебираем все возможные пары валют за исключением равенства
            for key2 in currency.keys():
                if key1!=key2:
                    #для каждой из пар запускаем обработку get_price
                    # получаем текущий курс и формируем итоговый текст сообщения.
                    result=CurrencyExchange.get_price(key1,key2,1)
                    text=text+f'1{key1} = {result}{key2}\n'
    #в случае возникновения ошибки сообщаем об этом пользователю в телеграм
    # если удалось сделать несколько запросов, то информация о частичном результате
    # будет внесена в сообщение пользователю вместе с сообщением об ошибке
    except ExchangeException:
        if result=='':
            text = ''
        text += ('К сожалению расчёт прерван, возможно проблемы с подключением к серверу')

    bot.send_message(message.chat.id, text)

# Обрабатываются все сообщения с текстом, не содержащие команд
# текст должен содержать информацию о паре валют для обмена и количестве базовой валюты
# валюта запрашивается в любом из двух форматов - название на русском языке и общепринятое сокращение.
@bot.message_handler(content_types=['text', ])
def exchange(message: telebot.types.Message):
    #попытка обработать текстовое сообщение пользователя
    # разбиваем текст на аргументы, проверяем количество,
    # делаем запрос к серверу через обработку get_price,
    # формируем итоговое сообщение с общим курсом и ценой
    # для количества введённого пользователем.
    try:
        args = message.text.split(' ')
        if len(args) != 3:
            raise ExchangeException('Некорректное количество аргументов')
        base, quote, amount = args
        result=CurrencyExchange.get_price(base, quote, amount)
        text = f'1{base} = {result}{quote}\n'
        text += f'{amount}{base} = {round(float(amount) * float(result), 3)}{quote}'
    # обрабатываем возможные ошибки связанные с некорректными входными данными
    # либо ошибки связанные с доступом к серверу.
    except ExchangeException as exception:
        text=(f'Не удалось обработать команду: \n{exception}')
    #обрабатываем возможные ошибки, не учтённые при разработке
    except Exception:
        text=('Что-то пошло не так...')
    #отправляем пользователю итоговое сообщение
    bot.send_message(message.chat.id, text)

bot.polling(none_stop=True)

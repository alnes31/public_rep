import requests
import json
from config import currency

class ExchangeException(Exception):
    pass
# формируем статический метод get_price для получения стоимости валюты
# на вход поступает пара валют в любом из двух форматов и количество.
class CurrencyExchange:
    @staticmethod
    def get_price(base:str,quote:str,amount:str):
        #приводим наименование валюты к виду, который требуется для запроса на сервер
        # если пользователь ввёл название валюты как общепринятое сокращение, то
        # переводим его к виду на русском языке для унификации дальнейшего алгоритма.
        if base in currency.values():
            for key in currency.keys():
                if base == currency[key]:
                    base = key
                    break
        if quote in currency.values():
            for key in currency.keys():
                if quote == currency[key]:
                    quote = key
                    break
        #проверяем, чтобы валюты в паре не совпадали
        if base == quote:
            raise ExchangeException('Валюты обмена не должны совпадать')

        # проверяем, является ли аргумент "количество" числом
        try:
            amount = float(amount)
        except ValueError:
            raise ExchangeException('Некорректно введено количество')
        # отправляем запрос на сервер предварительно проверяя корректно ли ввведены пользователем данные о валютах
        if (base in currency.keys()) and (quote in currency.keys()):
            #отслеживаем ошибки связанные с работой сервера
            try:
                r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={currency[base]}&tsyms={currency[quote]}')
            except requests.exceptions.ConnectionError:
                raise ExchangeException('Проблемы с соединением, попробуйте чуть позже')
        else:
            raise ExchangeException('Не удалось распознать валюту')
        #формируем итоговый результат
        return json.loads(r.content)[currency[quote]]

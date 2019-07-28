# WordstatCrawler

Сбор статистики с Wordstat.

Непосредственно парсером является class Browser(webdriver.Firefox) в файле browser.py.
Пример использования класса Browser:

driver = Browser();
driver.yandexLogin(user, pswd) # Логин и пароль яндекса
driver.getRelatedRequestsFromYandex(addwords, count=10) # Получим 10 страниц связанных запросов из wordstat
driver.close() # Обязательный момент. Если не закрыть вебдрайвер, то браузер будет висеть в памяти и его придется убивать.

Сбор статистики запросов выполняет class Collector в файле key_stat_collector.py
Пример использования класса Collector:
Сбор запросов по поднишам.

coll = Collector();
coll.collectAll();

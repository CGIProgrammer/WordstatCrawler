from selenium import webdriver
import time
import base64, requests
from random import choice
from lxml import html, etree
import json
from threading import Thread
from pytrends.request import TrendReq


# Антикапча
class Anticaptcha:
    __results = {}
    
    def __init__(self, key):
        self.__api_key = key
        self.__url = "https://api.anti-captcha.com/"    # Адрес вызова методов API
        self.__ct = "createTask"                        # Метод создания задачи
        self.__gtr = "getTaskResult"                    # Метод получения результата выполнения задачи
        self.__taskID = 0                               # ID задачи
        self.__imageUrl = ""                            # URL изобржения с капчей
    '''
        Создание задачи
        на вход даётся url картики с капчей
    '''
    def createTask(self, url):
        self.__imageUrl = url
        if url in Anticaptcha.__results:
            return
        Anticaptcha.__results[self.__imageUrl] = ""
        with requests.get(url, stream=True) as r:
            # Кодирование изображения в base64 для передачи в текстовом виде
            data = base64.b64encode(r.content).decode()
            # Форма создания задачи
            '''
                АХТУНГ! Не работает утановка русского языка. Информация о том, как его правильно задать, есть
                но наличие RU в структуре не помогает. Антикапча кидается в том числе людям, не имеющим русскую раскладку.
                Странно: иногда люди, не имеющие русской раскладки, вводят какие-то похожие кракозяабры и яндекс это засчитывает.
                Но иногда нет. В итоге антикапча срабатывает где-то в 60-70 % случаев.
            '''
            struct = {
                "clientKey" : self.__api_key,
                "task": {
                    "type": "ImageToTextTask",  # Тип задачи
                    "body": data,               # Изображение
                    "phrase": False,            # Фраза (ХЗ, что значит)
                    "case": True,               # Важен ли регистр
                    "numeric": False,           # Состоит ли капча только из цифр
                    "math": 0,                  # Предствляет ли капча математическую или арифметическую задачу.
                    "minLength": 0,             # Минимальная длина
                    "maxLength": 0              # Максимальная длина
                }
            }
            response = requests.post(self.__url + self.__ct, json=struct).json() # Отправка формы задачи
            if response['errorId']==0:
                self.__taskID = response['taskId']
            else:
                self.__taskID = -1
    
    '''
        Проверка выполнения задачи
    '''
    def getTaskResult(self):
        if self.__taskID == 0:
            return "not started"
        elif self.__taskID == -1:
            return "failed"
        elif Anticaptcha.__results[self.__imageUrl]:
            return "ready"
        else:
            struct = {
                "clientKey": self.__api_key,
                "taskId": self.__taskID
            }
            with requests.post(self.__url + self.__gtr, json=struct) as r:
                json = r.json()
                try:
                    Anticaptcha.__results[self.__imageUrl] = json["solution"]["text"]
                except:
                    Anticaptcha.__results[self.__imageUrl] = json['errorId']
                return json['status']
            return "connection failed"
        
    def getResult(self):
        return Anticaptcha.__results[self.__imageUrl]
    
    '''
        Ожидание получения ответа
        Метод возвращает результат, полученный с сервиса антикапчи
    '''
    def join(self):
        response = self.getTaskResult()
        while response=="processing":
            response = self.getTaskResult()
        return self.getResult()

'''
    Собственно парсер
'''
class Browser(webdriver.Firefox):
    ''' Множество регионов России '''
    russia = {
            "Республика Адыгея",
            "Республика Башкортостан",
            "Республика Бурятия",
            "Республика Алтай",
            "Республика Дагестан",
            "Республика Ингушетия",
            "Кабардино-Балкарская Республика",
            "Республика Калмыкия",
            "Карачаево-Черкесская Республика",
            "Республика Карелия",
            "Республика Коми",
            "Республика Марий Эл",
            "Республика Мордовия",
            "Республика Саха (Якутия)",
            "Республика Северная Осетия — Алания",
            "Республика Татарстан",
            "Республика Тыва",
            "Удмуртская Республика",
            "Республика Хакасия",
            "Чеченская Республика",
            "Чувашская Республика - Чувашия",
            "Алтайский край",
            "Краснодарский край",
            "Красноярский край",
            "Приморский край",
            "Ставропольский край",
            "Хабаровский край",
            "Амурская область",
            "Архангельская область",
            "Астраханская область",
            "Белгородская область",
            "Брянская область",
            "Владимирская область",
            "Волгоградская область",
            "Вологодская область",
            "Воронежская область",
            "Ивановская область",
            "Иркутская область",
            "Калининградская область",
            "Калужская область",
            "Камчатский край",
            "Кемеровская область",
            "Кировская область",
            "Костромская область",
            "Курганская область",
            "Курская область",
            "Ленинградская область",
            "Липецкая область",
            "Магаданская область",
            "Московская область",
            "Мурманская область",
            "Нижегородская область",
            "Новгородская область",
            "Новосибирская область",
            "Омская область",
            "ренбургская область",
            "Орловская область",
            "Пензенская область",
            "Пермский край",
            "Псковская область",
            "Ростовская область",
            "Рязанская область",
            "Самарская область",
            "Саратовская область",
            "Сахалинская область",
            "Свердловская область",
            "Смоленская область",
            "Тамбовская область",
            "Тверская область",
            "Томская область",
            "Тульская область",
            "Тюменская область",
            "Ульяновская область",
            "Челябинская область",
            "Забайкальский край",
            "Ярославская область",
            "Москва и Московская область",
            "Санкт-Петербург",
            "Еврейская автономная область",
            "Ненецкий автономный округ",
            "Ханты-Мансийский автономный округ - Югра",
            "Чукотский автономный округ",
            "Ямало-Ненецкий автономный округ",
            "Республика Крым",
            "Севастополь"
        }
    
    def __init__(self, *args, **kwargs):
        webdriver.Firefox.__init__(self, *args, **kwargs)
        self.__url = 'https://wordstat.yandex.ru/#!/?words='
        self.implicitly_wait(0)
    
    '''
        Отправка капчи на сервис антикапчи
    '''
    def __get_token(self, url):
        print("__get_token");
        ac = Anticaptcha("94262e1ba10430ace76525b13af6d2a4")
        ac.createTask(url)
        return ac.join()
    
    '''
        Ожидание спинера загрузки результатов
        Пока он не закончит крутиться, нужные данные на странице не появятся
    '''
    def __waitForSpinner(self, timeout = 10):
        captcha = False
        t1 = time.time()    # Засекаем время
        
        # Ждём пока спинер не скроется или не выйдет время
        while time.time()-t1<timeout and self.find_element_by_xpath('//div[@class = "b-popupa__spin-block"]').is_displayed():
            if not captcha:
                captcha = self.checkCaptcha()   # Проверка капчи, мало ли выдаст сразу после спинера. Всякое бывает.
            time.sleep(0.3)
    
    '''
        Ожидание появления элементов, удовлетворяющих заданному xpath.
        Внимание!!! Возвращает не элемент вебдрайвера, а элемент lxml.html. Клики и ввод не поддерживаются
        Это было сделано для ускорения. Функции поиска, имеющиеся в вебдрайвере работают медленно.
    '''
    def __waitForElements(self, xpath, timeout = 10):
        element = []
        t1 = time.time()
        while time.time()-t1<timeout and element==[]:
            element = self.find_elements_by_xpath(xpath)
            time.sleep(0.3)
        return element

    '''
        То же, что __waitForElements, только чисто для yandex wordstat
    '''
    def __waitForWordstatElement(self, xpath, timeout = 10):
        self.__waitForSpinner(timeout)
        element = []
        captcha = False
        t1 = time.time()
        while time.time()-t1<timeout and element==[]:
            if not captcha:
                captcha = self.checkCaptcha()
                # Если элемент существует, но спинер ещё крутится, то в этом элементе могут содержаться устаревшие данные
                self.__waitForSpinner(timeout)
            tree = html.fromstring(self.page_source)
            element = tree.xpath(xpath)
            time.sleep(0.3)
        return element
    
    '''
        Функция проверки капчи с ожиданием, вводом и повторными попытками в случае неудачи
    '''
    def checkCaptcha(self):
        # Находим рамку, в которой находится капча
        captchaFrame = self.find_elements_by_xpath('//div[contains(@class, "b-page__captcha-popup")]')
        t = time.time()
        url = ""
        # Если таковая найдена
        if captchaFrame:
            # Ищем изображение с капчей
            img = captchaFrame[0].find_element_by_xpath('//img[@class = "b-popupa__image"]')
            # и достаём её url
            url = img.get_property('src');
            if url:
                print('Waiting for solving captcha ' + url)
                
                # Находим поле ввода капчи по xpath
                # Данный xpath можно скопировать взять через браузер в режиме исследования элемента
                entry = "/html/body/div[7]/div/div/table/tbody/tr/td/div/form/table/tbody/tr[2]/td[1]/span/span/input"
                entry = self.find_element_by_xpath(entry)
                
                # На некоторые текстовые поля нудно кликнуть перед вводом.
                # Это как раз тот самый случай
                if entry.is_displayed():
                    entry.click()
                else:
                    return True
                
                # Заказываем распознавание капчи
                cappcha = str(self.__get_token(url))
                # Вводим её
                entry.send_keys(cappcha)
                
                # Ищем по xpath кнопку ввода капчи и кликаем на неё
                button = self.find_elements_by_xpath('/html/body/div[7]/div/div/table/tbody/tr/td/div/form/table/tbody/tr[2]/td[2]/span')
                while button==[]:
                    time.sleep(0.5)
                    button = self.find_element_by_xpath('/html/body/div[7]/div/div/table/tbody/tr/td/div/form/table/tbody/tr[2]/td[2]/span')
                button[0].click()
                
                time.sleep(2)
                # Если, после небольшого ожидания, капча ещё не исчезла, значит её ввели неправильно.
                if button[0].is_displayed():
                    # Заказываем по новой
                    self.checkCaptcha()
                
                # Здесь капча уже должна быть решена
                print('Captcha solved', time.time()-t, "с.")
                return True
        return False
    
    '''
        Кликает по элементу, найденному по xpath
    '''
    def clickElementByXpath(self, path):
        #t1 = time.time()
        #time.sleep(0.5)
        element = self.find_element_by_xpath(path)
        element.click()
        return
    
    '''
        Вводит текст в элемент, найденный по xpath
    '''        
    def enterTextByXpath(self, path, text):
        el = self.find_element_by_xpath(path)
        el.clear()
        el.send_keys(text)
    
    '''
        Регистрирует аккаунт Google (не работает, всё упирается в номер телефона)
    '''
    def registerGoogleAccount(self):
        self.get("https://accounts.google.com/signup/v2/webcreateaccount?&gmb=exp&biz=false&flowName=GlifWebSignIn&flowEntry=SignUp")
        first_name = self.find_element_by_xpath('//*[@id="firstName"]')
        last_name  = self.find_element_by_xpath('//*[@id="lastName"]')
        user_name  = self.find_element_by_xpath('//*[@id="username"]')
        passwords  = self.find_elements_by_xpath('//input[@type="password"]')
        
        first_name.send_keys("Поджог")
        last_name.send_keys("Сараев")
        user_name.send_keys("asdklasdjf")
        passwords[0].send_keys("lolkekcheburek")
        passwords[1].send_keys("lolkekcheburek")
        self.clickElementByXpath('//*[@id="accountDetailsNext"]')
    
    '''
        Получение статистики по регионам от Google
        Google даёт статистику с момента начала её сбора.
    '''
    def getGtrendsHistoryStat(self, request, country='ru_RU'):
        pytrends = TrendReq(hl=country, tz=360, timeout=(10,25),
                            #proxies=['https://34.203.233.13:80',],
                            retries=2, backoff_factor=0.4)
        pytrends.build_payload(kw_list=[request])
        interest_over_time_df = pytrends.interest_over_time()
        result = {}
        for k,v in interest_over_time_df:
            k = '{}-{}-{}'.format(str(k.year),str(k.month),str(k.day))
            result[k] = {}
            result[k]['absulute'] = v
        return interest_over_time_df[request]
    
    '''Получение статистики по регионам от Google (не даёт относительную популярность)'''
    def getGtrendsRegionalStat(self, request, country='ru_RU'):
        pytrends = TrendReq(hl=country, tz=360, timeout=(10,25),
                            #proxies=['https://34.203.233.13:80',],
                            retries=2, backoff_factor=0.4)
        pytrends.build_payload(kw_list=[request])
        interest_by_region_df = pytrends.interest_by_region()
        result = []
        for k,v in interest_by_region_df.items():
            result.append({
                'region' : k,
                'count'  : v
                })
        return result
    
    '''
        Вход в яндекс, через страницу wordstat
        Через другие страницы будет другая форма
    '''
    def yandexLogin(self, user, pswd):
        self.get("http://wordstat.yandex.ru")
        self.clickElementByXpath('//td[contains(@class, "b-head-userinfo__entry")]')
        self.enterTextByXpath('//*[@id="b-domik_popup-username"]', user)
        self.enterTextByXpath('//*[@id="b-domik_popup-password"]', pswd)
        self.clickElementByXpath("/html/body/form/table/tbody/tr[2]/td[2]/div/div[5]/span[1]")
        time.sleep(2.0)
        self.checkCaptcha()
    
    '''
        Регистрация аккаунта yandex
    '''
    def registerYandexAccount(self, name1, name2):
        def randomWord(length):
            charSet = "abcdefghijklmnopqrstuvwxyz"
            charSet += charSet.upper()# + "0123456789"
            result = ""
            for i in range(length):
                result += choice(charSet)
            return result
        
        langSwitcherPath = '//span[@class = "footer-item footer-item__langswitcher"]'
        langEngPath = '//a[@class = "control menu__item menu__item_type_link" and contains(@href, "set/lang")]'
        
        # Пути к нужным элементам
        # Пути к надписи нужны для кликов по надписям. Ввод в эту форму можно выполнить только после нажатия на надпись, которая находится поверх поля ввода.
        firstnamePath = '//input[@id = "firstname"]'  # Путь к полю имени
        firstnameLabelPath = '//label[@class = "registration__label" and @for = "firstname"]'   # Путь к надписи "Имя"
        lastnamePath = '//input[@id = "lastname"]'    # Путь к полю фамилии
        lastnameLabelPath = '//label[@class = "registration__label" and @for = "lastname"]'   # Путь к надписи "Фамилия"
        loginPath = '//input[@id = "login"]'          # Путь к полю логина
        loginLabelPath = '//label[@class = "registration__label" and @for = "login"]'   # Путь к надписи "Логин"
        password1Path = '//input[@id = "password"]'   # Путь к полю пароля
        password1LabelPath = '//label[@class = "registration__label" and @for = "password"]'   # Путь к надписи "Пароль"
        password2Path = '//input[@id = "password_confirm"]' # Путь к полю подтверждения пароля
        password2LabelPath = '//label[@class = "registration__label" and @for = "password_confirm"]'   # Путь к надписи "Подтверждение пароля"
        noPhonePath = '//span[@class = "toggle-link link_has-no-phone"]'    # Путь к кнопке выбора регистрации без телефона
        selectQuestionPath = '//button[@class = "control button2 button2_view_classic button2_tone_default button2_size_m button2_theme_normal control-questions button2_width_max select2__button"]'   # Путь к кнопке выбора секретного вопроса
        customQuestionButtonPath = '//span[@class = "menu__text" and contains(., "question")]'  # Путь к пункту
        customQuestionEntryPath  = '//input[@id = "hint_question_custom"]'   # Путь к полю ввода секретного вопроса
        customQuestionLabelPath  = '//label[@class = "registration__label" and @for = "hint_question_custom"]'   # Путь к кнопке
        answerEntryPath = '//input[@id = "hint_answer"]'   # Путь к полю ответа на вопрос
        answerLabelPath = '//label[@class = "registration__label" and @for = "hint_answer"]'   # Путь к надписи "Ответ"
        captchaPath = '//input[@id = "captcha"]'       # Путь к блоку капчи
        captchaLabelPath = '//label[@class = "registration__label" and @for = "captcha"]'   # Путь к надписи поверх ввода капчи
        captchaImgPath = '//img[@class = "captcha__image" and contains(@src, "https://ext.captcha.yandex.net/image")]'   # Путь к элементу изображения с капчей
        
        # Секретный вопрос
        question = randomWord(20)
        
        # Не менее секретный ответ
        answer = randomWord(10)
        
        # Генерация пароля
        password = randomWord(10)
        
        # Генерация логина
        login = randomWord(15)
        
        # Сохранение данных аккаунта
        fp = open('accounts/%s.txt' % (name1 + '_' + name2), 'w')
        print('Пользователь:', login, file = fp)
        print('Имя:', name1, file = fp)
        print('Фамилия:', name2, file = fp)
        print('Пароль:', password, file = fp)
        print('Вопрос:', question, file = fp)
        print('Ответ:', answer, file = fp)
        fp.close()
        
        # Переход на страницу регистрации аккаунта
        self.get("https://passport.yandex.ru/registration?mode=register&from=&retpath=https%3A%2F%2Fwordstat.yandex.ru%2F&twoweeks=yes")
        # Переключение яндеска на английский язык. Нужно для выдачи английской капчи.
        self.clickElementByXpath(langSwitcherPath)
        self.clickElementByXpath(langEngPath)
        self.get("https://passport.yandex.ru/registration?mode=register&from=&retpath=https%3A%2F%2Fwordstat.yandex.ru%2F&twoweeks=yes")
        
        self.clickElementByXpath(noPhonePath);
        try:
            self.clickElementByXpath(noPhonePath);
        except:
            pass
        time.sleep(0.25)
        # 
        self.clickElementByXpath(firstnameLabelPath); self.enterTextByXpath(firstnamePath, name1)
        self.clickElementByXpath(lastnameLabelPath); self.enterTextByXpath(lastnamePath, name2)
        self.clickElementByXpath(loginLabelPath); self.enterTextByXpath(loginPath, login)
        self.clickElementByXpath(password1LabelPath); self.enterTextByXpath(password1Path, password)
        self.clickElementByXpath(password2LabelPath); self.enterTextByXpath(password2Path, password)
        self.clickElementByXpath(selectQuestionPath);
        self.clickElementByXpath(customQuestionButtonPath);
        self.clickElementByXpath(customQuestionLabelPath); self.enterTextByXpath(customQuestionEntryPath, question)
        self.clickElementByXpath(answerLabelPath); self.enterTextByXpath(answerEntryPath, answer)
        curl = self.find_element_by_xpath(captchaImgPath).get_attribute("src")
        self.clickElementByXpath(captchaLabelPath); self.enterTextByXpath(captchaPath, self.__get_token(curl))
        self.clickElementByXpath('//button[@class = "control button2 button2_view_classic button2_size_l button2_theme_action button2_width_max button2_type_submit js-submit"]')

    
    '''
        Получение статистики по времени. Яндекс требует капчу при первом вызове.
        Антикапча подключена.
    '''
    def getStatHistory(self, kwords):
        self.get("https://wordstat.yandex.ru/#!/history?words="+kwords)
        tables = self.__waitForWordstatElement('//table[@class = "b-history__table"]')
        
        table1 = tables[0].xpath('//tr[@class = "odd" or @class = "even"]')
        table2 = tables[1].xpath('//tr[@class = "odd" or @class = "even"]')
        
        result = {}
        
        for row in table1 + table2:
            line = {}
            line['absolute'] = int(''.join([i.text for i in row[2]]))
            line['relative'] = float(''.join([i.text for i in row[3]]).replace(",", "."))
            result[row[0].text.replace("\xa0-\xa0", ' - ')] = line
            
        return result
    
    '''
        Получение статистики по регионам
    '''
    def getStatByRegions(self, kwords):
        self.get("https://wordstat.yandex.ru/#!/regions?filter=regions&words="+kwords)
        self.checkCaptcha()
        
        result = []
        t1 = time.time()
        cells = self.__waitForWordstatElement('//td[contains(@class, "b-regions-statistic__td")]')
        
        for el in range(3, len(cells), 3):
            props = cells[el:el+3]
            region  = props[0].text
            count   = int(props[1].text.replace(' ', ''))
            percent = float(props[2].text[:-1].replace(' ', ''))/100
            
            # Инорируем города, нужны толко области, республики, края и т.д.
            if region in Browser.russia:
                result.append({
                    'region'  : region,
                    'percent' : percent,
                    'count'   : count
                })
        print('Get regions data in', time.time() - t1, 'seconds')
        
        return result
    
    # Получить похожие запросы из яндекса
    def getLikeRequestsFromYandex(self, kwords):
        rqs = []
        self.get("https://wordstat.yandex.ru/#!/?words="+kwords)
        table = self.__waitForWordstatElement("//div[@class = 'b-word-statistics__column b-word-statistics__phrases-associations']")
        rows = table[0].xpath('//tr[contains(@class, "b-word-statistics__tr")]')
        for row in rows[1:-1]:
            try:
                request = row[0][0][0].text
            except:
                break
            rqs.append(request)

        return rqs
    
    # Получить связаные запросы из яндекса
    def getRelatedRequestsFromYandex(self, kwords, count = 1, start = 1):
        rqs = []
        for i in range(start,count+1):
            self.get("https://wordstat.yandex.ru/#!/?page=" + str(i) + "&words="+kwords)
            table = self.__waitForWordstatElement("//table[@class = 'b-word-statistics__table']")
            try:
                rows = table[0].xpath('//tr[contains(@class, "b-word-statistics__tr")]')
            except:
                break
            for row in rows[1:-1]:
                #print(row)
                try:
                    request = row[0][0][0].text
                except:
                    break
                rqs.append(request)
            if len(rows[1:-1])<40:
                break
        return rqs
    
    # Сохранить связаные запросы в файл
    def saveRelatedRequestsFromYandex(self, fname, kwords, count = 1, start = 1):
        fp = open(fname, 'w')
        for i in range(start,count+1):
            self.get("https://wordstat.yandex.ru/#!/?page=" + str(i) + "&words="+kwords)
            table = self.__waitForWordstatElement("//table[@class = 'b-word-statistics__table']")
            try:
                rows = table[0].xpath('//tr[contains(@class, "b-word-statistics__tr")]')
            except:
                break
            rqs = []
            for row in rows[1:-1]:
                #print(row)
                try:
                    request = row[0][0][0].text
                except:
                    break
                rqs.append(request)
            if len(rows[1:-1])<40:
                break
            fp.write('\n'.join(rqs))
            fp.flush()
        fp.close()
    '''
        Получить подкатегории товаров из Avito (работает неправильно)
    '''
    def __getAvitoSubcategories(self, url):
        r = requests.get(url)
        page = html.fromstring(r.text)
        root = page.xpath('//div[contains(@class, "rubricator-root")]')[0]
        items = root.xpath("//li[contains(@class, 'rubricator-item')]")
        root_title = root.xpath('ul/li/div/a')[0].text
        root = root.xpath('ul/li')[0]

        result = {'name' : root_title}

        for item in items:
            var = item.xpath('div/a')[0]
            if item.getparent().getparent() == root:
                print(var.get('title'))
                src = etree.tostring(item)
                item = html.fromstring(src)
                #print(src)
                subitems = item.xpath("//a[contains(@class, 'rubricator-link')]")
                #print(subitems)
                for var2 in subitems:
                    #result[var.get('title')] = var2.get('title')
                    print(var.get('title') + '\t' + var2.get('title'))
                    
        return result
    
    '''
        Получить категории товаров из Avito (работает неправильно из-за __getAvitoSubcategories)
    '''
    def getAvitoCategories(self):
        r = requests.get('https://avito.ru')
        page = html.fromstring(r.text)
        #cat_list = page.xpath('//div[@class = "search-form__category"]')
        cat_list = page.xpath('//a[@class = "simple-with-more-rubricator-header-categories-all__link-k_Jr3 js-header-categories-all__link"]')
        result = {}
        for i in cat_list[1:]:
            if i.xpath('text()'):
                url = 'https://www.avito.ru' + i.get('href')
                name = i.xpath('text()')[0]
                values = list(result.values())
                li = self.__getAvitoSubcategories(url)
                if li not in values:
                    print(name)
                    result[name] = li
                time.sleep(1.0)
        return result
    
    '''
        Получает категории из яндекс маркета (Работает через раз)
    '''
    def getYandexMarketCategories(self):
        self.get("https://market.yandex.ru/")
        time.sleep(2.0)
        
        region = self.find_element_by_xpath("//div[@class = 'n-region-notification__actions-cell']")
        region.click()
        time.sleep(1.0)
        categories = self.find_element_by_xpath("//div[@class = 'n-w-tab n-w-tab_interaction_click-navigation-menu n-w-tab_type_navigation-menu-grouping i-bem n-w-tab_js_inited n-w-tab_interaction-active_no']")
        categories.click()
        time.sleep(2.0)
        
        column = self.find_element_by_xpath("//div[@class = 'n-w-tabs__tabs-column']")
        categories = column.find_elements_by_xpath("//a[@class = 'link n-w-tab__control b-zone b-spy-events']")
        
        cats = {}
        
        for i in categories:
            cats[i.text] = {}
            cats[i.text]['url'] = i.get_attribute('href')
        
        for k,v in cats.items():
            print(k)
            url = v['url']
            v['subcats'] = {}
            self.get(url)
            mores = self.find_elements_by_xpath('//span[contains(., "Ещё")]')
            for m in mores:
                m.click()
                #time.sleep(0.5)
            column = self.__waitForElements('//div[@data-apiary-widget-name="@MarketNode/NavigationTree"]', 20)
            if len(column)==0: continue
            column = column[0]
            #print(column.find_element_by_xpath('div/div/div/div/div/div/div/a').text)
            subcats = column.find_elements_by_xpath('div/div/div/div/div/div[*]')
            i = 0
            while i < len(subcats):
                subcats = column.find_elements_by_xpath('div/div/div/div/div/div[*]')
                subcat = subcats[i]
                sc_name = subcat.find_element_by_xpath("div/a").text
                v['subcats'][sc_name] = []
                print(sc_name)
                for line in subcat.find_elements_by_tag_name('li'):
                    if line.text != "Все товары":
                        v['subcats'][sc_name].append(line.text)
                        print('\t', line.text)
                i += 1
        
        result = {}
        
        for k,v in cats.items():
            result[k] = v['subcats']        
        
        return result
    
import os,sys
# Режим демона (без графики). Закомментировать ели нужна отладка
#os.environ['MOZ_HEADLESS'] = '1'
keywords = set()

di = {}
di['transaction'] = 'Дорогой', 'Купля', 'Купить','Куплю','Покупка','Скупка','Продать','Продам','Заказать','отзыв','аналог','Заказ','Приобрести','Оплатить','Оплата','Арендовать','Доставка','Доставить','Прокат','В кредит','Кредит','Рассрочка','Бронирование','Бронь','Забронировать','Оформить','Оформление','Нанять','Услуги','Вызов','Вызвать'
di['commerce'] = 'Продажа','Цена','Стоимость','Сколько стоит','Дорого','Под ключ','Недорого','нужен','Дешево','Премиум','Люкс','VIP','вип','Распродажа','Дисконт','Sale','Прайс','Тариф','Опт','Оптовый','В наличии','Бюджетный','Скидки','Скидочный','Акции','Акционный','заявка'
di['time'] = 'Срочно','Быстро','Сегодня','Сейчас','За час'
di['place'] = 'онлайн', 'ИП','ЗАО', 'ООО', 'АО', 'ОАО', 'ЗАО', 'адрес', 'Официальный', 'Магазин','Интернет-магазин','Агентство','Бюро','Студия','Производитель','Фирма','Организация','Компания','Фабрика','Завод','Сайт'
di['first_step'] = 'Консультация','Замер','Расчёт','Рассчитать','Калькулятор','Тестовый','Пробный','Пробник','Оценка'
di['stores'] = 'aliexpress','алиэкспресс','авито','avito','с рук','eldorado','эльдорадо','стим','steam','origin','store','amazon','амазон', 'юла'

# Проверка ключевого запроса
def checkKey(key):
    key = key.lower().replace('интернет магазин', 'интернет-магазин')
    key = key.replace('б у', 'б/у')
    badwords = {"эзотерика","шутка","юмор","прикол","забава","анекдот","экстрасенс","таро","мистика","магия","нло","гадание","гомеопатия","астрология","тайна","праздник","загадка","суть","скачать","смотреть","слово","встреча","цвет","что","сколько","почему","как"}
    addwords = [i.lower() for i in di['transaction'] + di['commerce'] + di['time'] + di['place'] + di['first_step'] + di['stores']]
    
    for i in range(len(addwords)):
        if addwords[i].find(' ')>-1:
            k1 = addwords[i]
            k2 = addwords[i].replace(' ', '_')
            addwords[i] = k2
            key = key.replace(k1, k2)
    
    words = key.split()
    for i in words:
        if i.strip('+').strip('-') in badwords:
            return False
    if len(key.split())>4: return False
    cnt = 0
    for i in words:
        if i.strip('+').strip('-') in addwords:
            cnt += 1
    return cnt>0 and len(words)-cnt<=3

# Функция потока
def threadFun(keys, name):
    addwords  = '({})'.format('|'.join(keys))   # Формирование списка продающих добавок
    user = "serzhant.nalivaiko@yandex.ru"   # Логин
    pswd = 'lolkekcheburek'                 # Пароль
    driver = Browser()                      # Запуск браузера
    driver.yandexLogin(user, pswd)          # Вход в аккаунт
    print('starting', name)
    results = set()                         # Запросы
    
    r = [i for i in driver.getRelatedRequestsFromYandex(addwords, count=10) if checkKey(i)]
    results |= set(r)
    results |= set(driver.getLikeRequestsFromYandex(addwords))
    
    rs = list(results)
    contin = 0
    
    fp = open(name,'w')
    
    pages = 0
    
    for i in list(r):
        print(i, file=fp)
    fp.flush()
    
    # Запуск цикла сбора ключевых
    while 1:
        for r in rs:
            # Берём связаные и похожие запросы с яндекса
            try:
                page  = {i for i in driver.getRelatedRequestsFromYandex(r, count=10)[1:] if checkKey(i)}
                page |= {i for i in driver.getLikeRequestsFromYandex(r) if len(i.split())<=3}
            except:
                # Если не получилось, перезапустить драйвер и снова попытаться взять запросы
                print('Error occured: reset driver')
                driver.close()
                driver = Browser()
                driver.yandexLogin(user, pswd)
                page  = {i for i in driver.getRelatedRequestsFromYandex(r, count=10)[1:] if checkKey(i)}
                page |= {i for i in driver.getLikeRequestsFromYandex(r) if len(i.split())<=3}
                
            pages += 1
            for i in list(page):
                if i not in results:
                    print(i, file=fp)
            results |= page
            fp.flush()
            # Драйвер со временем потребляет всё больше и больше ОЗУ. Время от времени его надо перезапускать
            if pages>20:
                driver.close()
                driver = Browser()
                driver.yandexLogin(user, pswd)
                pages = 0
        
        # Создание списка для цикла с исключением уже пройденных запросов
        rs = list(results)[len(rs):]
     
    fp.close()
    driver.close()

def main():
    t1 = time.time()
    
    threads = []
    for k,v in di.items():
        threads.append(Thread(target=threadFun, args=(v, k+'.txt')))
        threads[-1].start()
    
    for t in threads:
        t.join()
    
    
if __name__ == '__main__':
    main()

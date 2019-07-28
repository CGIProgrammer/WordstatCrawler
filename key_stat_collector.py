import sqlite3
import browser
from threading import Thread, active_count
import time

class Collector:
    def __init__(self, login, password):
        self.__dbase = sqlite3.connect('UN_categories.sqlite')
        self.__cursor = self.__dbase.cursor()
        self.__login = login
        self.__password = password
    
    '''Передать изменения в базу данных'''
    def commit(self):
        self.__dbase.commit()
    
    '''Получить подниши, относящиеся к отрасли'''
    def getSubniches(self, industry=None):
        if industry:
            self.__cursor.execute('SELECT s.id, s.name FROM sections_relations r INNER JOIN sections s WHERE s.id=r.node_id and r.level=3 and r.parent_id="{}";'.format(industry))
        else:
            self.__cursor.execute('SELECT s.id, s.name FROM sections_relations r INNER JOIN sections s WHERE s.id=r.node_id and r.level=3;')
        return list(set(self.__cursor.fetchall()))
    
    '''Получить отрасли'''
    def getIndustries(self):
        self.__cursor.execute('SELECT s.id, s.name FROM sections_relations r INNER JOIN sections s WHERE s.id=r.parent_id and r.level=1;')
        return list({i for i in self.__cursor.fetchall() if not i[0].isdigit()}).sort()
    
    '''Добавить запрос'''
    def addRequest(self, request, section):
        try:
            self.__cursor.execute('INSERT INTO requests(request, section) VALUES("%s", "%s");' % (request, section))
            self.__dbase.commit()
        except:
            pass
    
    '''Получить запросы по поднише'''
    def getRequests(self, section):
        self.__cursor.execute('SELECT request FROM requests WHERE section="{}";'.format(section))
        return [i[0] for i in self.__cursor.fetchall()]
    
    '''Получить Все щапросы'''
    def getAllRequests(self):
        self.__cursor.execute('SELECT * FROM requests;')
        return self.__cursor.fetchall()
    
    '''Сбор запросов по заданной отрасли'''
    def collect(self, industry):
        driver = browser.Browser()
        driver.yandexLogin(self.__login, self.__password)
        sn = self.getSubniches(industry)
        print('collect from', industry)
        for ID, name in sn:
            try:
                requests = driver.getRelatedRequestsFromYandex(name, count=20)
            except:
                try:
                    print('reset driver')
                    try:
                        driver.close()
                    except:
                        pass
                    driver = browser.Browser()
                    driver.yandexLogin(self.__login, self.__password)
                    requests = driver.getRelatedRequestsFromYandex(name.replace(',',''), count=200)
                except Exception as e:
                    print(e)
                    continue
                
            for r in requests:
                self.addRequest(r, ID)
        print(industry, 'success')
        driver.close()
    
    '''Сбор статистики по регионам (не реализовано)'''
    #def getRegionsHistory(self, industry):
        
    '''Сбор статистики по истории зпросов'''
    def getStatHistory(self, industry):
        driver = browser.Browser()
        driver.yandexLogin(self.__login, self.__password)
        subniches = self.getSubniches(industry)
        for ID,sn in subniches:
            rqs = self.getRequests(ID)
            #print(rqs)
            sn_history = {}
            for i,r in enumerate(rqs):
                history = driver.getStatHistory(r)
                if i==0:
                    sn_history = history
                else:
                    for k,v in history.items():
                        sn_history[k]['absolute'] += history[k]['absolute']
                        
            for k,v in sn_history.items():
                today = datetime.today().strftime('%Y-%m-%d')
                self.__cursor.execute('INSERT INTO requests_history(section, period, requests_count, status, update_date) VALUES("%s", "%s", "%s", 0, "%s");' % (sn, k, v['absolute'], today))
            self.__dbase.commit()
    
    '''Сбор всех запросов'''
    def collectAll(self, mthreads):
        industries = self.getIndustries()
        threads = [Thread(target=self.collect, args=(ID,)) for ID, name in industries]
        if not mthreads:
            for i in threads:
                i.run()
        else:
            tc = len(threads)
            while tc:
                while active_count()>=7.0:
                    time.sleep(1.0)
                threads[tc-1].start()
                tc -= 1
            for t in threads:
                t.join()

coll = Collector('serzhant.nalivaiko@yandex.ru', "lolkekcheburek")
coll.getStatHistory('F')

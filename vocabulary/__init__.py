def isint(arg):
    try:
        return int(arg)
    except:
        return None

file = open('vocabulary/russian_vocabulary.txt', 'rb')
data = file.read().decode('1251')
vocabulary = data.split('\r\n\r\n')
file.close()
del data

words = {}
for word in vocabulary:
    splitter = word.find('\r\n')
    k = word[:splitter]
    v = word[splitter+2:].strip()
    
    v = v.replace(') а)', ')\r\n a)')
    v = v.replace('\r\n ', 'SPLITTER')
    v = v.replace('\r\n', '')
    v = v.replace('SPLITTER', '\r\n ')
    text = v.lower()
    #v = v.split('SPLITTER')
    descr = {}
    synonim_marker = 'то же, что: '
    adj_noun_marker = 'по знач. с сущ.: '
    noun_marker = 'к сущ.: '
    if adj_noun_marker in text:
        anm_start = text.find(adj_noun_marker) + len(adj_noun_marker)
        anm_end = text.find(' ', anm_start+1)
        descr['noun'] = text[anm_start:anm_end].strip().strip(',').strip('.')
    elif noun_marker in text:
        anm_start = text.find(noun_marker) + len(noun_marker)
        anm_end = text.find(' ', anm_start+1)
        descr['noun'] = text[anm_start:anm_end].strip().strip(',').strip('.')
    
    if synonim_marker in text:
        anm_start = text.find(synonim_marker) + len(synonim_marker)
        anm_end = text.find(' ', anm_start+1)
        descr['synonim'] = text[anm_start:anm_end].strip().strip(',').strip('.')

    line = v.split('\r\n ')[0].split()
    descr['slang'] = 'разг.' in set(line)
        
    if line[0] == 'прил.':
        descr['type'] = 'adjective'
    elif line[0] in {'мн.', 'ж.', 'м.', 'ср.'}:
        sexes = {'ж.' : 'female', 'м.' : 'male', 'ср.' : 'middle', 'мн.' : 'plural'}
        descr['type'] = 'noun'
        descr['sex'] = sexes[line[0]]
    elif line[0] == 'нареч.':
        descr['type'] = 'adverb'
    elif line[0] == 'предлог':
        descr['type'] = 'proposal'
    elif 'местоим.' in line:
        descr['type'] = 'pronoun'
    elif 'союз' in line:
        descr['type'] = 'union'
    elif 'предикатив' in line:
        descr['type'] = 'predic'
    elif 'сов.' in line or ' несов.' in line or len(k)>=3 and (k[-1] in {'л'} or k[-2] in {'ем','ить', 'ать', 'ять', 'ла', 'ли', 'ло', 'ет','ит', 'ат', 'ют', 'ят', 'уй', 'юй'}):
        descr['type'] = 'verb'
        
    else:
        for i in range(1, 100):
            i = str(i)+'. '
            line_start = text.find(i)
            if line_start==-1:
                break
            line_start += len(i)
            line_end = text.find('\r\n', line_start)
            line = text[line_start:line_end].split()
            if line[0] == 'прил.':
                descr['type'] = 'adjective'
            elif line[0] in {'мн.', 'ж.', 'м.', 'ср.'}:
                sexes = {'ж.' : 'female', 'м.' : 'male', 'ср.' : 'middle', 'мн.' : 'plural'}
                descr['type'] = 'noun'
                descr['sex'] = sexes[line[0]]
            elif line[0] == 'нареч.':
                descr['type'] = 'adverb'
            elif line[0] == 'предлог':
                descr['type'] = 'proposal'
            elif 'местоим.' in line:
                descr['type'] = 'pronoun'
            elif 'союз' in line:
                descr['type'] = 'union'
            elif 'предикатив' in line:
                descr['type'] = 'predic'
            elif 'сов.' in line or ' несов.' in line or len(k)>=3 and (k[-1] in {'л'} or k[-2] in {'ем', 'ить', 'ать', 'ять', 'ла', 'ли', 'ло', 'ет','ит', 'ат', 'ют', 'ят', 'уй', 'юй'}):
                descr['type'] = 'verb'
    
    words[k] = descr
    
vocabulary = words

def getInfinitive(word):
    adjectiveEndings = {
        # Муж.
        'ый', "ий",
        "его", "ого",
        "ому", "ему",
        "его", "ого",
        "им",  "ым",
        "ем",  "ом",
        # Жен.
        'ая', "яя",
        "ей", "ой",
        "ей", "ой",
        "ую", "юю",
        "ей", "ой",
        "ей", "ой",
        # Сред.
        'ое', "ее",
        "ого", "его",
        "ему", "ому",
        "его", "ого",
        "им", "ым",
        "ем", "ом",
        # Множ.
        'ие', "ые",
        "их", "ых",
        "им",
        "их", "ых",
        "ими", "ыми",
        "им", "ым"
    }
    ending = (word[-2:] in adjectiveEndings) * 2 + (word[-3:] in adjectiveEndings) * 3
    
    if word in vocabulary:
        return word

    elif word + 'а' in vocabulary: return word + 'а'
    elif word + 'и' in vocabulary: return word + 'и'
    elif word + 'ы' in vocabulary: return word + 'ы'
    elif word + 'я' in vocabulary: return word + 'я'

    elif word[:-1] + 'а' in vocabulary: return word[:-1] + 'а'
    elif word[:-1] + 'я' in vocabulary: return word[:-1] + 'я'
    elif word[:-1] + 'ы' in vocabulary: return word[:-1] + 'ы'
    elif word[:-1] + 'и' in vocabulary: return word[:-1] + 'и'
    elif word[:-1] + 'ь' in vocabulary: return word[:-1] + 'ь'
    
    elif ending:
        forms = []
        forms.append(word[:-ending] + 'ий')
        forms.append(word[:-ending] + 'ый')
        forms.append(word[:-ending] + 'ой')
        forms.append(word[:-ending] + 'ое')
        forms.append(word[:-ending] + 'ее')
        forms.append(word[:-ending] + 'ая')
        forms.append(word[:-ending] + 'яя')
        forms.append(word[:-ending] + 'ие')
        forms.append(word[:-ending] + 'ые')
        for i in forms:
            if i in vocabulary:
                return i
        
    if word[:-1] in vocabulary:
        return word[:-1]
    elif word[:-2] in vocabulary:
        return word[:-2]

file = open('vocabulary/russian_toponyms.txt', 'rb')
data = file.read().decode('1251')
file.close()
lines = data.split('\r\n')[2:]
del data

toponyms = {}
for i in lines:
    i = [word for word in i.lower().split(' ') if word]
    if len(i)>=2:
        if i[1] in {'г', 'респ', 'обл', 'ао'}:
            toponyms[i[0]] = {}
            toponyms[i[0]]['type'] = i[1]

def isRegion(word):
    word = word.lower()
    adjectiveEndings = {
        # Муж.
        'ый', "ий",
        "его", "ого",
        "ому", "ему",
        "его", "ого",
        "им",  "ым",
        "ем",  "ом",
        # Жен.
        'ая', "яя",
        "ей", "ой",
        "ей", "ой",
        "ую", "юю",
        "ей", "ой",
        "ей", "ой",
        # Сред.
        'ое', "ее",
        "ого", "его",
        "ему", "ому",
        "его", "ого",
        "им", "ым",
        "ем", "ом",
        # Множ.
        'ие', "ые",
        "их", "ых",
        "им",
        "их", "ых",
        "ими", "ыми",
        "им", "ым"
    }
    ending = (word[-2:] in adjectiveEndings) * 2 + (word[-3:] in adjectiveEndings) * 3
    if ending:
        forms = []
        forms.append(word[:-ending] + 'ий')
        forms.append(word[:-ending] + 'ый')
        forms.append(word[:-ending] + 'ое')
        forms.append(word[:-ending] + 'ее')
        forms.append(word[:-ending] + 'ая')
        forms.append(word[:-ending] + 'яя')
        forms.append(word[:-ending] + 'ие')
        forms.append(word[:-ending] + 'ые')
        for i in forms:
            if i in toponyms:
                return True
    return \
        word in toponyms or \
        word[:-1] in toponyms or \
        word[:-1] + 'а' in toponyms or \
        word[:-1] + 'ы' in toponyms or \
        word[:-1] + 'и' in toponyms or \
        word[:-1] + 'я' in toponyms or \
        word[:-1] + 'о' in toponyms or \
        word[:-1] + 'й' in toponyms or \
        word[:-2] + 'а' in toponyms or \
        word[:-2] + 'ы' in toponyms or \
        word[:-2] + 'и' in toponyms or \
        word[:-2] + 'я' in toponyms or \
        word[:-2] + 'о' in toponyms or \
        word[:-2] + 'й' in toponyms

def getType(word):
    word = getInfinitive(word)
    if word is not None and 'type' in vocabulary[word]:
        return vocabulary[word]['type']
    else:
        None

def getSex(word):
    word = getInfinitive(word)
    return vocabulary[word]['sex']

transaction = "новый", 'Дорогой', 'Купля', 'Купить','Куплю','Покупка','Скупка','Продать','Продам','Заказать','отзыв','аналог','Заказ','Приобрести','Оплатить','Оплата','Арендовать','Доставка','Доставить','Прокат','В кредит','Кредит','Рассрочка','Бронирование','Бронь','Забронировать','Оформить','Оформление','Нанять','Услуги','Вызов','Вызвать'
commerce = 'Продажа','Цена','Стоимость','Сколько стоит','Дорого','Под ключ','Недорого','нужен','Дешево','Премиум','Люкс','VIP','вип','Распродажа','Дисконт','Sale','Прайс','Тариф','Опт','Оптовый','В наличии','Бюджетный','Скидки','Скидочный','Акции','Акционный','заявка'
timec = 'Срочно','Быстро','Сегодня','Сейчас','За час'
place = 'онлайн','ИПР', 'ИП','ЗАО', 'ООО', 'АО', 'ОАО', 'ЗАО', 'адрес', 'СТО', 'Официальный', 'Магазин','Интернет-магазин','Агентство','Бюро','Студия','Производитель','Фирма','Организация','Компания','Фабрика','Завод','Сайт'
first_step = 'Консультация','Замер','Расчёт','Рассчитать','Просчёт','Просчитать','Калькулятор','Тестовый','Пробный','Пробник','Оценка'
stores = 'aliexpress','алиэкспресс','авито','avito','с рук','eldorado','эльдорадо','стим','steam','origin','store','amazon','амазон', 'юла'


sellings = ' '.join(transaction + commerce + timec + place + first_step + stores).lower().split(' ')

def isSellingWord(word):
    word = word.lower()
    return word in sellings
    inf = getInfinitive(word)
    if inf.lower() in sellings:
        return True
    return False


![Workflow Status](https://github.com/xVismar/foodgram/actions/workflows/main.yml/badge.svg)

# О проекте

Ссылка на рабочий проект - [![FOODGRAM-VISMAR](https://example.com/foodgram-image.jpg)](https://foodgram-vismar.ddns.net)

### Что можно в Foodgram?
- Регистрироваться на сайте
- Создавать странички рецептов блюд, с выбором из более чем 2000 различных вариантов ингредиентов
- Подписываться на авторов рецептов, чтобы следить за их новыми публикациями
- Добавлять рецепты блюд в корзину и получать список всех ингредиентов по клику
- Добавлять рецепты в Избранное
- Также доступна API версия сайта со всеми функциями

<br>

# Проект контейнеры и CI/CD для Foodgram

Проект настроен на сборку, деплой и запуск в контейнерах, настроено автоматическое тестирования соответствия кода Flake8 и деплой на удалённый сервер без участия пользователя.

<br>

# Стек технологий
- Python
- Django
- Gunicorn
- Djangorestframework
- Postgresql

Полный перечень библиотек, модулей и их версии можно посмотреть в `backend/requirements.txt`
API документация к проекту будет доступна по адресу - ``ваш домен/api/docs``
Пример - [ССЫЛКА](https://foodgram-vismar.ddns.net/api/docs/)
<br>

<details>
  <summary><b<strong>Инструкция по развертыванию проекта</strong></b></summary>

### Развертывание проекта

1. Форкнуть репозиторий проекта: xvismar/foodgram на свой аккаунт GitHub
2. Клонировать форкнутый репозиторий на локальную машину или VM сервер.
3. В репозитории проекта - Во вкладке ```Settings - Secrets and variables - Actions``` обозначить и сохранить следующие не публичные данные:

```

Логин и пароль вашего профиля на Docker.com:
- DOCKER_USERNAME  -- # Имя профиля на DockerHub
- DOCKER_PASSWORD  -- # Пароль от профиля на DockerHub

Данные удалённого сервера:
- HOST  -- # IP-адрес вашего сервера
- USER  -- # Имя пользователя для подключения к удаленному серверу
- SSH_KEY  -- # Приватный SSH-ключ (Сам текст из ключа, весь)
- SSH_PASSPHRASE -- # passphrase для приватного ключа SSH

Данные для отправки сообщения о деплое проекта:
- TELEGRAM_TO -- # ID пользователя, которому отправляется сообщение об успешном деплое проекта (Ваш Telegram ID)
- TELEGRAM_TOKEN -- # Bot API Token (токен вашего Бота в телеграм , через которого отправляется сообщение, получить можно через @botfather)
```

4. На сервере:
Создайте файл-окружения для хранения ценных переменных (`.env`)

```
cd
mkdir foodgram/
cd foodgram
touch .env
```
В файл `.env` поместить:
SECRET_KEY # - Секретный ключ Вашего Джанго проекта
ALLOWED_HOSTS # - Через запятую, без ковычек Ваши разрешенные хосты


- Определить базовые настройки `location` и `server` в секции в файле `/etc/nginx/sites-enabled/default`:

```
server {
    server_name <IP-адрес вашего сервера> <доменное имя вашего сайта>;
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8080;
    }
}

```

5. После добавления всех необходимых переменных и секретов - сделайте `push` в Ваш `GitHub` репозиторий
```
git add .
git commit -m "<ваше сообщение коммита>"
git push
```

</details>

<br>
<details>
  <summary><b<strong>Локальное развертывание без Docker</strong></b></summary>


### Клонировать репозиторий
```

git clone https://github.com/xVismar/foodgram.git
cd foodgram
```

### Установить зависимости
```

pip install -r backend/requirements.txt
```


### Создать файл окружения

```

cd
mkdir foodgram/
cd foodgram
touch .env

```

### Добавить в файл `.env` следующие переменные:

```

SECRET_KEY # - Секретный ключ Вашего Джанго проекта
ALLOWED_HOSTS # - Через запятую, без ковычек Ваши разрешенные хосты

```


### Определить базовые настройки ``location`` и ``server`` в файле `/etc/nginx/sites-enabled/default`:
### Пример:

```

server {
    server_name <IP-адрес вашего сервера> <доменное имя вашего сайта>;
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8080;
    }
}

```

### Применить миграции

```

python manage.py migrate

```

### Создать суперпользователя
```

python manage.py createsuperuser
```

### Запустить сервер
```

python manage.py runserver
```

</details>

<br>
# Авторы    

Frontend - [Команда Яндекс Практикума[yandex-prakticum]](https://github.com/yandex-praktikum)     
Backend - [Aлексеев Алексей (Vismar)](https://github.com/xVismar)          

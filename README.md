![Main Foodgram Workflow](https://github.com/AlexKlysh/foodgram-project-react/actions/workflows/main.yml/badge.svg)

# ПРОЕКТ ФУДГРАМ

## Ссылка на проект

klyshgram.bounceme.net

**Админка:**
- Email - klysha88@yandex.ru;
- Пароль - 1234
- - -

## Описание проекта
Фудграм - сайт, где каждый может раскрыться как настоящий повар. Смотрите рецепты других блюдоделов или создавайте свои.
Также вы с легкостью можете подписаться на интересного вам автора изысканных блюд или добавить любой рецепт в избранное.
А еще вы можете добавить рецепты в корзину и сохранить список покупок.
Никаких больше томов с рецептами - только **ФУДГРАМ**
- - -

## Стэк технологий в проекте
- Python
- Django
- DRF
- Docker
- Nginx
- Postgres
- - -

## Как развернуть проект у себя компьютере
- Клонировать репозиторий:

```
git clone https://github.com/AlexKlysh/foodgram-project-react
```

- Перейти в дерикторию backend:

```
cd backend/
```

- Создать и активировать виртуальное окружение:

```
python -m venv venv
source venv/scripts/activate - eсли у вас Windows
source venv/bin/activate - если у вас Linux/macOS
```

- Установить зависимости:

```
pip install -r requirements.txt
```

- Создать файл .env в корне проекта и заполнить данными:

```
SECRET_KEY=#Ваш секретный ключ
DEBUG=True или False
ALLOWED_HOSTS=127.0.0.1 localhost
DATABASES=prod - если вы хотите использовать Posgtres
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
```

- Выполнить миграции:

```
python manage.py migrate
```

- Выгрузить данные об ингрединетах и тэгах:

```
python manage.py load_ingredients_csv
python manage.py load_tags_csv
```

- Загрузка статики:

```
python manage.py collectstatic
```

- Запустить проект:

```
python manage.py runserver
```

- - -

## Как запустить проект через докер
- В корне проекта сбилдить образы:

```
docker-compose up -d --build
```

- Выполнить миграции:

```
docker-compose exec backend python manage.py migrate
```

- Собрать статику:

```
docker-compose exec backend python manage.py collectstatic
docker-compose exec backend python manage.py cp -r /app/static/ . /backend_static/
```

- Выгрузить данные:

```
docker-compose exec backend python manage.py load_ingredients_csv
docker-compose exec backend python manage.py load_tags_csv
```

- - -

## Автор проекта
Клышкин Александр [GitHub](https://github.com/AlexKlysh)

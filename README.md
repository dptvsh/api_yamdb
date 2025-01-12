# API для проекта YaMDb

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/dptvsh/api_yamdb.git
```

```
cd api_yamdb
```

Cоздать виртуальное окружение:

на Linux/macOS: ```python3 -m venv venv```

на Windows: ```python -m venv venv``` или ```py -3 -m venv venv```

Активировать виртуальное окружение командой:

на Windows: ```source venv/Scripts/activate```

на Linux/macOS: ```source venv/bin/activate```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:
```
python manage.py runserver
```

### Пример запроса API

Для получения конкретного произведения нужно выполнить запрос, где {titles_id} соответствует id необходимого произведения:

```
GET /api/v1/titles/{titles_id}/
```
В случае успешного выполнения запроса будет получен ответ в формате json:
```
{
  "id": 0,
  "name": "string",
  "year": 0,
  "rating": 0,
  "description": "string",
  "genre": [
    {
      "name": "string",
      "slug": "^-$"
    }
  ],
  "category": {
    "name": "string",
    "slug": "^-$"
  }
}
```
Аналогичным образом возможно получить данные о конкретном отзыве на произведение (reviews), комментарие к определенному отзыву (comments), либо их список. Более детальная информация по каждому доступному эндпоинту представлена в файле redoc.yaml.
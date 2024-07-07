import requests
import time

# URL для POST-запроса
url = "https://employer-api.robota.ua/cvdb/resumes"

# Параметры для POST-запроса
payload = {
    "page": 1,
    "period": "ThreeMonths",
    "sort": "UpdateDate",
    "searchType": "default",
    "ukrainian": True,
    "onlyDisliked": False,
    "onlyFavorite": False,
    "onlyWithCurrentNotebookNotes": False,
    "showCvWithoutSalary": True,
    "sex": "Any",
    "cityId": 0,
    "inside": False,
    "onlyNew": False,
    "moveability": True,
    "onlyMoveability": False,
    "rubrics": ["1-7"],
    "languages": [],
    "scheduleIds": [],
    "educationIds": [],
    "branchIds": [],
    "experienceIds": [],
    "keyWords": "",
    "hasPhoto": False,
    "onlyViewed": False,
    "onlyWithOpenedContacts": False,
    "resumeFillingTypeIds": [],
    "districtIds": [],
    "onlyStudents": False,
    "searchContext": "Filters"
}

# Заголовки для запроса (если необходимо)
headers = {
    "Content-Type": "application/json",
    # Добавьте здесь любые другие заголовки, если это необходимо, например, токен авторизации
}

# Список для хранения всех текстов ответов
all_responses = []

# Цикл для пагинации
while True:
    # Отправка POST-запроса
    response = requests.post(url, json=payload, headers=headers)

    # Обработка ответа
    if response.status_code == 200:
        text_data = response.text
        all_responses.append(text_data)

        print(f"Страница {payload['page']} обработана.")

        # Увеличение номера страницы для следующего запроса
        payload['page'] += 1

        # Задержка между запросами
        time.sleep(2)
    else:
        print(f"Ошибка при выполнении запроса: {response.status_code}")
        print(response.text)
        break

# Сохранение всех данных в текстовый файл
with open('responses.txt', 'w', encoding='utf-8') as f:
    for response in all_responses:
        f.write(response + '\n')

print("Данные сохранены в файл responses.txt.")

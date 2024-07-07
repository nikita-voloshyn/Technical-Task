import requests
import time
import csv

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
    "searchContext": "Filters",
    "requestedCount": 20  # Добавляем requestedCount
}

# Заголовки для запроса (если необходимо)
headers = {
    "Content-Type": "application/json",
    # Добавьте здесь любые другие заголовки, если это необходимо, например, токен авторизации
}


# Функция для обработки POST-запроса с возможностью повтора
def send_request(url, payload, headers, retries=3):
    for attempt in range(retries):
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Попытка {attempt + 1} не удалась. Статус код: {response.status_code}")
            time.sleep(2)
    return None


# Открытие файла для записи данных в CSV формате
with open('resumes.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = [
        'resumeId', 'userId', 'speciality', 'fullName', 'salary',
        'age', 'cityName', 'experience', 'photo', 'url'
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Цикл для пагинации
    while True:
        json_data = send_request(url, payload, headers)

        if json_data:
            print(f"Страница {payload['page']} обработана.")

            # Запись данных о людях в CSV файл
            for document in json_data.get('documents', []):
                writer.writerow({
                    'resumeId': document.get('resumeId'),
                    'userId': document.get('userId'),
                    'speciality': document.get('speciality'),
                    'fullName': document.get('fullName'),
                    'salary': document.get('salary', ''),
                    'age': document.get('age', ''),
                    'cityName': document.get('cityName', ''),
                    'experience': document.get('experience', []),  # Пример, можно изменить под свои нужды
                    'photo': document.get('photo', ''),
                    'url': document.get('url', '')
                })

            # Проверка количества документов
            if len(json_data.get('documents', [])) < payload['requestedCount']:
                print("Достигнут конец данных.")
                break

            # Увеличение номера страницы для следующего запроса
            payload['page'] += 1

            # Задержка между запросами
            time.sleep(2)
        else:
            print(f"Ошибка при выполнении запроса на странице {payload['page']}")
            break

print("Данные сохранены в файл resumes.csv.")

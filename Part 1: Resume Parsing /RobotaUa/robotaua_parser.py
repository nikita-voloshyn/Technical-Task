import requests
import time
import json
import re

# URL для POST-запроса и URL для GET-запроса с параметром markView: true
url_post = "https://employer-api.robota.ua/cvdb/resumes"
url_get_template = "https://employer-api.robota.ua/resume/{resume_id}?markView=true"

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

# Функция для отправки GET-запроса с использованием aiohttp
def fetch_resume(resume_id):
    url = url_get_template.format(resume_id=resume_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении данных кандидата {resume_id}: {response.status_code}")
        return None

# Функция для получения всех резюме и отправки GET-запросов
def get_and_process_resumes():
    all_responses = []

    # Цикл для пагинации
    while True:
        json_data = send_request(url_post, payload, headers)

        if json_data:
            print(f"Страница {payload['page']} обработана.")

            # Добавляем данные о людях в список
            all_responses.extend(json_data.get('documents', []))

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

    # Получение дополнительных данных о каждом кандидате
    extracted_data = []
    for resume in all_responses:
        resume_id = resume['resumeId']
        details = fetch_resume(resume_id)
        if details:
            # Очистка описания навыков от HTML тегов
            cleaned_skills = []
            for skill in details.get('skills', []):
                description = skill.get('description', '')
                clean_description = re.sub(r"<.*?>", "", description)  # Удаление всех HTML тегов
                cleaned_skills.append({"description": clean_description})

            # Добавление данных о кандидате в извлеченные данные
            data = {
                'resume_id': resume_id,
                'name': details.get('name', 'Not specified'),
                'age': details.get('age', 'Not specified'),
                'speciality': details.get('speciality', 'Not specified'),
                'salaryFull': details.get('salaryFull', 'Not specified'),
                'skills': cleaned_skills,
                'experience': details.get('experiences', [])
            }
            extracted_data.append(data)
            # print(all_responses)

    # Сохранение извлеченных данных в файл
    with open('extracted_data.json', 'w', encoding='utf-8') as jsonfile:
        json.dump(extracted_data, jsonfile, ensure_ascii=False, indent=4)

    print("Извлеченные данные сохранены в файл extracted_data.json.")

# Запуск основной функции
if __name__ == "__main__":
    get_and_process_resumes()

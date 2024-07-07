import aiohttp
import asyncio
import time
import json
import re
from datetime import datetime

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
async def send_request(session, url, payload, headers, retries=3):
    for attempt in range(retries):
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Попытка {attempt + 1} не удалась. Статус код: {response.status}")
                await asyncio.sleep(2)
    return None


# Функция для отправки GET-запроса с использованием aiohttp
async def fetch_resume(session, resume_id):
    url = url_get_template.format(resume_id=resume_id)
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Ошибка при получении данных кандидата {resume_id}: {response.status}")
            return None


# Функция для расчета общего времени работы
def calculate_total_experience(experiences):
    total_months = 0
    for exp in experiences:
        start = datetime.strptime(exp['startWork'].split('.')[0], "%Y-%m-%dT%H:%M:%S")
        end = exp['endWork']
        if end:
            end = datetime.strptime(end.split('.')[0], "%Y-%m-%dT%H:%M:%S")
        else:
            end = datetime.now()
        total_months += (end.year - start.year) * 12 + end.month - start.month

    years = total_months // 12
    months = total_months % 12
    return f"{years} років і {months} місяців"


# Функция для получения всех резюме и отправки GET-запросов
async def get_and_process_resumes():
    async with aiohttp.ClientSession() as session:
        all_responses = []

        # Цикл для пагинации
        while True:
            json_data = await send_request(session, url_post, payload, headers)

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
                await asyncio.sleep(2)
            else:
                print(f"Ошибка при выполнении запроса на странице {payload['page']}")
                break

        # Получение дополнительных данных о каждом кандидате
        extracted_data = []
        tasks = [fetch_resume(session, resume['resumeId']) for resume in all_responses]
        results = await asyncio.gather(*tasks)

        for details in results:
            if details:
                # Очистка описания навыков от HTML тегов и получение текста
                cleaned_skills = []
                for skill in details.get('skills', []):
                    description = skill.get('description', '')
                    clean_description = re.sub(r"<.*?>", "", description)  # Удаление всех HTML тегов
                    cleaned_skills.append(clean_description)

                # Расчет общего времени работы
                total_experience = calculate_total_experience(details.get('experiences', []))

                # Добавление данных о кандидате в извлеченные данные
                data = {
                    'resume_id': details.get('resumeId', 'Not specified'),
                    'name': details.get('name', 'Not specified'),
                    'age': details.get('age', 'Not specified'),
                    'speciality': details.get('speciality', 'Not specified'),
                    'salaryFull': details.get('salaryFull', 'Not specified'),
                    'skills': cleaned_skills,
                    'experience': total_experience
                }
                extracted_data.append(data)

        # Сохранение извлеченных данных в файл
        with open('extracted_data.json', 'w', encoding='utf-8') as jsonfile:
            json.dump(extracted_data, jsonfile, ensure_ascii=False, indent=4)

        print("Извлеченные данные сохранены в файл extracted_data.json.")


# Запуск основной функции
if __name__ == "__main__":
    asyncio.run(get_and_process_resumes())

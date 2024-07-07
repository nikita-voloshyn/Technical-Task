import aiohttp
import asyncio
import time
import json
import re
from datetime import datetime

# URL
url_post = "https://employer-api.robota.ua/cvdb/resumes"
url_get_template = "https://employer-api.robota.ua/resume/{resume_id}?markView=true"


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
    "requestedCount": 20  # Додаємо requestedCount
}


headers = {
    "Content-Type": "application/json",
#     можна додати ще але воно не блокує тому добре
}

async def send_request(session, url, payload, headers, retries=3):
    for attempt in range(retries):
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Спроба {attempt + 1} не вдалася. Статус код: {response.status}")
                await asyncio.sleep(2)
    return None

async def fetch_resume(session, resume_id):
    url = url_get_template.format(resume_id=resume_id)
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Помилка при отриманні даних кандидата {resume_id}: {response.status}")
            return None

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

async def get_and_process_resumes():
    async with aiohttp.ClientSession() as session:
        all_responses = []

        while True:
            json_data = await send_request(session, url_post, payload, headers)

            if json_data:
                print(f"Сторінка {payload['page']} оброблена.")

                all_responses.extend(json_data.get('documents', []))

                if len(json_data.get('documents', [])) < payload['requestedCount']:
                    print("Досягнуто кінець даних.")
                    break

                payload['page'] += 1

                await asyncio.sleep(2)
            else:
                print(f"Помилка при виконанні запиту на сторінці {payload['page']}")
                break

        extracted_data = []
        tasks = [fetch_resume(session, resume['resumeId']) for resume in all_responses]
        results = await asyncio.gather(*tasks)

        for details in results:
            if details:
                cleaned_skills = []
                for skill in details.get('skills', []):
                    description = skill.get('description', '')
                    clean_description = re.sub(r"<.*?>", "", description)  # Видалення всіх HTML тегів
                    cleaned_skills.append(clean_description)

                total_experience = calculate_total_experience(details.get('experiences', []))

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

        with open('robotaua_data.json', 'w', encoding='utf-8') as jsonfile:
            json.dump(extracted_data, jsonfile, ensure_ascii=False, indent=4)

        print("Отримані дані збережено у файл robotaua_data.json.")

if __name__ == "__main__":
    asyncio.run(get_and_process_resumes())

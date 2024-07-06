import requests

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

# Отправка POST-запроса
response = requests.post(url, json=payload, headers=headers)

# Обработка ответа
if response.status_code == 200:
    print("Успешно получен ответ!")
    data = response.json()
    print(data)
else:
    print(f"Ошибка при выполнении запроса: {response.status_code}")
    print(response.text)

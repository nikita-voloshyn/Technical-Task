import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

class WorkUaScraper:
    def __init__(self, base_url, start_page=1, end_page=10):
        """
        Инициализация скрапера с базовым URL и диапазоном страниц.

        Аргументы:
        base_url (str): Базовый URL для страниц с резюме.
        start_page (int): Начальная страница для парсинга.
        end_page (int): Конечная страница для парсинга.
        """
        self.base_url = base_url
        self.start_page = start_page
        self.end_page = end_page

    def get_links_from_page(self, url):
        """
        Извлечение ссылок с одной страницы.

        Аргументы:
        url (str): URL страницы.

        Возвращает:
        list: Список ссылок на резюме.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Проверка успешности запроса
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        links = [urljoin(url, tag['href']) for tag in soup.select('.card h2 a, .card h5 a')]
        return links

    def extract_numbers(self, text):
        """
        Извлечение чисел из текста.

        Аргументы:
        text (str): Входной текст.

        Возвращает:
        str: Строка, содержащая только числа.
        """
        numbers = re.findall(r'\d+', text)
        return ' '.join(numbers) if numbers else "Not specified"

    def extract_position_and_salary(self, tag):
        """
        Извлечение позиции и зарплаты из тега.

        Аргументы:
        tag (bs4.element.Tag): Тег, содержащий позицию и зарплату.

        Возвращает:
        tuple: Позиция и зарплата.
        """
        if tag:
            full_text = tag.get_text(separator=" ", strip=True)
            salary_tag = tag.find("span", class_="text-muted-print")
            if salary_tag:
                salary_text = salary_tag.get_text(strip=True)
                position = full_text.replace(salary_text, "").strip()
                salary = self.extract_numbers(salary_text)
            else:
                match = re.search(r'(\d[\d\s]*)\s*грн', full_text)
                if match:
                    salary = match.group(1).replace('\xa0', ' ')
                    position = full_text.replace(salary, "").replace('грн', "").strip()
                else:
                    position = full_text
                    salary = "Not specified"
        else:
            position = "Not specified"
            salary = "Not specified"
        return position, salary

    def scrape_resume_data(self, resume_url):
        """
        Сбор данных с конкретного резюме.

        Аргументы:
        resume_url (str): URL резюме.

        Возвращает:
        dict: Собранные данные с резюме.
        """
        try:
            response = requests.get(resume_url)
            response.raise_for_status()  # Проверка успешности запроса
        except requests.RequestException as e:
            print(f"Error fetching {resume_url}: {e}")
            return {}

        soup = BeautifulSoup(response.text, 'html.parser')

        # Получаем ID резюме из URL
        resume_id = resume_url.replace("https://www.work.ua/resumes/", "").replace("/", "")

        # Формируем CSS-селекторы
        position_selector = f'#resume_{resume_id} > div:nth-of-type(1) > div > div > h2'
        dl_selector = f'#resume_{resume_id} > div:nth-of-type(1) > div > div > dl'

        # Извлекаем данные о позиции и зарплате
        job_position_tag = soup.select_one(position_selector)
        job_position, salary_expectation = self.extract_position_and_salary(job_position_tag)

        # Извлекаем данные из dl-тега
        dl_tag = soup.select_one(dl_selector)
        location = age = willingness_to_work = "Not specified"
        if dl_tag:
            dt_tags = dl_tag.find_all("dt")
            for dt in dt_tags:
                if "Місто проживання" in dt.get_text():
                    location = dt.find_next_sibling("dd").get_text(strip=True)
                elif "Вік" in dt.get_text():
                    age = dt.find_next_sibling("dd").get_text(strip=True)
                elif "Готовий працювати" in dt.get_text():
                    willingness_to_work = dt.find_next_sibling("dd").get_text(strip=True)

        resume_data = {
            'job_position': job_position,
            'salary_expectation': salary_expectation,
            'location': location,
            'age': age,
            'willingness_to_work': willingness_to_work
        }

        return resume_data

    def scrape_all_resumes(self):
        """
        Сбор данных со всех резюме.

        Возвращает:
        list: Список данных со всех резюме.
        """
        all_links = []
        for page in range(self.start_page, self.end_page + 1):
            url = f"{self.base_url}{page}"
            print(f"Scraping page: {url}")
            links = self.get_links_from_page(url)
            all_links.extend(links)

        all_resume_data = []
        for link in all_links:
            resume_data = self.scrape_resume_data(link)
            all_resume_data.append(resume_data)

        return all_resume_data


# Пример использования
if __name__ == "__main__":
    # Укажите базовый URL и диапазон страниц для парсинга
    base_url = "https://www.work.ua/resumes-web+developer/?page="
    start_page = 1
    end_page = 5  # Измените это значение в зависимости от количества страниц, которые хотите спарсить

    # Создание экземпляра класса и запуск парсера
    scraper = WorkUaScraper(base_url, start_page, end_page)
    resume_data = scraper.scrape_all_resumes()

    # Вывод результатов
    for data in resume_data:
        print(data)

# Job position (e.g., Data Scientist, Web Developer, etc.) +++++
# Years of experience
# Skills or keywords
# Location    //*[@id="resume_8256382"]/div[1]/div/div/dl/dt[3]
# Salary expectation   +++++++
# Your criterias

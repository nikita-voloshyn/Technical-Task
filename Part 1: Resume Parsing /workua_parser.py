import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


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
        salary_selector = f'#resume_{resume_id} > div:nth-of-type(1) > div > div > h2 > span'

        # Извлекаем данные о позиции
        job_position_tag = soup.select_one(position_selector)
        job_position = job_position_tag.text.strip() if job_position_tag else "Not specified"


        # Извлекаем данные о зарплате, если указано
        salary_tag = soup.select_one(salary_selector)
        salary_expectation = salary_tag.text.strip() if salary_tag else "Not specified"

        resume_data = {
            'job_position': job_position,
            'salary_expectation': salary_expectation,
            # Другие данные, которые могут быть нужны
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



# //*[@id="resume_10215053"]/div[1]/div/div/h2
# //*[@id="resume_8256382"]/div[1]/div/div/h2/span


# //*[@id="resume_8256382"]/div[1]/div/div/h2

# Job position (e.g., Data Scientist, Web Developer, etc.)
# Years of experience
# Skills or keywords
# Location
# Salary expectation
# Your criterias

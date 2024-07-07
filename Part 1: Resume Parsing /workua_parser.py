import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

class WorkUaScraper:
    def __init__(self, base_url, start_page=1, end_page=10):

        self.base_url = base_url
        self.start_page = start_page
        self.end_page = end_page

    def get_links_from_page(self, url):

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        links = [urljoin(url, tag['href']) for tag in soup.select('.card h2 a, .card h5 a')]
        return links

    def extract_numbers(self, text):

        numbers = re.findall(r'\d+', text)
        return ' '.join(numbers) if numbers else "Not specified"

    def extract_position_and_salary(self, tag):

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

    def extract_experience(self, text):

        experience = "Not specified"
        match = re.search(r'\((.*?)\)', text)
        if match:
            experience = match.group(1).replace('\xa0', ' ')
        return experience

    def scrape_resume_data(self, resume_url):

        try:
            response = requests.get(resume_url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching {resume_url}: {e}")
            return {}

        soup = BeautifulSoup(response.text, 'html.parser')

        resume_id = resume_url.replace("https://www.work.ua/resumes/", "").replace("/", "")

        name_selector = f'#resume_{resume_id} > div:nth-of-type(1) > div > div > h1'
        position_selector = f'#resume_{resume_id} > div:nth-of-type(1) > div > div > h2'
        dl_selector = f'#resume_{resume_id} > div:nth-of-type(1) > div > div > dl'
        skill_selector = f'li.no-style.mr-sm.mt-sm'
        experience_section_selector = f'#resume_{resume_id} > h2:nth-of-type(2)'
        experience_selector = f'#resume_{resume_id} > p:nth-of-type(3) > span:nth-of-type(1)'

        job_position_tag = soup.select_one(position_selector)
        job_position, salary_expectation = self.extract_position_and_salary(job_position_tag)

        name_tag = soup.select_one(name_selector)
        name = name_tag.get_text(strip=True) if name_tag else "Not specified"

        dl_tag = soup.select_one(dl_selector)
        location = age = willingness_to_work = "Not specified"
        if dl_tag:
            dt_tags = dl_tag.find_all("dt")
            for dt in dt_tags:
                if "Місто проживання" in dt.get_text():
                    location = dt.find_next_sibling("dd").get_text(strip=True)
                elif "Вік" in dt.get_text():
                    age = dt.find_next_sibling("dd").get_text(strip=True).replace('\xa0', ' ')
                elif "Готовий працювати" in dt.get_text():
                    willingness_to_work = dt.find_next_sibling("dd").get_text(strip=True)

        skill_texts = []
        skill_tags = soup.select(skill_selector)
        for tag in skill_tags:
            skill_texts.append(tag.get_text(strip=True))

        experience_section_tag = soup.select_one(experience_section_selector)
        if experience_section_tag and "Досвід роботи" in experience_section_tag.get_text(strip=True):
            experience_tag = soup.select_one(experience_selector)
            experience = self.extract_experience(
                experience_tag.get_text(strip=True)) if experience_tag else "Not specified"
        else:
            experience = "Not specified"

        skills = "• ".join(skill_texts)

        resume_data = {
            'resume_id': resume_id,
            'name': name,
            'age': age,
            'speciality': job_position,
            'salaryFull': salary_expectation + " грн.",
            'skills': [skills],
            'experience': experience
        }

        return resume_data

    def scrape_all_resumes(self):

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

    def save_to_json(self, data, filename="workua_data.json"):

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    base_url = "https://www.work.ua/resumes-web+developer/?page="
    start_page = 1
    end_page = 48

    scraper = WorkUaScraper(base_url, start_page, end_page)
    resume_data = scraper.scrape_all_resumes()

    scraper.save_to_json(resume_data, filename="workua_data.json")
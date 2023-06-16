from ineuron_scrapper import IneuronScrapper
from application_logger.app_logger import Logger


class CourseScraper:
    def __init__(self):
        self.ineuron_scrapper = IneuronScrapper(r'chromedriver.exe')
        
    def scrape_courses(self, category):
        try:
            self.ineuron_scrapper.initialize_driver()
            self.ineuron_scrapper.load_web_page(category)
            course_links = self.ineuron_scrapper.get_courses_link()
            all_courses = self.ineuron_scrapper.extract_course_details(course_links)
            courses_json = self.ineuron_scrapper.save_courses_json(all_courses)
            self.ineuron_scrapper.save_pdfs(all_courses ,category)
            self.ineuron_scrapper.save_mongodb(category ,courses_json)
            self.ineuron_scrapper.save_msql(all_courses)
        finally:
            self.ineuron_scrapper.close_driver()
    
        
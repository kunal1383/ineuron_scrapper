from selenium import webdriver
from bs4 import BeautifulSoup as bs
import json
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from application_logger.app_logger import Logger
from create_pdf import PDFCreator
from mysql import MySQHandler
from mongodb import MongoDBHandler

class IneuronScrapper:
    def __init__(self ,driver_path):
        self.driver_path = driver_path
        self.driver = None
        self.log_writer = Logger()
        self.file_object = open("Scrapper_Logs/ineuron_log.txt", 'a+') 
        
    def initialize_driver(self):
        self.log_writer(self.file_object ,"Initializing the driver")
        try:
            self.driver = webdriver.Chrome(executable_path=self.driver_path)
            self.driver.implicitly_wait(10) 
        except Exception as e:   
            self.log_writer.log(self.file_object, f'Unsuccessful initialization of driver due to {str(e)}')
            raise Exception
        
        
    def load_page(self,category):
        self.log_writer(self.file_object ,"Loding the page")
        try:
            url =  'https://ineuron.ai/category/' + category.upper() +'/'
            self.driver.get(url)
        except Exception as e:    
            self.log_writer.log(self.file_object, f'Loading of page failed  due to {e}')
            raise Exception    
        
    def get_courses_link(self):
        self.log_writer(self.file_object ,"Started fetching courses links")
        try:
            # Scroll down to load all the course cards
            scroll_pause_time = 2
            last_height = self.driver.execute_script("return document.body.scrollHeight")

            course_links = set()

            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
                # Extract the dynamically loaded HTML source
                html_content = self.driver.page_source

                # Parse the HTML content with Beautiful Soup
                soup = bs(html_content, 'html.parser')

                # Find the course links
                course_cards = soup.find_all('div', class_='Course_course-card__1_V8S')
                new_links = set([card.find('a')['href'] for card in course_cards])
                course_links.update(new_links) 
            return course_links
        
        except Exception as e:    
            self.log_writer.log(self.file_object, f'Unsuccessful to fetch the links due to {e}')
            raise Exception
        
    
    def extract_course_details(self,course_links):
        all_courses = []

        for link in course_links:
            self.driver.get('https://ineuron.ai' + link)
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.CurriculumAndProjects_accordion-header__3ALRY')))
            except TimeoutException:
                # Handle the case when the element is not found within the timeout
                continue
            try:
                # Find the "View More" button and click it
                view_more_button = self.driver.find_element(By.CSS_SELECTOR, 'span.CurriculumAndProjects_view-more-btn__3ggZL')
                self.driver.execute_script("arguments[0].click();", view_more_button)

                # Wait for the expanded content to load
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.CurriculumAndProjects_curriculum-accordion__2pppc')))
            except NoSuchElementException:
                # Handle the case when the "View More" button is not found
                continue
            
            # Extract the dynamically loaded HTML source
            html_content = self.driver.page_source
            
            # Parse the HTML content with Beautiful Soup
            soup = bs(html_content, 'html.parser')
            
            # Extract the course title
            try:
                course_title = soup.select_one('div#__next section.Hero_hero__1u4sc div.Hero_container__2PLaQ.Hero_flex__27qKG.container.flex div.Hero_left__2v34v h3.Hero_course-title__1a-Hg').text.strip() 
            except Exception as e:  
                self.log_writer.log(self.file_object, f'Could not fetch the title due to {e}')
                
                
                    
            
            instructors = self.extract_instructors(soup)
            curriculum = self.extract_curriculum(soup)

            all_courses.append({
                'title': course_title,
                'instructors': instructors,
                'curriculum': curriculum
            })  
        return all_courses
    
    def extract_instructors(self ,soup):
        try:
            instructor_divs = soup.find_all('div', class_='InstructorDetails_mentor__2hmG8')
            instructors = {}

            for instructor in instructor_divs:
                name = instructor.div.h5.text.replace('.', '')
                about_instructor = instructor.div.p.text
                instructors[name] = about_instructor

            return instructors
        except Exception as e:    
            self.log_writer.log(self.file_object, f'Unsuccessful to fetch the instructors details due to {e}')
            raise Exception
    def  extract_curriculum(self ,soup):
        try:
            courses = {}
            curriculum_sections = soup.find_all('div', class_='CurriculumAndProjects_curriculum-accordion__2pppc')

            for section in curriculum_sections:
                course = section.find('div', class_='CurriculumAndProjects_accordion-header__3ALRY').text.replace('.', '')
                curriculum_items = section.find_all('li')
                curriculum_texts = [item.text for item in curriculum_items]
                courses[course] = curriculum_texts
            
            return courses  
        except Exception as e:    
            self.log_writer.log(self.file_object, f'Unsuccessful to fetch the curriculum due to {e}')
            raise Exception
    
    def save_courses_json(self, all_courses):
        self.log_writer(self.file_object ,'saving in json format')
        courses_json = json.dumps(all_courses, indent=4)
        try:
            with open('courses.json', 'w') as file:
                file.write(courses_json)
            return courses_json    
        except Exception as e:    
            self.log_writer.log(self.file_object, f'Unsuccessful to create courses_json due to {e}')
            raise Exception 
    
    def save_pdfs(self ,all_courses ,course_category):  
        self.log_writer(self.file_object ,'saving in pdf format')          
        for course in all_courses:
            pdf_creator = PDFCreator()
            pdf_creator.create_pdf(course, course_category)
            
    def save_mongodb(self,category ,courses_json,username='kunalb1383', password='kunalb1393', db_name='ineuron_courses'):
        self.log_writer(self.file_object ,'saving to mongodb') 
        mongo = MongoDBHandler(username, password, db_name)
        mongo.insert_courses_into_collection(category ,courses_json)
        
    def save_msql(self, all_courses, host="localhost",username="abc",password="password" ):
        self.log_writer.log(self.file_object, 'Saving to MySQL')

        try:
            db = MySQHandler(host, username, password)
            db.connect()

            for course in all_courses:
                db.create_database(course['title'])
                db.create_table(course['title'])
                db.insert_course(course['title'], course['instructors'], course['curriculum'])

            db.commit()
            db.close()
        except Exception as e:
            self.log_writer.log(self.file_object, f'Failed to save to MySQL due to {e}')
            raise Exception
              
                    

    
    def close_driver(self):
        self.log_writer(self.file_object ,'Closing the driver')
        try:
            if self.driver is not None:
                self.driver.quit() 
            self.file_object.close()    
        except Exception as e:    
            self.log_writer.log(self.file_object, f'Unsuccessful to close the driver due to {e}')
            raise Exception                     
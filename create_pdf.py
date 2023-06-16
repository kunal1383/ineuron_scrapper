from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import os
from application_logger.app_logger import Logger

class PDFCreator:
    def __init__(self) :
        self.log_writer = Logger()
        self.file_object = open("PDFCreator_Logs/pdf_log.txt", 'a+') 
        
    def create_pdf(self ,course, course_category):
        self.log_writer(self.file_object ,"Creating pdf")
        try:
            # Generate a  filename for the PDF based on the course title
            filename = course['title'].lower().replace(' ', '_') + '.pdf'

            # Generate the file path for the PDF inside the "courses_pdf" folder
            folder_path = os.path.join('courses_pdf',course_category)
            file_path = os.path.join(folder_path, filename)
            os.makedirs(file_path, exist_ok=True)

            # Create a new PDF document
            doc = SimpleDocTemplate(file_path, pagesize=letter)

            # Create a list to hold the PDF content
            content = []

            # Define styles for headings and paragraphs
            styles = getSampleStyleSheet()
            heading_style = styles['Heading1']
            paragraph_style = ParagraphStyle(
                'normal',
                parent=styles['BodyText'],
                spaceAfter=12,
                fontSize=11,
                leading=14,
            )

            # Add the course title
            title = Paragraph(course['title'], heading_style)
            content.append(title)
            content.append(Spacer(1, 0.5 * inch))

            # Add the instructors section
            instructors_heading = Paragraph('<b>Instructors:</b>', paragraph_style)
            content.append(instructors_heading)
            for name, about in course['instructors'].items():
                instructor_name = Paragraph(f'<b>{name}:</b>', paragraph_style)
                instructor_about = Paragraph(about, paragraph_style)
                content.append(instructor_name)
                content.append(instructor_about)
                content.append(Spacer(1, 0.2 * inch))
            content.append(Spacer(1, 0.5 * inch))

            # Add the curriculum section
            curriculum_heading = Paragraph('<b>Curriculum:</b>', paragraph_style)
            content.append(curriculum_heading)
            for topic, items in course['curriculum'].items():
                topic_title = Paragraph(f'<b>{topic}</b>', paragraph_style)
                content.append(topic_title)
                for item in items:
                    curriculum_item = Paragraph(f"• {item}", paragraph_style)
                    content.append(curriculum_item)
                content.append(Spacer(1, 0.2 * inch))
            content.append(Spacer(1, 0.5 * inch))

            # Build the PDF document
            doc.build(content)
            self.log_writer(self.file_object,f"Created PDF for course: {course['title']}")
            self.file_object.close()
        except Exception as e:   
            self.log_writer.log(self.file_object, f'Unsuccessful to create pdf due to {e}')
            raise Exception    

    
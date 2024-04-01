from celery import Celery
from celery.schedules import crontab
import datetime


app = Celery('celery_worker', broker="redis://localhost:6379/0")


app.conf.beat_schedule = {
            'process_courses': {
        'task': 'app.analze',
        'schedule': crontab(minute='*/60')  # Cada 2 minutos para pruebas
    }
}


current_date = datetime.datetime.now(datetime.timezone.utc)


from celery_functions.PDF_dl_processer import CourseProcessor
from celery_functions.VIDEO_dl_processer import CourseVideoProcessor

@app.task
def process_all_courses():
    processor_pdf = CourseProcessor()
    processor_pdf.process_courses()
    processor_video = CourseVideoProcessor()
    processor_video.process_all_courses()
    



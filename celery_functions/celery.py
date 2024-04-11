from datetime import timedelta
from celery import Celery
from celery_functions.task import CourseVideoProcessor

from celery import Celery
from celery.schedules import crontab
import datetime



app = Celery('celery_worker', broker="redis://localhost:6379/0")



from celery_functions.task import CourseProcessor

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute="*/20"),
        process_all_courses.s(),
        name="Run periodic transcriptions every 20 minutes.",
    )

@app.task
def process_all_courses():
    CourseProcessor().process_courses()
    CourseVideoProcessor().process_all_courses()
    
if __name__ == "__main__":
    app.start()
from datetime import timedelta
from celery import Celery
from celery_functions.task import CourseVideoProcessor
from celery import Celery
from celery.schedules import crontab
import datetime

app = Celery('celery_worker', broker="redis://localhost:6379/0", result_backend="redis://localhost:6379/0")

from celery_functions.task import CourseProcessor
from celery_functions.discovery import Discovery

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        120.0,
        process_all_courses.s(),
        name="Run periodic transcriptions every 20 minutes.",
    )
    sender.add_periodic_task(
        120.0,
        update_courses.s(),
        name="update every  20 minutes.",
    )

    sender.add_periodic_task(
        6000.0,
        discovery.s(),
        name="Crea Discovery's cada 10 min",
    )

@app.task
def process_all_courses():
    print("\033[96m[Celery Task] Starting process_all_courses task...\033[0m")
    CourseProcessor().process_courses()
    CourseVideoProcessor().process_all_courses()
    print("\033[92m[Celery Task] Finished process_all_courses task.\033[0m")

@app.task
def update_courses():
    print("\033[96m[Celery Task] Starting update_courses task...\033[0m")
    CourseProcessor().update_pdf()
    CourseVideoProcessor().update_all_courses()
    print("\033[92m[Celery Task] Finished update_courses task.\033[0m")

@app.task
def discovery():
    print("\033[96m[Celery Task] Starting discovery task...\033[0m")
    Discovery().process_courses()
    print("\033[92m[Celery Task] Finished discovery task.\033[0m")

if __name__ == "__main__":
    app.start()

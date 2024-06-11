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
        1200.0,
        process_all_courses.s(),
        name="Run periodic transcriptions every 20 minutes.",
    )
    sender.add_periodic_task(
        1200.0,
        update_courses.s(),
        name="update every 20 minutes.",
    )

    sender.add_periodic_task(
        600.0,
        discovery.s(),
        name="Crea Discovery's cada 10 min",
    )

@app.task
def process_all_courses():
    CourseProcessor().process_courses()
    CourseVideoProcessor().process_all_courses()


@app.task
def update_courses():
    CourseProcessor().update_pdf()
    CourseVideoProcessor().update_all_courses()
    
@app.task
def discovery():
    Discovery().process_courses()
    
if __name__ == "__main__":
    app.start()



# from datetime import timedelta
# from celery import Celery
# from celery.schedules import crontab

# app = Celery('celery_worker', broker="redis://localhost:6379/0", result_backend="redis://localhost:6379/0")

# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(
#         1.0,  # Cada 1 segundo
#         task_one_second.s(),
#         name="Run every 1 second."
#     )
#     sender.add_periodic_task(
#         2.0,  # Cada 2 segundos
#         task_two_seconds.s(),
#         name="Run every 2 seconds."
#     )
#     sender.add_periodic_task(
#         3.0,  # Cada 3 segundos
#         task_three_seconds.s(),
#         name="Run every 3 seconds."
#     )
#     sender.add_periodic_task(
#         4.0,  # Cada 4 segundos
#         task_four_seconds.s(),
#         name="Run every 4 seconds."
#     )
#     sender.add_periodic_task(
#         5.0,  # Cada 5 segundos
#         task_five_seconds.s(),
#         name="Run every 5 seconds."
#     )

# @app.task
# def task_one_second():
#     print("Hello, I am the task that runs every 1 second.")

# @app.task
# def task_two_seconds():
#     print("Hello, I am the task that runs every 2 seconds.")

# @app.task
# def task_three_seconds():
#     print("Hello, I am the task that runs every 3 seconds.")

# @app.task
# def task_four_seconds():
#     print("Hello, I am the task that runs every 4 seconds.")

# @app.task
# def task_five_seconds():
#     print("Hello, I am the task that runs every 5 seconds.")

# if __name__ == "__main__":
#     app.start()

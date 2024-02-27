from celery import Celery

app = Celery('tasks', broker='tu_broker_aqui')

@app.task
def process_all_courses():
    processor = CourseProcessor()
    processor.process_courses()

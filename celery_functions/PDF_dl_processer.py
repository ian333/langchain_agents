from supabase import create_client
from decouple import config
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from langchain_community.vectorstores import DeepLake
from langchain_openai import OpenAIEmbeddings

class CourseProcessor:
    def __init__(self):
        os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
        os.environ["ACTIVELOOP_TOKEN"] = config("ACTIVELOOP_TOKEN")

        self.embeddings = OpenAIEmbeddings()

        url_admin = config("SUPABASE_ADMIN_URL")
        key_admin = config("SUPABASE_ADMIN_KEY")
        self.supabase = create_client(supabase_url=url_admin, supabase_key=key_admin)

        self.successful_courses = []
        self.failed_courses = []

    def process_courses(self):
        course_list = self.supabase.table("courses_tb").select("*").execute().data

        for course in course_list:
            try:
                self.process_course(course)
                self.successful_courses.append(f"{course['name']} ({course['id']})")
            except Exception as e:
                print(f"Error al procesar el curso {course['name']} ({course['id']}): {str(e)}")
                self.failed_courses.append(f"{course['name']} ({course['id']}): {str(e)}")

        self.generate_report()

    def process_course(self, course):
        reference_files = course["reference_files"]
        courseid = course["id"]

        if reference_files and isinstance(reference_files, list) and course['status'] != 'ready':
            for ref_file in reference_files:
                url = ref_file["url"]
                name = ref_file["name"]
                self.download_and_process_file(url, name, courseid)
        else:
            print(f"No hay archivos de referencia para el curso {course['name']} ({course['id']})")

    def download_and_process_file(self, file_url, file_name, courseid):
        response = self.supabase.storage.from_("CoursesFiles").download(file_url)
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file_name)

        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(response)

        self.process_pdf(temp_file_path, courseid)
        os.unlink(temp_file_path)


        self.process_pdf(temp_file_path, courseid)
        os.unlink(temp_file_path)

    def process_pdf(self, file_path, courseid):
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        DeepLake.from_documents(pages, self.embeddings, dataset_path=f"hub://skillstech/PDF-{courseid}",overwrite=True)
        self.supabase.table("courses_tb").update({"pdf_processed": "processed"}).eq("id", courseid).execute()


    def generate_report(self):
        print("Reporte de procesamiento de cursos:")
        print("Cursos procesados exitosamente:")
        for course in self.successful_courses:
            print(course)

        print("\nCursos que fallaron al procesarse:")
        for course in self.failed_courses:
            print(course)



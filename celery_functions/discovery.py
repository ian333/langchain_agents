# archivo: discovery.py
from decouple import config
from supabase import create_client, Client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import json
import os
from PyPDF2 import PdfReader
import tempfile
from Config.config import set_language, get_language
from Prompt_languages import english, spanish

class Discovery:
    def __init__(self):
        # Configuración de Supabase
        url_user = config("SUPABASE_ADMIN_URL")
        key_user = config("SUPABASE_ADMIN_KEY")
        self.supabase: Client = create_client(supabase_url=url_user, supabase_key=key_user)
        url_user: str = config("SUPABASE_USER_URL")
        key_user: str = config("SUPABASE_USER_KEY")
        self.supabase_user: Client = create_client(supabase_url=url_user, supabase_key=key_user)

        # Configuración de la API de Google
        os.environ["GOOGLE_API_KEY"] = config("GOOGLE_API_KEY")

        # Inicialización del modelo de lenguaje
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

        # Definición del prompt
        language = get_language()
        if language == "english":
            discovery = english.discovery
        elif language == "spanish":
            discovery = spanish.discovery
        self.promptSummary = PromptTemplate.from_template(discovery)

    def agent_creation(self, course_information, user_information, thread_metrics):
        """
        Summarize conversation using Gemini and a prompt
        """
        chain = self.promptSummary | self.llm
        result = chain.invoke({"course_information": course_information, "user_information": user_information, "thread_metrics": thread_metrics})
        return result.content

    def extract_pdf_info(self, pdf_url):
        response = self.supabase.storage.from_("CoursesFiles").download(pdf_url)
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, "temp.pdf")

        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(response)

        pdf_reader = PdfReader(temp_file_path)
        num_pages = len(pdf_reader.pages)
        extracted_text = ""

        # Extraer texto de dos páginas aleatorias
        for page_num in range(min(2, num_pages)):
            page = pdf_reader.pages[page_num]
            extracted_text += page.extract_text() + "\n"

        os.unlink(temp_file_path)
        return extracted_text

    def process_courses(self, course_ids=None):
        query = self.supabase.table('courses_tb').select("*")
        if course_ids:
            query = query.in_("id", course_ids)
        courses = query.execute().data

        for course in courses:
            course_info = ""
            tb = self.supabase_user.table("threads_tb").select("*").eq("courseid", course["id"]).execute().data
            user_data = ""
            thread_metrics = ""

            for data in tb:
                user_data += str(data["thread_summary"])
                thread_metrics += str(data["thread_metrics"])

            print(user_data)
            print(thread_metrics)

            name = str(course.get("name", ""))
            general_objective = str(course.get("general_objective", ""))
            module_objective = str(course.get("module_objective", ""))
            syllabus = str(course.get("syllabus", ""))

            course_info = name + general_objective + module_objective + syllabus

            # Extraer información de los PDFs asociados al curso
            reference_files = course.get("reference_files", [])
            for ref_file in reference_files:
                pdf_url = ref_file["url"]
                course_info += self.extract_pdf_info(pdf_url)

            print(course_info)
            response = self.agent_creation(course_information=course_info, user_information=user_data, thread_metrics=thread_metrics)
            response = response.replace('```JSON\n', '').replace('```json\n', '').replace('\n```', '').strip()

            try:
                data = json.loads(response)
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError as e:
                print(f"JSON decoding failed: {e}")
                print(f"Original response: {response}")

            self.supabase.table("courses_tb").update({"categories": data}).eq("id", course["id"]).execute()


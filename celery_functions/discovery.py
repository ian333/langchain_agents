# archivo: discovery.py
from decouple import config
from supabase import create_client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import json
import os

class Discovery:
    def __init__(self):
        # Configuración de Supabase
        url_user = config("SUPABASE_ADMIN_URL")
        key_user = config("SUPABASE_ADMIN_KEY")
        self.supabase = create_client(supabase_url=url_user, supabase_key=key_user)

        # Configuración de la API de Google
        os.environ["GOOGLE_API_KEY"] = config("GOOGLE_API_KEY")

        # Inicialización del modelo de lenguaje
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro")

        # Definición del prompt
        self.promptSummary = PromptTemplate.from_template(
            """
            Analyze the following course information and categorize it into the given format.
            {course_information}

            You MUST organize the information into the following structure:

            categories:
              - name: "Category Name"
                threads:
                  - "Thread 1"
                  - "Thread 2"
                  - "Thread 3"
                icon_url: "Icon URL"
                description: "Description of the category"

            Use the given course details to fill in the following categories: Data Collection, Data Cleaning, Exploratory Data Analysis, Machine Learning, Statistical Analysis, and Big Data Technologies. Include the respective course modules, topics, and descriptions accordingly.

            Here are two examples of the desired output format:

            Example 1:
            categories:
              - name: "Data Collection"
                threads:
                  - "Survey Design and Sampling Methods"
                  - "Web Scraping and APIs"
                  - "Data Storage and Management"
                icon_url: "https://example.com/icons/data-collection.png"
                description: "Methods and tools for gathering data"
              - name: "Data Cleaning"
                threads:
                  - "Handling Missing Values"
                  - "Data Transformation and Normalization"
                  - "Outlier Detection and Treatment"
                icon_url: "https://example.com/icons/data-cleaning.png"
                description: "Preparing raw data for analysis"

            Example 2:
            categories:
              - name: "Exploratory Data Analysis"
                threads:
                  - "Descriptive Statistics"
                  - "Data Visualization Techniques"
                  - "Identifying Patterns and Trends"
                icon_url: "https://example.com/icons/exploratory-data-analysis.png"
                description: "Analyzing data to uncover insights"
              - name: "Machine Learning"
                threads:
                  - "Supervised Learning Algorithms"
                  - "Unsupervised Learning Techniques"
                  - "Model Evaluation and Validation"
                icon_url: "https://example.com/icons/machine-learning.png"
                description: "Building predictive models"

            ALWAYS give me the answer in the specified JSON format.
            """
        )

    def agent_creation(self, course_information):
        """
        Summarize conversation using Gemini and a prompt
        """
        chain = self.promptSummary | self.llm
        result = chain.invoke({"course_information": course_information})
        return result.content

    def process_courses(self):
        courses = self.supabase.table('courses_tb').select("*").execute().data

        for course in courses:
            name = str(course.get("name", ""))
            general_objective = str(course.get("general_objective", ""))
            module_objective = str(course.get("module_objective", ""))
            syllabus = str(course.get("syllabus", ""))
            
            course_info = name + general_objective + module_objective + syllabus
            print(course_info)
            response = self.agent_creation(course_information=course_info)
            response = response.replace('```JSON\n', '').replace('```json\n', '').replace('\n```', '').strip()

            try:
                data = json.loads(response)
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError as e:
                print(f"JSON decoding failed: {e}")
                print(f"Original response: {response}")

            self.supabase.table("courses_tb").update({"categories": data}).eq("id", course["id"]).execute()

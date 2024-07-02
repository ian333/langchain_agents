import yt_dlp
from langchain.document_loaders import AssemblyAIAudioTranscriptLoader
from langchain_community.vectorstores import DeepLake
from langchain_openai import OpenAIEmbeddings
import yt_dlp
from yt_dlp.utils import DownloadError

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.assemblyai import TranscriptFormat

from langchain.document_loaders import AssemblyAIAudioTranscriptLoader
from langchain_community.vectorstores import DeepLake
from langchain_openai import OpenAIEmbeddings
import assemblyai as aai
import os 
import json

import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from langchain_community.vectorstores import DeepLake
from langchain_openai import OpenAIEmbeddings


from decouple import config
from supabase import create_client, Client
aai.settings.api_key = "26f195ae63cf434280dd530fb61d6981"


url_user: str = config("SUPABASE_USER_URL")
key_user: str = config("SUPABASE_USER_KEY")
supabase_user:Client = create_client(supabase_url=url_user,supabase_key= key_user)

os.environ["ACTIVELOOP_TOKEN"] = config("ACTIVELOOP_TOKEN")



class YouTubeTranscription:
    def __init__(self, course_id=None):
        self.course_id = course_id
        self.embeddings = OpenAIEmbeddings()
        url_admin: str = config("SUPABASE_ADMIN_URL")
        key_admin: str = config("SUPABASE_ADMIN_KEY")

        self.supabase:Client = create_client(supabase_url=url_admin,supabase_key= key_admin)

    def get_transcript_yt(self, YT_URL):
        try:
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(YT_URL, download=False)
            if "entries" in info:
                info = info["entries"][0]
            YT_title = info.get('title', None)

            if "formats" not in info:
                print(f"Formats key not found in info dictionary for video {YT_URL}. Skipping...")
                return None, None, None

            audio_url = None
            for format in info["formats"][::-1]:
                if format["acodec"] != "none":
                    audio_url = format["url"]
                    break

            return YT_URL, YT_title, audio_url
        except DownloadError as e:
            print(f"Error downloading video {YT_URL}: {e}")
            return None, None, None
        
    def url_to_docs(self, YT_URL, YT_title, audio_url):
        config = aai.TranscriptionConfig(
                language_detection=True,
                #auto_highlights=True,
                #summarization=True, summarization incompatible with auto_chapters
                #auto_chapters=True,
                )
        loader = AssemblyAIAudioTranscriptLoader(audio_url,config=config,transcript_format=TranscriptFormat.PARAGRAPHS,)
        docs = loader.load()
        for doc in docs:
                doc.metadata = {"source": YT_URL, "title": YT_title, "start":doc.metadata["start"], "end":doc.metadata["end"]}
        return docs

    def docs_to_deeplakeDB(self, docs,course_id):
        dataset_path = f"./skillstech/VIDEO-{self.course_id}" if self.course_id else "default_path"
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
        texts=[]
        print(docs)
        print("😁😁😁😁 se esta procesando el curso")

        documents_str = '\n'.join([json.dumps(docs, indent=None, default=str)])
        print(documents_str)
        self.supabase.table("courses_tb").update({"video_docs_vdb": documents_str}).eq("id", course_id).execute()

        vectorstore = DeepLake(dataset_path=dataset_path, embedding=self.embeddings, overwrite=False)
        vectorstore.add_documents(docs)
#   "https://www.youtube.com/watch?v=dbQjFzOgpzg"


class CourseVideoProcessor:
    def __init__(self):
        url_admin: str = config("SUPABASE_ADMIN_URL")
        key_admin: str = config("SUPABASE_ADMIN_KEY")

        self.supabase:Client = create_client(supabase_url=url_admin,supabase_key= key_admin)

    def process_all_courses(self):
        courses_data = self.supabase.table("courses_tb").select("*").execute().data
        for course in courses_data:

            if course['reference_videos'] and course['video_processed'] != 'FALSE':
                print("😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍 SE ESTA PROCESANDO EL video y este es el course id",course['id'])
                self.transcriber = YouTubeTranscription(course_id=course['id'])
                for video_url in course['reference_videos']:
                    if video_url:  # Asegurar que la URL no está vacía
                        URL, title, audio_url = self.transcriber.get_transcript_yt(video_url)
                        if URL and title and audio_url:  # Asegurar que todos los componentes son válidos
                            
                            docs = self.transcriber.url_to_docs(URL, title, audio_url)
                            self.transcriber.docs_to_deeplakeDB(docs,course_id=course['id'])
                print("😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍 SE ESTA CAMBIANDO A TRUe video y este es el course id",course['id'])

                video=self.supabase.table("courses_tb").update({"video_processed": "TRUE"}).eq("id", course['id']).execute()
                status=self.supabase.table("courses_tb").update({"status": "ready"}).eq("id", course['id']).execute()
                print(video)
                print(status)
                print("😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍  SE CAMBIO A  TRUE video")
    
    def update_all_courses(self):
        courses_data = self.supabase.table("courses_tb").select("*").execute().data
        for course in courses_data:
            if course['videos_to_update']:
                self.supabase.table("courses_tb").update({"status": "processing"}).eq("id", course['id']).execute()
                self.transcriber = YouTubeTranscription(course_id=course['id'])
                for video_url in course['videos_to_update']:
                    if video_url:  # Asegurar que la URL no está vacía
                        URL, title, audio_url = self.transcriber.get_transcript_yt(video_url)
                        if URL and title and audio_url:  # Asegurar que todos los componentes son válidos
                            docs = self.transcriber.url_to_docs(URL, title, audio_url)
                            self.transcriber.docs_to_deeplakeDB(docs,course_id=course['id'])
                print("😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍 SE ESTA CAMBIANDO A TRUe video")

                video=self.supabase.table("courses_tb").update({"video_processed": "TRUE"}).eq("id", course['id']).execute()
                self.supabase.table("courses_tb").update({"videos_to_update": ""}).eq("id", course['id']).execute()

                status=self.supabase.table("courses_tb").update({"status": "ready"}).eq("id", course['id']).execute()
                print(video)
                print(status)
                print("😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍  SE CAMBIO A  TRUE video")
    



class CourseProcessor:
    def __init__(self):
        os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
        os.environ["ACTIVELOOP_TOKEN"] = config("ACTIVELOOP_TOKEN")

        self.embeddings = OpenAIEmbeddings()

        url_admin = config("SUPABASE_ADMIN_URL")
        key_admin = config("SUPABASE_ADMIN_KEY")
        self.supabase:Client = create_client(supabase_url=url_admin, supabase_key=key_admin)

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

        if reference_files and isinstance(reference_files, list) and course['pdf_processed'] != 'FALSE':
            for ref_file in reference_files:
                url = ref_file["url"]
                name = ref_file["name"]
                self.download_and_process_file(file_url=url, file_name=name, courseid=courseid)
        else:
            print(f"No hay archivos de referencia para el curso {course['name']} ({course['id']})")

    def download_and_process_file(self, file_url, file_name, courseid):
        print("😁😁😁😁😁😁😁",file_url)

        response = self.supabase.storage.from_("CoursesFiles").download(file_url)
        print(response)
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file_name)
        print(temp_dir)
        print(temp_file_path)


        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(response)

        self.process_pdf(file_path=temp_file_path, courseid=courseid)
        os.unlink(temp_file_path)



    

    def vector_pdf_database(self,courseid,pages):
        print("vector_pdf_database")

        DeepLake.from_documents(pages, self.embeddings, dataset_path=f"./skillstech/PDF-{courseid}",overwrite=False)
        print("😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍 SE ESTA CAMBIANDO A TRU PDF",courseid)
        save=self.supabase.table("courses_tb").update({"pdf_processed": "TRUE"}).eq("id", courseid).execute()
        print(save)
        print("😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍  SE CAMBIO A  TRUE PDF")
    
    
    def process_pdf(self,  courseid,file_path=None):
        print("funcion process_pdf")
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        print(pages)

        self.vector_pdf_database(pages=pages,courseid=courseid)

    def generate_report(self):
        print("Reporte de procesamiento de cursos:")
        print("Cursos procesados exitosamente:")
        for course in self.successful_courses:
            print(course)

        print("\nCursos que fallaron al procesarse:")
        for course in self.failed_courses:
            print(course)

    def update_pdf(self):
        print("😁😁😁😁😁😁😁 estamos actualizando pdfs")
        course_list = self.supabase.table("courses_tb").select("*").execute().data
        for course in course_list:
            # try:
                if course["pdf_to_update"]:
                    reference_files = course["pdf_to_update"]
                    courseid = course["id"]
                    self.supabase.table("courses_tb").update({"status": "processing"}).eq("id", courseid).execute()


                    if reference_files:
                        for ref_file in reference_files:
                            url = ref_file["url"]
                            name = ref_file["name"]
                            print("😁😁😁😁😁😁😁😁 este es el url del file que se esta actualizando",url)
                            self.download_and_process_file(file_url=url, file_name=name, courseid=courseid)
                    else:
                        print(f"No hay archivos de referencia para el curso {course['name']} ({course['id']})")

                    self.successful_courses.append(f"{course['name']} ({course['id']})")
                    self.supabase.table("courses_tb").update({"status": "ready"}).eq("id", courseid).execute()
                    self.supabase.table("courses_tb").update({"pdf_to_update": ""}).eq("id", courseid).execute()


            # except Exception as e:
            #     print(f"Error al procesar el curso {course['name']} ({course['id']}): {str(e)} esta es la url {url}")
            #     self.failed_courses.append(f"{course['name']} ({course['id']}): {str(e)}")



class CourseFactsProcessor:
    def __init__(self):
        os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
        os.environ["ACTIVELOOP_TOKEN"] = config("ACTIVELOOP_TOKEN")

        self.embeddings = OpenAIEmbeddings()

        url_admin = config("SUPABASE_ADMIN_URL")
        key_admin = config("SUPABASE_ADMIN_KEY")
        self.supabase:Client = create_client(supabase_url=url_admin, supabase_key=key_admin)

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

        if reference_files and isinstance(reference_files, list) and course['pdf_processed'] != 'TRUE':
            for ref_file in reference_files:
                url = ref_file["url"]
                name = ref_file["name"]
                self.download_and_process_file(file_url=url, file_name=name, courseid=courseid)
        else:
            print(f"No hay archivos de referencia para el curso {course['name']} ({course['id']})")

    def download_and_process_file(self, file_url, file_name, courseid):
        print("😁😁😁😁😁😁😁😁 este es el url del file",file_url)
        response = self.supabase.storage.from_("CoursesFiles").download(file_url)
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file_name)

        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(response)

        self.process_pdf(temp_file_path, courseid)
        os.unlink(temp_file_path)



    

    def vector_pdf_database(self,courseid,pages):

        DeepLake.from_documents(pages, self.embeddings, dataset_path=f"hub://skillstech/FACTS-{courseid}",overwrite=False)
        print("😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍 SE ESTA CAMBIANDO A TRU PDF",courseid)
        save=self.supabase.table("courses_tb").update({"pdf_processed": "TRUE"}).eq("id", courseid).execute()
        print(save)
        print("😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍  SE CAMBIO A  TRUE PDF")
    
    
    def process_pdf(self,  courseid,file_path=None):
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()

        self.vector_pdf_database(pages=pages,courseid=courseid)

    def generate_report(self):
        print("Reporte de procesamiento de cursos:")
        print("Cursos procesados exitosamente:")
        for course in self.successful_courses:
            print(course)

        print("\nCursos que fallaron al procesarse:")
        for course in self.failed_courses:
            print(course)

    def update_pdf(self):
        course_list = self.supabase.table("courses_tb").select("*").execute().data
        for course in course_list:
            try:
                reference_files = course["pdf_to_update"]
                courseid = course["id"]
                if reference_files :
                    for ref_file in reference_files:
                        self.supabase.table("courses_tb").update({"status": "processing"}).eq("id", courseid).execute()
                        url = ref_file["url"]
                        name = ref_file["name"]
                        print("😁😁😁😁😁😁😁😁 este es el url del file que se esta actualizando",url)

                        self.download_and_process_file(file_url=url, file_name=name, courseid=courseid)
                else:
                    print(f"No hay archivos de referencia para el curso {course['name']} ({course['id']})")

                self.successful_courses.append(f"{course['name']} ({course['id']})")
                self.supabase.table("courses_tb").update({"status": "ready"}).eq("id", courseid).execute()
                self.supabase.table("courses_tb").update({"pdf_to_update": ""}).eq("id", courseid).execute()


            except Exception as e:
                print(f"Error al procesar el curso {course['name']} ({course['id']}): {str(e)}")
                self.failed_courses.append(f"{course['name']} ({course['id']}): {str(e)}")


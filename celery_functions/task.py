import os
import json
import yt_dlp
from yt_dlp.utils import DownloadError
from langchain_core.documents import Document
from langchain.document_loaders import AssemblyAIAudioTranscriptLoader
from langchain_community.vectorstores import DeepLake
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.assemblyai import TranscriptFormat
import assemblyai as aai
from decouple import config
from supabase import create_client,Client
import time
import glob

# Configuración de las API Keys
aai.settings.api_key = config("ASSEMBLYAI_API_KEY")

url_user = config("SUPABASE_USER_URL")
key_user = config("SUPABASE_USER_KEY")
supabase_user = create_client(supabase_url=url_user, supabase_key=key_user)

class YouTubeTranscription:
    def __init__(self, course_id=None):
        self.course_id = course_id
        self.embeddings = OpenAIEmbeddings()
        
        url_admin = config("SUPABASE_ADMIN_URL")
        key_admin = config("SUPABASE_ADMIN_KEY")
        self.supabase = create_client(supabase_url=url_admin, supabase_key=key_admin)

    def get_video_info(self, YT_URL):
        try:
            print(f"\033[92mFetching information for URL: {YT_URL}\033[0m")
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(YT_URL, download=False)
            print(f"\033[92mExtracted info: {info}\033[0m")
            
            if "entries" in info:
                info = info["entries"][0]
            YT_title = info.get('title', None)

            if "formats" not in info:
                print(f"\033[91mFormats key not found in info dictionary for video {YT_URL}. Skipping...\033[0m")
                return None, None
            
            return YT_URL, YT_title
        except DownloadError as e:
            print(f"\033[91mError downloading video info {YT_URL}: {e}\033[0m")
            return None, None

    def download_audio(self, YT_URL, output_path):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'keepvideo': True,  # Añadir esta opción
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([YT_URL])
            print(f"\033[92mDownloaded audio to: {output_path}\033[0m")
            return output_path
        except Exception as e:
            print(f"\033[91mError downloading audio: {e}\033[0m")
            return None


    def url_to_docs(self, YT_URL, YT_title, audio_url):
        # Crear directorio para el curso si no existe
        course_dir = f"./audio_files/{self.course_id}"
        os.makedirs(course_dir, exist_ok=True)
        output_path = f"{course_dir}/{YT_title}.mp3"  # Guardar en directorio del curso
        
        downloaded_path = self.download_audio(YT_URL, output_path)
        if not downloaded_path:
            print(f"\033[91mFailed to download audio from URL: {audio_url}\033[0m")
            return []

        print(f"\033[92mTranscribing audio from file: {downloaded_path}\033[0m")
        config = aai.TranscriptionConfig(
                language_detection=True,
                )
        loader = AssemblyAIAudioTranscriptLoader(downloaded_path, config=config, transcript_format=TranscriptFormat.PARAGRAPHS)
        docs = loader.load()
        for doc in docs:
            doc.metadata = {"source": YT_URL, "title": YT_title, "start": doc.metadata["start"], "end": doc.metadata["end"]}
        return docs
    
    def docs_to_deeplakeDB(self, docs, course_id):
        dataset_path = f"./skillstech/VIDEO-{self.course_id}" if self.course_id else "default_path"
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
        texts = []

        for document in docs:
            if isinstance(document, list):
                for doc in document:
                    if isinstance(doc, Document):
                        texts.extend(text_splitter.split_documents([doc]))
                    else:
                        print(f"\033[91mSkipping non-Document item: {doc}\033[0m")
            elif isinstance(document, Document):
                texts.extend(text_splitter.split_documents([document]))
            else:
                print(f"\033[91mSkipping non-Document item: {document}\033[0m")

        print(f"\033[92mSplit texts: {texts}\033[0m")

        if not texts:
            print("\033[91mNo texts to add to DeepLake. Skipping...\033[0m")
            return

        documents_str = '\n'.join([json.dumps(doc.metadata, indent=None, default=str) for doc in texts])
        print(f"\033[92mDocuments string to be stored: {documents_str}\033[0m")

        self.supabase.table("courses_tb").update({"video_docs_vdb": documents_str}).eq("id", course_id).execute()
        print(f"\033[92mUpdated video_docs_vdb for course ID: {course_id}\033[0m")

        vectorstore = DeepLake(dataset_path=dataset_path, embedding=self.embeddings, overwrite=True)
        vectorstore.add_documents(texts)
        print(f"\033[92mAdded documents to DeepLake at dataset path: {dataset_path}\033[0m")

class CourseVideoProcessor:
    def __init__(self):
        url_admin = config("SUPABASE_ADMIN_URL")
        key_admin = config("SUPABASE_ADMIN_KEY")
        self.lista_de_docs = []
        self.supabase = create_client(supabase_url=url_admin, supabase_key=key_admin)

    def process_all_courses(self):
        courses_data = self.supabase.table("courses_tb").select("*").execute().data
        for course in courses_data:
            if course['reference_videos'] and course['local_video_processed'] != 'TRUE':
                save=self.supabase.table("courses_tb").update({"local_pdf_processed": "TRUE"}).eq("id", course['id']).execute()

                self.transcriber = YouTubeTranscription(course_id=course['id'])
                print(f"\033[96mProcessing course: {course['id']}\033[0m")
                for video_url in course['reference_videos']:
                    if video_url:
                        URL, title = self.transcriber.get_video_info(video_url)
                        if URL and title:
                            audio_url = URL  # La URL del video de YouTube será usada para descargar el audio
                            docs = self.transcriber.url_to_docs(URL, title, audio_url)
                            if isinstance(docs, list):
                                for doc in docs:
                                    if isinstance(doc, Document):
                                        self.lista_de_docs.append(doc)
                            elif isinstance(docs, Document):
                                self.lista_de_docs.append(docs)
                            else:
                                print(f"\033[91mSkipping non-Document item in docs: {docs}\033[0m")
                print(f"\033[96mDocuments list: {self.lista_de_docs}\033[0m")
                self.transcriber.docs_to_deeplakeDB(self.lista_de_docs, course_id=course['id'])
                self.supabase.table("courses_tb").update({"local_video_processed": "TRUE"}).eq("id", course['id']).execute()
                print(f"\033[96mMarked local_video_processed as TRUE for course ID: {course['id']}\033[0m")
                self.lista_de_docs = []

    def reset_processed_columns(self):
        courses_data = self.supabase.table("courses_tb").select("*").execute().data
        for course in courses_data:
            self.supabase.table("courses_tb").update({"local_video_processed": "FALSE", "local_pdf_processed": "FALSE"}).eq("id", course["id"]).execute()
        print("\033[96mTodas las columnas local_video_processed y local_pdf_processed han sido actualizadas a FALSE.\033[0m")

    def clean_temp_files(self, directory="/tmp", age_in_seconds=86400):
        now = time.time()
        for filename in glob.glob(f"{directory}/*"):
            if os.path.isfile(filename):
                file_age = now - os.path.getmtime(filename)
                if file_age > age_in_seconds:
                    os.remove(filename)
                    print(f"\033[92mDeleted old temp file: {filename}\033[0m")


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

        if reference_files and isinstance(reference_files, list) and course['local_pdf_processed'] != 'TRUE':
            save=self.supabase.table("courses_tb").update({"local_pdf_processed": "TRUE"}).eq("id", courseid).execute()
            for ref_file in reference_files:
                url = ref_file["url"]
                name = ref_file["name"]
                self.download_and_process_file(file_url=url, file_name=name, courseid=courseid)
        else:
            print(f"No hay archivos de referencia para el curso {course['name']} ({course['id']})")

    def download_and_process_file(self, file_url, file_name, courseid):
        print("😁😁😁😁😁😁😁",file_url)

        response = self.supabase.storage.from_("CoursesFiles").download(file_url)
        # print(response)
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file_name)
        # print(temp_dir)
        # print(temp_file_path)


        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(response)

        self.process_pdf(file_path=temp_file_path, courseid=courseid)
        os.unlink(temp_file_path)



    

    def vector_pdf_database(self,courseid,pages):
        print("vector_pdf_database")

        DeepLake.from_documents(pages, self.embeddings, dataset_path=f"./skillstech/PDF-{courseid}",overwrite=False)
        # print("😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍 SE ESTA CAMBIANDO A TRU PDF",courseid)

        # print(save)
        # print("😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍  SE CAMBIO A  TRUE PDF")
    
    
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

import tempfile
from langchain_community.document_loaders import PyPDFLoader

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


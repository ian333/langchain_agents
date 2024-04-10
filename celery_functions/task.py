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
aai.settings.api_key = "26f195ae63cf434280dd530fb61d6981"
import os 

from decouple import config
from supabase import create_client

url_user: str = config("SUPABASE_USER_URL")
key_user: str = config("SUPABASE_USER_KEY")
supabase_user = create_client(supabase_url=url_user,supabase_key= key_user)

os.environ["ACTIVELOOP_TOKEN"] = config("ACTIVELOOP_TOKEN")

class YouTubeTranscription:
    def __init__(self, course_id=None):
        self.course_id = course_id
        self.embeddings = OpenAIEmbeddings()

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

    def docs_to_deeplakeDB(self, docs):
        dataset_path = f"hub://skillstech/VIDEO-{self.course_id}" if self.course_id else "default_path"
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
        texts = text_splitter.split_documents(docs)
        vectorstore = DeepLake(dataset_path=dataset_path, embedding=self.embeddings, overwrite=False)
        vectorstore.add_documents(texts)


class CourseVideoProcessor:
    def __init__(self):
        url_admin: str = config("SUPABASE_ADMIN_URL")
        key_admin: str = config("SUPABASE_ADMIN_KEY")

        self.supabase = create_client(supabase_url=url_admin,supabase_key= key_admin)

    def process_all_courses(self):
        courses_data = self.supabase.table("courses_tb").select("*").execute().data
        for course in courses_data:
            if course['reference_videos'] and course['status'] != 'ready':
                self.transcriber = YouTubeTranscription(course_id=course['id'])
                for video_url in course['reference_videos']:
                    if video_url:  # Asegurar que la URL no está vacía
                        URL, title, audio_url = self.transcriber.get_transcript_yt(video_url)
                        if URL and title and audio_url:  # Asegurar que todos los componentes son válidos
                            docs = self.transcriber.url_to_docs(URL, title, audio_url)
                            self.transcriber.docs_to_deeplakeDB(docs)
                self.supabase.table("courses_tb").update({"pdf_processed": "TRUE"}).eq("id", course['id']).execute()



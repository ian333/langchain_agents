import yt_dlp
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_openai import ChatOpenAI
from langchain.document_loaders import AssemblyAIAudioTranscriptLoader
from langchain_community.document_loaders.assemblyai import TranscriptFormat
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import DeepLake
import os
import re
import assemblyai as aai

import assemblyai as aai
aai.settings.api_key = "26f195ae63cf434280dd530fb61d6981"
import yt_dlp
from langchain.document_loaders import AssemblyAIAudioTranscriptLoader
from langchain_community.vectorstores import DeepLake
from langchain_openai import OpenAIEmbeddings

class YouTubeTranscription:
    def __init__(self, course_id=None):
        self.course_id = course_id
        self.embeddings = OpenAIEmbeddings()

    def get_transcript_yt(self, YT_URL):
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(YT_URL, download=False)
            YT_title = info.get('title', None)
            audio_url = None
            for format in info["formats"][::-1]:
                if format["acodec"] != "none":
                    audio_url = format["url"]
                    break
        return YT_URL, YT_title, audio_url

    def url_to_docs(self, YT_URL, YT_title, audio_url):
        loader = AssemblyAIAudioTranscriptLoader(audio_url)
        docs = loader.load_and_split()
        for doc in docs:
            doc.metadata = {"source": YT_URL, "title": YT_title}
        return docs

    def docs_to_deeplakeDB(self, docs):
        dataset_path = f"hub://skillstech/VIDEO-{self.course_id}" if self.course_id else "default_path"
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
        texts = text_splitter.split_documents(docs)
        vectorstore = DeepLake(dataset_path=dataset_path, embedding=self.embeddings, overwrite=False)
        vectorstore.add_documents(texts)

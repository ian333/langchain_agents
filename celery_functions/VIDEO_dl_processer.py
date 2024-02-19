from langchain_community.document_loaders import PyPDFLoader
import tempfile
import os
from langchain.schema import Document
from langchain_community.vectorstores import DeepLake
from langchain_openai import OpenAIEmbeddings
from decouple import config
from database.supa import supabase_user,supabase_admin  # Importar los clientes de Supabase
from supabase import create_client
from decouple import config
os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
os.environ["ACTIVELOOP_TOKEN"] = config("ACTIVELOOP_TOKEN")

url_admin: str = config("SUPABASE_ADMIN_URL")
key_admin: str = config("SUPABASE_ADMIN_KEY")

supabase_admin_2 = create_client(supabase_url=url_admin,supabase_key= key_admin)
admin_data = supabase_admin.table("courses_tb").select("*").eq("id", "ba86e360-577c-4145-baac-974611be0872").execute().data[0]
admin_data

embeddings = OpenAIEmbeddings()
username_or_org = "<USERNAME_OR_ORG>"

courseid="73e5618f-e2c0-476e-87d3-43d352f14ee0"
for file in files:
    if file["metadata"]["mimetype"]=="application/pdf":
      file_path = f"{carpeta}/{file['name']}"
      print(f"Descargando archivo: {file_path}")

      # Descargar el contenido del archivo
      response = supabase_user.storage.from_(bucket_name).download(file_path)
      # Crear un directorio temporal
      temp_dir = tempfile.mkdtemp()
      temp_file_path = os.path.join(temp_dir, file['name'])

      # Guardar el contenido descargado en un archivo dentro del directorio temporal
      with open(temp_file_path, 'wb') as temp_file:
          temp_file.write(response)

      print(f"Archivo temporal creado: {temp_file_path}")

      # Cargar el archivo PDF desde la ruta temporal y procesarlo
      loader = PyPDFLoader(temp_file.name)
      pages = loader.load_and_split()
      print(pages)
      vectorstore = DeepLake.from_documents(
      pages,
      embeddings,
      dataset_path=f"hub://skillstech/PDF-{courseid}",
  )

      # Opcional: eliminar el archivo temporal después de procesarlo
      os.unlink(temp_file.name)

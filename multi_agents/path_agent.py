from fastapi import FastAPI, HTTPException, status, Form
from pydantic import BaseModel
from uuid import uuid4
from database.supa import supabase_user
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from datetime import datetime, timezone
import os
from decouple import config
import uuid

from Prompt_languages import english, spanish

# Configuración del idioma
language = "english"  # Cambiar a "spanish" para español

# Importar las configuraciones según el idioma seleccionado
path_prompt_template=""
if language == "english":
    path_prompt_template = english.path_prompt_template
    state_modifier_path_details = english.state_modifier_path_details
    state_modifier_path_topics = english.state_modifier_path_topics
    state_modifier_subtopics = english.state_modifier_subtopics
    topic_prompt_template = english.topic_prompt_template
    subtopic_prompt_template = english.subtopic_prompt_template
    prompts_for_subtopics_template = english.prompts_for_subtopics_template

elif language == "spanish":
    path_prompt_template = spanish.path_prompt_template
    state_modifier_path_details = spanish.state_modifier_path_details
    state_modifier_path_topics = spanish.state_modifier_path_topics
    state_modifier_subtopics = spanish.state_modifier_subtopics
    topic_prompt_template = spanish.topic_prompt_template
    subtopic_prompt_template = spanish.subtopic_prompt_template
    prompts_for_subtopics_template = spanish.prompts_for_subtopics_template

# Ahora puedes usar las variables según el idioma seleccionado en tu código.


# Configurar la API de Google
os.environ["GOOGLE_API_KEY"] = config("GOOGLE_API_KEY")



async def generate_path_details(topic: str,pathid:str):
    print(f"\033[94m[INFO] Iniciando la generación del nombre y descripción del Path para el tema: {topic}\033[0m")
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        print(f"\033[92m[INFO] Modelo LLM 'gemini-1.5-pro' inicializado correctamente.\033[0m")
        
        app = create_react_agent(
            model=llm, 
            tools=[], 
            state_modifier=state_modifier_path_details
        )
        print(f"\033[92m[INFO] Agente creado exitosamente.\033[0m")
        formatted_prompt = path_prompt_template.format(topic=topic)
        
        messages = app.invoke({"messages": [("human", formatted_prompt)]})
        
        content = messages["messages"][-1].content.split("\n\n", 1)
        name = content[0].strip()
        description = content[1].strip()
        print(f"\033[92m[INFO] Nombre y descripción generados con éxito: {name}, {description}\033[0m")
        
        return name, description
    
    except Exception as e:
        print(f"\033[91m[ERROR] Error al generar el nombre y la descripción del Path: {e}\033[0m")
        raise


async def generate_path_topics(path_name: str, max_items: int = 5, language: str = 'es'):
    print(f"\033[94m[INFO] Iniciando la generación de temas para el Path: {path_name}\033[0m")
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        print(f"\033[92m[INFO] Modelo LLM 'gemini-1.5-pro' inicializado correctamente.\033[0m")
        
        # Configuración del agente dependiendo del idioma
        app = create_react_agent(
            model=llm, 
            tools=[], 
            state_modifier=state_modifier_path_topics
        )
        print(f"\033[92m[INFO] Agente creado exitosamente.\033[0m")
        
        topic_prompt = f"Por favor, genera una lista de títulos de temas para un Path de aprendizaje llamado '{path_name}', SOLO GENERA 5 TEMAS SOLO 5con un enfoque en proporcionar un flujo educativo lógico y claro., POR FAVOR RESPONDE SOLO CON LOS TITULOS O CON LOS TOPICS, solo la lista de los topics{max_items}"
        messages = app.invoke({"messages": [("human", topic_prompt)]})
        topics = [topic.strip() for topic in messages["messages"][-1].content.split("\n") if topic.strip()]
        print(f"\033[92m[INFO] Temas generados con éxito: {topics}\033[0m")
        
        return topics
    
    except Exception as e:
        print(f"\033[91m[ERROR] Error al generar los temas del Path: {e}\033[0m")
        raise


async def generate_subtopics_for_topic(topic_name: str, path_name: str, language: str = 'es', max_subtopics: int = 5):
    print(f"\033[94m[INFO] Iniciando la generación de subtemas para el topic: {topic_name} en el Path: {path_name}\033[0m")

    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        print(f"\033[92m[INFO] Modelo LLM 'gemini-1.5-pro' inicializado correctamente.\033[0m")
    except Exception as e:
        print(f"\033[91m[ERROR] Error al inicializar el modelo LLM: {e}\033[0m")
        raise

    try:
        # Configurar el agente dependiendo del idioma

        app = create_react_agent(
            model=llm, 
            tools=[], 
            state_modifier=state_modifier_subtopics
        )
        print(f"\033[92m[INFO] Agente creado exitosamente.\033[0m")

        # Generar los subtopics
        subtopic_prompt = subtopic_prompt_template.format(topic_name=topic_name, path_name=path_name)


        messages = app.invoke({"messages": [("human", subtopic_prompt)]})
        
        # Filtrar los subtemas para eliminar encabezados y otros elementos no deseados
        subtopics = [subtopic.strip() for subtopic in messages["messages"][-1].content.split("\n") if subtopic.strip()]
        
        print(f"\033[92m[INFO] Subtemas generados con éxito: {subtopics}\033[0m")

        return subtopics
    
    except Exception as e:
        print(f"\033[91m[ERROR] Error al generar los subtemas del topic: {e}\033[0m")
        raise

    
async def create_article_and_subtopics_for_topic(topic_name: str, pathid: str, topicid: str, courseid: str, projectid: str, memberid: str, orgid: str, path_name: str):
    # Crear tareas para la creación de artículos y subtopics
    tasks = [
        asyncio.create_task(create_article_for_topic(topic_name=topic_name, pathid=pathid, courseid=courseid, projectid=projectid, memberid=memberid, orgid=orgid)),
        asyncio.create_task(save_subtopics_to_db(pathid, topicid, topic_name, path_name))
    ]

    # Ejecutar todas las tareas en paralelo
    await asyncio.gather(*tasks)

import asyncio
async def process_and_save_subtopic(pathid: str, topicid: str, subtopicid: str, subtopic_name: str, topic_name: str, path_name: str, order: int):
    # Create a task to generate prompts
    prompts_task = asyncio.create_task(generate_prompts_for_subtopics(subtopic_name, topic_name, path_name))
    prompts=await asyncio.gather(prompts_task)

    # Save subtopic to the database
    result = supabase_user.table("paths_subtopics_tb").insert({
        "id": subtopicid,
        "pathid": pathid,
        "topicid": topicid,
        "name": subtopic_name,
        "order": order,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    if not result or "error" in result:
        print(f"\033[91m[ERROR] Error al guardar el subtema en la tabla 'paths_subtopics_tb': {result.get('error')}\033[0m")
        raise HTTPException(status_code=500, detail="Error saving subtopic to database")

    # Wait for the prompts to be generated and then save them
    save = asyncio.create_task(save_prompts_to_db(pathid, topicid, subtopicid, prompts))
    save=await asyncio.gather(save)



async def save_subtopics_to_db(pathid: str, topicid: str, subtopics: list, path_name: str, topic_name: str):
    tasks = []  # List to store all tasks
    print(f"\033[94m[INFO] ESTE ES SUBTOPICS '{subtopics}' en la tabla 'paths_subtopics_tb' con orden\033[0m")

    for order, subtopic in enumerate(subtopics, start=1):
        subtopicid = str(uuid.uuid4())
        print(f"\033[94m[INFO] Creando tarea para guardar subtema '{subtopic}' en la tabla 'paths_subtopics_tb' con orden {order}\033[0m")

        # Create a task to save the subtopic and process the prompts
        task = asyncio.create_task(process_and_save_subtopic(pathid, topicid, subtopicid, subtopic, topic_name, path_name, order))
        tasks.append(task)

    # Run all tasks concurrently
    await asyncio.gather(*tasks)



async def save_to_supabase(table_name: str, data: dict):
    print(f"\033[94m[INFO] Guardando datos en la tabla '{table_name}'...\033[0m")
    try:
        result = supabase_user.table(table_name).insert(data).execute()
        if not result or "error" in result:
            print(f"\033[91m[ERROR] Error al guardar en la tabla {table_name}: {result.get('error')}\033[0m")
            raise HTTPException(status_code=500, detail=f"Error saving to {table_name}")
        print(f"\033[92m[INFO] Datos guardados exitosamente en '{table_name}'\033[0m")
        return result.data[0]
    
    except Exception as e:
        print(f"\033[91m[ERROR] Error al guardar en la tabla '{table_name}': {str(e)}\033[0m")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def generate_prompts_for_subtopics(subtopic_name: str, topic_name: str, path_name: str, max_prompts: int = 5):
    print(f"\033[94m[INFO] Iniciando la generación de prompts para el subtema: {subtopic_name} dentro del topic: {topic_name} del Path: {path_name}\033[0m")

    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        print(f"\033[92m[INFO] Modelo LLM 'gemini-1.5-pro' inicializado correctamente.\033[0m")
    except Exception as e:
        print(f"\033[91m[ERROR] Error al inicializar el modelo LLM: {e}\033[0m")
        raise

    try:
        # Crear el agente para la generación de prompts
        app = create_react_agent(
            model=llm, 
            tools=[], 
            state_modifier=f"""Eres un asistente útil. Responde en un lenguaje formal y enfocado en crear una lista de prompts claros y útiles para un subtema llamado '{subtopic_name}' dentro del topic '{topic_name}' en el Path '{path_name}'solo genera y responde con las puras preguntas , NO RESPONDAS EN MARKDOWN, DE ESTA MANERAEXTRAEMOS LOS SUBTOPICS  prompts = [prompt.strip() for prompt in messages["messages"][-1].content.split("\n") if prompt.strip()],OTRA COSA SUPER IMPORTANTE , CONTESTA EN EL IDIOMA QUE SE TE HABLAOTRA COSA SUPER IMPORTANTE , CONTESTA EN EL IDIOMA QUE SE TE HABLA, PERO PREFERIBLEMENTE CONTESTA EN INGLES"""
        )
        print(f"\033[92m[INFO] Agente creado exitosamente.\033[0m")

        # Generar los prompts
        prompt_template = prompts_for_subtopics_template.format(subtopic_name=subtopic_name, topic_name=topic_name, path_name=path_name,max_prompts=max_prompts)

        messages = app.invoke({"messages": [("human", prompt_template)]})
        prompts = [prompt.strip() for prompt in messages["messages"][-1].content.split("\n") if prompt.strip()]
        print(f"\033[92m[INFO] Prompts generados con éxito: {prompts}\033[0m")

        return prompts
    
    except Exception as e:
        print(f"\033[91m[ERROR] Error al generar los prompts para el subtema: {e}\033[0m")
        raise






async def save_prompts_to_db(pathid: str, topicid: str, subtopicid: str, prompts: list):
    print(f"\033[94m[INFO] ESTOS SON PROMPTS '{prompts}' \033[0m")

    prompts=prompts[0]
    for order, prompt in enumerate(prompts, start=1):
        print(f"\033[94m[INFO] Guardando prompt '{prompt}' en la tabla 'paths_prompts_tb' con orden {order}\033[0m")
        result = supabase_user.table("paths_prompts_tb").insert({
            "pathid": pathid,
            "topicid": topicid,
            "subtopicid": subtopicid,
            "text": prompt,
            "order": order,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()

        if not result or "error" in result:
            print(f"\033[91m[ERROR] Error al guardar el prompt en la tabla 'paths_prompts_tb': {result.get('error')}\033[0m")
            raise HTTPException(status_code=500, detail="Error saving prompt to database")




async def delete_test_entries(table_name: str, pathid: str):
    print(f"\033[94m[INFO] Eliminando registros de prueba en la tabla '{table_name}' con pathid '{pathid}'...\033[0m")
    try:
        result = supabase_user.table(table_name).delete().eq('pathid', pathid).execute()
        if not result or "error" in result:
            print(f"\033[91m[ERROR] Error al eliminar registros en la tabla {table_name}: {result.get('error')}\033[0m")
            raise HTTPException(status_code=500, detail=f"Error deleting entries from {table_name}")
        print(f"\033[92m[INFO] Registros eliminados exitosamente de '{table_name}'\033[0m")
    except Exception as e:
        print(f"\033[91m[ERROR] Error al eliminar registros en la tabla '{table_name}': {str(e)}\033[0m")
        raise HTTPException(status_code=500, detail="Internal Server Error")


import requests
from multi_agents.articles_agent import make_article

async def create_article_for_topic(topic_name: str, pathid: str, courseid: str, projectid: str, memberid: str, orgid: str):
    print(f"\033[94m[INFO] Generando artículo para el topic '{topic_name}'...\033[0m")
    

    try:
        # Generar el artículo directamente usando LangGraph en lugar de llamar a la API

        print(f"\033[94m[INFO] Recibiendo datos del formulario...\033[0m")
        print(f"\033[94mPrompt: {topic_name}\033[0m")
        print(f"\033[94mCourse ID: {courseid}\033[0m")
        print(f"\033[94mProject ID: {projectid}\033[0m")
        print(f"\033[94mMember ID: {memberid}\033[0m")
        print(f"\033[94mOrganization ID: {orgid}\033[0m")

        # Generar el contenido del artículo usando el prompt proporcionado
        content = await make_article(topic_name)
        print(f"\033[92m[INFO] Artículo generado: {content[:200]}... (truncado para vista previa)\033[0m")

        # Guardar el artículo en la base de datos utilizando Supabase
        result = supabase_user.table("articles_tb").insert({
            "prompt": topic_name,
            "content": content,
            "courseid": courseid,
            "projectid": projectid,
            "memberid": memberid,
            "organizationid": orgid,
        }).execute()

        if not result or "error" in result:
            raise HTTPException(status_code=500, detail="Error saving article to database")

        # Devolver el ID del artículo creado
        article_id = result.data[0]['id']

        # Guardar los datos del artículo en la tabla 'path_articles_tb'
        data_save_article = {
            "id": article_id,  # ID único para el artículo
            "articleid": article_id,
            "pathid": pathid,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        print(f"\033[92m[INFO] Este es data_save_article: {data_save_article}\033[0m")

        result = supabase_user.table("paths_articles_tb").insert(data_save_article).execute()

        if not result or "error" in result:
            print(f"\033[91m[ERROR] Error al guardar el artículo en la tabla 'paths_articles_tb': {result.get('error')}\033[0m")
            raise HTTPException(status_code=500, detail="Error saving article to database")

    except Exception as e:
        print(f"\033[91m[ERROR] Error al generar el artículo: {str(e)}\033[0m")
        raise


async def delete_all_entries_except_exclusions(exclusion_ids: list):
    try:
        print(f"\033[94m[INFO] Iniciando la eliminación de todos los datos relacionados, excluyendo los IDs {exclusion_ids}...\033[0m")

        # Obtener todos los IDs de paths_tb que no están en la lista de exclusión
        paths_to_delete = await get_paths_to_delete(exclusion_ids)

        # Eliminar las entradas de la tabla 'paths_articles_tb' primero para evitar conflictos
        await delete_test_entries('paths_progress_tb', paths_to_delete)
        await delete_test_entries('paths_articles_tb', paths_to_delete)

        # Tablas a procesar (en orden de dependencia)
        tables = ['paths_progress_tb','paths_prompts_tb', 'paths_subtopics_tb', 'paths_topics_tb', 'paths_tb']

        # Eliminar las entradas de las demás tablas
        for table in tables:
            await delete_test_entries(table, paths_to_delete)

        print(f"\033[92m[INFO] Todos los datos han sido eliminados exitosamente, excepto los IDs {exclusion_ids}.\033[0m")

    except Exception as e:
        print(f"\033[91m[ERROR] Error al eliminar los datos: {str(e)}\033[0m")
        raise HTTPException(status_code=500, detail="Error deleting all entries except exclusions")


async def get_paths_to_delete(exclusion_ids: list):
    try:
        print(f"\033[94m[INFO] Obteniendo IDs de paths_tb que no están en la lista de exclusión...\033[0m")
        
        # Obtener todos los IDs en paths_tb
        result = supabase_user.table('paths_tb').select('id').execute()

        if not result or "error" in result:
            print(f"\033[91m[ERROR] Error al obtener los IDs de paths_tb: {result.get('error')}\033[0m")
            raise HTTPException(status_code=500, detail="Error getting paths to delete")
        
        # Filtrar los IDs para excluir los proporcionados en exclusion_ids
        paths_to_delete = [item['id'] for item in result.data if item['id'] not in exclusion_ids]
        print(f"\033[92m[INFO] IDs a eliminar: {paths_to_delete}\033[0m")
        return paths_to_delete
    
    except Exception as e:
        print(f"\033[91m[ERROR] Error al obtener los IDs de paths_tb: {str(e)}\033[0m")
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def delete_test_entries(table_name: str, paths_to_delete: list):
    print(f"\033[94m[INFO] Eliminando registros en la tabla '{table_name}' para los IDs '{paths_to_delete}'...\033[0m")
    try:
        for path_id in paths_to_delete:
            if table_name != 'paths_tb':
                result = supabase_user.table(table_name).delete().eq('pathid', path_id).execute()
            else:
                result = supabase_user.table(table_name).delete().eq('id', path_id).execute()
            if not result or "error" in result:
                print(f"\033[91m[ERROR] Error al eliminar registros en la tabla {table_name}: {result.get('error')}\033[0m")
                raise HTTPException(status_code=500, detail=f"Error deleting entries from {table_name}")
        print(f"\033[92m[INFO] Registros eliminados exitosamente de '{table_name}' para los IDs '{paths_to_delete}'\033[0m")
    except Exception as e:
        print(f"\033[91m[ERROR] Error al eliminar registros en la tabla '{table_name}': {str(e)}\033[0m")
        raise HTTPException(status_code=500, detail="Internal Server Error")

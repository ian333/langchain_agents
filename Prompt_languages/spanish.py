# Archivo de prompts en español

main_prompt = """
                Eres un modelo conversacional avanzado diseñado para proporcionar respuestas precisas y contextualmente relevantes. Tu función actual y la naturaleza de esta interacción están definidas por el siguiente contexto específico: {custom_prompt}. Este contexto es crucial ya que da forma a tu comprensión, respuestas y la manera en que te relacionas con el usuario.

                Por favor, revisa el historial de este chat: {history}. Cada interacción proporciona información valiosa sobre la dirección y el tono de la conversación en curso. Este contexto histórico es esencial para mantener un diálogo coherente y relevante. Te ayuda a entender la progresión de la conversación y ajustar tus respuestas en consecuencia.

                Tu tarea principal es abordar la pregunta del usuario presentada como: {user_message}. Es imperativo que analices tanto el contexto proporcionado como la totalidad del historial del chat para adaptar tu respuesta de manera efectiva. Tu respuesta debe abordar directamente la consulta del usuario, aprovechando los detalles específicos y matices de las interacciones anteriores.
                
                    this is the user information
                    -----------------
                    {user_information}

                    -----
                    tris is the threads metrics

                    {thread_metrics}
                    -------------
                
                
                
                
                
                
                """

follow_up = """
Tu trabajo es darme una lista de preguntas relacionadas con {query}.
IMPORTANTE -------------------------------
Por favor, devuelve solo 4 preguntas en formato de lista separadas por punto y coma (;) de esta manera:
Pregunta1;Pregunta2;Pregunta3;Pregunta4
IMPORTANTE -------------------------------
SIGUE LAS INSTRUCCIONES AL PIE DE LA LETRA SEPARADAS POR PUNTO Y COMA
#ejemplo 1
¿Cuál es la mejor manera de almacenar hierbas secas?;¿Cuáles son algunos ejercicios de bajo impacto adecuados para personas mayores?;¿Puedes recomendar algunos proyectos de carpintería fáciles para principiantes?;¿Es posible propagar plantas suculentas usando hojas?

#ejemplo 2
¿Cómo hago pasta casera sin una máquina?;¿Qué verduras crecen bien en contenedores?;¿Hay buenos recursos en línea para aprender nuevos idiomas?;¿Debo usar aceite o mantequilla al cocinar con ajo?

Además, por favor responde en el mismo idioma en que se hace la consulta. Por ejemplo, si la consulta está en español, tu respuesta también debe estar en español.
"""

discovery = """
Analiza la siguiente información del curso y clasifícala en el formato dado.
{course_information}

DEBES organizar la información en la siguiente estructura:

categorías:
  - nombre: "Nombre de la Categoría"
    hilos:
      - "Hilo 1"
      - "Hilo 2"
      - "Hilo 3"
    icono_url: "URL del Icono"
    descripción: "Descripción de la categoría"

Utiliza los detalles del curso proporcionados para completar las siguientes categorías: Recolección de Datos, Limpieza de Datos, Análisis Exploratorio de Datos, Aprendizaje Automático, Análisis Estadístico y Tecnologías de Big Data. Incluye los módulos del curso, temas y descripciones correspondientes.

Aquí tienes dos ejemplos del formato de salida deseado:

Ejemplo 1:
categorías:
  - nombre: "Recolección de Datos"
    hilos:
      - "Diseño de Encuestas y Métodos de Muestreo"
      - "Web Scraping y APIs"
      - "Almacenamiento y Gestión de Datos"
    icono_url: "https://example.com/icons/data-collection.png"
    descripción: "Métodos y herramientas para recopilar datos"
  - nombre: "Limpieza de Datos"
    hilos:
      - "Manejo de Valores Faltantes"
      - "Transformación y Normalización de Datos"
      - "Detección y Tratamiento de Valores Atípicos"
    icono_url: "https://example.com/icons/data-cleaning.png"
    descripción: "Preparación de datos crudos para el análisis"

Ejemplo 2:
categorías:
  - nombre: "Análisis Exploratorio de Datos"
    hilos:
      - "Estadísticas Descriptivas"
      - "Técnicas de Visualización de Datos"
      - "Identificación de Patrones y Tendencias"
    icono_url: "https://example.com/icons/exploratory-data-analysis.png"
    descripción: "Análisis de datos para descubrir ideas"
  - nombre: "Aprendizaje Automático"
    hilos:
      - "Algoritmos de Aprendizaje Supervisado"
      - "Técnicas de Aprendizaje No Supervisado"
      - "Evaluación y Validación de Modelos"
    icono_url: "https://example.com/icons/machine-learning.png"
    descripción: "Construcción de modelos predictivos"

SIEMPRE dame la respuesta en el formato JSON especificado.
"""
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
follow_up="""
Tu trabajo es proporcionarme una lista de preguntas relacionadas con {query}.
IMPORTANTE -------------------------------
Por favor, devuelve solo 4 preguntas en formato de lista separadas por punto y coma (;) de esta manera:
Pregunta1;Pregunta2;Pregunta3;Pregunta4
IMPORTANTE -------------------------------
SIGUE LAS INSTRUCCIONES AL PIE DE LA LETRA SEPARADAS POR PUNTO Y COMA
-----------------------------------------
Las preguntas deben ser claras, concisas y directamente relacionadas con el tema especificado en {query}.
-----------------------------------------
#ejemplo 1
¿Cuál es la mejor manera de almacenar hierbas secas?;¿Cuáles son algunos ejercicios de bajo impacto adecuados para personas mayores?;¿Puedes recomendar algunos proyectos de carpintería fáciles para principiantes?;¿Es posible propagar plantas suculentas usando hojas?

#ejemplo 2
¿Cómo hago pasta casera sin una máquina?;¿Qué verduras crecen bien en contenedores?;¿Hay buenos recursos en línea para aprender nuevos idiomas?;¿Debo usar aceite o mantequilla cuando cocino con ajo?

#ejemplo 3
¿Cuáles son los beneficios de la meditación para la salud mental?;¿Cómo puedo empezar un pequeño negocio desde casa?;¿Cuáles son las mejores prácticas para el marketing por correo electrónico?;¿Cómo mantengo una dieta equilibrada mientras viajo?

#ejemplo 4
¿Cuáles son algunas estrategias efectivas de gestión del tiempo para estudiantes?;¿Cómo puedo mejorar mis habilidades de oratoria?;¿Cuáles son las atracciones turísticas más populares en París?;¿Cómo puedo crear un presupuesto para mis finanzas personales?

#ejemplo 5
¿Cuáles son los síntomas de una alergia al gluten?;¿Cómo puedo mejorar mis habilidades fotográficas?;¿Cuáles son algunos buenos hábitos para mantener la salud mental?;¿Cuáles son los elementos clave de un plan de negocios exitoso?

#ejemplo 6
¿Cómo puedo aprender a tocar la guitarra por mi cuenta?;¿Cuáles son las mejores prácticas para una vida sostenible?;¿Cómo puedo mejorar mis habilidades para resolver problemas?;¿Cuáles son los beneficios del ejercicio físico regular?

Además, por favor responde en el mismo idioma que la consulta. Por ejemplo, si la consulta está en inglés, tu respuesta también debe estar en inglés.
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



ai_companion="""Eres un asistente de inteligencia artificial llamado AI Companion. Tu objetivo es proporcionar insights útiles y sugerencias para mejorar el aprendizaje del usuario basado en su historial de conversaciones. No debes responder directamente a la pregunta actual, sino ofrecer orientación adicional, recursos útiles y consejos para mejorar su comprensión del tema.

Contexto del usuario:
- Estás ayudando a un estudiante que está aprendiendo sobre temas
- El entorno es educativo, enfocado en el aprendizaje y la mejora continua.
- La comunicación debe ser clara, respetuosa y motivadora.

Instrucciones:
1. Analiza el historial de conversaciones del usuario para identificar patrones y áreas donde podría necesitar más ayuda.
2. Proporciona sugerencias útiles y recursos adicionales que puedan mejorar su comprensión del tema.
3. Ofrece consejos prácticos y motivadores para ayudar al usuario a seguir avanzando en su aprendizaje.
4. Mantén un tono amistoso y profesional.

Ejemplo de respuesta:
"Hola [nombre del usuario], he revisado tus preguntas anteriores y parece que estás trabajando duro en entender [tema específico]. Un área que podrías explorar más es [tema relacionado]. Aquí tienes algunos recursos adicionales que podrían ayudarte: [enlace a recursos]. También te recomendaría [sugerencia práctica]. ¡Sigue así, estás haciendo un gran trabajo!"

Historial de conversaciones:
{history}

Pregunta actual:
{user_message}

Responde proporcionando insights y sugerencias adicionales para el usuario.


                    this is the user information
                    -----------------
                    {user_information}

                    -----
                    tris is the threads metrics

                    {thread_metrics}
                    -------------
                    This is extra Information:
                    {sources}
                    {videos}
                    {web}

"""

# prompts.py

# english.py
# Prompt template for path details
path_prompt_template = """
Based on the following topic: {topic}, please generate an appropriate name for a learning Path, followed by a detailed description.

The name should be brief, catchy, and reflect the focus of the Path.

The description should include:
1. Path Objective: Briefly explain the purpose and key objectives.
2. Covered Content: Mention the main topics and skills that users will learn.
3. Benefits: Detail the benefits of following this Path and how it can be applied in practice.

Please separate the name and description by two newlines `\n\n`.

EXAMPLE:

"Introduction to Machine Learning for Beginners"
"This course will cover the basics of machine learning, including supervised and unsupervised learning techniques, data preprocessing, and model evaluation. Students will learn how to apply these techniques to solve real-world problems."

"Advanced Data Science Techniques"
"Explore advanced data science techniques, such as deep learning, natural language processing, and computer vision. This path is designed for learners with a strong foundation in data science and aims to take their skills to the next level."

"Web Development Bootcamp"
"Learn the fundamentals of web development, including HTML, CSS, JavaScript, and modern frameworks like React. This course will provide you with the skills needed to build responsive and dynamic websites from scratch."

"Digital Marketing Strategies"
"Understand the core concepts of digital marketing, including SEO, content marketing, social media marketing, and analytics. This path will equip you with the tools and strategies to create effective online marketing campaigns."

"Cybersecurity Essentials"
"Gain a solid understanding of cybersecurity principles, including risk management, threat analysis, and defensive strategies. This course is ideal for anyone looking to start a career in cybersecurity or enhance their knowledge in the field."
"""

# State modifier for generating path details
state_modifier_path_details = """
You are a helpful assistant. Your task is to generate a clear and attractive name and description for a learning Path focused on '{topic}'. Please respond in plain text, not in markdown. 

Important: The name should be on the first line. The description should follow on the second line, separated by two newline characters ('\\n\\n') from the name. The output will be split at these newlines to extract the name and description separately.

EXAMPLE:

"Introduction to Machine Learning for Beginners"
"This course will cover the basics of machine learning, including supervised and unsupervised learning techniques, data preprocessing, and model evaluation. Students will learn how to apply these techniques to solve real-world problems."

"Advanced Data Science Techniques"
"Explore advanced data science techniques, such as deep learning, natural language processing, and computer vision. This path is designed for learners with a strong foundation in data science and aims to take their skills to the next level."

"Web Development Bootcamp"
"Learn the fundamentals of web development, including HTML, CSS, JavaScript, and modern frameworks like React. This course will provide you with the skills needed to build responsive and dynamic websites from scratch."

"Digital Marketing Strategies"
"Understand the core concepts of digital marketing, including SEO, content marketing, social media marketing, and analytics. This path will equip you with the tools and strategies to create effective online marketing campaigns."

"Cybersecurity Essentials"
"Gain a solid understanding of cybersecurity principles, including risk management, threat analysis, and defensive strategies. This course is ideal for anyone looking to start a career in cybersecurity or enhance their knowledge in the field."
"""

# State modifier for generating path topics
state_modifier_path_topics = """
You are a helpful assistant. Your task is to generate a clear and organized list of topics for a learning Path called '{path_name}'. 

Important: Respond only with the titles of the topics, one per line. The output will be used as a simple list of topics, so ensure each topic title is concise and informative. Limit the output to {max_items} topics.
JUST 5 PLEASE JUST generate 5
JUST 5 PLEASE JUST generate 5
JUST 5 PLEASE JUST generate 5
JUST 5 PLEASE JUST generate 5
JUST 5 PLEASE JUST generate 5

EXAMPLES:

1. "Introduction to Machine Learning"
2. "Data Preprocessing Techniques"
3. "Supervised Learning Algorithms"
4. "Unsupervised Learning Methods"
5. "Model Evaluation and Tuning"
"""

# State modifier for generating subtopics
state_modifier_subtopics = """
You are a helpful assistant. Your task is to generate a clear and organized list of subtopics for a specific topic called '{topic_name}' within the learning Path '{path_name}'. 

Important: Respond only with the subtopics, one per line, without headers or additional formatting. The output will be used as a simple list of subtopics, so ensure each subtopic is clear and relevant. Limit the output to {max_subtopics} subtopics.
JUST 5 PLEASE JUST generate 5
JUST 5 PLEASE JUST generate 5
JUST 5 PLEASE JUST generate 5
JUST 5 PLEASE JUST generate 5

EXAMPLES:

1. "Understanding Linear Regression"
2. "Applying Logistic Regression"
3. "Decision Trees and Random Forests"
4. "K-Nearest Neighbors"
5. "Support Vector Machines"
"""

# Prompt template for generating path topics
topic_prompt_template = """
Please generate a list of topic titles for a learning Path called '{path_name}'. The focus should be on providing a logical and clear educational flow.

Important: Respond only with the titles or the topics, one per line, without any additional text or formatting. The output will be treated as a list of topics.
JUST 5 PLEASE JUST generate 5
JUST 5 PLEASE JUST generate 5
JUST 5 PLEASE JUST generate 5
JUST 5 PLEASE JUST generate 5
JUST 5 PLEASE JUST generate 5
JUST 5 PLEASE JUST generate 5

EXAMPLES:

1. "Introduction to Web Development"
2. "HTML and CSS Basics"
3. "JavaScript for Beginners"
4. "Responsive Design"
5. "Building Web Applications with React"
"""

# Prompt template for generating subtopics
subtopic_prompt_template = """
Please generate a list of subtopics for the topic '{topic_name}' within the Path '{path_name}'.

Important: Respond only with the subtopics, one per line, without headers or additional formatting. The output will be used as a list of subtopics, so each line should represent a single subtopic.

EXAMPLES:

1. "Understanding Flexbox in CSS"
2. "Implementing Grid Layouts"
3. "Building Responsive Navigation Menus"
4. "Using Media Queries"
5. "Optimizing Images for Web Performance"
"""

# Prompt template for generating prompts for subtopics
prompts_for_subtopics_template = """
Please generate a list of prompts for the subtopic '{subtopic_name}' within the topic '{topic_name}' in the Path '{path_name}'.

Important: Only generate {max_prompts} questions. Remember, these questions will guide the entire learning process, so make them long and complex enough to engage the user. Respond with each question on a new line without additional formatting or text.

EXAMPLES:

1. "What are the key principles of Flexbox in CSS, and how can they be applied to create a responsive layout?"
2. "How does the CSS Grid system differ from Flexbox, and in what scenarios would you prefer one over the other?"
3. "Explain the process of creating a responsive navigation menu using CSS and JavaScript. What challenges might arise, and how can they be addressed?"
4. "What are media queries, and how can they be used to create a responsive design that adapts to different screen sizes?"
5. "Discuss the importance of optimizing images for web performance. What techniques can be used to reduce file size without compromising quality?"
"""

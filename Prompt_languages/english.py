
main_prompt="""
                You are an advanced conversational model designed to provide accurate and contextually relevant responses. Your current role and the nature of this interaction are defined by the following specific context: {custom_prompt}. This context is crucial as it shapes your understanding, responses, and the way you engage with the user.

                Please review the history of this chat: {history}. Each interaction provides valuable insights into the ongoing conversation's direction and tone. This historical context is essential for maintaining a coherent and relevant dialogue. It helps you understand the progression of the conversation and adjust your responses accordingly.

                Your primary task is to address the user's question presented as: {user_message}. It’s imperative that you analyze both the provided context and the entirety of the chat history to tailor your response effectively. Your answer should directly address the user's inquiry, leveraging the specific details and nuances of the preceding interactions.

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



follow_up="""
Your job is to give me a list of questions related to {query}.
IMPORTANT -------------------------------
Please, return only 4 questions in list format separated by semicolon (;) in this manner:
Question1;Question2;Question3;Question4
IMPORTANT -------------------------------
FOLLOW THE INSTRUCTIONS TO THE LETTER SEPARATED BY SEMICOLON
-----------------------------------------
The questions should be clear, concise, and directly related to the topic specified in {query}.
-----------------------------------------
#example 1
What's the best way to store dried herbs?;What are some low-impact exercises suitable for seniors?;Can you recommend some easy beginner woodworking projects?;Is it possible to propagate succulent plants using leaves?

#example 2
How do I make homemade pasta without a machine?;Which vegetables grow well in containers?;Are there any good online resources for learning new languages?;Should I use oil or butter when cooking with garlic?

#example 3
What are the benefits of meditation for mental health?;How can I start a small business from home?;What are the best practices for email marketing?;How do I maintain a balanced diet while traveling?

#example 4
What are some effective time management strategies for students?;How can I improve my public speaking skills?;What are the most popular tourist attractions in Paris?;How can I create a budget for my personal finances?

#example 5
What are the symptoms of a gluten allergy?;How can I improve my photography skills?;What are some good habits for maintaining mental health?;What are the key elements of a successful business plan?

#example 6
How can I learn to play the guitar on my own?;What are the best practices for sustainable living?;How can I enhance my problem-solving skills?;What are the benefits of regular physical exercise?

Additionally, please respond in the same language as the query. For example, if the query is in Spanish, your response should also be in Spanish.
"""

discovery = """
    Analyze the following course information and categorize it into the given format.
    {course_information}
    this is the user information
    -----------------
    {user_information}

    -----
    tris is the threads metrics

    {thread_metrics}
    -------------
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

    Your goal is to make the threads and categories as engaging and clickable as possible. Consider the following points:
    - Use action-oriented language for the threads to encourage user interaction.
    - Make the descriptions concise but informative, highlighting the benefits of exploring the category.
    - Ensure that the icon URLs are relevant and visually appealing.
    - Create titles and descriptions that would attract a user's attention and curiosity.

    Here are six examples of the desired output format. These examples are for illustrative purposes and are based on data science topics. For the actual categories and threads, you MUST base them on the specific course information provided:

    Example 1:
    categories:
      - name: "Become a Data Collection Expert: Mastering Methods and Tools"
        threads:
          - "Explain me how to design surveys that yield the best results. What are the key factors to consider in survey design to ensure high response rates and data accuracy? How can sampling methods impact the quality of your data?"
          - "Can you explain how to unlock insights using Web Scraping and APIs? What are the ethical considerations and best practices in web scraping? How do APIs facilitate data integration from multiple sources?"
          - "What are the most efficient data storage and management techniques? How can cloud storage solutions enhance data accessibility and security? What role do database management systems play in organizing large datasets?"
        description: "Explore advanced methods and tools for gathering data effectively and efficiently."

      - name: "Perfect Your Data Cleaning Skills: Transform Raw Data into Actionable Insights"
        threads:
          - "Explain me how to handle missing values like a pro. What are the various techniques for imputing missing data, and how do you choose the right one for your dataset? How can the presence of missing values affect your analysis outcomes?"
          - "What techniques will you use to transform and normalize your data for better results? How do normalization and standardization help in preparing data for machine learning algorithms? What are the common pitfalls to avoid during data transformation?"
          - "Curious about detecting and treating outliers in your data? How can outliers skew your data analysis, and what methods can you use to identify them? What strategies can be implemented to mitigate the impact of outliers on your results?"
        description: "Learn how to prepare raw data for analysis by cleaning and transforming it."

    Example 2:
    categories:
      - name: "Explore Data Like a Pro: Techniques for Effective Analysis"
        threads:
          - "Explain me how to uncover insights with descriptive statistics. What are the key measures of central tendency and variability, and how do they help in summarizing data? How can descriptive statistics provide a foundation for further statistical analysis?"
          - "Ready to visualize data using advanced techniques? How do different types of charts and graphs facilitate the understanding of data patterns? What are the best practices for creating impactful data visualizations that convey your message clearly?"
          - "How can you identify patterns and trends in your data? What statistical methods and tools are most effective for trend analysis? How can recognizing patterns in data help in making data-driven decisions?"
        description: "Analyze data to uncover hidden insights and patterns."

      - name: "Dive into Machine Learning: Build and Validate Predictive Models"
        threads:
          - "Explain me the key supervised learning algorithms you should know. How do algorithms like linear regression, decision trees, and support vector machines work, and what are their typical applications? How do you choose the right algorithm for your predictive modeling tasks?"
          - "Interested in unlocking the potential of unsupervised learning techniques? How do clustering methods like k-means and hierarchical clustering differ, and what are their use cases? How can unsupervised learning help in discovering hidden patterns in data?"
          - "How can you ensure your models are evaluated and validated correctly? What are the essential techniques for model evaluation, such as cross-validation and ROC curves? How do you interpret model performance metrics to improve your machine learning models?"
        description: "Build and validate predictive models with cutting-edge machine learning techniques."

    Example 3:
    categories:
      - name: "Statistical Analysis: Unlock Deeper Insights from Your Data"
        threads:
          - "Explain me how to perform hypothesis testing. What are the different types of hypothesis tests, and how do you choose the appropriate test for your data? How do you interpret the results of a hypothesis test to draw meaningful conclusions?"
          - "What are the best practices for conducting regression analysis? How do different types of regression models, like linear and logistic regression, differ in their applications? How can regression analysis help in understanding relationships between variables?"
          - "Curious about time series analysis? How do you analyze data that varies over time, and what are the common techniques used in time series analysis? How can time series forecasting be applied in real-world scenarios?"
        description: "Delve into the world of statistical analysis to uncover deeper insights from your data."

    Example 4:
    categories:
      - name: "Big Data Technologies: Taming the Data Deluge"
        threads:
          - "Explain me the Hadoop ecosystem. What are the key components of Hadoop, and how do they work together to manage and process large datasets? How does Hadoop's distributed storage and processing capability enhance data management?"
          - "What makes the Spark framework a powerful tool for data processing? How does Spark differ from Hadoop, and what are its advantages in terms of speed and efficiency? How can you leverage Spark for real-time data analysis?"
          - "How do NoSQL databases handle massive volumes of unstructured data? What are the different types of NoSQL databases, and how do you choose the right one for your needs? How can NoSQL databases improve scalability and flexibility in data management?"
        description: "Explore powerful technologies to manage and analyze massive datasets efficiently."

    Example 5:
    categories:
      - name: "Advanced Data Visualization: Crafting Stories with Data"
        threads:
          - "Explain me the principles of effective data visualization. What are the key elements to consider when creating visualizations, and how can they enhance the communication of data insights? How do you choose the right type of chart or graph for your data?"
          - "How can you use tools like Tableau and Power BI for data visualization? What are the features and capabilities of these tools, and how do they compare? How can you create interactive and dynamic dashboards to present data?"
          - "Interested in learning about geospatial data visualization? How do you visualize geographic data, and what tools are available for this purpose? What are the best practices for creating maps and other geospatial visualizations?"
        description: "Master the art of data visualization to effectively communicate your data insights."

    Example 6:
    categories:
      - name: "Data Engineering: Building Robust Data Pipelines"
        threads:
          - "Explain me the fundamentals of data engineering. What are the key responsibilities of a data engineer, and how do they contribute to the data lifecycle? What skills and tools are essential for a successful career in data engineering?"
          - "How do you design and build data pipelines? What are the steps involved in creating a data pipeline, and how do you ensure its reliability and scalability? How do you handle data ingestion, transformation, and storage in a pipeline?"
          - "Curious about data warehousing? What is a data warehouse, and how does it differ from a database? How do you design a data warehouse to support efficient querying and analysis? What are the best practices for maintaining a data warehouse?"
        description: "Learn how to build robust data pipelines and manage the data lifecycle effectively."

    REMEMBER: The examples provided above are for data science topics. The final categories and threads should be based on the specific course information provided, especially if it pertains to food-related topics or other non-data science subjects.

    ALWAYS give me the answer in the specified JSON format.
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

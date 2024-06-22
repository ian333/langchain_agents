
main_prompt="""
                You are an advanced conversational model designed to provide accurate and contextually relevant responses. Your current role and the nature of this interaction are defined by the following specific context: {custom_prompt}. This context is crucial as it shapes your understanding, responses, and the way you engage with the user.

                Please review the history of this chat: {history}. Each interaction provides valuable insights into the ongoing conversation's direction and tone. This historical context is essential for maintaining a coherent and relevant dialogue. It helps you understand the progression of the conversation and adjust your responses accordingly.

                Your primary task is to address the user's question presented as: {user_message}. It’s imperative that you analyze both the provided context and the entirety of the chat history to tailor your response effectively. Your answer should directly address the user's inquiry, leveraging the specific details and nuances of the preceding interactions.
                """



follow_up="""
Your job is to give me a list of questions related to {query}.
IMPORTANT -------------------------------
Please, return only 4 questions in list format separated by semicolon (;) in this manner:
Question1;Question2;Question3;Question4
IMPORTANT -------------------------------
FOLLOW THE INSTRUCTIONS TO THE LETTER SEPARATED BY SEMICOLON
#example 1
What's the best way to store dried herbs?;What are some low-impact exercises suitable for seniors?;Can you recommend some easy beginner woodworking projects?;Is it possible to propagate succulent plants using leaves?

#example 2
How do I make homemade pasta without a machine?;Which vegetables grow well in containers?;Are there any good online resources for learning new languages?;Should I use oil or butter when cooking with garlic?

Additionally, please respond in the same language as the query. For example, if the query is in Spanish, your response should also be in Spanish.

                                                       
    """


discovery=    """
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
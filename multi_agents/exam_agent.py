# exam_agent.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

# Inicializar el modelo LLM globalmente para reutilización
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")


from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel, Field
from uuid import uuid4

# Define un modelo para los datos del formulario
class ExamGenerateRequest(BaseModel):
    prompt: str = Field(..., example="haz un examen complejo de física de cohetes avanzada")
    max_items: int = Field(..., example=5)
    memberid: str = Field(..., example="8b013804-faa6-426e-bfcc-43227f58e3c8")
    type: str = Field(default="diagnostic", example="diagnostic")
    courseid: str = Field(..., example="661659eb-3afa-4c8e-8c4e-25a9115eed69")

# Modelos Pydantic
from pydantic import BaseModel, Field

class Answer(BaseModel):
    question_id: str = Field(..., example="00db7caf-45b0-4085-8c92-ad102cb7eca1")
    question: str = Field(..., example="What is the difference between a cash game and a tournament in online poker?")
    answer: str = Field(..., example="In online poker, a cash game is a type of poker game where players buy chips and each chip has a real-money value. Players can join or leave the game at any time, and they can cash out their chips whenever they want. On the other hand, a tournament has a fixed buy-in amount, and players compete to win a portion of the prize pool.")

from pydantic import BaseModel, Field

class Answer(BaseModel):
    question_id: str = Field(..., example="65a7e585-8397-405d-b777-aa53a186a5c5")
    question: str = Field(..., example="Derive the Tsiolkovsky rocket equation, explaining each term and its physical significance.")
    answer: str = Field(..., example="The Tsiolkovsky rocket equation is used to calculate the final velocity of a rocket based on its initial and final mass and the exhaust velocity. The equation is: delta_v = v_e * ln(m0/mf).")

class ExamRequest(BaseModel):
    courseid: str = Field(..., example="661659eb-3afa-4c8e-8c4e-25a9115eed69")
    memberid: str = Field(..., example="8b013804-faa6-426e-bfcc-43227f58e3c8")
    exam_id: str = Field(..., example="bbd2fa7d-4a7a-4a7d-898d-0f2efcd1e123")
    projectid: str = Field(..., example="28722c50-cc1b-4b92-811b-0709320063e5")
    orgid: str = Field(..., example="6c0bfedb-258a-4c77-9bad-b0e87c0d9c98")

    answers: list[Answer] = Field(..., example=[
        {
            "question_id": "65a7e585-8397-405d-b777-aa53a186a5c5",
            "question": "Derive the Tsiolkovsky rocket equation, explaining each term and its physical significance.",
            "answer": "The Tsiolkovsky rocket equation is used to calculate the final velocity of a rocket based on its initial and final mass and the exhaust velocity. The equation is: delta_v = v_e * ln(m0/mf)."
        },
        {
            "question_id": "b4979767-e0f5-4f67-acdd-03b3c636e7ca",
            "question": "A rocket engine with a specific impulse of 300 seconds burns fuel at a rate of 10 kg/s. Calculate the thrust produced by the engine.",
            "answer": "The thrust produced by a rocket engine with a specific impulse of 300 seconds and a fuel burn rate of 10 kg/s is 29,430 Newtons."
        },
        {
            "question_id": "583afe59-4ba0-4919-b92d-25613fecd147",
            "question": "Explain the concept of the Oberth effect and its application in space missions.",
            "answer": "The Oberth effect refers to the increased efficiency of a rocket burn at higher speeds, typically when close to a planet. This effect is used in space missions to maximize fuel efficiency during maneuvers."
        },
        {
            "question_id": "5ad0dbb2-7416-4cfd-bd57-d042de82a8f6",
            "question": "A spacecraft is in a circular orbit around Earth at an altitude of 500 km. Calculate the orbital velocity and period of the spacecraft.",
            "answer": "For a spacecraft at 500 km altitude, the orbital velocity is approximately 7.6 km/s, and the orbital period is about 90 minutes."
        },
        {
            "question_id": "c977dfe6-7957-46bc-b907-69786fe84347",
            "question": "Describe the different types of rocket propellants and their advantages and disadvantages.",
            "answer": "Rocket propellants can be classified into liquid and solid. Liquid propellants offer better control but are complex, while solid propellants are simpler but less efficient."
        },
        {
            "question_id": "5a56d1f8-e802-438b-91eb-6d885b086e8a",
            "question": "A rocket is launched vertically from the surface of the Earth. Assuming a constant acceleration of 10 m/s², calculate the time it takes to reach an altitude of 100 km.",
            "answer": "For a rocket launched vertically with constant acceleration of 10 m/s², the time to reach 100 km altitude is approximately 141.4 seconds."
        },
        {
            "question_id": "9de68197-d799-4102-9566-7820a8510dc1",
            "question": "Explain the concept of the rocket equation and its limitations in describing the motion of a rocket.",
            "answer": "The rocket equation, delta_v = v_e * ln(m0/mf), is limited by the assumptions of constant exhaust velocity and no external forces. It also doesn't account for complex forces like gravity or atmospheric drag."
        },
        {
            "question_id": "859f7191-b18e-4df4-ad54-e363496d5482",
            "question": "A rocket is designed to achieve a delta-v of 10 km/s. If the initial mass of the rocket is 1000 kg and the exhaust velocity is 2 km/s, calculate the final mass of the rocket.",
            "answer": "For a rocket with an initial mass of 1000 kg, an exhaust velocity of 2 km/s, and a required delta-v of 10 km/s, the final mass of the rocket would be approximately 13.53 kg."
        },
        {
            "question_id": "4e910e2d-1e59-4679-b633-f352e024fcaf",
            "question": "Describe the challenges of designing a rocket engine for a mission to Mars.",
            "answer": "Designing a rocket engine for a mission to Mars presents challenges such as long-duration reliability, efficient fuel use, and the need to withstand extreme environmental conditions on Mars."
        },
        {
            "question_id": "66e74fe3-f14b-4526-a2d8-86d98dbe5fb7",
            "question": "Discuss the role of aerodynamics in the design and performance of a rocket.",
            "answer": "Aerodynamics plays a crucial role in rocket design, particularly during the initial stages of launch. It affects stability, drag, and fuel efficiency."
        }
    ])


# State modifier para generar preguntas del examen
state_modifier_exam_generation = """
You are a helpful assistant. Your task is to generate an exam based on the following prompt: '{prompt}'.

Important: Generate only {max_items} questions. The questions should be varied in difficulty and should cover different aspects of the topic. Respond with each question on a new line without additional formatting or text.

EXAMPLES:

1. "Explain the concept of inheritance in object-oriented programming. Provide an example in Python."
2. "What is the difference between a list and a tuple in Python? When would you use each one?"
3. "Describe the process of creating a virtual environment in Python. Why is it important?"
4. "How does exception handling work in Python? Provide an example using try, except, and finally."
5. "What are Python decorators, and how are they used? Provide an example of a simple decorator."
6. "Explain the differences between supervised and unsupervised learning in machine learning. Provide examples of algorithms used for each."
7. "Discuss the key differences between a stack and a queue in data structures. Provide examples of their use cases."
8. "What is a database transaction, and why is it important in ensuring data integrity? Provide an example using SQL."
9. "Explain the concept of Big O notation and how it is used to evaluate the performance of algorithms."
10. "What is recursion in computer science? Provide an example of how recursion can be used to solve a problem, such as calculating the factorial of a number."
"""

def generate_exam(prompt: str, max_items: int):
    """
    Generate an exam based on a given prompt.
    """
    try:
        # Crear el agente con el state_modifier adecuado
        agent = create_react_agent(
            model=llm, 
            tools=[], 
            state_modifier=state_modifier_exam_generation
        )

        # Generar el examen usando el prompt y el número máximo de preguntas
        exam_prompt = f"Generate an exam based on the following topic: '{prompt}', with a maximum of {max_items} questions."
        messages = agent.invoke({"messages": [("human", exam_prompt)]})

        # Extraer las preguntas de la respuesta
        questions = [question.strip() for question in messages["messages"][-1].content.split("\n") if question.strip()]
        
        # Limitar el número de preguntas generadas al valor máximo especificado
        questions = questions[:max_items]
        
        return questions

    except Exception as e:
        print(f"\033[91m[ERROR] Error generating exam: {str(e)}\033[0m")
        raise





# State modifier para la evaluación de la respuesta
state_modifier_evaluate_answer = """
You are an experienced teacher. Your task is to evaluate the student's answer to the following question: '{question}'.

Please provide two outputs:
1. A quantitative score from 0 to 100 based on the accuracy, completeness, and relevance of the answer.
2. A qualitative feedback that highlights the strengths and areas for improvement in the student's response.

Respond in the following format:
Score: [Quantitative Score]
Feedback: [Qualitative Feedback]

EXAMPLES:

1. "Score: 85\nFeedback: The answer demonstrates a good understanding of the concept, but it could be improved by providing more specific examples."

2. "Score: 92\nFeedback: Excellent response! The answer is well-structured and covers all key points, but be sure to elaborate more on the second point."

3. "Score: 70\nFeedback: The answer is correct, but it lacks detail and depth. Consider expanding on the main ideas and providing examples."
"""

def evaluate_answer(question: str, answer: str):
    """
    Evaluate a student's answer to a specific question.
    """
    try:
        agent = create_react_agent(
            model=llm, 
            tools=[], 
            state_modifier=state_modifier_evaluate_answer
        )

        evaluation_prompt = f"Evaluate the following answer: '{answer}' to the question: '{question}'"
        messages = agent.invoke({"messages": [("human", evaluation_prompt)]})

        # Imprimir toda la respuesta del agente para depuración
        print(f"\033[94m[INFO] Respuesta completa de la IA: {messages['messages'][-1].content}\033[0m")
        
        # Extraer la calificación cuantitativa y cualitativa
        response_content = messages["messages"][-1].content.strip().split("\n")
        
        # Asegurarnos de que la respuesta contiene al menos dos líneas (score y feedback)
        if len(response_content) >= 2:
            score = response_content[0].replace("Score: ", "").strip()
            feedback = response_content[1].replace("Feedback: ", "").strip()
        else:
            score = "N/A"
            feedback = "La respuesta no contiene una calificación y/o feedback adecuados."

        print(f"\033[92m[INFO] Calificación obtenida: {score}\033[0m")
        print(f"\033[92m[INFO] Feedback obtenido: {feedback}\033[0m")
        
        return {"score": score, "feedback": feedback}

    except Exception as e:
        print(f"\033[91m[ERROR] Error evaluating answer: {str(e)}\033[0m")
        raise


# exam_agent.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

# Inicializar el modelo LLM globalmente para reutilización
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# State modifier para el feedback general del examen
state_modifier_exam_feedback = """
You are an experienced teacher. You have evaluated the exam and individual answers. Now, you need to provide a comprehensive overall feedback based on the exam responses, individual feedback, and the overall score.

Please provide a detailed feedback that covers the following:
1. A summary of the student's strengths.
2. Areas where the student needs improvement.
3. General tips on how the student can perform better in future exams.

Respond in a professional and constructive tone.

EXAMPLES:

1. "Overall, the student has demonstrated a strong understanding of the basic concepts. However, there are areas such as {topic} that require more attention. I would suggest reviewing {topic} in more detail. Additionally, practicing more problems related to {concept} would be beneficial."

2. "The student's answers show a good grasp of the topics covered in this exam, but there are some gaps in understanding the more advanced concepts. It is recommended to revisit {specific topic} and practice related exercises."

3. "Great job on completing the exam! You did especially well in {specific area}, but could improve on {specific area}. I recommend focusing on {specific study method} to strengthen your understanding in this area."
"""

def generate_feedback(exam_feedback: str):
    """
    Generate detailed feedback based on all the feedback from individual answers.
    """
    try:
        # Crear el agente con el state_modifier adecuado
        agent = create_react_agent(
            model=llm, 
            tools=[], 
            state_modifier=state_modifier_exam_feedback
        )

        # Generar el feedback usando el feedback de todas las preguntas
        feedback_prompt = f"Generate a comprehensive feedback based on the following feedback and exam score: '{exam_feedback}'"
        messages = agent.invoke({"messages": [("human", feedback_prompt)]})

        # Imprimir toda la respuesta del agente para depuración
        print(f"\033[94m[INFO] Feedback completo generado por la IA: {messages['messages'][-1].content}\033[0m")
        
        return messages["messages"][-1].content.strip()

    except Exception as e:
        print(f"\033[91m[ERROR] Error generating exam feedback: {str(e)}\033[0m")
        raise

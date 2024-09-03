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
# Modelos Pydantic
from pydantic import BaseModel, Field

class Answer(BaseModel):
    question_id: str = Field(..., example="00db7caf-45b0-4085-8c92-ad102cb7eca1")
    question: str = Field(..., example="What is the difference between a cash game and a tournament in online poker?")
    answer: str = Field(..., example="In online poker, a cash game is a type of poker game where players buy chips and each chip has a real-money value. Players can join or leave the game at any time, and they can cash out their chips whenever they want. On the other hand, a tournament has a fixed buy-in amount, and players compete to win a portion of the prize pool.")

class ExamRequest(BaseModel):
    courseid: str = Field(..., example="661659eb-3afa-4c8e-8c4e-25a9115eed69")
    memberid: str = Field(..., example="8b013804-faa6-426e-bfcc-43227f58e3c8")
    exam_id: str = Field(..., example="3483c05c-0c1c-4f28-8238-f5d2ca61606c")
    answers: list[Answer] = Field(..., example=[
        {
            "question_id": "00db7caf-45b0-4085-8c92-ad102cb7eca1",
            "question": "What is the difference between a cash game and a tournament in online poker?",
            "answer": "In online poker, a cash game is a type of poker game where players buy chips and each chip has a real-money value. Players can join or leave the game at any time, and they can cash out their chips whenever they want. On the other hand, a tournament has a fixed buy-in amount, and players compete to win a portion of the prize pool."
        },
        {
            "question_id": "00db7caf-45b0-4085-8c92-ad102cb7eca1",
            "question": "Explain the concept of rake in online poker.",
            "answer": "Rake is the fee that a poker room charges for hosting a poker game. In a cash game, the rake is typically a small percentage of the pot taken by the house each time a hand is played. In tournaments, the rake is usually a fixed percentage of the buy-in, and it is taken out before the prize pool is determined. The rake is how poker rooms make money and cover the costs of running the games."
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
"""


def generate_exam(prompt: str, max_items: int):
    """
    Generate an exam based on a given prompt.
    """
    try:
        agent = create_react_agent(
            model=llm, 
            tools=[], 
            state_modifier=state_modifier_exam_generation
        )

        exam_prompt = f"Generate an exam based on the following topic: '{prompt}'"
        messages = agent.invoke({"messages": [("human", exam_prompt)]})
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
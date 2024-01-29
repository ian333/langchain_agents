# examples/chat_examples.py
import uuid

chat_examples = {
    "example1": {
        "summary": "Ejemplo 1",
        "description": "Una solicitud simple",
        "value": {
            "text": "Hola, ¿cómo estás?",
            "courseid": "123",
            "memberid": "456",
            "prompt": "Explica el concepto de relatividad.",
            "threadid": str(uuid.uuid4()),
            "followup": "Necesito más información sobre este tema.",
            "email": "usuario@example.com"
        },
    },
    "example2": {
        "summary": "Ejemplo 2",
        "description": "Otra solicitud simple",
        "value": {
            "text": "Hola de nuevo",
            "courseid": "789",
            "memberid": "101112",
            "prompt": "Describir la teoría de cuerdas.",
            "threadid": str(uuid.uuid4()),
            "followup": "¿Puedes darme más detalles?",
            "email": "otrousuario@example.com"
        },
    },
}

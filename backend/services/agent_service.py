def answer_question(data):
    if data.get("question"):
        return {
            "answer": "Supervised learning is a machine learning technique where models learn from labeled data...",
            "sources": [{
                "title": "AI Basics",
                "fileId": "98765",
                "url": "https://moocportal.com/materials/98765"
            }]
        }
    return None

def get_history(user_id):
    return [{
        "question": "What is supervised learning?",
        "answer": "Supervised learning is a technique...",
        "timestamp": "2025-02-11T12:34:56Z"
    }]

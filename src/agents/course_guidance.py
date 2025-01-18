from typing import Dict, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from src.core import BaseAgent

class CourseGuidanceAgent(BaseAgent):
    def __init__(self, config: dict):
        super().__init__(config)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=config['google_api_key'],
            temperature=0.7
        )
        self.course_data = self._load_course_data()
        self._setup_chain()

    def _load_course_data(self) -> Dict:
        """Load course data - in production, this would fetch from a database"""
        return {
            "courses": {
                "CS101": {
                    "name": "Introduction to Programming",
                    "topics": ["Python Basics", "Data Structures", "Algorithms"],
                    "resources": ["Course Notes", "Practice Problems", "Video Tutorials"],
                    "assignments": [
                        "Assignment 1: Basic Python",
                        "Assignment 2: Data Structures"
                    ]
                }
            },
            "study_strategies": [
                "Break down complex problems into smaller steps",
                "Create sample test cases",
                "Draw flowcharts or diagrams",
                "Implement pseudo-code first",
                "Test edge cases"
            ]
        }

    def _setup_chain(self):
        """Initialize the guidance chain with academic integrity focus"""
        self.guidance_prompt = PromptTemplate(
            input_variables=["query_type", "query", "context", "strategies"],
            template="""You are an academic guidance assistant helping students learn effectively while maintaining academic integrity.

            Query Type: {query_type}
            Student Query: {query}
            Course Context: {context}
            Study Strategies: {strategies}

            Guidelines for response:
            1. For assignment questions:
            - Never provide direct solutions
            - Give conceptual hints
            - Suggest relevant study materials
            - Guide through problem-solving steps
            - Encourage critical thinking
            
            2. For concept questions:
            - Provide detailed explanations
            - Use relevant examples
            - Link to course materials
            - Suggest practice exercises

            Response:"""
        )

        self.chain = (
            {
                "query_type": self._classify_query,
                "query": RunnablePassthrough(),
                "context": self._get_course_context,
                "strategies": self._get_study_strategies
            }
            | self.guidance_prompt
            | self.llm
        )

    def _classify_query(self, query: str) -> str:
        """Determine query type and check for academic integrity concerns"""
        assignment_keywords = [
            "assignment", "homework", "solution", "answer",
            "solve this", "help me with", "give me the answer"
        ]
        
        if any(keyword in query.lower() for keyword in assignment_keywords):
            return "ASSIGNMENT_QUERY"
        return "CONCEPT_QUERY"

    def _get_course_context(self, query: str) -> str:
        """Get relevant course context based on query"""
        # In production, implement smart context selection
        course = self.course_data["courses"]["CS101"]
        return f"""Course: {course['name']}
        Current Topics: {', '.join(course['topics'])}
        Available Resources: {', '.join(course['resources'])}"""

    def _get_study_strategies(self, query: str) -> str:
        """Get relevant study strategies"""
        return "\n".join(f"- {strategy}" for strategy in self.course_data["study_strategies"])

    def _generate_response(self, query: str) -> str:
        """Generate academically appropriate guidance"""
        try:
            # Generate response using the chain
            response = self.chain.invoke(query)
            
            # Track interaction
            if hasattr(self, 'conversation_manager'):
                self.conversation_manager.store_interaction({
                    'query_type': self._classify_query(query),
                    'query': query,
                    'response': response.content,
                    'course_context': self._get_course_context(query)
                })
            
            return response.content
            
        except Exception as e:
            return f"Error generating guidance: {str(e)}"

    def suggest_resources(self, query: str) -> List[str]:
        """Suggest relevant learning resources"""
        course = self.course_data["courses"]["CS101"]
        return course["resources"]

    def check_academic_integrity(self, query: str) -> bool:
        """Check if query raises academic integrity concerns"""
        direct_solution_keywords = [
            "give me the answer",
            "solve this for me",
            "what is the solution",
            "do my homework"
        ]
        return not any(keyword in query.lower() for keyword in direct_solution_keywords)
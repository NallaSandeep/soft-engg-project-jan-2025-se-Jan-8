from typing import Dict, Any, List, Optional, AsyncGenerator
from src.core.state import AgentState
from langgraph.graph import END
from src.core.base import BaseAgent
# from src.db.student_db import StudentDatabase
from langchain.schema import SystemMessage, AIMessage, HumanMessage
import logging


class CourseGuideAgent(BaseAgent):
    """Course guide agent for course/curriculum questions and exam preparation."""

    def __init__(self, db_path: str):
        """Initialize the course guide agent."""
        super().__init__()
        self.system_message = """You are an intelligent academic assistant for course guidance. 
        Help students navigate their course materials and prepare for upcoming exams.
        Use the specific course information provided in the context to give personalized responses.
        For exam preparation, focus on the specific exam topics listed in the context."""

        # self.db = StudentDatabase(db_path)

    def enrich_query_with_context(
        self, message: str, student_id: str
    ) -> Dict[str, Any]:
        """Enrich the student's query with course context.

        Args:
            message: The student's message/query
            student_id: The student's ID to look up course information

        Returns:
            Dictionary with enriched context
        """
        # Get student information
        student_data = self.db.get_student_data(student_id)
        if not student_data:
            return {"message": message, "context": "No student data found."}

        # Get course information
        courses = self.db.get_student_courses(student_id)

        # Extract relevant context based on query keywords
        query_keywords = self._extract_keywords(message.lower())
        relevant_courses = self._find_relevant_courses(query_keywords, courses)

        # Build context
        context = {
            "student": {
                "name": student_data.get("name", ""),
                "academic_level": student_data.get("academic_level", ""),
            },
            "enrolled_courses": [
                {
                    "id": c.get("id", ""),
                    "title": c.get("title", ""),
                    "topics": c.get("topics", []),
                }
                for c in courses
            ],
            "relevant_courses": relevant_courses,
            "has_upcoming_exams": any(c.get("upcoming_exam") for c in courses),
        }

        return {"message": message, "context": context}

    def _extract_keywords(self, message: str) -> List[str]:
        """Extract keywords from the message for relevance matching."""
        # Simple keyword extraction - in production, use NLP techniques
        common_words = {"the", "a", "an", "in", "for", "to", "and", "or", "but", "of"}
        words = message.lower().split()
        return [word for word in words if word not in common_words and len(word) > 2]

    def _find_relevant_courses(
        self, keywords: List[str], courses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find courses relevant to the keywords."""
        relevant_courses = []

        for course in courses:
            score = 0
            # Check course title
            title = course.get("title", "").lower()
            for keyword in keywords:
                if keyword in title:
                    score += 3

            # Check course topics
            topics = " ".join(course.get("topics", [])).lower()
            for keyword in keywords:
                if keyword in topics:
                    score += 2

            # Check exam relevance
            if "exam" in keywords or "test" in keywords or "quiz" in keywords:
                if course.get("upcoming_exam"):
                    score += 3

            if score > 0:
                relevant_courses.append(
                    {
                        "id": course.get("id", ""),
                        "title": course.get("title", ""),
                        "topics": course.get("topics", []),
                        "upcoming_exam": course.get("upcoming_exam"),
                        "exam_topics": course.get("exam_topics", []),
                        "relevance_score": score,
                    }
                )

        # Sort by relevance
        return sorted(
            relevant_courses, key=lambda x: x.get("relevance_score", 0), reverse=True
        )

    def prepare_exam_guidance(
        self, student_id: str, course_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Prepare exam guidance for a student.

        Args:
            student_id: The student ID
            course_id: Optional specific course ID, if None will include all courses with upcoming exams

        Returns:
            Dictionary with exam preparation guidance
        """
        student_data = self.db.get_student_data(student_id)
        if not student_data:
            return {"error": "Student not found"}

        # Get courses with exams
        courses = self.db.get_student_courses(student_id)
        exam_courses = []

        for course in courses:
            if course_id and course.get("id") != course_id:
                continue

            if course.get("upcoming_exam"):
                exam_courses.append(
                    {
                        "id": course.get("id", ""),
                        "title": course.get("title", ""),
                        "exam_date": course.get("upcoming_exam"),
                        "exam_topics": course.get("exam_topics", []),
                    }
                )

        return {
            "student_name": student_data.get("name", ""),
            "exam_courses": exam_courses,
            "has_exams": len(exam_courses) > 0,
        }

    async def respond(self, message: str, student_id: str) -> str:
        """Respond to the incoming message with course guidance.

        Args:
            message: The student's message/query
            student_id: The student's ID

        Returns:
            Response from the agent
        """
        # Enrich query with context
        enriched_context = self.enrich_query_with_context(message, student_id)

        # Check if this is an exam-related query
        is_exam_query = any(
            term in message.lower()
            for term in ["exam", "test", "midterm", "final", "quiz", "preparation"]
        )

        if is_exam_query:
            # Add exam guidance
            exam_guidance = self.prepare_exam_guidance(student_id)
            enriched_context["exam_guidance"] = exam_guidance

        # Create prompt with context
        prompt_template = """
        Context: {context}
        
        Student: {message}
        
        Important Academic Integrity Guidelines:
        1. Provide guidance and explanations rather than direct answers
        2. Encourage critical thinking and understanding
        3. Remind users to apply their own understanding
        4. Include appropriate academic integrity disclaimers if the query relates to assignments

        Provide helpful guidance based on the student's enrolled courses and academic needs.
        """

        chain = self.create_chain(prompt_template)
        response = chain.invoke({"context": str(enriched_context), "message": message})

        return response


async def course_guidance_node(state: AgentState) -> AsyncGenerator[AgentState, None]:
    """Process node for course guidance in the agent workflow."""
    try:
        # Extract the last message and student_id from metadata
        last_message = next(
            (
                msg.content
                for msg in reversed(state["messages"])
                if isinstance(msg, HumanMessage)
            ),
            "",
        )

        metadata = state.get("metadata", {})
        student_id = metadata.get("student_id", "")

        if not student_id:
            # No student ID available, add error message and end
            state["messages"].append(
                AIMessage(
                    content="I cannot provide personalized course guidance without student identification."
                )
            )
            state["next_step"] = END
            yield state
            return

        # Initialize agent with database
        agent = CourseGuideAgent(
            db_path="path/to/your/db.sqlite"
        )  # Adjust path as needed

        # Enrich query with context
        enriched_context = agent.enrich_query_with_context(last_message, student_id)

        # Check if this is an exam-related query
        is_exam_query = any(
            term in last_message.lower()
            for term in ["exam", "test", "midterm", "final", "quiz", "preparation"]
        )

        if is_exam_query:
            # Add exam guidance
            exam_guidance = agent.prepare_exam_guidance(student_id)
            enriched_context["exam_guidance"] = exam_guidance

        # Create final response prompt
        final_prompt = f"""You are an academic course guidance assistant. Using the following context, 
        provide a helpful response while maintaining academic integrity:

        Student Context: {enriched_context}
        
        User Question: {last_message}

        Important Academic Integrity Guidelines:
        1. Provide guidance and explanations rather than direct answers
        2. Encourage critical thinking and understanding
        3. Remind users to apply their own understanding
        4. Include appropriate academic integrity disclaimers if the query relates to assignments

        Provide specific guidance based on the student's enrolled courses, academic needs, and maintaining academic integrity."""

        # Generate final response
        async for chunk in agent.llm.astream([SystemMessage(content=final_prompt)]):
            if hasattr(chunk, "content") and chunk.content:
                state["messages"].append(AIMessage(content=chunk.content))
                state["next_step"] = END
                yield state
                return

    except Exception as e:
        logging.error(f"Course guidance error: {str(e)}")
        state["messages"].append(
            AIMessage(
                content="Sorry, I encountered an error while processing your course guidance request."
            )
        )
        state["next_step"] = END
        yield state

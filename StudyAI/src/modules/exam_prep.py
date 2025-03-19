# from typing import Dict, Any, List, Optional
# from datetime import datetime, timedelta
# from src.core.base import BaseAgent
# from src.db.student_db import StudentDatabase
# from src.core.state import AgentState
# from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
# from src.core.workflow import END
# import logging
# from typing import AsyncGenerator


# class ExamPrepAgent(BaseAgent):
#     """Specialized agent for exam preparation assistance."""

#     def __init__(self):
#         """Initialize the exam preparation agent."""
#         super().__init__()
#         self.system_message = """You are an intelligent academic exam preparation assistant.
#         Help students prepare for upcoming exams by creating study plans, practice questions, 
#         and summarizing key topics they should focus on. Use the specific exam information 
#         provided in the context to give personalized responses."""

#         self.db = StudentDatabase()

#     def create_study_plan(self, student_id: str, course_id: str) -> Dict[str, Any]:
#         """Create a personalized study plan for an exam.

#         Args:
#             student_id: The student's ID
#             course_id: The specific course ID

#         Returns:
#             Dictionary with study plan information
#         """
#         student_data = self.db.get_student_data(student_id)
#         course_data = self.db.get_course_data(course_id)

#         if not student_data or not course_data:
#             return {"error": "Student or course not found"}

#         exam_date = course_data.get("upcoming_exam")
#         if not exam_date:
#             return {"error": "No upcoming exam found for this course"}

#         # Parse exam date
#         try:
#             exam_datetime = datetime.strptime(exam_date, "%Y-%m-%d")
#             days_until_exam = (exam_datetime - datetime.now()).days
#         except ValueError:
#             days_until_exam = 14  # Default if date format is invalid

#         # Create study plan based on days until exam
#         topics = course_data.get("exam_topics", [])

#         if days_until_exam < 0:
#             return {"error": "Exam date has already passed"}

#         study_plan = {
#             "course": course_data.get("title"),
#             "exam_date": exam_date,
#             "days_until_exam": days_until_exam,
#             "topics": topics,
#             "schedule": self._generate_study_schedule(topics, days_until_exam),
#         }

#         return study_plan

#     def _generate_study_schedule(
#         self, topics: List[str], days_left: int
#     ) -> List[Dict[str, Any]]:
#         """Generate a daily study schedule based on topics and available days.

#         Args:
#             topics: List of exam topics
#             days_left: Number of days until the exam

#         Returns:
#             List of daily study activities
#         """
#         schedule = []

#         # Determine study days (give 1 day break before exam)
#         study_days = max(1, days_left - 1)

#         # Distribute topics across available days
#         topics_per_day = max(1, len(topics) / study_days)

#         # Create schedule
#         current_date = datetime.now()
#         topic_index = 0

#         for day in range(study_days):
#             day_date = (current_date + timedelta(days=day)).strftime("%Y-%m-%d")
#             day_topics = []

#             # Assign topics for this day
#             topics_today = min(round(topics_per_day), len(topics) - topic_index)
#             for i in range(topics_today):
#                 if topic_index < len(topics):
#                     day_topics.append(topics[topic_index])
#                     topic_index += 1

#             # Add review days near the exam
#             if day >= study_days - 3:
#                 activity_type = "Review"
#             else:
#                 activity_type = "Learn"

#             schedule.append(
#                 {
#                     "date": day_date,
#                     "day": day + 1,
#                     "topics": day_topics,
#                     "type": activity_type,
#                 }
#             )

#         return schedule

#     def generate_practice_questions(self, course_id: str, topic: str = None) -> str:
#         """Generate practice questions for a course topic.

#         Args:
#             course_id: The course identifier
#             topic: Optional specific topic, if None will cover general exam topics

#         Returns:
#             Generated practice questions
#         """
#         course_data = self.db.get_course_data(course_id)
#         if not course_data:
#             return "Course not found."

#         topics = course_data.get("exam_topics", [])
#         if not topics:
#             return "No exam topics found for this course."

#         if topic and topic not in topics:
#             return f"Topic '{topic}' not found in exam topics."

#         # Filter to specific topic if provided
#         focus_topics = [topic] if topic else topics

#         # Create prompt for generating questions
#         prompt_template = """
#         Generate 3 practice questions for a course on {course_title}.
#         Focus on the following topic(s): {topics}.
        
#         For each question:
#         1. Create a challenging but fair question
#         2. Provide a detailed answer with explanation
#         3. Include hints for students who are stuck
        
#         Format each question clearly and number them 1-3.
#         """

#         chain = self.create_chain(prompt_template)
#         questions = chain.invoke(
#             {
#                 "course_title": course_data.get("title", ""),
#                 "topics": ", ".join(focus_topics),
#             }
#         )

#         return questions

#     async def respond(
#         self, message: str, student_id: str, course_id: Optional[str] = None
#     ) -> str:
#         """Respond to the incoming message with exam preparation guidance.

#         Args:
#             message: The student's message/query
#             student_id: The student's ID
#             course_id: Optional specific course ID

#         Returns:
#             Response from the agent
#         """
#         student_data = self.db.get_student_data(student_id)
#         if not student_data:
#             return "Student data not found. Please provide a valid student ID."

#         # Determine if we need to identify a course from the message
#         if not course_id:
#             enrolled_courses = student_data.get("enrolled_courses", [])
#             course_id = self._identify_course_from_message(message, enrolled_courses)

#         # If still no course_id, but need one
#         if not course_id and (
#             "study plan" in message.lower() or "schedule" in message.lower()
#         ):
#             return "Please specify which course you need help with for the exam preparation."

#         # Process based on query intent
#         if "study plan" in message.lower() or "schedule" in message.lower():
#             study_plan = self.create_study_plan(student_id, course_id)

#             # Format study plan as a response
#             prompt_template = """
#             Create a personalized study plan response based on this data:
#             {study_plan}
            
#             Format the response as a helpful message to the student, explaining the 
#             study plan day by day and providing motivation. Be concise but informative.
#             """

#             chain = self.create_chain(prompt_template)
#             response = chain.invoke({"study_plan": str(study_plan)})

#         elif (
#             "practice question" in message.lower()
#             or "sample question" in message.lower()
#         ):
#             # Extract topic if mentioned
#             topic = self._extract_topic_from_message(message, course_id)
#             questions = self.generate_practice_questions(course_id, topic)
#             response = questions

#         else:
#             # General exam help
#             prompt_template = """
#             The student is asking about exam preparation for their courses.
#             Student: {message}
            
#             Student info: {student_info}
#             Course info: {course_info}
            
#             Provide helpful guidance on how to prepare for their upcoming exams,
#             with specific advice tailored to their courses and academic level.
#             Be encouraging and practical in your response.
#             """

#             course_info = self.db.get_course_data(course_id) if course_id else None

#             chain = self.create_chain(prompt_template)
#             response = chain.invoke(
#                 {
#                     "message": message,
#                     "student_info": str(student_data),
#                     "course_info": (
#                         str(course_info)
#                         if course_info
#                         else "No specific course identified"
#                     ),
#                 }
#             )

#         return response

#     def _identify_course_from_message(
#         self, message: str, enrolled_courses: List[str]
#     ) -> Optional[str]:
#         """Identify which course the message is referring to."""
#         message_lower = message.lower()

#         for course_id in enrolled_courses:
#             course_data = self.db.get_course_data(course_id)
#             if not course_data:
#                 continue

#             # Check for course ID or title in message
#             title_lower = course_data.get("title", "").lower()
#             if course_id.lower() in message_lower or title_lower in message_lower:
#                 return course_id

#         return None

#     def _extract_topic_from_message(
#         self, message: str, course_id: str
#     ) -> Optional[str]:
#         """Extract a specific topic from the message if mentioned."""
#         message_lower = message.lower()
#         course_data = self.db.get_course_data(course_id)

#         if not course_data:
#             return None

#         for topic in course_data.get("exam_topics", []):
#             if topic.lower() in message_lower:
#                 return topic

#         return None


# async def exam_prep_node(state: AgentState) -> AsyncGenerator[AgentState, None]:
#     """Process node for exam preparation in the agent workflow."""
#     try:
#         # Extract the last message and student_id from metadata
#         last_message = next(
#             (
#                 msg.content
#                 for msg in reversed(state["messages"])
#                 if isinstance(msg, HumanMessage)
#             ),
#             "",
#         )

#         metadata = state.get("metadata", {})
#         student_id = metadata.get("student_id", "")
#         course_id = metadata.get("course_id")  # Optional course ID

#         if not student_id:
#             state["messages"].append(
#                 AIMessage(
#                     content="I cannot provide exam preparation guidance without student identification."
#                 )
#             )
#             state["next_step"] = END
#             yield state
#             return

#         # Initialize agent
#         agent = ExamPrepAgent(db_path="path/to/your/db.sqlite")  # Adjust path as needed

#         # Determine if we need to identify a course from the message
#         if not course_id:
#             student_data = agent.db.get_student_data(student_id)
#             enrolled_courses = student_data.get("enrolled_courses", [])
#             course_id = agent._identify_course_from_message(
#                 last_message, enrolled_courses
#             )

#         # Create response based on query intent
#         if "study plan" in last_message.lower() or "schedule" in last_message.lower():
#             if not course_id:
#                 state["messages"].append(
#                     AIMessage(
#                         content="Please specify which course you need a study plan for."
#                     )
#                 )
#                 state["next_step"] = END
#                 yield state
#                 return

#             study_plan = agent.create_study_plan(student_id, course_id)

#             final_prompt = f"""You are an exam preparation assistant. Create a personalized study plan response:

#             Study Plan Data: {study_plan}
#             User Question: {last_message}

#             Important Academic Integrity Guidelines:
#             1. Focus on study strategies and time management
#             2. Encourage active learning and understanding
#             3. Provide structured preparation guidance
#             4. Include motivation and learning tips

#             Create a detailed, encouraging response that outlines the study plan and provides practical advice."""

#         elif "practice" in last_message.lower() or "question" in last_message.lower():
#             if not course_id:
#                 state["messages"].append(
#                     AIMessage(
#                         content="Please specify which course you need practice questions for."
#                     )
#                 )
#                 state["next_step"] = END
#                 yield state
#                 return

#             topic = agent._extract_topic_from_message(last_message, course_id)
#             questions = agent.generate_practice_questions(course_id, topic)

#             final_prompt = f"""You are an exam preparation assistant. Review and present these practice questions:

#             Practice Questions: {questions}
#             User Question: {last_message}

#             Important Academic Integrity Guidelines:
#             1. Emphasize learning over memorization
#             2. Encourage understanding core concepts
#             3. Provide helpful hints before answers
#             4. Include explanation of thought process

#             Present the questions in a structured format with clear learning objectives."""

#         else:
#             # General exam preparation guidance
#             student_data = agent.db.get_student_data(student_id)
#             course_info = agent.db.get_course_data(course_id) if course_id else None

#             final_prompt = f"""You are an exam preparation assistant. Provide general exam guidance:

#             Student Info: {student_data}
#             Course Info: {course_info if course_info else "No specific course identified"}
#             User Question: {last_message}

#             Important Academic Integrity Guidelines:
#             1. Focus on study strategies and preparation techniques
#             2. Encourage time management and organization
#             3. Provide general exam-taking tips
#             4. Include stress management advice

#             Create a helpful response with practical exam preparation guidance."""

#         # Generate final response
#         async for chunk in agent.llm.astream([SystemMessage(content=final_prompt)]):
#             if hasattr(chunk, "content") and chunk.content:
#                 state["messages"].append(AIMessage(content=chunk.content))
#                 state["next_step"] = END
#                 yield state
#                 return

#     except Exception as e:
#         logging.error(f"Exam prep error: {str(e)}")
#         state["messages"].append(
#             AIMessage(
#                 content="Sorry, I encountered an error while processing your exam preparation request."
#             )
#         )
#         state["next_step"] = END
#         yield state

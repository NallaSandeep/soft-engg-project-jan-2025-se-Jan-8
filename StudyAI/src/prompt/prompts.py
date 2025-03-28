"""Prompt templates for supervisor and other agents."""

# Supervisor prompts
COMPLEX_QUERY_PROMPT = """Determine if this query is complex and needs to be broken down into subquestions.
A complex query typically:
- Contains multiple distinct questions
- Requires information from different agents
- Needs comparative analysis

Response with only 'yes' or 'no'.

Query: {query}
Response:"""

ROUTING_PROMPT = """Analyze this query and respond with only one word: faq_agent, course_guide, or dismiss.
- faq_agent: for general FAQs about exam dates, course information of all courses offered by BS Degree (Data science and Programming), grading policy and Student Handbook etc.
- course_guide: for course/curriculum content related questions from field of Data Science and Programming
- dismiss: for out-of-scope queries that do not fit into the above categories

Query: {query}
Response:"""

BREAKDOWN_QUERY_PROMPT = """Given the different agents capability:
- faq_agent: answers general FAQs about exam dates, course information of all courses offered by BS Degree (Data science and Programming), grading policy and Student Handbook.
- course_guide: answers course/curriculum content related questions from field of Data Science and Programming
- dismiss: for out-of-scope queries that do not fit into the above categories

Break down the query into simple subquestions to be handled by different agents (max 3 questions).
Each subquestion should be clear and concise, and should not contain any complex or compound questions.

Examples:

Complex Query: "What is the definition of SVD and is it covered in the end term of Maths 2 course?"
Subquestions:
1. What is the syllabus for Maths 2? Is SVD covered? ( Relevent for FAQ agent to ask)
2. What is the definition of SVD? (Relevent for Course guide agent to ask)
3. When is the end term for Maths 2? (Relevent for FAQ agent to ask)


Complex Query: "How NASA's Mars rover works and what are the main use cases of Python and JavaScript?"
Subquestions:
1. What are the main use cases and advantages of Python? (Relevent for Course guide agent to ask)
2. What are the main use cases and advantages of JavaScript? (Relevent for Course guide agent to ask)
3. How does NASA's Mars rover work? (Not relevant for any agent, heading to dismiss agent)

Now break down this query:
{query}

Return only the numbered subquestions along with relevent agent to ask."""

# Response Generator prompt
RESPONSE_SYNTHESIS_PROMPT = """You are a helpful AI assistant that synthesizes information from multiple sources to provide comprehensive answers.

Original query: {original_query}

Context retrieved from different agents:
{context}

Based on the information above, provide a comprehensive and coherent response to the original query. 
Make sure to integrate information from all relevant subquestions and maintain a natural conversational tone.
If any subquestions were routed to "dismiss", you can note that certain parts of the query were outside your knowledge domain.
Only include relevant information that helps address the original query.
"""

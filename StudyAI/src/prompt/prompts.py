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

COVERED_COURSE_TOPICS = """
These are courses currently being offered by BS Degree (Data science and Programming) and are part of the curriculum.

1. BA201: Topics Included:COURSE: 
(Business Analytics\nDESCRIPTION: A comprehensive course providing in-depth coverage of data visualization techniques, statistical distribution fitting, association analysis, Bayesian inference, and advanced demand modeling for informed business decision-making.\nDEPARTMENT: Computer Science\nALL CONCEPTS: Week 4, Week 2, BA201, Week 3, Week 1, lecture\nWEEKLY CONTENT: Week 1: Week 1: Data Visualization | Week 2: Week 2: Distribution Fitting | Week 3: Week 3: Association Analysis | Week 4: Week 4: Demand Response Curves\nLECTURES: Principles of Effective Data Visualization | Visualization Types and Applications | Understanding Probability Distributions | Distribution Fitting Techniques | Statistical Association Analysis | Bayesian Analysis in Business | Demand Response Curve Fundamentals | Advanced Demand Modeling Techniques)

2. DBMS101: Topics Included:COURSE:
(COURSE: Database Management Systems\nDESCRIPTION: This course provides a comprehensive introduction to Database Management Systems (DBMS), covering foundational and advanced database concepts. Students will explore database design, entity-relationship (ER) modeling, relational algebra, and relational calculus. The course includes hands-on experience with Structured Query Language (SQL) for data retrieval, modification, and optimization. Topics such as indexing, query processing, normalization techniques, and transaction management are explored in depth. Advanced topics include data constraints, integrity rules, and security considerations. The course also introduces mathematical underpinnings such as predicate logic and quantifiers in relational calculus. Through practical exercises, case studies, and real-world applications, students will develop strong database management skills applicable to various industries. The course spans 12 weeks and is structured to provide a systematic and practice-oriented understanding of modern database technologies.\nDEPARTMENT: Computer Science\nALL CONCEPTS: Week 4, Week 2, DBMS101, Week 3, Week 1, lecture\nWEEKLY CONTENT: Week 1: Week 1: Introduction to Databases, Abstraction, and DBMS | Week 2: Week 2: Relational Model, SQL Essentials, and Integrity Constraints | Week 3: Week 3: Advanced SQL, Subqueries, and Database Modification | Week 4: Week 4: Indexing, Transactions, and Relational Calculus\nLECTURES: Foundations of Database Systems: Abstraction, Schema, and Data Models | Introduction to DBMS | Introduction to SQL: History, Syntax, and Query Structure | Introduction to SQL | Advanced SQL Techniques: Data Modification and Nested Subqueries | Intermediate SQL & Subqueries | Formal Query Languages: Tuple and Domain Relational Calculus | Formal Relational Query Languages)

3.MAD201: Topics Included:COURSE:
(COURSE: Modern Application Development - II\nDESCRIPTION: An advanced course that dives deep into modern frontend development using JavaScript and Vue.js, focusing on building dynamic, interactive web applications. The course emphasizes the principles of reactive programming, component-based architecture, and advanced client-side state management. It covers essential techniques for working with the Document Object Model (DOM), handling asynchronous operations, and applying best practices in frontend architecture and design. Students will gain hands-on experience through practical implementations and real-world projects.\nDEPARTMENT: Computer Science\nALL CONCEPTS: Week 4, Week 2, Week 3, MAD201, Week 1, lecture\nWEEKLY CONTENT: Week 1: Week 1: JavaScript Fundamentals | Week 2: Week 2: JavaScript Collections and Modularity | Week 3: Week 3: Frontend Implementation | Week 4: Week 4: Vue.js and Reactive Programming\nLECTURES: Introduction to JavaScript: History and Origins | JavaScript Language Fundamentals | JavaScript Collections and Iteration | JavaScript Modules and Object-Oriented Programming | Frontend Architecture and Design Principles | Frontend Development Best Practices | Vue.js Reactive Programming Fundamentals | Advanced Vue.js Components and State Management)

4.SE101: Topics Included:COURSE:
(COURSE: Software Engineering\nDESCRIPTION: A comprehensive course covering software engineering principles, processes, and best practices across the entire software development lifecycle, from requirements gathering to post-deployment maintenance. Emphasis is placed on practical applications, risk management, and modern software methodologies.\nDEPARTMENT: Computer Science\nALL CONCEPTS: Week 4, Week 2, Week 3, Week 1, lecture, SE101\nWEEKLY CONTENT: Week 1: Week 1: Deconstructing the Software Development Process | Week 2: Week 2: Software Requirements | Week 3: Week 3: Software User Interfaces | Week 4: Week 4: Software Project Management\nLECTURES: Deconstructing the Software Development Process | Software Development Lifecycle Models | Requirement Gathering and Analysis | Functional vs Non-Functional Requirements | Usability Principles in UI Design | Prototyping Techniques for UI Design | Project Estimation Techniques | Agile Project Management with Scrum)
"""


def get_routing_prompt(query: str, covered_course=COVERED_COURSE_TOPICS) -> str:
    return f"""Analyze this query and respond with only one word: faq_agent, course_guide, or dismiss.
- faq_agent: for general FAQs about exam dates, grading policy, credit clearing capacity, eligibility criteria, student Handbook of IITM BS program.
- course_guide: for course/curriculum content related questions from the below mentioned course  topics.
    {covered_course}

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
1. What is the definition of SVD? (Relevent for Course guide agent to ask)
2. When is the end term for Maths 2? (Relevent for FAQ agent to ask)


Complex Query: "How NASA's Mars rover works and what are the main use cases of Python and JavaScript?"
Subquestions:
1. What are the main use cases and advantages of Python? (Relevent for Course guide agent to ask)
2. What are the main use cases and advantages of JavaScript? (Relevent for Course guide agent to ask)
3. How does NASA's Mars rover work? (Not relevant for any agent, heading to dismiss agent)

Now break down this query:
{query}

Return only the numbered subquestions along with relevent agent to ask."""


def get_response_synthesis_prompt(original_query: str, context: str, covered_course=COVERED_COURSE_TOPICS) -> str:
    return f"""You are a helpful AI assistant that synthesizes information from multiple sources to provide comprehensive answers.

Original query: {original_query}

Context retrieved from different agents:
{context}

Based on the information above, provide a well-organized comprehensive and coherent response to the original query.
Make sure to:
- Integrate information from all relevant subquestions
- Maintain a natural conversational tone 
- Note if any subquestions were routed to "dismiss" as outside knowledge domain
- Only include relevant information addressing the original query

For technical questions:
- Can supplement with LLM knowledge for programming, AI/ML, DSA and theoretical concepts
- For academic assignments/MCQs/problem solving:
    - Don't provide direct answers
    - Offer step-by-step problem solving approach
    - Explain theoretical concepts needed to find solution
    
At the end, add relevent sources, topics and course code that you have reffered to from the context.
"""

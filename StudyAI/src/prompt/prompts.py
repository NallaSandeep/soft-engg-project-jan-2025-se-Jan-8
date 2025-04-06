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

Course Code: BA201 
Course name: Business Analytics 
Course description: The Business Analytics course (BA201) offers a comprehensive and expanded exploration of analytical techniques essential for data-driven decision-making. It covers data visualization for effective communication, fitting probability distributions to business data, statistical association analysis, and Bayesian inference for probabilistic reasoning. The curriculum includes advanced demand modeling and price optimization, regression analysis for predictive modeling, time series forecasting for analyzing temporal data, principles of experimental design for causal inference, and an introduction to optimization techniques for resource allocation. Real-world case studies and practical exercises reinforce these methodologies.

Weeks names/Topics covered in the content:

Week 1: Foundations of Data Visualization: principles, techniques for effective communication, chart selection and design.

Week 2: Probability Distribution Fitting: fitting distributions, parameter estimation (MLE), goodness-of-fit testing.

Week 3: Comprehensive Statistical Association Analysis and Bayesian Inference: analyzing relationships, contingency tables, Bayes' theorem.

Week 4: Advanced Demand Modeling and Price Optimization: demand curves, elasticity estimation, pricing strategies, revenue management.

Week 5: Regression Analysis: building, interpreting, and evaluating simple linear regression models.

Week 6: Multiple Linear Regression Analysis: modeling with multiple predictors, coefficient interpretation, multicollinearity.

Week 7: Introduction to Time Series Forecasting: time series data, components (trends, seasonality), basic forecasting methods.

Week 8: Principles of Experimental Design: causal inference, A/B testing, randomization, control groups, validity.

Week 9: Introduction to Optimization Techniques: defining optimization problems, linear programming concepts, constraints.

================

Course Code: DBMS201 
Course name: Advanced Database Management Systems 
Course description: This expanded course provides an in-depth exploration of DBMS, covering advanced database design, implementation, and management. Students will master advanced ER modeling, relational algebra and calculus, and complex SQL. The course extensively covers indexing, query processing, normalization, transaction management, and concurrency control. New topics include NoSQL databases, distributed database systems, data warehousing, OLAP, database security, and performance tuning. Through practical exercises and case studies, students will develop strong database management skills for enterprise-level systems.

Weeks names/Topics covered in the content:

Week 1: Foundations Revisited: data abstraction levels (physical, logical, view), database architectures, data independence.

Week 2: Advanced Relational Model, SQL Deep Dive, and Enhanced Integrity Constraints: domains, keys, SQL DDL, constraints.

Week 3: Expert SQL: Subqueries, Views, and Data Modification Mastery: nested, correlated, scalar subqueries, CTEs, data modification.

Week 4: Deep Dive into Indexing and Query Processing Strategies: index types (B-tree, hash), query optimization.

Week 5: Advanced Normalization and Database Design Methodologies: BCNF, 4NF, 5NF, DKNF, design approaches.

Week 6: Transaction Management and Concurrency Control: ACID properties, isolation levels, concurrency anomalies, locking.

Week 7: Database Recovery Techniques and Failure Management: logging (WAL), checkpoints, recovery algorithms.

Week 8: Introduction to NoSQL Databases: Concepts and Key-Value Stores: characteristics, architecture, operations, use cases.

Week 9: NoSQL Databases: Document Databases and Column-Family Stores: data models, MongoDB, Cassandra.

Week 10: NoSQL Databases: Graph Databases and Polyglot Persistence: Neo4j, Cypher, graph querying, database selection.

Week 11: Distributed Databases: Architectures and Data Replication: homogeneous, heterogeneous, replication strategies, consistency.

Week 12: Distributed Databases: Query Processing and Concurrency Control: fragmentation, join strategies, distributed locking, 2PC.

Week 13: Data Warehousing and OLAP: Principles and Design: OLTP vs. OLAP, data warehouse architecture, schemas.

Week 14: Data Warehousing and OLAP: Operations and Advanced Topics: OLAP operations, server types, data cube computation.

Week 15: Database Security: Principles and Implementation: threats, security goals, authentication, authorization.

Week 16: Database Performance Tuning and Emerging Trends: query optimization, indexing, in-memory, cloud databases, AI integration.


================


Course Code: JAVA101 
Course name: Introduction to Java Programming 
Course description: A foundational course in Java programming principles, this course introduces basic syntax, data types, operators, and control flow statements. Students will learn object-oriented programming concepts including classes, objects, constructors, access modifiers, inheritance, polymorphism, and abstract classes. The course also covers exception handling for runtime errors and provides an introduction to the Java collections framework with basic collection types. The goal is to equip students with a solid understanding of the fundamentals of Java programming.

Weeks names/Topics covered in the content:

Week 1: Introduction to Java and Setup: Java history, JDK installation, basic syntax, JVM.

Week 2: Data Types, Variables, and Operators: primitive types, variable declaration, arithmetic, comparison.

Week 3: Control Flow Statements: if-else, switch statements, for, while, do-while loops.

Week 4: Introduction to Classes and Objects: class definition, object creation, instance variables, methods.

Week 5: Constructors and Access Modifiers: default, parameterized constructors, public, private, protected, default.

Week 6: Inheritance: superclass, subclass, extends keyword, method overriding, super keyword.

Week 7: Polymorphism and Abstract Classes: upcasting, downcasting, abstract classes, abstract methods.

Week 8: Exception Handling: try-catch blocks, finally block, throwing exceptions, built-in hierarchy.

Week 9: Introduction to Collections: ArrayList, LinkedList, HashSet, basic operations.

================

Course Code: MAD201 
Course name: Modern Application Development II 
Course description: This course focuses on modern web application development, building upon foundational knowledge with advanced JavaScript, HTML5, and CSS3. Students will explore advanced JavaScript features (ES6+), DOM manipulation, event handling, and asynchronous operations. The course covers advanced CSS3 for responsive design and UI enhancements. It also introduces modern frontend frameworks, specifically Vue.js and React, covering components, reactivity, state management, and architectural patterns. Best practices for frontend development, including testing and performance optimization, are also emphasized.

Weeks names/Topics covered in the content:

Week 1: Advanced JavaScript Fundamentals and ES6+: syntax, scope, data types, functions, modules.

Week 2: DOM Manipulation, Events, and Asynchronous JavaScript: DOM traversal, event handling, Fetch API.

Week 3: Introduction to HTML5 and Advanced CSS3: semantic HTML, advanced selectors, box model, Flexbox, Grid.

Week 4: Introduction to Vue.js: Components and Reactivity: Vue components, Options API, reactivity, data binding.

Week 5: Advanced Vue.js: Composition API and State Management: setup, ref, reactive, Vuex store.

Week 6: Introduction to React: Components and JSX: React components, JSX syntax, props, event handling.

Week 7: Advanced React: Hooks and State Management: useState, useEffect, Context API.

Week 8: Frontend Architecture, Best Practices, and Testing: patterns, clean code, performance, accessibility, testing.

================

Course Code: SE101 
Course name: Software Engineering 
Course description: This comprehensive course covers software engineering principles, processes, and best practices across the entire software development lifecycle. It contrasts traditional plan-driven models (Waterfall, V-Model) with adaptive frameworks (Agile, Scrum). Students will learn about requirements gathering (SRS), software design (UML, architectural patterns), robust testing strategies, project estimation, risk management, and agile development practices. The course also addresses software deployment (DevOps), maintenance and evolution, and software engineering ethics, equipping students for effective software development and management.

Weeks names/Topics covered in the content:

Week 1: Deconstructing the Software Development Process: SDLC models, traditional and Agile methodologies, processes.

Week 2: Software Requirements Engineering: stakeholder identification, functional/non-functional requirements, SRS documentation.

Week 3: Software Architecture and Design: architectural styles, design principles (SOLID), design patterns, UML.

Week 4: Software Testing and Quality Assurance: testing levels, techniques (black/white-box), quality attributes, TDD.

Week 5: Software Deployment and DevOps: deployment strategies, infrastructure as code, CI/CD, containerization.

Week 6: Software Maintenance and Evolution: types of maintenance, refactoring, technical debt management.

Week 7: Agile Project Management - Advanced Topics: scaled agile frameworks, Kanban, backlog and release planning.

Week 8: Software Engineering Best Practices and Ethics: code quality, documentation, ethical considerations, future trends.
"""


def get_routing_prompt(query: str, covered_course=COVERED_COURSE_TOPICS) -> str:
    return f"""Analyze this query and respond with only one word: faq_agent, course_guide, or dismiss.
- faq_agent: for general FAQs about exam dates, grading policy, credit clearing capacity, eligibility criteria, student Handbook of IITM BS program.
- course_guide: for course/curriculum content related questions from the below mentioned course  topics.
    {covered_course}

- dismiss: for out-of-scope queries that do not fit into the above categories

Query: {query}
Response:"""


def get_relevent_course_prompt(
    original_query: str, covered_course=COVERED_COURSE_TOPICS
) -> str:
    return f"""Analyze this query and determine which course it relates to based on the topics covered in each course.
Return the most relevant course in the following format: "COURSE_CODE|COURSE_NAME|BRIEF_SUMMARY"
For example: "DBMS201|Database Management Systems|This course covers database concepts and SQL fundamentals..."
If the query doesn't match any course topics, respond with 'None'.

Course Topics:
{covered_course}

When analyzing:
- Look for specific course names, codes, or topics mentioned in the query
- Check for subject matter that aligns with course content (e.g., database concepts for DBMS101)
- Consider technical terms that appear in specific course descriptions
- If query matches multiple courses, select the most relevant one based on topic specificity
- For the selected course, provide a brief 3-4 sentence summary about the course content
- Respond with 'None' if the query doesn't clearly relate to any of these courses

Original query: {original_query}

Response (format: "COURSE_CODE|COURSE_NAME|BRIEF_SUMMARY" or "None"):"""


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


def get_response_synthesis_prompt(
    original_query: str, context: str, covered_course=COVERED_COURSE_TOPICS
) -> str:
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
If no context is available supplement with your knowledge, don't mention that no context is available.
"""

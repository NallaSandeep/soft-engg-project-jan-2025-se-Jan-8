[INFO] Successfully imported StudyHub models and database
[INFO] Successfully imported StudyHub models and database
[2025-04-06 04:29:03] [INFO] Starting database initialization...
[2025-04-06 04:29:03] [INFO] RESETTING DATABASE - THIS WILL DELETE ALL DATA
[2025-04-06 04:29:03] [INFO] Dropping all tables...
[2025-04-06 04:29:05] [INFO] Creating tables...
[2025-04-06 04:29:06] [INFO] Database reset completed successfully
[2025-04-06 04:29:06] [INFO] PHASE 1: CREATING USERS
[2025-04-06 04:29:06] [INFO] Creating admin user...
[2025-04-06 04:29:06] [INFO] Created admin user: admin (ID: 1)
[2025-04-06 04:29:06] [INFO] Creating 5 student users...
[2025-04-06 04:29:06] [DEBUG] Created student: student1 (ID: 2)
[2025-04-06 04:29:06] [DEBUG] Created student: student2 (ID: 3)
[2025-04-06 04:29:06] [DEBUG] Created student: student3 (ID: 4)
[2025-04-06 04:29:06] [DEBUG] Created student: student4 (ID: 5)
[2025-04-06 04:29:06] [DEBUG] Created student: student5 (ID: 6)
[2025-04-06 04:29:07] [INFO] PHASE 1 COMPLETED - USERS CREATED
[2025-04-06 04:29:07] [INFO] PHASE 2: IMPORTING COURSE CONTENT
[2025-04-06 04:29:07] [INFO] Calling import_courses.py with verbose logging...
[2025-04-06 04:29:07] [INFO] Found course data directory: E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course
[2025-04-06 04:29:07] [INFO] Found 5 JSON files in E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course
[2025-04-06 04:29:07] [INFO] Processing ba_updated.json...
[2025-04-06 04:29:07] [INFO] === Processing file: E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course\ba_updated.json ===
[2025-04-06 04:29:07] [INFO] Parsing JSON file: E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course\ba_updated.json
[2025-04-06 04:29:07] [INFO] Successfully parsed JSON with 7 top-level keys
[2025-04-06 04:29:07] [INFO] Course info found: Business Analytics (BA201)
[2025-04-06 04:29:07] [INFO] Found 9 weeks
[2025-04-06 04:29:07] [INFO] Found 8 lectures
[2025-04-06 04:29:07] [INFO] Found 10 assignments
[2025-04-06 04:29:07] [INFO] Found 45 questions
[2025-04-06 04:29:07] [INFO] Checking for existing courses in the database...
[2025-04-06 04:29:07] [INFO] No existing courses found in the database
[2025-04-06 04:29:07] [DEBUG]   Extracting from LLM_Summary - Found acronyms: 0, synonyms: 0
[2025-04-06 04:29:07] [DEBUG]   Creating new course BA201 - Acronyms: 0, Synonyms: 0
[2025-04-06 04:29:07] [DEBUG]   Course model BA201 (before adding) - Acronyms: {}, Synonyms: {}
[2025-04-06 04:29:07] [INFO] Created course: BA201 - Business Analytics
[2025-04-06 04:29:07] [INFO] Processing 9 weeks for course BA201
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 1
[2025-04-06 04:29:07] [DEBUG] Created week 1: Week 1: Foundations of Data Visualization (DB ID: 1)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 2
[2025-04-06 04:29:07] [DEBUG] Created week 2: Week 2: Advanced Probability Distribution Fitting (DB ID: 2)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 3
[2025-04-06 04:29:07] [DEBUG] Created week 3: Week 3: Comprehensive Statistical Association Analysis and Bayesian Inference (DB ID: 3)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 4
[2025-04-06 04:29:07] [DEBUG] Created week 4: Week 4: Advanced Demand Modeling and Price Optimization (DB ID: 4)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 5
[2025-04-06 04:29:07] [DEBUG] Created week 5: Week 5: Fundamentals of Regression Analysis (DB ID: 5)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 6
[2025-04-06 04:29:07] [DEBUG] Created week 6: Multiple Linear Regression Analysis (DB ID: 6)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 7
[2025-04-06 04:29:07] [DEBUG] Created week 7: Introduction to Time Series Forecasting (DB ID: 7)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 8
[2025-04-06 04:29:07] [DEBUG] Created week 8: Introduction to Experimental Design (DB ID: 8)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 9
[2025-04-06 04:29:07] [DEBUG] Created week 9: Introduction to Optimization Techniques (DB ID: 9)
[2025-04-06 04:29:07] [INFO] Processing 8 lectures
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Principles of Effective Data Visualization for week 1
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Visualization Types and Applications for week 1
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Understanding Probability Distributions for week 2
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Distribution Fitting Techniques for week 2
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Statistical Association Analysis for week 3
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Bayesian Analysis in Business for week 3
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Demand Response Curve Fundamentals for week 4
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Advanced Demand Modeling Techniques for week 4
[2025-04-06 04:29:07] [INFO] Processed 9 weeks and 8 lectures for course BA201
[2025-04-06 04:29:07] [INFO] Creating question bank...
[2025-04-06 04:29:07] [INFO] Creating 45 questions for course BA201
[2025-04-06 04:29:07] [DEBUG]   Created question 1: Which of the following is NOT ...
[2025-04-06 04:29:07] [DEBUG]   Created question 2: Which of the following visuali...
[2025-04-06 04:29:07] [DEBUG]   Created question 3: In a contingency table showing...
[2025-04-06 04:29:07] [DEBUG]   Created question 4: Calculate P(A|B) given P(A) = ...
[2025-04-06 04:29:07] [DEBUG]   Created question 5: Which of the following are req...
[2025-04-06 04:29:07] [DEBUG]   Created question 6: A chi-square test for independ...
[2025-04-06 04:29:07] [DEBUG]   Created question 7: Calculate the degrees of freed...
[2025-04-06 04:29:07] [DEBUG]   Created question 8: In a survey, 60% prefer Brand ...
[2025-04-06 04:29:07] [DEBUG]   Created question 9: In a survey of 200 people, 120...
[2025-04-06 04:29:07] [DEBUG]   Created question 10: Which visualization would best...
[2025-04-06 04:29:07] [DEBUG]   Created question 11: A demand response curve has wh...
[2025-04-06 04:29:07] [DEBUG]   Created question 12: Calculate price elasticity whe...
[2025-04-06 04:29:07] [DEBUG]   Created question 13: Which of the following distrib...
[2025-04-06 04:29:07] [DEBUG]   Created question 14: In hypothesis testing, what do...
[2025-04-06 04:29:07] [DEBUG]   Created question 15: Which of the following are ste...
[2025-04-06 04:29:07] [DEBUG]   Created question 16: Calculate the slope of a linea...
[2025-04-06 04:29:07] [DEBUG]   Created question 17: Which goodness-of-fit test is ...
[2025-04-06 04:29:07] [DEBUG]   Created question 18: In a market experiment, prices...
[2025-04-06 04:29:07] [DEBUG]   Created question 19: Which of the following are ass...
[2025-04-06 04:29:07] [DEBUG]   Created question 20: What is the main advantage of ...
[2025-04-06 04:29:07] [DEBUG]   Created question 21: Calculate R▓ for a regression ...
[2025-04-06 04:29:07] [DEBUG]   Created question 22: Which of the following distrib...
[2025-04-06 04:29:07] [DEBUG]   Created question 23: In hypothesis testing, what is...
[2025-04-06 04:29:07] [DEBUG]   Created question 24: What is the primary purpose of...
[2025-04-06 04:29:07] [DEBUG]   Created question 25: Which of the following transfo...
[2025-04-06 04:29:07] [DEBUG]   Created question 26: In a simple linear regression ...
[2025-04-06 04:29:07] [DEBUG]   Created question 27: What does the R-squared value ...
[2025-04-06 04:29:07] [DEBUG]   Created question 28: Which of the following is a ke...
[2025-04-06 04:29:07] [DEBUG]   Created question 29: In multiple linear regression,...
[2025-04-06 04:29:07] [DEBUG]   Created question 30: What is multicollinearity in t...
[2025-04-06 04:29:07] [DEBUG]   Created question 31: Which of the following is a co...
[2025-04-06 04:29:07] [DEBUG]   Created question 32: What is a key characteristic o...
[2025-04-06 04:29:07] [DEBUG]   Created question 33: Which component of a time seri...
[2025-04-06 04:29:07] [DEBUG]   Created question 34: What is the primary goal of a ...
[2025-04-06 04:29:07] [DEBUG]   Created question 35: In simple exponential smoothin...
[2025-04-06 04:29:07] [DEBUG]   Created question 36: Which forecast accuracy metric...
[2025-04-06 04:29:07] [DEBUG]   Created question 37: What is the purpose of randomi...
[2025-04-06 04:29:07] [DEBUG]   Created question 38: What is the role of a control ...
[2025-04-06 04:29:07] [DEBUG]   Created question 39: What is the purpose of replica...
[2025-04-06 04:29:07] [DEBUG]   Created question 40: In a completely randomized exp...
[2025-04-06 04:29:07] [DEBUG]   Created question 41: What is the primary advantage ...
[2025-04-06 04:29:07] [DEBUG]   Created question 42: What is the purpose of Analysi...
[2025-04-06 04:29:07] [DEBUG]   Created question 43: What are the three basic compo...
[2025-04-06 04:29:07] [DEBUG]   Created question 44: In linear programming, what is...
[2025-04-06 04:29:07] [DEBUG]   Created question 45: According to the graphical met...
[2025-04-06 04:29:07] [INFO] Created 90 questions for course BA201
[2025-04-06 04:29:07] [INFO] Creating assignments...
[2025-04-06 04:29:07] [INFO] Creating 10 assignments for course BA201
[2025-04-06 04:29:07] [DEBUG]   Creating assignment: Data Visualization Fundamentals (Week 1, Type: practice)
[2025-04-06 04:29:07] [INFO]   Adding 3 questions to assignment Data Visualization Fundamentals
[2025-04-06 04:29:07] [DEBUG]     Added question 1 to assignment Data Visualization Fundamentals
[2025-04-06 04:29:07] [DEBUG]     Added question 2 to assignment Data Visualization Fundamentals
[2025-04-06 04:29:07] [DEBUG]     Added question 10 to assignment Data Visualization Fundamentals
[2025-04-06 04:29:07] [DEBUG]   Created assignment 1: Data Visualization Fundamentals
[2025-04-06 04:29:07] [DEBUG]   Creating assignment: Probability and Statistical Analysis (Week 3, Type: practice)
[2025-04-06 04:29:07] [INFO]   Adding 4 questions to assignment Probability and Statistical Analysis
[2025-04-06 04:29:07] [DEBUG]     Added question 3 to assignment Probability and Statistical Analysis
[2025-04-06 04:29:07] [DEBUG]     Added question 4 to assignment Probability and Statistical Analysis
[2025-04-06 04:29:07] [DEBUG]     Added question 5 to assignment Probability and Statistical Analysis
[2025-04-06 04:29:07] [DEBUG]     Added question 9 to assignment Probability and Statistical Analysis
[2025-04-06 04:29:07] [DEBUG]   Created assignment 2: Probability and Statistical Analysis
[2025-04-06 04:29:07] [DEBUG]   Creating assignment: Chi-square and Independence Testing (Week 3, Type: practice)
[2025-04-06 04:29:07] [INFO]   Adding 3 questions to assignment Chi-square and Independence Testing
[2025-04-06 04:29:07] [DEBUG]     Added question 6 to assignment Chi-square and Independence Testing
[2025-04-06 04:29:07] [DEBUG]     Added question 7 to assignment Chi-square and Independence Testing
[2025-04-06 04:29:07] [DEBUG]     Added question 8 to assignment Chi-square and Independence Testing
[2025-04-06 04:29:07] [DEBUG]   Created assignment 3: Chi-square and Independence Testing
[2025-04-06 04:29:07] [DEBUG]   Creating assignment: Distribution Fitting and Hypothesis Testing (Week 2, Type: graded)
[2025-04-06 04:29:07] [INFO]   Adding 6 questions to assignment Distribution Fitting and Hypothesis Testing
[2025-04-06 04:29:07] [DEBUG]     Added question 13 to assignment Distribution Fitting and Hypothesis Testing
[2025-04-06 04:29:07] [DEBUG]     Added question 14 to assignment Distribution Fitting and Hypothesis Testing
[2025-04-06 04:29:07] [DEBUG]     Added question 15 to assignment Distribution Fitting and Hypothesis Testing
[2025-04-06 04:29:07] [DEBUG]     Added question 17 to assignment Distribution Fitting and Hypothesis Testing
[2025-04-06 04:29:07] [DEBUG]     Added question 22 to assignment Distribution Fitting and Hypothesis Testing
[2025-04-06 04:29:07] [DEBUG]     Added question 23 to assignment Distribution Fitting and Hypothesis Testing
[2025-04-06 04:29:07] [DEBUG]   Created assignment 4: Distribution Fitting and Hypothesis Testing
[2025-04-06 04:29:07] [DEBUG]   Creating assignment: Demand Analysis and Market Experiments (Week 4, Type: graded)
[2025-04-06 04:29:07] [INFO]   Adding 9 questions to assignment Demand Analysis and Market Experiments
[2025-04-06 04:29:07] [DEBUG]     Added question 11 to assignment Demand Analysis and Market Experiments
[2025-04-06 04:29:07] [DEBUG]     Added question 12 to assignment Demand Analysis and Market Experiments
[2025-04-06 04:29:07] [DEBUG]     Added question 16 to assignment Demand Analysis and Market Experiments
[2025-04-06 04:29:07] [DEBUG]     Added question 18 to assignment Demand Analysis and Market Experiments
[2025-04-06 04:29:07] [DEBUG]     Added question 19 to assignment Demand Analysis and Market Experiments
[2025-04-06 04:29:07] [DEBUG]     Added question 20 to assignment Demand Analysis and Market Experiments
[2025-04-06 04:29:07] [DEBUG]     Added question 21 to assignment Demand Analysis and Market Experiments
[2025-04-06 04:29:07] [DEBUG]     Added question 24 to assignment Demand Analysis and Market Experiments
[2025-04-06 04:29:07] [DEBUG]     Added question 25 to assignment Demand Analysis and Market Experiments
[2025-04-06 04:29:07] [DEBUG]   Created assignment 5: Demand Analysis and Market Experiments
[2025-04-06 04:29:07] [DEBUG]   Creating assignment: Simple Linear Regression Analysis (Week 5, Type: practice)
[2025-04-06 04:29:07] [INFO]   Adding 3 questions to assignment Simple Linear Regression Analysis
[2025-04-06 04:29:07] [DEBUG]     Added question 26 to assignment Simple Linear Regression Analysis
[2025-04-06 04:29:07] [DEBUG]     Added question 27 to assignment Simple Linear Regression Analysis
[2025-04-06 04:29:07] [DEBUG]     Added question 28 to assignment Simple Linear Regression Analysis
[2025-04-06 04:29:07] [DEBUG]   Created assignment 6: Simple Linear Regression Analysis
[2025-04-06 04:29:07] [DEBUG]   Creating assignment: Multiple Linear Regression (Week 6, Type: graded)
[2025-04-06 04:29:07] [INFO]   Adding 3 questions to assignment Multiple Linear Regression
[2025-04-06 04:29:07] [DEBUG]     Added question 29 to assignment Multiple Linear Regression
[2025-04-06 04:29:07] [DEBUG]     Added question 30 to assignment Multiple Linear Regression
[2025-04-06 04:29:07] [DEBUG]     Added question 31 to assignment Multiple Linear Regression
[2025-04-06 04:29:07] [DEBUG]   Created assignment 7: Multiple Linear Regression
[2025-04-06 04:29:07] [DEBUG]   Creating assignment: Time Series Forecasting Basics (Week 7, Type: practice)
[2025-04-06 04:29:07] [INFO]   Adding 5 questions to assignment Time Series Forecasting Basics
[2025-04-06 04:29:07] [DEBUG]     Added question 32 to assignment Time Series Forecasting Basics
[2025-04-06 04:29:07] [DEBUG]     Added question 33 to assignment Time Series Forecasting Basics
[2025-04-06 04:29:07] [DEBUG]     Added question 34 to assignment Time Series Forecasting Basics
[2025-04-06 04:29:07] [DEBUG]     Added question 35 to assignment Time Series Forecasting Basics
[2025-04-06 04:29:07] [DEBUG]     Added question 36 to assignment Time Series Forecasting Basics
[2025-04-06 04:29:07] [DEBUG]   Created assignment 8: Time Series Forecasting Basics
[2025-04-06 04:29:07] [DEBUG]   Creating assignment: Principles of Experimental Design (Week 8, Type: practice)
[2025-04-06 04:29:07] [INFO]   Adding 5 questions to assignment Principles of Experimental Design
[2025-04-06 04:29:07] [DEBUG]     Added question 37 to assignment Principles of Experimental Design
[2025-04-06 04:29:07] [DEBUG]     Added question 38 to assignment Principles of Experimental Design
[2025-04-06 04:29:07] [DEBUG]     Added question 39 to assignment Principles of Experimental Design
[2025-04-06 04:29:07] [DEBUG]     Added question 40 to assignment Principles of Experimental Design
[2025-04-06 04:29:07] [DEBUG]     Added question 41 to assignment Principles of Experimental Design
[2025-04-06 04:29:07] [DEBUG]   Created assignment 9: Principles of Experimental Design
[2025-04-06 04:29:07] [DEBUG]   Creating assignment: Introduction to Linear Programming (Week 9, Type: practice)
[2025-04-06 04:29:07] [INFO]   Adding 3 questions to assignment Introduction to Linear Programming
[2025-04-06 04:29:07] [DEBUG]     Added question 43 to assignment Introduction to Linear Programming
[2025-04-06 04:29:07] [DEBUG]     Added question 44 to assignment Introduction to Linear Programming
[2025-04-06 04:29:07] [DEBUG]     Added question 45 to assignment Introduction to Linear Programming
[2025-04-06 04:29:07] [DEBUG]   Created assignment 10: Introduction to Linear Programming
[2025-04-06 04:29:07] [INFO] Created 10 assignments for course BA201
[2025-04-06 04:29:07] [DEBUG] Enrolled student student2 in course BA201
[2025-04-06 04:29:07] [INFO] Successfully processed course BA201 from E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course\ba_updated.json
[2025-04-06 04:29:07] [INFO] Processing dbms_updated.json...
[2025-04-06 04:29:07] [INFO] === Processing file: E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course\dbms_updated.json ===
[2025-04-06 04:29:07] [INFO] Parsing JSON file: E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course\dbms_updated.json
[2025-04-06 04:29:07] [INFO] Successfully parsed JSON with 7 top-level keys
[2025-04-06 04:29:07] [INFO] Course info found: Advanced Database Management Systems (DBMS201)
[2025-04-06 04:29:07] [INFO] Found 16 weeks
[2025-04-06 04:29:07] [INFO] Found 32 lectures
[2025-04-06 04:29:07] [INFO] Found 16 assignments
[2025-04-06 04:29:07] [INFO] Found 25 questions
[2025-04-06 04:29:07] [INFO] Checking for existing courses in the database...
[2025-04-06 04:29:07] [INFO] Found 1 existing courses
[2025-04-06 04:29:07] [DEBUG]   - BA201: Business Analytics
[2025-04-06 04:29:07] [DEBUG]   Extracting from LLM_Summary - Found acronyms: 19, synonyms: 6
[2025-04-06 04:29:07] [DEBUG]   Creating new course DBMS201 - Acronyms: 19, Synonyms: 6
[2025-04-06 04:29:07] [DEBUG]   Course model DBMS201 (before adding) - Acronyms: {"DBMS": "Database Management Systems", "ER": "Entity-Relationship", "SQL": "Structured Query Language", "DDL": "Data Definition Language", "DML": "Data Manipulation Language", "ACID": "Atomicity, Consistency, Isolation, Durability", "OLAP": "Online Analytical Processing", "OLTP": "Online Transaction Processing", "BCNF": "Boyce-Codd Normal Form", "4NF": "Fourth Normal Form", "5NF": "Fifth Normal Form", "DKNF": "Domain-Key Normal Form", "MVCC": "Multi-Version Concurrency Control", "2PL": "Two-Phase Locking", "2PC": "Two-Phase Commit", "MOLAP": "Multidimensional OLAP", "ROLAP": "Relational OLAP", "HOLAP": "Hybrid OLAP", "ETL": "Extract, Transform, Load"}, Synonyms: {"Normalization": ["Schema Refinement", "Removing Data Redundancies"], "Entity-Relationship (ER) Modeling": ["Relational Schema Design"], "Concurrency Control": ["Locking Protocols", "Serializability Approaches"], "Distributed Databases": ["Federated Databases", "Shared-Nothing Architecture"], "Data Warehousing": ["Analytical Data Storage", "OLAP Systems"], "NoSQL": ["Non-Relational Databases"]}
[2025-04-06 04:29:07] [INFO] Created course: DBMS201 - Advanced Database Management Systems
[2025-04-06 04:29:07] [INFO] Processing 16 weeks for course DBMS201
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 1
[2025-04-06 04:29:07] [DEBUG] Created week 1: Week 1: Foundations Revisited - Data, Abstraction, and Database Architectures (DB ID: 10)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 2
[2025-04-06 04:29:07] [DEBUG] Created week 2: Week 2: Advanced Relational Model, SQL Deep Dive, and Enhanced Integrity Constraints (DB ID: 11)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 3
[2025-04-06 04:29:07] [DEBUG] Created week 3: Week 3: Expert SQL: Subqueries, Views, and Data Modification Mastery (DB ID: 12)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 4
[2025-04-06 04:29:07] [DEBUG] Created week 4: Week 4: Deep Dive into Indexing and Query Processing Strategies (DB ID: 13)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 5
[2025-04-06 04:29:07] [DEBUG] Created week 5: Week 5: Advanced Normalization and Database Design Methodologies (DB ID: 14)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 6
[2025-04-06 04:29:07] [DEBUG] Created week 6: Week 6: Transaction Management: ACID Properties and Concurrency Control (DB ID: 15)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 7
[2025-04-06 04:29:07] [DEBUG] Created week 7: Week 7: Database Recovery Techniques and Failure Management (DB ID: 16)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 8
[2025-04-06 04:29:07] [DEBUG] Created week 8: Week 8: Introduction to NoSQL Databases: Concepts and Key-Value Stores (DB ID: 17)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 9
[2025-04-06 04:29:07] [DEBUG] Created week 9: Week 9: NoSQL Databases: Document Databases and Column-Family Stores (DB ID: 18)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 10
[2025-04-06 04:29:07] [DEBUG] Created week 10: Week 10: NoSQL Databases: Graph Databases and Polyglot Persistence (DB ID: 19)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 11
[2025-04-06 04:29:07] [DEBUG] Created week 11: Week 11: Distributed Databases: Architectures and Data Replication (DB ID: 20)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 12
[2025-04-06 04:29:07] [DEBUG] Created week 12: Week 12: Distributed Databases: Query Processing and Concurrency Control (DB ID: 21)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 13
[2025-04-06 04:29:07] [DEBUG] Created week 13: Week 13: Data Warehousing and OLAP: Principles and Design (DB ID: 22)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 14
[2025-04-06 04:29:07] [DEBUG] Created week 14: Week 14: Data Warehousing and OLAP: Operations and Advanced Topics (DB ID: 23)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 15
[2025-04-06 04:29:07] [DEBUG] Created week 15: Week 15: Database Security: Principles and Implementation (DB ID: 24)
[2025-04-06 04:29:07] [DEBUG] Added LLM_Summary to week 16
[2025-04-06 04:29:07] [DEBUG] Created week 16: Week 16: Database Performance Tuning and Emerging Trends (DB ID: 25)
[2025-04-06 04:29:07] [INFO] Processing 32 lectures
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Foundations Revisited: Deep Dive into Data Abstraction for week 1
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Database System Architectures: Centralized, Client-Server, and Parallel Systems for week 1
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Advanced Relational Model Concepts: Domains, Keys, and Relational Constraints for week 2
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: SQL DDL and Schema Manipulation: Views, Indexes, and Advanced Data Types for week 2
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Mastering SQL Subqueries: Correlated, Nested, and Scalar Subqueries in Depth for week 3
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Advanced SQL: Window Functions, CTEs, and Procedural SQL Extensions for week 3
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Indexing Strategies: B-trees, Hash Indexes, and Advanced Indexing Techniques for week 4
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Query Processing and Optimization: From Parsing to Execution for week 4
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Beyond 3NF: Understanding 4NF and Boyce-Codd Normal Form (BCNF) for week 5
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: 5NF and Domain-Key Normal Form (DKNF): Achieving Ultimate Normalization for week 5
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Deep Dive into ACID Properties: Atomicity and Consistency in Transactions for week 6
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: ACID Properties: Isolation and Durability in Concurrent Transactions for week 6
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Database Logging and Write-Ahead Logging (WAL) in Recovery Systems for week 7
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Checkpointing and Database Recovery Algorithms: Ensuring Data Durability for week 7
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: The Rise of NoSQL: Motivations, Characteristics, and the CAP Theorem for week 8
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Exploring Key-Value Stores: Architecture, Use Cases, and Examples for week 8
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Delving into Document Databases: Data Model, Architecture, and MongoDB for week 9
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Exploring Column-Family Stores: Data Model, Architecture, and Apache Cassandra for week 9
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Graph Databases Unveiled: Data Model, Querying with Cypher, and Neo4j for week 10
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Polyglot Persistence: Choosing the Right Database for the Job for week 10
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Foundations of Distributed Databases: Homogeneous vs. Heterogeneous Systems for week 11
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Data Replication in Distributed Databases: Consistency and Availability Trade-offs for week 11
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Distributed Query Processing: Fragmentation, Data Localization, and Join Strategies for week 12
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Distributed Concurrency Control and Transaction Management: Ensuring Consistency for week 12
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Data Warehousing Fundamentals: OLTP vs. OLAP and the Need for Data Warehouses for week 13
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Data Warehouse Architecture and Dimensional Modeling: Star, Snowflake, and Fact Constellations for week 13
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: OLAP Operations: Slicing, Dicing, Roll-up, Drill-down, and Pivoting for Data Analysis for week 14
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Types of OLAP Servers: MOLAP, ROLAP, and HOLAP Architectures for week 14
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Database Security Fundamentals: Threats, Vulnerabilities, and Security Goals for week 15
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Database Security Mechanisms: Authentication, Authorization, and Access Control Models for week 15
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:07] [DEBUG] Created lecture 1: Advanced Query Optimization and Performance Tuning Techniques for week 16
[2025-04-06 04:29:07] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:07] [DEBUG] Created lecture 2: Emerging Trends in Database Technologies: In-Memory, NewSQL, Cloud Databases, and AI Integration for week 16
[2025-04-06 04:29:07] [INFO] Processed 16 weeks and 32 lectures for course DBMS201
[2025-04-06 04:29:07] [INFO] Creating question bank...
[2025-04-06 04:29:07] [INFO] Creating 25 questions for course DBMS201
[2025-04-06 04:29:07] [DEBUG]   Created question 46: Which of the following databas...
[2025-04-06 04:29:07] [DEBUG]   Created question 47: Which type of data independenc...
[2025-04-06 04:29:07] [DEBUG]   Created question 48: Identify the key characteristi...
[2025-04-06 04:29:07] [DEBUG]   Created question 49: According to the CAP Theorem, ...
[2025-04-06 04:29:07] [DEBUG]   Created question 50: Which type of NoSQL database s...
[2025-04-06 04:29:07] [DEBUG]   Created question 51: In SQL, which DDL command is u...
[2025-04-06 04:29:07] [DEBUG]   Created question 52: Which SQL feature provides a v...
[2025-04-06 04:29:07] [DEBUG]   Created question 53: Identify the isolation levels ...
[2025-04-06 04:29:07] [DEBUG]   Created question 54: Which concurrency control tech...
[2025-04-06 04:29:07] [DEBUG]   Created question 55: Which of the ACID properties e...
[2025-04-06 04:29:07] [DEBUG]   Created question 56: What is the primary purpose of...
[2025-04-06 04:29:07] [DEBUG]   Created question 57: Which of the following is a te...
[2025-04-06 04:29:07] [DEBUG]   Created question 58: In data warehousing, which sch...
[2025-04-06 04:29:07] [DEBUG]   Created question 59: Which OLAP operation involves ...
[2025-04-06 04:29:07] [DEBUG]   Created question 60: Which of the following is a pr...
[2025-04-06 04:29:07] [DEBUG]   Created question 61: Which access control model gra...
[2025-04-06 04:29:07] [DEBUG]   Created question 62: What type of database primaril...
[2025-04-06 04:29:07] [DEBUG]   Created question 63: Which category of database sys...
[2025-04-06 04:29:07] [DEBUG]   Created question 64: In distributed databases, divi...
[2025-04-06 04:29:07] [DEBUG]   Created question 65: What is a subject-oriented, in...
[2025-04-06 04:29:07] [DEBUG]   Created question 66: Which replication technique in...
[2025-04-06 04:29:07] [DEBUG]   Created question 67: What is the primary query lang...
[2025-04-06 04:29:07] [DEBUG]   Created question 68: Which of the following is NOT ...
[2025-04-06 04:29:07] [DEBUG]   Created question 69: Explain the concept of 'eventu...
[2025-04-06 04:29:07] [DEBUG]   Created question 70: What are the key differences b...
[2025-04-06 04:29:08] [INFO] Created 50 questions for course DBMS201
[2025-04-06 04:29:08] [INFO] Creating assignments...
[2025-04-06 04:29:08] [INFO] Creating 16 assignments for course DBMS201
[2025-04-06 04:29:08] [DEBUG]   Creating assignment: Advanced Database Design and Architecture Analysis (Week 1, Type: practice)
[2025-04-06 04:29:08] [INFO]   Adding 7 questions to assignment Advanced Database Design and Architecture Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 46 to assignment Advanced Database Design and Architecture Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 47 to assignment Advanced Database Design and Architecture Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 49 to assignment Advanced Database Design and Architecture Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 52 to assignment Advanced Database Design and Architecture Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 55 to assignment Advanced Database Design and Architecture Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 58 to assignment Advanced Database Design and Architecture Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 61 to assignment Advanced Database Design and Architecture Analysis
[2025-04-06 04:29:08] [DEBUG]   Created assignment 11: Advanced Database Design and Architecture Analysis
[2025-04-06 04:29:08] [DEBUG]   Creating assignment: Advanced SQL DDL and Integrity Constraints (Week 2, Type: practice)
[2025-04-06 04:29:08] [INFO]   Adding 9 questions to assignment Advanced SQL DDL and Integrity Constraints
[2025-04-06 04:29:08] [DEBUG]     Added question 48 to assignment Advanced SQL DDL and Integrity Constraints
[2025-04-06 04:29:08] [DEBUG]     Added question 50 to assignment Advanced SQL DDL and Integrity Constraints
[2025-04-06 04:29:08] [DEBUG]     Added question 53 to assignment Advanced SQL DDL and Integrity Constraints
[2025-04-06 04:29:08] [DEBUG]     Added question 56 to assignment Advanced SQL DDL and Integrity Constraints
[2025-04-06 04:29:08] [DEBUG]     Added question 59 to assignment Advanced SQL DDL and Integrity Constraints
[2025-04-06 04:29:08] [DEBUG]     Added question 62 to assignment Advanced SQL DDL and Integrity Constraints
[2025-04-06 04:29:08] [DEBUG]     Added question 65 to assignment Advanced SQL DDL and Integrity Constraints
[2025-04-06 04:29:08] [DEBUG]     Added question 68 to assignment Advanced SQL DDL and Integrity Constraints
[2025-04-06 04:29:08] [DEBUG]     Added question 70 to assignment Advanced SQL DDL and Integrity Constraints
[2025-04-06 04:29:08] [DEBUG]   Created assignment 12: Advanced SQL DDL and Integrity Constraints
[2025-04-06 04:29:08] [DEBUG]   Creating assignment: Mastering SQL Subqueries and Data Modification (Week 3, Type: practice)
[2025-04-06 04:29:08] [INFO]   Adding 8 questions to assignment Mastering SQL Subqueries and Data Modification
[2025-04-06 04:29:08] [DEBUG]     Added question 49 to assignment Mastering SQL Subqueries and Data Modification
[2025-04-06 04:29:08] [DEBUG]     Added question 51 to assignment Mastering SQL Subqueries and Data Modification
[2025-04-06 04:29:08] [DEBUG]     Added question 54 to assignment Mastering SQL Subqueries and Data Modification
[2025-04-06 04:29:08] [DEBUG]     Added question 57 to assignment Mastering SQL Subqueries and Data Modification
[2025-04-06 04:29:08] [DEBUG]     Added question 60 to assignment Mastering SQL Subqueries and Data Modification
[2025-04-06 04:29:08] [DEBUG]     Added question 63 to assignment Mastering SQL Subqueries and Data Modification
[2025-04-06 04:29:08] [DEBUG]     Added question 66 to assignment Mastering SQL Subqueries and Data Modification
[2025-04-06 04:29:08] [DEBUG]     Added question 69 to assignment Mastering SQL Subqueries and Data Modification
[2025-04-06 04:29:08] [DEBUG]   Created assignment 13: Mastering SQL Subqueries and Data Modification
[2025-04-06 04:29:08] [DEBUG]   Creating assignment: In-depth Indexing Strategies and Query Optimization (Week 4, Type: practice)
[2025-04-06 04:29:08] [INFO]   Adding 5 questions to assignment In-depth Indexing Strategies and Query Optimization
[2025-04-06 04:29:08] [DEBUG]     Added question 55 to assignment In-depth Indexing Strategies and Query Optimization
[2025-04-06 04:29:08] [DEBUG]     Added question 58 to assignment In-depth Indexing Strategies and Query Optimization
[2025-04-06 04:29:08] [DEBUG]     Added question 61 to assignment In-depth Indexing Strategies and Query Optimization
[2025-04-06 04:29:08] [DEBUG]     Added question 64 to assignment In-depth Indexing Strategies and Query Optimization
[2025-04-06 04:29:08] [DEBUG]     Added question 67 to assignment In-depth Indexing Strategies and Query Optimization
[2025-04-06 04:29:08] [DEBUG]   Created assignment 14: In-depth Indexing Strategies and Query Optimization
[2025-04-06 04:29:08] [DEBUG]   Creating assignment: Advanced Normalization Forms and Design Principles (Week 5, Type: practice)
[2025-04-06 04:29:08] [INFO]   Adding 5 questions to assignment Advanced Normalization Forms and Design Principles
[2025-04-06 04:29:08] [DEBUG]     Added question 56 to assignment Advanced Normalization Forms and Design Principles
[2025-04-06 04:29:08] [DEBUG]     Added question 59 to assignment Advanced Normalization Forms and Design Principles
[2025-04-06 04:29:08] [DEBUG]     Added question 62 to assignment Advanced Normalization Forms and Design Principles
[2025-04-06 04:29:08] [DEBUG]     Added question 65 to assignment Advanced Normalization Forms and Design Principles
[2025-04-06 04:29:08] [DEBUG]     Added question 68 to assignment Advanced Normalization Forms and Design Principles
[2025-04-06 04:29:08] [DEBUG]   Created assignment 15: Advanced Normalization Forms and Design Principles
[2025-04-06 04:29:08] [DEBUG]   Creating assignment: Transaction Management and Concurrency Control Scenarios (Week 6, Type: practice)
[2025-04-06 04:29:08] [INFO]   Adding 5 questions to assignment Transaction Management and Concurrency Control Scenarios
[2025-04-06 04:29:08] [DEBUG]     Added question 57 to assignment Transaction Management and Concurrency Control Scenarios
[2025-04-06 04:29:08] [DEBUG]     Added question 60 to assignment Transaction Management and Concurrency Control Scenarios
[2025-04-06 04:29:08] [DEBUG]     Added question 63 to assignment Transaction Management and Concurrency Control Scenarios
[2025-04-06 04:29:08] [DEBUG]     Added question 66 to assignment Transaction Management and Concurrency Control Scenarios
[2025-04-06 04:29:08] [DEBUG]     Added question 69 to assignment Transaction Management and Concurrency Control Scenarios
[2025-04-06 04:29:08] [DEBUG]   Created assignment 16: Transaction Management and Concurrency Control Scenarios
[2025-04-06 04:29:08] [DEBUG]   Creating assignment: Database Recovery Planning and Failure Analysis (Week 7, Type: practice)
[2025-04-06 04:29:08] [INFO]   Adding 5 questions to assignment Database Recovery Planning and Failure Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 58 to assignment Database Recovery Planning and Failure Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 61 to assignment Database Recovery Planning and Failure Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 64 to assignment Database Recovery Planning and Failure Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 67 to assignment Database Recovery Planning and Failure Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 70 to assignment Database Recovery Planning and Failure Analysis
[2025-04-06 04:29:08] [DEBUG]   Created assignment 17: Database Recovery Planning and Failure Analysis
[2025-04-06 04:29:08] [DEBUG]   Creating assignment: Exploring NoSQL Databases: Key-Value Stores (Week 8, Type: graded)
[2025-04-06 04:29:08] [INFO]   Adding 5 questions to assignment Exploring NoSQL Databases: Key-Value Stores
[2025-04-06 04:29:08] [DEBUG]     Added question 54 to assignment Exploring NoSQL Databases: Key-Value Stores
[2025-04-06 04:29:08] [DEBUG]     Added question 57 to assignment Exploring NoSQL Databases: Key-Value Stores
[2025-04-06 04:29:08] [DEBUG]     Added question 60 to assignment Exploring NoSQL Databases: Key-Value Stores
[2025-04-06 04:29:08] [DEBUG]     Added question 63 to assignment Exploring NoSQL Databases: Key-Value Stores
[2025-04-06 04:29:08] [DEBUG]     Added question 66 to assignment Exploring NoSQL Databases: Key-Value Stores
[2025-04-06 04:29:08] [DEBUG]   Created assignment 18: Exploring NoSQL Databases: Key-Value Stores
[2025-04-06 04:29:08] [DEBUG]   Creating assignment: Document and Column-Family Databases in Practice (Week 9, Type: graded)
[2025-04-06 04:29:08] [INFO]   Adding 5 questions to assignment Document and Column-Family Databases in Practice
[2025-04-06 04:29:08] [DEBUG]     Added question 49 to assignment Document and Column-Family Databases in Practice
[2025-04-06 04:29:08] [DEBUG]     Added question 52 to assignment Document and Column-Family Databases in Practice
[2025-04-06 04:29:08] [DEBUG]     Added question 55 to assignment Document and Column-Family Databases in Practice
[2025-04-06 04:29:08] [DEBUG]     Added question 58 to assignment Document and Column-Family Databases in Practice
[2025-04-06 04:29:08] [DEBUG]     Added question 61 to assignment Document and Column-Family Databases in Practice
[2025-04-06 04:29:08] [DEBUG]   Created assignment 19: Document and Column-Family Databases in Practice
[2025-04-06 04:29:08] [DEBUG]   Creating assignment: Graph Databases and Polyglot Persistence Design (Week 10, Type: graded)
[2025-04-06 04:29:08] [INFO]   Adding 5 questions to assignment Graph Databases and Polyglot Persistence Design
[2025-04-06 04:29:08] [DEBUG]     Added question 50 to assignment Graph Databases and Polyglot Persistence Design
[2025-04-06 04:29:08] [DEBUG]     Added question 53 to assignment Graph Databases and Polyglot Persistence Design
[2025-04-06 04:29:08] [DEBUG]     Added question 56 to assignment Graph Databases and Polyglot Persistence Design
[2025-04-06 04:29:08] [DEBUG]     Added question 59 to assignment Graph Databases and Polyglot Persistence Design
[2025-04-06 04:29:08] [DEBUG]     Added question 62 to assignment Graph Databases and Polyglot Persistence Design
[2025-04-06 04:29:08] [DEBUG]   Created assignment 20: Graph Databases and Polyglot Persistence Design
[2025-04-06 04:29:08] [DEBUG]   Creating assignment: Distributed Database Replication Strategies (Week 11, Type: graded)
[2025-04-06 04:29:08] [INFO]   Adding 5 questions to assignment Distributed Database Replication Strategies
[2025-04-06 04:29:08] [DEBUG]     Added question 54 to assignment Distributed Database Replication Strategies
[2025-04-06 04:29:08] [DEBUG]     Added question 57 to assignment Distributed Database Replication Strategies
[2025-04-06 04:29:08] [DEBUG]     Added question 60 to assignment Distributed Database Replication Strategies
[2025-04-06 04:29:08] [DEBUG]     Added question 63 to assignment Distributed Database Replication Strategies
[2025-04-06 04:29:08] [DEBUG]     Added question 70 to assignment Distributed Database Replication Strategies
[2025-04-06 04:29:08] [DEBUG]   Created assignment 21: Distributed Database Replication Strategies
[2025-04-06 04:29:08] [DEBUG]   Creating assignment: Distributed Query Processing and Concurrency Control Challenges (Week 12, Type: graded)
[2025-04-06 04:29:08] [INFO]   Adding 5 questions to assignment Distributed Query Processing and Concurrency Control Challenges
[2025-04-06 04:29:08] [DEBUG]     Added question 49 to assignment Distributed Query Processing and Concurrency Control Challenges
[2025-04-06 04:29:08] [DEBUG]     Added question 52 to assignment Distributed Query Processing and Concurrency Control Challenges
[2025-04-06 04:29:08] [DEBUG]     Added question 55 to assignment Distributed Query Processing and Concurrency Control Challenges
[2025-04-06 04:29:08] [DEBUG]     Added question 58 to assignment Distributed Query Processing and Concurrency Control Challenges
[2025-04-06 04:29:08] [DEBUG]     Added question 59 to assignment Distributed Query Processing and Concurrency Control Challenges
[2025-04-06 04:29:08] [DEBUG]   Created assignment 22: Distributed Query Processing and Concurrency Control Challenges
[2025-04-06 04:29:08] [DEBUG]   Creating assignment: Data Warehouse Design and Dimensional Modeling (Week 13, Type: graded)
[2025-04-06 04:29:08] [INFO]   Adding 5 questions to assignment Data Warehouse Design and Dimensional Modeling
[2025-04-06 04:29:08] [DEBUG]     Added question 49 to assignment Data Warehouse Design and Dimensional Modeling
[2025-04-06 04:29:08] [DEBUG]     Added question 52 to assignment Data Warehouse Design and Dimensional Modeling
[2025-04-06 04:29:08] [DEBUG]     Added question 55 to assignment Data Warehouse Design and Dimensional Modeling
[2025-04-06 04:29:08] [DEBUG]     Added question 58 to assignment Data Warehouse Design and Dimensional Modeling
[2025-04-06 04:29:08] [DEBUG]     Added question 59 to assignment Data Warehouse Design and Dimensional Modeling
[2025-04-06 04:29:08] [DEBUG]   Created assignment 23: Data Warehouse Design and Dimensional Modeling
[2025-04-06 04:29:08] [DEBUG]   Creating assignment: OLAP Operations and Data Analysis (Week 14, Type: graded)
[2025-04-06 04:29:08] [INFO]   Adding 5 questions to assignment OLAP Operations and Data Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 49 to assignment OLAP Operations and Data Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 52 to assignment OLAP Operations and Data Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 55 to assignment OLAP Operations and Data Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 58 to assignment OLAP Operations and Data Analysis
[2025-04-06 04:29:08] [DEBUG]     Added question 59 to assignment OLAP Operations and Data Analysis
[2025-04-06 04:29:08] [DEBUG]   Created assignment 24: OLAP Operations and Data Analysis
[2025-04-06 04:29:08] [DEBUG]   Creating assignment: Implementing Database Security Policies (Week 15, Type: graded)
[2025-04-06 04:29:08] [INFO]   Adding 5 questions to assignment Implementing Database Security Policies
[2025-04-06 04:29:08] [DEBUG]     Added question 49 to assignment Implementing Database Security Policies
[2025-04-06 04:29:08] [DEBUG]     Added question 52 to assignment Implementing Database Security Policies
[2025-04-06 04:29:08] [DEBUG]     Added question 55 to assignment Implementing Database Security Policies
[2025-04-06 04:29:08] [DEBUG]     Added question 58 to assignment Implementing Database Security Policies
[2025-04-06 04:29:08] [DEBUG]     Added question 59 to assignment Implementing Database Security Policies
[2025-04-06 04:29:08] [DEBUG]   Created assignment 25: Implementing Database Security Policies
[2025-04-06 04:29:08] [DEBUG]   Creating assignment: Database Performance Tuning and Emerging Technologies Report (Week 16, Type: graded)
[2025-04-06 04:29:08] [INFO]   Adding 5 questions to assignment Database Performance Tuning and Emerging Technologies Report
[2025-04-06 04:29:08] [DEBUG]     Added question 49 to assignment Database Performance Tuning and Emerging Technologies Report
[2025-04-06 04:29:08] [DEBUG]     Added question 52 to assignment Database Performance Tuning and Emerging Technologies Report
[2025-04-06 04:29:08] [DEBUG]     Added question 55 to assignment Database Performance Tuning and Emerging Technologies Report
[2025-04-06 04:29:08] [DEBUG]     Added question 58 to assignment Database Performance Tuning and Emerging Technologies Report
[2025-04-06 04:29:08] [DEBUG]     Added question 59 to assignment Database Performance Tuning and Emerging Technologies Report
[2025-04-06 04:29:08] [DEBUG]   Created assignment 26: Database Performance Tuning and Emerging Technologies Report
[2025-04-06 04:29:08] [INFO] Created 16 assignments for course DBMS201
[2025-04-06 04:29:08] [DEBUG] Enrolled student student2 in course DBMS201
[2025-04-06 04:29:08] [INFO] Successfully processed course DBMS201 from E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course\dbms_updated.json
[2025-04-06 04:29:08] [INFO] Processing java course raw.json...
[2025-04-06 04:29:08] [INFO] === Processing file: E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course\java course raw.json ===
[2025-04-06 04:29:08] [INFO] Parsing JSON file: E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course\java course raw.json
[2025-04-06 04:29:08] [INFO] Successfully parsed JSON with 7 top-level keys
[2025-04-06 04:29:08] [INFO] Course info found: Introduction to Java Programming (JAVA101)
[2025-04-06 04:29:08] [INFO] Found 9 weeks
[2025-04-06 04:29:08] [INFO] Found 16 lectures
[2025-04-06 04:29:08] [INFO] Found 8 assignments
[2025-04-06 04:29:08] [INFO] Found 48 questions
[2025-04-06 04:29:08] [INFO] Checking for existing courses in the database...
[2025-04-06 04:29:08] [INFO] Found 2 existing courses
[2025-04-06 04:29:08] [DEBUG]   - BA201: Business Analytics
[2025-04-06 04:29:08] [DEBUG]   - DBMS201: Advanced Database Management Systems
[2025-04-06 04:29:08] [DEBUG]   Extracting from LLM_Summary - Found acronyms: 0, synonyms: 0
[2025-04-06 04:29:08] [DEBUG]   Creating new course JAVA101 - Acronyms: 0, Synonyms: 0
[2025-04-06 04:29:08] [DEBUG]   Course model JAVA101 (before adding) - Acronyms: {}, Synonyms: {}
[2025-04-06 04:29:08] [INFO] Created course: JAVA101 - Introduction to Java Programming
[2025-04-06 04:29:08] [INFO] Processing 9 weeks for course JAVA101
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 1
[2025-04-06 04:29:08] [DEBUG] Created week 1: Week 1: Introduction to Java and Setup (DB ID: 26)
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 2
[2025-04-06 04:29:08] [DEBUG] Created week 2: Week 2: Data Types, Variables, and Operators (DB ID: 27)
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 3
[2025-04-06 04:29:08] [DEBUG] Created week 3: Week 3: Control Flow Statements (DB ID: 28)
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 4
[2025-04-06 04:29:08] [DEBUG] Created week 4: Week 4: Introduction to Classes and Objects (DB ID: 29)
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 5
[2025-04-06 04:29:08] [DEBUG] Created week 5: Week 5: Constructors and Access Modifiers (DB ID: 30)
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 6
[2025-04-06 04:29:08] [DEBUG] Created week 6: Week 6: Inheritance (DB ID: 31)
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 7
[2025-04-06 04:29:08] [DEBUG] Created week 7: Week 7: Polymorphism and Abstract Classes (DB ID: 32)
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 8
[2025-04-06 04:29:08] [DEBUG] Created week 8: Week 8: Exception Handling (DB ID: 33)
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 9
[2025-04-06 04:29:08] [DEBUG] Created week 9: Week 9: Introduction to Collections (DB ID: 34)
[2025-04-06 04:29:08] [INFO] Processing 16 lectures
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:08] [DEBUG] Created lecture 1: Introduction to Java for week 1
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:08] [DEBUG] Created lecture 2: Setting up the Java Development Environment for week 1
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:08] [DEBUG] Created lecture 1: Primitive Data Types and Variables in Java for week 2
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:08] [DEBUG] Created lecture 2: Operators in Java for week 2
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:08] [DEBUG] Created lecture 1: If-Else and Switch Statements in Java for week 3
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:08] [DEBUG] Created lecture 2: Loops in Java: For, While, and Do-While for week 3
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:08] [DEBUG] Created lecture 1: Introduction to Classes in Java for week 4
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:08] [DEBUG] Created lecture 2: Creating and Using Objects in Java for week 4
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:08] [DEBUG] Created lecture 1: Constructors in Java for week 5
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:08] [DEBUG] Created lecture 2: Access Modifiers in Java for week 5
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:08] [DEBUG] Created lecture 1: Inheritance in Java for week 6
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:08] [DEBUG] Created lecture 2: Polymorphism and Abstract Classes in Java for week 6
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:08] [DEBUG] Created lecture 1: Exception Handling in Java for week 7
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:08] [DEBUG] Created lecture 2: Working with ArrayList in Java for week 7
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:08] [DEBUG] Created lecture 1: Working with LinkedList in Java for week 8
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:08] [DEBUG] Created lecture 2: Working with HashSet in Java for week 8
[2025-04-06 04:29:08] [INFO] Processed 9 weeks and 16 lectures for course JAVA101
[2025-04-06 04:29:08] [INFO] Creating question bank...
[2025-04-06 04:29:08] [INFO] Creating 48 questions for course JAVA101
[2025-04-06 04:29:08] [INFO]   Question 9 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 10 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 11 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 12 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 13 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 14 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 15 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 16 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 17 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 18 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 19 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 20 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 21 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 22 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 23 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 24 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 25 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 26 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 27 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 28 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 29 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 30 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 31 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 32 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 33 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 34 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 35 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 36 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 37 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 38 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 39 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 40 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 41 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 42 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 43 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 44 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 45 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 46 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 47 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 48 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 49 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 50 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 51 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 52 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 53 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 54 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 55 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 56 already exists, skipping
[2025-04-06 04:29:08] [INFO] Created 48 questions for course JAVA101
[2025-04-06 04:29:08] [INFO] Creating assignments...
[2025-04-06 04:29:08] [INFO] Creating 8 assignments for course JAVA101
[2025-04-06 04:29:08] [INFO]   Assignment 3 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Assignment 4 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Assignment 5 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Assignment 6 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Assignment 7 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Assignment 8 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Assignment 9 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Assignment 10 already exists, skipping
[2025-04-06 04:29:08] [INFO] Created 8 assignments for course JAVA101
[2025-04-06 04:29:08] [DEBUG] Enrolled student student2 in course JAVA101
[2025-04-06 04:29:08] [INFO] Successfully processed course JAVA101 from E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course\java course raw.json
[2025-04-06 04:29:08] [INFO] Processing mad2_updated.json...
[2025-04-06 04:29:08] [INFO] === Processing file: E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course\mad2_updated.json ===
[2025-04-06 04:29:08] [INFO] Parsing JSON file: E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course\mad2_updated.json
[2025-04-06 04:29:08] [INFO] Successfully parsed JSON with 7 top-level keys
[2025-04-06 04:29:08] [INFO] Course info found: Modern Application Development - II (MAD201)
[2025-04-06 04:29:08] [INFO] Found 8 weeks
[2025-04-06 04:29:08] [INFO] Found 24 lectures
[2025-04-06 04:29:08] [INFO] Found 10 assignments
[2025-04-06 04:29:08] [INFO] Found 23 questions
[2025-04-06 04:29:08] [INFO] Checking for existing courses in the database...
[2025-04-06 04:29:08] [INFO] Found 3 existing courses
[2025-04-06 04:29:08] [DEBUG]   - BA201: Business Analytics
[2025-04-06 04:29:08] [DEBUG]   - DBMS201: Advanced Database Management Systems
[2025-04-06 04:29:08] [DEBUG]   - JAVA101: Introduction to Java Programming
[2025-04-06 04:29:08] [DEBUG]   Extracting from LLM_Summary - Found acronyms: 0, synonyms: 0
[2025-04-06 04:29:08] [DEBUG]   Creating new course MAD201 - Acronyms: 0, Synonyms: 0
[2025-04-06 04:29:08] [DEBUG]   Course model MAD201 (before adding) - Acronyms: {}, Synonyms: {}
[2025-04-06 04:29:08] [INFO] Created course: MAD201 - Modern Application Development - II
[2025-04-06 04:29:08] [INFO] Processing 8 weeks for course MAD201
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 1
[2025-04-06 04:29:08] [DEBUG] Created week 1: Week 1: Advanced JavaScript Fundamentals and ES6+ (DB ID: 35)
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 2
[2025-04-06 04:29:08] [DEBUG] Created week 2: Week 2: DOM Manipulation, Events, and Asynchronous JavaScript (DB ID: 36)
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 3
[2025-04-06 04:29:08] [DEBUG] Created week 3: Week 3: Introduction to HTML5 and Advanced CSS3 (DB ID: 37)
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 4
[2025-04-06 04:29:08] [DEBUG] Created week 4: Week 4: Introduction to Vue.js: Components and Reactivity (DB ID: 38)
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 5
[2025-04-06 04:29:08] [DEBUG] Created week 5: Week 5: Advanced Vue.js: Composition API and State Management (DB ID: 39)
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 6
[2025-04-06 04:29:08] [DEBUG] Created week 6: Week 6: Introduction to React: Components and JSX (DB ID: 40)
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 7
[2025-04-06 04:29:08] [DEBUG] Created week 7: Week 7: Advanced React: Hooks and State Management (DB ID: 41)
[2025-04-06 04:29:08] [DEBUG] Added LLM_Summary to week 8
[2025-04-06 04:29:08] [DEBUG] Created week 8: Week 8: Frontend Architecture, Best Practices, and Testing (DB ID: 42)
[2025-04-06 04:29:08] [INFO] Processing 24 lectures
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:08] [DEBUG] Created lecture 1: Advanced JavaScript Syntax and ES6+ Features for week 1
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:08] [DEBUG] Created lecture 2: Scope, Closures, and Higher-Order Functions in JavaScript for week 1
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 3
[2025-04-06 04:29:08] [DEBUG] Created lecture 3: Asynchronous JavaScript: Promises and Async/Await for week 1
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:08] [DEBUG] Created lecture 1: Deep Dive into DOM Manipulation and Traversal for week 2
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:08] [DEBUG] Created lecture 2: JavaScript Events: Bubbling, Capturing, and Delegation for week 2
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 3
[2025-04-06 04:29:08] [DEBUG] Created lecture 3: Making HTTP Requests with the Fetch API for week 2
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:08] [DEBUG] Created lecture 1: Semantic HTML5 and Accessibility (A11y) for week 3
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:08] [DEBUG] Created lecture 2: Advanced CSS3 Selectors and the Box Model for week 3
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 3
[2025-04-06 04:29:08] [DEBUG] Created lecture 3: Responsive Design with Flexbox and Grid for week 3
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:08] [DEBUG] Created lecture 1: Vue.js Fundamentals: Instance and Component Basics for week 4
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:08] [DEBUG] Created lecture 2: Vue.js Reactivity System and Computed Properties/Watchers for week 4
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 3
[2025-04-06 04:29:08] [DEBUG] Created lecture 3: Component Communication in Vue.js: Props and Events for week 4
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:08] [DEBUG] Created lecture 1: Vue.js Composition API: Setup and Reactive Primitives for week 5
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:08] [DEBUG] Created lecture 2: Composition API: Computed Properties and Watchers for week 5
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 3
[2025-04-06 04:29:08] [DEBUG] Created lecture 3: Vuex State Management: Core Concepts and Store Setup for week 5
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:08] [DEBUG] Created lecture 1: Introduction to React Components and JSX for week 6
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:08] [DEBUG] Created lecture 2: Props and Basic Event Handling in React for week 6
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 3
[2025-04-06 04:29:08] [DEBUG] Created lecture 3: State in React: useState Hook and Class Component State for week 6
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:08] [DEBUG] Created lecture 1: React Hooks: useEffect for Side Effects for week 7
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:08] [DEBUG] Created lecture 2: Context API in React: Global State Management for week 7
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 3
[2025-04-06 04:29:08] [DEBUG] Created lecture 3: Introduction to Redux: Actions, Reducers, and Store for week 7
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:08] [DEBUG] Created lecture 1: Frontend Architectural Patterns: MVC, MVVM, Flux/Redux for week 8
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:08] [DEBUG] Created lecture 2: Frontend Performance Optimization Techniques for week 8
[2025-04-06 04:29:08] [DEBUG] Added keywords to lecture 3
[2025-04-06 04:29:08] [DEBUG] Created lecture 3: Introduction to Frontend Testing: Unit, Integration, and E2E for week 8
[2025-04-06 04:29:08] [INFO] Processed 8 weeks and 24 lectures for course MAD201
[2025-04-06 04:29:08] [INFO] Creating question bank...
[2025-04-06 04:29:08] [INFO] Creating 23 questions for course MAD201
[2025-04-06 04:29:08] [INFO]   Question 5 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 6 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 7 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 8 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 9 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 10 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 11 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 12 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 13 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 14 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 15 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 16 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 17 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 18 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 19 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 20 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 21 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 22 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 23 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 24 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 25 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 26 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Question 27 already exists, skipping
[2025-04-06 04:29:08] [INFO] Created 23 questions for course MAD201
[2025-04-06 04:29:08] [INFO] Creating assignments...
[2025-04-06 04:29:08] [INFO] Creating 10 assignments for course MAD201
[2025-04-06 04:29:08] [INFO]   Assignment 1 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Assignment 2 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Assignment 3 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Assignment 4 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Assignment 5 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Assignment 6 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Assignment 7 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Assignment 8 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Assignment 9 already exists, skipping
[2025-04-06 04:29:08] [INFO]   Assignment 10 already exists, skipping
[2025-04-06 04:29:08] [INFO] Created 10 assignments for course MAD201
[2025-04-06 04:29:09] [DEBUG] Enrolled student student2 in course MAD201
[2025-04-06 04:29:09] [INFO] Successfully processed course MAD201 from E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course\mad2_updated.json
[2025-04-06 04:29:09] [INFO] Processing se_updated.json...
[2025-04-06 04:29:09] [INFO] === Processing file: E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course\se_updated.json ===
[2025-04-06 04:29:09] [INFO] Parsing JSON file: E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course\se_updated.json
[2025-04-06 04:29:09] [INFO] Successfully parsed JSON with 7 top-level keys
[2025-04-06 04:29:09] [INFO] Course info found: Software Engineering (SE101)
[2025-04-06 04:29:09] [INFO] Found 8 weeks
[2025-04-06 04:29:09] [INFO] Found 18 lectures
[2025-04-06 04:29:09] [INFO] Found 8 assignments
[2025-04-06 04:29:09] [INFO] Found 33 questions
[2025-04-06 04:29:09] [INFO] Checking for existing courses in the database...
[2025-04-06 04:29:09] [INFO] Found 4 existing courses
[2025-04-06 04:29:09] [DEBUG]   - BA201: Business Analytics
[2025-04-06 04:29:09] [DEBUG]   - DBMS201: Advanced Database Management Systems
[2025-04-06 04:29:09] [DEBUG]   - JAVA101: Introduction to Java Programming
[2025-04-06 04:29:09] [DEBUG]   - MAD201: Modern Application Development - II
[2025-04-06 04:29:09] [DEBUG]   Extracting from LLM_Summary - Found acronyms: 0, synonyms: 0
[2025-04-06 04:29:09] [DEBUG]   Creating new course SE101 - Acronyms: 0, Synonyms: 0
[2025-04-06 04:29:09] [DEBUG]   Course model SE101 (before adding) - Acronyms: {}, Synonyms: {}
[2025-04-06 04:29:09] [INFO] Created course: SE101 - Software Engineering
[2025-04-06 04:29:09] [INFO] Processing 8 weeks for course SE101
[2025-04-06 04:29:09] [DEBUG] Added LLM_Summary to week 1
[2025-04-06 04:29:09] [DEBUG] Created week 1: **Week 1: Deconstructing the Software Development Process** (DB ID: 43)
[2025-04-06 04:29:09] [DEBUG] Added LLM_Summary to week 2
[2025-04-06 04:29:09] [DEBUG] Created week 2: **Week 2: Software Requirements Engineering** (DB ID: 44)
[2025-04-06 04:29:09] [DEBUG] Added LLM_Summary to week 3
[2025-04-06 04:29:09] [DEBUG] Created week 3: **Week 3: Software Architecture and Design** (DB ID: 45)
[2025-04-06 04:29:09] [DEBUG] Added LLM_Summary to week 4
[2025-04-06 04:29:09] [DEBUG] Created week 4: **Week 4: Software Testing and Quality Assurance** (DB ID: 46)
[2025-04-06 04:29:09] [DEBUG] Added LLM_Summary to week 5
[2025-04-06 04:29:09] [DEBUG] Created week 5: **Week 5: Software Deployment and DevOps** (DB ID: 47)
[2025-04-06 04:29:09] [DEBUG] Added LLM_Summary to week 6
[2025-04-06 04:29:09] [DEBUG] Created week 6: **Week 6: Software Maintenance and Evolution** (DB ID: 48)
[2025-04-06 04:29:09] [DEBUG] Added LLM_Summary to week 7
[2025-04-06 04:29:09] [DEBUG] Created week 7: **Week 7: Agile Project Management - Advanced Topics** (DB ID: 49)
[2025-04-06 04:29:09] [DEBUG] Added LLM_Summary to week 8
[2025-04-06 04:29:09] [DEBUG] Created week 8: **Week 8: Software Engineering Best Practices and Ethics** (DB ID: 50)
[2025-04-06 04:29:09] [INFO] Processing 18 lectures
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:09] [DEBUG] Created lecture 1: **Lecture 1: The Nature of Software and Software Engineering** for week 1
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:09] [DEBUG] Created lecture 2: **Lecture 2: Software Development Lifecycle Models - A Detailed Comparison** for week 1
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 3
[2025-04-06 04:29:09] [DEBUG] Created lecture 3: **Lecture 3: Introduction to Agile Methodologies: Scrum and Kanban** for week 1
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:09] [DEBUG] Created lecture 1: **Lecture 4: Requirement Gathering and Analysis - Advanced Techniques** for week 2
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:09] [DEBUG] Created lecture 2: **Lecture 5: Documenting Requirements: Use Cases and User Stories** for week 2
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 3
[2025-04-06 04:29:09] [DEBUG] Created lecture 3: **Lecture 6: Functional vs. Non-Functional Requirements in Detail** for week 2
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:09] [DEBUG] Created lecture 1: **Lecture 7: Software Architecture: Styles and Patterns** for week 3
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:09] [DEBUG] Created lecture 2: **Lecture 8: Software Design Principles: SOLID and Design Patterns** for week 3
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:09] [DEBUG] Created lecture 1: **Lecture 9: Fundamentals of Software Testing: Levels and Types** for week 4
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:09] [DEBUG] Created lecture 2: **Lecture 10: Software Testing Techniques: Black-Box and White-Box** for week 4
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:09] [DEBUG] Created lecture 1: **Lecture 11: Software Deployment Strategies and Tools** for week 5
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:09] [DEBUG] Created lecture 2: **Lecture 12: Introduction to DevOps: Principles and Practices** for week 5
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:09] [DEBUG] Created lecture 1: **Lecture 13: Types of Software Maintenance and Maintenance Process** for week 6
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:09] [DEBUG] Created lecture 2: **Lecture 14: Software Refactoring and Technical Debt Management** for week 6
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:09] [DEBUG] Created lecture 1: **Lecture 15: Scaling Agile: SAFe and LeSS Frameworks** for week 7
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:09] [DEBUG] Created lecture 2: **Lecture 16: Kanban and Hybrid Agile Approaches** for week 7
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 1
[2025-04-06 04:29:09] [DEBUG] Created lecture 1: **Lecture 17: Software Engineering Ethics and Professional Responsibility** for week 8
[2025-04-06 04:29:09] [DEBUG] Added keywords to lecture 2
[2025-04-06 04:29:09] [DEBUG] Created lecture 2: **Lecture 18: Future Trends in Software Engineering** for week 8
[2025-04-06 04:29:09] [INFO] Processed 8 weeks and 18 lectures for course SE101
[2025-04-06 04:29:09] [INFO] Creating question bank...
[2025-04-06 04:29:09] [INFO] Creating 33 questions for course SE101
[2025-04-06 04:29:09] [DEBUG]   Created question 71: Which of the following is NOT ...
[2025-04-06 04:29:09] [DEBUG]   Created question 72: Which Agile practices emphasiz...
[2025-04-06 04:29:09] [DEBUG]   Created question 73: Calculate the velocity of a te...
[2025-04-06 04:29:09] [DEBUG]   Created question 74: Which requirement gathering te...
[2025-04-06 04:29:09] [DEBUG]   Created question 75: What are characteristics of go...
[2025-04-06 04:29:09] [DEBUG]   Created question 76: How many actors would a typica...
[2025-04-06 04:29:09] [DEBUG]   Created question 77: Which of the following is an e...
[2025-04-06 04:29:09] [DEBUG]   Created question 78: Which SDLC model would be most...
[2025-04-06 04:29:09] [DEBUG]   Created question 79: What percentage of Agile teams...
[2025-04-06 04:29:09] [DEBUG]   Created question 80: Which elements should be inclu...
[2025-04-06 04:29:09] [DEBUG]   Created question 81: Which architectural pattern se...
[2025-04-06 04:29:09] [DEBUG]   Created question 82: Which design pattern ensures o...
[2025-04-06 04:29:09] [DEBUG]   Created question 83: How many relationships are sho...
[2025-04-06 04:29:09] [DEBUG]   Created question 84: Which SOLID principle states t...
[2025-04-06 04:29:09] [DEBUG]   Created question 85: Which testing levels verify in...
[2025-04-06 04:29:09] [DEBUG]   Created question 86: What is the minimum number of ...
[2025-04-06 04:29:09] [DEBUG]   Created question 87: Which quality attribute measur...
[2025-04-06 04:29:09] [DEBUG]   Created question 88: Which UML diagram best shows o...
[2025-04-06 04:29:09] [DEBUG]   Created question 89: Which patterns are creational ...
[2025-04-06 04:29:09] [DEBUG]   Created question 90: How many test cases are needed...
[2025-04-06 04:29:09] [DEBUG]   Created question 91: Which architectural style is m...
[2025-04-06 04:29:09] [DEBUG]   Created question 92: Which principles contribute to...
[2025-04-06 04:29:09] [DEBUG]   Created question 93: What percentage of defects are...
[2025-04-06 04:29:09] [DEBUG]   Created question 94: Which testing technique is mos...
[2025-04-06 04:29:09] [DEBUG]   Created question 95: Which quality attributes are m...
[2025-04-06 04:29:09] [DEBUG]   Created question 96: What is Infrastructure as Code...
[2025-04-06 04:29:09] [DEBUG]   Created question 97: What are the benefits of a CI/...
[2025-04-06 04:29:09] [DEBUG]   Created question 98: What is the primary goal of co...
[2025-04-06 04:29:09] [DEBUG]   Created question 99: Which refactoring technique in...
[2025-04-06 04:29:09] [DEBUG]   Created question 100: What is an Agile Release Train...
[2025-04-06 04:29:09] [DEBUG]   Created question 101: What is the purpose of limitin...
[2025-04-06 04:29:09] [DEBUG]   Created question 102: According to the IEEE Code of ...
[2025-04-06 04:29:09] [DEBUG]   Created question 103: Which emerging trend in softwa...
[2025-04-06 04:29:09] [INFO] Created 66 questions for course SE101
[2025-04-06 04:29:09] [INFO] Creating assignments...
[2025-04-06 04:29:09] [INFO] Creating 8 assignments for course SE101
[2025-04-06 04:29:09] [DEBUG]   Creating assignment: **SDLC and Agile Fundamentals** (Week 1, Type: practice)
[2025-04-06 04:29:09] [INFO]   Adding 7 questions to assignment **SDLC and Agile Fundamentals**
[2025-04-06 04:29:09] [DEBUG]     Added question 71 to assignment **SDLC and Agile Fundamentals**
[2025-04-06 04:29:09] [DEBUG]     Added question 72 to assignment **SDLC and Agile Fundamentals**
[2025-04-06 04:29:09] [DEBUG]     Added question 73 to assignment **SDLC and Agile Fundamentals**
[2025-04-06 04:29:09] [DEBUG]     Added question 78 to assignment **SDLC and Agile Fundamentals**
[2025-04-06 04:29:09] [DEBUG]     Added question 79 to assignment **SDLC and Agile Fundamentals**
[2025-04-06 04:29:09] [DEBUG]     Added question 101 to assignment **SDLC and Agile Fundamentals**
[2025-04-06 04:29:09] [DEBUG]     Added question 95 to assignment **SDLC and Agile Fundamentals**
[2025-04-06 04:29:09] [DEBUG]   Created assignment 27: **SDLC and Agile Fundamentals**
[2025-04-06 04:29:09] [DEBUG]   Creating assignment: **Requirements Engineering Essentials** (Week 2, Type: practice)
[2025-04-06 04:29:09] [INFO]   Adding 7 questions to assignment **Requirements Engineering Essentials**
[2025-04-06 04:29:09] [DEBUG]     Added question 74 to assignment **Requirements Engineering Essentials**
[2025-04-06 04:29:09] [DEBUG]     Added question 75 to assignment **Requirements Engineering Essentials**
[2025-04-06 04:29:09] [DEBUG]     Added question 76 to assignment **Requirements Engineering Essentials**
[2025-04-06 04:29:09] [DEBUG]     Added question 77 to assignment **Requirements Engineering Essentials**
[2025-04-06 04:29:09] [DEBUG]     Added question 80 to assignment **Requirements Engineering Essentials**
[2025-04-06 04:29:09] [DEBUG]     Added question 96 to assignment **Requirements Engineering Essentials**
[2025-04-06 04:29:09] [DEBUG]     Added question 97 to assignment **Requirements Engineering Essentials**
[2025-04-06 04:29:09] [DEBUG]   Created assignment 28: **Requirements Engineering Essentials**
[2025-04-06 04:29:09] [DEBUG]   Creating assignment: **Software Architecture and Design Principles** (Week 3, Type: graded)
[2025-04-06 04:29:09] [INFO]   Adding 7 questions to assignment **Software Architecture and Design Principles**
[2025-04-06 04:29:09] [DEBUG]     Added question 81 to assignment **Software Architecture and Design Principles**
[2025-04-06 04:29:09] [DEBUG]     Added question 82 to assignment **Software Architecture and Design Principles**
[2025-04-06 04:29:09] [DEBUG]     Added question 83 to assignment **Software Architecture and Design Principles**
[2025-04-06 04:29:09] [DEBUG]     Added question 84 to assignment **Software Architecture and Design Principles**
[2025-04-06 04:29:09] [DEBUG]     Added question 88 to assignment **Software Architecture and Design Principles**
[2025-04-06 04:29:09] [DEBUG]     Added question 89 to assignment **Software Architecture and Design Principles**
[2025-04-06 04:29:09] [DEBUG]     Added question 91 to assignment **Software Architecture and Design Principles**
[2025-04-06 04:29:09] [DEBUG]   Created assignment 29: **Software Architecture and Design Principles**
[2025-04-06 04:29:09] [DEBUG]   Creating assignment: **Software Testing and Quality Assurance Techniques** (Week 4, Type: graded)
[2025-04-06 04:29:09] [INFO]   Adding 7 questions to assignment **Software Testing and Quality Assurance Techniques**
[2025-04-06 04:29:09] [DEBUG]     Added question 85 to assignment **Software Testing and Quality Assurance Techniques**
[2025-04-06 04:29:09] [DEBUG]     Added question 86 to assignment **Software Testing and Quality Assurance Techniques**
[2025-04-06 04:29:09] [DEBUG]     Added question 87 to assignment **Software Testing and Quality Assurance Techniques**
[2025-04-06 04:29:09] [DEBUG]     Added question 90 to assignment **Software Testing and Quality Assurance Techniques**
[2025-04-06 04:29:09] [DEBUG]     Added question 93 to assignment **Software Testing and Quality Assurance Techniques**
[2025-04-06 04:29:09] [DEBUG]     Added question 94 to assignment **Software Testing and Quality Assurance Techniques**
[2025-04-06 04:29:09] [DEBUG]     Added question 95 to assignment **Software Testing and Quality Assurance Techniques**
[2025-04-06 04:29:09] [DEBUG]   Created assignment 30: **Software Testing and Quality Assurance Techniques**
[2025-04-06 04:29:09] [DEBUG]   Creating assignment: **Deployment Strategies and DevOps Fundamentals** (Week 5, Type: practice)
[2025-04-06 04:29:09] [INFO]   Adding 5 questions to assignment **Deployment Strategies and DevOps Fundamentals**
[2025-04-06 04:29:09] [DEBUG]     Added question 96 to assignment **Deployment Strategies and DevOps Fundamentals**
[2025-04-06 04:29:09] [DEBUG]     Added question 87 to assignment **Deployment Strategies and DevOps Fundamentals**
[2025-04-06 04:29:09] [DEBUG]     Added question 98 to assignment **Deployment Strategies and DevOps Fundamentals**
[2025-04-06 04:29:09] [DEBUG]     Added question 99 to assignment **Deployment Strategies and DevOps Fundamentals**
[2025-04-06 04:29:09] [DEBUG]     Added question 90 to assignment **Deployment Strategies and DevOps Fundamentals**
[2025-04-06 04:29:09] [DEBUG]   Created assignment 31: **Deployment Strategies and DevOps Fundamentals**
[2025-04-06 04:29:09] [DEBUG]   Creating assignment: **Software Maintenance and Technical Debt** (Week 6, Type: practice)
[2025-04-06 04:29:09] [INFO]   Adding 5 questions to assignment **Software Maintenance and Technical Debt**
[2025-04-06 04:29:09] [DEBUG]     Added question 98 to assignment **Software Maintenance and Technical Debt**
[2025-04-06 04:29:09] [DEBUG]     Added question 99 to assignment **Software Maintenance and Technical Debt**
[2025-04-06 04:29:09] [DEBUG]     Added question 91 to assignment **Software Maintenance and Technical Debt**
[2025-04-06 04:29:09] [DEBUG]     Added question 92 to assignment **Software Maintenance and Technical Debt**
[2025-04-06 04:29:09] [DEBUG]     Added question 83 to assignment **Software Maintenance and Technical Debt**
[2025-04-06 04:29:09] [DEBUG]   Created assignment 32: **Software Maintenance and Technical Debt**
[2025-04-06 04:29:09] [DEBUG]   Creating assignment: **Advanced Agile Project Management** (Week 7, Type: graded)
[2025-04-06 04:29:09] [INFO]   Adding 5 questions to assignment **Advanced Agile Project Management**
[2025-04-06 04:29:09] [DEBUG]     Added question 100 to assignment **Advanced Agile Project Management**
[2025-04-06 04:29:09] [DEBUG]     Added question 101 to assignment **Advanced Agile Project Management**
[2025-04-06 04:29:09] [DEBUG]     Added question 94 to assignment **Advanced Agile Project Management**
[2025-04-06 04:29:09] [DEBUG]     Added question 85 to assignment **Advanced Agile Project Management**
[2025-04-06 04:29:09] [DEBUG]     Added question 86 to assignment **Advanced Agile Project Management**
[2025-04-06 04:29:09] [DEBUG]   Created assignment 33: **Advanced Agile Project Management**
[2025-04-06 04:29:09] [DEBUG]   Creating assignment: **Ethics and Future Trends in Software Engineering** (Week 8, Type: graded)
[2025-04-06 04:29:09] [INFO]   Adding 5 questions to assignment **Ethics and Future Trends in Software Engineering**
[2025-04-06 04:29:09] [DEBUG]     Added question 102 to assignment **Ethics and Future Trends in Software Engineering**
[2025-04-06 04:29:09] [DEBUG]     Added question 103 to assignment **Ethics and Future Trends in Software Engineering**
[2025-04-06 04:29:09] [DEBUG]     Added question 87 to assignment **Ethics and Future Trends in Software Engineering**
[2025-04-06 04:29:09] [DEBUG]     Added question 98 to assignment **Ethics and Future Trends in Software Engineering**
[2025-04-06 04:29:09] [DEBUG]     Added question 89 to assignment **Ethics and Future Trends in Software Engineering**
[2025-04-06 04:29:09] [DEBUG]   Created assignment 34: **Ethics and Future Trends in Software Engineering**
[2025-04-06 04:29:09] [INFO] Created 8 assignments for course SE101
[2025-04-06 04:29:09] [DEBUG] Enrolled student student2 in course SE101
[2025-04-06 04:29:09] [INFO] Successfully processed course SE101 from E:\SEPROJECT\M6Alpha\soft-engg-project-jan-2025-se-Jan-8\studyhub\backend\scripts\course\se_updated.json
[2025-04-06 04:29:09] [INFO] PHASE 3: CREATING ENROLLMENTS AND PERSONAL RESOURCES
[2025-04-06 04:29:09] [DEBUG] Enrolled student 2 in course BA201
[2025-04-06 04:29:09] [DEBUG] Enrolled student 2 in course DBMS201
[2025-04-06 04:29:09] [DEBUG] Enrolled student 2 in course JAVA101
[2025-04-06 04:29:09] [DEBUG] Enrolled student 2 in course MAD201
[2025-04-06 04:29:09] [DEBUG] Enrolled student 2 in course SE101
[2025-04-06 04:29:09] [DEBUG] Enrolled student 4 in course BA201
[2025-04-06 04:29:09] [DEBUG] Enrolled student 4 in course DBMS201
[2025-04-06 04:29:09] [DEBUG] Enrolled student 4 in course JAVA101
[2025-04-06 04:29:09] [DEBUG] Enrolled student 4 in course MAD201
[2025-04-06 04:29:09] [DEBUG] Enrolled student 4 in course SE101
[2025-04-06 04:29:09] [DEBUG] Enrolled student 5 in course BA201
[2025-04-06 04:29:09] [DEBUG] Enrolled student 5 in course DBMS201
[2025-04-06 04:29:09] [DEBUG] Enrolled student 5 in course JAVA101
[2025-04-06 04:29:09] [DEBUG] Enrolled student 5 in course MAD201
[2025-04-06 04:29:09] [DEBUG] Enrolled student 5 in course SE101
[2025-04-06 04:29:09] [DEBUG] Enrolled student 6 in course BA201
[2025-04-06 04:29:09] [DEBUG] Enrolled student 6 in course DBMS201
[2025-04-06 04:29:09] [DEBUG] Enrolled student 6 in course JAVA101
[2025-04-06 04:29:09] [DEBUG] Enrolled student 6 in course MAD201
[2025-04-06 04:29:09] [DEBUG] Enrolled student 6 in course SE101
[2025-04-06 04:29:09] [INFO] Creating personal resources from personal_notes.py
[2025-04-06 04:29:09] [INFO] Processing resources for course BA201
[2025-04-06 04:29:09] [INFO] Creating resources for student 2 in course BA201
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'End Term Study Guide' for student 2 in course BA201
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'Weekly Quizzes Review' for student 2 in course BA201
[2025-04-06 04:29:09] [INFO] Creating resources for student 3 in course BA201
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'End Term Study Guide' for student 3 in course BA201
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'Weekly Quizzes Review' for student 3 in course BA201
[2025-04-06 04:29:09] [INFO] Creating resources for student 4 in course BA201
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'End Term Study Guide' for student 4 in course BA201
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'Weekly Quizzes Review' for student 4 in course BA201
[2025-04-06 04:29:09] [INFO] Creating resources for student 5 in course BA201
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'End Term Study Guide' for student 5 in course BA201
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'Weekly Quizzes Review' for student 5 in course BA201
[2025-04-06 04:29:09] [INFO] Creating resources for student 6 in course BA201
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'End Term Study Guide' for student 6 in course BA201
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'Weekly Quizzes Review' for student 6 in course BA201
[2025-04-06 04:29:09] [WARNING] Course DBMS101 not found, skipping resource creation
[2025-04-06 04:29:09] [INFO] Processing resources for course MAD201
[2025-04-06 04:29:09] [INFO] Creating resources for student 2 in course MAD201
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'JavaScript Core Concepts' for student 2 in course MAD201
[2025-04-06 04:29:09] [INFO] Creating resources for student 3 in course MAD201
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'JavaScript Core Concepts' for student 3 in course MAD201
[2025-04-06 04:29:09] [INFO] Creating resources for student 4 in course MAD201
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'JavaScript Core Concepts' for student 4 in course MAD201
[2025-04-06 04:29:09] [INFO] Creating resources for student 5 in course MAD201
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'JavaScript Core Concepts' for student 5 in course MAD201
[2025-04-06 04:29:09] [INFO] Creating resources for student 6 in course MAD201
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'JavaScript Core Concepts' for student 6 in course MAD201
[2025-04-06 04:29:09] [INFO] Processing resources for course SE101
[2025-04-06 04:29:09] [INFO] Creating resources for student 2 in course SE101
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'Software Engineering Fundamentals' for student 2 in course SE101
[2025-04-06 04:29:09] [INFO] Creating resources for student 3 in course SE101
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'Software Engineering Fundamentals' for student 3 in course SE101
[2025-04-06 04:29:09] [INFO] Creating resources for student 4 in course SE101
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'Software Engineering Fundamentals' for student 4 in course SE101
[2025-04-06 04:29:09] [INFO] Creating resources for student 5 in course SE101
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'Software Engineering Fundamentals' for student 5 in course SE101
[2025-04-06 04:29:09] [INFO] Creating resources for student 6 in course SE101
[2025-04-06 04:29:09] [DEBUG] Created personal resource 'Software Engineering Fundamentals' for student 6 in course SE101
[2025-04-06 04:29:09] [INFO] SYNCING COURSES WITH STUDYINDEXER...
[2025-04-06 04:29:09] [DEBUG] Syncing course BA201 with StudyIndexer...
[2025-04-06 04:29:09] [DEBUG] DEBUG: Payload for BA201 - Acronyms: {}, Synonyms: {}
[2025-04-06 04:29:09] [DEBUG] Calling StudyIndexer CourseContent API for BA201...
[2025-04-06 04:29:12] [DEBUG] Successfully synced course BA201 with CourseContent API
[2025-04-06 04:29:12] [DEBUG] Calling StudyIndexer CourseSelector API for BA201...
[2025-04-06 04:29:13] [DEBUG] Successfully synced course BA201 with CourseSelector API
[2025-04-06 04:29:13] [DEBUG] Syncing course DBMS201 with StudyIndexer...
[2025-04-06 04:29:13] [DEBUG] DEBUG: Payload for DBMS201 - Acronyms: {"DBMS": "Database Management Systems", "ER": "Entity-Relationship", "SQL": "Structured Query Language", "DDL": "Data Definition Language", "DML": "Data Manipulation Language", "ACID": "Atomicity, Consistency, Isolation, Durability", "OLAP": "Online Analytical Processing", "OLTP": "Online Transaction Processing", "BCNF": "Boyce-Codd Normal Form", "4NF": "Fourth Normal Form", "5NF": "Fifth Normal Form", "DKNF": "Domain-Key Normal Form", "MVCC": "Multi-Version Concurrency Control", "2PL": "Two-Phase Locking", "2PC": "Two-Phase Commit", "MOLAP": "Multidimensional OLAP", "ROLAP": "Relational OLAP", "HOLAP": "Hybrid OLAP", "ETL": "Extract, Transform, Load"}, Synonyms: {"Normalization": ["Schema Refinement", "Removing Data Redundancies"], "Entity-Relationship (ER) Modeling": ["Relational Schema Design"], "Concurrency Control": ["Locking Protocols", "Serializability Approaches"], "Distributed Databases": ["Federated Databases", "Shared-Nothing Architecture"], "Data Warehousing": ["Analytical Data Storage", "OLAP Systems"], "NoSQL": ["Non-Relational Databases"]}
[2025-04-06 04:29:13] [DEBUG] Calling StudyIndexer CourseContent API for DBMS201...
[2025-04-06 04:29:13] [DEBUG] Successfully synced course DBMS201 with CourseContent API
[2025-04-06 04:29:13] [DEBUG] Calling StudyIndexer CourseSelector API for DBMS201...
[2025-04-06 04:29:14] [DEBUG] Successfully synced course DBMS201 with CourseSelector API
[2025-04-06 04:29:14] [DEBUG] Syncing course JAVA101 with StudyIndexer...
[2025-04-06 04:29:14] [DEBUG] DEBUG: Payload for JAVA101 - Acronyms: {}, Synonyms: {}
[2025-04-06 04:29:14] [DEBUG] Calling StudyIndexer CourseContent API for JAVA101...
[2025-04-06 04:29:15] [DEBUG] Successfully synced course JAVA101 with CourseContent API
[2025-04-06 04:29:15] [DEBUG] Calling StudyIndexer CourseSelector API for JAVA101...
[2025-04-06 04:29:16] [DEBUG] Successfully synced course JAVA101 with CourseSelector API
[2025-04-06 04:29:16] [DEBUG] Syncing course MAD201 with StudyIndexer...
[2025-04-06 04:29:16] [DEBUG] DEBUG: Payload for MAD201 - Acronyms: {}, Synonyms: {}
[2025-04-06 04:29:16] [DEBUG] Calling StudyIndexer CourseContent API for MAD201...
[2025-04-06 04:29:16] [DEBUG] Successfully synced course MAD201 with CourseContent API
[2025-04-06 04:29:16] [DEBUG] Calling StudyIndexer CourseSelector API for MAD201...
[2025-04-06 04:29:17] [DEBUG] Successfully synced course MAD201 with CourseSelector API
[2025-04-06 04:29:17] [DEBUG] Syncing course SE101 with StudyIndexer...
[2025-04-06 04:29:17] [DEBUG] DEBUG: Payload for SE101 - Acronyms: {}, Synonyms: {}
[2025-04-06 04:29:17] [DEBUG] Calling StudyIndexer CourseContent API for SE101...
[2025-04-06 04:29:17] [DEBUG] Successfully synced course SE101 with CourseContent API
[2025-04-06 04:29:17] [DEBUG] Calling StudyIndexer CourseSelector API for SE101...
[2025-04-06 04:29:18] [DEBUG] Successfully synced course SE101 with CourseSelector API
[2025-04-06 04:29:18] [INFO] Sync summary: 5 courses processed
[2025-04-06 04:29:18] [INFO] CourseContent API: 5 successes
[2025-04-06 04:29:18] [INFO] CourseSelector API: 5 successes
[2025-04-06 04:29:18] [INFO] PHASE 4: SYNCING PERSONAL RESOURCES WITH STUDYINDEXER
[2025-04-06 04:29:18] [INFO] Found 20 personal resources to sync
[2025-04-06 04:29:18] [INFO] Starting personal resource sync...
[2025-04-06 04:29:27] [INFO] Sync completed: 20 added, 0 failed, 20 total
[2025-04-06 04:29:27] [INFO] All personal resources synced successfully
[2025-04-06 04:29:27] [INFO] PHASE 5: SYNCING GRADED ASSIGNMENTS WITH STUDYINDEXER
[2025-04-06 04:29:27] [INFO] Found 16 graded assignments to sync
[2025-04-06 04:29:27] [INFO] Starting graded assignment sync...
[2025-04-06 04:29:27] Starting graded assignments sync with StudyIndexer
[2025-04-06 04:29:27] Exporting graded assignments (limit=None, course_id=None, batch_size=50)
[2025-04-06 04:29:27] Found 16 graded assignments to export
[2025-04-06 04:29:27] Exported assignment 4: Distribution Fitting and Hypothesis Testing with 6 questions
[2025-04-06 04:29:27] Exported assignment 5: Demand Analysis and Market Experiments with 9 questions
[2025-04-06 04:29:27] Exported assignment 7: Multiple Linear Regression with 3 questions
[2025-04-06 04:29:27] Exported assignment 18: Exploring NoSQL Databases: Key-Value Stores with 5 questions
[2025-04-06 04:29:27] Exported assignment 19: Document and Column-Family Databases in Practice with 5 questions
[2025-04-06 04:29:27] Exported assignment 20: Graph Databases and Polyglot Persistence Design with 5 questions
[2025-04-06 04:29:27] Exported assignment 21: Distributed Database Replication Strategies with 5 questions
[2025-04-06 04:29:27] Exported assignment 22: Distributed Query Processing and Concurrency Control Challenges with 5 questions
[2025-04-06 04:29:28] Exported assignment 23: Data Warehouse Design and Dimensional Modeling with 5 questions
[2025-04-06 04:29:28] Exported assignment 24: OLAP Operations and Data Analysis with 5 questions
[2025-04-06 04:29:28] Exported assignment 25: Implementing Database Security Policies with 5 questions
[2025-04-06 04:29:28] Exported assignment 26: Database Performance Tuning and Emerging Technologies Report with 5 questions
[2025-04-06 04:29:28] Exported assignment 29: **Software Architecture and Design Principles** with 7 questions
[2025-04-06 04:29:28] Exported assignment 30: **Software Testing and Quality Assurance Techniques** with 7 questions
[2025-04-06 04:29:28] Exported assignment 33: **Advanced Agile Project Management** with 5 questions
[2025-04-06 04:29:28] Exported assignment 34: **Ethics and Future Trends in Software Engineering** with 5 questions
[2025-04-06 04:29:28] Exported 16 assignments with questions
[2025-04-06 04:29:28] Sending 16 assignments to StudyIndexer in batches of 50
[2025-04-06 04:29:28] Processing batch 1 with 16 assignments
[2025-04-06 04:29:42] Bulk index completed: 16 added, 0 failed
[2025-04-06 04:29:42] Assignment indexing completed: 16 added, 0 failed
[2025-04-06 04:29:42] [INFO] Sync completed: 16 added, 0 failed, 16 total
[2025-04-06 04:29:42] [INFO] All graded assignments synced successfully
[2025-04-06 04:29:42] [INFO] Database initialization completed

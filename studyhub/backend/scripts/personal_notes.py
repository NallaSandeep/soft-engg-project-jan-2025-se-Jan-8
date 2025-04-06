COURSE_RESOURCES = {
    "BA201": [
        {
            "name": "End Term Study Guide",
            "description": "Comprehensive review of all topics covered in Business Analytics (BA201).",
            "notes": [
                {
                    "name": "Data Visualization and Distribution Fitting Summary",
                    "content": """Okay, so for Business Analytics, BA201, the end term is coming up and I'm trying to put together a study guide based on my understanding of the first couple of weeks. Week 1 was all about **Data Visualization**. I remember the lecture videos emphasizing how crucial it is to present data effectively for business decisions [1]. It's not just about making pretty charts; it's about bridging the gap between analysis and action. The four core principles they talked about were **data integrity**, making sure the visualization accurately reflects the data; **purpose-driven design**, knowing what you want to communicate; **data-ink ratio optimization**, getting rid of unnecessary clutter; and **strategic annotation**, guiding the viewer to the key takeaways [1].

                    I should probably go back and review the different chart types. Bar charts are best for **categorical comparisons** [2], which makes sense because you can easily see the difference in height. Line charts are for **time series and trends** [2], showing how something changes over time. Scatter plots help see **relationships between two variables** [2], like if higher spending leads to more sales. And histograms are for showing **distributions** [2], how frequently different values occur. I need to be careful not to use 3D effects that can distort the data [2], or misleading axis scales [2]. Also, too much 'chart junk' is bad [2]. I wonder if there are specific rules for when to use a pie chart versus a bar chart? Maybe the cheat sheet has more details [3].

                    Week 2 moved into **Statistical Distribution Fitting** [4]. This seemed a bit more theoretical. We learned that probability distributions help model the likelihood of different outcomes [5]. The lecture content extract mentioned common distributions like **normal, exponential, and uniform** [5]. It's important to identify the correct distribution to predict future events, like sales or loan defaults [5]. There were three main ways to use data: using raw data in simulations, fitting a theoretical distribution, or defining an **empirical distribution** directly from the data [5]. Empirical distributions are built from the observed data itself [5].

                    The notes said that theoretical distributions are generally preferred if they fit well because they are smoother and can generalize beyond the observed data [5]. But sometimes, an empirical distribution is better if no theoretical one fits properly [5]. We looked at summary statistics like mean, median, and standard deviation to get an initial idea of the distribution's shape [5]. If the mean and median are close, it might be symmetric. A high coefficient of variation (CV) could suggest a right-skewed distribution, possibly log-normal [5]. We also talked about **skewness** (ν) - positive means a right tail (like exponential), negative means a left tail [5].

                    Then came **parameter estimation**. For example, a normal distribution has mean and standard deviation as parameters, and exponential has a rate parameter (λ) [5]. The most common method is **Maximum Likelihood Estimation (MLE)** [5]. After that, we need to check the **goodness-of-fit** [5]. Methods include frequency comparisons, probability plots (like **Q-Q plots** which compare quantiles and should be a straight line if the fit is good), and statistical tests like the **chi-square test** and the **Kolmogorov-Smirnov (K-S) test** [5]. The chi-square test compares observed and expected frequencies in intervals, while the K-S test looks at the maximum difference between cumulative distribution functions [5]. I need to remember when to use which test. The notes say chi-square is versatile for both continuous and discrete data, but K-S is better for continuous [5].

                    I should probably try to work through some examples of fitting distributions to different types of data. And maybe review the assumptions behind the normal distribution – are there situations in business where it definitely wouldn't apply? What about the exponential distribution – is that only for time-related data? These are things I should clarify.
                    """,
                    "file_type": "text/plain"
                },
                {
                    "name": "Association Analysis and Demand Modeling Notes",
                    "content": """Okay, continuing my BA201 study guide, I need to cover Weeks 3 and 4. Week 3 was on **Association Analysis** [6]. This felt a bit different from the first two weeks, more about finding relationships between different things. The overview mentioned **Bayesian networks** and **association rule mining** [6]. I remember we briefly touched on **correspondence analysis** as well [6].

                    Association rule mining is probably the most important part here. It's about finding rules like "if a customer buys X, they are also likely to buy Y." I need to remember the key metrics like **support, confidence, and lift** for evaluating these rules. Support is how frequently the itemset appears, confidence is how often Y appears if X also appears, and lift tells us how much more likely Y is to be bought when X is bought, compared to the general probability of buying Y. I should probably look up some examples of how to calculate these and how to interpret the results. What's a good lift score? Is there a threshold?

                    The overview also mentioned things like **causal inference techniques** and **propensity score matching** [6], which sound more advanced. I think the main focus for the exam will be on the basics of association rule mining. Maybe I should also quickly review what Bayesian networks are and how they can show probabilistic relationships between variables.

                    Week 4 was all about **Demand Response Curves** [6]. This was quite practical, focusing on how demand changes with price. The summary talked about **price elasticity estimation** and **revenue optimization** [6]. We learned about the properties of demand curves and the concept of **consumer surplus** [6]. Then we got into different modeling approaches like **linear regression** and **constant elasticity models** [6]. The log-log transformation was mentioned as a way to model constant elasticity [6].

                    We spent a lot of time on **experimental design** to estimate demand [6]. It's tricky to isolate the effect of price from other factors. The importance of **model validation** was also highlighted [6]. We discussed how businesses use demand modeling for **pricing strategy, market segmentation, and revenue management** [6].

                    Some of the more advanced topics included **discrete choice models** and **price optimization under constraints** [6, 7]. Also, integrating **cost structures** into demand modeling seemed important for profit maximization [6]. I should probably review the case studies to see how price elasticity was estimated in real-world scenarios and how those insights were used for pricing decisions [6].

                    The summary also mentioned special cases like **Veblen goods** and **Giffen goods** [6], where the law of demand might not hold. I need to understand the difference between these. Veblen goods are desirable because they are expensive, while Giffen goods are inferior goods for which demand increases as price increases (which sounds counterintuitive!).

                    Overall, for the end term, I should focus on understanding the core principles of data visualization and being able to choose appropriate chart types. For distribution fitting, I need to know the common distributions, how to estimate parameters, and how to assess goodness-of-fit using both visual methods and statistical tests. For association analysis, the focus seems to be on association rule mining and the key metrics. And for demand response curves, I need to understand price elasticity, different modeling approaches, and how businesses use these models for pricing and revenue optimization. I should also probably skim through the concepts not covered in each week to make sure I don't miss anything critical, although the "not covered" list probably won't be tested directly [4, 6-8].
                    """,
                    "file_type": "text/plain"
                }
            ]
        },
        {
            "name": "Weekly Quizzes Review",
            "description": "My notes and reflections on the weekly quizzes for BA201.",
            "notes": [
                {
                    "name": "Quiz 1 Insights",
                    "content": """Reflecting on the first quiz for BA201, it was heavily focused on the principles of data visualization. I remember one question asked about the importance of the **data-ink ratio**, which I now understand is all about maximizing the amount of ink used to display actual data while minimizing non-data ink. This makes the visualizations clearer and more effective. I also recall a question about choosing the right chart type for different scenarios. For instance, comparing the sales figures across different product categories requires a **bar chart**, while showing the trend of website traffic over the past year is best done with a **line chart**.

                    There was a bit of confusion I had regarding the different types of scales used in charts, like nominal, ordinal, interval, and ratio scales. I should probably review these again. Nominal scales are just categories with no order, like product names. Ordinal scales have an order, like satisfaction levels (low, medium, high). Interval scales have ordered categories with equal intervals between them, but no true zero point, like temperature in Celsius. Ratio scales have ordered categories with equal intervals and a true zero point, like sales revenue. Knowing these is important for choosing appropriate visualizations.

                    Another question was about common pitfalls in data visualization, such as using **misleading 3D effects** or **incorrect axis scales**. These can completely distort the viewer's understanding of the data, which defeats the whole purpose of visualization in the first place. I also learned that using consistent color schemes is crucial for clarity. Inconsistent colors can be confusing and make it harder to interpret the data.

                    I also remember a question about the role of annotations in visualizations. **Annotations** are text labels or symbols used to highlight important data points or trends in a chart. They can guide the viewer's attention and help them understand the key takeaways from the visualization. Strategic use of titles, subtitles, and data labels is also important for providing context.

                    Overall, the first quiz reinforced the fundamental principles of effective data visualization and the importance of making conscious choices about chart types, scales, colors, and annotations to communicate data insights clearly and accurately for business decision-making. I need to practice identifying bad visualization examples and explaining why they are ineffective.
                    """,
                    "file_type": "text/plain"
                },
                {
                    "name": "Quiz 2 Review: Distribution Fitting",
                    "content": """The second quiz in BA201 covered distribution fitting, and it was definitely more challenging. One question involved identifying the likely type of distribution based on summary statistics like the mean and median. If the mean is significantly higher than the median, it often suggests a **right-skewed distribution**, like the exponential or log-normal. Conversely, if the median is higher, it might indicate a **left-skewed distribution**. If they are close, the distribution could be **symmetric**, like the normal distribution.

                    Another question tested my understanding of **empirical vs. theoretical distributions**. Empirical distributions are built directly from the observed data and can be useful when no standard theoretical distribution fits well. However, they are limited to the range of the observed data and cannot extrapolate beyond it. Theoretical distributions, on the other hand, are mathematical models that can generalize beyond the sample data, but their accuracy depends on how well they fit the actual data.

                    I also remember a question about **parameter estimation**, specifically for the normal distribution. The parameters of a normal distribution are its mean (μ) and standard deviation (σ). These are typically estimated from the sample data using methods like the sample mean and sample standard deviation. For other distributions, like the exponential distribution, the parameter is the rate (λ), which is often estimated as the inverse of the sample mean.

                    A significant part of the quiz focused on assessing the **goodness-of-fit**. I recall a question about interpreting a Q-Q plot. If the points on a Q-Q plot roughly fall along a straight diagonal line, it suggests that the chosen theoretical distribution provides a good fit to the data. Deviations from this line, especially at the tails, indicate a poor fit.

                    Finally, there was a question about the **chi-square goodness-of-fit test**. This test compares the observed frequencies of data in different categories or intervals with the expected frequencies under the hypothesized distribution. The test statistic measures the discrepancy between these frequencies, and a high test statistic (or a low p-value) suggests that the hypothesized distribution does not provide a good fit to the data. I need to remember how to calculate the degrees of freedom for the chi-square test – it depends on the number of categories and the number of parameters estimated from the data.

                    This quiz highlighted the importance of not only understanding different types of distributions but also knowing how to choose an appropriate distribution for a given dataset and how to formally evaluate whether the chosen distribution provides a good representation of the data. I should probably review the steps involved in the distribution fitting process: exploratory data analysis, hypothesizing a distribution, parameter estimation, and goodness-of-fit testing.
                    """,
                    "file_type": "text/plain"
                }
            ]
        }
    ],
    "DBMS101": [
        {
            "name": "Midterm Exam Notes",
            "description": "My comprehensive notes for the DBMS101 midterm exam.",
            "notes": [
                {
                    "name": "Introduction to Databases and Relational Model",
                    "content": """Alright, prepping for the DBMS101 midterm and the first few weeks seem to be the most fundamental. Week 1 introduced the whole idea of **Database Management Systems (DBMS)** [9]. It's basically software to manage and organize data, acting as an intermediary between users and the actual database [10]. The big advantage over file systems is that DBMS helps with **data consistency, data security, concurrent access, and backup & recovery** [10].

                    The concept of **data abstraction** was key [10, 11]. They talked about three levels: **physical level** (how data is actually stored), **logical level** (what data is stored and the relationships), and **view level** (how users see parts of the database) [10, 11]. Then there's the **schema**, which is the overall design, including tables, attributes, and constraints, and the **instance**, which is the actual data at a specific point in time [10]. We also learned about different **data models**: the **relational model** (using tables), the **entity-relationship (ER) model** (entities, attributes, relationships), and others like object-based, hierarchical, and network models, though the course seems to focus mainly on relational [10].

                    Week 2 dove into the **relational model** and **SQL essentials** [12]. SQL is the standard language for relational databases [10]. It has two main parts: **Data Definition Language (DDL)** for defining the database structure (like `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`) and **Data Manipulation Language (DML)** for working with the data (like `SELECT`, `INSERT`, `UPDATE`, `DELETE`) [10]. I should definitely remember these commands.

                    **Integrity constraints** are super important for ensuring data consistency [12]. We covered **primary keys** (unique identifier), **foreign keys** (linking tables), and **NOT NULL constraints** [10, 12]. I need to understand how to define these when creating tables in SQL. For example, a `PRIMARY KEY` automatically becomes `NOT NULL` [13]. The `FOREIGN KEY` constraint is crucial for maintaining **referential integrity**, ensuring that values in one table correspond to values in another [13, 14].

                    The basic structure of a SQL query is `SELECT` (what to retrieve), `FROM` (which tables to use), and `WHERE` (conditions to filter results) [14]. You can use `DISTINCT` to get unique rows [14]. The `*` in `SELECT *` means select all attributes [14, 15]. You can also perform arithmetic operations in the `SELECT` clause [14]. The `WHERE` clause uses logical operators like `AND`, `OR`, and `NOT` to specify conditions [14]. When you list multiple tables in the `FROM` clause without a join condition, it creates a **Cartesian product** [14, 15], which is all possible combinations of rows. This is usually combined with a `WHERE` clause to get meaningful results by specifying join conditions (like matching IDs in related tables) [15].

                    I should practice writing basic SQL queries to retrieve, filter, and combine data from single and multiple tables. Understanding how primary and foreign keys enforce relationships is also key. Maybe I should try to design a simple database schema with a couple of related tables and then write SQL queries to retrieve information based on different criteria.

                    What about the different SQL standards like SQL-86, SQL-92, SQL:1999, etc. [14]? Do I need to know the specifics of each version, or just that SQL has evolved over time with added features? The lecture extract mentioned some of the additions like regular expressions and XML features [14]. Probably good to just have a general idea of the evolution.
                    """,
                    "file_type": "text/plain"
                },
                {
                    "name": "Advanced SQL and Relational Calculus",
                    "content": """Week 3 moved into **Advanced SQL** and **Subqueries** [16]. Subqueries are basically queries nested inside other queries. They can be used in the `WHERE`, `FROM`, and `SELECT` clauses [17, 18]. Subqueries in the `WHERE` clause can be used for **set membership** using `IN` or `NOT IN`, for **set comparison** using operators like `>`, `<`, `=`, with `SOME` or `ALL`, and for checking **set cardinality** using `EXISTS` or `NOT EXISTS` [17, 18].

                    The `SOME` clause checks if the condition is true for at least one value returned by the subquery, while `ALL` requires the condition to be true for all values [18]. `EXISTS` checks if the subquery returns any rows at all [18, 19]. For example, to find students enrolled in both Fall 2020 and Spring 2021, you could use a subquery with `IN` [18]. To find instructors with a salary greater than at least one instructor in Biology, you'd use `> SOME` [18].

                    Subqueries can also appear in the `FROM` clause, allowing you to create temporary tables within your query. These are sometimes called **derived tables**. The `WITH` clause, or **Common Table Expressions (CTEs)**, provides a way to define temporary, named result sets that can be referenced within a single query, making complex queries more readable [18].

                    Scalar subqueries in the `SELECT` clause are expected to return a single value [18]. For example, you could select the department name and the count of instructors in that department using a scalar subquery [18]. It's important to make sure these subqueries indeed return only one value, or it will cause an error.

                    We also covered **Database Modification** using `INSERT` (to add new records), `DELETE` (to remove records), and `UPDATE` (to change existing records) [16-18]. You can use subqueries in `DELETE` and `UPDATE` statements in the `WHERE` clause to specify conditions based on the results of another query [18].

                    Week 4 introduced **Indexing, Transactions, and Relational Calculus** [20]. Indexing is a way to speed up data retrieval, but I don't think it was covered in much detail in the initial materials. Transactions are sequences of operations that should be treated as a single logical unit of work, ensuring **ACID properties**: Atomicity, Consistency, Isolation, and Durability [20].

                    **Relational Calculus** is a formal, non-procedural query language based on predicate logic [20, 21]. It describes the desired result without specifying how to compute it [21]. There are two main types: **Tuple Relational Calculus (TRC)**, which uses tuple variables, and **Domain Relational Calculus (DRC)**, which uses domain variables (representing attributes) [20-22]. Both use **universal (∀)** and **existential (∃) quantifiers** to express conditions [21-23]. TRC queries are of the form `{t | P(t)}` (all tuples `t` such that predicate `P(t)` is true), while DRC queries are like `{<x1, x2, ..., xn> | P(x1, x2, ..., xn)}` (all tuples of values `<x1, x2, ..., xn>` such that predicate `P` is true) [21].

                    The concept of **safe expressions** in relational calculus is important to ensure that queries produce finite result sets and don't involve infinite relations or values not in the database [20, 21, 24]. An expression is safe if every component of the resulting tuple appears in one of the relations, tuples, or constants in the predicate [21]. Relational algebra (which we didn't cover in detail yet but I know is procedural) and relational calculus (both TRC and DRC) are actually **equivalent in expressive power** [20, 21].

                    I should probably review the different types of subqueries and practice writing them. Understanding the difference between `SOME` and `ALL`, and when to use `EXISTS` is crucial. Also, I need to grasp the basic syntax and concepts of Tuple and Domain Relational Calculus, especially the use of quantifiers and the idea of safe expressions. How does SQL relate to relational calculus? Is SQL an implementation of it? The lecture mentioned that relational calculus provides a foundation for modern query languages like SQL [20, 21].
                    """,
                    "file_type": "text/plain"
                }
            ]
        }
    ],
    "MAD201": [
        {
            "name": "JavaScript Core Concepts",
            "description": "My notes on the fundamental JavaScript concepts covered in the initial weeks of MAD201.",
            "notes": [
                {
                    "name": "Week 1 & 2 JavaScript Fundamentals",
                    "content": """Okay, for Modern Application Development II (MAD201), it seems like the first two weeks are all about solidifying our JavaScript foundation before we jump into Vue.js. Week 1 covered **JavaScript Fundamentals** [25]. We started with the history and how it got standardized under **ECMAScript** [25]. It's interesting to know how the language evolved to become what it is today for web development.

                    The lecture emphasized **variable declarations** using `var`, `let`, and `const` [25]. I need to remember the key differences, especially the scoping rules (`var` has function scope, while `let` and `const` have block scope) and the fact that `const` variables cannot be reassigned after initialization. We also talked about **dynamic typing**, meaning you don't have to explicitly declare the type of a variable, and the language handles it at runtime [25]. This can be both flexible and a source of potential errors if you're not careful with **type coercion** and **comparison operators** (like `==` vs. `===`) [25]. The triple equals (`===`) checks for both value and type equality without coercion, which is generally preferred.

                    JavaScript's interaction with the **Document Object Model (DOM)** for dynamic web page manipulation was introduced [25]. This is how we can use JavaScript to change the content, structure, and style of HTML documents. We also went over basic **control structures** like `if/else` statements, `for` and `while` loops, and different types of **functions** [25]. I should probably practice manipulating the DOM using JavaScript to make sure I understand how it works.

                    Week 2 moved into **JavaScript Collections and Modularity** [26]. We looked at **arrays** in detail and the various **iteration techniques**, especially **higher-order functions** like `map`, `filter`, and `reduce` [26]. These are super powerful for working with collections in a functional style. `map` transforms each element, `filter` selects elements based on a condition, and `reduce` combines elements into a single value. I should definitely get more comfortable using these.

                    We also covered **destructuring** (for easily extracting values from arrays and objects) and **generators** (which can pause and resume execution) [26]. These seem more advanced but could be useful in certain situations.

                    A big part of Week 2 was **modularity**. We compared different **module systems**: **ES6 modules** (using `import` and `export`), **CommonJS** (used by Node.js with `require` and `module.exports`), and **AMD** [26]. It seems like ES6 modules are the modern standard for browser-based JavaScript. We also learned how to use **Node Package Manager (npm)** to manage project dependencies [26]. This is essential for bringing in external libraries and frameworks.

                    Finally, we touched on **object-oriented programming (OOP)** in JavaScript, including **prototype-based inheritance**, **class syntax** (which is syntactic sugar over prototypes), and **asynchronous execution** through the **event loop** [26]. The event loop is crucial for handling non-blocking operations like network requests.

                    For the midterm, I should really focus on understanding variable scoping, the difference between `==` and `===`, DOM manipulation basics, using `map`, `filter`, and `reduce` effectively, the different module systems and how to import/export, and the fundamentals of JavaScript objects and asynchronous programming with the event loop. I wonder if we need to know the specifics of AMD since ES6 modules are the standard now. Maybe it's just for historical context? I should also try to understand the 'this' keyword in JavaScript better – it can be quite confusing.
                    """,
                    "file_type": "text/plain"
                },
                {
                    "name": "Frontend Implementation and Vue.js Introduction",
                    "content": """Weeks 3 and 4 of MAD201 seem to bridge the gap between pure JavaScript and the Vue.js framework. Week 3 was about **Frontend Implementation** in general [27]. We discussed the separation of **frontend and backend responsibilities** [27]. The frontend is all about the user interface (UI) and user experience (UX), while the backend handles data and business logic. We looked at both **imperative** (step-by-step instructions) and **declarative** (describing the desired outcome) programming paradigms in the context of UI development [27]. Frameworks like Vue.js lean towards the declarative approach.

                    **State management** was a key topic [27]. In frontend applications, managing data and how it changes over time is crucial for building interactive interfaces. We briefly touched on local component state versus more global state management solutions (which I think Vuex will cover later). **Responsive and adaptive design principles** were also discussed [27], making sure our applications work well on different screen sizes. And the importance of **component-based architecture** for building reusable UI elements was highlighted [27].

                    We also covered best practices for **performance optimization**, **accessibility**, and **asynchronous programming** in the frontend [27]. Things like minimizing HTTP requests, optimizing images, and using techniques like debouncing and throttling can improve performance. Accessibility (making applications usable by people with disabilities) is really important, and we need to follow guidelines like WCAG. For asynchronous operations (like fetching data from an API), we use things like Promises and `async/await` in JavaScript.

                    Week 4 was our introduction to **Vue.js and Reactive Programming** [28]. The core of Vue.js is its **reactivity system** [28]. When you change data in a Vue component, the UI automatically updates to reflect those changes. This makes building dynamic interfaces much easier. We learned how to create **Vue components**, which are reusable building blocks of our application [28]. We also looked at **data binding** using the `v-model` directive for two-way binding (when the UI changes, the data updates, and vice versa) and mustache syntax `{{ }}` for one-way binding (displaying data in the template) [28].

                    **Props** are used to pass data down from parent to child components, and **events** are used for child components to communicate back to their parents [28]. This prop-event pattern is fundamental for component communication. We also discussed the importance of separating **local and global state** [28]. Local state is data specific to a component, while global state might be needed across multiple parts of the application (which is where Vuex comes in).

                    Vue uses a **virtual DOM** to optimize updates [28]. Instead of directly manipulating the real DOM (which can be slow), Vue creates a virtual representation, compares it to the previous virtual DOM, and only updates the necessary parts of the real DOM.

                    We then got an **introduction to Vuex state management** [29]. Vuex provides a centralized store for managing the state of larger Vue.js applications. It follows a specific pattern with **state** (the data), **mutations** (synchronous functions for modifying the state), **actions** (asynchronous functions that can commit mutations), and **getters** (computed properties for the store) [29]. We started learning about managing both **global vs. local state** using Vuex [29]. Finally, we touched on **performance optimization and debugging in Vue** [29].

                    For the midterm, I should understand the principles of frontend architecture, the importance of state management, and responsive design. For Vue.js, I need to grasp the core concepts of reactivity, components, props and events, data binding, and the role of the virtual DOM. I should also have a basic understanding of the Vuex store and its core components (state, mutations, actions, getters). I wonder when we will learn about routing in Vue.js for multi-page applications? And how does Vue.js handle more complex component interactions? I should probably look at some more Vue.js component examples to solidify my understanding.
                    """,
                    "file_type": "text/plain"
                }
            ]
        }
    ],
    "SE101": [
        {
            "name": "Software Engineering Fundamentals",
            "description": "My notes covering the foundational concepts of software engineering from the beginning of the SE101 course.",
            "notes": [
                {
                    "name": "Week 1 & 2: SDLC and Requirements",
                    "content": """Starting my study for Software Engineering (SE101), the first couple of weeks laid the groundwork for the entire course. Week 1 was all about **Deconstructing the Software Development Process** [30]. We learned that software engineering evolved from just coding to a more disciplined approach with processes, models, and strategies [31].

                    We looked at different **Software Development Lifecycle (SDLC) models**. The **Waterfall model** is a sequential process with phases like requirements, design, implementation, testing, and maintenance [32, 33]. It's straightforward but can be inflexible to changes. Then we discussed **Agile methodologies**, which emphasize iterative development, customer collaboration, and responding to change [32, 33]. Frameworks like Scrum and Kanban fall under Agile. The lecture also touched on **component-based architecture** and how large systems like Amazon are built from smaller, integrated modules [31, 32]. We also talked about the importance of **quality assurance** throughout the process, including **Test-Driven Development (TDD)** [32, 33].

                    Week 2 was dedicated to **Software Requirements** [34]. This seems really crucial because if you don't know what you're supposed to build, you'll probably build the wrong thing! We learned about identifying **stakeholders** (primary, secondary, tertiary users) and different **requirement collection techniques** like interviews, questionnaires, observation, focus groups, and looking at existing documentation [35].

                    The key output of requirements engineering is the **Software Requirements Specification (SRS)** [36-38]. It should clearly define both **functional requirements** (what the system should do) and **non-functional requirements** (how well it should do it, like performance, security, usability, reliability, etc.) [38]. We discussed how to specify, prioritize, and validate these requirements. **Use cases** and **user stories** are common ways to capture functional requirements, especially in agile development [33, 39, 40]. Good user stories follow the **INVEST** criteria: Independent, Negotiable, Valuable, Estimable, Small, and Testable [39]. We also learned about managing **requirements volatility** and tracing requirements throughout the development process [34].

                    For the upcoming assessment, I should definitely know the main SDLC models (Waterfall and Agile especially), their pros and cons, and when each might be more appropriate. I also need to understand the different techniques for gathering requirements and the importance of a well-written SRS that includes both functional and non-functional requirements. I should be able to differentiate between them and perhaps give examples. Also, understanding what makes a good user story (INVEST) seems important. How do you handle conflicting requirements from different stakeholders? The lecture mentioned prioritizing, but are there specific techniques for that? And how do you ensure that the documented requirements are actually what the user needs? Validation techniques were mentioned, but I should probably review those.
                    """,
                    "file_type": "text/plain"
                },
                {
                    "name": "UI Design and Project Management Fundamentals",
                    "content": """Weeks 3 and 4 of SE101 shifted focus to user interfaces and project management. Week 3 was all about **Software User Interfaces** [41]. It started with **usability principles** based on ISO 9241 [41, 42]. Usability is about effectiveness, efficiency, learnability, safety, and memorability [42]. We discussed the **psychological foundations of human-computer interaction**, like cognitive load and perception [41].

                    The **UI/UX design lifecycle** was covered, from low-fidelity prototyping (like paper prototypes and storyboards) to high-fidelity interactive mockups [41]. The importance of **iterative refinement** through **user testing** was emphasized [41]. We also learned about **accessibility guidelines (WCAG)** and inclusive design [41]. Designing for users with disabilities is a really important aspect. Other topics included using **design systems**, evaluating **information architecture**, and creating **style guides** [41]. We briefly touched on more advanced areas like emotion-driven design and microinteractions. The focus seemed to be on creating user-centered designs that are effective, efficient, and satisfying to use. I should probably review some examples of good and bad UI designs based on these principles.

                    Week 4 moved into **Software Project Management** [43]. This covered both traditional and agile approaches. We learned about **estimation methods** like COCOMO II, function point analysis, and planning poker [43, 44]. It seems like accurate estimation is really challenging in software development. We also looked at the **Scrum framework** in detail, including roles (Product Owner, Scrum Master, Development Team), events (Sprint Planning, Daily Scrum, Sprint Review, Sprint Retrospective), and artifacts (Product Backlog, Sprint Backlog, Increment) [39, 43]. We also touched on scaled agile frameworks like SAFe and LeSS.

                    **Risk management** was another key topic, covering risk identification, assessment, and mitigation strategies [33, 43]. We practiced this through simulated project scenarios. We also learned about **metrics-driven management** using tools like burn-down charts and earned value analysis [43]. Understanding how to track progress and identify potential problems early seems crucial. The impact of leadership, communication, and stakeholder management on project success was also discussed, along with managing technical debt and continuous improvement.

                    For the upcoming assessment, I should understand the core usability principles and the UI/UX design process, including prototyping and user testing. For project management, I need to know the basics of estimation techniques and have a good grasp of the Scrum framework, its roles, events, and artifacts. I should also understand the importance of risk management and be familiar with some common techniques. How do you balance the need for a perfect design with project deadlines and budget constraints? And in agile, how do you handle changes in requirements during a sprint? These are practical challenges that I should think about. Also, I should probably review the different testing methodologies mentioned in the context of quality assurance [33, 45].
                    """,
                    "file_type": "text/plain"
                }
            ]
        }
    ]
}
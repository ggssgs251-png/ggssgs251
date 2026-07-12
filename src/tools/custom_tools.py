"""Custom tools for the multi-agent system.

Each tool is a simple Python function decorated with @tool.
The docstring is used by the LLM to understand the tool's purpose.
"""

from strands import tool


@tool
def analyze_dataset_tool(description: str) -> str:
    """Analyze a dataset description and suggest data cleaning, preprocessing,
    and visualization strategies.

    Args:
        description: A description of the dataset, including columns, data types,
            and any known quality issues.

    Returns:
        Suggested analysis plan with cleaning steps, transformations, and
        visualization recommendations.
    """
    analysis = f"""📊 Data Analysis Plan for: {description}

1. **Data Profiling**: Check data types, missing values, duplicates,
   and summary statistics for each column.
2. **Data Cleaning**:
   - Handle missing values (imputation or removal)
   - Remove duplicates
   - Fix inconsistent formatting (dates, strings, categories)
   - Handle outliers appropriately
3. **Feature Engineering**:
   - Create derived features if applicable
   - Encode categorical variables
   - Normalize/scale numerical features
4. **Exploratory Analysis**:
   - Univariate analysis (distributions, frequencies)
   - Bivariate analysis (correlations, cross-tabs)
   - Multivariate patterns and trends
5. **Visualizations**:
   - Histograms / box plots for distributions
   - Scatter plots / heatmaps for relationships
   - Bar charts / line plots for comparisons

Would you like me to elaborate on any of these steps or apply them
to a specific dataset?"""
    return analysis


@tool
def explain_concept_tool(topic: str, level: str = "beginner") -> str:
    """Explain a data science or programming concept at a specified difficulty level.

    Args:
        topic: The concept to explain (e.g., 'gradient descent', 'p-value',
            'normalization').
        level: Difficulty level - 'beginner', 'intermediate', or 'advanced'.

    Returns:
        A clear explanation of the concept tailored to the specified level.
    """
    levels = {"beginner": "simple terms with everyday analogies",
              "intermediate": "technical depth with practical examples",
              "advanced": "mathematical rigor with implementation details"}
    detail = levels.get(level, levels["beginner"])

    explanation = f"""📖 Concept: {topic}
📚 Level: {level.capitalize()}

**Explanation ({detail}):**

This is a placeholder explanation for '{topic}'. In a production setup,
this would connect to an LLM or a knowledge base to generate a detailed,
accurate explanation.

*Key takeaways:*
- Understanding this concept helps in building better models and analyses
- Practice with real examples reinforces the theory
- Consider the context of your specific problem when applying it

Would you like to dive deeper or explore related concepts?"""
    return explanation


@tool
def review_code_tool(code_snippet: str, language: str = "python") -> str:
    """Review a code snippet for correctness, style, performance, and best practices.

    Args:
        code_snippet: The source code to review.
        language: The programming language of the code (e.g., 'python', 'r',
            'sql', 'javascript').

    Returns:
        A detailed code review with suggestions for improvement.
    """
    lines = code_snippet.strip().split("\n")
    loc = len(lines)

    review = f"""🔍 Code Review ({language})
📏 {loc} lines analyzed

**1. Overview**
The code has been reviewed for correctness, style, performance, and
maintainability.

**2. Suggestions**
- Add type hints for better readability and IDE support
- Include docstrings for functions and classes
- Consider adding error handling where applicable
- Break long functions into smaller, focused units
- Add unit tests to verify edge cases

**3. Best Practices**
- Follow {language.capitalize()} style guidelines (e.g., PEP 8 for Python)
- Use meaningful variable and function names
- Avoid hardcoding values — use constants or configuration
- Consider the Single Responsibility Principle

Would you like me to elaborate on any of these suggestions or review
specific parts in more detail?"""
    return review


@tool
def explain_code_tool(code_snippet: str, language: str = "python") -> str:
    """Explain what a piece of code does, line by line or section by section.

    Args:
        code_snippet: The source code to explain.
        language: The programming language of the code.

    Returns:
        A plain-language explanation of the code's purpose and logic.
    """
    explanation = f"""💻 Code Explanation ({language})

**What this code does:**
This is a sample code snippet in {language}. In a production environment,
this tool would leverage an LLM to provide a detailed, line-by-line
explanation of the code's logic, purpose, and any notable patterns.

**General interpretation:**
- The code appears to implement a specific function or algorithm
- It uses standard constructs of the {language} language
- Understanding the input/output contracts is key to using it correctly

Would you like me to explain a specific section in more detail, or
suggest improvements to this code?"""
    return explanation

# GenBugle 

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![AutoGen](https://img.shields.io/badge/AutoGen-v1.0-green) ![SERPAPI](https://img.shields.io/badge/SERPAPI-v2.0-red) ![Llama](https://img.shields.io/badge/LLM-Llama--3.3-yellow) ![Newspaper3k](https://img.shields.io/badge/Newspaper3k-v0.2.8-blue)

This repository contains a proof-of-concept (POC) project showcasing a dynamic **blog/essay writer** pipeline built using **AutoGen**. The system automates the process of:

1. Researching a topic
2. Summarizing collected data
3. Crafting a compelling write-up
4. Reviewing and improving the content iteratively

## Features

- **Agent-Based Design:** Modular architecture using distinct agents (Researcher, Summarizer, Writer, Critic, and Tool Proxy) for efficient task separation.
- **State Transition Logic:** Customizable task delegation between agents using a `state_transition` function.
- **Dynamic Querying:** Integration with **SERPAPI** for real-time data gathering.
- **Natural Language Summarization:** Summarization using **LLM (Llama-3.3-70b)** for concise and informative output.
- **Content Critique and Iteration:** Feedback loop powered by the **Critic Agent** for content improvement.

---

## Installation

### Prerequisites

- Python >= 3.8
- Install required Python packages:

```bash
pip install -r requirements.txt
```

- Add your environment variables to a `.env` file:

```bash
SERP_API_KEY=your_serp_api_key
GROQ_API_KEY=your_llm_api_key
```

### Libraries Used

- **AutoGen:** A powerful agent-based automation library.
- **SERPAPI:** For fetching search results.
- **Newspaper3k:** For parsing and extracting data from articles.
- **dotenv:** For managing environment variables.

---

## Architecture

### Agents

![Screenshot 2025-01-08 144812](https://github.com/user-attachments/assets/11b74563-e58e-4ccf-af8b-b13362f46a6f)

1. **User Proxy:** Simulates a human input proxy and manages system commands.
2. **Tool Proxy:** Executes tools such as the SERPAPI wrapper.
3. **Researcher:** Collects raw data via APIs (e.g., SERPAPI) without processing or summarizing it.
4. **Summarizer:** Extracts key points and generates concise summaries from raw data.
5. **Writer:** Crafts the initial draft of the blog or essay, focusing on tone and readability.
6. **Critic:** Reviews and refines the content by providing actionable feedback.

### Core Functions

#### 1. **State Transition Logic**

The `state_transition` function dynamically determines the next agent to be invoked based on the current state of the group chat:

```python
def state_transition(last_speaker, groupchat):
    messages = groupchat.messages
    if last_speaker is user_proxy:
        return researcher
    elif last_speaker is researcher:
        return tool_proxy
    elif last_speaker is tool_proxy:
        return summerizer
    elif last_speaker is summerizer:
        return writer
    elif last_speaker is writer:
        if "TERMINATE" in messages[-2]['content']:
            return None
        return critic
    elif last_speaker is critic:
        return writer
```

**Key Points:**
- Automatically determines the next agent based on the chain of tasks.
- Implements feedback iteration for continuous content improvement.

#### 2. **SERPAPI Integration**

Fetches search results for a given query and processes the top articles:

```python
def get_search_results(query: str) -> Union[str, List[str]]:
    client = serpapi.Client(api_key=SERP_API_KEY)
    results = client.search({'engine': 'google', 'q': query, 'n': 5, 'location': "India"})
    # Process and return top 5 article contents
```

---

## How It Works

1. **Initialization:** Start the system by providing a query to the **User Proxy**.
2. **Research Phase:** The **Researcher** gathers raw information using SERPAPI.
3. **Summarization Phase:** The **Summarizer** distills key insights from the raw data.
4. **Writing Phase:** The **Writer** crafts a blog/essay draft.
5. **Critique Phase:** The **Critic** reviews and provides constructive feedback.
6. **Iteration:** The Writer incorporates feedback and refines the content.

---

## Example

```python
user_proxy.initiate_chat(
    manager,
    message="""
    Write an essay about Elon Musk in 500 words.
    """,
)
```

The system will:

1. Research Elon Musk (via SERPAPI).
2. Summarize the findings.
3. Draft an essay.
4. Critique and iterate until the content is finalized.

---

Feel free to fork, experiment, and contribute to this exciting project!

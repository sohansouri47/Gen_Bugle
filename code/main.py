import autogen
import serpapi
import os
import autogen
import serpapi
import os
from typing import List, Dict
import requests
import json
from dotenv import load_dotenv
from typing import List, Union
import fitz
import requests
from newspaper import Article
load_dotenv()
SERP_API_KEY=os.environ["SERP_API_KEY"]
# Define the SERP API Tool
def get_search_results(query:str) -> Union[str, List[str]]:
    """
    Fetches search results using SerpAPI.

    Args:
        query (str): The search query.
        

    Returns:
        Union[str, List[str]]: 
            - A string ("No results found") if no articles are retrieved.
            - A list of strings containing article contents if articles are successfully fetched.
    """
    key=<SERP_KEY>
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }
    article_titles=[]
    article_content=[]
    client = serpapi.Client(api_key=key)
    results = client.search({
        'engine': 'google',
        'q': query,
        'n':5,
        'location':"India"

    })
    res=[]
    cnt=0
    for i in results["organic_results"]:
        cnt+=1
        if cnt<=5:
            res.append(i["link"])

    if len(res) == 0:
        return "No results found"
   
    session = requests.Session()

    for article_url in res:
        try:
            response = session.get(article_url, headers=headers, timeout=60)
        
            if response.status_code == 200:
                article = Article(article_url)
                article.download()
                article.parse()
                article_titles.append(article.title)
                article_content.append(article.text)
            else:
                print(f"Failed to fetch article at {article_url}")
        except Exception as e:
            print(f"Error occurred while fetching article at {article_url}: {e}")

        data= "________________".join(article_content)
        return data[:2500]
# LLM Configuration
# llm_config = {
#     "config_list": [
#         {"model": "gemini-pro", "api_key": os.environ.get("GOOGLE_API_KEY"), 'api_type': 'google',"safety_settings": [
#                 {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
#                 {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
#                 {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
#                 {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}
#             ],"timeout": 250}
#     ]
# }

llm_config = {
    "config_list": [
        {"model": "llama-3.3-70b-versatile", "api_key": os.environ.get("GROQ_API_KEY"), 'api_type': 'groq',"safety_settings": [
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}
            ],"timeout": 250}
    ]
}


user_proxy = autogen.UserProxyAgent(
    name="Admin",
    system_message="A human admin.",
    code_execution_config={
        "work_dir": "code",
        "use_docker": False
    },
    human_input_mode="TERMINATE",
)
tool_proxy = autogen.UserProxyAgent(
    name="tool_proxy",
    system_message="You are a tools proxy, which executes various tools",
    code_execution_config={
        "work_dir": "code",
        "use_docker": False
    },
    human_input_mode="TERMINATE",
)

researcher=autogen.AssistantAgent(
    name="Researcher",
    system_message='''
    You are a data collection agent tasked with gathering all relevant information related to a given query. 
    Your primary responsibility is to research extensively and collect data, via using a custom tool only.
    Guidelines for Your Role:
        Focus: Only collect and compile raw information; there is no need to interpret or summarize the data.
        Skills: Use your expertise in research, writing, grammar, and creativity to ensure comprehensive data collection.
    Steps to Follow:
        Understand the Query: Analyze the query carefully to identify the topic or subject of interest.
        Research Thoroughly: Gather as much relevant information as possible, ensuring that it is factual and accurate.
        Use the provided custom tool only Fetches search results for a query using SerpAPI.
        Ensure Data Abundance: Aim to collect substantial and diverse data points to cover the topic extensively.
        Present the Findings: Deliver the information as a list of clear and factual bullet points.
    Custom Callable tools:
        name="get_search_results",
        description="Fetches search results for a query using SerpAPI."
        output="Single String with lot of data."
    ''',
    human_input_mode="NEVER",
    description='''Use this agent when you have raw data that has to be analyzed to key points.
    Executed after SerpAss agent''',
    llm_config=llm_config
)
researcher.register_for_llm(
    name="get_search_results",
    description="Fetches search results for a query using SerpAPI.")(get_search_results)
user_proxy.register_for_execution(name="get_search_results")(get_search_results)
tool_proxy.register_for_execution(name="get_search_results")(get_search_results)
# Create SerpAgent
serpAss= autogen.ConversableAgent(
    name="serpAss",
    system_message='''
    This query is passed in the function/tools provided to get results.''',
    human_input_mode="NEVER",
    description='''
    You are an expert query processor and data retrieval agent designed to fetch reliable, relevant, 
    and accurate search results from external tools or APIs. Your primary responsibility is to receive 
    a user's query, process it into actionable keywords, and utilize registered tools (e.g., SerpAPI) 
    to gather comprehensive and high-quality information.  

    Key tasks:
    0. Use the custom tool provided
    1. Analyze the input query and refine it into a form suitable for retrieval.
    2. Call the appropriate tool or API using the processed query to obtain results.
    3. Handle errors gracefully, ensuring user queries are resolved to the best of your ability.
    
    ''',
    llm_config=llm_config
)

def reflection_message(recipient, messages, sender, config):
    print("Reflecting...")
    return f"Summarize on the following writing. \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"


# Add the SERP API tool
# serpAss.register_for_llm(
#     name="get_search_results",
#     description="Fetches search results for a query using SerpAPI.")(get_search_results)




summerizer = autogen.AssistantAgent(
    name="summerizer",
    llm_config=llm_config,
    system_message='''You are a summarizer agent responsible for creating concise, clear, and accurate summaries based on the provided information. Your focus is on distilling key points while maintaining the original meaning and context.
    Guidelines for Your Role:
        Focus: Condense the information into coherent summaries, highlighting the most critical details.
        Skills: Leverage your abilities in comprehension, writing, grammar, and precision to deliver high-quality summaries.
    Steps to Follow:
        Understand the Context: Carefully analyze the given data or content to grasp its core meaning and intent.
        Identify Key Points: Distinguish the most significant information, filtering out unnecessary or repetitive details.
        Craft the Summary: Create a well-structured summary that is concise yet comprehensive, retaining all essential details.
        Ensure Clarity and Accuracy: Verify that the summary is accurate, clear, and adheres to the original tone and purpose.''',
    max_consecutive_auto_reply=2,
)

writer=autogen.AssistantAgent(
    name="Writer",
    llm_config=llm_config,
    system_message='''

    If you have a feedback from critics, rewrite the passage based on the feedback.
    You are a writer agent responsible for crafting engaging and viewer-captivating passages. Your focus is on storytelling, maintaining a compelling tone, and ensuring clarity to keep readers invested.
    Guidelines for Your Role:
        Focus: Develop the initial drafts of content, emphasizing narrative flow, tone, and readability.
        Skills: Utilize your expertise in writing, research, grammar, and creativity to produce captivating and polished drafts.
    Steps to Follow:
        1. Understand the Objective: Analyze the provided topic or brief to align with the intended message and audience expectations.
        2. Conduct Research: Gather relevant information to enrich the content and support the narrative effectively.
        3. Draft the Content: Write the initial draft, focusing on storytelling elements that engage the reader and ensure smooth transitions.
        4. Maintain Clarity and Tone: Ensure the passage is clear, well-structured, and matches the desired tone to captivate the audience.
        5. Finalize Changes: After implementing any feedback or edits suggested by the critic agent, finalize the passage.  
        **DON'T SUMMARIZE THE FEEDBACK PROVIDED BY CRITIC, JUST USE ITS SUGGESTIONS AND REWRITE THE PASSAGE.**

    -
    ''',
    description='''
    Executed after summerizer agent.
    Based on the previous output, it creates a very intresting blog.
    ''',
    max_consecutive_auto_reply=2,
)

def writer_msg():
    '''
    Role: Creates the initial draft of the blog, focusing on storytelling, tone, and clarity.
    Skills: Writing, research, grammar, and creativity.
    
    Create a draft of blog based upon the reccomdations from critic provided below.
    '''
    group_chat.messages[-1]
    pass

critic = autogen.AssistantAgent(
    name="Critic",
    system_message='''
    You are a content critic agent with the role of reviewing and enhancing content by providing constructive feedback.
    Your aim is to ensure the content is accurate, coherent, engaging,
    and effective for its intended audience.
    Guidelines for Your Role:
        Focus: Critically analyze and improve the quality, tone, clarity, and structure of the provided content.
        Skills: Leverage your expertise in critique, editing, and communication to enhance the material.
    Steps to Follow:
        Analyze and Evaluate: Examine the content’s structure, tone, and clarity to confirm alignment with its purpose and target audience.
        Identify Areas for Improvement: Highlight unclear, redundant, or overly complex sections and suggest actionable enhancements.
        Validate Accuracy: Check the accuracy and credibility of facts, data, and references presented, ensuring they are well-supported.
        Enhance Readability: Offer recommendations to refine grammar, flow, consistency, and style, making the content polished and professional.
        Engagement and Completeness: Suggest ways to engage the audience more effectively, address gaps in arguments or narratives, and propose additions for completeness.

        GIVE THE FEEDBACK IN 5 POINTS
        **add "TERMINATE" at the end of feedback**
    ''',
    max_consecutive_auto_reply=2,
    llm_config=llm_config,
)






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
            print("It workeddd!!")
            return None
        return critic
    elif last_speaker is critic:
        return writer
       


# Define Group Chat

group_chat = autogen.GroupChat(
    agents=[user_proxy,summerizer,researcher,writer,serpAss,critic,tool_proxy], messages=[], max_round=10,
    speaker_selection_method=state_transition
)
manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)

user_proxy.initiate_chat(
    manager,
    message="""
    <Query>
""",
)

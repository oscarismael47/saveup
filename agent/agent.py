import streamlit as st
from langchain_openai import ChatOpenAI
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.store.base import BaseStore
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt, Command
from pydantic import BaseModel, Field
from typing import List, Optional


MODEL = st.secrets.get("OPENAI_MODEL")
API_KEY = st.secrets.get("OPENAI_KEY")
MODEL = ChatOpenAI(model=MODEL, api_key=API_KEY, temperature=1)


# Chatbot instruction
MODEL_SYSTEM_MESSAGE = """You are a financial assistant chatbot. Your primary goal is to help users create a personalized plan to achieve their financial goals.

**Core Instructions:**

1.  **Information Gathering:** Begin by asking the user for all the necessary information to create their financial plan. You must gather the following details:
    * **Financial Goal** (e.g., "buy a car," "vacation")
    * **Goal Amount** (the total cost of the goal)
    * **Current Savings**
    * **Desired Time Period** (the timeframe to achieve the goal)
    * **Monthly Expenses**
    * **Salary**

2.  **Review and Request:** Check the provided user information. If any of the fields listed above are missing, 
        politely ask the user to provide them before proceeding. Do not generate a plan until all required information is available.

3.  **Plan Generation:** Once you have all the necessary information, call 'generate_financial_plan' tool to generate the financial plan.
        Finally Return a detailed financial plan report


**Current User Financial Information:**
{financial_information}"""

# System Memory Update Instruction
GET_FINANCIAL_INFORMTATION_INSTRUCTION = """ You are an internal system tool responsible for updating the financial user information.
 Your goal is to extract and organize key information from the user's conversation history to personalize future interactions.

**Instructions:**
1.  **Review provided data:** Carefully analyze the `CHAT_HISTORY` and the existing `CURRENT_USER_MEMORY`.
2.  **Identify new information:** Extract any new, factual details about the user, such as:
    * Financial Goal (e.g., "buy a car," "vacation")
    * Goal Amount (the total cost of the goal)
    * Current Savings
    * Desired Time Period (the timeframe to achieve the goal)
    * Monthly Expenses
    * Salary
3.  **Synthesize and update:** Combine the new information with the `CURRENT_USER_MEMORY`. 
        If there are any conflicts, prioritize the most recent information from the chat history.
4.  Based on the chat history below, update the user information

**Important:** Only include information explicitly stated by the user. Do not make assumptions, guesses, or inferences.

**Current Data:**
CURRENT_FINANCIAL_INFORMATION: {financial_information}
CHAT_HISTORY:
"""

GENERATE_FINANCIAL_PLAN_INSTRUCTION = """
Generate a comprehensive, personalized financial plan based on the following user data. 
The plan should be clear, actionable, and easy to understand.

FINANCIAL_INFORMATION: {financial_information}

Your response should be a well-structured plan that includes sections for:
1. A summary of the user's current financial situation.
2. Specific, actionable recommendations for budgeting and cash flow management.
3. Strategies for savings and investment, tailored to their goals (e.g., retirement, home purchase).
4. Advice on managing and paying down debt.
5. A risk assessment and suggestions for building an emergency fund.
6. A clear next steps section.

Ensure the tone is supportive and encouraging.
"""

class FinancialPlan(BaseModel):
    summary: str = Field(..., description="A concise overview of the current financial situation, including income, expenses, assets, liabilities, and overall financial health.")
    budgeting_recommendations: List[str] = Field(..., description="Specific and actionable advice for budgeting, tracking expenses, and managing monthly cash flow.")
    savings_and_investment: List[str] = Field(..., description="Tailored strategies for savings goals (e.g., emergency fund, retirement, home purchase) and investment planning.")
    debt_management: List[str] = Field(..., description="Guidance on reducing, restructuring, or paying down debts effectively.")
    risk_and_emergency: List[str] = Field(..., description="Evaluation of risks (e.g., job loss, unexpected expenses) and recommendations for building an adequate emergency fund.")
    next_steps: List[str] = Field(..., description="Clear, encouraging actions the individual should take next to improve their financial situation.")

def assistant(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """Load memory from the store and use it to personalize the chatbot's response."""
    
    # Get the user ID from the config
    user_id = config["configurable"]["user_id"]

    # Retrieve memory from the store
    namespace = (user_id, "user_information")
    key = "financial_information"
    financial_information = store.get(namespace, key)

    # Extract the actual memory content if it exists and add a prefix
    if financial_information:
        # Value is a dictionary with a memory key
        financial_information_content = financial_information.value.get('financial_information')
    else:
        financial_information_content = "No existing financial information found."

    # Format the memory in the system prompt
    system_msg = MODEL_SYSTEM_MESSAGE.format(financial_information=financial_information_content)
    
    # Respond using memory as well as the chat history
    response = MODEL_WITH_TOOLS.invoke([SystemMessage(content=system_msg)]+state["messages"])

    return {"messages": response}

def extract_write_information(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """Reflect on the chat history and save a memory to the store."""
    
    # Get the user ID from the config
    user_id = config["configurable"]["user_id"]

    # Retrieve existing memory from the store
    namespace = (user_id, "user_information")
    financial_information = store.get(namespace, "financial_information")
        
    # Extract the memory
    if financial_information:
        financial_information_content = financial_information.value.get('financial_information')
    else:
        financial_information_content = "No existing financial information found."

    # Format the memory in the system prompt
    system_msg = GET_FINANCIAL_INFORMTATION_INSTRUCTION.format(financial_information=financial_information_content)
    new_financial_information = MODEL.invoke([SystemMessage(content=system_msg)]+state['messages'])
    key = "financial_information"

    # Write value as a dictionary with a memory key
    store.put(namespace, key, {"financial_information": new_financial_information.content})

def should_continue(state: MessagesState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return "extract"


@tool("generate_financial_plan")
def generate_financial_plan(financial_information: str) -> str:
    """
    Generate a financial plan using the financial user information

    Parameters:
        financial_information (str): The financial user information

    Returns:
        str: financial plan
    """

    response = interrupt({
            "question":("I have gathered enough information to generate your personalized financial plan. "
                        "Please review the details above. Do you agree with this information, or would you like to update any part of it before I proceed?",
                        "ACCEPT, DECLINE, EDIT"),
            "financial_information":financial_information            
            })    
    
    if response in ("accept", "ACCEPT", "yes" ):
        pass
    elif response == "edit":
        pass # To do https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/add-human-in-the-loop/#review-tool-calls
    else:
        raise ValueError(f"Unknown response type: {response['type']}")

    system_msg = GENERATE_FINANCIAL_PLAN_INSTRUCTION.format(financial_information=financial_information)
    financial_plan = MODEL.with_structured_output(FinancialPlan).invoke([SystemMessage(content=system_msg)])

    return financial_plan.model_dump()



def invoke(message, thread_id="1", user_id="1"):
    
    
    config = {"configurable": {"thread_id": thread_id, # We supply a thread ID for short-term (within-thread) memory
                               "user_id": user_id}} # We supply a user ID for long-term (across-thread) memory 

    # The states are returned in reverse chronological order.
    states = list(graph.get_state_history(config))
    
    # get the latest state
    if len(states) > 0:
        last_state = states[0]
        interrupts = last_state.interrupts
    else:
        interrupts = []

    if len(interrupts) > 0:
        user_message = Command(resume=message)
    else:
        user_message = {"messages":  [HumanMessage(content=message)] }

    response = graph.invoke(user_message, config=config)
    
    if "__interrupt__" in response:
        interruption = response["__interrupt__"][0].value
    else:
        interruption = None
    
    return response["messages"], interruption

tools = [generate_financial_plan]
MODEL_WITH_TOOLS = MODEL.bind_tools(tools)
tool_node = ToolNode(tools)

# Define the graph
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", tool_node)
builder.add_node("extract_write_information", extract_write_information)
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    should_continue,
    {"tools": "tools", "extract": "extract_write_information"}
)
builder.add_edge("tools", "assistant")
builder.add_edge("extract_write_information", END)

# Store for long-term (across-thread) memory
across_thread_memory = InMemoryStore()

# Checkpointer for short-term (within-thread) memory
within_thread_memory = MemorySaver()

# Compile the graph with the checkpointer fir and store
graph = builder.compile(checkpointer=within_thread_memory, store=across_thread_memory)

#graph_image = graph.get_graph(xray=True).draw_mermaid_png()
#with open("agent.png", "wb") as f:
#    f.write(graph_image)

if __name__ == "__main__":
    while True:
        user_message = input("You: ")
        if user_message.lower() == "exit":
            break
        
        messages, interruption = invoke(user_message)
        if interruption is not None:
            print("Current financial information: ",  interruption["financial_information"])
            print("Assinstant: ", interruption["question"])
        else:
            print("Assistant:", messages[-1].content)
        #print("Messages:", messages)
        print("-----")
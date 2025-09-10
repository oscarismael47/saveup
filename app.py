import uuid
import pandas as pd
import streamlit as st
from agent.agent import invoke
from file_helper import  generate_pdf_bytes

def update_selection_value(value):
    st.session_state.selection = value


filename="out/financial_plan.pdf"

st.title("SaveUp")

# Sidebar: system message input
with st.sidebar:
    pass

if "user_id" not in st.session_state:
    st.session_state.user_id = "001"  

if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello, How can I help you?", "metadata":{}}]

if "financial_plan" not in st.session_state:
    st.session_state.financial_plan = {}

if "selection" not in st.session_state:
    st.session_state.selection = None


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(name=message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)
        if len(message["metadata"]) > 0:
            if "financial_information" in message["metadata"]:
                df = message["metadata"]["financial_information"]
                st.dataframe(df,width="content", hide_index=True)
            #
            #if "download_pdf_btn" in message["metadata"]:
            #    pdf_buffer = message["metadata"]["download_pdf_btn"]["pdf_buffer"]
            #    st.download_button( label="⬇️ Download PDF",
            #                            data=pdf_buffer,
            #                            file_name="financial_plan.pdf",
            #                            mime="application/pdf")

print("---------------Iteration-----------")
for message in st.session_state.messages:
    print(message)

# Handle new user input
user_message = st.chat_input("What is up?")

if st.session_state.selection is not None:
    user_message = st.session_state.selection
    st.session_state.selection = None

if user_message :


    st.session_state.messages.append({"role": "user", "content": user_message, "metadata":{}})
    with st.chat_message("user"):
        st.markdown(user_message, unsafe_allow_html=True)

    response, interruption = invoke(user_message,
                        thread_id=st.session_state.chat_id,
                        user_id=st.session_state.user_id)
    ai_message =  response["messages"][-1].content
    
    metadata = {}
    if interruption is not None:
        print("interruption")
        financial_information =  interruption["financial_information"]
        interruption_text =  interruption["question"]["text"]
        interruption_options = interruption["question"]["options"]
        ai_message = interruption_text

        # Mapping function
        financial_information = {key.replace("_", " ").title(): str(value) for key, value in financial_information.items()}
        df = pd.DataFrame(list(financial_information.items()), columns=["Field", "Value"])


        with st.chat_message("assistant"):
            st.markdown(ai_message, unsafe_allow_html=True)
            st.dataframe(df,width="content", hide_index=True)
            flex = st.container(horizontal=True, horizontal_alignment="left")
            for option in interruption_options:
                flex.button(option, on_click=update_selection_value, args=(option,),  type="primary")
            metadata = {"financial_information": df}

    else:
        with st.chat_message("assistant"):
            st.markdown(ai_message, unsafe_allow_html=True)
            if "financial_plan" in response:
                financial_plan = response["financial_plan"]
                if financial_plan != st.session_state.financial_plan:
                    st.session_state.financial_plan = financial_plan
                    pdf_buffer = generate_pdf_bytes(st.session_state.financial_plan)
                    st.download_button( label="⬇️ Download PDF",
                                        data=pdf_buffer,
                                        file_name="financial_plan.pdf",
                                        mime="application/pdf")
                    metadata = {"pdf_buffer": pdf_buffer}

    st.session_state.messages.append({"role": "assistant", "content": ai_message, "metadata":metadata})
    #print(ai_message)
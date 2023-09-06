import json
import logging

import openai
import streamlit as st

from config import UUID
from openai_utils import chat_completion_request, extract_insights, functions
from user_props import (
    create_class,
    create_client,
    create_object,
    get_object_properties,
)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

openai.api_key = st.secrets["OPENAI_API_KEY"]

if "messages" not in st.session_state:
    st.session_state.messages = []


@st.cache_resource
def create_user():
    client = create_client()
    create_class(client)
    create_object(client)
    return client


def clear_conversation(client):
    res = extract_insights(client, st.session_state.messages[1:])  # index 0 is system
    st.info(res)
    del st.session_state.messages[:]


def display_user_info(client):
    with st.expander("User info"):
        st.write(get_object_properties(client, UUID))

        if st.button("Clear info"):
            st.cache_resource.clear()


def display_conversation():
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


def main():
    st.set_page_config(
        page_title="Shop Advisor",
        page_icon="👜",
    )

    st.title("Shop Advisor")
    client = create_user()
    display_user_info(client)
    display_conversation()

    st.session_state.messages.append(
        {
            "role": "system",
            "content": f"You're are a highly efficient and knowledgeable shopping assistant. Your goal is to provide exceptional assistance to customers as they navigate a bustling shopping mall. Your expertise in finding the best deals, recommending suitable products, and ensuring a smooth shopping experience is unmatched. You also have the following information about the shopper: {get_object_properties(client, UUID)}",
        }
    )

    if prompt := st.chat_input("What is up?"):
        # add and display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # render api response
        with st.chat_message("assistant"):
            response = chat_completion_request(
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                temperature=0.2,
            ).json()["choices"][0]["message"]["content"]
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

    # if no messages besides system message
    if len(st.session_state.messages) > 1:
        st.button("Clear conversation", on_click=clear_conversation, args=(client,))


if __name__ == "__main__":
    main()

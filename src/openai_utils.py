import json
import logging
from tenacity import retry, stop_after_attempt, wait_random_exponential
import requests
import openai
from config import GPT_MODEL, UUID
from termcolor import colored

from user_props import (
    create_property,
    get_class_properties,
    get_object_properties,
    update_object,
)


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(
    messages, functions=None, function_call=None, temperature=None, model=GPT_MODEL
):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
    }
    json_data = {"model": model, "messages": messages}
    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    if temperature is not None:
        json_data.update({"temperature": temperature})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }

    for message in messages:
        if message["role"] == "system":
            print(
                colored(
                    f"system: {message['content']}\n", role_to_color[message["role"]]
                )
            )
        elif message["role"] == "user":
            print(
                colored(f"user: {message['content']}\n", role_to_color[message["role"]])
            )
        elif message["role"] == "assistant" and message.get("function_call"):
            print(
                colored(
                    f"assistant: {message['function_call']}\n",
                    role_to_color[message["role"]],
                )
            )
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(
                colored(
                    f"assistant: {message['content']}\n", role_to_color[message["role"]]
                )
            )
        elif message["role"] == "function":
            print(
                colored(
                    f"function ({message['name']}): {message['content']}\n",
                    role_to_color[message["role"]],
                )
            )


functions = [
    {
        "name": "create_new_property",
        "description": "Use this function to create a new property.",
        "parameters": {
            "type": "object",
            "properties": {
                "properties": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of user property, has to follow the format /[_A-Za-z][_0-9A-Za-z]/ ",
                            },
                            "value": {
                                "type": "string",
                                "description": "Value of user property",
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of property",
                            },
                            "dataType": {
                                "type": "string",
                                "description": "Data Type of property",
                            },
                        },
                    },
                }
            },
            "required": ["properties"],
        },
    },
]


def add_property(client, res, prop_names):
    try:
        # if property does not exist, create it first
        if res["name"].lower() not in prop_names:
            prop = {
                "name": res["name"],
                "description": res["description"],
                "dataType": [res["dataType"]],
            }
            results = create_property(client, prop)
            logging.info(prop)

        # assign value to property
        data_object = {res["name"]: res["value"]}
        results = update_object(client, data_object)

    except Exception as e:
        results = f"query failed with error: {e}"
    return results


def execute_function_call(client, message):
    results = []
    if message["function_call"]["name"] == "create_new_property":
        prop_names = get_class_properties(client)
        res = json.loads(message["function_call"]["arguments"])["properties"]
        for r in res:
            results.append(add_property(client, r, prop_names))
    else:
        results.append(
            f"Error: function {message['function_call']['name']} does not exist"
        )
    return results


def extract_insights(client, past_convo):
    messages = []
    props_w_values = get_object_properties(client, UUID)
    existing_props = get_class_properties(client, detail=True)

    prompt = f"""
    Your task is to extract insights about the shopper from the conversation history.

    Here are the current existing properties with descriptions: {existing_props}
    Here are properties with assigned values: {props_w_values}

    Please check if a specific property exists for the user. If it doesn't exist, create a new property with the appropriate value using the function 'create_new_property'.

    Fully utilize the conversation history to create new properties if possible. The properties must be relevant to the user's shopping behavior.

    Here are some example attributes:
    - Demographics: Age, gender, and occupation provide insights into users' backgrounds.
    - Location: Local references and city mentions help determine users' geographic preferences.
    - Sustainability Preference: Users' concerns about the environment and sustainability indicate their preference for eco-friendly products.
    - Luxury vs. Value: Brand preferences and price sensitivity hint at users' preference for luxury or value-based shopping.
    - Shopping Behavior: Insights into users' impulse vs. planned purchases and product discovery habits.
    - Influence Sources: The influencers, blogs, or social media platforms users follow for shopping advice.
    - Seasonal Shopping Habits: How users adapt their shopping behavior during different seasons and holidays.
    - Payment Preferences: Insights into users' preferred payment methods and digital wallets.
    - Product Lifecycles: Expectations regarding product durability and lifespan.

    Please ensure that the properties are correctly assigned and updated as needed.
    """

    messages.append({"role": "system", "content": prompt})
    messages.append(
        {
            "role": "user",
            "content": f"Given this chat history {past_convo}, extract insights about the shopper based on the user messages.",
        }
    )
    chat_response = chat_completion_request(
        messages,
        functions=functions,
        function_call={"name": "create_new_property"},
    )

    assistant_message = chat_response.json()["choices"][0]["message"]

    logging.info(assistant_message)

    if assistant_message.get("function_call"):
        results = execute_function_call(client, assistant_message)
        logging.info(results)

    return results

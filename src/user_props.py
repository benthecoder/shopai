import os

import weaviate
from dotenv import load_dotenv

from config import CLASS_NAME, VECTORIZER, UUID
import streamlit as st


def get_env(API_KEY):
    load_dotenv()
    if os.getenv(API_KEY) is not None:
        return os.getenv(API_KEY)
    else:
        raise Exception(f"{API_KEY} not found")


def create_client():
    load_dotenv()
    # WEAVIATE_API_KEY = get_env("WEAVIATE_API_KEY")
    # OPENAI_API_KEY = get_env("OPENAI_API_KEY")

    auth_config = weaviate.AuthApiKey(api_key=st.secrets["WEAVIATE_API_KEY"])

    client = weaviate.Client(
        url="https://shopai-i90k6enj.weaviate.network",
        auth_client_secret=auth_config,
        additional_headers={
            "X-OpenAI-Api-Key": st.secrets["OPENAI_API_KEY"],
        },
    )

    if client.is_ready():
        return client

    raise Exception("Instance not ready")


def create_class(client):
    # Clear up the schema, so that we can recreate it
    client.schema.delete_all()
    client.schema.get()

    user_schema = {
        "class": CLASS_NAME,
        "description": "Information about a shopper on a shopping platform",
        "vectorizer": VECTORIZER,
        "moduleConfig": {
            "text2vec-openai": {"model": "ada", "modelVersion": "002", "type": "text"}
        },
        "properties": [
            {
                "name": "name",
                "description": "Name of the user.",
                "dataType": ["string"],
            },
            {
                "name": "age_range",
                "description": "Inferred age range group from conversation.",
                "dataType": ["string"],
            },
            {
                "name": "gender",
                "description": "Hints about gender from statements.",
                "dataType": ["string"],
            },
            {
                "name": "location",
                "description": "Hints about location from statements.",
                "dataType": ["string"],
            },
            {
                "name": "interests",
                "description": "Hints about interests from statements.",
                "dataType": ["string"],
            },
        ],
    }

    client.schema.create_class(user_schema)


def get_class(client):
    response = client.schema.get(CLASS_NAME)
    return response


def get_class_properties(client, detail=False):
    response = get_class(client)

    if detail:
        output_list = []
        for item in response["properties"]:
            output_list.append(
                {
                    "name": item["name"],
                    "description": item["description"],
                    "datatype": item["dataType"],
                }
            )
        return output_list
    else:
        output_list = []
        for item in response["properties"]:
            output_list.append(item["name"])
        return output_list


def create_object(client):
    data_object = {
        "name": "John Doe",
    }

    uuid = client.data_object.create(
        # hardcode uuid
        uuid=UUID,
        data_object=data_object,
        class_name=CLASS_NAME,
    )

    return uuid


def get_object_properties(client, uuid):
    """Gets current existing properties and it's content"""
    object = client.data_object.get_by_id(
        uuid,
        class_name=CLASS_NAME,
        with_vector=False,
    )

    return object["properties"]


def create_property(client, prop, skip_vectorization=False):
    """
    prop must follow this format:
    prop = {
        "name": "name",
        "description": "Name of the user.",
        "dataType": ["string"],
    }
    """

    if prop["name"] in get_class_properties(client):
        raise Exception("Property already exists")

    prop.update({"moduleConfig": {"text2vec-openai": {"skip": skip_vectorization}}})

    try:
        client.schema.property.create(CLASS_NAME, prop)
    except Exception as e:
        raise Exception(e)

    return f"Property {prop['name']} created"


def update_object(client, data_object):
    for key in data_object.keys():
        if key not in get_class_properties(client):
            raise Exception(
                f"Property {key} does not exist, use create_property to create it first"
            )

    props = get_object_properties(client, UUID)
    data_object.update(props)
    try:
        client.data_object.replace(
            uuid=UUID,
            data_object=data_object,
            class_name=CLASS_NAME,
        )
    except Exception as e:
        raise Exception(e)

    return f"Property {list(data_object.keys())[0]} assigned"


def main():
    client = create_client()
    create_class(client)
    create_object(client)

    print(get_object_properties(client, UUID))

    # add existing
    data_object = {
        "gender": "female",
    }

    update_object(client, data_object)
    print(get_object_properties(client, UUID))

    # create and add

    prop = {
        "name": "onHomePage",
        "description": "If user is on homepage",
        "dataType": ["boolean"],
    }
    create_property(client, prop)

    data_object = {
        "onHomePage": True,
    }

    update_object(client, data_object)
    print(get_object_properties(client, UUID))


if __name__ == "__main__":
    main()

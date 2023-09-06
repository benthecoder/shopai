# Shopper Profile with LLMs

Goal: The goal of this project is to extract valuable insights about a shopper on a e-commerce platform.

Stack:

- [Weaviate](https://weaviate.io/) VectorDB
- OpenAI `gpt-3.5-turbo-16k-0613` function calling
- Streamlit

## User attributes

The insights could be the following attributes:

1. **Demographics**: Age, gender, and occupation provide insights into users' backgrounds.
2. **Location**: Local references and city mentions help determine users' geographic preferences.
3. **Sustainability Preference**: Users' concerns about the environment and sustainability indicate their preference for eco-friendly products.
4. **Luxury vs. Value**: Brand preferences and price sensitivity hint at users' preference for luxury or value-based shopping.
5. **Shopping Behavior**: Insights into users' impulse vs. planned purchases and product discovery habits.
6. **Influence Sources**: The influencers, blogs, or social media platforms users follow for shopping advice.
7. **Seasonal Shopping Habits**: How users adapt their shopping behavior during different seasons and holidays.
8. **Payment Preferences**: Insights into users' preferred payment methods and digital wallets.
9. **Product Lifecycles**: Expectations regarding product durability and lifespan.

## Project Flow

1. Users engage in chat sessions with a bot.
2. Initial session retrieves user context and attributes.
3. Conversations occur over multiple sessions using GPT models.
4. All chat data is collected, including user input and bot responses.
5. Chat data is processed with GPT models to generate insights-rich text.
6. Insights related to demographics, location, and preferences are extracted.
7. Extracted insights are stored in Weaviate, associated with the user's ID, creating a structured knowledge graph.

This project facilitates understanding and utilizing valuable shopper information from chat interactions on the e-commerce platform.

## TODO

- [x] Weaviate intergration
  - [x] create class and object of a user
  - [x] Get properties of the object
  - [x] Add properties of the object
- [x] LLM
  - [x] Find out best way to add context to create completion (system or assistant message)
  - [x] Given conversation history, and current properties, write function that extracts insights, outcome is update property or create new one
- [x] chat
  - [x] on each new conversation, read in context about user
  - [x] on each session end, load in property to db
- [x] improve prompt
  - [x] have it create new property
  - [ ] have it create properties that are related to user.

## References

Weaviate

- [classes and objects operations](https://weaviate.io/developers/weaviate/manage-data)
- [Adding a property](https://weaviate.io/developers/weaviate/api/rest/schema#example-request-for-adding-a-property)

OpenAI

- return multiple objects in function calling [forum](https://community.openai.com/t/function-calling-return-multiple-objects/282989)

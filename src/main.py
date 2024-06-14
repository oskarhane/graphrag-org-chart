from neo4j import GraphDatabase
from neo4j_genai import Text2CypherRetriever
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from openai_chat_wrapper import Text2CypherOpenAIChatWrapper
from rewriter import Rewriter
import logging
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEO4J_URL = os.getenv("NEO4J_URL")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# logger = logging.getLogger("neo4j_genai")
# logging.basicConfig(format="%(asctime)s - %(message)s")
# logger.setLevel(logging.DEBUG)

def main(user_input = None):
    with GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        existing_data = []
        llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-4o")
        retriver = Text2CypherRetriever(driver, Text2CypherOpenAIChatWrapper(llm))
        rw = Rewriter(llm)
        while True:
            question = rw.rewrite(user_input, existing_data[-5:])
            result, _ = retriver.search(question)
            generation_messages = [
                {"role": "system", "content": "You're a helpful assistant that answers questions by only using the information provided to you. If there's no answer to the question provided, you say just that there is no answer available. Do not use any of your implicit knowledge. Answer with a relaxed surfer tone and attitude."},
                {"role": "assistant", "content": f"Here's a history of user exchanged messages and ansers to give you some extra context: {[f'{x[0]}: {x[1]}' for x in existing_data]}"},
                {"role": "assistant", "content": f"The information retrieved to respond to the user input is: '''{result}'''"},
                {"role": "user", "content": f"The user input: '''\n{question}\n''''"},
            ]
            response = llm.invoke(generation_messages)
            print(f"🏄‍♀️: {response.content}\n")
            existing_data.append((question, response.content))
            user_input = input("Anything else you want to ask about the Engineering org?\n🗣️ -> ")



if __name__ == "__main__":
    print("\n\n======== GraphRAG via text2cypher ========")
    print("\n")
    print("Press Ctrl+c to exit at any time.")
    print("\n\n")
    user_input = input("What do you want to ask about the Engineering org?\n🗣️ -> ")
    main(user_input)

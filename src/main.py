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
            result = retriver.search(question, examples=[
                "Who is the manager of team X?\nMATCH (team:Team)<-[:MEMBER_OF]-(:Person)<-[:MANAGES]-(m:Manager) WHERE toLower(team.name) = toLower('X') RETURN DISTINCT m.name AS teamManager, team.name AS teamName", 
                "Who are the managers of the team that XYZ works in?\nMATCH (person:Person)-[:MEMBER_OF]->(:Team)<-[:MEMBER_OF]-(:Person)<-[:MANAGES]-(m:Manager) WHERE toLower(person.name) = toLower('XYZ') RETURN DISTINCT m.name AS teamManagers, person.name AS personName", 
                "What is the name of the team that has the most members?\nMATCH (t:Team)<-[:MEMBER_OF]-(m:Member) RETURN t.name AS teamName ORDER BY COUNT(m) DESC LIMIT 1", 
                "Who is AAA managing?\n(m:Manager)-[:MANAGES]->(p:Person) WHERE toLower(m.name) = toLower('AAA') RETURN p.name as managedPerson, m.name as theManager", 
                "Who is AAA's manager?\n(m:Manager)-[:MANAGES]->(p:Person) WHERE toLower(p.name) = toLower('AAA') RETURN m.name as theManager, p.name as thePerson", 
                ])
            result_list = ", ".join(list(map(lambda item: item.content, result.items)))
            generation_messages = [
                {"role": "system", "content": "You're a helpful assistant that answers questions by only using the information provided to you. If there's no answer to the question provided, you say just that there is no answer available. Do not use any of your implicit knowledge. Answer with a relaxed surfer tone and attitude, but don't repeat ending phrases."},
                {"role": "assistant", "content": f"Here's a history of user exchanged messages and ansers to give you some extra context: {[f'{x[0]}: {x[1]}' for x in existing_data]}"},
                {"role": "assistant", "content": f"The information retrieved to respond to the user input is. If there is anything here it is relevant to the question. '''{result_list}'''"},
                {"role": "user", "content": f"The user input: '''\n{question}\n''''"},
            ]
            
            response = llm.invoke(generation_messages)
            print(f"🏄‍♀️: {response.content}\n")
            existing_data.append((question, response.content))
            user_input = input("\n🗣️ -> ")



if __name__ == "__main__":
    print("\n\n======== GraphRAG via text2cypher ========")
    print("\n")
    print("Press Ctrl+c to exit at any time.")
    print("\n\n")
    user_input = input("What do you want to ask about the Engineering org?\n🗣️ -> ")
    main(user_input)

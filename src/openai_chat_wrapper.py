from neo4j_genai.llm import LLM
import json

class Text2CypherOpenAIChatWrapper(LLM):
    """
    The purpose of this wrapper is to make Langchain Chat models compatible with the Text2CypherRetriever.
    One additional method is added to the LLM class, reflect, which is used to reflect the output of the model back to the user to improve quality.
    """
    def __init__(self, llm):
        self.llm = llm
    def invoke(self, input) -> str:
        response = self.llm.invoke(input)
        reflected = self.reflect(input, response.content)
        return reflected

    def reflect(self, input, cypher, extra_messages=None):
        messages = [
            {"role": "system", "content": "You are a Cypher Query language expert. Your job is to review queries and make sure they are correct. You are given an original prompt and your job is to see if the query generated from that prompt is correct or not."},
            {"role": "assistant", "content": f"The original prompt is: '''\n{input}\n''''."},
            {"role": "assistant", "content": f"The already generated Cypher query is: '{cypher}'."},
            {"role": "assistant", "content": f"If the Cypher has any filters that might be too narrow, widen them. Match string case insensitive."},
            {"role": "user", "content": "Please provide the correct Cypher query to correct any issues. Make sure it still finds the answer to the original question."},
            {"role": "user", "content": 'Respond in the following JSON format: {"query":"..."}'},
        ]
        if extra_messages:
            messages += extra_messages

        response = self.llm.invoke(messages, {
            "response_format": {"type": "json_object"},
        })
        try:
            parsed_response = json.loads(response.content)
        except:
            print("Error parsing JSON response, retrying...")
            return self.reflect(input, cypher, [{"role":"assistant", "content": "Output only valid JSON, nothing else. Try again."}])
        return parsed_response["query"]

class Rewriter:
    def __init__(self, llm):
        self.llm = llm

    def rewrite(self, question, context_messages = []):
        messages = [
            {"role": "system", "content":"You're an expert at understanding user intent and rewriting user input and questions to make them clear, concise and atomic by using addtional context provided. make every part of the question specific using the provided context."},
            {"role": "assistant", "content": f"The context messages are: {[f'{x[0]}: {x[1]}' for x in context_messages]}"},
            {"role": "assistant", "content": f"If the context messages aren't helpful, ignore them and leave the original question as is."},
            {"role": "assistant", "content": f"The last user input is: '''\n{question}\n''''."},
            {"role": "user", "content": "Please provide the rewritten question: "},
        ]
        response = self.llm.invoke(messages)
        return response.content

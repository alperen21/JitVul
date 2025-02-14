from langchain_openai import ChatOpenAI

class Agent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    def chat(self, text):
        return self.llm.invoke(text).content
    
    def find_other_version(self, function_body, file_content):
        prompt = f"""
        You are given a function body and a file content. 
        You need to find the function in the file content that is similar to the given function body.
        
        Only reply with the function body and nothing else
        
        Function body:
        {function_body}
        
        File content:
        {file_content}
        """
        
        response = self.chat(prompt)
        return response.replace("```", "").replace("```c", "")
    
    def extract_function(self, text, function_name):
        prompt = f"""
        You are given a code snippet. You need to extract the function from the code snippet.
        
        Only reply with the function body and nothing else
        
        Function:
        {function_name}
        
        Code snippet:
        {text}
        
        If the function is not found, reply with "#NOT_FOUND#" and nothing else
        """
        
        response = self.chat(prompt)
        return response.replace("```", "").replace("```c", "")
    
if __name__ == '__main__':
    agent = Agent()
    print(agent.chat("What is the best way to fix a vulnerability in a codebase?"))
from langchain.agents import initialize_agent, AgentType

class Agent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools 
        
        self.agent = initialize_agent(
            tools=tools,  # List of tools the agent can use
            llm=llm,  # The language model
            agent_type=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # Choose the type of agent
            verbose=True,  # Whether to print out the intermediate steps,
            handle_parsing_errors=True
        )
        

        
    def predict(self, input_text):
        response = self.agent.invoke(input_text)
        
        vulnerability_prediction = None 
        cwe_prediction = None
        if "@@vulnerable@@" in response["output"].lower():
            print('vulnerable')
            vulnerability_prediction = 1
        else:
            print('not vulnerable')
            vulnerability_prediction = 0
            
            
        print(f'Vulnerability prediction: {vulnerability_prediction}')
        if "@@CWE:" in response["output"]:
            start_index = response["output"].index("@@CWE:") + len("@@CWE: ")
            end_index = response["output"].index("@@", start_index)
            cwe_prediction = response["output"][start_index:end_index].strip()
            print(f'CWE detected: {cwe_prediction}')
        else:
            print('No CWE detected')
            cwe_prediction = ""
            
        
        
        return (vulnerability_prediction, cwe_prediction)



class BaselineAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def predict(self, input_text):
        response = self.llm(input_text).content
        print(response)
        
        vulnerability_prediction = None 
        cwe_prediction = None
        
        if "@@vulnerable@@" in response.lower():
            print('vulnerable')
            vulnerability_prediction = 1
        else:
            print('not vulnerable')
            vulnerability_prediction = 0
            
            
        print(f'Vulnerability prediction: {vulnerability_prediction}')
        if "@@CWE:" in response:
            start_index = response.index("@@CWE:") + len("@@CWE: ")
            end_index = response.index("@@", start_index)
            cwe_prediction = response[start_index:end_index].strip()
            print(f'CWE detected: {cwe_prediction}')
        else:
            print('No CWE detected')
            cwe_prediction = ""
            
        
        
        return (vulnerability_prediction, cwe_prediction)
    
    def chat(self, input_text):
        return self.llm(input_text).content


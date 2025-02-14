from langchain_core.tools import tool
from langchain.tools import Tool
import json
import session


def load_json_file(file_path: str) -> dict:
    """
    Loads a JSON file and returns its contents as a dictionary.

    Parameters:
        file_path (str): The path to the JSON file to be loaded.
    Returns:
        dict: The contents of the JSON file as a dictionary.
    Example:
        >>> data = load_json_file('/path/to/file.json')
        >>> print(data)
        {'key': 'value'}
    """
    with open(file_path, 'r') as file:
        return json.load(file)

def get_call_graph():
    current_session = load_json_file("current_session.json")
    call_graph_file = current_session["call_graph_file"]
    call_graph = load_json_file(call_graph_file)
    
    return call_graph

def get_function_bodies():
    current_session = load_json_file("current_session.json")
    function_body_file = current_session["function_body_file"]
    function_bodies = load_json_file(function_body_file)
    
    return function_bodies

@tool
def get_callers(function_name : str) -> list:
    """
    Returns the list of functions that call the given function.

    Parameters:
        function_name (str): The name of the function to find callers for.
    Returns:
        list[str]: A list of function names that call the given function.
    Example:
        >>> callers = get_callers('my_function')
        >>> print(callers)
        ['caller_function1', 'caller_function2']
    """
    # call_graph = get_call_graph()
    
    # if function_name not in call_graph:
    #     print(f"Function {function_name} not found in call graph.")
    #     return []
    # else:
    #     return call_graph[function_name]["callers"]
    
    caller_graph = session.caller_graph
    return caller_graph.get(function_name, [])
    

@tool
def get_callees(function_name : str) -> list:
    """
    Returns the list of functions that call the given function.

    Parameters:
        function_name (str): The name of the function to find callers for.
    Returns:
        list[str]: A list of function names that call are called in the given function.
    Example:
        >>> callees = get_callees('my_function')
        >>> print(callees)
        ['callee_function1', 'callee_function2']
    """
    # call_graph = get_call_graph()
    
    # if function_name not in call_graph:
    #     print(f"Function {function_name} not found in call graph.")
    #     return []
    # else:
    #     return call_graph[function_name]["callers"]
    caller_graph = session.caller_graph
    return caller_graph.get(function_name, [])
    



@tool
def get_function_body(function_name : str) -> str:
    """
    Retrieves the body of a function as a string.
        Args:
            function_name (str): The name of the function whose body is to be retrieved.
        Returns:
            str: A string representing the function body.
        Example:
            >>> body = get_function_body('my_function')
            >>> print(body)
            def my_function():
                # function body
                pass
    """ 
    
    # function_bodies = get_function_bodies()
    # if function_name not in function_bodies:
    #     print(f"Function {function_name} not found in call graph.")
    #     return []
    # else:
    #     return function_bodies[function_name.replace("'","").strip()]["function_body"]
    
    function_bodies = session.function_bodies
    return function_bodies.get(function_name, "")
    
    
    


REACT_TOOLS = [
    Tool(
        name="get_callers",
        func=get_callers,
        description=(
            """
            Returns the list of functions that call the given function.

            Parameters:
                function_name (str): The name of the function to find callers for.
            Returns:
                list[str]: A list of function names that call the given function.
            Example:
                >>> callers = get_callers('my_function')
                >>> print(callers)
                ['caller_function1', 'caller_function2']
            """
        )
    ),
    
    
    
    Tool(
        name="get_function_body",
        func=get_function_body,
        description=(
            """
            Retrieves the body of a function as a string.
                Args:
                    function_name (str): The name of the function whose body is to be retrieved.
                Returns:
                    str: A string representing the function body.
                Example:
                    >>> body = get_function_body('my_function')
                    >>> print(body)
                    def my_function():
                        # function body
                        pass
            """ 
        )
    ),
    
    Tool(
        name="get_callees",
        func=get_callees,
        description=(
"""
    Returns the list of functions that call the given function.

    Parameters:
        function_name (str): The name of the function to find callers for.
    Returns:
        list[str]: A list of function names that call are called in the given function.
    Example:
        >>> callees = get_callees('my_function')
        >>> print(callees)
        ['callee_function1', 'callee_function2']
    """
        )
    )
]
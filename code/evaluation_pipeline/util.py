import json
import os
import session 

def create_session(callee_graph, caller_graph, function_bodies):
    # call_graph_file = os.path.join(".", "call_graph", f"{project}_{commit_id}_call_graph.json")
    # function_body_file = os.path.join(".", "function_bodies", f"{project}_{commit_id}function_bodies.json")
    # object = {
    #         "project": project,
    #         "commit_id": commit_id,
    #         "call_graph_file" : call_graph_file,
    #         "function_body_file" : function_body_file
    #     }
    # with open('current_session.json', 'w') as file:
    #     file.write(json.dumps(object))
    
    session.callee_graph = callee_graph
    session.caller_graph = caller_graph 
    session.function_bodies = function_bodies
        

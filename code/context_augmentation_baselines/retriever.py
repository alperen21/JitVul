import os
from tree_sitter import Parser
from tree_sitter_languages import get_parser
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from tqdm import tqdm
from langchain_openai import ChatOpenAI
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo


class Chunker:
    def __init__(self):
        self.__parsers = {
        '.py': get_parser('python'),
        '.js': get_parser('javascript'),
        '.java': get_parser('java'),
        '.cpp': get_parser('cpp'),
        '.c': get_parser('c'),
        '.h': get_parser('c'),
        '.cs': get_parser('c_sharp'),
    }
        
        
    def __get_all_files(self, repo_path):
        file_paths = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                file_paths.append(os.path.join(root, file))
        return file_paths
    
    def __is_code_file(self, file_path):
        return os.path.splitext(file_path)[1] in self.__parsers
    
    def __extract_chunks(self, file_path):
        
        ext = os.path.splitext(file_path)[1]
        parser = self.__parsers[ext]
        
        with open(file_path, 'rb') as f:
            content = f.read()
            
        tree = parser.parse(content)

        chunks = []
        cursor = tree.walk()
        stack = [cursor.node]
        

        while stack:
            node = stack.pop()
            if node.is_named:
                # Customize the node types to extract
                if node.type in ('function_definition', 'class_definition', 'method_definition'):
                    start_byte = node.start_byte
                    end_byte = node.end_byte
                    chunks.append(content[start_byte:end_byte])
                else:
                    stack.extend(node.children)
        return chunks
    


    def read_and_parse_documents(self, repo_path):
        code_files = [
            f for f in self.__get_all_files(repo_path) if self.__is_code_file(f)
        ]
        documents = []
        
        for file_path in code_files:
                chunks = self.__extract_chunks(file_path)
                
                for chunk in chunks:
                    doc = Document(
                        page_content=chunk.decode('utf-8', errors='replace'),
                        metadata={'source': file_path}
                    )
                    documents.append(doc)
        
        return documents


class VectorDatabaseGenerator:
    def __init__(self, project_path):
        self.project_path = project_path
        self.vector_database_path = os.path.join(self.project_path, "mydatabase")
        self.__embeddings = OpenAIEmbeddings()
        self.chunker = Chunker()
        
    def check_if_db_exists(self):
        return os.path.exists(self.vector_database_path)
    
    def generate(self):
        print("generating the vector database")
        documents = self.chunker.read_and_parse_documents(self.project_path)

        batch_size = 5000
        # Split documents into batches of 5000
        batches = [documents[i:i + batch_size] for i in range(0, len(documents), batch_size)]
        
        vectorstore = None
        for batch in tqdm(batches):
            if vectorstore == None:
                vectorstore = Chroma.from_documents(batch, self.__embeddings, persist_directory=self.vector_database_path)
            else:
                vectorstore.add_documents(batch)
        return vectorstore
    
    def load(self):
        print("loading the vector database")
        return Chroma(persist_directory=self.vector_database_path, embedding_function=self.__embeddings)

class Retriever:
    def __init__(self, vectorstore) -> None:
        self.__vectorstore = vectorstore
        self.__embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        metadata_field_info = [
            AttributeInfo(
                name="source",
                description="file path of the implementation",
                type="string or list[string]",
            ),
        ]
        self.retriever = SelfQueryRetriever.from_llm(
            self.llm, self.__vectorstore, "a code repository", metadata_field_info, verbose=True)
    
    def retrieve(self, query):
        retrieval = self.retriever.invoke(query)
        
        return [document.page_content for document in retrieval]
        

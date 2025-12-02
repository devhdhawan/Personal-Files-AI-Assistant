import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Personal Files AI Assistant")

# Wrapper class to make LangChain embeddings compatible with ChromaDB
class ChromaDBEmbeddingWrapper:
    def __init__(self, langchain_embeddings):
        self.embeddings = langchain_embeddings
    
    def __call__(self, input):
        return self.embeddings.embed_documents(input)
    
    def name(self):
        return "google-generative-ai"

# Setup
load_dotenv()
# os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
# langchain_embeddings = GoogleGenerativeAIEmbeddings(model="gemini-2.5-flash")
# embeddings = ChromaDBEmbeddingWrapper(langchain_embeddings)
client = chromadb.PersistentClient(path="./chroma_db")  # Persist for FastAPI
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

# Load & chunk files
folder_path = "data"  # Your tech docs folder
files = ['data/'+f for f in os.listdir(folder_path) 
              if os.path.isfile(os.path.join(folder_path, f))]

sources = [f.split('.')[0] for f in os.listdir(folder_path) 
              if os.path.isfile(os.path.join(folder_path, f))]

doc_lst = [f.split('.')[0]+'_docs' for f in os.listdir(folder_path) 
              if os.path.isfile(os.path.join(folder_path, f))]

allowed_terms = [f.split('.')[0] for f in os.listdir(folder_path) 
              if os.path.isfile(os.path.join(folder_path, f))]
print(doc_lst)
def add_doc_to_chroma():
    
    for file_path, source in zip(files, sources):
        with open(file_path, "r") as f:
            text = f.read()

        chunks = splitter.split_text(text)
        docs = chunks
        # docs = [chunk.page_content for chunk in chunks]
        metas = [{"source": source, "chunk": i} for i in range(len(chunks))]
        ids = [f"{source}_{i}" for i in range(len(chunks))]
        collection = client.get_or_create_collection(
            name=f"{source}_docs"
        )
        collection.add(documents=docs, metadatas=metas, ids=ids)

# Test multi-collection query_
@mcp.tool()
async def search_document(query: str):
    """
    Search the knowledge base for relevant documents.
    Restrict to queries about your stored tech topics.
    """
    allowed_terms = ["python", "java", "sql", "pyspark", "kafka"]
    q_lower = query.lower()

    # 1) Hard restriction: if query is not about your topics, return empty
    # if not any(term in q_lower for term in allowed_terms):
    #     print("[search_document] blocked query:", query)
    #     return {"documents": [], "ids": [], "distances": []}

    doc_lst = ["python_docs", "java_docs", "sql_docs", "pyspark_docs", "kafka_docs"]
    distance = -1
    final_res = {}

    # 2) Normal multi-collection search
    for doc in doc_lst:
        results = client.get_collection(doc).query(
            query_texts=[query],
            n_results=1,
        )

        if distance == -1 or distance > results["distances"][0]:
            distance = results["distances"][0]
            final_res = results

    return final_res


if __name__ == "__main__":
    print("searchdocument called with:", query)
    # add_doc_to_chroma()
    mcp.run(transport="stdio")
    print("exit")
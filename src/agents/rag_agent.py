from typing import List, Dict
import os

from langchain_chroma import Chroma 
from langchain.schema import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.caches import InMemoryCache
from langchain.globals import set_llm_cache
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from src.core import BaseAgent


class RAGAgent(BaseAgent):
    def __init__(self, config: dict):
        super().__init__(config)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=config['google_api_key']
        )
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=config['google_api_key'],
            temperature=0.7
        )
        self.vector_store = None
        self.cache = InMemoryCache()
        set_llm_cache(self.cache)
        
        self._initialize_vector_store()
        self._setup_chain()

    def _setup_chain(self):
        self.response_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""Using the following context, answer the question. 
    If you cannot answer from the context, say so.

    Context: {context}
    Question: {question}
    Answer:"""
        )
        self.chain = (
            {"context": RunnablePassthrough(), "question": RunnablePassthrough()} 
            | self.response_prompt 
            | self.llm
        )

    def _initialize_vector_store(self):
        """Initialize vector store with proper validation"""
        persist_directory = os.path.join("data", "vector_store", "chroma_db")
        os.makedirs(persist_directory, exist_ok=True)
        
        # Create an empty document with placeholder content
        placeholder_doc = Document(
            page_content="Initial document for vector store initialization",
            metadata={"source": "initialization"}
        )
        
        try:
            # Try to load existing store
            self.vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings,
                collection_name="my_collection"
            )
        except Exception:
            # Initialize with placeholder if loading fails
            self.vector_store = Chroma.from_documents(
                documents=[placeholder_doc],
                embedding=self.embeddings,
                persist_directory=persist_directory,
                collection_name="my_collection"
            )
            self.vector_store.persist()

    def _generate_response(self, query: str) -> str:
        """Implementation of abstract method from BaseAgent"""
        if not self.vector_store:
            return "Knowledge base is empty. Please add documents first."

        # Retrieve similar documents from the vector store
        docs = self.vector_store.similarity_search(query, k=3)
        context = "\n".join(doc.page_content for doc in docs)
        
        # Store interaction metadata
        if hasattr(self, 'conversation_manager'):
            self.conversation_manager.store_interaction({
                'query': query,
                'retrieved_docs': len(docs),
                'context_length': len(context)
            })
        
        # Generate and return the answer using the new chain format
        response = self.chain.invoke({"context": context, "question": query})
        return response.content

    def add_documents(self, documents: List[str], metadata: List[Dict] = None):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=100
        )
        
        docs = []
        for i, doc in enumerate(documents):
            # Skip empty documents
            if not doc.strip():
                continue
            splits = splitter.split_text(doc)
            meta = metadata[i] if metadata and i < len(metadata) else {}
            # Filter out empty splits
            valid_splits = [split for split in splits if split.strip()]
            docs.extend([Document(page_content=split, metadata=meta) for split in valid_splits])

        if not docs:
            raise ValueError("No valid document chunks found to add.")
        
        if not self.vector_store:
            raise ValueError("Vector store is not initialized.")
        else:
            self.vector_store.add_documents(docs)
        
        self._save_vector_store()

    def _save_vector_store(self):
        # Persist the updated Chroma vector store
        self.vector_store.persist()

    def clear_cache(self):
        self.cache.clear()


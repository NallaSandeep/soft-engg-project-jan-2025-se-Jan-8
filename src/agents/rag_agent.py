from typing import List, Dict, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from src.core import BaseAgent
import pickle
import os

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
        self.chain = LLMChain(llm=self.llm, prompt=self.response_prompt)

    def _initialize_vector_store(self):
        vector_store_path = os.path.join("data", "vector_store", "vector_store.pkl")
        os.makedirs(os.path.dirname(vector_store_path), exist_ok=True)
        
        if os.path.exists(vector_store_path):
            with open(vector_store_path, "rb") as f:
                self.vector_store = pickle.load(f)
        else:
            self.vector_store = FAISS.from_documents(
                documents=[],
                embedding=self.embeddings
            )

    def _generate_response(self, query: str) -> str:
        """Implementation of abstract method from BaseAgent"""
        if not self.vector_store:
            return "Knowledge base is empty. Please add documents first."

        docs = self.vector_store.similarity_search(query, k=3)
        context = "\n".join(doc.page_content for doc in docs)
        
        # Store interaction metadata
        self.conversation_manager.store_interaction({
            'query': query,
            'retrieved_docs': len(docs),
            'context_length': len(context)
        })
        
        return self.chain.run(context=context, question=query)

    def add_documents(self, documents: List[str], metadata: List[Dict] = None):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        docs = []
        for i, doc in enumerate(documents):
            splits = splitter.split_text(doc)
            meta = metadata[i] if metadata else {}
            docs.extend([Document(page_content=split, metadata=meta) for split in splits])

        if not self.vector_store:
            self.vector_store = FAISS.from_documents(docs, self.embeddings)
        else:
            self.vector_store.add_documents(docs)
        
        self._save_vector_store()

    def _save_vector_store(self):
        vector_store_path = os.path.join("data", "vector_store", "vector_store.pkl")
        with open(vector_store_path, "wb") as f:
            pickle.dump(self.vector_store, f)

    def clear_cache(self):
        self.cache.clear()
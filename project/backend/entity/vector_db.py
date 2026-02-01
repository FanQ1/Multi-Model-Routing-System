from settings import Settings
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer 
import torch


# 从 settings 中获取 QDRANT_URL
QDRANT_URL = Settings().get_qdrant_url()

qdrant_client = QdrantClient(url=QDRANT_URL)

class VectorDB:
    def __init__(self):
        self.client = qdrant_client

        # embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_model.eval()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.embedding_model.to(device)

    def add_memory(self, content):
        """
        Add a new memory to the vector database.
        :param content: The content of the memory
        """
        vector = self.get_offline_embedding(content)
        point = {
            "id": None,  # Let Qdrant auto-generate ID
            "vector": vector,
            "payload": {"content": content}
        }
        self.upsert_vectors(
            collection_name="long_term_memory",
            points=[point]
        )

    def update_memory(self, content, point_id):
        """
        Update an existing memory in the vector database.
        :param content: The updated content of the memory
        :param point_id: The ID of the memory to update
        """
        vector = self.get_offline_embedding(content)
        point = {
            "id": point_id,
            "vector": vector,
            "payload": {"content": content}
        }
        self.upsert_vectors(
            collection_name="long_term_memory",
            points=[point]
        )

    def delete_memory(self, point_id):
        """
        Delete a memory from the vector database.
        :param point_id: The ID of the memory to delete
        """
        self.client.delete(
            collection_name="long_term_memory",
            points=[point_id]
        )
        print(f"Deleted memory with ID: {point_id}")


    def retrieve_memory(self, collection_name, query, top_k=5):
        """
        Search for similar vectors in the specified collection.
        
        """
        vector = self.get_offline_embedding(query)
        results = self.client.query_points(
            collection_name=collection_name,
            query=vector.tolist(),
            limit=top_k
        )
        return results
    
    def get_offline_embedding(self, query):
        try:
            response = self.embedding_model.encode(
                query, 
                convert_to_tensor=True,
                show_progress_bar=False 
            )
            return response
        except Exception as e:
            raise e

vector_orm = VectorDB()
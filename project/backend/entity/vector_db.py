from settings import Settings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer 
import torch
from logger import logger

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
        self.init_collection(
            collection_name="long_term_memory",
            vector_size=384  # all-MiniLM-L6-v2, vector's dimension is 384
        )

    # ======== collection operations ========
    def init_collection(self, collection_name, vector_size):

        """
        Initialize a collection in Qdrant if it does not exist.
        :param collection_name: Name of the collection
        :param vector_size: Size of the embedding vectors
        """
        if not self.is_collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            logger.info(f"Collection '{collection_name}' created with vector size {vector_size}.")
        else:
            logger.info(f"Collection '{collection_name}' already exists.")

    def is_collection_exists(self, collection_name) -> bool:
        """
        Check if a collection exists in Qdrant.
        :param collection_name: Name of the collection
        :return: True if exists, False otherwise
        """
        collections = self.client.get_collections().collections
        return any(col.name == collection_name for col in collections)
    
    # ======== vector operations ========
    def upsert_vectors(self, collection_name, points):
        """
        Upsert vectors into the specified collection.
        :param collection_name: Name of the collection
        :param points: List of points to upsert, each point is a dict with 'id', 'vector', and 'payload'
        """
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )
        logger.info(f"Upserted {len(points)} vectors into collection '{collection_name}'.")
    
    # ======== memory operations ========
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
        try:
            results = self.client.query_points(
                collection_name=collection_name,
                query=vector.tolist(),
                limit=top_k
            )
        except Exception as e:
            print("Error retrieving memory:", e)
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
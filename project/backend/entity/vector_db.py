# file: backend/entity/vector_db.py
from ..settings import Settings
from qdrant_client import QdrantClient


# 从 settings 中获取 QDRANT_URL
QDRANT_URL = Settings().get_qdrant_url()

# 创建 Qdrant 客户端（单例模式）
qdrant_client = QdrantClient(url=QDRANT_URL)

class VectorDB:
    def __init__(self):
        self.client = qdrant_client

    def upsert_vectors(self, collection_name, points):
        """
        Upsert vectors into the specified collection.
        :param collection_name: Name of the collection
        :param points: List of points to upsert
        """
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )

    def search_vectors(self, collection_name, vector, top_k=5):
        """
        Search for similar vectors in the specified collection.
        :param collection_name: Name of the collection
        :param vector: The query vector
        :param top_k: Number of top similar vectors to return
        :return: List of search results
        """
        results = self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=top_k
        )
        return results

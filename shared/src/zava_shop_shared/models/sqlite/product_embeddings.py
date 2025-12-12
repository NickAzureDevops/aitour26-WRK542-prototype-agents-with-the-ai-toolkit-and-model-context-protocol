"""
Product embedding models for SQLite
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from .base import Base


class ProductImageEmbedding(Base):
    """Stores image embeddings for products as JSON strings"""

    __tablename__ = "product_image_embeddings"

    product_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)
    image_embedding = Column(Text, nullable=False)  # JSON string of embedding vector
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])

    def __repr__(self):
        return f"<ProductImageEmbedding(product_id={self.product_id})>"


class ProductDescriptionEmbedding(Base):
    """Stores description embeddings for products as JSON strings"""

    __tablename__ = "product_description_embeddings"

    product_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)
    description_embedding = Column(Text, nullable=False)  # JSON string of embedding vector
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])

    def __repr__(self):
        return f"<ProductDescriptionEmbedding(product_id={self.product_id})>"

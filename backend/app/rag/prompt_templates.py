GROUNDED_ANSWER_TEMPLATE = """Draft support only for pharmacist review.

Question:
{question}

Retrieved context:
{context}

TODO: Generate an answer using only retrieved context, include citations, and
refuse unsupported claims.
"""

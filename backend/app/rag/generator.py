from app.rag.chunker import DocumentChunk
from app.rag.prompt_templates import GROUNDED_ANSWER_TEMPLATE


def generate_grounded_answer(question: str, context_chunks: list[DocumentChunk]) -> str:
    """Return a placeholder grounded answer.

    TODO: Replace with an approved generation model and strict citation checks.
    """
    context = "\n\n".join(chunk.text for chunk in context_chunks)
    if not context:
        return (
            "No grounded context was retrieved. Do not answer from memory; "
            "ask the pharmacist to verify trusted references."
        )

    return GROUNDED_ANSWER_TEMPLATE.format(question=question, context=context)

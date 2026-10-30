from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from minimal_rag.retriever import fetch_documents

load_dotenv()

def create_rag():
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
                You are a technical documentation assistant.

                Answer the user's question using only the supplied context.

                If the context doesn't contain sufficient information,
                say: "I don't have enough information in the provided documents."

                Cite supporting source IDs in square brackets.

                Context:
                {context}
            """
        ),
        ("human", "{question}"),
    ])
    
    llm = ChatOpenAI(model="gpt-4.1-mini",temperature=0,)
    
    return prompt | llm | StrOutputParser()


def ask_rag(question: str) -> dict:
    chain = create_rag()
    
    documents = fetch_documents(question)
    context = "\n\n".join(
        f"[Source: {doc.metadata.get('chunk_id')}]\n"
        f"{doc.page_content}"
        for doc in documents
    )
    
    answer = chain.invoke({
        "context": context,
        "question": question,
    })

    return {
        "question": question,
        "answer": answer,
        "retrieved_documents": documents,
    }
    
    
if __name__ == "__main__":
    # question = (
    #     "Which controller manages ReplicaSets "
    #     "during rolling updates?"
    # )
    
    # Unsupported question
    question = "Who created Kubernetes, and in which year?"
    
    print(ask_rag(question))
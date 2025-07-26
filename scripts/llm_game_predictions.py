import os
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain.schema import Document
from langchain_core.output_parsers import StrOutputParser

api_key = os.environ.get("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key

# Path to the games data file
DATA_FILE = "../data/games.txt"


def load_data(file_path):
    """Load game data from the text file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} does not exist.")
    loader = TextLoader(file_path)
    return loader.load()


def split_text(file_path):
    """Manually read lines from the input text file and create a Document object for each line."""
    documents = []
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()  # Remove leading/trailing whitespace
            if line:  # Skip empty lines
                documents.append(Document(page_content=line))
    return documents


def create_vectorstore(documents):
    """Create a FAISS vector store from the documents."""
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore


def create_rag_chain(vectorstore):
    """Create a Retrieval-Augmented Generation (RAG) chain with context inspection."""
    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": 20}
    )
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # Define the prompt template
    prompt_template = """
    You are a sports analyst. Based on the following historical game data, predict the probability that the home team will win the next game.
    
    Historical games:
    {context}
    
    Question: {question}
    
    Provide a single decimal value between 0 and 1 as the probability.
    """
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    # Define a wrapper to inspect the retrieved context
    def inspect_context(input):
        context = retriever.get_relevant_documents(input)
        print("\nRetrieved Context:")
        for i, doc in enumerate(context):
            print(f"Document {i + 1}: {doc.page_content}")
        return {
            "context": "\n".join([doc.page_content for doc in context]),
            "question": input,
        }

    def print_inputs(inputs):
        print("Inputs:", inputs)
        return inputs

    # Create the RetrievalQA chain with a custom preprocessor
    # chain = RetrievalQA.from_chain_type(
    #    llm=llm,
    #    retriever=retriever,
    #    chain_type_kwargs={"prompt": prompt},
    #    input_preprocessor=RunnableLambda(inspect_context)
    # )

    chain = (
        # {
        #    "context": inspect_context(),
        #    "question": RunnablePassthrough(),
        # }
        RunnableLambda(print_inputs)
        | RunnableLambda(inspect_context)
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def predict_home_team_win(chain, home_team, away_team):
    """Predict the probability of the home team winning."""
    question = f"What is the probability that {home_team} will win against {away_team}?"
    result = chain.invoke(question)
    return result


if __name__ == "__main__":
    # Load and process the data
    print("Loading game data...")
    documents = split_text(DATA_FILE)

    print("Creating vector store...")
    vectorstore = create_vectorstore(documents)
    print(
        "Number of documents in vectorstore:",
    )
    print(vectorstore.index.ntotal)

    print("Setting up RAG chain...")
    rag_chain = create_rag_chain(vectorstore)

    # Example prediction
    home_team = "EDM"  # Replace with the home team's abbreviation
    away_team = "TOR"  # Replace with the away team's abbreviation

    print(f"Predicting probability for {home_team} vs {away_team}...")
    probability = predict_home_team_win(rag_chain, home_team, away_team)
    print(f"Predicted probability that {home_team} will win: {probability}")

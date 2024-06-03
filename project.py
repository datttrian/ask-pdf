import os
import shutil
import sys

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

CHROMA_PATH = "chroma"
DATA_PATH = "data/books"


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python project.py file.pdf query")

    pdf_file = sys.argv[1]
    documents = load_documents(pdf_file)
    chunks = split_text(documents)
    save_to_chroma(chunks)

    query_text = sys.argv[2]
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    results = db.similarity_search_with_relevance_scores(query_text, k=3)

    print(results)


def load_documents(file):
    loader = DirectoryLoader(DATA_PATH, glob=file)
    documents = loader.load()
    return documents


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks


def save_to_chroma(chunks: list[Document]):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    Chroma.from_documents(chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH)


if __name__ == "__main__":
    main()

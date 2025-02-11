from vertexai import rag
from vertexai.generative_models import GenerativeModel, Tool
import vertexai
import os
from dotenv import load_dotenv

# Create a RAG Corpus, Import Files, and Generate a response

# TODO(developer): Update and un-comment below lines
# PROJECT_ID = "your-project-id"
# display_name = "test_corpus"
# paths = ["https://drive.google.com/file/d/123", "gs://my_bucket/my_files_dir"]  # Supports Google Cloud Storage and Google Drive Links


load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")


# Initialize Vertex AI API once per session
vertexai.init(project=PROJECT_ID, location="us-central1")

# Create RagCorpus
# Configure embedding model, for example "text-embedding-005".
embedding_model_config = rag.EmbeddingModelConfig(
  publisher_model="publishers/google/models/text-embedding-005"
)

backend_config = rag.RagVectorDbConfig(rag_embedding_model_config=embedding_model_config)

rag_corpus = rag.create_corpus(
    display_name="my_rag_corpus",
    backend_config=backend_config,
)

# List the rag corpus you just created
rag_corpus = rag.list_corpora()

# Import Files to the RagCorpus
# choose a corpus to import files to, you can use rag_corpus.name for just created corpus
# or use the name in list_corpora()
corpus_name = rag_corpus.name

transformation_config = rag.TransformationConfig(
      chunking_config=rag.ChunkingConfig(
          chunk_size=512,
          chunk_overlap=100,
      ),
  )

rag.import_files(
    corpus_name,
    paths,
    transformation_config=transformation_config, # Optional
    max_embedding_requests_per_min=1000,  # Optional
)

# # Alternatively, you can use async import
# response = await rag.import_files_async(
#   corpus_name,
#   paths,
#   transformation_config=transformation_config, # Optional
#   max_embedding_requests_per_min=1000,  # Optional
# )
# result = await response.result()
# print(result)

# List the files in the rag corpus
rag.list_files(corpus_name)

# Direct context retrieval
rag_retrieval_config=rag.RagRetrievalConfig(
    top_k=3,  # Optional
    filter=rag.Filter(vector_distance_threshold=0.5)  # Optional
)
response = rag.retrieval_query(
    rag_resources=[
        rag.RagResource(
            rag_corpus=corpus_name,
            # Optional: supply IDs from `rag.list_files()`.
            # rag_file_ids=["rag-file-1", "rag-file-2", ...],
        )
    ],
    text="What is RAG and why it is helpful?",
    rag_retrieval_config=rag_retrieval_config,
)
print(response)

# Enhance generation
# Create a RAG retrieval tool
rag_retrieval_tool = Tool.from_retrieval(
    retrieval=rag.Retrieval(
        source=rag.VertexRagStore(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=corpus_name,  # Currently only 1 corpus is allowed.
                    # Optional: supply IDs from `rag.list_files()`.
                    # rag_file_ids=["rag-file-1", "rag-file-2", ...],
                )
            ],
            rag_retrieval_config=rag_retrieval_config,
        ),
    )
)
# Create a gemini model instance
rag_model = GenerativeModel(
    model_name="gemini-1.5-flash-001", tools=[rag_retrieval_tool]
)

# Generate response
response = rag_model.generate_content("What is RAG and why it is helpful?")
print(response.text)

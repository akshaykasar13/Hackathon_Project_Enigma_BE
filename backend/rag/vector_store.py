"""
Vector store module for RAG (Retrieval-Augmented Generation).
Supports: PDF, Word (.docx), TXT, PPTX, Images (with OCR)
"""
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend import config
import os

# Try to import Chroma, fallback to mock if not available
try:
    from langchain_community.vectorstores import Chroma
    CHROMA_AVAILABLE = True
except (ImportError, Exception) as e:
    CHROMA_AVAILABLE = False
    print(f"[VectorStore] Warning: Chroma not available: {e}")
    print("[VectorStore] Will use mock vector store")

# Import mock embeddings for test mode
if config.TEST_MODE:
    from backend.rag.mock_embeddings import MockEmbeddings
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: OCR libraries not installed. Image processing disabled.")

# Chunking configuration with overlap (from config)
CHUNK_SIZE = config.CHUNK_SIZE
CHUNK_OVERLAP = config.CHUNK_OVERLAP

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

# Initialize embeddings - use mock in test mode, OpenAI otherwise
if config.TEST_MODE:
    print("[VectorStore] Using mock embeddings (test mode)")
    embedding_function = MockEmbeddings()
else:
    embedding_function = OpenAIEmbeddings(openai_api_key=config.OPENAI_API_KEY)

# Create a mock vector store class for when Chroma is not available
class MockVectorStore:
    """Mock vector store for when ChromaDB is not available."""
    def __init__(self, persist_directory=None, embedding_function=None):
        self.persist_directory = persist_directory
        self.embedding_function = embedding_function
        self._docs = []
    
    def similarity_search(self, query, k=3):
        """Return empty results (mock)."""
        return []
    
    def add_documents(self, docs):
        """Store documents (mock)."""
        self._docs.extend(docs)
    
    def persist(self):
        """Persist (mock - no-op)."""
        pass

# Initialize vector store - use Chroma if available, otherwise mock
_db = None

def get_db():
    """Get or create the vector store instance."""
    global _db
    if _db is None:
        if CHROMA_AVAILABLE:
            try:
                _db = Chroma(
                    persist_directory=config.CHROMA_PERSIST_DIR,
                    embedding_function=embedding_function
                )
            except Exception as e:
                print(f"[VectorStore] Could not initialize ChromaDB: {e}")
                print("[VectorStore] Falling back to mock vector store")
                _db = MockVectorStore(
                    persist_directory=config.CHROMA_PERSIST_DIR,
                    embedding_function=embedding_function
                )
        else:
            _db = MockVectorStore(
                persist_directory=config.CHROMA_PERSIST_DIR,
                embedding_function=embedding_function
            )
    return _db

# For backward compatibility - create a simple wrapper
class DBWrapper:
    def similarity_search(self, *args, **kwargs):
        return get_db().similarity_search(*args, **kwargs)
    def add_documents(self, *args, **kwargs):
        return get_db().add_documents(*args, **kwargs)
    def persist(self, *args, **kwargs):
        return get_db().persist(*args, **kwargs)

db = DBWrapper()

def load_image_with_ocr(image_path):
    """Extract text from images using OCR."""
    if not OCR_AVAILABLE:
        return []
    
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        
        # Create a document-like structure
        from langchain_core.documents import Document
        return [Document(page_content=text, metadata={"source": image_path, "type": "image"})]
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return []


def ingest_docs(docs_dir: str = None):
    """Ingest all documents from the docs directory with chunking.
    Supports: PDF, Word (.docx), TXT, PPTX, Images (with OCR)
    Returns: dict with chunks_created, files_processed, errors
    """
    docs_dir = docs_dir or config.DOCS_DIR
    all_chunks = []
    files_processed = 0
    errors = []
    
    if not os.path.exists(docs_dir):
        print(f"Directory {docs_dir} does not exist")
        return {"chunks_created": 0, "files_processed": 0, "errors": [f"Directory {docs_dir} does not exist"]}
    
    # Load all supported file types
    for filename in sorted(os.listdir(docs_dir)):
        filepath = os.path.join(docs_dir, filename)
        
        try:
            if filename.endswith(".pdf"):
                loader = PyPDFLoader(filepath)
                docs = loader.load()
                print(f"Loaded PDF {filename}: {len(docs)} pages")
                
            elif filename.endswith((".docx", ".doc")):
                loader = UnstructuredWordDocumentLoader(filepath)
                docs = loader.load()
                print(f"Loaded Word {filename}: {len(docs)} pages")
                
            elif filename.endswith(".txt"):
                loader = TextLoader(filepath, encoding='utf-8')
                docs = loader.load()
                print(f"Loaded TXT {filename}: {len(docs)} pages")
                
            elif filename.endswith((".pptx", ".ppt")):
                loader = UnstructuredPowerPointLoader(filepath)
                docs = loader.load()
                print(f"Loaded PowerPoint {filename}: {len(docs)} slides")
                
            elif filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                if OCR_AVAILABLE:
                    docs = load_image_with_ocr(filepath)
                    print(f"Loaded Image {filename} (OCR): {len(docs)} pages")
                else:
                    print(f"Skipping {filename}: OCR not available")
                    continue
            else:
                continue
            
            # Chunk documents with overlap
            chunks = text_splitter.split_documents(docs)
            all_chunks.extend(chunks)
            files_processed += 1
            print(f"  -> {len(chunks)} chunks created")
            
        except Exception as e:
            err_msg = f"Error loading {filename}: {e}"
            print(err_msg)
            errors.append(err_msg)
            continue
    
    if all_chunks:
        db.add_documents(all_chunks)
        db.persist()
        print(f"\nTotal chunks ingested: {len(all_chunks)} (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    else:
        print("No supported files found to ingest")
    
    return {"chunks_created": len(all_chunks), "files_processed": files_processed, "errors": errors}


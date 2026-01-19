#!/usr/bin/env python3
"""
MyAIGist MCP Server
Document processing and Q&A with RAG
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Redirect all print to stderr for MCP compatibility (must be before any imports that print)
import builtins
_original_print = builtins.print
def print(*args, **kwargs):
    """Override print to always write to stderr for MCP"""
    kwargs['file'] = sys.stderr
    _original_print(*args, **kwargs)
builtins.print = print

# Get the absolute path to this script's directory
SERVER_DIR = Path(__file__).parent.absolute()
DATA_DIR = SERVER_DIR / "data"

# Import FastMCP
from mcp.server.fastmcp import FastMCP

# Import all agents from local mcp_agents
from mcp_agents.document_processor import DocumentProcessor
from mcp_agents.summarizer import Summarizer
from mcp_agents.embeddings import Embedder
from mcp_agents.url_crawler import UrlCrawler
from mcp_agents.openai_client import get_openai_client
from mcp_agents.qa_agent import QAAgent

# Load environment variables
load_dotenv()

# Verify required environment variables
required_vars = ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    print(f"💡 ANTHROPIC_API_KEY is used for Claude (summarization, Q&A)")
    print(f"💡 OPENAI_API_KEY is used for embeddings (RAG)")
    sys.exit(1)

# Initialize MCP server
mcp = FastMCP("myaigist")

# Initialize global agents
print("🚀 Initializing MyAIGist MCP Server...")
print(f"📁 Server directory: {SERVER_DIR}")
print(f"📁 Data directory: {DATA_DIR}")
try:
    document_processor = DocumentProcessor()
    summarizer = Summarizer()
    qa_agent = QAAgent(data_dir=str(DATA_DIR))
    url_crawler = UrlCrawler()
    print("✅ All agents initialized successfully")
except Exception as e:
    print(f"❌ Error initializing agents: {e}")
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

# Ensure directories exist (using absolute paths)
DATA_DIR.mkdir(exist_ok=True)


# ==================== Helper Functions ====================

def resolve_file_path(file_path: str) -> Optional[str]:
    """
    Resolve file path to handle both local paths and Claude Desktop uploads

    Args:
        file_path: Path provided by user or Claude Desktop

    Returns:
        Resolved absolute path if file exists, None otherwise
    """
    # Try the path as-is first
    if os.path.exists(file_path):
        return os.path.abspath(file_path)

    # If it's a Claude Desktop upload path, it should be accessible
    # Claude Desktop mounts uploads so they're accessible to MCP servers
    if file_path.startswith('/mnt/user-data/uploads/'):
        # The file should be accessible at this path from MCP server
        if os.path.exists(file_path):
            return file_path
        # If not found, log helpful error
        print(f"⚠️  Claude Desktop upload path not accessible: {file_path}")
        print(f"📁 Please save the file locally and provide the local path instead")
        return None

    # Try expanding user home directory
    expanded_path = os.path.expanduser(file_path)
    if os.path.exists(expanded_path):
        return os.path.abspath(expanded_path)

    # Try relative to server directory
    server_relative = SERVER_DIR / file_path
    if server_relative.exists():
        return str(server_relative.absolute())

    return None


# ==================== Content Processing Tools ====================

@mcp.tool()
def process_document(file_path: str, title: Optional[str] = None, summary_level: str = "standard") -> str:
    """
    Process a document from a LOCAL FILE PATH (PDF, DOCX, TXT) and add it to the knowledge base.

    ⚠️  IMPORTANT: This tool ONLY works with local Mac filesystem paths like:
    - /Users/username/Documents/file.pdf
    - ~/Downloads/document.docx

    ❌ DO NOT use this tool for Claude Desktop file attachments/uploads!
    ✅ For file attachments, use process_uploaded_document instead.

    Args:
        file_path: LOCAL filesystem path to the document (NOT /mnt/user-data/uploads/)
        title: Optional title for the document (defaults to filename)
        summary_level: Summary detail level (quick/standard/detailed)

    Returns:
        JSON string with summary and document ID
    """
    try:
        # Resolve file path
        resolved_path = resolve_file_path(file_path)
        if not resolved_path:
            return f"Error: File not found at {file_path}\n\nTip: Save the file locally first, then provide the full path like:\n/Users/yourusername/Documents/filename.pdf"

        # Extract title from filename if not provided
        if not title:
            title = Path(resolved_path).stem

        # Extract text from document
        print(f"📄 Processing document: {title}")
        print(f"📁 File path: {resolved_path}")
        text = document_processor.extract_text(resolved_path)

        if not text or len(text.strip()) < 10:
            return "Error: Document appears to be empty or unreadable"

        # Generate summary
        print(f"📝 Generating {summary_level} summary...")
        summary = summarizer.summarize(text, detail_level=summary_level)

        if not summary:
            summary = "Could not generate summary for this document."

        # Add to knowledge base
        print("💾 Adding to knowledge base...")
        doc_id = qa_agent.add_document(text, title)

        # Get status
        status = qa_agent.get_status()

        result = {
            "success": True,
            "title": title,
            "summary": summary,
            "doc_id": doc_id,
            "document_length": len(text),
            "summary_level": summary_level,
            "knowledge_base": {
                "total_documents": status['documents_count'],
                "total_chunks": status['chunks_count']
            }
        }

        import json
        return json.dumps(result, indent=2)

    except Exception as e:
        import json
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool()
def process_uploaded_document(content: str, filename: str, summary_level: str = "standard") -> str:
    """
    ✅ USE THIS TOOL for Claude Desktop file attachments/uploads (PDFs, DOCX, TXT, etc.)

    This is the RECOMMENDED tool for processing documents attached to Claude Desktop.

    How it works:
    1. User attaches a file to Claude Desktop
    2. Claude reads and extracts the text content from the file
    3. Claude calls THIS tool with the extracted content
    4. Tool processes the content, generates summary, and adds to knowledge base

    ⚠️  For local filesystem paths (not attachments), use process_document instead.

    Args:
        content: The extracted text content from the uploaded document
        filename: Original filename (used for title)
        summary_level: Summary detail level (quick/standard/detailed)

    Returns:
        JSON string with summary and document ID
    """
    try:
        # Extract title from filename
        title = Path(filename).stem

        # Validate content
        if not content or len(content.strip()) < 10:
            return "Error: Document content is too short or empty"

        print(f"📄 Processing uploaded document: {title}")
        print(f"📏 Content length: {len(content)} characters")

        # Generate summary
        print(f"📝 Generating {summary_level} summary...")
        summary = summarizer.summarize(content, detail_level=summary_level)

        if not summary:
            summary = "Could not generate summary for this document."

        # Add to knowledge base
        print("💾 Adding to knowledge base...")
        doc_id = qa_agent.add_document(content, title)

        # Get status
        status = qa_agent.get_status()

        result = {
            "success": True,
            "title": title,
            "summary": summary,
            "doc_id": doc_id,
            "document_length": len(content),
            "summary_level": summary_level,
            "knowledge_base": {
                "total_documents": status['documents_count'],
                "total_chunks": status['chunks_count']
            }
        }

        import json
        return json.dumps(result, indent=2)

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error processing uploaded document: {e}\n{error_trace}")
        return f"Error processing document: {str(e)}"


@mcp.tool()
def process_text(text: str, title: Optional[str] = None, summary_level: str = "standard") -> str:
    """
    Process raw text and add it to the knowledge base.

    Args:
        text: Text content to process
        title: Optional title for the text
        summary_level: Summary detail level (quick/standard/detailed)

    Returns:
        JSON string with summary and document ID
    """
    try:
        if not text or len(text.strip()) < 10:
            return "Error: Text is too short to process"

        if not title:
            title = f"Text Document {uuid.uuid4().hex[:8]}"

        # Generate summary
        print(f"📝 Generating {summary_level} summary...")
        summary = summarizer.summarize(text, detail_level=summary_level)

        if not summary:
            summary = "Could not generate summary for this text."

        # Add to knowledge base
        print("💾 Adding to knowledge base...")
        doc_id = qa_agent.add_document(text, title)

        # Get status
        status = qa_agent.get_status()

        result = {
            "success": True,
            "title": title,
            "summary": summary,
            "doc_id": doc_id,
            "text_length": len(text),
            "summary_level": summary_level,
            "knowledge_base": {
                "total_documents": status['documents_count'],
                "total_chunks": status['chunks_count']
            }
        }

        import json
        return json.dumps(result, indent=2)

    except Exception as e:
        import json
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool()
def process_url(url: str, title: Optional[str] = None, summary_level: str = "standard") -> str:
    """
    Crawl a web URL, extract content, and add it to the knowledge base.

    Args:
        url: Web URL to crawl
        title: Optional title (defaults to page title)
        summary_level: Summary detail level (quick/standard/detailed)

    Returns:
        JSON string with summary and document ID
    """
    try:
        # Crawl URL
        print(f"🌐 Crawling URL: {url}")
        crawl_result = url_crawler.crawl_url(url)

        if not crawl_result.get('success'):
            error_msg = crawl_result.get('error', 'Unknown error')
            return f"Error: {error_msg}"

        text = crawl_result.get('content', '')
        if not text or len(text.strip()) < 50:
            return f"Error: Could not extract meaningful content from {url}"

        if not title:
            title = crawl_result.get('title', url)

        # Generate summary
        print(f"📝 Generating {summary_level} summary...")
        summary = summarizer.summarize(text, detail_level=summary_level)

        if not summary:
            summary = "Could not generate summary for this content."

        # Add to knowledge base
        print("💾 Adding to knowledge base...")
        doc_id = qa_agent.add_document(text, title)

        # Get status
        status = qa_agent.get_status()

        result = {
            "success": True,
            "url": url,
            "title": title,
            "summary": summary,
            "doc_id": doc_id,
            "content_length": len(text),
            "summary_level": summary_level,
            "knowledge_base": {
                "total_documents": status['documents_count'],
                "total_chunks": status['chunks_count']
            }
        }

        import json
        return json.dumps(result, indent=2)

    except Exception as e:
        import json
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool()
def process_batch(file_paths: List[str], summary_level: str = "standard", generate_unified_summary: bool = True) -> str:
    """
    Process multiple files and optionally generate a unified summary.

    Args:
        file_paths: List of file paths to process
        summary_level: Summary detail level (quick/standard/detailed)
        generate_unified_summary: Whether to generate a unified summary across all files

    Returns:
        JSON string with individual and unified results
    """
    try:
        if not file_paths:
            return "Error: No file paths provided"

        results = []
        all_texts = []
        all_titles = []

        for file_path in file_paths:
            try:
                if not os.path.exists(file_path):
                    results.append({
                        "file": file_path,
                        "success": False,
                        "error": "File not found"
                    })
                    continue

                title = Path(file_path).stem

                # Process document
                text = document_processor.process_file(file_path)

                if not text or len(text.strip()) < 10:
                    results.append({
                        "file": file_path,
                        "success": False,
                        "error": "Empty or unreadable content"
                    })
                    continue

                # Generate individual summary
                summary = summarizer.summarize(text, detail_level=summary_level)

                # Add to knowledge base
                doc_id = qa_agent.add_document(text, title)

                results.append({
                    "file": file_path,
                    "success": True,
                    "title": title,
                    "summary": summary,
                    "doc_id": doc_id,
                    "content_length": len(text)
                })

                # Store for unified summary
                all_texts.append(text)
                all_titles.append(title)

            except Exception as e:
                results.append({
                    "file": file_path,
                    "success": False,
                    "error": str(e)
                })

        # Generate unified summary if requested
        unified_summary = None

        if generate_unified_summary and all_texts:
            print("📝 Generating unified summary across all documents...")
            combined_text = "\n\n".join([
                f"Document: {title}\n{text}"
                for title, text in zip(all_titles, all_texts)
            ])
            unified_summary = summarizer.summarize(combined_text, detail_level=summary_level)

        # Get final status
        status = qa_agent.get_status()

        result = {
            "success": True,
            "total_files": len(file_paths),
            "processed_successfully": sum(1 for r in results if r.get('success')),
            "individual_results": results,
            "unified_summary": unified_summary,
            "knowledge_base": {
                "total_documents": status['documents_count'],
                "total_chunks": status['chunks_count']
            }
        }

        import json
        return json.dumps(result, indent=2)

    except Exception as e:
        import json
        return json.dumps({"success": False, "error": str(e)}, indent=2)


# ==================== Q&A Tools ====================

@mcp.tool()
def ask_question(question: str) -> str:
    """
    Ask a question about the stored documents using RAG.

    Args:
        question: Question to ask

    Returns:
        JSON string with answer
    """
    try:
        if not question or len(question.strip()) < 3:
            return "Error: Question is too short"

        # Get answer from QA agent
        print(f"❓ Answering question: {question}")
        answer = qa_agent.answer_question(question)

        result = {
            "success": True,
            "question": question,
            "answer": answer
        }

        import json
        return json.dumps(result, indent=2)

    except Exception as e:
        import json
        return json.dumps({"success": False, "error": str(e)}, indent=2)


# ==================== Document Management Tools ====================

@mcp.tool()
def list_documents() -> str:
    """
    List all documents in the knowledge base.

    Returns:
        JSON string with list of documents and their metadata
    """
    try:
        documents = qa_agent.list_documents()
        status = qa_agent.get_status()

        result = {
            "success": True,
            "total_documents": len(documents),
            "documents": documents,
            "knowledge_base": status
        }

        import json
        return json.dumps(result, indent=2)

    except Exception as e:
        import json
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool()
def delete_document(doc_id: str) -> str:
    """
    Delete a specific document from the knowledge base.

    Args:
        doc_id: Document ID to delete

    Returns:
        JSON string with deletion status
    """
    try:
        success = qa_agent.delete_document(doc_id)

        if success:
            status = qa_agent.get_status()
            result = {
                "success": True,
                "message": f"Document {doc_id} deleted successfully",
                "knowledge_base": status
            }
        else:
            result = {
                "success": False,
                "error": f"Document {doc_id} not found"
            }

        import json
        return json.dumps(result, indent=2)

    except Exception as e:
        import json
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool()
def clear_all_documents() -> str:
    """
    Clear all documents from the knowledge base.

    Returns:
        JSON string with clearing status
    """
    try:
        qa_agent.clear_documents()
        status = qa_agent.get_status()

        result = {
            "success": True,
            "message": "All documents cleared successfully",
            "knowledge_base": status
        }

        import json
        return json.dumps(result, indent=2)

    except Exception as e:
        import json
        return json.dumps({"success": False, "error": str(e)}, indent=2)


# ==================== Utility Tools ====================

@mcp.tool()
def get_status() -> str:
    """
    Get system status and knowledge base statistics.

    Returns:
        JSON string with system status
    """
    try:
        qa_status = qa_agent.get_status()

        result = {
            "success": True,
            "knowledge_base": qa_status,
            "supported_formats": {
                "documents": ["pdf", "docx", "txt"]
            }
        }

        import json
        return json.dumps(result, indent=2)

    except Exception as e:
        import json
        return json.dumps({"success": False, "error": str(e)}, indent=2)


# Run the server
if __name__ == "__main__":
    print("🎉 MyAIGist MCP Server is ready!")
    print(f"📚 Knowledge base: {qa_agent.get_status()['documents_count']} documents")
    print(f"💾 Data directory: {DATA_DIR}")
    print("✅ Core functionality: Document processing and Q&A")
    mcp.run()

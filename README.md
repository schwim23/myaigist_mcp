# MyAIGist MCP Server

MCP server providing document intelligence and knowledge management for Claude Desktop and other MCP-compatible clients. Process documents, answer questions with RAG, and maintain a persistent knowledge base - all running locally.

## Overview

**MyAIGist MCP** provides 10 powerful tools for document intelligence and knowledge management:

- **Document Processing**: PDF, DOCX, TXT, URLs, file attachments, and batch processing
- **Q&A System**: RAG-powered question answering across multiple documents
- **Knowledge Management**: Persistent vector storage with document tracking

## Features

✅ **MCP-compatible** - Works with Claude Desktop, Cursor, and other MCP clients
✅ **Claude-powered** - Uses Claude Sonnet 4.5 for summarization and Q&A
✅ **Local execution** - Runs on your machine with no external infrastructure
✅ **Persistent storage** - Single vector store survives across sessions
✅ **Multi-document RAG** - Unlimited documents in knowledge base
✅ **Simple setup** - Install dependencies, configure API keys, and go

## Installation

### Prerequisites

- Python 3.8+
- Anthropic API key (for Claude text generation)
- OpenAI API key (for embeddings)
- MCP-compatible client (Claude Desktop, Cursor, etc.)

### Setup

1. **Install dependencies:**
   ```bash
   cd /path/to/myaigist_mcp
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add both API keys:
   # - ANTHROPIC_API_KEY (for Claude)
   # - OPENAI_API_KEY (for embeddings)
   ```

3. **Configure your MCP client:**

   **Claude Desktop** - Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "myaigist": {
         "command": "python3",
         "args": ["/path/to/myaigist_mcp/server.py"]
       }
     }
   }
   ```

   **Cursor** - Add to your Cursor MCP settings:
   ```json
   {
     "mcpServers": {
       "myaigist": {
         "command": "python3",
         "args": ["/path/to/myaigist_mcp/server.py"]
       }
     }
   }
   ```

   **Other MCP clients** - Refer to your client's documentation for MCP server configuration.

4. **Restart your MCP client**

   The MCP server will start automatically when you open your client.

## Architecture

```
myaigist_mcp/               # MCP server (this project)
├── server.py               # Main MCP server with 10 tools
├── mcp_agents/             # All agent code (local, self-contained)
│   ├── document_processor.py  # PDF/DOCX/TXT extraction
│   ├── summarizer.py          # 3-level summarization (Claude)
│   ├── embeddings.py          # OpenAI embeddings
│   ├── url_crawler.py         # Web content extraction
│   ├── claude_client.py       # Anthropic client factory
│   ├── openai_client.py       # OpenAI client factory
│   ├── qa_agent.py            # Q&A with RAG (Claude)
│   └── vector_store.py        # Vector storage
└── data/                   # Persistent vector storage
    └── vector_store.pkl    # Created at runtime
```

**Architecture Notes:**
- All agents are self-contained in `mcp_agents/`
- No external dependencies on other projects
- Single-user design (no session/user isolation)
- Persistent vector storage with unlimited documents
- **Claude Sonnet 4.5** for text generation (summarization, Q&A)
- **OpenAI** for embeddings (RAG)

## Available Tools (10 Total)

### Content Processing (5 tools)

#### 1. `process_document`
Process a document from LOCAL FILE PATH (PDF, DOCX, TXT) and add to knowledge base.

**Parameters:**
- `file_path` (string, required): LOCAL filesystem path (e.g., /Users/mike/file.pdf)
- `title` (string, optional): Document title (defaults to filename)
- `summary_level` (string, optional): `quick`, `standard`, or `detailed`

**Example:**
```
"Process /Users/mike/contract.pdf as a detailed summary"
```

**Compatibility:** Works with all MCP clients.

#### 2. `process_uploaded_document`
Process a document attached to Claude Desktop (optimized for Claude Desktop file uploads).

**Parameters:**
- `content` (string, required): Text content extracted by Claude
- `filename` (string, required): Original filename
- `summary_level` (string, optional): `quick`, `standard`, or `detailed`

**Example:**
```
[Attach PDF file in Claude Desktop]
"Process this document with MyAIGist"
```

**Compatibility:** Designed for Claude Desktop. Other clients should use `process_document` with file paths.

#### 3. `process_text`
Process raw text and add to knowledge base.

**Example:**
```
"Process this text: [paste long article]"
```

**Compatibility:** Works with all MCP clients.

#### 4. `process_url`
Crawl web URL, extract content, and add to knowledge base.

**Example:**
```
"Process https://example.com/article"
```

**Compatibility:** Works with all MCP clients.

#### 5. `process_batch`
Process multiple files and generate unified summary.

**Example:**
```
"Process all files in /Users/mike/research/ and give me a unified summary"
```

**Compatibility:** Works with all MCP clients.

### Q&A System (1 tool)

#### 6. `ask_question`
Ask questions about stored documents using RAG.

**Example:**
```
"What are the main findings in the research papers?"
```

**Compatibility:** Works with all MCP clients.

### Document Management (3 tools)

#### 7. `list_documents`
List all documents in knowledge base with metadata.

**Example:**
```
"Show me all my documents"
```

**Compatibility:** Works with all MCP clients.

#### 8. `delete_document`
Delete specific document by ID.

**Example:**
```
"Delete document abc123xyz"
```

**Compatibility:** Works with all MCP clients.

#### 9. `clear_all_documents`
Clear entire knowledge base.

**Example:**
```
"Clear all my documents"
```

**Compatibility:** Works with all MCP clients.

### Utility Tools (1 tool)

#### 10. `get_status`
Get system status and knowledge base statistics.

**Example:**
```
"What's my system status?"
```

**Compatibility:** Works with all MCP clients.

## Common Workflows

### File Upload (Claude Desktop)
```
User: [Attaches PDF to Claude Desktop]
User: "Process this document with MyAIGist"
Claude: ✅ Processed with summary

User: "What are the key points?"
Claude: "The key points are..."
```

### Single Document Q&A (Any MCP Client)
```
User: "Process /Users/mike/contract.pdf"
AI: ✅ Processed with summary

User: "What are the payment terms?"
AI: "The payment terms are net 30..."
```

### Multi-Document Research (Any MCP Client)
```
User: "Process these 3 research papers: paper1.pdf, paper2.pdf, paper3.pdf"
AI: ✅ Processed all 3 with unified summary

User: "What are the common findings across all papers?"
AI: "The common findings are..."
```

## Configuration

### Environment Variables (.env)

```bash
# Anthropic API Key (required - for Claude text generation)
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# OpenAI API Key (required - for embeddings)
OPENAI_API_KEY=sk-your-key-here
OPENAI_EMBED_MODEL=text-embedding-3-large
```

### Model Selection

**Current Configuration:**
- **Claude Sonnet 4.5** (`claude-sonnet-4-5-20250929`) - Summarization and Q&A
- **text-embedding-3-large** - Higher accuracy for RAG vector search

**Why Two API Keys?**
- **Anthropic Claude**: Text generation (summarization, Q&A) - excellent quality
- **OpenAI**: Embeddings (Claude doesn't provide embeddings)

### Storage

**Vector Store:**
- Path: `data/vector_store.pkl`
- Format: Pickle with numpy arrays
- Persistence: Survives server restarts
- Capacity: Unlimited documents

## API Costs

**Usage-based pricing:**
- **Claude Sonnet 4.5**: $3/$15 per 1M tokens (input/output)
- **OpenAI Embeddings**: $0.13 per 1M tokens

**Typical monthly usage:**
- 100 documents processed: ~$5-10
- 500 questions answered: ~$2-5
- **Total: ~$10-15/month**

## Troubleshooting

### Server won't start
```bash
# Check if Python can find dependencies
python3 -c "import mcp; print('✅ MCP installed')"

# Check syntax
python3 -m py_compile server.py

# Check logs (Claude Desktop example)
tail -f ~/Library/Logs/Claude/mcp-server-myaigist.log
```

### Import errors
```bash
# Test agent imports
cd /path/to/myaigist_mcp
python3 -c "from mcp_agents.summarizer import Summarizer; print('✅ Imports work')"
python3 -c "from mcp_agents.qa_agent import QAAgent; print('✅ QAAgent works')"
```

### API Key errors
```bash
# Check environment variables are set
python3 -c "import os; print('Anthropic:', bool(os.getenv('ANTHROPIC_API_KEY'))); print('OpenAI:', bool(os.getenv('OPENAI_API_KEY')))"
```

### Empty knowledge base after restart
- Check `data/vector_store.pkl` exists
- Verify file permissions (readable/writable)
- Check for errors in server logs

### File upload not working
- **Claude Desktop**: Use `process_uploaded_document` for file attachments
- **Other clients**: Use `process_document` with local filesystem paths
- See tool descriptions for compatibility details

## Development

### Running Tests
```bash
# Test agent imports
python3 -c "from mcp_agents.qa_agent import QAAgent; qa = QAAgent(); print('✅ QAAgent works')"

# Test document processing
cd /path/to/myaigist_mcp
python3 -c "from mcp_agents.document_processor import DocumentProcessor; dp = DocumentProcessor(); print('✅ DocumentProcessor works')"
```

### Debugging
```bash
# Run server manually to see output
python3 /path/to/myaigist_mcp/server.py
```

## Project Structure

```
myaigist_mcp/
├── server.py              # Main MCP server (10 tools)
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example          # Template
├── README.md             # This file
├── mcp_agents/           # MCP-adapted agents
│   ├── __init__.py
│   ├── claude_client.py   # Anthropic client factory
│   ├── summarizer.py      # Modified: uses Claude
│   ├── qa_agent.py        # Modified: uses Claude, single-user
│   ├── vector_store.py    # Modified: no user filtering
│   ├── document_processor.py
│   ├── embeddings.py
│   ├── url_crawler.py
│   └── openai_client.py
└── data/                 # Persistent storage
    └── vector_store.pkl  # Vector embeddings and metadata
```

## MCP Client Compatibility

### Tested Clients
- ✅ **Claude Desktop** - Full support including file attachments
- ⚠️ **Cursor** - Core functionality works (use file paths instead of attachments)
- ❓ **Other MCP clients** - Should work with file path-based tools

### Compatibility Notes
- All tools work with standard file paths
- `process_uploaded_document` is optimized for Claude Desktop's file attachment behavior
- Other clients should use `process_document` with local file paths
- Standard MCP protocol (stdio transport, JSON-RPC)

## License

MIT License

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review MCP server logs (location varies by client)
3. Verify environment variables in `.env`
4. Test agent imports individually

---

**Last Updated:** 2026-01-19
**Project Status:** ✅ Production ready - 10 core tools implemented and tested
**Models:** Claude Sonnet 4.5 (text) + OpenAI (embeddings)
**Focus:** Document intelligence (text-based content only)
**Compatibility:** Claude Desktop, Cursor, and other MCP-compatible clients

# Backend - AI Presentation Generator

Powerful REST API for automatic presentation generation using Rostelecom AI APIs.

## Features

✨ **AI-Powered Slide Generation**
- Intelligent slide structure using Rostelecom Leopold LLM
- Multiple presentation styles (corporate, creative, minimal)
- Various tone options (professional, friendly, academic)
- Support for 1-20 slides per presentation

🖼️ **AI Image Generation**
- Generates custom images for each slide using Yandex ART
- Local file storage for reliability
- Automatic retry logic and timeout handling

📄 **Document Support**
- PDF extraction and analysis
- DOCX extraction and analysis
- Content used to inform slide generation

✏️ **Slide Editing**
- Edit slide titles and content after generation
- Regenerate individual slide images
- Add new slides to presentation
- Delete slides (keeping minimum 1)
- Regenerate PPTX file with updated content

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── models.py               # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py      # LLM integration
│   │   ├── image_service.py    # Image generation
│   │   └── pptx_generator.py   # PPTX file creation
│   └── utils/
│       ├── __init__.py
│       └── logger.py           # Logging utility
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── test_api.py                 # Full test suite
├── test_simple.py              # Simple test suite
├── API_DOCS.md                 # API documentation
├── .env.example                # Environment template
└── README.md                   # This file
```

## Quick Start

### 1. Setup Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file:
```bash
cp .env .env
```

Edit `.env` with your Rostelecom API token:
```env
ROSTELECOM_API_TOKEN=your-token-here
ENVIRONMENT=development
```

### 3. Run Server

```bash
# Development with auto-reload
python -m uvicorn app.main:app --reload

# Production
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Server runs at: `http://localhost:8000`

API docs: `http://localhost:8000/docs` (Swagger UI)

## API Usage Examples

### Generate Presentation

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -F "prompt=Artificial Intelligence in Business" \
  -F "num_slides=5" \
  -F "style=corporate" \
  -F "tone=professional" \
  -F "include_images=true"
```

### Edit Slide

```bash
curl -X PUT "http://localhost:8000/api/session/{session_id}/slides/0" \
  -F "title=New Title" \
  -F "content=• Updated content"
```

### Download Presentation

```bash
curl -X GET "http://localhost:8000/api/download/{session_id}" \
  -o presentation.pptx
```

See [API_DOCS.md](API_DOCS.md) for complete API reference.

## Testing

### Quick Test
```bash
python test_simple.py
```

### Full Test Suite
```bash
python test_api.py
python test_api.py --quick
python test_api.py --help
```

## Architecture

### Data Flow

```
User Request
    ↓
FastAPI Endpoint
    ↓
LLM Service (Text Generation)
    ↓
Image Service (Image Generation)
    ↓
PPTX Generator (File Assembly)
    ↓
File Storage + Session Management
    ↓
Download/Edit Endpoints
```

### Services

#### LLMService
- Communicates with Rostelecom Leopold LLM
- Generates slide structure from prompts
- Processes uploaded documents (PDF/DOCX)
- Provides fallback structures for reliability
- Temperature: 0.7 for balanced creativity

#### ImageService
- Communicates with Yandex ART API
- Generates images from text descriptions
- Saves images locally for PPTX embedding
- Retry logic for async API calls
- Timeout handling (30s default)

#### PPTXGenerator
- Creates PowerPoint files using python-pptx
- Applies styles (colors, fonts, layouts)
- Embeds local images in slides
- Professional formatting for all styles

## Configuration

Key environment variables:

```env
# API Credentials (Required)
ROSTELECOM_API_TOKEN=your-token

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=True
ENVIRONMENT=development

# File Storage
GENERATED_FILES_DIR=generated_files
MAX_FILE_SIZE_MB=10
MAX_DOCUMENT_CHARS=10000

# LLM Parameters
LLAMA_TEMPERATURE=0.7
LLAMA_MAX_TOKENS=4096

# Image Generation
DEFAULT_IMAGE_ASPECT=16:9
IMAGE_GENERATION_TIMEOUT=30
```

## Error Handling

The API provides meaningful error responses:

```json
{
  "detail": "File too large. Max size: 10MB"
}
```

HTTP Status Codes:
- `200 OK`: Successful operation
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource not found
- `500 Server Error`: API failure, generation error

## Performance Notes

- Slide text generation: 2-5 seconds per slide
- Image generation: 3-5 seconds per image
- PPTX creation: 1-2 seconds
- **Total for 5-slide presentation with images: ~30-50 seconds**

Factors affecting performance:
- Network latency to Rostelecom APIs
- Image generation queue
- File size and complexity
- Number of images included

## Troubleshooting

### "ROSTELECOM_API_TOKEN is not set"
- Ensure `.env` file exists with valid token
- Check file is in `backend/` directory
- Restart server after adding token

### Images not appearing in PPTX
- Check `generated_files/images/` directory
- Verify image generation returned file path
- Check PPTX generator error logs

### Timeout errors
- Increase `IMAGE_GENERATION_TIMEOUT` in `.env`
- Check network connection to Rostelecom APIs
- Try again (transient network issues)

### "Presentation not found"
- Session ID may have expired
- Generate new presentation
- Sessions are stored in memory (lost on restart)

## Development

### Code Style
```bash
# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

### Adding New Features

1. Add model in `app/models.py`
2. Create service method
3. Add endpoint in `app/main.py`
4. Add tests
5. Update `API_DOCS.md`

## Deployment

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Example

See deployment configuration in infrastructure folder.

## Contributing

1. Create feature branch
2. Make changes with tests
3. Ensure all tests pass
4. Submit pull request

## License

Proprietary - Rostelecom AI

## Support

For API issues: Contact Rostelecom support
For bugs: Create GitHub issue
For features: Submit feature request

## Changelog

### v1.1.0 (Current)
- Fixed image embedding in PPTX
- Improved LLM prompts for better content
- Added slide editing endpoints
- Added image regeneration for individual slides
- Better error handling and logging
- Performance improvements

### v1.0.0
- Initial release
- Basic presentation generation
- Image support
- PDF/DOCX processing

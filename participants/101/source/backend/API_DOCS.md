# Backend API Documentation

## Setup & Run

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file with your Rostelecom API token:
```
ROSTELECOM_API_TOKEN=your-token-here
HOST=0.0.0.0
PORT=8000
RELOAD=True
```

### 3. Run Server
```bash
python -m uvicorn app.main:app --reload
```

Server will start at: `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /health
```
Response: Server status and available services

### Generate Presentation
```
POST /api/generate
```
**Parameters:**
- `prompt` (required): Presentation topic/description
- `num_slides` (default: 10): Number of slides (1-20)
- `style` (default: corporate): Style - corporate, creative, or minimal
- `tone` (default: professional): Tone - professional, friendly, or academic
- `include_images` (default: true): Include AI-generated images
- `document` (optional): PDF or DOCX file for content analysis

**Response:**
```json
{
  "session_id": "uuid",
  "file_url": "/api/download/uuid",
  "slides": [
    {
      "index": 0,
      "title": "Slide Title",
      "content": "Slide content...",
      "has_image": true,
      "image_path": "/path/to/image.png"
    }
  ],
  "message": "Презентация успешно создана!"
}
```

### Get Session Info
```
GET /api/session/{session_id}
```
Get details about a generated presentation session

### Edit Slide
```
PUT /api/session/{session_id}/slides/{slide_index}
```
**Parameters:**
- `title` (optional): New slide title
- `content` (optional): New slide content
- `image_prompt` (optional): New image prompt

### Add Slide
```
POST /api/session/{session_id}/slides/add
```
**Parameters:**
- `title` (required): Slide title
- `content` (required): Slide content
- `image_prompt` (optional): Image description

### Delete Slide
```
DELETE /api/session/{session_id}/slides/{slide_index}
```
Cannot delete first slide or last remaining slide

### Regenerate Image for Slide
```
POST /api/session/{session_id}/slides/{slide_index}/regenerate-image
```
Regenerates the image for a specific slide using its current image_prompt

### Regenerate PPTX
```
POST /api/session/{session_id}/regenerate-pptx
```
**Parameters:**
- `style` (optional): Presentation style
- `include_images` (default: true): Include images in regenerated PPTX

### Download Presentation
```
GET /api/download/{session_id}
```
Downloads the PPTX file

### Get Configuration
```
GET /api/config
```
Returns available styles, tones, and other config

## Features

✅ **LLM-Powered Content Generation**
- Uses Rostelecom Leopold model for intelligent slide structure
- Improved prompts for better text quality
- Fallback structure for reliability

✅ **AI Image Generation**
- Yandex ART for high-quality illustrations
- Local file storage for reliability
- Automatic retry logic for image generation

✅ **Flexible Editing**
- Edit slide titles and content
- Regenerate individual images
- Add/delete slides
- Regenerate PPTX after edits

✅ **Document Processing**
- PDF extraction
- DOCX extraction
- Content used for LLM context

✅ **Robust Error Handling**
- Timeout handling for API calls
- Fallback structures for all operations
- Detailed error messages

## Error Handling

All errors return appropriate HTTP status codes:
- `400`: Bad Request (validation errors)
- `404`: Not Found (session/slide not found)
- `500`: Server Error (API failures, generation errors)

## Testing

Run the test suite:
```bash
python test_api.py
python test_api.py --quick
```

## Performance Notes

- Image generation takes 3-5 seconds per image (needs API to complete processing)
- First PPTX generation takes 2-3 seconds
- Each slide with image: ~5 seconds
- Larger presentations (15-20 slides): 60-90 seconds total

## Architecture

### Services:
1. **LLMService**: Generates presentation structure using Rostelecom Leopold
2. **ImageService**: Generates and manages slide images via Yandex ART
3. **PPTXGenerator**: Creates PowerPoint files with proper formatting

### Data Flow:
1. User submits prompt + parameters
2. LLM generates slide structure
3. Images are generated and saved locally
4. PPTX is created and stored
5. User can edit and regenerate as needed
6. PPTX is downloaded or slides are edited further

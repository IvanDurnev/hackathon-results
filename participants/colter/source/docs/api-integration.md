# API Integration Contract

## Principle

Frontend never calls the external AI service directly. The token stays on the backend in environment variables, and the browser talks only to our domain endpoints.

The user generation flow is split into two phases:

1. Create or regenerate an outline.
2. Approve the outline and build a presentation document.

Image generation is a backend side effect during phase 2: by default the backend asks Yandex ART for an image, downloads the produced file, stores it as an `Asset`, and inserts the asset into the presentation JSON. Stable Diffusion remains available via `RT_AI_IMAGE_PROVIDER=sd`.

## External Services

### Qwen

Endpoint:

```http
POST https://ai.rt.ru/api/1.0/llama/chat
Authorization: Bearer <RT_AI_TOKEN>
Content-Type: application/json
```

Minimum request shape:

```json
{
  "uuid": "generation-or-request-uuid",
  "chat": {
    "model": "Qwen/Qwen2.5-72B-Instruct",
    "user_message": "Task text",
    "contents": [],
    "system_prompt": "Return valid JSON only.",
    "max_new_tokens": 1536,
    "temperature": 0.2,
    "top_k": 40,
    "top_p": 0.9,
    "chat_history": []
  }
}
```

Relevant response fields:

```json
[
  {
    "message": {
      "serviceType": "llama",
      "type": "msg",
      "content": "model response text",
      "id": 231719
    },
    "uuid": "response-uuid"
  }
]
```

### Yandex ART

Request image:

```http
POST https://ai.rt.ru/api/1.0/ya/image
Authorization: Bearer <RT_AI_TOKEN>
Content-Type: application/json
```

```json
{
  "uuid": "generation-or-asset-uuid",
  "image": {
    "request": "Image prompt",
    "seed": 123456789,
    "translate": false,
    "model": "yandex-art",
    "aspect": "16:9"
  }
}
```

Relevant response field: `message.id`.

Download image:

```http
GET https://ai.rt.ru/api/1.0/download?id=231719&serviceType=yaArt&imageType=png
Authorization: Bearer <RT_AI_TOKEN>
```

## Backend Environment

```env
RT_AI_BASE_URL=https://ai.rt.ru/api/1.0
RT_AI_TOKEN=...
RT_AI_LLM_MODEL=Qwen/Qwen2.5-72B-Instruct
RT_AI_TIMEOUT_SECONDS=240
RT_AI_IMAGE_PROVIDER=yandex
RT_AI_YANDEX_MODEL=yandex-art
RT_AI_YANDEX_ASPECT=16:9
RT_AI_MOCK=0
```

For local contract checks without external calls, set `RT_AI_MOCK=1`.

## Internal Frontend-To-Backend API

### Generation Basis

The user must choose exactly one basis:

```ts
type GenerationBasis =
  | {
      kind: "layout";
      templateId: string;
      layoutIds?: string[];
    }
  | {
      kind: "style";
      styleId: "business" | "friendly" | "academic" | "promo";
    };
```

`layout` means we use existing template/layout geometry. `style` means we generate the deck theme without binding the request to a template. These fields are intentionally mutually exclusive.

### Create Outline

```http
POST /api/ai/generations/outline
```

```json
{
  "prompt": "Presentation for investors...",
  "slideCount": 12,
  "language": "ru",
  "basis": {
    "kind": "layout",
    "templateId": "template_business_01"
  }
}
```

Alternative style request:

```json
{
  "prompt": "Presentation for investors...",
  "slideCount": 12,
  "language": "ru",
  "basis": {
    "kind": "style",
    "styleId": "business"
  }
}
```

Response:

```json
{
  "generationId": "gen_123",
  "status": "outline_ready",
  "outline": {
    "title": "Deck title",
    "audience": "Board of directors",
    "goal": "Decision support",
    "slides": [
      {
        "order": 1,
        "title": "Context",
        "purpose": "Set the stage",
        "keyPoints": ["Point 1", "Point 2"],
        "visualIntent": "Simple chart or hero image",
        "needsImage": false
      }
    ]
  }
}
```

### Regenerate Outline

```http
POST /api/ai/generations/{generationId}/outline/retry
```

```json
{
  "feedback": "Make it shorter and more executive.",
  "outline": {
    "title": "Previous title",
    "slides": []
  }
}
```

Response shape is the same as `Create Outline`.

### Approve Outline And Build Presentation

```http
POST /api/ai/generations/{generationId}/presentation
```

```json
{
  "outline": {
    "title": "Approved title",
    "slides": []
  },
  "imagePolicy": {
    "generateImages": true,
    "imageType": "png"
  }
}
```

Response is the existing `PresentationDocument`:

```json
{
  "schemaVersion": "1.0.0",
  "documentType": "presentation",
  "id": "pres_123",
  "name": "Approved title",
  "templateId": "template_business_01",
  "slideSize": { "widthEmu": 12192000, "heightEmu": 6858000, "ratio": "16:9" },
  "theme": {},
  "slides": [],
  "assets": []
}
```

## Qwen Prompt Payloads

For outline generation, the backend sends Qwen:

```json
{
  "task": "presentation_outline",
  "prompt": "user prompt",
  "slideCount": 12,
  "basis": {},
  "requiredJsonSchema": "Outline schema"
}
```

For slide content generation after approval:

```json
{
  "task": "presentation_slide_content",
  "prompt": "original user prompt",
  "outline": {},
  "basis": {},
  "requiredJsonSchema": "Slide content schema"
}
```

The backend validates and normalizes model output before creating `PresentationDocument`.

## Error Rules

- `422`: invalid user request, invalid outline, or both layout and style were sent.
- `401`: backend token is missing or rejected by the external service.
- `409`: the generation is in the wrong state, for example presentation build before outline approval.
- `502`: external Qwen or SD call failed.

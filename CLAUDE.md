# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TextDiff is a text version management and diff comparison system with:
- **Backend**: FastAPI + SQLAlchemy (Python)
- **Frontend**: Vue 3 + TypeScript + Pinia
- **Database**: SQLite (dev) / PostgreSQL (prod)

## Common Commands

### Backend Development
```bash
cd backend
python -m app.main                    # Start backend server (port 8000)
# OR if port is in use:
lsof -ti:8000 | xargs kill -9        # Kill existing process
python -m app.main
```

### Frontend Development
```bash
cd frontend
npm install                           # Install dependencies
npm run dev                           # Start dev server (port 5173)
npm run build                         # Production build
npm run type-check                    # Check TypeScript types
```

### Running Both Services
```bash
# Terminal 1
cd backend && python -m app.main

# Terminal 2
cd frontend && npm run dev
```

## Architecture

### Core Data Flow
1. **Document** → has many **Versions** → each Version can have **Tags**
2. Versions are immutable snapshots with parent-child relationships
3. Content deduplication via MD5 hashing prevents storing identical versions

### Key Services

**Backend Services** (`backend/app/services/`):
- `version_service.py`: CRUD operations for documents/versions
- `diff_service.py`: 4 diff modes (character, word, line, semantic)
- `websocket_manager.py`: Real-time collaboration

**Frontend State** (`frontend/src/stores/document.ts`):
- Centralized Pinia store managing document state
- Auto-save with debouncing
- Save modes: manual, auto, hybrid

### API Structure
- Documents: `/api/documents/{id}`
- Versions: `/api/documents/{id}/versions`
- Diff: `/api/diff/{v1}/{v2}?diff_mode=word&ignore_case=false&ignore_whitespace=false`

## Critical Implementation Details

### IPv4/IPv6 Fix
**IMPORTANT**: The proxy in `frontend/vite.config.ts` must use `127.0.0.1` (not `localhost`) to force IPv4:
```typescript
proxy: {
  '/api': {
    target: 'http://127.0.0.1:8000',  // NOT localhost
    changeOrigin: true
  }
}
```

### Diff Display Modes
The `DiffViewer.vue` component supports two display modes:
1. **diff-only**: Shows only changed content
2. **full-text**: Shows complete text with changes highlighted

Backend must return `type: 'unchanged'` changes for full-text mode to work.

### Content Hashing
Versions are deduplicated using MD5 hashing in `version_service.py`:
```python
content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()
if latest_version.content_hash == content_hash:
    return None  # Skip duplicate
```

### Save Strategy
Three save modes configured in `SaveSettings.vue`:
- **manual**: User triggers save (button or Ctrl+S)
- **auto**: Periodic save (default 30s interval)
- **hybrid**: Both manual and auto enabled

## Database Models

```python
Document:
  id (UUID), title, created_at, updated_at, current_version_number

Version:
  id (UUID), document_id (FK), version_number, content, content_hash,
  save_type (manual|auto|draft), parent_version_id (FK)

VersionTag:
  id (UUID), version_id (FK), tag_name, description
```

## Common Issues & Solutions

1. **500 Error "ECONNREFUSED ::1:8000"**
   - Cause: Vite using IPv6, backend on IPv4
   - Fix: Use `127.0.0.1` in vite.config.ts proxy

2. **Port 8000 Already in Use**
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

3. **Module Import Errors**
   - Must run from backend directory: `cd backend && python -m app.main`
   - NOT: `python main.py`

4. **TypeScript Config Error**
   - If @vue/tsconfig missing, config is written directly in tsconfig.json

## File Locations

**Backend Core Files**:
- Entry: `backend/app/main.py`
- Models: `backend/app/models/document.py`
- Services: `backend/app/services/`
- API Routes: `backend/app/api/routes/`

**Frontend Core Files**:
- Entry: `frontend/src/main.ts`
- Store: `frontend/src/stores/document.ts`
- Components: `frontend/src/components/`
- API Client: `frontend/src/api/client.ts`
- Types: `frontend/src/types/index.ts`

## Testing

```bash
cd backend
pytest                              # Run all tests
pytest tests/unit -v               # Unit tests only
pytest tests/integration -v        # Integration tests
pytest --cov=app                    # Coverage report
```

## Environment Variables

Backend `.env`:
```bash
DATABASE_URL=sqlite:///./textdiff.db
ALLOWED_ORIGINS=["http://localhost:5173"]
```

## Development Notes

- Frontend uses Composition API with `<script setup>` syntax
- All API responses are typed with TypeScript interfaces
- Pinia store uses composition style (not options API)
- SCSS with responsive breakpoints defined in `variables.scss`
- WebSocket support at `/ws/document/{id}` for real-time features
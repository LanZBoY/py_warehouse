# Gemini CLI Workspace Rules

## Prompt Processing Protocol
Whenever the user references a file in the `prompt/` directory as a directive or instruction:

1.  **Status Tracking**: Once the requested task is completed, you MUST update the corresponding prompt file.
2.  **Format**: Append a `---` separator followed by a `## 實作紀錄 (Status: Done)` section.
3.  **Details**: List the specific actions, files modified, and libraries installed.
4.  **Reference**: If new documentation or technical notes were created (e.g., in `Note/`), mention them in the record.

## API Response Standard
All API responses must follow these structures:

1. **Single Object Response**:
   ```json
   {
     "data": T
   }
   ```
2. **List Objects Response**:
   ```json
   {
     "total": number,
     "data": [T]
   }
   ```
   *Implement these using Pydantic inheritance for consistency.*

## Architecture Guidelines
- Follow Domain-Driven Design (DDD) principles.
- Use `dependency-injector` for all DI needs.
- Maintain consistency with existing async patterns (FastAPI + SQLAlchemy Async).
- **DateTime Standards**:
  - Always use `datetime.now(timezone.utc)` instead of the deprecated `datetime.utcnow()`.
  - Database columns should always use `TIMESTAMP WITH TIME ZONE`.
  - Application logic should handle all times in UTC.

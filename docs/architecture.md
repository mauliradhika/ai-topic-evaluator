# AI Topic Evaluator - System Architecture

## High-Level Architecture

```
                +----------------------+
                |     React Frontend   |
                +----------+-----------+
                           |
                     HTTP Requests
                           |
                           v
                +----------+-----------+
                |      FastAPI API     |
                +----------+-----------+
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
   Topic Engine     AI Evaluation     Session Manager
          |                |                |
          +----------------+----------------+
                           |
                           v
                    PostgreSQL Database
```

---

## Major Modules

### 1. Frontend

Responsible for:

- User Interface
- Timers
- Topic Selection
- Response Capture
- Result Display

---

### 2. Backend

Responsible for:

- Business Logic
- Random Topic Selection
- Evaluation Requests
- Authentication
- API Endpoints

---

### 3. Database

Stores:

- Users
- Topics
- Subtopics
- References
- Sessions
- Evaluations

---

### 4. AI Engine

Responsible for:

- Evaluating responses
- Applying weighted rubrics
- Generating personalized feedback
- Returning structured JSON
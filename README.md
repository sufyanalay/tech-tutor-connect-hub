
# Education and Gadget Repair Platform API

A comprehensive Django REST Framework backend for an education and gadget repair platform with features like user authentication, repair requests management, academic support, real-time chat, and resources hub.

## Features

- **User Authentication System**
  - Registration/Login for Students, Teachers, Technicians
  - JWT Authentication
  - Role-based access control

- **Online Gadget Repair System**
  - Submit repair requests with descriptions and media
  - Connect students with repair technicians
  - Track repair status

- **Academic Support System**
  - Submit academic questions with optional media
  - Connect students with teachers for help
  - Q&A functionality

- **Real-time Chat System**
  - WebSocket-based real-time chat via Django Channels
  - File/image sharing in chat

- **Rating and Feedback System**
  - Rate and review service providers
  - View average ratings

- **Earning Dashboard**
  - Track total earnings and completed services
  - Service history

- **Resources Hub**
  - Upload and retrieve tutorials and guides
  - Categorize educational resources

## Getting Started

### Prerequisites

- Python 3.8 or higher
- SQLite database (included)

### Installation

1. Clone the repository:
```bash
git clone https://your-repository-url.git
cd education-repair-platform
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser (admin):
```bash
python manage.py createsuperuser
```

6. Start the development server:
```bash
python manage.py runserver
```

The API will be available at http://localhost:8000/api/

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## Authentication

The API uses JWT (JSON Web Token) authentication. To get an access token:

```
POST /api/users/token/
{
  "email": "your-email@example.com",
  "password": "your-password"
}
```

Use the token in subsequent requests in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Key Endpoints

- Users: `/api/users/`
- Authentication: `/api/users/token/`
- Repair Requests: `/api/repairs/requests/`
- Academic Questions: `/api/academics/questions/`
- Chat Rooms: `/api/chat/rooms/`
- Messages: `/api/chat/messages/`
- Resources: `/api/resources/resources/`

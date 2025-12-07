# API Documentation

Smart Registration Services provides a comprehensive RESTful API for managing course registration, planning, and collaboration.

## Base URL

- Development: `http://localhost:8000/api/`
- Production: `https://your-domain.com/api/`

## Authentication

The API uses session-based authentication integrated with CAS. For API access, you can also use:
- Session Authentication (browser-based)
- Token Authentication (to be implemented for mobile apps)

### Login
```
POST /accounts/login/
```

### Logout
```
GET /accounts/logout/
```

## Interactive Documentation

The API includes interactive documentation powered by Swagger and ReDoc:

- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **OpenAPI Schema**: `/api/schema/`

## Endpoints Overview

### Course Catalog

#### List Courses
```
GET /api/courses/
```

Query Parameters:
- `department` - Filter by department (e.g., "Computer Science")
- `level` - Filter by level (FRESHMAN, SOPHOMORE, JUNIOR, SENIOR, GRADUATE)
- `credits` - Filter by credit hours
- `search` - Search in course code, title, or description
- `ordering` - Order by field (course_code, title, department, credits)
- `page` - Page number for pagination
- `page_size` - Results per page (default: 20)

Example:
```bash
curl "http://localhost:8000/api/courses/?department=Computer%20Science&level=FRESHMAN"
```

Response:
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "course_code": "CS101",
      "title": "Introduction to Computer Science",
      "description": "Fundamental concepts of computer science...",
      "credits": 3,
      "department": "Computer Science",
      "level": "FRESHMAN",
      "prerequisites": [],
      "prerequisite_details": [],
      "is_active": true,
      "created_at": "2024-12-02T14:00:00Z",
      "updated_at": "2024-12-02T14:00:00Z"
    }
  ]
}
```

#### Get Course Details
```
GET /api/courses/{id}/
```

Example:
```bash
curl "http://localhost:8000/api/courses/1/"
```

#### Search Courses
```
GET /api/courses/?search=database
```

Full-text search across course code, title, and description.

### Course Sections

#### List Course Sections
```
GET /api/sections/
```

Query Parameters:
- `term` - Filter by term (e.g., "Fall", "Spring")
- `year` - Filter by year (e.g., 2024)
- `course__department` - Filter by department
- `meeting_days` - Filter by meeting days (e.g., "MWF", "TTH")
- `search` - Search course code, title, section number, instructor
- `ordering` - Order by field
- `page` - Page number
- `page_size` - Results per page

Example:
```bash
curl "http://localhost:8000/api/sections/?term=Fall&year=2024"
```

Response:
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "course": 1,
      "course_details": {
        "id": 1,
        "course_code": "CS101",
        "title": "Introduction to Computer Science",
        "description": "...",
        "credits": 3,
        "department": "Computer Science",
        "level": "FRESHMAN",
        "prerequisites": [],
        "prerequisite_details": [],
        "is_active": true
      },
      "section_number": "001",
      "term": "Fall",
      "year": 2024,
      "instructor": 2,
      "instructor_name": "John Smith",
      "max_enrollment": 30,
      "current_enrollment": 0,
      "location": "CS Building 101",
      "meeting_days": "MWF",
      "start_time": "09:00:00",
      "end_time": "10:00:00",
      "is_available": true,
      "is_full": false,
      "available_seats": 30,
      "created_at": "2024-12-02T14:00:00Z",
      "updated_at": "2024-12-02T14:00:00Z"
    }
  ]
}
```

#### Get Section Details
```
GET /api/sections/{id}/
```

#### Get Available Sections
```
GET /api/sections/available/
```

Returns only sections with available seats.

Example:
```bash
curl "http://localhost:8000/api/sections/available/?term=Fall&year=2024"
```

## Future API Endpoints

The following endpoints are planned for implementation:

### Student Planning

#### List Student Plans
```
GET /api/plans/
```

#### Create Student Plan
```
POST /api/plans/
```

Request Body:
```json
{
  "name": "Fall 2024 Schedule",
  "term": "Fall",
  "year": 2024,
  "notes": "My planned courses for Fall semester"
}
```

#### Get Plan Details
```
GET /api/plans/{id}/
```

#### Update Plan
```
PUT /api/plans/{id}/
PATCH /api/plans/{id}/
```

#### Delete Plan
```
DELETE /api/plans/{id}/
```

#### Add Course to Plan
```
POST /api/plans/{id}/add_course/
```

Request Body:
```json
{
  "section_id": 1,
  "priority": 1,
  "notes": "Required for major"
}
```

#### Remove Course from Plan
```
POST /api/plans/{id}/remove_course/
```

#### Submit Plan for Review
```
POST /api/plans/{id}/submit/
```

#### Check Schedule Conflicts
```
GET /api/plans/{id}/conflicts/
```

### Registration

#### List Enrollments
```
GET /api/enrollments/
```

#### Register for Course
```
POST /api/enrollments/
```

Request Body:
```json
{
  "section_id": 1
}
```

#### Drop Course
```
DELETE /api/enrollments/{id}/
```

#### List Registration Requests
```
GET /api/registration-requests/
```

#### Submit Registration Request
```
POST /api/registration-requests/
```

Request Body:
```json
{
  "plan_id": 1,
  "notes": "Ready to register for Fall 2024"
}
```

### Advisor Collaboration

#### List Assigned Students (Advisors)
```
GET /api/advisor/students/
```

#### List Pending Plans (Advisors)
```
GET /api/advisor/pending-plans/
```

#### Approve Plan
```
POST /api/advisor/plans/{id}/approve/
```

Request Body:
```json
{
  "comments": "Approved. Good course selection."
}
```

#### Reject Plan
```
POST /api/advisor/plans/{id}/reject/
```

Request Body:
```json
{
  "comments": "Please add MATH101 as prerequisite."
}
```

#### Add Comment to Plan
```
POST /api/advisor/plans/{id}/comments/
```

Request Body:
```json
{
  "comment": "Consider taking CS201 in Spring instead.",
  "requires_change": false
}
```

#### List Messages
```
GET /api/messages/
```

#### Send Message
```
POST /api/messages/
```

Request Body:
```json
{
  "recipient_id": 5,
  "message": "Your plan looks good!",
  "plan_id": 1
}
```

### AI Recommendations

#### Get Course Recommendations
```
GET /api/recommendations/
```

Query Parameters:
- `term` - Target term
- `year` - Target year
- `limit` - Number of recommendations (default: 10)

Response:
```json
{
  "recommendations": [
    {
      "course": {
        "id": 2,
        "course_code": "CS201",
        "title": "Data Structures and Algorithms"
      },
      "score": 0.95,
      "reasoning": "Recommended based on your completion of CS101 and your major requirements.",
      "term": "Fall",
      "year": 2024
    }
  ]
}
```

#### Submit Recommendation Feedback
```
POST /api/recommendations/{id}/feedback/
```

Request Body:
```json
{
  "rating": 5,
  "comment": "Very helpful recommendation!"
}
```

### Notifications

#### List Notifications
```
GET /api/notifications/
```

Query Parameters:
- `is_read` - Filter by read status (true/false)
- `notification_type` - Filter by type

#### Mark Notification as Read
```
POST /api/notifications/{id}/mark_read/
```

#### Mark All as Read
```
POST /api/notifications/mark_all_read/
```

#### Get Notification Preferences
```
GET /api/notifications/preferences/
```

#### Update Notification Preferences
```
PUT /api/notifications/preferences/
```

Request Body:
```json
{
  "email_notifications": true,
  "push_notifications": true,
  "registration_deadlines": true,
  "meeting_reminders": true,
  "schedule_changes": true,
  "advisor_actions": true,
  "new_messages": true
}
```

## WebSocket API

### Chat WebSocket

Connect to advisor-student chat:
```
ws://localhost:8000/ws/chat/{room_name}/
```

Send message:
```json
{
  "message": "Hello, I have a question about my schedule.",
  "sender_id": 1,
  "recipient_id": 2
}
```

Receive message:
```json
{
  "message": "Hello! How can I help you?",
  "sender_id": 2,
  "timestamp": "2024-12-02T14:30:00Z"
}
```

## Error Handling

The API uses standard HTTP status codes:

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `204 No Content` - Successful request with no response body
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error Response Format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

Or for validation errors:
```json
{
  "field_name": [
    "Error message for this field"
  ]
}
```

## Rate Limiting

API rate limiting is not currently implemented but is planned for production:
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Burst limit: 10 requests/second

## Pagination

All list endpoints support pagination:

Request:
```
GET /api/courses/?page=2&page_size=10
```

Response:
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/courses/?page=3&page_size=10",
  "previous": "http://localhost:8000/api/courses/?page=1&page_size=10",
  "results": [...]
}
```

## Filtering

Many endpoints support filtering using query parameters:

```
GET /api/courses/?department=Computer%20Science&credits=3
```

## Searching

Full-text search is available on many endpoints:

```
GET /api/courses/?search=database
```

## Ordering

Results can be ordered using the `ordering` parameter:

```
GET /api/courses/?ordering=course_code
GET /api/courses/?ordering=-credits  # Descending order
```

## Best Practices

1. **Use pagination** for large result sets
2. **Cache responses** when appropriate
3. **Use filters** to reduce response size
4. **Handle errors** gracefully in your client
5. **Include authentication** credentials with requests
6. **Validate input** before sending requests
7. **Use HTTPS** in production

## Examples

### Python (using requests)

```python
import requests

# Login (session-based)
session = requests.Session()
session.post('http://localhost:8000/accounts/login/', data={
    'username': 'student1',
    'password': 'password123'
})

# Get courses
response = session.get('http://localhost:8000/api/courses/')
courses = response.json()

# Search for specific course
response = session.get('http://localhost:8000/api/courses/', params={
    'search': 'database',
    'department': 'Computer Science'
})
results = response.json()['results']
```

### JavaScript (using fetch)

```javascript
// Get courses
fetch('http://localhost:8000/api/courses/')
  .then(response => response.json())
  .then(data => {
    console.log('Courses:', data.results);
  })
  .catch(error => console.error('Error:', error));

// Get sections for Fall 2024
fetch('http://localhost:8000/api/sections/?term=Fall&year=2024')
  .then(response => response.json())
  .then(data => {
    console.log('Sections:', data.results);
  });
```

### cURL

```bash
# Get all courses
curl http://localhost:8000/api/courses/

# Search for courses
curl "http://localhost:8000/api/courses/?search=computer"

# Get specific course
curl http://localhost:8000/api/courses/1/

# Get available sections
curl "http://localhost:8000/api/sections/available/?term=Fall&year=2024"
```

## Support

For API questions or issues:
1. Check the interactive documentation at `/api/docs/`
2. Review code examples in the repository
3. Open an issue on GitHub
4. Contact the development team

## Changelog

### Version 1.0.0 (Current)
- Initial API release
- Course catalog endpoints
- Course section endpoints
- Basic authentication
- API documentation

### Planned Features
- Student planning endpoints
- Registration endpoints
- Advisor collaboration endpoints
- AI recommendation endpoints
- Notification endpoints
- WebSocket chat implementation
- Rate limiting
- API versioning
- Token authentication

---

## Student Planning API

### Student Plans

#### List My Plans
```
GET /api/plans/
```

Returns plans for the current user based on role:
- Students: their own plans
- Advisors: plans assigned to them
- Registrar: all plans

#### Get Plan Details
```
GET /api/plans/{id}/
```

Returns detailed plan with courses, conflicts, and total credits.

#### Create Plan
```
POST /api/plans/
```

Request Body:
```json
{
  "name": "Fall 2024 Schedule",
  "term": "Fall",
  "year": 2024,
  "notes": "Optional notes"
}
```

#### Add Course to Plan
```
POST /api/plans/{id}/add_course/
```

Request Body:
```json
{
  "section_id": 1,
  "priority": 0,
  "notes": "Optional notes"
}
```

Automatically checks prerequisites and returns error if not met.

#### Remove Course from Plan
```
POST /api/plans/{id}/remove_course/
```

#### Detect Conflicts
```
POST /api/plans/{id}/detect_conflicts/
```

Runs conflict detection and returns all detected conflicts.

#### Submit Plan for Approval
```
POST /api/plans/{id}/submit/
```

Students can submit draft plans for advisor review.

#### Approve/Reject Plan (Advisors Only)
```
POST /api/plans/{id}/approve/
POST /api/plans/{id}/reject/
```

---

## Registration & Enrollment API

### Enrollment Actions

#### Enroll in Course
```
POST /api/registration-actions/enroll/
```

Request Body:
```json
{
  "section_id": 1
}
```

Automatically checks prerequisites, detects conflicts, and enrolls or waitlists based on capacity.

#### Drop Course
```
POST /api/registration-actions/drop/
```

Request Body:
```json
{
  "enrollment_id": 1
}
```

#### Check Enrollment Eligibility
```
POST /api/registration-actions/check_eligibility/
```

Returns eligibility status with prerequisites, conflicts, and capacity information.

### Registration Requests

#### Create Registration Request
```
POST /api/registration-requests/
```

Request Body:
```json
{
  "plan": 1,
  "notes": "Please approve my registration"
}
```

#### Approve/Reject Request (Advisors Only)
```
POST /api/registration-requests/{id}/approve_reject/
```

Request Body:
```json
{
  "action": "approve",
  "advisor_comments": "Optional comments"
}
```

---

## Example Workflows

### Student Registration Workflow

1. Search for courses: `GET /api/sections/search_sections/?term=Fall&year=2024`
2. Check eligibility: `POST /api/registration-actions/check_eligibility/`
3. Enroll in course: `POST /api/registration-actions/enroll/`

### Plan Creation Workflow

1. Create a plan: `POST /api/plans/`
2. Add courses: `POST /api/plans/{id}/add_course/`
3. Check for conflicts: `POST /api/plans/{id}/detect_conflicts/`
4. Submit for approval: `POST /api/plans/{id}/submit/`


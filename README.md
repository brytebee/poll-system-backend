# Poll System Backend

A robust Django REST API for creating and managing online polls with real-time voting capabilities.

## Features

- **Custom User Authentication** with extended profile fields
- **Poll Management** with categories and expiration dates
- **Flexible Voting** supporting anonymous and authenticated users
- **Real-time Results** with hybrid calculation approach
- **Multi-choice Support** for complex poll scenarios
- **Result Persistence** for finalized polls
- **UUID-based** primary keys for enhanced security

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: Django Custom User Model
- **API**: RESTful with CORS support

## Architecture

### Core Entities

- **User**: Custom authentication with profile fields
- **Category**: Poll categorization system
- **Poll**: Main poll entity with settings and metadata
- **Option**: Individual poll choices
- **Vote**: Voting records with duplicate prevention
- **VoteSession**: Anonymous voting session management
- **PollResult**: Cached results for finalized polls

### Key Features

- UUID primary keys across all entities
- Hybrid result calculation (live during voting, cached after)
- Constraint-based duplicate vote prevention
- Support for both anonymous and authenticated voting

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip/pipenv

### Installation

1. **Clone and setup environment**

   ```bash
   git clone <repository-url>
   cd poll-system-backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Database setup**

   ```bash
   createdb poll_system
   cp .env.example .env  # Configure your database credentials
   ```

4. **Run migrations**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Start development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000/admin/` to access the admin interface.

## Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DB_NAME=poll_system
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

## Project Structure

```
poll-system-backend/
├── poll_system/           # Main project configuration
│   ├── settings/          # Split settings (base, dev, prod)
│   ├── urls.py
│   └── wsgi.py
├── apps/                     # All Django apps
│   ├── __init__.py
│   ├── authentication/       # Custom user management
│   ├── polls/               # Core poll functionality
│   ├── analytics/           # Reporting and insights
│   └── common/              # Shared utilities
├── static/               # Static files
├── media/                # User uploads
├── requirements.txt
└── manage.py
```

## API Design Philosophy

### Voting Logic

- **Active Polls**: Results calculated in real-time
- **Finalized Polls**: Results served from cached `PollResult` table
- **Duplicate Prevention**: Constraint-based for data integrity
- **Anonymous Support**: IP-based tracking with session management

### Data Modeling

- **UUID Primary Keys**: Enhanced security and distributed system support
- **Soft Relationships**: Foreign keys with proper cascading
- **Timestamp Tracking**: `created_at` and `updated_at` on all entities
- **Flexible Constraints**: Support for both anonymous and authenticated workflows

## Development

### Running Tests

```bash
python manage.py test
```

### Database Operations

```bash
# Create new migration
python manage.py makemigrations app_name

# Apply migrations
python manage.py migrate

# Reset database (development only)
python manage.py flush
```

### Code Quality

- Follow PEP 8 style guidelines
- Use meaningful variable names
- Document complex business logic
- Write tests for critical functionality

## Deployment Considerations

### Security

- Change `SECRET_KEY` in production
- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS`
- Use environment variables for sensitive data

### Performance

- Configure database connection pooling
- Implement caching for frequently accessed data
- Consider read replicas for high-traffic scenarios
- Monitor query performance with Django Debug Toolbar

### Scalability

- Horizontal scaling supported via UUID primary keys
- Stateless API design for load balancing
- Database indexing on frequently queried fields
- Background job support for result finalization

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- Create an issue in this repository
- Check the [documentation](docs/) folder
- Review the [API documentation](docs/api.md) (coming soon)

---

**Status**: 🚧 Development Phase - Day 2 Complete
**Next Steps**: API endpoints for Poll and Vote CRUD

# polls/schema.py
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import status

# Poll ViewSet Schema
poll_list_examples = [
    OpenApiExample(
        'Poll List Response',
        summary='Successful poll list',
        description='List of polls with pagination',
        value={
            "count": 25,
            # TODO: Update link
            "next": "http://localhost:8000/api/polls/?page=2",
            "previous": None,
            "results": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Best Programming Language?",
                    "description": "Vote for your favorite programming language",
                    "created_by": {
                        "id": "123e4567-e89b-12d3-a456-426614174001",
                        "username": "techuser",
                        "display_name": "Tech User"
                    },
                    "category": {
                        "id": "123e4567-e89b-12d3-a456-426614174002",
                        "name": "Technology",
                        "slug": "technology"
                    },
                    "total_votes": 150,
                    "options_count": 4,
                    "is_active": True,
                    "can_vote": True,
                    "created_at": "2024-01-15T10:30:00Z"
                }
            ]
        },
        response_only=True,
        status_codes=[status.HTTP_200_OK]
    )
]

poll_create_examples = [
    OpenApiExample(
        'Create Poll Request',
        summary='Create a new poll',
        description='Example request to create a new poll with options',
        value={
            "title": "What's the best web framework?",
            "description": "Help us decide the best web framework for beginners",
            "category_id": "123e4567-e89b-12d3-a456-426614174002",
            "is_anonymous": False,
            "multiple_choice": False,
            "expires_at": "2024-02-15T10:30:00Z",
            "options": [
                {"text": "Django", "order_index": 1},
                {"text": "React", "order_index": 2},
                {"text": "Vue.js", "order_index": 3},
                {"text": "Angular", "order_index": 4}
            ]
        },
        request_only=True
    )
]

vote_examples = [
    OpenApiExample(
        'Single Choice Vote',
        summary='Vote for single option',
        description='Cast a vote for a single option',
        value={
            "option_id": "123e4567-e89b-12d3-a456-426614174003"
        },
        request_only=True
    ),
    OpenApiExample(
        'Multiple Choice Vote',
        summary='Vote for multiple options',
        description='Cast votes for multiple options (multiple choice polls only)',
        value={
            "options": [
                "123e4567-e89b-12d3-a456-426614174003",
                "123e4567-e89b-12d3-a456-426614174004"
            ]
        },
        request_only=True
    )
]

# Schema decorators for views
poll_schema = extend_schema_view(
    list=extend_schema(
        summary="List Polls",
        description="Retrieve a paginated list of polls with filtering and search capabilities",
        parameters=[
            OpenApiParameter(name='category', type=OpenApiTypes.UUID, description='Filter by category ID'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter active polls'),
            OpenApiParameter(name='search', type=OpenApiTypes.STR, description='Search polls by title/description'),
            OpenApiParameter(name='ordering', type=OpenApiTypes.STR, description='Order by: created_at, title, expires_at'),
        ],
        examples=poll_list_examples,
        tags=['Polls']
    ),
    create=extend_schema(
        summary="Create Poll",
        description="Create a new poll with options. Requires authentication.",
        examples=poll_create_examples,
        tags=['Polls']
    ),
    retrieve=extend_schema(
        summary="Get Poll Details",
        description="Retrieve detailed information about a specific poll including options",
        tags=['Polls']
    ),
    update=extend_schema(
        summary="Update Poll",
        description="Update poll details. Only poll owner can update.",
        tags=['Polls']
    ),
    destroy=extend_schema(
        summary="Delete Poll",
        description="Delete a poll. Only poll owner can delete.",
        tags=['Polls']
    ),
    vote=extend_schema(
        summary="Vote on Poll",
        description="Cast a vote on a poll. Supports single and multiple choice voting.",
        examples=vote_examples,
        tags=['Polls']
    ),
    results=extend_schema(
        summary="Get Poll Results",
        description="Get real-time or finalized poll results",
        tags=['Polls']
    ),
    finalize=extend_schema(
        summary="Finalize Poll Results",
        description="Finalize poll results and stop accepting votes. Only poll owner can finalize.",
        tags=['Polls']
    )
)

category_schema = extend_schema_view(
    list=extend_schema(
        summary="List Categories",
        description="Get list of poll categories",
        parameters=[
            OpenApiParameter(
                name='active_only',
                type=OpenApiTypes.BOOL,
                description='Filter categories with active polls only'
            )
        ],
        tags=['Categories']
    ),
    retrieve=extend_schema(
        summary="Get Category Details",
        description="Get detailed information about a specific category",
        tags=['Categories']
    )
)

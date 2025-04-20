# ShareTunes Project Development Guidelines

## Development Workflow
- Follow GitHub Flow process when developing new features
- Create feature branches from main
- Make small, frequent commits
- Open pull requests early for discussion
- Push changes to remote environment before merging
- Create branches with descriptive names related to the feature/fix
- Delete feature branches after merging to main

## Repository Information
- Remote repository: https://github.com/lalalasyun/ShareTunesApp
- Main branch: main
- Clone with: `git clone https://github.com/lalalasyun/ShareTunesApp.git`
- Always create pull requests to the main branch for code reviews

## Commit Messages
- Follow Conventional Commits format
- Write commit messages in English
- Format: `type(scope): description`
- Common types: feat, fix, docs, style, refactor, test, chore
- Example: `feat(playlist): add shuffle functionality to playlist player`

## Code Comments
- All comments in code must be written in English
- Use descriptive comments for complex logic
- Document public functions and classes with appropriate documentation style

## Technologies
- Backend: Django REST Framework (Python)
- Frontend: Next.js with TypeScript
- Database: SQLite (Development), PostgreSQL (Production)
- Containerization: Docker and Docker Compose

## Architecture
- Microservices-inspired architecture
- Backend modules: users, tracks, playlists, recommendations, feedbacks
- RESTful API endpoints for all resources
- Frontend components follow atomic design principles

## Testing
- Write unit tests for critical functionality
- Ensure API endpoints are tested
- Frontend components should have appropriate tests

## Security
- Follow best practices for authentication and authorization
- Sanitize user inputs
- Protect sensitive user data
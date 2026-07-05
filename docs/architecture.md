# Architecture

This project follows a three-layer architecture:

1. Presentation layer: Flask templates, CSS, and JavaScript provide the user experience.
2. Application layer: Flask routes and service objects contain business logic and validation.
3. Data layer: SQLAlchemy models and repository functions manage database access.

The application factory pattern keeps configuration and initialization centralized.

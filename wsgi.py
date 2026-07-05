"""WSGI entry point for deployment."""

from app import create_app

app = create_app("production")

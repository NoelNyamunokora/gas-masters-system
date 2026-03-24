"""
WSGI entry point for Gunicorn
"""
import sys
import traceback

try:
    from app import create_app
    app = create_app()
    print("✓ Application created successfully", file=sys.stderr)
except Exception as e:
    print(f"✗ Failed to create application: {str(e)}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    app.run()

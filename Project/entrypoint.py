try:
    from app import create_app
except ImportError:
    from .app import create_app
    
app = create_app("config.py")
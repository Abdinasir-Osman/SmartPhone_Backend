from dotenv import load_dotenv
import os

load_dotenv()  # Load the .env file

from alembic import context

# Load Alembic config object
config = context.config

# ✅ Set sqlalchemy URL from .env
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Continue with your usual Alembic setup below...

import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from db.base import Base

load_dotenv()

url = os.getenv('DATABASE_URL')
if url and url.startswith('postgres://'):
    url = url.replace('postgres://', 'postgresql://', 1)

print("Connecting to DB...")
engine = create_engine(url)
Base.metadata.create_all(bind=engine)
print('✅ Tables created successfully!')

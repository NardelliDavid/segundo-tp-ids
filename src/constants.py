import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL='/MYAPP'



DB_CONFIG={
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '1234'),
    'database': os.getenv('DB_NAME', 'club_deportivo')
}
DEFAULT_LIMIT=10
MAX_LIMIT=100
MIN_LIMIT=1
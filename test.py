import jwt
from datetime import datetime

from config import settings

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NzRhMmEwOC1jODU0LTRiMjQtOWIxNC1iNDE2NTg3YTg0YTciLCJleHAiOjE3NzI3MTE5NTAsImlhdCI6MTc3MjcxMDE1MCwidHlwZSI6ImFjY2VzcyJ9.-3N3fBCFjwdZf0asSk3ZKrRLW1K7Ys0fCk5qsOTgMAo"
decoded = jwt.decode(token, settings.jwt.secret_key, algorithms=["HS256"], options={"verify_exp": False})
print(decoded)

exp = decoded["exp"]
now = datetime.now().timestamp()

if now > exp:
    print("Token is expired")
else:
    print("Token is valid")
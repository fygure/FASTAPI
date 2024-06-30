from dotenv import load_dotenv, find_dotenv
import os

#Find .env file automatically
dotenv_path = find_dotenv()

#Load the .env file w/ params
load_dotenv(dotenv_path=dotenv_path, verbose=True, override=True, encoding="utf-8")

#Access .env variables
secret_key = os.getenv('FOO')

print(secret_key)

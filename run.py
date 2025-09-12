from flask_ngrok import run_with_ngrok
from app import main

run_with_ngrok(main)

if __name__ == "__main__":
    main.run()

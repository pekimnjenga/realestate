from app import create_app

app = create_app()

if __name__ == "__main__":
    # Bind explicitly to localhost to avoid attempting to bind to a
    # production `SERVER_NAME` from the environment during local development.
    app.run(host="127.0.0.1", debug=True, load_dotenv=False)

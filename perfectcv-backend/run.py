from app import create_app

app = create_app()

if __name__ == '__main__':
    # Disable reloader to prevent WinError 10038 on Windows/Python 3.13
    app.run(debug=True, use_reloader=False)
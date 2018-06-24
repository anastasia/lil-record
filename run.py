from web.app import app
app.config.from_pyfile('../settings/settings.py')

if __name__ == "__main__":
    app.run()



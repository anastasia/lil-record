from web import app
app.config.from_pyfile('../settings/settings.py')

app.run(debug=True)

if __name__ == "__main__":
    app.run()

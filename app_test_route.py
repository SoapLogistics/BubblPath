from app import app
from flask import render_template

@app.route("/god-eye-ui")
def god_eye_ui():
    return render_template("god_eye.html")

if __name__ == "__main__":
    app.run(port=18789)

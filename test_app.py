from flask import Flask, url_for, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return f"<a href='{url_for('purchases')}'>Go to Purchases</a>"

@app.route('/purchases')
def purchases():
    return "This is the purchases page."

if __name__ == '__main__':
    app.run(debug=True)
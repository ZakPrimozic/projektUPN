
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def glavna_stran():
    return render_template("glavna.html")

@app.route('/1letnik')
def letnik1():
    return render_template("1letnik.html")
if __name__ == '__main__':
    app.run(debug=True, port=8080)
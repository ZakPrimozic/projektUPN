from flask import Flask, render_template, request, jsonify
from tinydb import TinyDB, Query

app = Flask(__name__)

db = TinyDB("uporabni.json") 
User = Query()

@app.route('/')
def glavna_stran():
    return render_template("glavna.html")

@app.route('/1letnik')
def letnik1():
    return render_template("1letnik.html")


@app.route("/prijava")
def prijava():
    return render_template("prijava.html")


@app.route("/shrani", methods=["POST"])
def shrani_uporabnika():
    nova_vnos = request.get_json()
    
    if not nova_vnos:
        return jsonify({"error": "Manjkajo podatki!"}), 400

    db.insert(nova_vnos)  
    return jsonify({"message": "Podatki shranjeni!"}), 201

@app.route("/uporabniki", methods=["GET"])
def pridobi_uporabnike():
    return jsonify(db.all())

if __name__ == '__main__':
    app.run(debug=True, port=8080)

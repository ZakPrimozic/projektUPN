from flask import Flask, render_template, request, jsonify
from tinydb import TinyDB, Query
import json
from datetime import datetime
app = Flask(__name__)

db = TinyDB("uporabni.json")
vprasanja_db = TinyDB("matura_vprasanja.json")
rez_db = TinyDB('rezultati.json')
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
    
@app.route('/graf_mature', methods=['GET'])
def graf_mature():
    podatki = {
        "skupno": 6294,
        "uspesno": 5592,
        "neuspesno": 702
    }
    return jsonify(podatki)


def nalozi_vprasanja():
    with open("matura_vprasanja.json", "r", encoding="utf-8") as f:
        return json.load(f)
    

@app.route("/matura", methods=["GET", "POST"])
def kviz():
    vprasanja = nalozi_vprasanja()
    rezultati = []

    if request.method == "POST":
        for i, v in enumerate(vprasanja):
            uporabnikov_odgovor = request.form.get(f"odgovor_{i}")
            pravilen = str(v["odgovor"]).lower()
            rezultat = {
                "naslov": v["naslov"],
                "vprasanje": v["vprasanje"],
                "pravilen": pravilen,
                "uporabnikov": uporabnikov_odgovor,
                "je_pravilen": uporabnikov_odgovor == pravilen
            }
            rezultati.append(rezultat)
        pravilni = sum(1 for r in rezultati if r["je_pravilen"])
        napacni = len(rezultati) - pravilni
        return render_template(
            "matura.html",
            rezultati=rezultati,
            pravilni=pravilni,
            napacni=napacni
        )
    return render_template("matura.html", vprasanja=vprasanja)


@app.route('/shrani_rezultat', methods=['POST'])
def shrani_rezultat():
    podatki = request.json
    uporabnik = podatki['uporabnik']
    obstaja = db.search(User.ime == uporabnik)
    rezultat = {
        'uporabnik': uporabnik,
        'tocke': podatki['tocke'],
        'skupno': podatki['skupno'],
        'datum': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    rez_db.insert(rezultat)
    return jsonify({"sporocilo": "Rezultat shranjen!"}), 200
if __name__ == '__main__':
    app.run(debug=True, port=8080)

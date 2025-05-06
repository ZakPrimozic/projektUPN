from flask import Flask, render_template, request, jsonify, session, redirect
from tinydb import TinyDB, Query
import json
from datetime import datetime
import random
from gemini_api import generate_gemini_response
app = Flask(__name__)
app.secret_key = 'ključ'
db = TinyDB("uporabni.json")
vprasanja_db = TinyDB("matura_vprasanja.json")
vprasanja_api_db = TinyDB("db.json")
rez_db = TinyDB('rezultati.json')
User = Query()
# ------------------------------------------------------------------------------------------------------- 
@app.route('/')
def glavna_stran():
    return render_template("glavna.html")
# ------------------------------------------------------------------------------------------------------- 
@app.route('/1letnik')
def letnik1():
    return render_template("1letnik.html")

# ------------------------------------------------------------------------------------------------------- 
@app.route("/prijava")
def prijava():
    return render_template("prijava.html")

# ------------------------------------------------------------------------------------------------------- 
@app.route("/shrani", methods=["POST"])
def shrani_uporabnika():
    if session.get("logged_in"):
        return jsonify({"message": "Uporabnik je že prijavljen!"}), 400
    nova_vnos = request.get_json()
    
    if not nova_vnos:
        return jsonify({"error": "Manjkajo podatki!"}), 400

    db.insert(nova_vnos)
    session["logged_in"] = True
    session["username"] = nova_vnos.get("ime", "")
    return jsonify({"message": "Podatki shranjeni!"}), 201
# ------------------------------------------------------------------------------------------------------- 
@app.route("/odjava")
def odjava():
    session.clear()
    return redirect("/")
# ------------------------------------------------------------------------------------------------------- 
@app.route("/uporabniki", methods=["GET"])
def pridobi_uporabnike():
    return jsonify(db.all())
# -------------------------------------------------------------------------------------------------------   
@app.route('/graf_mature', methods=['GET'])
def graf_mature():
    podatki = {
        "skupno": 6294,
        "uspesno": 5592,
        "neuspesno": 702
    }
    return jsonify(podatki)

# ------------------------------------------------------------------------------------------------------- 
def nalozi_vprasanja():
    with open("matura_vprasanja.json", "r", encoding="utf-8") as f:
        return json.load(f)
    
# ------------------------------------------------------------------------------------------------------- 
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
# ------------------------------------------------------------------------------------------------------- 
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

# se nedela pravilno
# ------------------------------------------------------------------------------------------------------- 
@app.route('/dnevno_vprasanje', methods=['GET', 'POST'])
def dnevno_vprasanje():
    vprasanja = nalozi_vprasanja()
    danes = datetime.now().strftime('%Y-%m-%d')
    random.seed(danes)
    vprasanje = random.choice(vprasanja)
    prikazi = False
    je_pravilen = False

    if request.method == 'POST':
        odgovor = request.form.get("odgovor", "")
        pravilen = str(vprasanje.get("odgovor", ""))
        je_pravilen = odgovor.lower() == pravilen.lower()
        prikazi = True

    return render_template("dnevni_kviz.html",vprasanje=vprasanje,prikazi_rezultat=prikazi,je_pravilen=je_pravilen)
# ------------------------------------------------------------------------------------------------------- 
@app.route('/generate-question', methods=['POST'])
def generate_question():
    data = request.get_json()
    prompt = data.get('prompt')
    print("PRIMLJEN PROMPT:", prompt)

    result = generate_gemini_response(prompt)
    print("ODGOVOR GEMINI:", result)

    if 'error' in result:
        return jsonify(result), 500

    try:
        questions = json.loads(result['response'])
        vprasanja_api_db.truncate()
        vprasanja_api_db.insert_multiple(questions)
        return jsonify({"message": "Generated and saved questions successfully!"})
    except json.JSONDecodeError:
        print("NAPAKA PRI JSON:", result['response'])
        return jsonify({"error": "Gemini ni vrnil veljavnega JSON."}), 500
# -------------------------------------------------------------------------------------------------------
@app.route('/2letnik')
def vprasanja_2letnik():
    vprasanja = vprasanja_api_db.all()
    return render_template('2letnik.html', vprasanja=vprasanja)
# -------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=8080)

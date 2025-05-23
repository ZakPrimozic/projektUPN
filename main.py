from flask import Flask, render_template, request, jsonify, session, redirect
from tinydb import TinyDB, Query
import json
from datetime import datetime
import random
# ------------------------------------------------------------------------------------------------------- 
app = Flask(__name__)
app.secret_key = "matejgay123"
# ------------------------------------------------------------------------------------------------------- 
db = TinyDB("uporabni.json")
vprasanja_db = TinyDB("matura_vprasanja.json")
rez_db = TinyDB("rezultati.json")
flash_db = TinyDB("flash_kartice.json")
mnenje_db = TinyDB("mnenja.json")
User = Query()
# ------------------------------------------------------------------------------------------------------- 
@app.route("/")
def glavna_stran():
    return render_template("glavna.html")
# ------------------------------------------------------------------------------------------------------- 
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
    session["priimek"] = nova_vnos.get("priimek", "")
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
@app.route("/graf_mature", methods=["GET"])
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
@app.route("/shrani_rezultat", methods=["POST"])
def shrani_rezultat():
    podatki = request.json
    uporabnik = session.get("username")
    priimek = session.get("priimek")
    rezultat = {
        "uporabnik": uporabnik,
        "priimek": priimek,
        "tocke": podatki["tocke"],
        "skupno": podatki["skupno"],
        "datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "kategorija": podatki.get("kategorija")
    }
    rez_db.insert(rezultat)
    return jsonify({"sporocilo": "Rezultat shranjen!"}), 200

# se nedela pravilno
# ------------------------------------------------------------------------------------------------------- 
@app.route("/dnevno_vprasanje", methods=["GET", "POST"])
def dnevno_vprasanje():
    vprasanja = nalozi_vprasanja()
    danes = datetime.now().strftime("%Y-%m-%d")
    random.seed(danes)
    vprasanje = random.choice(vprasanja)
    prikazi = False
    je_pravilen = False

    if request.method == "POST":
        odgovor = request.form.get("odgovor", "")
        pravilen = str(vprasanje.get("odgovor", ""))
        je_pravilen = odgovor.lower() == pravilen.lower()
        prikazi = True

    return render_template("dnevni_kviz.html",vprasanje=vprasanje,prikazi_rezultat=prikazi,je_pravilen=je_pravilen)
# ------------------------------------------------------------------------------------------------------- 
@app.route("/profil")
def profil():
    ime = session.get("username")
    priimek = session.get("priimek")
    podatki = db.get((User.ime == ime) & (User.priimek == priimek))
    rezultati = rez_db.search((User.uporabnik == ime) & (User.priimek == priimek))
    sola = podatki.get("sola")
    starost = podatki.get("starost")
    if rezultati:
        skupne_tocke = 0
        for r in rezultati:
            skupne_tocke += r["tocke"]
        povprecje = round(skupne_tocke / len(rezultati), 2)
    else:
        povprecje = 0
    return render_template("profil.html",uporabnik=f"{ime} {priimek}", sola=sola, starost=starost, rezultati=rezultati, povprecje=povprecje)
# ------------------------------------------------------------------------------------------------------- 
def vprasanja_2_letnik():
    with open("vp_2_letnik.json", "r", encoding="utf-8") as f:
        vprasanja = json.load(f)
    return vprasanja

def premesaj_vprasanja(vprasanja):
    random.shuffle(vprasanja)
    return vprasanja 
# ------------------------------------------------------------------------------------------------------- 
@app.route("/2letnik", methods=["GET", "POST"])
def kviz_2letnik():
    vprasanja = vprasanja_2_letnik()
    vprasanja = premesaj_vprasanja(vprasanja)

    if request.method == "POST":
        rezultati = []
        pravilni = 0
        for i in range(len(vprasanja)):
            odgovor = request.form.get(f"odgovor_{i}")
            pravilen = str(vprasanja[i]["odgovor"]).lower()
            en_rezultat = {
                "vprasanje": vprasanja[i]["vprasanje"],
                "pravilen": pravilen,
                "uporabnikov": odgovor,
                "je_pravilen": odgovor == pravilen
            }
            rezultati.append(en_rezultat)
            if odgovor == pravilen:
                pravilni += 1
        napacni =len(vprasanja)- pravilni
        return render_template("2letnik.html", rezultati=rezultati, pravilni=pravilni, napacni=napacni)
    return render_template("2letnik.html", vprasanja=vprasanja)
# -------------------------------------------------------------------------------------------------------
@app.route("/flash", methods=["GET", "POST"])
def flash_kartice():
    if request.method == "POST":
        podatki = request.get_json()
        nova = {
            "vprasanje": podatki["vprasanje"],
            "odgovor": podatki["odgovor"]
        }
        flash_db.insert(nova)
        return jsonify({"status": "dodano"}), 200
    kartice = flash_db.all()
    return render_template("flash.html", kartice=kartice)
# -------------------------------------------------------------------------------------------------------
@app.route("/mnenje", methods=["GET", "POST"])
def mnenjee():
    if request.method == "POST":
        ime = request.form.get("ime")
        besedilo = request.form.get("besedilo")
        mnenje_db.insert({
            "ime": ime,
            "besedilo": besedilo,
            "cas": datetime.now().strftime("%d.%m.%Y %H:%M")
        })
    vsa_mnenja = mnenje_db.all()
    return render_template("mnenje.html", mnenja = vsa_mnenja)
# -------------------------------------------------------------------------------------------------------
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        geslo = request.form.get("geslo")
        if geslo == "matejgay123":
            session["admin"] = True
            return redirect("/mnenje")
        else:
            return render_template("admin_prijava.html", napaka="Napačno geslo.")
    return render_template("admin_prijava.html")
# -------------------------------------------------------------------------------------------------------
@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/")
# -------------------------------------------------------------------------------------------------------
@app.route("/izbrisi_mnenje/<int:id>", methods=["POST"])
def izbrisi_mnenje(id):
    if session.get("admin"):
        mnenje_db.remove(doc_ids=[id])
    return redirect("/mnenje")
# -------------------------------------------------------------------------------------------------------

# se nedela 
def vprasanja_1_letnik():
    with open("vp_1_letnik.json", "r", encoding="utf-8") as f:
        vprasanja_1 = json.load(f)
    return vprasanja_1
# -------------------------------------------------------------------------------------------------------
def premesaj_vprasanja_1letnik(vprasanja_1):
    random.shuffle(vprasanja_1)
    return vprasanja_1
# -------------------------------------------------------------------------------------------------------
@app.route("/1letnik", methods=["GET", "POST"])
def kviz_1letnik():
    vprasanja_1 = vprasanja_1_letnik()
    vprasanja_1 = premesaj_vprasanja_1letnik(vprasanja_1)
    if request.method == "POST":
        rezultati = []
        pravilni = 0
        for i in range(len(vprasanja_1)):
            odgovor = request.form.get(f"odgovor_{i}")
            pravilen = str(vprasanja_1[i]["odgovor"]).lower()
            en_rezultat = {
                "vprasanje": vprasanja_1[i]["vprasanje"],
                "pravilen": pravilen,
                "uporabnikov": odgovor,
                "je_pravilen": odgovor == pravilen
            }
            rezultati.append(en_rezultat)
            if odgovor == pravilen:
                pravilni += 1
        napacni =len(vprasanja_1)- pravilni
        return render_template("1letnik.html", rezultati=rezultati, pravilni=pravilni, napacni=napacni)
    return render_template("1letnik.html", vprasanja_1=vprasanja_1)
# -------------------------------------------------------------------------------------------------------
def vprasanja_3_letnik():
    with open("vp_3_letnik.json", "r", encoding="utf-8") as f:
        vprasanja_3 = json.load(f)
    return vprasanja_3
# -------------------------------------------------------------------------------------------------------
def premesaj_vprasanja_3letnik(vprasanja_3):
    random.shuffle(vprasanja_3)
    return vprasanja_3
# -------------------------------------------------------------------------------------------------------
@app.route("/3letnik", methods=["GET", "POST"])
def kviz_3letnik():
    vprasanja_3 = vprasanja_3_letnik()
    vprasanja_3 = premesaj_vprasanja_3letnik(vprasanja_3)
    if request.method == "POST":
        rezultati = []
        pravilni = 0
        for i in range(len(vprasanja_3)):
            odgovor = request.form.get(f"odgovor_{i}")
            pravilen = str(vprasanja_3[i]["odgovor"]).lower()
            en_rezultat = {
                "vprasanje": vprasanja_3[i]["vprasanje"],
                "pravilen": pravilen,
                "uporabnikov": odgovor,
                "je_pravilen": odgovor == pravilen
            }
            rezultati.append(en_rezultat)
            if odgovor == pravilen:
                pravilni += 1
        napacni =len(vprasanja_3)- pravilni
        return render_template("3letnik.html", rezultati=rezultati, pravilni=pravilni, napacni=napacni)
    return render_template("3letnik.html", vprasanja_3=vprasanja_3)
if __name__ == "__main__":
    app.run(debug=True, port=8080)

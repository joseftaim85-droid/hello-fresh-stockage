from flask import Flask, render_template, request, redirect, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "hellofresh_secret"

def get_db():
    conn = sqlite3.connect("hellofresh_wms_v5.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS palettes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        palette_id TEXT,
        type TEXT,
        quantity INTEGER,
        day_code TEXT,
        location TEXT,
        created_at TEXT,
        UNIQUE(palette_id, type, day_code, location)
    );

    CREATE TABLE IF NOT EXISTS expeditions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        camion TEXT,
        transporteur TEXT,
        conducteur TEXT,
        plaque TEXT,
        heure_depart TEXT,
        heure_arrivee TEXT,
        date_envoi TEXT
    );

    CREATE TABLE IF NOT EXISTS expedition_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expedition_id INTEGER,
        palette_id TEXT,
        type_palette TEXT,
        quantite_envoyee INTEGER
    );
    """)
    db.commit()
    db.close()

init_db()

@app.route("/")
def stock():
    db = get_db()
    palettes = db.execute("SELECT * FROM palettes ORDER BY id DESC").fetchall()
    db.close()
    return render_template("stock.html", palettes=palettes)

@app.route("/add_stock", methods=["POST"])
def add_stock():
    data = request.form
    db = get_db()
    try:
        db.execute("""
        INSERT INTO palettes
        (palette_id, type, quantity, day_code, location, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["palette_id"],
            data["type"],
            int(data["quantity"]),
            data["day_code"],
            data["location"],
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))
        db.commit()
        flash("Palette ajoutée")
    except Exception as e:
        flash("Erreur: " + str(e))
    db.close()
    return redirect("/")

@app.route("/delete_stock/<int:id>")
def delete_stock(id):
    db = get_db()
    db.execute("DELETE FROM palettes WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect("/")

@app.route("/expedition")
def expedition():
    return render_template("expedition.html")

@app.route("/history")
def history():
    db = get_db()
    expeditions = db.execute("SELECT * FROM expeditions ORDER BY id DESC").fetchall()
    db.close()
    return render_template("history.html", expeditions=expeditions)

@app.route("/reset")
def reset():
    db = get_db()
    db.executescript("""
    DELETE FROM expedition_items;
    DELETE FROM expeditions;
    DELETE FROM palettes;
    """)
    db.commit()
    db.close()
    flash("Database reset successful")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

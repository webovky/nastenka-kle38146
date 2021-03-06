from . import app
from flask import render_template, request, redirect, url_for, session, flash
import functools
from werkzeug.security import generate_password_hash, check_password_hash

import sqlite3

# conn = sqlite3.connect("databaza.sqlite", isolation_level=None)
dbfile = "databaza.sqlite"

# from werkzeug.security import check_password_hash

slova = ("Super", "Perfekt", "Úža", "Flask")


def prihlasit(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if "user" in session:
            return function(*args, **kwargs)
        else:
            return redirect(url_for("login", url=request.path))

    return wrapper


@app.route("/", methods=["GET"])
def index():
    if "nick" in session:
        with sqlite3.connect(dbfile) as conn:
            tabulka = conn.execute("SELECT nick, text, id FROM prispevek")



        return render_template("base.html.j2", tabulka=tabulka)
    else:
        flash("Musíš se přihlásit!!!")
        return redirect(url_for("login"))

@app.route("/login/")
def login():
    return render_template("login.html.j2")


@app.route("/login/", methods=["POST"])
def login_post():
    nick = request.form.get("nick")
    passwd = request.form.get("passwd")
    if nick and passwd:
        with sqlite3.connect(dbfile) as conn:
            tabulka = tuple(
                conn.execute("SELECT passwd FROM uzivatel WHERE nick=?", [nick])
            )
        if tabulka and check_password_hash(tabulka[0][0], passwd):
            flash("Anooooo")
            session["nick"] = nick
        else:
            flash("Neeeee")
    return redirect(url_for("index"))


@app.route("/logout/")
def logout():
    session.pop("nick", None)
    return redirect(url_for("index"))



@app.route("/registrate/")
def registrate():
    return render_template("registrate.html.j2", slova=slova)


@app.route("/registrate/", methods=["POST"])
def registrate_post():
    nick = request.form.get("nick")
    passwd1 = request.form.get("passwd1")
    passwd2 = request.form.get("passwd2")
    if nick and passwd1 and passwd2 == passwd1:
        hashpasswd = generate_password_hash(passwd1)
        with sqlite3.connect(dbfile) as conn:
            try:
                conn.execute(
                    "INSERT INTO uzivatel (nick, passwd) VALUES (?,?)",
                    [nick, hashpasswd],
                )
                flash("Uživatel vytvořen.")
            except sqlite3.IntegrityError:
                flash("Uživatel již existuje!")
    else:
        flash("Chyba: je nutné zadat jméno a dvakrát stejné heslo.")
        return redirect(url_for("registrate"))
    return redirect(url_for("index"))


@app.route("/insert/", methods=["POST"])
def insert():
    if "nick" in session:
        prispevek = request.form.get("prispevek")
        with sqlite3.connect(dbfile) as conn:
            conn.execute("INSERT INTO prispevek (text, nick) VALUES (?, ?)", [prispevek, session["nick"]])

        return redirect(url_for("index"))
    else:
        return abort(403)
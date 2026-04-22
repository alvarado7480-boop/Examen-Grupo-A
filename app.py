import os
import sqlite3

from flask import Flask, flash, redirect, render_template, request, url_for

DATABASE = os.path.join(os.path.dirname(__file__), "inventario.db")

app = Flask(__name__)
app.secret_key = "cambiar-en-produccion"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                precio REAL NOT NULL,
                stock INTEGER NOT NULL
            )
            """
        )


@app.route("/")
def listar():
    with get_db() as db:
        filas = db.execute(
            "SELECT id, nombre, categoria, precio, stock FROM productos ORDER BY id"
        ).fetchall()
    productos = [dict(f) for f in filas]
    return render_template("index.html", productos=productos)


@app.route("/productos/nuevo", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        categoria = request.form.get("categoria", "").strip()
        try:
            precio = float(request.form.get("precio", ""))
            stock = int(request.form.get("stock", ""))
        except (TypeError, ValueError):
            flash("Precio y stock deben ser números válidos.", "danger")
            return render_template("formulario.html", producto=None, titulo="Nuevo producto")

        if not nombre or not categoria:
            flash("Nombre y categoría son obligatorios.", "danger")
            return render_template("formulario.html", producto=None, titulo="Nuevo producto")

        with get_db() as db:
            db.execute(
                """
                INSERT INTO productos (nombre, categoria, precio, stock)
                VALUES (?, ?, ?, ?)
                """,
                (nombre, categoria, precio, stock),
            )
        flash("Producto registrado correctamente.", "success")
        return redirect(url_for("listar"))

    return render_template("formulario.html", producto=None, titulo="Nuevo producto")


@app.route("/productos/<int:producto_id>/editar", methods=["GET", "POST"])
def editar(producto_id):
    with get_db() as db:
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            categoria = request.form.get("categoria", "").strip()
            try:
                precio = float(request.form.get("precio", ""))
                stock = int(request.form.get("stock", ""))
            except (TypeError, ValueError):
                flash("Precio y stock deben ser números válidos.", "danger")
                row = db.execute(
                    "SELECT id, nombre, categoria, precio, stock FROM productos WHERE id = ?",
                    (producto_id,),
                ).fetchone()
                if not row:
                    flash("Producto no encontrado.", "warning")
                    return redirect(url_for("listar"))
                return render_template(
                    "formulario.html",
                    producto=dict(row),
                    titulo="Editar producto",
                )

            if not nombre or not categoria:
                flash("Nombre y categoría son obligatorios.", "danger")
                row = db.execute(
                    "SELECT id, nombre, categoria, precio, stock FROM productos WHERE id = ?",
                    (producto_id,),
                ).fetchone()
                return render_template(
                    "formulario.html",
                    producto=dict(row) if row else None,
                    titulo="Editar producto",
                )

            cur = db.execute(
                """
                UPDATE productos
                SET nombre = ?, categoria = ?, precio = ?, stock = ?
                WHERE id = ?
                """,
                (nombre, categoria, precio, stock, producto_id),
            )
            if cur.rowcount == 0:
                flash("Producto no encontrado.", "warning")
                return redirect(url_for("listar"))
            flash("Producto actualizado correctamente.", "success")
            return redirect(url_for("listar"))

        row = db.execute(
            "SELECT id, nombre, categoria, precio, stock FROM productos WHERE id = ?",
            (producto_id,),
        ).fetchone()
    if not row:
        flash("Producto no encontrado.", "warning")
        return redirect(url_for("listar"))
    return render_template(
        "formulario.html",
        producto=dict(row),
        titulo="Editar producto",
    )


@app.post("/productos/<int:producto_id>/eliminar")
def eliminar(producto_id):
    with get_db() as db:
        cur = db.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
    if cur.rowcount:
        flash("Producto eliminado.", "success")
    else:
        flash("Producto no encontrado.", "warning")
    return redirect(url_for("listar"))


init_db()


if __name__ == "__main__":
    app.run(debug=True)

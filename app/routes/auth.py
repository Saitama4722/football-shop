from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..extensions import db
from ..models import User

bp = Blueprint("auth", __name__)


def get_current_user() -> User | None:
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(int(user_id))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")

    email = (request.form.get("email") or "").strip().lower()
    full_name = (request.form.get("full_name") or "").strip()
    password = request.form.get("password") or ""
    password2 = request.form.get("password2") or ""

    if not email or not password:
        flash("Email и пароль обязательны.", "danger")
        return render_template("auth/register.html")

    if password != password2:
        flash("Пароли не совпадают.", "danger")
        return render_template("auth/register.html")

    exists = User.query.filter_by(email=email).first()
    if exists is not None:
        flash("Пользователь с таким email уже существует.", "warning")
        return render_template("auth/register.html")

    user = User(email=email, full_name=full_name or None, is_admin=False)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    session["is_admin"] = bool(user.is_admin)

    flash("Регистрация выполнена.", "success")
    return redirect(url_for("main.index"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""

    if not email or not password:
        flash("Введите email и пароль.", "danger")
        return render_template("auth/login.html")

    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        flash("Неверный email или пароль.", "danger")
        return render_template("auth/login.html")

    session["user_id"] = user.id
    session["is_admin"] = bool(user.is_admin)

    flash("Вход выполнен.", "success")
    return redirect(url_for("main.index"))


@bp.post("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("is_admin", None)

    flash("Вы вышли из системы.", "info")
    return redirect(url_for("main.index"))

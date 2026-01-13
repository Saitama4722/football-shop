from __future__ import annotations

from decimal import Decimal

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from ..extensions import db
from ..models import Category, Product

bp = Blueprint("admin", __name__)


def _require_admin() -> None:
    if not session.get("is_admin"):
        abort(403)


def _slugify(value: str) -> str:
    value = (value or "").strip().lower()
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789-"
    value = value.replace("_", "-").replace(" ", "-")
    value = "".join(ch for ch in value if ch in allowed)
    value = "-".join([part for part in value.split("-") if part])
    return value or "item"


@bp.get("/")
def admin_root():
    _require_admin()
    return redirect(url_for("admin.products"))


@bp.route("/products", methods=["GET", "POST"])
def products():
    _require_admin()

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        slug = _slugify(request.form.get("slug") or name)
        description = (request.form.get("description") or "").strip()

        price_raw = (request.form.get("price") or "0").strip().replace(",", ".")
        stock_raw = (request.form.get("stock_qty") or "0").strip()

        category_id_raw = (request.form.get("category_id") or "").strip()

        if not name or not category_id_raw:
            flash("Заполните название и категорию.", "danger")
            return redirect(url_for("admin.products"))

        try:
            price = Decimal(price_raw)
        except Exception:
            price = Decimal("0.00")

        try:
            stock_qty = max(0, int(stock_raw))
        except ValueError:
            stock_qty = 0

        category = Category.query.get(int(category_id_raw))
        if category is None:
            flash("Категория не найдена.", "danger")
            return redirect(url_for("admin.products"))

        exists_slug = Product.query.filter_by(slug=slug).first()
        if exists_slug is not None:
            flash("Slug уже занят.", "warning")
            return redirect(url_for("admin.products"))

        product_obj = Product(
            name=name,
            slug=slug,
            description=description or None,
            price=price,
            stock_qty=stock_qty,
            category_id=category.id,
            is_active=True,
        )
        db.session.add(product_obj)
        db.session.commit()

        flash("Товар добавлен.", "success")
        return redirect(url_for("admin.products"))

    categories = Category.query.order_by(Category.name.asc()).all()
    products_list = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin/products.html", products=products_list, categories=categories)


@bp.post("/products/<int:product_id>/toggle")
def product_toggle(product_id: int):
    _require_admin()

    product_obj = Product.query.get_or_404(product_id)
    product_obj.is_active = not bool(product_obj.is_active)
    db.session.commit()

    flash("Статус товара изменён.", "info")
    return redirect(url_for("admin.products"))


@bp.post("/products/<int:product_id>/delete")
def product_delete(product_id: int):
    _require_admin()

    product_obj = Product.query.get_or_404(product_id)
    db.session.delete(product_obj)
    db.session.commit()

    flash("Товар удалён.", "info")
    return redirect(url_for("admin.products"))

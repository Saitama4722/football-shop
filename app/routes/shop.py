from __future__ import annotations

from decimal import Decimal
from typing import Any

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..extensions import db
from ..models import Category, Order, OrderItem, Product, User

bp = Blueprint("shop", __name__)


def _get_cart() -> dict[str, int]:
    cart = session.get("cart")
    if not isinstance(cart, dict):
        cart = {}
        session["cart"] = cart
    return cart


def _cart_items() -> list[dict[str, Any]]:
    cart = _get_cart()
    if not cart:
        return []

    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.query.filter(Product.id.in_(product_ids), Product.is_active.is_(True)).all()
    products_by_id = {p.id: p for p in products}

    items: list[dict[str, Any]] = []
    for pid_str, qty in cart.items():
        pid = int(pid_str)
        product = products_by_id.get(pid)
        if product is None:
            continue
        qty_int = int(qty)
        unit_price = Decimal(product.price)
        items.append(
            {
                "product": product,
                "qty": qty_int,
                "unit_price": unit_price,
                "line_total": unit_price * Decimal(qty_int),
            }
        )
    return items


def _cart_total(items: list[dict[str, Any]]) -> Decimal:
    total = Decimal("0.00")
    for item in items:
        total += item["line_total"]
    return total


@bp.get("/")
def catalog_root():
    return redirect(url_for("shop.catalog"))


@bp.get("/catalog")
def catalog():
    q = (request.args.get("q") or "").strip()
    category_slug = (request.args.get("category") or "").strip()

    categories = Category.query.order_by(Category.name.asc()).all()

    query = Product.query.filter(Product.is_active.is_(True))
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    if category_slug:
        query = query.join(Category).filter(Category.slug == category_slug)

    products = query.order_by(Product.created_at.desc()).all()

    return render_template(
        "catalog.html",
        products=products,
        categories=categories,
        q=q,
        category_slug=category_slug,
    )


@bp.get("/product/<slug>")
def product(slug: str):
    product_obj = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    return render_template("product.html", product=product_obj)


@bp.post("/cart/add/<int:product_id>")
def cart_add(product_id: int):
    product_obj = Product.query.filter_by(id=product_id, is_active=True).first()
    if product_obj is None:
        flash("Товар не найден.", "danger")
        return redirect(url_for("shop.catalog"))

    qty_raw = request.form.get("qty", "1")
    try:
        qty = max(1, int(qty_raw))
    except ValueError:
        qty = 1

    cart = _get_cart()
    key = str(product_id)
    cart[key] = int(cart.get(key, 0)) + qty
    session["cart"] = cart

    flash("Товар добавлен в корзину.", "success")
    return redirect(url_for("shop.cart_view"))


@bp.post("/cart/remove/<int:product_id>")
def cart_remove(product_id: int):
    cart = _get_cart()
    key = str(product_id)
    if key in cart:
        cart.pop(key)
        session["cart"] = cart
        flash("Товар удалён из корзины.", "info")
    return redirect(url_for("shop.cart_view"))


@bp.post("/cart/clear")
def cart_clear():
    session["cart"] = {}
    flash("Корзина очищена.", "info")
    return redirect(url_for("shop.cart_view"))


@bp.get("/cart")
def cart_view():
    items = _cart_items()
    total = _cart_total(items)
    return render_template("cart.html", items=items, total=total)


def _get_or_create_user(email: str, full_name: str | None) -> User:
    user = User.query.filter_by(email=email).first()
    if user is not None:
        if full_name and not user.full_name:
            user.full_name = full_name
            db.session.commit()
        return user

    user = User(email=email, full_name=full_name, is_admin=False)
    user.set_password("temporary-password")
    db.session.add(user)
    db.session.commit()
    return user


@bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    items = _cart_items()
    if not items:
        flash("Корзина пуста.", "warning")
        return redirect(url_for("shop.catalog"))

    if request.method == "GET":
        total = _cart_total(items)
        return render_template("checkout.html", items=items, total=total)

    customer_name = (request.form.get("customer_name") or "").strip()
    customer_phone = (request.form.get("customer_phone") or "").strip()
    customer_email = (request.form.get("customer_email") or "").strip().lower()
    delivery_address = (request.form.get("delivery_address") or "").strip()

    if not customer_name or not customer_phone or not customer_email:
        flash("Заполните имя, телефон и email.", "danger")
        total = _cart_total(items)
        return render_template("checkout.html", items=items, total=total)

    user = _get_or_create_user(customer_email, customer_name)

    order = Order(
        user_id=user.id,
        status="new",
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_email=customer_email,
        delivery_address=delivery_address or None,
    )
    db.session.add(order)
    db.session.flush()

    for item in items:
        product_obj: Product = item["product"]
        qty: int = int(item["qty"])
        unit_price = Decimal(product_obj.price)

        order_item = OrderItem(
            order_id=order.id,
            product_id=product_obj.id,
            qty=qty,
            unit_price=unit_price,
        )
        db.session.add(order_item)

    db.session.commit()
    session["cart"] = {}

    flash(f"Заказ №{order.id} оформлен.", "success")
    return redirect(url_for("main.index"))

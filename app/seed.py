from decimal import Decimal

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Category, Product, User


def get_or_create_category(name: str, slug: str) -> Category:
    category = Category.query.filter_by(slug=slug).first()
    if category:
        return category
    category = Category(name=name, slug=slug)
    db.session.add(category)
    db.session.flush()
    return category


def get_or_create_admin(email: str, password: str, full_name: str = "Администратор") -> User:
    user = User.query.filter_by(email=email).first()
    if user:
        # делаем админом, если поле существует
        if hasattr(user, "is_admin"):
            user.is_admin = True
        db.session.add(user)
        return user

    # создаём только по реально существующим полям модели User
    user = User(
        email=email,
        full_name=full_name,
        password_hash=generate_password_hash(password),
    )
    if hasattr(user, "is_admin"):
        user.is_admin = True

    db.session.add(user)
    return user


def get_or_create_product(
    *,
    category: Category,
    name: str,
    slug: str,
    description: str,
    price: Decimal,
    stock_qty: int,
    is_active: bool = True,
) -> Product:
    product = Product.query.filter_by(slug=slug).first()
    if product:
        product.name = name
        product.description = description
        product.price = price
        product.stock_qty = stock_qty
        product.category_id = category.id
        if hasattr(product, "is_active"):
            product.is_active = is_active
        db.session.add(product)
        return product

    product = Product(
        category_id=category.id,
        name=name,
        slug=slug,
        description=description,
        price=price,
        stock_qty=stock_qty,
    )
    if hasattr(product, "is_active"):
        product.is_active = is_active

    db.session.add(product)
    return product


def seed() -> None:
    app = create_app()
    with app.app_context():
        admin_email = "admin@footballshop.local"
        admin_password = "admin12345"
        get_or_create_admin(admin_email, admin_password, full_name="Администратор магазина")

        kits = get_or_create_category("Футбольная форма", "kits")
        balls = get_or_create_category("Мячи", "balls")
        boots = get_or_create_category("Бутсы", "boots")
        accessories = get_or_create_category("Аксессуары", "accessories")
        fan = get_or_create_category("Атрибутика болельщика", "fan")
        goalkeepers = get_or_create_category("Вратарская экипировка", "goalkeepers")

        get_or_create_product(
            category=kits,
            name="Домашняя форма «Сборная 2026»",
            slug="home-kit-2026",
            description="Комплект формы (футболка+шорты). Дышащая ткань, комфортная посадка, подходит для тренировок и игр.",
            price=Decimal("4990.00"),
            stock_qty=25,
        )
        get_or_create_product(
            category=kits,
            name="Гостевая форма «Classic Away»",
            slug="away-kit-classic",
            description="Лёгкая гостевая форма в классическом стиле. Быстро сохнет, не сковывает движения.",
            price=Decimal("4590.00"),
            stock_qty=18,
        )
        get_or_create_product(
            category=balls,
            name="Мяч матчевый «Pro Match» (размер 5)",
            slug="ball-pro-match-5",
            description="Матчевый мяч размера 5. Стабильная траектория, износостойкое покрытие, подходит для натурального и искусственного газона.",
            price=Decimal("3290.00"),
            stock_qty=40,
        )
        get_or_create_product(
            category=balls,
            name="Мяч тренировочный «Training Plus» (размер 5)",
            slug="ball-training-plus-5",
            description="Тренировочный мяч размера 5 для ежедневных занятий. Хороший контроль и мягкий отскок.",
            price=Decimal("2190.00"),
            stock_qty=55,
        )
        get_or_create_product(
            category=boots,
            name="Бутсы «Speed FG»",
            slug="boots-speed-fg",
            description="Бутсы для твёрдого грунта (FG). Лёгкий верх, отличное сцепление, контроль мяча на скорости.",
            price=Decimal("6990.00"),
            stock_qty=12,
        )
        get_or_create_product(
            category=boots,
            name="Бутсы «Control AG»",
            slug="boots-control-ag",
            description="Бутсы для искусственных полей (AG). Усиленная подошва, точный контроль, комфорт при длительной игре.",
            price=Decimal("7490.00"),
            stock_qty=10,
        )
        get_or_create_product(
            category=goalkeepers,
            name="Перчатки вратарские «Grip Pro»",
            slug="gk-gloves-grip-pro",
            description="Вратарские перчатки с усиленной ладонью. Надёжный хват и амортизация, удобная фиксация запястья.",
            price=Decimal("2890.00"),
            stock_qty=30,
        )
        get_or_create_product(
            category=goalkeepers,
            name="Шорты вратарские с защитой",
            slug="gk-shorts-protect",
            description="Шорты с мягкими вставками для защиты бёдер. Подходят для тренировок и матчей.",
            price=Decimal("1990.00"),
            stock_qty=22,
        )
        get_or_create_product(
            category=accessories,
            name="Набор манишек (5 шт.)",
            slug="training-bibs-5",
            description="Комплект манишек для тренировок (5 штук). Лёгкие, заметные, удобные для командных занятий.",
            price=Decimal("1490.00"),
            stock_qty=35,
        )
        get_or_create_product(
            category=accessories,
            name="Щитки «Shield Lite»",
            slug="shin-guards-shield-lite",
            description="Лёгкие щитки для защиты голени. Анатомическая форма и комфортная фиксация.",
            price=Decimal("1290.00"),
            stock_qty=45,
        )
        get_or_create_product(
            category=fan,
            name="Шарф болельщика «Football Shop»",
            slug="fan-scarf-football-shop",
            description="Тёплый шарф болельщика с фирменным стилем магазина. Отлично подходит для стадиона и повседневной носки.",
            price=Decimal("990.00"),
            stock_qty=60,
        )
        get_or_create_product(
            category=fan,
            name="Кепка болельщика «Supporter Cap»",
            slug="fan-cap-supporter",
            description="Кепка болельщика с вышитым логотипом. Регулируемый ремешок, универсальный размер.",
            price=Decimal("1190.00"),
            stock_qty=50,
        )

        db.session.commit()

        print("✅ Seed выполнен успешно.")
        print("👤 Админ:", admin_email)
        print("🔑 Пароль:", admin_password)


if __name__ == "__main__":
    seed()

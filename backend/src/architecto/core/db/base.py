from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base déclarative partagée par tous les modèles SQLAlchemy.

    Isolée de la session pour que les modèles (dans les features) puissent en
    hériter sans importer le moteur de connexion.
    """

from pydantic_settings import SettingsConfigDict

from architecto.core.config.base import SectionSettings


class KnowledgeSettings(SectionSettings):
    """Ingestion de la base de connaissances — préfixe `KNOWLEDGE_`.

    Bornes appliquées aux téléversements côté client (garde-fous serveur).
    """

    model_config = SettingsConfigDict(env_prefix="KNOWLEDGE_")

    max_upload_mb: int = 20  # taille max par fichier
    max_files: int = 20  # nombre max de fichiers par requête

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

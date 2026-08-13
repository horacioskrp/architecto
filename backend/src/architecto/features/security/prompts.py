# Skeleton fixe : OWASP Top 10 (2021) — ancre la checklist sur un standard réel.
OWASP_TOP_10 = [
    "A01:2021 – Broken Access Control",
    "A02:2021 – Cryptographic Failures",
    "A03:2021 – Injection",
    "A04:2021 – Insecure Design",
    "A05:2021 – Security Misconfiguration",
    "A06:2021 – Vulnerable and Outdated Components",
    "A07:2021 – Identification and Authentication Failures",
    "A08:2021 – Software and Data Integrity Failures",
    "A09:2021 – Security Logging and Monitoring Failures",
    "A10:2021 – Server-Side Request Forgery (SSRF)",
]

SECURITY_SYSTEM_PROMPT = """Tu es un expert en sécurité applicative.
Produis une CHECKLIST de sécurité pour le système décrit, ancrée sur l'OWASP Top 10.

Règles :
- Une section Markdown par catégorie OWASP ci-dessous (garde le code, ex. « A03:2021 »).
- Sous chaque catégorie, 2 à 5 points **à vérifier**, concrets et adaptés au système,
  sous forme de cases à cocher `- [ ]`.
- C'est une checklist de VÉRIFICATION, **pas un verdict** : n'affirme jamais que le
  système est « sécurisé » ou « vulnérable ». Liste ce qu'il faut contrôler.
- Si une catégorie ne s'applique pas au système, indique-le brièvement plutôt que
  d'inventer des points.

Catégories OWASP Top 10 (2021) :
{categories}"""


def build_system_prompt() -> str:
    """Prompt système avec les 10 catégories OWASP injectées."""
    categories = "\n".join(f"- {c}" for c in OWASP_TOP_10)
    return SECURITY_SYSTEM_PROMPT.format(categories=categories)

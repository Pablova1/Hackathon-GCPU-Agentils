"""Prompts pour l'agent de résumé des besoins utilisateur"""

def build_summary_prompt(conversation_text: str) -> str:
    """Construit le prompt pour analyser et résumer les besoins de l'utilisateur"""
    return f"""
Analyse cette conversation et extrait UNIQUEMENT les informations IMPORTANTES et NOUVELLES. Sois très concis et ne mentionne que ce qui est réellement significatif.

CONVERSATION:
{conversation_text}

CONSIGNES STRICTES:
- Maximum 3-4 lignes courtes au total
- N'indique une information QUE si elle est importante/nouvelle
- Évite les répétitions et les détails insignifiants
- Utilise des puces courtes (• )

Format de réponse CONCIS:

PROFIL:
• [Seulement objectifs/contraintes importantes mentionnées]

HABITUDES:
• [Seulement préférences/restrictions significatives]

BESOINS:
• [Seulement demandes/problèmes spécifiques]

Si aucune information importante n'est mentionnée, réponds: "Aucune information nutritionnelle significative détectée."
"""
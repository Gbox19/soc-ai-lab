"""Tu turno: decide cuándo el modelo NO puede cerrar una alerta solo.

Esta función recibe una alerta (un dict de alerts/alerts.json) y devuelve:
    (True,  "motivo")  -> el flujo obliga a revisión humana
    (False, "")        -> el flujo deja pasar el veredicto del modelo

Pistas: mira alert["model_verdict"] y alert["analyst_context"].
Los campos útiles: confidence, suggestion, host_criticality, account_type,
account_usual_hours, parent_process, command_line.

Corre `python triage.py --check` después de cada cambio.
"""


def needs_human_review(alert: dict) -> tuple[bool, str]:
    verdict = alert["model_verdict"]
    ctx = alert["analyst_context"]

    # Regla de ejemplo: si el modelo duda, que mire un humano.
    if verdict["confidence"] < 0.70:
        return True, "confianza baja del modelo"

    # Ejecución ofuscada + sugerencia de auto-cierre
    cmd = ctx["command_line"].lower()
    if verdict["suggestion"] == "auto-cierre" and any(
        f in cmd for f in ("-enc", "-w hidden")
    ):
        return True, "ejecución ofuscada con sugerencia de auto-cierre"

    return False, ""

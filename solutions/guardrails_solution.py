"""Una solución posible. No la abras hasta haber intentado la tuya.

Para probarla sin tocar tu archivo:
    cp solutions/guardrails_solution.py guardrails.py
"""

OBFUSCATION_FLAGS = ("-enc", "-encodedcommand", "-w hidden", "-windowstyle hidden")


def _hour(ts_hhmm: str) -> int:
    return int(ts_hhmm.split(":")[0])


def _outside_hours(alert: dict) -> bool:
    ctx = alert["analyst_context"]
    start, end = ctx["account_usual_hours"].split("-")
    h = int(alert["timestamp"][11:13])
    s, e = _hour(start), _hour(end)
    inside = (s <= h < e) if s < e else (h >= s or h < e)
    return not inside


def needs_human_review(alert: dict) -> tuple[bool, str]:
    verdict = alert["model_verdict"]
    ctx = alert["analyst_context"]
    cmd = ctx["command_line"].lower()
    auto_close = verdict["suggestion"] == "auto-cierre"

    if verdict["confidence"] < 0.70:
        return True, "confianza baja del modelo"

    if auto_close and any(flag in cmd for flag in OBFUSCATION_FLAGS):
        return True, "ejecución ofuscada con sugerencia de auto-cierre"

    if auto_close and ctx["host_criticality"] == "alta":
        return True, "host crítico con sugerencia de auto-cierre"

    if auto_close and ctx["account_type"] == "servicio" and _outside_hours(alert):
        return True, "cuenta de servicio fuera de su horario habitual"

    return False, ""

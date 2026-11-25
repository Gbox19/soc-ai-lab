#!/usr/bin/env python3
"""Mini-laboratorio: IA en el SOC. ¿Confías o verificas?

Todo es sintético y el "modelo" está simulado (sus veredictos viven en
alerts/alerts.json). No hay red, no hay producción, no hay dependencias.

Uso:
    python triage.py                 # las 4 alertas con el veredicto del modelo
    python triage.py --alert A-004   # lo que vio el modelo
    python triage.py --context A-004 # lo que vería un analista
    python triage.py --present       # modo charla: voto, pausa y revelación
    python triage.py --check         # prueba tu guardrails.py
"""
import argparse
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
USE_COLOR = sys.stdout.isatty()


def c(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def load_alerts():
    return json.loads((ROOT / "alerts" / "alerts.json").read_text(encoding="utf-8"))


def find(alerts, alert_id):
    for a in alerts:
        if a["id"].lower() == alert_id.lower():
            return a
    sys.exit(f"No existe la alerta {alert_id}. Prueba con: " + ", ".join(a["id"] for a in alerts))


def verdict_color(label):
    return {"benigno": "32", "sospechoso": "33", "malicioso": "31"}.get(label, "0")


def show_table(alerts):
    print(c("\nCola de alertas — veredictos del modelo (simulado)\n", "1"))
    print(f"{'ID':<7}{'VEREDICTO':<13}{'CONF.':<8}{'SUGERENCIA':<13}TÍTULO")
    print("-" * 78)
    for a in alerts:
        v = a["model_verdict"]
        label = c(f"{v['label'].upper():<13}", verdict_color(v["label"]))
        print(f"{a['id']:<7}{label}{int(v['confidence'] * 100):>3}%    {v['suggestion']:<13}{a['title']}")
    print("\nSiguiente paso: python triage.py --alert A-004\n")


def show_model_view(a):
    v, m = a["model_verdict"], a["model_view"]
    print(c(f"\n{a['id']} · {a['title']}", "1"))
    print(f"Hora: {a['timestamp']}\n")
    print(c("LO QUE VIO EL MODELO", "36"))
    print(f"  Comando (resumen):        {m['command_summary']}")
    print(f"  Coincidencias de TI:      {m['ti_matches']}")
    print(f"  Alertas previas similares: {m['similar_past_alerts']}")
    print(f"  Similitud:                {m['similarity']}")
    print(c("\nVEREDICTO DEL MODELO", "36"))
    print(f"  {c(v['label'].upper(), verdict_color(v['label']))} · {int(v['confidence'] * 100)}% · sugiere: {v['suggestion']}")
    print(f"  Razón: {v['reason']}")
    print(f"\n¿Cierras, pides contexto o escalas? Para ver el contexto: python triage.py --context {a['id']}\n")


def show_context(a):
    ctx = a["analyst_context"]
    print(c(f"\n{a['id']} · LO QUE VERÍA UN ANALISTA", "33"))
    for key, label in [
        ("host", "Host"), ("host_criticality", "Criticidad del host"),
        ("account", "Cuenta"), ("account_type", "Tipo de cuenta"),
        ("account_usual_hours", "Horario habitual"), ("parent_process", "Proceso padre"),
        ("process", "Proceso"),
    ]:
        print(f"  {label + ':':<22}{ctx[key]}")
    print(f"  {'Línea de comando:':<22}{ctx['command_line']}")
    if "change_ticket" in ctx:
        print(f"  {'Ticket de cambio:':<22}{ctx['change_ticket']}")
    print("  Notas:")
    for n in ctx["notes"]:
        print(f"    - {n}")
    print()


def present(alerts):
    """Modo charla: muestra la alerta, pausa para votar y revela el contexto."""
    for a in alerts:
        show_model_view(a)
        input(c("  [Enter] cuando termine la votación… ", "2"))
        show_context(a)
        input(c("  [Enter] para la siguiente alerta… ", "2"))
    print(c("\nFin. ¿Cuántos cambiaron de decisión al ver el contexto?\n", "1"))


def check(alerts):
    truth = json.loads((ROOT / "answers" / "ground_truth.json").read_text(encoding="utf-8"))
    sys.path.insert(0, str(ROOT))
    try:
        guardrails = importlib.import_module("guardrails")
    except Exception as e:  # noqa: BLE001
        sys.exit(f"No pude cargar guardrails.py: {e}")

    print(c("\nTus guardrails contra las 4 alertas\n", "1"))
    print(f"{'ID':<7}{'MODELO':<12}{'TU REGLA':<14}MOTIVO")
    print("-" * 78)
    missed, overload = [], []
    for a in alerts:
        try:
            flagged, reason = guardrails.needs_human_review(a)
        except Exception as e:  # noqa: BLE001
            sys.exit(f"Error en needs_human_review para {a['id']}: {e}")
        should = truth[a["id"]]["needs_human_review"]
        rule = c("REVISIÓN", "33") if flagged else "deja pasar"
        print(f"{a['id']:<7}{a['model_verdict']['label']:<12}{rule:<14}{reason}")
        if should and not flagged:
            missed.append(a["id"])
        if flagged and not should:
            overload.append(a["id"])

    print()
    if not missed and not overload:
        print(c("¡Perfecto! Las alertas que importan pasan por un humano y no cargaste de más a nadie.", "32"))
    if missed:
        print(c("Se te escaparon (peligro):", "31"), ", ".join(missed))
        for i in missed:
            print(f"  {i}: {truth[i]['why']}")
    if overload:
        print(c("Mandaste a revisión de más (carga para el analista):", "33"), ", ".join(overload))
        for i in overload:
            print(f"  {i}: {truth[i]['why']}")
    print()


def main():
    p = argparse.ArgumentParser(description="Laboratorio: IA en el SOC")
    p.add_argument("--alert", metavar="ID", help="lo que vio el modelo")
    p.add_argument("--context", metavar="ID", help="lo que vería un analista")
    p.add_argument("--present", action="store_true", help="modo charla")
    p.add_argument("--check", action="store_true", help="prueba tu guardrails.py")
    args = p.parse_args()

    alerts = load_alerts()
    if args.alert:
        show_model_view(find(alerts, args.alert))
    elif args.context:
        show_context(find(alerts, args.context))
    elif args.present:
        present(alerts)
    elif args.check:
        check(alerts)
    else:
        show_table(alerts)


if __name__ == "__main__":
    main()

# Laboratorio: IA en el SOC — ¿Confías o verificas?

Mini-laboratorio de la charla **"IA en el SOC: la noche que el modelo casi me hace quedar mal"** (BugCON 2026).

Tienes 4 alertas con el veredicto de un modelo. Tu trabajo: decidir si confías o verificas, y después escribir un **guardrail** que obligue a revisión humana cuando el modelo no debería cerrar solo.

> **Todo es sintético.** El modelo está simulado, los datos son inventados y las IPs son de documentación (`203.0.113.0/24`). No hay red, no hay producción y no se necesita internet.

## Requisitos

- Python 3.10 o superior
- Nada más (cero dependencias)

## En 4 pasos

```bash
# 1. Mira las 4 alertas con el veredicto del modelo
python triage.py

# 2. Entra a una alerta: ¿qué vio el modelo?
python triage.py --alert A-004

# 3. Revela lo que vería un analista y compara
python triage.py --context A-004

# 4. Escribe tu guardrail en guardrails.py y pruébalo
python triage.py --check
```

Para repetir el ejercicio de la charla (voto, pausa, revelación) alerta por alerta:

```bash
python triage.py --present
```

## El reto

Abre `guardrails.py`. Ya trae una regla de ejemplo (si el modelo duda, revisa un humano). Completa los TODO:

1. Ejecución ofuscada + sugerencia de auto-cierre
2. Host de criticidad alta + sugerencia de auto-cierre
3. *(Reto)* Cuenta de servicio fuera de su horario habitual

Corre `python triage.py --check` después de cada cambio. Te dirá:

- **Qué se te escapó** (una alerta peligrosa que el modelo cerraría solo)
- **Qué mandaste de más** (carga innecesaria para el analista)

El objetivo no es revisar todo: es revisar **lo correcto**.

## Estructura

```
.
├── README.md
├── triage.py                    # el triage simulado (no lo necesitas editar)
├── guardrails.py                # TU archivo: aquí va tu regla
├── alerts/alerts.json           # las 4 alertas, con el veredicto del modelo
├── answers/ground_truth.json    # respuestas (las usa --check; no las abras antes)
└── solutions/
    └── guardrails_solution.py   # una solución posible (al final)
```

## Para llevarte

- La confianza del analista crece sola; la validación hay que diseñarla.
- Similitud no es intención.
- Un guardrail no es desconfiar de la IA: es reconocer dónde su error cuesta más caro.
- Lo que sirve en un entorno puede ahogarte en falsos positivos en otro. Pruébalo contra tu histórico.

## Aviso

Material educativo. Las reglas de este laboratorio son ejemplos ilustrativos, no reglas listas para producción.

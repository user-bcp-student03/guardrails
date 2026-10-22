"""Rol chapter: edita aquí sus instrucciones y entregables."""

from graph.state import WorkflowState
from graph.context import _ctx, _runs, _const_block, _ronda, _feedback_block


INSTRUCTIONS = """Eres el Chapter del equipo, revisor técnico. Contrasta de forma conjunta el requerimiento y sus criterios de aceptación, la arquitectura, los datos, el código, las pruebas y la seguridad. Evalúa si el análisis, el plan y los cambios reportados cumplen el Issue, las interfaces documentadas del producto y la constitución. Emite un veredicto técnico con motivos y correcciones concretas. Mantén la revisión dentro del alcance indicado; no implementes ni escribas código funcional.

Tu veredicto técnico no sustituye ni omite las aprobaciones humanas. No declares una aprobación humana ni alteres decisiones humanas previas; conserva el flujo de revisión y aprobación HITL.

Devuelve Markdown con ## Analysis y ## Plan, cada encabezado en su propia línea y en ese orden. Al final incluye una línea exacta con uno de estos formatos: VEREDICTO: APROBADO, VEREDICTO: APROBADO CON OBSERVACIONES o VEREDICTO: RECHAZADO.

En ## Analysis:
- Resume el alcance del Issue y diagnostica los cambios con evidencia de los reportes disponibles.
- Relaciona cada criterio de aceptación con el componente que debe resolverlo y señala si está cubierto, incompleto o incumplido. Considera las responsabilidades y límites de cada componente.
- Contrasta las interfaces afectadas con los documentos del producto. Para cada API afectada, revisa entradas, respuestas y errores e incluye ejemplos breves que permitan aclarar el contrato esperado. Si no se afecta una API o la información no está disponible, indícalo sin inventar contratos.
- Distingue hechos de supuestos y enumera preguntas pendientes relevantes.

En ## Plan:
- Indica el diagnóstico final, los archivos afectados o que requieren corrección y el orden de los cambios por dependencia.
- Para cada observación, especifica qué criterio o contrato debe verificarse para cerrarla. Si no hay cambios pendientes, indícalo.
- No propongas rediseños fuera del Issue ni incluyas implementación funcional.
"""


def chapter_node(state: WorkflowState, invoke) -> dict:
    """
    Revisa los cambios y emite veredicto. Si deja observaciones, quedan en
    `review_feedback` para que el dev las incorpore en la ronda siguiente.

    Usa `context` como checklist de compliance.
    Escribe en: out_chapter, review_feedback, last_verdict, approved, review_round
    """
    ronda = _ronda(state)  # esta revision incrementa el contador
    print(f"[chapter_node] Revisando cambios (ronda {ronda})...")

    prev = (
        "\nEn rondas anteriores diste observaciones. "
        "Verifica si se han incorporado correctamente.\n"
        if ronda > 1
        else ""
    )
    reports = "\n\n".join(
        f"## {label}\n{_ctx(state.get(field, ''), 6000)}"
        for field, label in (
            ("out_backend", "Backend"),
            ("out_frontend", "Frontend"),
            ("out_testing", "Pruebas"),
            ("out_security", "Seguridad"),
        )
    )

    prompt = (INSTRUCTIONS + _const_block(state, "Respeta las restricciones del proyecto y la constitución.") + "\nRepositorio: " + state["repo_name"] + "\nAnálisis del arquitecto:\n" + _ctx(state.get("out_analysis", ""),1500) + "\nPlan:\n" + _ctx(state.get("out_plan", ""),1500) + "\nCambios:\n" + reports)
    if state.get("include_data"):
        prompt += "\nDatos y persistencia (tablas, relaciones, restricciones y migraciones):\n" + _ctx(state.get("out_data", ""), 6000)
    else:
        prompt += "\nDatos y persistencia:\nNo se generó un reporte del nodo de datos en esta ejecución. Evalúa si el Issue o la arquitectura tienen impacto de datos; si no puede determinarse, decláralo como supuesto o pregunta pendiente."
    salida = invoke(prompt)
    veredicto = parse_verdict(salida)

    etiqueta = {
        "aprobado": "APROBADO ✓",
        "observaciones": "APROBADO CON OBSERVACIONES",
        "rechazado": "RECHAZADO ✗",
    }[veredicto]
    print(f"[chapter_node] Ronda {ronda}: {etiqueta}")

    return {
        "out_chapter": salida,
        "review_feedback": salida,  # lo lee el dev en la ronda siguiente
        "last_verdict": veredicto,
        "approved": veredicto == "aprobado",
        "review_round": ronda,
    }


def parse_verdict(text: str) -> str:
    """
    Interpreta el veredicto de forma conservadora: si no dice claramente
    APROBADO sin observaciones, fuerza otra ronda.

    Retorna: "aprobado" | "observaciones" | "rechazado"
    """
    t = (text or "").lower()
    if "rechazado" in t or "rejected" in t:
        return "rechazado"
    if "aprobado con observaciones" in t or "approved with comments" in t:
        return "observaciones"
    if "aprobado" in t or "approved" in t:
        return "aprobado"
    return "observaciones" 

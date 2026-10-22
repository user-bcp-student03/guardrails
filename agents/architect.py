"""Arquitecto: diagnóstico, componentes, límites y contrato de API."""

from graph.state import WorkflowState
from graph.context import _ctx, _const_block


INSTRUCTIONS = """Eres el arquitecto de software del equipo. Define una solución acotada al Issue
y sus criterios de aceptación usando el código y las interfaces existentes. Identifica
componentes, responsabilidades, límites y contrato de API: entradas, respuestas y
errores. Respeta las interfaces existentes salvo que el Issue solicite cambiarlas.
No implementes código ni inventes requisitos, evidencia o resultados de pruebas.
Distingue hechos observados, propuestas y supuestos pendientes. Produce un plan
accionable y verificable para Datos, Backend, Frontend y Pruebas.
"""


def architect_node(state: WorkflowState, invoke) -> dict:
    prompt = (
        INSTRUCTIONS
        + _const_block(
            state,
            "Respeta el alcance del Issue, sus criterios de aceptación y la constitución.",
        )
        + "\nRepositorio: "
        + state["repo_name"]
        + "\nTipo de proyecto: "
        + state.get("project_type", "ambos")
        + "\nCódigo y artefactos originales:\n"
        + _ctx(state["snapshot"], 10000)
        + """

Analiza el Issue, sus criterios de aceptación y las interfaces existentes del producto
incluidas en el contexto. Diagnostica qué existe, qué falta y por qué se necesita el
cambio. Si falta información necesaria, indícala como pendiente; no des por satisfechos
criterios que no puedas verificar.

Devuelve exactamente las secciones ## Analysis y ## Plan, cada una en su propia línea.
En ## Analysis, resume el problema y qué existe/falta. Sustenta observaciones con
rutas o interfaces del repositorio cuando estén disponibles y separa hechos de dudas.

En ## Plan, redacta el informe de arquitectura con estos apartados:
- Componentes y límites: responsabilidad, entradas/salidas y dependencias; especifica
  qué queda fuera del alcance del Issue.
- Recorrido de petición: pasos del caso válido por los componentes hasta la respuesta.
- Contrato de API: método y ruta; campos de entrada, tipos, obligatoriedad y
  validaciones; respuesta exitosa con forma y ejemplo; errores con código HTTP,
  código estable, forma del cuerpo y condición que los produce. Cita la interfaz
  existente si aplica. Si no hay API, explica por qué y define las interfaces afectadas.
- Ejemplos: petición y respuesta coherentes con los criterios; añade un error relevante
  cuando los criterios o las interfaces existentes lo contemplen.
- Criterios verificables: relaciona cada criterio de aceptación con comportamiento,
  componente y comprobación observable.
- Archivos afectados: indica las rutas existentes que deben cambiar y los archivos
  nuevos necesarios, vinculando cada uno con su responsabilidad. Basa las rutas en el
  repositorio; si no puedes determinar una ruta, márcala como propuesta.
- Orden de cambios: enumera los pasos de implementación y sus dependencias para que
  Datos, Backend, Frontend y Pruebas trabajen sobre decisiones compatibles.
- Supuestos y preguntas pendientes: declara cada supuesto, pregunta y responsable de
  resolverla (Datos, Backend, Frontend o equipo).

No inventes endpoints, campos, errores ni criterios. Si el Issue no define un detalle,
propónlo como decisión pendiente de confirmar y no como requisito aprobado. No afirmes
que se ejecutaron pruebas: marca como NO EJECUTADO lo que no esté comprobado.
"""
    )
    report = invoke(prompt)
    analysis, separator, plan = report.partition("\n## Plan\n")
    if not analysis.startswith("## Analysis\n") or not separator or not plan.strip():
        raise ValueError(
            "El arquitecto debe devolver las secciones ## Analysis y ## Plan."
        )
    return {
        "out_architect": report,
        "out_analysis": analysis.removeprefix("## Analysis\n").strip(),
        "out_plan": plan.strip(),
    }

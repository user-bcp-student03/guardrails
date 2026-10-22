"""Revisor de seguridad: edita aquí las instrucciones de revisión."""

from graph.state import WorkflowState
from graph.context import _ctx, _const_block, _feedback_block


INSTRUCTIONS = (
    "ROL: Eres el Revisor de seguridad del equipo. Evalúas los riesgos de seguridad "
    "de la solución propuesta y de los cambios recibidos; no implementas cambios ni "
    "sustituyes las aprobaciones humanas.\n"
    "OBJETIVO: Contrastar los criterios de aceptación y el recorrido de la petición "
    "con el código original y las propuestas de Backend y Frontend. Determinar si "
    "autenticación, autorización, validación de entradas, secretos, datos sensibles "
    "e inyección se manejan de forma adecuada y señalar riesgos con evidencia.\n"
    "ACCIONES:\n"
    "1. Lee el plan y el código disponible; identifica el recorrido de la petición, "
    "sus fronteras de confianza y los componentes que reciben o exponen datos.\n"
    "2. Comprueba qué puede hacer un usuario sin permiso o con entradas manipuladas, "
    "incluido acceder o modificar recursos que pertenecen a otra persona. Revisa "
    "autenticación y autorización en el servidor, validación de entradas, posibles "
    "inyecciones, manejo de secretos y exposición de datos sensibles.\n"
    "3. Usa el contrato aprobado de Datos si está incluido. No asumas que una medida "
    "existe si no aparece en el material recibido; para cada hallazgo registra "
    "evidencia concreta y localizable, como archivo y ubicación o comportamiento "
    "observado.\n"
    "4. Para cada hallazgo indica archivo y ubicación, escenario e impacto, evidencia, "
    "corrección propuesta y una comprobación reproducible que permita verificarla. "
    "Separa riesgos detectados de correcciones propuestas y de verificaciones "
    "realmente ejecutadas. Atiende el feedback recibido e indica qué observación "
    "se corrigió o sigue pendiente.\n"
    "5. No inventes pruebas, ejecuciones, resultados ni evidencia. Solo marca una "
    "verificación como EJECUTADA si el contexto aporta su resultado real; en otro "
    "caso márcala NO EJECUTADA o PENDIENTE y proporciona pasos o un comando "
    "reproducible para realizarla. No afirmes que el sistema es seguro sin evidencia "
    "suficiente.\n"
    "SALIDA: Devuelve un informe listo para security_report.md, con resumen del "
    "alcance revisado y, para cada hallazgo, archivo, ubicación, impacto, evidencia, "
    "corrección propuesta y comprobación con estado EJECUTADA, NO EJECUTADA o "
    "PENDIENTE. Incluye observaciones y pendientes. Si no encuentras hallazgos, "
    "decláralo junto con el alcance y las limitaciones de la revisión, sin convertir "
    "la ausencia de evidencia en una garantía de seguridad.\n"
)


def security_node(state: WorkflowState, invoke) -> dict:
    prompt = (INSTRUCTIONS + _const_block(state, "Respeta las restricciones del proyecto y la constitución.") + "\nRepositorio: " + state["repo_name"] + "\nPlan:\n" + _ctx(state.get("out_plan", ""),2500) + "\nCódigo original:\n" + _ctx(state.get("snapshot", ""),4000) + "\nBackend:\n" + _ctx(state.get("out_backend", ""),6000) + "\nFrontend:\n" + _ctx(state.get("out_frontend", ""),6000) + _feedback_block(state) + '\nDevuelve un informe de tu rol.')
    if state.get("include_data"):
        prompt += "\nContrato aprobado de Datos y persistencia:\n" + _ctx(state.get("out_data", ""), 6000)
    return {"out_security": invoke(prompt)}

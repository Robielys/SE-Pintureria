import collections
import collections.abc
import math
from dataclasses import dataclass
from typing import Any

import streamlit as st

# Compatibilidad con versiones de Python utilizadas por Experta.
for nombre in ("Mapping", "MutableMapping", "Sequence", "Iterable", "Callable"):
    if not hasattr(collections, nombre) and hasattr(collections.abc, nombre):
        setattr(collections, nombre, getattr(collections.abc, nombre))

from experta import Fact, KnowledgeEngine, Rule, MATCH, L, P


# =============================================================================
# 1. CONFIGURACIÓN GENERAL
# =============================================================================

st.set_page_config(
    page_title="Asistente técnico para pintar",
    page_icon="🖌️",
    layout="wide",
)

st.title("🖌️ Asistente técnico para pintar superficies")
st.caption(
    "Sistema de apoyo para orientar la preparación, selección genérica de "
    "recubrimientos y estimación de cantidades. No reemplaza una inspección profesional."
)

SUSTRATOS = {
    "Pared / revoque existente": "revoque_viejo",
    "Pared / revoque nuevo": "revoque_nuevo",
    "Ladrillo": "ladrillo",
    "Yeso": "yeso",
    "Metal / hierro": "metal",
    "Madera": "madera",
}

ESTADOS = {
    "Sin pintar (virgen)": "virgen",
    "Pintura existente en buen estado": "buen_estado",
    "Pintura descascarada o ampollada": "descascarada",
    "Presencia de hongos o moho": "hongos",
    "Humedad visible": "humedad",
    "Manchas blancas / salitre (eflorescencia)": "eflorescencia",
    "Óxido": "oxido",
}

UBICACIONES = {
    "Interior": "interior",
    "Exterior": "exterior",
}

# Rendimientos orientativos para que el prototipo pueda hacer el cálculo.
# Deben reemplazarse por los valores de la ficha técnica del producto concreto.
RENDIMIENTOS_BASE = {
    "fijador_sellador": 15.0,
    "latex_interior": 10.0,
    "latex_exterior": 10.0,
    "primer_metal": 10.0,
    "esmalte": 12.0,
    "primer_madera": 10.0,
    "impregnante": 12.0,
    "recubrimiento_ladrillo": 10.0,
}


# =============================================================================
# 2. HECHOS DEL SISTEMA EXPERTO
# =============================================================================

class Superficie(Fact):
    pass


class NecesidadTratamiento(Fact):
    pass


class EsquemaRecomendado(Fact):
    pass


class InsumoAdicional(Fact):
    pass


class Alerta(Fact):
    pass


class ReglaAplicada(Fact):
    pass


# =============================================================================
# 3. MOTOR DE INFERENCIA EXPERTA
# =============================================================================

class SistemaExpertoPintura(KnowledgeEngine):

    # ----------------------------- DIAGNÓSTICO -------------------------------

    @Rule(Superficie(estado="hongos"))
    def diagnostico_hongos(self):
        self.declare(
            NecesidadTratamiento(
                orden=1,
                paso=(
                    "Antes de pintar: identificar y corregir la causa de humedad. "
                    "Aplicar un líquido fungicida/algicida apto para el sustrato y "
                    "seguir estrictamente su etiqueta. Realizar el lavado posterior "
                    "con agua o con la solución de lavandina únicamente si el "
                    "fabricante del tratamiento lo indica; nunca mezclar lavandina "
                    "con fungicidas, ácidos, amoníaco u otros limpiadores. Ventilar "
                    "y dejar secar completamente antes de aplicar el fondo."
                ),
            ),
            InsumoAdicional(
                categoria="Preparación",
                item="Líquido fungicida/algicida apto para el sustrato, según etiqueta y ficha técnica",
            ),
            InsumoAdicional(
                categoria="Herramientas de limpieza",
                item="Cepillo de cerda dura y elementos para lavado, compatibles con el soporte",
            ),
            InsumoAdicional(
                categoria="Herramientas de preparación",
                item="Lija para pared, solo si quedan imperfecciones y después del tratamiento y secado",
            ),
            InsumoAdicional(
                categoria="Protección personal",
                item="Guantes de nitrilo, protección ocular y respiratoria; ventilación adecuada",
            ),
            ReglaAplicada(
                codigo="DIA-01",
                nombre="Tratamiento de hongos",
                fundamento=(
                    "La presencia de hongos exige tratar la causa de humedad, "
                    "limpiar con un producto indicado para el uso y secar antes de recubrir."
                ),
                fuente="Validar el procedimiento con la ficha técnica y etiqueta del fungicida elegido.",
            ),
        )

    @Rule(Superficie(estado="humedad"))
    def alerta_humedad(self):
        self.declare(
            Alerta(
                codigo="ALT-01",
                motivo="Se detectó humedad visible.",
                detalle=(
                    "No es seguro recomendar una pintura como solución. La humedad "
                    "puede provocar ampollado, desprendimiento o reaparición de manchas."
                ),
                accion=(
                    "Identificar y reparar el origen de la humedad. Esperar a que el "
                    "sustrato esté seco y, si el origen no es evidente o persiste, "
                    "solicitar una inspección profesional."
                ),
            ),
            ReglaAplicada(
                codigo="DIA-02",
                nombre="Bloqueo por humedad",
                fundamento="La humedad activa requiere resolver su origen antes de aplicar un recubrimiento.",
                fuente="Criterio preventivo del prototipo; confirmar con diagnóstico profesional.",
            ),
        )

    @Rule(Superficie(estado="eflorescencia", sustrato=MATCH.sustrato))
    def diagnostico_eflorescencia(self, sustrato):
        if sustrato == "revoque_nuevo":
            self.declare(
                Alerta(
                    codigo="ALT-02A",
                    motivo="No es posible generar una recomendación automatizada segura para esta combinación de parámetros.",
                    detalle=(
                        "Revoque nuevo con eflorescencia/salitre: puede existir humedad activa "
                        "o una condición del soporte que no se resuelve aplicando pintura. "
                        "Además, debe verificarse el curado de la mampostería."
                    ),
                    accion=(
                        "No aplicar fijador ni pintura. Solicitar la inspección de un "
                        "profesional de la construcción para identificar y corregir la "
                        "causa raíz; luego verificar secado y curado antes de definir el sistema."
                    ),
                ),
                ReglaAplicada(
                    codigo="DIA-03A",
                    nombre="Corte por revoque nuevo con eflorescencia",
                    fundamento="La combinación de soporte nuevo y eflorescencia requiere resolver la causa raíz y verificar curado antes de recubrir.",
                    fuente="Criterio de seguridad del sistema; confirmar diagnóstico y condiciones del soporte mediante inspección profesional.",
                ),
            )
            return
        self.declare(
            NecesidadTratamiento(
                orden=1,
                paso=(
                    "No cubrir las manchas. Retirar las sales superficiales en seco "
                    "con un cepillo adecuado, sin dispersar el polvo. Investigar y "
                    "corregir el ingreso o transporte de humedad. No pintar hasta "
                    "que la causa esté resuelta y la superficie esté seca."
                ),
            ),
            InsumoAdicional(
                categoria="Herramientas de preparación",
                item="Cepillo de cerdas adecuado para retirar sales superficiales",
            ),
            InsumoAdicional(
                categoria="Protección personal",
                item="Guantes, protección ocular y protección respiratoria contra polvo",
            ),
            Alerta(
                codigo="ALT-02",
                motivo="Se detectaron manchas compatibles con eflorescencia o salitre.",
                detalle=(
                    "La presencia de sales puede indicar humedad en el muro. "
                    "Una pintura de terminación no corrige la causa."
                ),
                accion=(
                    "Corregir el origen de la humedad y confirmar que el soporte esté "
                    "seco y estable. Si persiste, consultar a un profesional."
                ),
            ),
            ReglaAplicada(
                codigo="DIA-03",
                nombre="Eflorescencia",
                fundamento="Las sales deben retirarse y debe corregirse la causa de humedad antes de pintar.",
                fuente="Criterio preventivo del prototipo; validar el tratamiento específico según el soporte.",
            ),
        )

    @Rule(Superficie(estado="descascarada"))
    def diagnostico_descascarado(self):
        self.declare(
            NecesidadTratamiento(
                orden=1,
                paso=(
                    "Rasquetear la pintura floja o ampollada hasta llegar a una zona "
                    "firme. Lijar suavemente los bordes, retirar todo el polvo y "
                    "reparar imperfecciones con un material compatible si corresponde."
                ),
            ),
            InsumoAdicional(categoria="Herramientas de preparación", item="Espátula o rasqueta"),
            InsumoAdicional(categoria="Herramientas de preparación", item="Lija adecuada al sustrato"),
            InsumoAdicional(categoria="Preparación", item="Masilla o enduido compatible, si hay imperfecciones"),
            ReglaAplicada(
                codigo="DIA-04",
                nombre="Pintura descascarada",
                fundamento="Se debe retirar todo material sin adherencia y preparar el soporte firme antes de repintar.",
                fuente="Validar granulometría y masilla con la ficha técnica del sistema elegido.",
            ),
        )

    @Rule(Superficie(sustrato="metal", estado="oxido"))
    def diagnostico_oxido(self):
        self.declare(
            NecesidadTratamiento(
                orden=1,
                paso=(
                    "Retirar mecánicamente el óxido suelto y las partículas sin "
                    "adherencia. Limpiar y desengrasar con el producto indicado por "
                    "la ficha técnica del recubrimiento. No aplicar el acabado sobre "
                    "óxido suelto."
                ),
            ),
            InsumoAdicional(categoria="Herramientas de preparación", item="Cepillo de alambre para retirar óxido suelto"),
            InsumoAdicional(categoria="Herramientas de preparación", item="Lija para metal y espátula o rasqueta"),
            InsumoAdicional(categoria="Preparación", item="Solvente o desengrasante compatible; aguarrás mineral únicamente si la ficha técnica lo admite"),
            InsumoAdicional(categoria="Protección personal", item="Guantes, protección ocular y respiratoria según tarea"),
            ReglaAplicada(
                codigo="DIA-05",
                nombre="Preparación de metal oxidado",
                fundamento="El óxido no adherido debe eliminarse y el metal debe prepararse antes del sistema anticorrosivo.",
                fuente="La preparación final debe seguir la ficha técnica del primer y del acabado elegidos.",
            ),
        )

    @Rule(Superficie(sustrato="madera", estado="virgen"))
    def diagnostico_madera_virgen(self):
        self.declare(
            NecesidadTratamiento(
                orden=1,
                paso=(
                    "Lijar en el sentido de la veta, retirar completamente el polvo "
                    "y verificar que la madera esté limpia y seca. Aplicar el impregnante "
                    "seleccionado; incorporar un fondo independiente solo si lo exige "
                    "la ficha técnica del producto."
                ),
            ),
            InsumoAdicional(categoria="Herramientas de preparación", item="Lija para madera"),
            InsumoAdicional(categoria="Limpieza", item="Paño limpio para retirar el polvo"),
            ReglaAplicada(
                codigo="DIA-06",
                nombre="Preparación de madera virgen",
                fundamento="La madera debe estar limpia, seca y preparada antes del recubrimiento.",
                fuente="Confirmar lijado, fondo y humedad admisible en la ficha técnica del producto.",
            ),
        )

    @Rule(Superficie(sustrato="revoque_nuevo", curado=False))
    def alerta_revoque_no_curado(self):
        self.declare(
            Alerta(
                codigo="ALT-03",
                motivo="El revoque nuevo todavía no está curado y seco.",
                detalle="Aplicar un recubrimiento antes de cumplir las condiciones del fabricante puede generar fallas de adherencia y durabilidad.",
                accion="Esperar el curado y verificar las condiciones de humedad y alcalinidad exigidas por la ficha técnica.",
            ),
            ReglaAplicada(
                codigo="DIA-07",
                nombre="Bloqueo por revoque nuevo no curado",
                fundamento="No se recomienda recubrir un soporte nuevo sin verificar curado y condiciones de aplicación.",
                fuente="El plazo y los límites deben tomarse de la ficha técnica del producto seleccionado.",
            ),
        )

    # ------------------------------ ESQUEMAS ---------------------------------

    @Rule(
        Superficie(
            sustrato=L("revoque_viejo") | L("revoque_nuevo"),
            ubicacion="interior",
            estado=L("virgen") | L("buen_estado") | L("descascarada") | L("hongos"),
            curado=True,
        )
    )
    def esquema_mamposteria_interior(self):
        self.declare(
            EsquemaRecomendado(
                codigo="REC-01",
                fondo="Fijador o sellador al agua compatible con mampostería",
                clave_fondo="fijador_sellador",
                manos_fondo=1,
                terminacion="Pintura látex acrílica para interior",
                clave_terminacion="latex_interior",
                manos_terminacion=2,
                fundamento="Esquema genérico para mampostería interior firme, seca y correctamente preparada.",
                fuente="Seleccionar productos compatibles y confirmar manos/rendimientos en sus fichas técnicas.",
            ),
            ReglaAplicada(codigo="REC-01", nombre="Mampostería interior", fundamento="Revoque interior firme y seco; si hubo hongos, el esquema queda condicionado a completar el tratamiento, corregir la humedad y secar totalmente.", fuente="Fichas técnicas vigentes del fijador y látex elegidos." )
        )

    @Rule(
        Superficie(
            sustrato=L("revoque_viejo") | L("revoque_nuevo"),
            ubicacion="exterior",
            estado=L("virgen") | L("buen_estado") | L("descascarada"),
            curado=True,
        )
    )
    def esquema_mamposteria_exterior(self):
        self.declare(
            EsquemaRecomendado(
                codigo="REC-02",
                fondo="Fijador o imprimación para mampostería exterior compatible",
                clave_fondo="fijador_sellador",
                manos_fondo=1,
                terminacion="Recubrimiento acrílico para exterior",
                clave_terminacion="latex_exterior",
                manos_terminacion=2,
                fundamento="Esquema genérico para mampostería exterior firme, seca y preparada.",
                fuente="Confirmar que el producto esté especificado para exterior y para el tipo de soporte.",
            ),
            ReglaAplicada(codigo="REC-02", nombre="Mampostería exterior", fundamento="Revoque exterior firme, seco y preparado.", fuente="Fichas técnicas vigentes del fondo y recubrimiento exterior." )
        )

    @Rule(
        Superficie(
            sustrato="yeso",
            ubicacion="interior",
            estado=L("virgen") | L("buen_estado") | L("descascarada"),
        )
    )
    def esquema_yeso_interior(self):
        self.declare(
            EsquemaRecomendado(
                codigo="REC-03",
                fondo="Sellador o imprimación indicada para yeso",
                clave_fondo="fijador_sellador",
                manos_fondo=1,
                terminacion="Pintura látex acrílica para interior",
                clave_terminacion="latex_interior",
                manos_terminacion=2,
                fundamento="Esquema genérico para yeso interior seco y firme.",
                fuente="Verificar absorción, preparación y compatibilidad en la ficha técnica.",
            ),
            ReglaAplicada(codigo="REC-03", nombre="Yeso interior", fundamento="Yeso interior seco y firme.", fuente="Ficha técnica vigente del sellador y látex." )
        )

    @Rule(Superficie(sustrato="yeso", ubicacion="exterior"))
    def alerta_yeso_exterior(self):
        self.declare(
            Alerta(
                codigo="ALT-04",
                motivo="La combinación yeso + exterior no está contemplada por este prototipo.",
                detalle="No se debe extrapolar automáticamente un esquema de yeso interior a una exposición exterior.",
                accion="Solicitar evaluación del sistema constructivo y de un recubrimiento expresamente aprobado para ese uso.",
            )
        )

    @Rule(
        Superficie(
            sustrato="metal",
            estado=L("virgen") | L("buen_estado") | L("descascarada") | L("oxido"),
            ubicacion=MATCH.ubicacion,
        )
    )
    def esquema_metal(self, ubicacion):
        self.declare(
            EsquemaRecomendado(
                codigo="REC-04",
                fondo="Fondo antióxido compatible (o convertidor de óxido únicamente si el sistema completo lo admite)",
                clave_fondo="primer_metal",
                manos_fondo=1,
                terminacion=(
                    "Esmalte sintético para metal apto para "
                    f"{'interior' if ubicacion == 'interior' else 'exterior'}"
                ),
                clave_terminacion="esmalte",
                manos_terminacion=2,
                fundamento="Sistema genérico de protección para metal; la imprimación y el esmalte deben formar un sistema compatible.",
                fuente="Verificar tipo de metal, preparación, interior/exterior y compatibilidad en las fichas técnicas.",
            ),
            ReglaAplicada(
                codigo="REC-04",
                nombre=f"Sistema anticorrosivo para metal en {ubicacion}",
                fundamento=(
                    "La imprimación anticorrosiva y el esmalte deben ser compatibles "
                    f"entre sí y aptos para {ubicacion}."
                ),
                fuente="Fichas técnicas vigentes del fondo antióxido/convertidor y esmalte sintético.",
            )
        )

    @Rule(
        Superficie(
            sustrato="madera",
            estado=L("virgen") | L("buen_estado") | L("descascarada"),
            ubicacion=MATCH.ubicacion,
        )
    )
    def esquema_madera(self, ubicacion):
        self.declare(
            EsquemaRecomendado(
                codigo="REC-05",
                fondo="No se prevé un fondo independiente para esta recomendación de impregnante; verificar la ficha técnica",
                clave_fondo="primer_madera",
                manos_fondo=0,
                terminacion=(
                    "Impregnante para madera (acabado satinado o brillante), apto para "
                    f"{'interior' if ubicacion == 'interior' else 'exterior'}"
                ),
                clave_terminacion="impregnante",
                manos_terminacion=2,
                fundamento="Sistema genérico de protección de madera. No asumir aplicación directa sin consultar la ficha técnica.",
                fuente="Confirmar uso interior/exterior, necesidad de fondo y número de manos en la ficha técnica.",
            ),
            ReglaAplicada(
                codigo="REC-05",
                nombre=f"Protección de madera para {ubicacion}",
                fundamento=(
                    f"Madera limpia y seca. Se recomienda impregnante apto para {ubicacion}; "
                    "el fondo solo se aplica si lo requiere la ficha técnica del producto."
                ),
                fuente="Ficha técnica vigente del protector/impregnante, que debe indicar aptitud para interior o exterior.",
            )
        )

    @Rule(
        Superficie(
            sustrato="ladrillo",
            estado=L("virgen") | L("buen_estado") | L("descascarada"),
        )
    )
    def esquema_ladrillo(self):
        self.declare(
            EsquemaRecomendado(
                codigo="REC-06",
                fondo="Imprimación o sellador indicado para ladrillo y su porosidad",
                clave_fondo="fijador_sellador",
                manos_fondo=1,
                terminacion="Recubrimiento acrílico indicado para ladrillo y ubicación",
                clave_terminacion="recubrimiento_ladrillo",
                manos_terminacion=2,
                fundamento="Esquema genérico sujeto a que el ladrillo esté firme, seco y sea apto para el recubrimiento.",
                fuente="Validar si el producto admite ladrillo visto, mampostería y la exposición correspondiente.",
            ),
            ReglaAplicada(codigo="REC-06", nombre="Recubrimiento para ladrillo", fundamento="Ladrillo firme y seco con producto indicado para el soporte y exposición.", fuente="Ficha técnica vigente del sellador y recubrimiento." )
        )

    # --------------------------- HERRAMIENTAS --------------------------------

    @Rule(EsquemaRecomendado(terminacion=P(lambda t: "látex" in t.lower() or "acrílico" in t.lower())))
    def insumos_pintura_muros(self):
        self.declare(
            InsumoAdicional(categoria="Aplicación", item="Rodillo adecuado al relieve y al producto"),
            InsumoAdicional(categoria="Aplicación", item="Pincel o brocha para bordes y encuentros"),
            InsumoAdicional(categoria="Aplicación", item="Bandeja o recipiente de aplicación"),
            InsumoAdicional(categoria="Protección del entorno", item="Cinta de enmascarar y cubrepisos"),
            ReglaAplicada(
                codigo="INS-01",
                nombre="Herramientas para recubrimientos de pared",
                fundamento="Se incluyen herramientas diferenciadas para paños y sectores de detalle.",
                fuente="Elegir rodillo y accesorios según la ficha técnica y la textura del soporte.",
            ),
        )

    @Rule(EsquemaRecomendado(terminacion=P(lambda t: "esmalte" in t.lower())))
    def insumos_metal(self):
        self.declare(
            InsumoAdicional(categoria="Aplicación", item="Pincel o rodillo apto para esmalte"),
            InsumoAdicional(categoria="Aplicación", item="Bandeja o recipiente compatible"),
            InsumoAdicional(categoria="Protección del entorno", item="Cinta de enmascarar y cubrepisos"),
            ReglaAplicada(
                codigo="INS-02",
                nombre="Herramientas para esmalte",
                fundamento="La herramienta debe ser apta para el tipo de esmalte y el acabado buscado.",
                fuente="Verificar herramienta y diluyente únicamente en la ficha técnica del producto.",
            ),
        )

    @Rule(EsquemaRecomendado(terminacion=P(lambda t: "madera" in t.lower() or "impregnante" in t.lower())))
    def insumos_madera(self):
        self.declare(
            InsumoAdicional(
                categoria="Aplicación (elegir una alternativa)",
                item="Opción A — Pincel de cerda fina, siguiendo la veta de la madera.",
            ),
            InsumoAdicional(
                categoria="Aplicación (elegir una alternativa)",
                item=(
                    "Opción B — Pistola de pintar/soplete, únicamente si el protector "
                    "admite pulverización y se cuenta con ventilación y protección adecuadas."
                ),
            ),
            InsumoAdicional(categoria="Protección del entorno", item="Cubrepisos y cinta de enmascarar"),
            ReglaAplicada(
                codigo="INS-03",
                nombre="Herramientas para madera",
                fundamento=(
                    "El pincel y la pistola son métodos alternativos de aplicación para "
                    "la misma tarea; se debe elegir uno solo según el producto y las condiciones de trabajo."
                ),
                fuente=(
                    "Consultar la ficha técnica del protector para confirmar si admite "
                    "aplicación con pincel o pulverización."
                ),
            ),
        )


# =============================================================================
# 4. VALIDACIONES Y EJECUCIÓN
# =============================================================================

ESTADOS_VALIDOS_POR_SUSTRATO = {
    "revoque_viejo": {"virgen", "buen_estado", "descascarada", "hongos", "humedad", "eflorescencia"},
    "revoque_nuevo": {"virgen", "buen_estado", "descascarada", "hongos", "humedad", "eflorescencia"},
    "ladrillo": {"virgen", "buen_estado", "descascarada", "hongos", "humedad", "eflorescencia"},
    "yeso": {"virgen", "buen_estado", "descascarada", "hongos", "humedad"},
    "metal": {"virgen", "buen_estado", "descascarada", "oxido"},
    "madera": {"virgen", "buen_estado", "descascarada", "hongos", "humedad"},
}


def redondear_litros(cantidad: float) -> int:
    """Redondea hacia arriba a litros enteros para estimación de compra."""
    return max(1, math.ceil(cantidad))


def calcular_cantidad(m2: float, manos: int, rendimiento: float) -> int:
    if rendimiento <= 0:
        raise ValueError("El rendimiento debe ser mayor que cero.")
    return redondear_litros((m2 * manos) / rendimiento)


def ejecutar_sistema(sustrato, estado, ubicacion, m2, curado, rendimientos):
    if m2 <= 0:
        return {"error": "Ingresá una superficie mayor que 0 m²."}

    if estado not in ESTADOS_VALIDOS_POR_SUSTRATO[sustrato]:
        return {
            "error": (
                "La combinación de sustrato y estado no está contemplada. "
                "No se genera una recomendación automática para evitar una indicación insegura."
            )
        }

    motor = SistemaExpertoPintura()
    motor.reset()
    motor.declare(
        Superficie(
            sustrato=sustrato,
            estado=estado,
            ubicacion=ubicacion,
            m2=float(m2),
            curado=bool(curado),
        )
    )
    motor.run()

    hechos = list(motor.facts.values())
    alertas = [f for f in hechos if isinstance(f, Alerta)]
    tratamientos = sorted(
        [f for f in hechos if isinstance(f, NecesidadTratamiento)],
        key=lambda f: f["orden"],
    )
    esquemas = [f for f in hechos if isinstance(f, EsquemaRecomendado)]
    insumos = [f for f in hechos if isinstance(f, InsumoAdicional)]
    reglas = [f for f in hechos if isinstance(f, ReglaAplicada)]
    hechos_inferidos = [
        {"tipo": type(f).__name__, "contenido": dict(f)}
        for f in hechos
        if not isinstance(f, Superficie)
    ]

    # Cualquier alerta bloquea la recomendación de pintura.
    if alertas:
        return {
            "alertas": alertas,
            "tratamientos": tratamientos,
            "reglas": reglas,
            "hechos_entrada": {"sustrato": sustrato, "estado": estado, "ubicacion": ubicacion, "superficie_m2": float(m2), "revoque_curado": bool(curado)},
            "hechos_inferidos": hechos_inferidos,
            "bloqueado": True,
        }

    if not esquemas:
        return {
            "error": (
                "No existe una regla de recubrimiento para esta combinación. "
                "El sistema no puede emitir una recomendación segura; se requiere "
                "revisión de una persona especializada."
            ),
            "tratamientos": tratamientos,
            "reglas": reglas,
            "hechos_entrada": {"sustrato": sustrato, "estado": estado, "ubicacion": ubicacion, "superficie_m2": float(m2), "revoque_curado": bool(curado)},
            "hechos_inferidos": hechos_inferidos,
        }

    esquema = esquemas[0]
    cantidades = {
        "fondo": (
            calcular_cantidad(m2, esquema["manos_fondo"], rendimientos[esquema["clave_fondo"]])
            if esquema["manos_fondo"] > 0 else 0
        ),
        "terminacion": calcular_cantidad(
            m2,
            esquema["manos_terminacion"],
            rendimientos[esquema["clave_terminacion"]],
        ),
    }

    # Herramientas comunes y elementos básicos de protección.
    insumos.extend(
        [
            InsumoAdicional(categoria="Protección personal", item="Guantes adecuados a los productos utilizados"),
            InsumoAdicional(categoria="Protección personal", item="Protección ocular cuando exista riesgo de salpicaduras o polvo"),
            InsumoAdicional(categoria="Protección del entorno", item="Cubrepisos o cartón protector"),
            InsumoAdicional(categoria="Limpieza", item="Paños y elementos de limpieza compatibles con el producto"),
        ]
    )

    # Deduplicar insumos manteniendo las categorías.
    agrupados = {}
    for insumo in insumos:
        agrupados.setdefault(insumo["categoria"], set()).add(insumo["item"])

    return {
        "bloqueado": False,
        "esquema": esquema,
        "cantidades": cantidades,
        "tratamientos": tratamientos,
        "insumos": agrupados,
        "reglas": reglas,
        "hechos_entrada": {"sustrato": sustrato, "estado": estado, "ubicacion": ubicacion, "superficie_m2": float(m2), "revoque_curado": bool(curado)},
        "hechos_inferidos": hechos_inferidos,
    }


# =============================================================================
# 5. INTERFAZ STREAMLIT
# =============================================================================

with st.sidebar:
    st.header("Parámetros de cálculo")

    origen_rendimientos = st.selectbox(
        "Origen de los rendimientos",
        options=[
            "Valores orientativos del sistema",
            "Ficha técnica o etiqueta del producto",
        ],
        help="Elegí si vas a utilizar los valores iniciales o los rendimientos declarados por el fabricante.",
    )

    if origen_rendimientos == "Valores orientativos del sistema":
        st.warning(
            "Se utilizarán valores de referencia. "
            "Las cantidades son estimativas y deben verificarse."
        )
    else:
        st.info(
            "Ingresá manualmente los rendimientos indicados en las fichas "
            "técnicas o etiquetas de los productos que vas a utilizar."
        )

    st.caption(
        "Todos los rendimientos se expresan en m² por litro y por mano, "
        "salvo que el fabricante indique otra condición."
    )

    etiquetas = {
        "fijador_sellador": "Fijador / sellador (m²/L)",
        "latex_interior": "Látex interior (m²/L)",
        "latex_exterior": "Acrílico exterior (m²/L)",
        "primer_metal": "Fondo antióxido (m²/L)",
        "esmalte": "Esmalte para metal (m²/L)",
        "primer_madera": "Fondo para madera (m²/L)",
        "impregnante": "Impregnante para madera (m²/L)",
        "recubrimiento_ladrillo": "Recubrimiento para ladrillo (m²/L)",
    }

    # Los dos modos son excluyentes: el modo orientativo ignora por completo
    # cualquier valor que haya quedado guardado en los widgets editables.
    if origen_rendimientos == "Valores orientativos del sistema":
        rendimientos = dict(RENDIMIENTOS_BASE)
        st.caption("Rendimientos orientativos utilizados por el prototipo:")
        for clave, etiqueta in etiquetas.items():
            st.write(f"- {etiqueta}: **{rendimientos[clave]:.1f} m²/L**")
    else:
        rendimientos = {}
        for clave, etiqueta in etiquetas.items():
            rendimientos[clave] = st.number_input(
                etiqueta,
                min_value=0.1,
                value=float(RENDIMIENTOS_BASE[clave]),
                step=0.5,
                key=f"rend_{clave}",
            )

        st.caption(
            "Se utilizarán exclusivamente los rendimientos que ingreses "
            "a partir de las fichas técnicas o etiquetas."
        )

st.subheader("1. Características de la superficie")
col1, col2 = st.columns(2)

with col1:
    sustrato_label = st.selectbox(
        "¿De qué material es la superficie?",
        options=list(SUSTRATOS.keys()),
        index=None,
        placeholder="Seleccioná el material",
    )
    estado_label = st.selectbox(
        "¿En qué estado se encuentra?",
        options=list(ESTADOS.keys()),
        index=None,
        placeholder="Seleccioná el estado",
    )

with col2:
    ubicacion_label = st.selectbox(
        "¿Dónde está ubicada?",
        options=list(UBICACIONES.keys()),
        index=None,
        placeholder="Seleccioná interior o exterior",
    )
    m2 = st.number_input(
        "Superficie a pintar (m²)",
        min_value=0.1,
        value=30.0,
        step=1.0,
        format="%.1f",
    )

curado = True
if sustrato_label == "Pared / revoque nuevo":
    curado = st.radio(
        "¿El revoque nuevo está curado y seco según las indicaciones aplicables?",
        options=[True, False],
        format_func=lambda x: "Sí" if x else "No / No estoy seguro",
        horizontal=True,
    )

st.info(
    "Si hay humedad activa, salitre o una patología cuyo origen no se conoce, "
    "el sistema puede bloquear la recomendación de pintura."
)

if st.button("Generar recomendación", type="primary", use_container_width=True):
    if not all([sustrato_label, estado_label, ubicacion_label]):
        st.error("Completá todos los datos obligatorios antes de generar el diagnóstico.")
    else:
        resultado = ejecutar_sistema(
            SUSTRATOS[sustrato_label],
            ESTADOS[estado_label],
            UBICACIONES[ubicacion_label],
            float(m2),
            curado,
            rendimientos,
        )

        st.session_state["ultimo_resultado"] = resultado
        st.session_state["ultimos_parametros"] = {
            "sustrato": sustrato_label,
            "estado": estado_label,
            "ubicacion": ubicacion_label,
            "m2": m2,
        }
        # Guardar una copia de los valores exactos usados en este cálculo.
        st.session_state["rendimientos_usados"] = dict(rendimientos)
        st.session_state["origen_rendimientos"] = origen_rendimientos

# Recuperar los datos fuera del botón: Streamlit vuelve a ejecutar todo
# el archivo ante cualquier cambio de widget.
rendimientos_usados = st.session_state.get(
    "rendimientos_usados", dict(RENDIMIENTOS_BASE)
)
origen_usado = st.session_state.get(
    "origen_rendimientos", "Valores orientativos del sistema"
)

if "ultimo_resultado" in st.session_state:
    resultado = st.session_state["ultimo_resultado"]
    parametros = st.session_state.get("ultimos_parametros", {})

    st.divider()
    st.subheader("2. Resultado del análisis")
    if parametros:
        st.caption(
            f"{parametros['m2']} m² · {parametros['sustrato']} · "
            f"{parametros['estado']} · {parametros['ubicacion']}"
        )

    if resultado.get("error"):
        st.error(resultado["error"])

    if resultado.get("alertas"):
        for alerta in resultado["alertas"]:
            st.error(f"**{alerta['motivo']}**\n\n{alerta['detalle']}\n\n**Qué hacer:** {alerta['accion']}")

    if resultado.get("tratamientos"):
        st.markdown("### Preparación y diagnóstico")
        for i, tratamiento in enumerate(resultado["tratamientos"], start=1):
            st.markdown(f"{i}. {tratamiento['paso']}")

    if resultado.get("esquema"):
        esquema = resultado["esquema"]
        cantidades = resultado["cantidades"]
        st.markdown("### Esquema de recubrimientos")
        if parametros.get("estado") == "Presencia de hongos o moho":
            st.warning("Este esquema es condicional: aplicarlo únicamente después de completar la limpieza/tratamiento, corregir el origen de humedad y confirmar que la superficie esté completamente seca.")
        if esquema["manos_fondo"] > 0:
            st.markdown(
                f"- **Fondo / imprimación:** {esquema['fondo']} "
                f"({esquema['manos_fondo']} mano(s))."
            )
        else:
            st.markdown(f"- **Fondo / imprimación:** {esquema['fondo']}.")
        st.markdown(
            f"- **Terminación:** {esquema['terminacion']} "
            f"({esquema['manos_terminacion']} manos)."
        )

        st.markdown("### Cantidades estimadas para comprar")

        superficie = float(parametros["m2"])

        st.caption(
            f"Superficie a cubrir: {superficie:.1f} m²"
        )

        if cantidades["fondo"] > 0:
            rendimiento_fondo = rendimientos_usados[
                esquema["clave_fondo"]
            ]

            consumo_fondo = (
                superficie * esquema["manos_fondo"]
            ) / rendimiento_fondo

            st.markdown("**1. Fondo o imprimación**")

            st.markdown(
                f"- Producto: {esquema['fondo']}"
            )
            st.markdown(
                f"- Cantidad estimada: **{cantidades['fondo']} litros**"
            )
            st.caption(
                f"Cálculo: {superficie:.1f} m² × "
                f"{esquema['manos_fondo']} mano(s) ÷ "
                f"{rendimiento_fondo:.1f} m²/L = "
                f"{consumo_fondo:.2f} L. "
                f"Se redondea hacia arriba."
            )

        st.markdown("**2. Pintura de terminación**")

        rendimiento_terminacion = rendimientos_usados[
            esquema["clave_terminacion"]
        ]

        consumo_terminacion = (
            superficie * esquema["manos_terminacion"]
        ) / rendimiento_terminacion

        st.markdown(
            f"- Producto: {esquema['terminacion']}"
        )
        st.markdown(
            f"- Cantidad estimada: **{cantidades['terminacion']} litros**"
        )
        st.caption(
            f"Cálculo: {superficie:.1f} m² × "
            f"{esquema['manos_terminacion']} manos ÷ "
            f"{rendimiento_terminacion:.1f} m²/L = "
            f"{consumo_terminacion:.2f} L. "
            f"Se redondea hacia arriba."
        )

        st.divider()

        st.markdown("**Origen de los rendimientos utilizados**")

        if origen_usado == "Valores orientativos del sistema":
            st.warning(
                "Se utilizaron rendimientos orientativos del prototipo. "
                "Las cantidades no representan una medición exacta ni "
                "sustituyen los datos del fabricante."
            )
        else:
            st.success(
                "Se utilizaron los rendimientos ingresados manualmente "
                "a partir de la ficha técnica o etiqueta del producto."
            )

        st.caption(
            "Las cantidades corresponden a litros estimados de aplicación. "
            "No incluyen margen por desperdicio, absorción extraordinaria "
            "ni conversión a envases comerciales. Para productos auxiliares "
            "como fungicidas, consultar la dosificación de su fabricante."
        )

    if resultado.get("insumos"):
        st.markdown("### Herramientas, protección e insumos")
        for categoria, items in resultado["insumos"].items():
            st.markdown(f"**{categoria}**")
            for item in sorted(items):
                st.markdown(f"- {item}")

    if resultado.get("reglas") or resultado.get("hechos_entrada"):
        with st.expander("Trazabilidad de inferencia: hechos y reglas activadas"):
            st.markdown("**Hechos de entrada declarados**")
            st.json(resultado.get("hechos_entrada", {}))
            st.markdown("**Hechos inferidos (nuevos hechos incorporados a la memoria de trabajo)**")
            st.json(resultado.get("hechos_inferidos", []))
            st.markdown("**Reglas disparadas por el motor**")
            if resultado.get("reglas"):
                for regla in resultado["reglas"]:
                    st.markdown(f"**{regla['codigo']} — {regla['nombre']}**")
                    st.write(f"Condición/fundamento: {regla['fundamento']}")
                    st.caption(f"Referencia a verificar: {regla['fuente']}")
            else:
                st.write("No se registraron reglas adicionales.")

st.divider()
with st.expander("Alcance y limitaciones del prototipo"):
    st.markdown(
        """
        - No recomienda marcas comerciales ni combina productos de fabricantes distintos.
        - No reconoce colores mediante fotografías (RF-07 fuera de alcance).
        - No diagnostica causas estructurales de humedad, filtraciones ni patologías ocultas.
        - No sustituye una inspección profesional ni las fichas técnicas vigentes.
        - Los rendimientos y manos deben confirmarse para cada producto real.
        - No calcula presupuesto, disponibilidad, tiempos de obra ni condiciones climáticas.
        - Ante una combinación no contemplada o una alerta, no emite una recomendación automática.
        - Las cantidades de productos auxiliares de limpieza y tratamiento no se calculan si no se dispone de su rendimiento o dosificación específica.
- El sistema no determina presentaciones comerciales ni disponibilidad de envases.
        """
    )

             
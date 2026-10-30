import streamlit as st
import collections
import collections.abc
import math

# ==============================================================================
# 1. PARCHE DE COMPATIBILIDAD DE EXPERTA (Debe ir ANTES de importar experta)
# ==============================================================================
for nombre in ("Mapping", "MutableMapping", "Sequence", "Iterable", "Callable"):
    if not hasattr(collections, nombre) and hasattr(collections.abc, nombre):
        setattr(collections, nombre, getattr(collections.abc, nombre))

from experta import Fact, KnowledgeEngine, Rule, MATCH, L, P

# ==============================================================================
# 2. DEFINICIÓN DE HECHOS (Memoria de Trabajo)
# ==============================================================================
class Superficie(Fact):
    pass

class NecesidadTratamiento(Fact):
    pass

class EsquemaRecomendado(Fact):
    pass

class InsumoAdicional(Fact):
    pass

class AlertaIncompatibilidad(Fact):
    pass

# ==============================================================================
# 3. MOTOR DE INFERENCIA
# ==============================================================================
class SistemaExpertoPintura(KnowledgeEngine):

    # --------------------------------------------------------------------------
    # PREPARACIÓN Y DIAGNÓSTICO
    # --------------------------------------------------------------------------
    @Rule(Superficie(estado='hongos'))
    def tratamiento_hongos(self):
        self.declare(NecesidadTratamiento(
            paso="Aplicar líquido fungicida/algicida, lavar con agua y lavandina diluida, y dejar secar completamente antes de pintar."
        ))
        self.declare(InsumoAdicional(categoria="Herramientas de Limpieza", item="Cepillo de cerda dura"))
        self.declare(InsumoAdicional(categoria="Productos de Preparación", item="Líquido fungicida / Lavandina diluida"))
        self.declare(InsumoAdicional(categoria="Productos de Preparación", item="Lija de grano fino"))
        self.declare(InsumoAdicional(categoria="Protección Personal", item="Guantes de nitrilo"))

    @Rule(Superficie(estado='descascarada'))
    def tratamiento_descascarado(self):
        self.declare(NecesidadTratamiento(
            paso="Rasquetear toda la pintura suelta o ampollada con espátula y lijar los bordes hasta dejar la superficie firme."
        ))
        self.declare(InsumoAdicional(categoria="Herramientas de Preparación", item="Espátula de metal"))
        self.declare(InsumoAdicional(categoria="Productos de Preparación", item="Lija de grano mediano (120)"))

    @Rule(Superficie(sustrato='metal', estado='oxido'))
    def tratamiento_oxido_metal(self):
        self.declare(NecesidadTratamiento(
            paso="Lijar o cepillar el óxido suelto y remover restos de grasa o suciedad utilizando aguarrás."
        ))
        self.declare(InsumoAdicional(categoria="Herramientas de Preparación", item="Cepillo de alambre y Espátula"))
        self.declare(InsumoAdicional(categoria="Productos de Preparación", item="Lija para metal y Aguarrás mineral"))

    @Rule(Superficie(sustrato='madera', estado='virgen'))
    def tratamiento_madera_virgen(self):
        self.declare(NecesidadTratamiento(
            paso="Lijar suavemente la madera en el sentido de las vetas para eliminar asperezas y mejorar la adherencia."
        ))
        self.declare(InsumoAdicional(categoria="Productos de Preparación", item="Lija para madera (grano mediano/fino)"))

    # --------------------------------------------------------------------------
    # ESQUEMAS DE PINTURA Y CANTIDADES
    # --------------------------------------------------------------------------
    @Rule(
        Superficie(sustrato=L('revoque_viejo') | L('yeso'),
                   ubicacion='interior',
                   m2=MATCH.m2)
    )
    def esquema_interior_muros(self, m2):
        litros_fondo = math.ceil(m2 / 15)
        litros_pintura = math.ceil((m2 * 2) / 10)
        self.declare(EsquemaRecomendado(
            fondo="Fijador Sellador al agua",
            litros_fondo=litros_fondo,
            terminacion="Látex Acrílico Interior",
            litros_terminacion=litros_pintura,
            manos=2
        ))

    @Rule(
        Superficie(sustrato='metal', ubicacion='exterior', m2=MATCH.m2)
    )
    def esquema_metal_exterior(self, m2):
        litros_fondo = math.ceil(m2 / 10)
        litros_pintura = math.ceil((m2 * 2) / 12)
        self.declare(EsquemaRecomendado(
            fondo="Fondo Antióxido o Convertidor de Óxido",
            litros_fondo=litros_fondo,
            terminacion="Esmalte Sintético Exterior",
            litros_terminacion=litros_pintura,
            manos=2
        ))

    @Rule(
        Superficie(sustrato='madera', ubicacion='exterior', m2=MATCH.m2)
    )
    def esquema_madera_exterior(self, m2):
        litros_pintura = math.ceil((m2 * 2) / 12)
        self.declare(EsquemaRecomendado(
            fondo="No requiere base previa (aplicación directa)",
            litros_fondo=0,
            terminacion="Impregnante protector para madera",
            litros_terminacion=litros_pintura,
            manos=2
        ))

    # --------------------------------------------------------------------------
    # HERRAMIENTAS Y APLICACIÓN
    # --------------------------------------------------------------------------
    @Rule(EsquemaRecomendado(terminacion=P(lambda t: "Látex" in t)))
    def herramientas_latex(self):
        self.declare(InsumoAdicional(categoria="Herramientas de Pintado", item="Rodillo de pelo corto O Pincel ancho (Opciones equivalentes)"))
        self.declare(InsumoAdicional(categoria="Protección del Lugar", item="Cinta de enmascarar"))

    @Rule(EsquemaRecomendado(terminacion=P(lambda t: "Esmalte" in t)))
    def herramientas_esmalte(self):
        self.declare(InsumoAdicional(categoria="Herramientas de Pintado", item="Pincel / Brocha plana O Rodillo para sintético"))
        self.declare(InsumoAdicional(categoria="Limpieza de Herramientas", item="Aguarrás mineral"))

    @Rule(EsquemaRecomendado(terminacion=P(lambda t: "Impregnante" in t)))
    def herramientas_impregnante(self):
        self.declare(InsumoAdicional(categoria="Herramientas de Pintado", item="Pincel de cerda fina O Pistola de pintar / Soplete (Opciones equivalentes)"))

    # --------------------------------------------------------------------------
    # ALERTAS Y RECOMENDACIONES
    # --------------------------------------------------------------------------
    @Rule(Superficie(sustrato='revoque_nuevo', estado='eflorescencia'))
    def alerta_eflorescencia(self):
        self.declare(AlertaIncompatibilidad(
            motivo="Problema de humedad de cimientos o falta de curado de la pared.",
            detalle="Aplicar pintura sobre una pared nueva con salitre o humedad provocará que el producto se ampolle y se desprenda en poco tiempo.",
            accion="Te recomendamos solucionar primero la causa de la humedad o consultar con un profesional de la construcción antes de aplicar cualquier pintura."
        ))

# ==============================================================================
# 4. LÓGICA Y MAPEO
# ==============================================================================
OPCIONES_SUSTRATO = {
    "Pared existente / Revoque viejo": "revoque_viejo",
    "Pared nueva / Revoque fresco": "revoque_nuevo",
    "Metal / Hierro": "metal",
    "Madera": "madera",
    "Yeso": "yeso"
}

OPCIONES_ESTADO = {
    "Tiene hongos o moho": "hongos",
    "Tiene óxido": "oxido",
    "Tiene manchas blancas de salitre o humedad": "eflorescencia",
    "Está sin pintar (virgen)": "virgen",
    "Tiene pintura descascarada / saltada": "descascarada",
    "Está en buen estado (pintada)": "buen_estado"
}

OPCIONES_UBICACION = {
    "Interior (Habitaciones, pasillos, etc.)": "interior",
    "Exterior (Fachadas, patios, intemperie)": "exterior"
}

def resolver_sistema_experto(sustrato_label, estado_label, ubicacion_label, m2):
    if m2 is None or m2 <= 0:
        return "⚠️ **Por favor, ingresa un número de m² válido mayor a 0.**", ""

    motor = SistemaExpertoPintura()
    motor.reset()
    motor.declare(Superficie(
        sustrato=OPCIONES_SUSTRATO[sustrato_label],
        estado=OPCIONES_ESTADO[estado_label],
        ubicacion=OPCIONES_UBICACION[ubicacion_label],
        m2=float(m2)
    ))
    motor.run()

    # Manejo de Alertas para el usuario
    alertas = [f for f in motor.facts.values() if isinstance(f, AlertaIncompatibilidad)]
    if alertas:
        lineas_alerta = [
            "## ⚠️ Recomendación Especial",
            "**No es posible recomendar una pintura directa para este caso.**",
            ""
        ]
        for a in alertas:
            lineas_alerta.append(f"**Motivo:** {a['motivo']}")
            lineas_alerta.append(f"- **Explicación:** {a['detalle']}")
            lineas_alerta.append(f"\n👉 **¿Qué debes hacer?:** {a['accion']}")

        traza_alerta = "### 🔎 Detalle Técnico\n- El motor de reglas detuvo la recomendación para evitar una falla en la aplicación por humedad no tratada."
        return "\n".join(lineas_alerta), traza_alerta

    # Salida normal para el usuario
    lineas = [
        "## 📋 Tu Lista de Materiales y Guía de Trabajo",
        f"*Resumen:* Superficie de **{m2} m²** | Material: **{sustrato_label}** | Ubicación: **{ubicacion_label}**",
        "---",
        "### 1. 🛠️ Pasos Previos de Preparación"
    ]

    tratamientos = [f for f in motor.facts.values() if isinstance(f, NecesidadTratamiento)]
    if tratamientos:
        for idx, t in enumerate(tratamientos, 1):
            lineas.append(f"- {t['paso']}")
    else:
        lineas.append("- La superficie está lista para pintar. Solo realiza una limpieza básica del polvo con un trapo seco.")

    lineas.append("\n### 2. 🎨 Pinturas y Cantidades a Comprar")
    esquemas = [f for f in motor.facts.values() if isinstance(f, EsquemaRecomendado)]
    for e in esquemas:
        if e['litros_fondo'] > 0:
            lineas.append(f"- **Base / Imprimación:** {e['fondo']} → **Comprar approx. {e['litros_fondo']} Litro(s)**")
        lineas.append(f"- **Pintura de Terminación:** {e['terminacion']} ({e['manos']} manos) → **Comprar approx. {e['litros_terminacion']} Litro(s)**")

    lineas.append("\n### 3. 🧰 Herramientas y Elementos Recomendados")
    insumos = [f for f in motor.facts.values() if isinstance(f, InsumoAdicional)]
    categorias = {}
    for i in insumos:
        cat = i['categoria']
        categorias.setdefault(cat, set()).add(i['item'])

    for cat, items in categorias.items():
        lineas.append(f"**[{cat}]**")
        for item in items:
            lineas.append(f"- {item}")

    # Trazabilidad técnica secundaria
    traza = ["### 🔎 Detalle Técnico de Reglas"]
    traza.append(f"- Evaluado correctamente mediante reglas determinísticas de compatibilidad física y química.")
    if tratamientos:
        traza.append("- Regla de diagnóstico activada por patología detectada.")
    if esquemas:
        traza.append("- Regla de esquema de recubrimiento y cálculo de litros por m² completada.")

    return "\n".join(lineas), "\n".join(traza)


# ==============================================================================
# 5. INTERFAZ GRÁFICA (Streamlit UI)
# ==============================================================================

# Configuración inicial de la página
st.set_page_config(page_title="Asistente de Pintado", page_icon="🖌️", layout="centered")

# Encabezado
st.title("🖌️ Asistente Técnico para Pintar tu Superficie")
st.markdown("Ingresa los datos de tu pared, madera o metal y calcula automáticamente qué productos, cantidades y herramientas necesitas.")
st.divider()

# Formularios de Entrada
col1, col2 = st.columns(2)
with col1:
    sustrato = st.selectbox(
        "¿De qué material es tu superficie?",
        options=list(OPCIONES_SUSTRATO.keys())
    )
with col2:
    estado = st.selectbox(
        "¿En qué estado se encuentra?",
        options=list(OPCIONES_ESTADO.keys())
    )

col3, col4 = st.columns(2)
with col3:
    ubicacion = st.selectbox(
        "¿Dónde está ubicada?",
        options=list(OPCIONES_UBICACION.keys())
    )
with col4:
    m2 = st.number_input(
        "¿Cuántos metros cuadrados (m²) vas a pintar?",
        min_value=0.1, 
        value=30.0, 
        step=1.0,
        format="%.1f"
    )

st.write("") # Espaciador

# Ejecución e Inferencia
if st.button("⚡ Generar recomendación", type="primary", use_container_width=True):
    # Ejecutamos el sistema experto
    resultado_md, diagnostico_md = resolver_sistema_experto(sustrato, estado, ubicacion, m2)
    
    # Mostrar resultados
    if "⚠️ Recomendación Especial" in resultado_md:
        st.warning(resultado_md)
    else:
        st.success("¡Análisis completado con éxito!")
        st.markdown(resultado_md)
    
    # Acordeón oculto para la trazabilidad técnica
    with st.expander("🔎 Ver detalle técnico de reglas del sistema"):
        st.markdown(diagnostico_md)
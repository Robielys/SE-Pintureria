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

class MedidaSeguridad(Fact):
    pass

# ==============================================================================
# 3. MOTOR DE INFERENCIA (LÓGICA INTACTA)
# ==============================================================================
class SistemaExpertoPintura(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.reglas_disparadas = []

    # --- BLOQUE 1: INCOMPATIBILIDADES FÍSICAS (FILTROS) ---
    @Rule(Superficie(sustrato=L('metal') | L('madera'), estado='eflorescencia'))
    def alerta_eflorescencia_falsa(self):
        self.reglas_disparadas.append("alerta_eflorescencia_falsa")
        self.declare(AlertaIncompatibilidad(
            motivo="Combinación de sustrato y estado físicamente imposible.",
            detalle="La eflorescencia (salitre) es una patología exclusiva de la mampostería. Los metales o maderas no sudan sales.",
            accion="Revisa los datos ingresados en el formulario."
        ))

    @Rule(Superficie(sustrato=L('madera') | L('yeso') | L('revoque_nuevo') | L('revoque_viejo') | L('ladrillo'), estado='oxido'))
    def alerta_oxido_falso(self):
        self.reglas_disparadas.append("alerta_oxido_falso")
        self.declare(AlertaIncompatibilidad(
            motivo="Patología incompatible con el material.",
            detalle="El óxido es un proceso de corrosión exclusivo de metales ferrosos.",
            accion="Verifica que el material base sea metal si detectas óxido, o corrige el estado ingresado."
        ))

    @Rule(Superficie(sustrato='revoque_nuevo', estado='eflorescencia'))
    def alerta_eflorescencia_real(self):
        self.reglas_disparadas.append("alerta_eflorescencia_real")
        self.declare(AlertaIncompatibilidad(
            motivo="Problema estructural de humedad o curado.",
            detalle="Pintar sobre una pared con salitre o humedad provocará desprendimiento inmediato.",
            accion="Soluciona la humedad de cimientos o permite el curado completo (30 días) antes de intervenir."
        ))

    # --- BLOQUE 2: DIAGNÓSTICO Y PREPARACIÓN (NIVEL 1 -> NIVEL 2) ---
    @Rule(Superficie(estado='hongos'))
    def tratamiento_hongos(self):
        self.reglas_disparadas.append("tratamiento_hongos")
        self.declare(NecesidadTratamiento(paso="Aplicar líquido fungicida o lavandina diluida (1 en 10), cepillar, lavar y dejar secar."))
        self.declare(InsumoAdicional(categoria="Preparación", item="Líquido fungicida o Lavandina"))
        self.declare(InsumoAdicional(categoria="Preparación", item="Cepillo de cerda dura"))

    @Rule(Superficie(estado='descascarada'))
    def tratamiento_descascarado(self):
        self.reglas_disparadas.append("tratamiento_descascarado")
        self.declare(NecesidadTratamiento(paso="Eliminar recubrimientos sueltos mediante rasqueteo mecánico o lijado."))
        self.declare(InsumoAdicional(categoria="Preparación", item="Espátula de acero o Lija de grano mediano (120)"))

    @Rule(Superficie(sustrato='metal', estado='oxido'))
    def tratamiento_oxido_metal(self):
        self.reglas_disparadas.append("tratamiento_oxido_metal")
        self.declare(NecesidadTratamiento(paso="Eliminar la corrosión descamable mediante cepillado mecánico o lijado. Desengrasar."))
        self.declare(InsumoAdicional(categoria="Preparación", item="Cepillo de alambre de acero"))
        self.declare(InsumoAdicional(categoria="Limpieza", item="Aguarrás mineral"))

    @Rule(Superficie(sustrato='madera', estado='virgen'))
    def tratamiento_madera_virgen(self):
        self.reglas_disparadas.append("tratamiento_madera_virgen")
        self.declare(NecesidadTratamiento(paso="Lijar en dirección a las vetas para abrir porosidad y eliminar el polvillo."))
        self.declare(InsumoAdicional(categoria="Preparación", item="Lija para madera (grano fino)"))

    # --- BLOQUE 3: SELECCIÓN DE ESQUEMAS (NIVEL 1 -> NIVEL 2) ---
    @Rule(Superficie(sustrato=L('revoque_viejo') | L('yeso'), ubicacion='interior', m2=MATCH.m2))
    def esquema_interior_mamposteria(self, m2):
        self.reglas_disparadas.append("esquema_interior_mamposteria")
        self.declare(EsquemaRecomendado(
            fondo="Fijador Sellador al agua",
            litros_fondo=math.ceil(m2 / 15),
            terminacion="Látex Acrílico Interior",
            litros_terminacion=math.ceil((m2 * 2) / 10),
            manos=2
        ))

    @Rule(Superficie(sustrato=L('revoque_viejo') | L('revoque_nuevo'), ubicacion='exterior', m2=MATCH.m2))
    def esquema_exterior_mamposteria(self, m2):
        self.reglas_disparadas.append("esquema_exterior_mamposteria")
        self.declare(EsquemaRecomendado(
            fondo="Imprimación Fijadora al Aguarrás",
            litros_fondo=math.ceil(m2 / 12),
            terminacion="Látex Impermeabilizante para Exteriores",
            litros_terminacion=math.ceil((m2 * 2) / 10),
            manos=2
        ))

    @Rule(Superficie(sustrato='metal', ubicacion='exterior', m2=MATCH.m2))
    def esquema_metal_exterior(self, m2):
        self.reglas_disparadas.append("esquema_metal_exterior")
        self.declare(EsquemaRecomendado(
            fondo="Fondo Convertidor de Óxido (Doble acción)",
            litros_fondo=math.ceil(m2 / 12),
            terminacion="Esmalte Sintético Exterior (Brillante)",
            litros_terminacion=math.ceil((m2 * 2) / 12),
            manos=2
        ))

    @Rule(Superficie(sustrato='metal', ubicacion='interior', m2=MATCH.m2))
    def esquema_metal_interior(self, m2):
        self.reglas_disparadas.append("esquema_metal_interior")
        self.declare(EsquemaRecomendado(
            fondo="Fondo Antióxido Tradicional",
            litros_fondo=math.ceil(m2 / 12),
            terminacion="Esmalte Sintético Interior (Satinado/Mate)",
            litros_terminacion=math.ceil((m2 * 2) / 12),
            manos=2
        ))

    @Rule(Superficie(sustrato='madera', ubicacion='exterior', m2=MATCH.m2))
    def esquema_madera_exterior(self, m2):
        self.reglas_disparadas.append("esquema_madera_exterior")
        self.declare(EsquemaRecomendado(
            fondo="Preservador para maderas (Fungicida/Insecticida)",
            litros_fondo=math.ceil(m2 / 10),
            terminacion="Impregnante protector formador de película micro-porosa",
            litros_terminacion=math.ceil((m2 * 2) / 12),
            manos=2
        ))

    @Rule(Superficie(sustrato='madera', ubicacion='interior', m2=MATCH.m2))
    def esquema_madera_interior(self, m2):
        self.reglas_disparadas.append("esquema_madera_interior")
        self.declare(EsquemaRecomendado(
            fondo="Sellador para madera",
            litros_fondo=math.ceil(m2 / 10),
            terminacion="Barniz Interior o Esmalte Sintético",
            litros_terminacion=math.ceil((m2 * 2) / 12),
            manos=2
        ))

    @Rule(Superficie(sustrato='ladrillo', ubicacion='exterior', m2=MATCH.m2))
    def esquema_ladrillo_exterior(self, m2):
        self.reglas_disparadas.append("esquema_ladrillo_exterior")
        self.declare(EsquemaRecomendado(
            fondo="No requiere base (Aplicación directa diluida)",
            litros_fondo=0,
            terminacion="Impermeabilizante Siliconado para Ladrillos",
            litros_terminacion=math.ceil((m2 * 2) / 10),
            manos=2
        ))

    @Rule(Superficie(sustrato='ladrillo', ubicacion='interior', m2=MATCH.m2))
    def esquema_ladrillo_interior(self, m2):
        self.reglas_disparadas.append("esquema_ladrillo_interior")
        self.declare(EsquemaRecomendado(
            fondo="No requiere base",
            litros_fondo=0,
            terminacion="Látex Acrílico Interior",
            litros_terminacion=math.ceil((m2 * 2) / 8),
            manos=2
        ))

    # --- BLOQUE 4: SELECCIÓN DE HERRAMIENTAS (NIVEL 2 -> NIVEL 3) ---
    @Rule(EsquemaRecomendado())
    def proteccion_entorno_general(self):
        self.reglas_disparadas.append("proteccion_entorno_general")
        self.declare(InsumoAdicional(categoria="Protección", item="Nylon o cartón para protección del entorno"))

    @Rule(EsquemaRecomendado(terminacion=P(lambda t: "Látex" in t)))
    def herramientas_latex(self):
        self.reglas_disparadas.append("herramientas_latex")
        self.declare(InsumoAdicional(categoria="Herramientas", item="Rodillo de lana pelo corto o Pincel ancho"))
        self.declare(InsumoAdicional(categoria="Protección", item="Cinta de enmascarar plástica"))

    @Rule(EsquemaRecomendado(terminacion=P(lambda t: "Esmalte" in t)))
    def herramientas_esmalte(self):
        self.reglas_disparadas.append("herramientas_esmalte")
        self.declare(InsumoAdicional(categoria="Herramientas", item="Pincel de cerda pura o Rodillo para sintético"))
        self.declare(InsumoAdicional(categoria="Limpieza", item="Aguarrás mineral"))

    @Rule(EsquemaRecomendado(terminacion=P(lambda t: "Impregnante" in t) | P(lambda t: "Barniz" in t)))
    def herramientas_impregnante(self):
        self.reglas_disparadas.append("herramientas_impregnante")
        self.declare(InsumoAdicional(categoria="Herramientas", item="Pincel de cerda fina o Pistola de pintar"))
        self.declare(InsumoAdicional(categoria="Limpieza", item="Aguarrás mineral"))

    @Rule(EsquemaRecomendado(terminacion=P(lambda t: "Siliconado" in t)))
    def herramientas_silicona(self):
        self.reglas_disparadas.append("herramientas_silicona")
        self.declare(InsumoAdicional(categoria="Herramientas", item="Pulverizador manual o brocha ancha"))

    # --- BLOQUE 5: CADENA CAUSAL PROFUNDA DE SEGURIDAD (NIVEL 3 -> NIVEL 4) ---
    @Rule(InsumoAdicional(item=L("Aguarrás mineral")))
    def seguridad_solventes(self):
        self.reglas_disparadas.append("seguridad_solventes")
        self.declare(MedidaSeguridad(protocolo="Ventilación Obligatoria: Los vapores orgánicos del solvente son tóxicos e inflamables. Utilizar en ambiente ventilado o con máscara de carbón activado."))

    @Rule(InsumoAdicional(item=P(lambda i: "Fungicida" in i or "Lavandina" in i)))
    def seguridad_quimicos(self):
        self.reglas_disparadas.append("seguridad_quimicos")
        self.declare(MedidaSeguridad(protocolo="Protección Ocular y Dérmica: Riesgo de quemaduras químicas. Uso obligatorio de guantes de látex/nitrilo y antiparras para salpicaduras."))

    @Rule(InsumoAdicional(item=P(lambda i: "Espátula" in i or "Cepillo de alambre" in i)))
    def seguridad_particulas(self):
        self.reglas_disparadas.append("seguridad_particulas")
        self.declare(MedidaSeguridad(protocolo="Protección Respiratoria y Ocular: El rasqueteo mecánico libera partículas. Usar barbijo para polvo (N95) y antiparras para polvo."))


# ==============================================================================
# 4. LÓGICA Y MAPEO
# ==============================================================================
OPCIONES_SUSTRATO = {
    "Pared existente / Revoque viejo": "revoque_viejo",
    "Pared nueva / Revoque fresco": "revoque_nuevo",
    "Ladrillo a la vista": "ladrillo",
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

def resolver_sistema_experto(sustrato_label, estado_label, ubicacion_label, alto, ancho):
    if alto is None or ancho is None or alto <= 0 or ancho <= 0:
        return "⚠️ **Por favor, ingresa dimensiones de alto y ancho válidas (mayores a 0).**", ""

    m2 = float(alto * ancho)

    motor = SistemaExpertoPintura()
    motor.reset()
    motor.declare(Superficie(
        sustrato=OPCIONES_SUSTRATO[sustrato_label],
        estado=OPCIONES_ESTADO[estado_label],
        ubicacion=OPCIONES_UBICACION[ubicacion_label],
        m2=float(m2)
    ))
    motor.run()

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
            lineas_alerta.append("\n⚠️ **Se recomienda solicitar la inspección de un profesional de la construcción en el lugar antes de aplicar cualquier recubrimiento.**")

        traza_alerta = "### 🔎 Detalle Técnico\n- El motor de reglas detuvo la recomendación para evitar una falla en la aplicación por humedad no tratada."
        return "\n".join(lineas_alerta), traza_alerta

    lineas = [
        "## 📋 Tu Lista de Materiales y Guía de Trabajo",
        f"*Resumen:* Superficie de **{m2:.2f} m²** | Material: **{sustrato_label}** | Ubicación: **{ubicacion_label}**",
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
        lineas.append("") 
        lineas.append(f"**[{cat}]**")
        for item in items:
            lineas.append(f"- {item}")

    lineas.append("\n### 4. ⚠️ Protocolos de Seguridad Derivados")
    seguridad = [f for f in motor.facts.values() if isinstance(f, MedidaSeguridad)]
    if seguridad:
        for s in seguridad:
            lineas.append(f"- {s['protocolo']}")
    else:
        lineas.append("- No se detectaron riesgos químicos especiales para este esquema.")

    traza = ["### 🔎 Trazabilidad del Razonamiento"]
    traza.append("**1. Reglas activadas (Cadena de Inferencia):**")
    for regla in motor.reglas_disparadas:
        traza.append(f"- Regla ejecutada: `{regla}`")

    traza.append("\n**2. Hechos deducidos (Memoria de Trabajo):**")
    for hecho in motor.facts.values():
        traza.append(f"- `{type(hecho).__name__}: {dict(hecho)}`")

    return "\n".join(lineas), "\n".join(traza)

# ==============================================================================
# 5. INTERFAZ GRÁFICA (STREAMLIT UI)
# =================================================================
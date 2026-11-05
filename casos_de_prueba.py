# Casos de pruebas
def ejecutar_caso_de_prueba(id_caso, nombre_caso, sustrato, estado, ubicacion, m2, esperados):
    print("=" * 100)
    print(f"       TEST RUNNER - CASO DE PRUEBA {id_caso}: {nombre_caso.upper()}")
    print("=" * 100)
    print(f"📥 ENTRADAS: Sustrato='{sustrato}', Estado='{estado}', Ubicación='{ubicacion}', Área={m2} m²\n")

    motor = SistemaExpertoPintura()
    motor.reset()
    motor.declare(Superficie(sustrato=sustrato, estado=estado, ubicacion=ubicacion, m2=m2))
    motor.run()

    # Recolectar hechos declarados por categoría
    alertas = [f for f in motor.facts.values() if isinstance(f, AlertaIncompatibilidad)]
    tratamientos = [f for f in motor.facts.values() if isinstance(f, NecesidadTratamiento)]
    esquemas = [f for f in motor.facts.values() if isinstance(f, EsquemaRecomendado)]
    insumos_hechos = [f for f in motor.facts.values() if isinstance(f, InsumoAdicional)]

    cumple_caso = True

    print("📊 COMPARATIVA DE SALIDAS (ESPERADAS VS. OBTENIDAS):\n")

    # 1. Alerta de Seguridad
    if esperados.get("alerta"):
        esperado_txt = "Alerta de Incompatibilidad / Sin recomendación automatizada"
        obtenido_txt = alertas[0]['motivo'] + " - " + alertas[0]['detalle'] if alertas else "No se emitió alerta"
        ok = len(alertas) > 0
        if not ok: cumple_caso = False
        print(f"• Componente: ALERTA DE SEGURIDAD")
        print(f"  - Esperado: {esperado_txt}")
        print(f"  - Obtenido: {obtenido_txt}")
        print(f"  - Estado:   {'[ CUMPLE ]' if ok else '[ NO CUMPLE ]'}\n")

    # 2. Diagnóstico / Preparación
    if esperados.get("preparacion"):
        esperado_txt = esperados["preparacion"]
        obtenido_txt = tratamientos[0]['paso'] if tratamientos else "Ninguno"
        ok = len(tratamientos) > 0
        if not ok: cumple_caso = False
        print(f"• Componente: DIAGNÓSTICO / TRATAMIENTO")
        print(f"  - Esperado: {esperado_txt}")
        print(f"  - Obtenido: {obtenido_txt}")
        print(f"  - Estado:   {'[ CUMPLE ]' if ok else '[ NO CUMPLE ]'}\n")

    # 3. Esquema Recomendado
    if esperados.get("esquema"):
        esperado_txt = esperados["esquema"]
        if esquemas:
            e = esquemas[0]
            fondo_str = f"Fondo: {e['fondo']} ({e['litros_fondo']}L) + " if e['litros_fondo'] > 0 else ""
            obtenido_txt = f"{fondo_str}Terminación: {e['terminacion']} ({e['litros_terminacion']}L, {e['manos']} manos)"
        else:
            obtenido_txt = "Ninguno"
        ok = len(esquemas) > 0 and esperados["esquema"].lower() in esquemas[0]['terminacion'].lower()
        if not ok: cumple_caso = False
        print(f"• Componente: ESQUEMA RECOMENDADO Y CANTIDADES")
        print(f"  - Esperado: {esperado_txt}")
        print(f"  - Obtenido: {obtenido_txt}")
        print(f"  - Estado:   {'[ CUMPLE ]' if ok else '[ NO CUMPLE ]'}\n")

    # 4. Herramientas e Insumos (Agrupados por categoría)
    if esperados.get("herramientas"):
        esperado_txt = esperados["herramientas"]
        # Filtrar o consolidar los insumos por sus ítems
        lista_insumos = [i['item'] for i in insumos_hechos]
        obtenido_txt = ", ".join(lista_insumos) if lista_insumos else "Ninguno"
        ok = len(insumos_hechos) > 0
        if not ok: cumple_caso = False
        print(f"• Componente: HERRAMIENTAS E INSUMOS COMPLETO")
        print(f"  - Esperado: {esperado_txt}")
        print(f"  - Obtenido: {obtenido_txt}")
        print(f"  - Estado:   {'[ CUMPLE ]' if ok else '[ NO CUMPLE ]'}\n")

    print("-" * 100)

    # VERDICTO FINAL
    if cumple_caso:
        print(f"✅ RESULTADO FINAL: CASO DE PRUEBA {id_caso} --> [ APROBADO / CUMPLE ]")
    else:
        print(f"❌ RESULTADO FINAL: CASO DE PRUEBA {id_caso} --> [ NO APROBADO / NO CUMPLE ]")

    print(f"📜 TRAZABILIDAD DE INFERENCIA: {len(motor.facts)} hechos generados en la Memoria de Trabajo RETE.")
    print("=" * 100 + "\n\n")


# ==============================================================================
# EJECUCIÓN DE LOS 4 CASOS DE PRUEBA DEL PLIEGO
# ==============================================================================

# ==============================================================================
# EJECUCIÓN DE LOS 4 CASOS DE PRUEBA DEL PLIEGO (VALORES ALINEADOS)
# ==============================================================================

if __name__ == "__main__":

    # Caso 1: Pared Interior con Hongos
    ejecutar_caso_de_prueba(
        id_caso=1,
        nombre_caso="Pared Interior con Hongos",
        sustrato="revoque_viejo",
        estado="hongos",
        ubicacion="interior",
        m2=30.0,
        esperados={
            "preparacion": "Aplicar líquido fungicida o lavandina diluida (1 en 10), cepillar, lavar y dejar secar.",
            "esquema": "Látex Acrílico Interior",
            "herramientas": "Líquido fungicida o Lavandina, Cepillo de cerda dura, Nylon o cartón para protección del entorno, Rodillo de lana pelo corto o Pincel ancho, Cinta de enmascarar plástica"
        }
    )

    # Caso 2: Metal Oxidado Exterior
    ejecutar_caso_de_prueba(
        id_caso=2,
        nombre_caso="Metal Oxidado Exterior",
        sustrato="metal",
        estado="oxido",
        ubicacion="exterior",
        m2=10.0,
        esperados={
            "preparacion": "Eliminar la corrosión descamable mediante cepillado mecánico o lijado. Desengrasar.",
            "esquema": "Esmalte Sintético Exterior",
            "herramientas": "Cepillo de alambre de acero, Aguarrás mineral, Nylon o cartón para protección del entorno, Pincel de cerda pura o Rodillo para sintético"
        }
    )


    # Caso 3: Flexibilidad de Herramientas (RF-06)
    ejecutar_caso_de_prueba(
        id_caso=4,
        nombre_caso="Flexibilidad de Herramientas (RF-06)",
        sustrato="madera",
        estado="virgen",
        ubicacion="exterior",
        m2=5.0,
        esperados={
            "preparacion": "Lijar en dirección a las vetas para abrir porosidad y eliminar el polvillo.",
            "esquema": "Impregnante protector",
            "herramientas": "Lija para madera (grano fino), Nylon o cartón para protección del entorno, Pincel de cerda fina o Pistola de pintar, Aguarrás mineral"
        }
    )

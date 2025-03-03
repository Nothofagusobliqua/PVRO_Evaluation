import etapas
import planta
import matplotlib.pyplot as plt
import red_elec
import economics as eco
import pandas as pd

from tqdm import tqdm

# from playsound import playsound
# import keyboard

# PUERTO ALDEA
name = "Puerto_Aldea"

p_inicial = 5
p_final = 150
years = 20

nombre = "Comité APR Puerto Aldea"

consumo = etapas.Consumo(consumo_diario=90, hora_i=7, hora_f=23)

bomba_1 = etapas.ACPump(26, em=0.75, ed=0.75, ep=0.75, fpa=0.95)
bomba_2 = etapas.ACPump(35, em=0.75, ed=0.75, ep=0.75, fpa=0.95)

# ro = etapas.ReverseOsmosisFixSEC(sec_ro=1.5, fpa=0.9)

ro = etapas.ReverseOsmosisAlanood(effi_ERD=0, Pf_in_plant=10, RR1=0.75,
                                  RR2=0.75, Pcoef1=0.85, effi_hhp=0.75, effi_bp=0.75)

cloracion = etapas.MeteringPump(head=1, factor=0.0005)

red = red_elec.RedElec(cargo_fijo_mensual=1324.4, cargo_servicio_publico=0.701, cargo_transporte=23.633,
                       cargo_energia=91.856, cargo_potencia=18588.4, tarifa_inyeccion=77.19)

tmy = pd.read_csv("datos_chile/clima_puerto_aldea.csv", index_col=0)

lista_analisis = [0.8, 0.9, 1.1, 1.2]
for k in range(0, len(lista_analisis)):
    porcentaje = int(lista_analisis[k] * 100)
    tasa = 6
    tacita = tasa / 100

    val_act_base_list = []
    val_act_autogen_list = []
    val_act_ntbg_list = []

    inv_base_list = []
    inv_autogen_list = []
    inv_ntbg_list = []

    capacidad_instalada = []
    for i in tqdm(range(p_inicial, p_final, 2)):
        capacidad_instalada.append(i)
        potencia = i
        PTA = planta.PlantaTratamiento(name="Puerto_Aldea", altitude=38, location=(-30.3034790642, -71.608649494),
                                       bomba_elevadora=bomba_1, reverse_osmosis=ro, bomba_almacenamiento=bomba_2,
                                       clorado=cloracion, consumo=consumo, redelec=red, fact_cap_inst_1=0,
                                       fact_cap_inst_2=0, capacidad_instalada1=potencia, capacidad_instalada2=potencia,
                                       tilt=29, azimuth=-31, tmy=tmy)

        PTA.redelec.factor_analisis_tarifas = lista_analisis[k]
        analisis = eco.Econo(planta_de_tratamiento=PTA, n_years=years, tasa=tacita, porc_aumento_demanda=0.04,
                             porc_aumento_tarifa=0.03, factor=1)

        analisis.run_all_years()

        list_year_ex_base = analisis.list_year_ex_base
        list_year_ex_auto_gen = analisis.list_year_ex_auto_gen
        list_year_ex_ntbg = analisis.list_year_ex_ntbg

        inv_base, val_act_base = analisis.calc_van_base_separado()
        inv_autogen, val_act_autogen = analisis.calc_van_autogen_separado()
        inv_ntbg, val_act_ntbg = analisis.calc_van_ntbg_separado()

        val_act_base_list.append(val_act_base)
        val_act_autogen_list.append(val_act_autogen)
        val_act_ntbg_list.append(val_act_ntbg)

        inv_base_list.append(inv_base)
        inv_autogen_list.append(inv_autogen)
        inv_ntbg_list.append(inv_ntbg)

    val_act_no_ponde_base = []
    val_act_no_ponde_autogen = []
    val_act_no_ponde_ntbg = []

    base_poderado_5_5 = []
    autogen_poderado_5_5 = []
    ntbg_poderado_5_5 = []

    base_poderado_6_4 = []
    autogen_poderado_6_4 = []
    ntbg_poderado_6_4 = []

    base_poderado_7_3 = []
    autogen_poderado_7_3 = []
    ntbg_poderado_7_3 = []

    base_poderado_8_2 = []
    autogen_poderado_8_2 = []
    ntbg_poderado_8_2 = []

    base_poderado_9_1 = []
    autogen_poderado_9_1 = []
    ntbg_poderado_9_1 = []

    for i in range(0, len(capacidad_instalada)):
        base_np = inv_base_list[i] + val_act_base_list[i]
        autogen_np = inv_autogen_list[i] + val_act_autogen_list[i]
        ntbg_np = inv_ntbg_list[i] + val_act_ntbg_list[i]

        base_55 = (inv_base_list[i] * 0.5) + (val_act_base_list[i] * 0.5)
        autogen_55 = (inv_autogen_list[i] * 0.5) + (val_act_autogen_list[i] * 0.5)
        ntbg_55 = (inv_ntbg_list[i] * 0.5) + (val_act_ntbg_list[i] * 0.5)

        base_64 = (inv_base_list[i] * 0.4) + (val_act_base_list[i] * 0.6)
        autogen_64 = (inv_autogen_list[i] * 0.4) + (val_act_autogen_list[i] * 0.6)
        ntbg_64 = (inv_ntbg_list[i] * 0.4) + (val_act_ntbg_list[i] * 0.6)

        base_73 = (inv_base_list[i] * 0.3) + (val_act_base_list[i] * 0.7)
        autogen_73 = (inv_autogen_list[i] * 0.3) + (val_act_autogen_list[i] * 0.7)
        ntbg_73 = (inv_ntbg_list[i] * 0.3) + (val_act_ntbg_list[i] * 0.7)

        base_82 = (inv_base_list[i] * 0.2) + (val_act_base_list[i] * 0.8)
        autogen_82 = (inv_autogen_list[i] * 0.2) + (val_act_autogen_list[i] * 0.8)
        ntbg_82 = (inv_ntbg_list[i] * 0.2) + (val_act_ntbg_list[i] * 0.8)

        base_91 = (inv_base_list[i] * 0.1) + (val_act_base_list[i] * 0.9)
        autogen_91 = (inv_autogen_list[i] * 0.1) + (val_act_autogen_list[i] * 0.9)
        ntbg_91 = (inv_ntbg_list[i] * 0.1) + (val_act_ntbg_list[i] * 0.9)

        val_act_no_ponde_base.append(base_np)
        val_act_no_ponde_autogen.append(autogen_np)
        val_act_no_ponde_ntbg.append(ntbg_np)

        base_poderado_5_5.append(base_55)
        autogen_poderado_5_5.append(autogen_55)
        ntbg_poderado_5_5.append(ntbg_55)

        base_poderado_6_4.append(base_64)
        autogen_poderado_6_4.append(autogen_64)
        ntbg_poderado_6_4.append(ntbg_64)

        base_poderado_7_3.append(base_73)
        autogen_poderado_7_3.append(autogen_73)
        ntbg_poderado_7_3.append(ntbg_73)

        base_poderado_8_2.append(base_82)
        autogen_poderado_8_2.append(autogen_82)
        ntbg_poderado_8_2.append(ntbg_82)

        base_poderado_9_1.append(base_91)
        autogen_poderado_9_1.append(autogen_91)
        ntbg_poderado_9_1.append(ntbg_91)

    # LOS BEST
    # optimos por caso
    best_autogen_no_poderado = 2 * (val_act_no_ponde_autogen.index(min(val_act_no_ponde_autogen))) + p_inicial
    best_ntbg_no_poderado = 2 * (val_act_no_ponde_ntbg.index(min(val_act_no_ponde_ntbg))) + p_inicial

    best_autogen_poderado_5_5 = 2 * (autogen_poderado_5_5.index(min(autogen_poderado_5_5))) + p_inicial
    best_ntbg_poderado_5_5 = 2 * (ntbg_poderado_5_5.index(min(ntbg_poderado_5_5))) + p_inicial

    best_autogen_poderado_6_4 = 2 * (autogen_poderado_6_4.index(min(autogen_poderado_6_4))) + p_inicial
    best_ntbg_poderado_6_4 = 2 * (ntbg_poderado_6_4.index(min(ntbg_poderado_6_4))) + p_inicial

    best_autogen_poderado_7_3 = 2 * (autogen_poderado_7_3.index(min(autogen_poderado_7_3))) + p_inicial
    best_ntbg_poderado_7_3 = 2 * (ntbg_poderado_7_3.index(min(ntbg_poderado_7_3))) + p_inicial

    best_autogen_poderado_8_2 = 2 * (autogen_poderado_8_2.index(min(autogen_poderado_8_2))) + p_inicial
    best_ntbg_poderado_8_2 = 2 * (ntbg_poderado_8_2.index(min(ntbg_poderado_8_2))) + p_inicial

    best_autogen_poderado_9_1 = 2 * (autogen_poderado_9_1.index(min(autogen_poderado_9_1))) + p_inicial
    best_ntbg_poderado_9_1 = 2 * (ntbg_poderado_9_1.index(min(ntbg_poderado_9_1))) + p_inicial

    lista_best = [best_autogen_poderado_5_5, best_ntbg_poderado_5_5,
                  best_autogen_poderado_6_4, best_ntbg_poderado_6_4,
                  best_autogen_poderado_7_3, best_ntbg_poderado_7_3,
                  best_autogen_poderado_8_2, best_ntbg_poderado_8_2,
                  best_autogen_poderado_9_1, best_ntbg_poderado_9_1,
                  best_autogen_no_poderado, best_ntbg_no_poderado]

    str_best = ["best_autogen_poderado_5_5", "best_ntbg_poderado_5_5",
                "best_autogen_poderado_6_4", "best_ntbg_poderado_6_4",
                "best_autogen_poderado_7_3", "best_ntbg_poderado_7_3",
                "best_autogen_poderado_8_2", "best_ntbg_poderado_8_2",
                "best_autogen_poderado_9_1", "best_ntbg_poderado_9_1",
                "best_autogen_no_poderado", "best_ntbg_no_poderado"]

    # LOS INDICES DE LOS BEST
    indice_best_autogen_poderado_5_5 = capacidad_instalada.index(best_autogen_poderado_5_5)
    indice_best_ntbg_poderado_5_5 = capacidad_instalada.index(best_ntbg_poderado_5_5)

    indice_best_autogen_poderado_6_4 = capacidad_instalada.index(best_autogen_poderado_6_4)
    indice_best_ntbg_poderado_6_4 = capacidad_instalada.index(best_ntbg_poderado_6_4)

    indice_best_autogen_poderado_7_3 = capacidad_instalada.index(best_autogen_poderado_7_3)
    indice_best_ntbg_poderado_7_3 = capacidad_instalada.index(best_ntbg_poderado_7_3)

    indice_best_autogen_poderado_8_2 = capacidad_instalada.index(best_autogen_poderado_8_2)
    indice_best_ntbg_poderado_8_2 = capacidad_instalada.index(best_ntbg_poderado_8_2)

    indice_best_autogen_poderado_9_1 = capacidad_instalada.index(best_autogen_poderado_9_1)
    indice_best_ntbg_poderado_9_1 = capacidad_instalada.index(best_ntbg_poderado_9_1)

    indice_best_autogen_no_poderado = capacidad_instalada.index(best_autogen_no_poderado)
    indice_best_ntbg_no_poderado = capacidad_instalada.index(best_ntbg_no_poderado)

    # LA INVERSION DE LOS BEST
    inv_best_autogen_poderado_5_5 = inv_autogen_list[indice_best_autogen_poderado_5_5]
    inv_best_ntbg_poderado_5_5 = inv_ntbg_list[indice_best_ntbg_poderado_5_5]

    inv_best_autogen_poderado_6_4 = inv_autogen_list[indice_best_autogen_poderado_6_4]
    inv_best_ntbg_poderado_6_4 = inv_ntbg_list[indice_best_ntbg_poderado_6_4]

    inv_best_autogen_poderado_7_3 = inv_autogen_list[indice_best_autogen_poderado_7_3]
    inv_best_ntbg_poderado_7_3 = inv_ntbg_list[indice_best_ntbg_poderado_7_3]

    inv_best_autogen_poderado_8_2 = inv_autogen_list[indice_best_autogen_poderado_8_2]
    inv_best_ntbg_poderado_8_2 = inv_ntbg_list[indice_best_ntbg_poderado_8_2]

    inv_best_autogen_poderado_9_1 = inv_autogen_list[indice_best_autogen_poderado_9_1]
    inv_best_ntbg_poderado_9_1 = inv_ntbg_list[indice_best_ntbg_poderado_9_1]

    inv_best_autogen_no_poderado = inv_autogen_list[indice_best_autogen_no_poderado]
    inv_best_ntbg_no_poderado = inv_ntbg_list[indice_best_ntbg_no_poderado]

    lista_inv_best = [inv_best_autogen_poderado_5_5, inv_best_ntbg_poderado_5_5,
                      inv_best_autogen_poderado_6_4, inv_best_ntbg_poderado_6_4,
                      inv_best_autogen_poderado_7_3, inv_best_ntbg_poderado_7_3,
                      inv_best_autogen_poderado_8_2, inv_best_ntbg_poderado_8_2,
                      inv_best_autogen_poderado_9_1, inv_best_ntbg_poderado_9_1,
                      inv_best_autogen_no_poderado, inv_best_ntbg_no_poderado]

    # VAGF DE LOS BEST
    vagf_best_autogen_poderado_5_5 = val_act_autogen_list[indice_best_autogen_poderado_5_5]
    vagf_best_ntbg_poderado_5_5 = val_act_ntbg_list[indice_best_ntbg_poderado_5_5]

    vagf_best_autogen_poderado_6_4 = val_act_autogen_list[indice_best_autogen_poderado_6_4]
    vagf_best_ntbg_poderado_6_4 = val_act_ntbg_list[indice_best_ntbg_poderado_6_4]

    vagf_best_autogen_poderado_7_3 = val_act_autogen_list[indice_best_autogen_poderado_7_3]
    vagf_best_ntbg_poderado_7_3 = val_act_ntbg_list[indice_best_ntbg_poderado_7_3]

    vagf_best_autogen_poderado_8_2 = val_act_autogen_list[indice_best_autogen_poderado_8_2]
    vagf_best_ntbg_poderado_8_2 = val_act_ntbg_list[indice_best_ntbg_poderado_8_2]

    vagf_best_autogen_poderado_9_1 = val_act_autogen_list[indice_best_autogen_poderado_9_1]
    vagf_best_ntbg_poderado_9_1 = val_act_ntbg_list[indice_best_ntbg_poderado_9_1]

    vagf_best_autogen_no_poderado = val_act_autogen_list[indice_best_autogen_no_poderado]
    vagf_best_ntbg_no_poderado = val_act_ntbg_list[indice_best_ntbg_no_poderado]

    lista_vagf_best = [vagf_best_autogen_poderado_5_5, vagf_best_ntbg_poderado_5_5,
                       vagf_best_autogen_poderado_6_4, vagf_best_ntbg_poderado_6_4,
                       vagf_best_autogen_poderado_7_3, vagf_best_ntbg_poderado_7_3,
                       vagf_best_autogen_poderado_8_2, vagf_best_ntbg_poderado_8_2,
                       vagf_best_autogen_poderado_9_1, vagf_best_ntbg_poderado_9_1,
                       vagf_best_autogen_no_poderado, vagf_best_ntbg_no_poderado]

    # VAA DE LOS BEST
    vaa_best_autogen_poderado_5_5 = vagf_best_autogen_poderado_5_5 + inv_best_autogen_poderado_5_5
    vaa_best_ntbg_poderado_5_5 = vagf_best_ntbg_poderado_5_5 + inv_best_ntbg_poderado_5_5

    vaa_best_autogen_poderado_6_4 = vagf_best_autogen_poderado_6_4 + inv_best_autogen_poderado_6_4
    vaa_best_ntbg_poderado_6_4 = vagf_best_ntbg_poderado_6_4 + inv_best_ntbg_poderado_6_4

    vaa_best_autogen_poderado_7_3 = vagf_best_autogen_poderado_7_3 + inv_best_autogen_poderado_7_3
    vaa_best_ntbg_poderado_7_3 = vagf_best_ntbg_poderado_7_3 + inv_best_ntbg_poderado_7_3

    vaa_best_autogen_poderado_8_2 = vagf_best_autogen_poderado_8_2 + inv_best_autogen_poderado_8_2
    vaa_best_ntbg_poderado_8_2 = vagf_best_ntbg_poderado_8_2 + inv_best_ntbg_poderado_8_2

    vaa_best_autogen_poderado_9_1 = vagf_best_autogen_poderado_9_1 + inv_best_autogen_poderado_9_1
    vaa_best_ntbg_poderado_9_1 = vagf_best_ntbg_poderado_9_1 + inv_best_ntbg_poderado_9_1

    vaa_best_autogen_no_poderado = vagf_best_autogen_no_poderado + inv_best_autogen_no_poderado
    vaa_best_ntbg_no_poderado = vagf_best_ntbg_no_poderado + inv_best_ntbg_no_poderado

    lista_vaa_best = [vaa_best_autogen_poderado_5_5, vaa_best_ntbg_poderado_5_5,
                      vaa_best_autogen_poderado_6_4, vaa_best_ntbg_poderado_6_4,
                      vaa_best_autogen_poderado_7_3, vaa_best_ntbg_poderado_7_3,
                      vaa_best_autogen_poderado_8_2, vaa_best_ntbg_poderado_8_2,
                      vaa_best_autogen_poderado_9_1, vaa_best_ntbg_poderado_9_1,
                      vaa_best_autogen_no_poderado, vaa_best_ntbg_no_poderado]

    data_best = {"categoria": str_best,
                 "potencia kW": lista_best,
                 "inv_best": lista_inv_best,
                 "vagf_best": lista_vagf_best,
                 "lista_vaa_best": lista_vaa_best}

    data_best_df = pd.DataFrame(data_best)
    data_best_df.to_csv(f'resultados/analisis/tarifas/planillas/{name}_optimos_tarifas_{lista_analisis[k]}.csv',
                        index=False)

    data = {'Capacidad': capacidad_instalada,
            'val_act_no_ponde_base': val_act_no_ponde_base,
            'val_act_no_ponde_autogen': val_act_no_ponde_autogen,
            'val_act_no_ponde_ntbg': val_act_no_ponde_ntbg,
            'base_poderado_5_5': base_poderado_5_5,
            'autogen_poderado_5_5': autogen_poderado_5_5,
            'ntbg_poderado_5_5': ntbg_poderado_5_5,
            'base_poderado_6_4': base_poderado_6_4,
            'autogen_poderado_6_4': autogen_poderado_6_4,
            'ntbg_poderado_6_4': ntbg_poderado_6_4,
            'base_poderado_7_3': base_poderado_7_3,
            'autogen_poderado_7_3': autogen_poderado_7_3,
            'ntbg_poderado_7_3': ntbg_poderado_7_3,
            'base_poderado_8_2': base_poderado_8_2,
            'autogen_poderado_8_2': autogen_poderado_8_2,
            'ntbg_poderado_8_2': ntbg_poderado_8_2,
            'base_poderado_9_1': base_poderado_9_1,
            'autogen_poderado_9_1': autogen_poderado_9_1,
            'ntbg_poderado_9_1': ntbg_poderado_9_1,
            'val_act_base_list': val_act_base_list,
            'val_act_autogen_list': val_act_autogen_list,
            'val_act_ntbg_list': val_act_ntbg_list,
            'inv_base_list': inv_base_list,
            'inv_autogen_list': inv_autogen_list,
            'inv_ntbg_list': inv_ntbg_list}

    df = pd.DataFrame(data)
    df.to_csv(f'resultados/analisis/tarifas/planillas/{name}_resultados_vida_util_tarifas_{lista_analisis[k]}.csv',
              index=False)

    # grafico autogeneración chico
    autogen_5_5 = [n * (1 / 1000000) for n in autogen_poderado_5_5]
    autogen_6_4 = [n * (1 / 1000000) for n in autogen_poderado_6_4]
    autogen_7_3 = [n * (1 / 1000000) for n in autogen_poderado_7_3]
    autogen_8_2 = [n * (1 / 1000000) for n in autogen_poderado_8_2]
    autogen_9_1 = [n * (1 / 1000000) for n in autogen_poderado_9_1]

    plt.figure(figsize=(7, 6))
    plt.grid(True)
    plt.plot(capacidad_instalada, autogen_5_5, label="Ponderación 50% - 50%")
    plt.plot(capacidad_instalada, autogen_6_4, label="Ponderación 60% - 40%")
    plt.plot(capacidad_instalada, autogen_7_3, label="Ponderación 70% - 30%")
    plt.plot(capacidad_instalada, autogen_8_2, label="Ponderación 80% - 20%")
    plt.plot(capacidad_instalada, autogen_9_1, label="Ponderación 90% - 10%")
    plt.xlabel("Capacidad instalada PV en kW")
    plt.ylabel("Millones de Pesos")
    plt.title(
        f"Valor actual ponderado gastos en energía\ncaso Autogeneración con tasa del {tasa}% y {porcentaje}% de tarifas\n{nombre}")
    plt.legend()
    # plt.show()
    plt.savefig(
        f"resultados/analisis/tarifas/graficos/{name}_val_act_pond_tarifas_{porcentaje}_autogen_chico")
    plt.close()

    # grafico netbilling chico
    ntbg_5_5 = [n * (1 / 1000000) for n in ntbg_poderado_5_5]
    ntbg_6_4 = [n * (1 / 1000000) for n in ntbg_poderado_6_4]
    ntbg_7_3 = [n * (1 / 1000000) for n in ntbg_poderado_7_3]
    ntbg_8_2 = [n * (1 / 1000000) for n in ntbg_poderado_8_2]
    ntbg_9_1 = [n * (1 / 1000000) for n in ntbg_poderado_9_1]

    plt.figure(figsize=(7, 6))
    plt.grid(True)
    plt.plot(capacidad_instalada, ntbg_5_5, label="Ponderación 50% - 50%")
    plt.plot(capacidad_instalada, ntbg_6_4, label="Ponderación 60% - 40%")
    plt.plot(capacidad_instalada, ntbg_7_3, label="Ponderación 70% - 30%")
    plt.plot(capacidad_instalada, ntbg_8_2, label="Ponderación 80% - 20%")
    plt.plot(capacidad_instalada, ntbg_9_1, label="Ponderación 90% - 10%")
    plt.xlabel("Capacidad instalada PV en kW")
    plt.ylabel("Millones de Pesos")
    plt.title(
        f"Valor actual ponderado gastos en energía\ncaso Net Billing con tasa de descuento del {tasa}% y {porcentaje}% de tarifas\n{nombre}")
    plt.legend()
    # plt.show()
    plt.savefig(f"resultados/analisis/tarifas/graficos/{name}_val_act_pond_tarifas_{porcentaje}_ntbg_chico")
    plt.close()

    # van normal chico
    v_a_np_b = [n * (1 / 1000000) for n in val_act_no_ponde_base]
    v_a_np_autogen = [n * (1 / 1000000) for n in val_act_no_ponde_autogen]
    v_a_np_ntbg = [n * (1 / 1000000) for n in val_act_no_ponde_ntbg]

    plt.figure(figsize=(7, 6))
    plt.grid(True)
    plt.plot(capacidad_instalada, v_a_np_b, label="Red Eléctrica")
    plt.plot(capacidad_instalada, v_a_np_autogen, label="Autogeneración")
    plt.plot(capacidad_instalada, v_a_np_ntbg, label="Net Billing")
    plt.xlabel("Capacidad instalada PV en kW")
    plt.ylabel("Millones de Pesos")
    plt.title(f"Valor actual gastos en energía\ntasa de descuento del {tasa}% y {porcentaje}% de tarifas\n{nombre}")
    plt.legend()
    # plt.show()
    plt.savefig(f"resultados/analisis/tarifas/graficos/{name}_val_act_normal_tarifas_{porcentaje}_chico")
    plt.close()

    print(f"listo {name} {porcentaje}% inversion")

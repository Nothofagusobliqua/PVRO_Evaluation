import etapas
import planta
import matplotlib.pyplot as plt
import red_elec
import economics as eco
import pandas as pd
from tqdm import tqdm
import PV_systems_clear_sky as pvrsk

# PUERTO ALDEA
nombre = "Comité APR Puerto Aldea"
consumo = etapas.Consumo(consumo_diario=90, hora_i=7, hora_f=23)
bomba_captacion = etapas.ACPump(26, em=0.75, ed=0.75, ep=0.75, fpa=0.95)
bomba_elevadora = etapas.ACPump(35, em=0.75, ed=0.75, ep=0.75, fpa=0.95)

ro = etapas.ReverseOsmosisAlanood(effi_ERD=0, Pf_in_plant=10, RR1=0.75,
                                  RR2=0.75, Pcoef1=0.85, effi_hhp=0.75, effi_bp=0.75)

cloracion = etapas.MeteringPump(head=1, factor=0.0005)

red = red_elec.RedElec(cargo_fijo_mensual=1324.4, cargo_servicio_publico=0.701, cargo_transporte=23.633,
                       cargo_energia=91.856, cargo_potencia=18588.4, tarifa_inyeccion=77.19)

'''red = red_elec.RedElec(cargo_fijo_mensual=1142.69, cargo_servicio_publico=0.709, cargo_transporte=23.633,
                       cargo_energia=90.476, cargo_potencia=17400.6, tarifa_inyeccion=77.19)  # BT2 2012 Coquimbo'''

tmy = pd.read_csv("datos_chile/clima_puerto_aldea.csv", index_col=0)

PTA = planta.PlantaTratamiento(name="Puerto_Aldea", altitude=38,
                               location=(-30.3034790642, -71.608649494),
                               bomba_elevadora=bomba_captacion, reverse_osmosis=ro,
                               bomba_almacenamiento=bomba_elevadora,
                               clorado=cloracion, consumo=consumo,
                               redelec=red, fact_cap_inst_1=0,
                               fact_cap_inst_2=0, capacidad_instalada1=17,
                               capacidad_instalada2=77,
                               tilt=29, azimuth=-31, tmy=tmy)

print(f"ejecutando {PTA.name}")
PTA.run_pta()  # calcula la energía consumida por la pta
print("run_pta")
PTA.run_pta_grid()  # calcula los gasto en electricidad caso solo con red eléctrica
print("run_pta_grid")
PTA.run_pta_pvs_grid()
print("run_pta_pvs_grid")
PTA.run_pta_pvs_ntbg()
print("run_pta_pvs_ntbg")

#capacidad_instalada2=77
meses_short2 = ["ENE", "FEB", "MAR", "ABR", "MAY",
               "JUN", "JUL", "AGO", "SEP",
               "OCT", "NOV", "DIC"]

meses_short = ["Ene", "Feb", "Mar", "Abr", "May",
               "Jun", "Jul", "Ago", "Sep",
               "Oct", "Nov", "Dic"]


year_save_autoge = PTA.cost_year_energy_pta_grid - PTA.cost_year_energy_pta_pvs_grid
year_save_ntbg = PTA.cost_year_energy_pta_grid - PTA.cost_year_energy_pta_pvs_ntbg

print("year_save_autoge ", year_save_autoge)
print("year_save_ntbg ", year_save_ntbg)

'''
df = {"meses": meses_short,
      "energia_consumida": PTA.months_energy_dtg_pta_grid,
      "energia_generada_ntbg": PTA.pta_pvs_ntbg_pv_system.months_energy_ac,
      "energia_consumida_ntbg": PTA.months_energy_dtg_pta_pvs_ntbg,
      "exdentes_ntbg": PTA.months_energy_exce}


data_df = pd.DataFrame(df)
data_df.to_csv(f'resultados/operacion_diaria_optima/{PTA.name}_testeo_ntbg.csv', index=False)
'''
# 'Desempeño anual Alternativa de Net Billing
'''plt.figure()
plt.grid(True)

plt.plot(meses_short, PTA.months_energy_dtg_pta_grid, label="Consumo PTA")
plt.scatter(meses_short, PTA.months_energy_dtg_pta_grid)


plt.plot(meses_short, PTA.months_energy_dtg_pta_pvs_ntbg, label="Consumo desde la Red")
plt.scatter(meses_short, PTA.months_energy_dtg_pta_pvs_ntbg)

plt.plot(meses_short, PTA.months_energy_exce, label="Excedentes")
plt.scatter(meses_short, PTA.months_energy_exce)

plt.plot(meses_short, PTA.pta_pvs_ntbg_pv_system.months_energy_ac, label="Generación")
plt.scatter(meses_short, PTA.pta_pvs_ntbg_pv_system.months_energy_ac)

plt.xlabel('Meses')
plt.ylabel("Energía kWh")
plt.title(f'Desempeño anual Alternativa de Net Billing\n{nombre}')
plt.legend()
#plt.savefig(f"resultados/operacion_diaria_optima/{PTA.name}_desempeno_anual_optimo_ntbg.png")
plt.show()
#plt.close()'''


#Gasto mensual en energía por solución
'''redd = [n * (1 / 1000) for n in PTA.cost_months_energy_pta_grid]
autogen = [n * (1 / 1000) for n in PTA.cost_months_energy_pta_pvs_grid]
ntbg = [n * (1 / 1000) for n in PTA.cost_months_energy_pta_pvs_ntbg]

plt.figure()
plt.grid(True)
plt.plot(meses_short, redd, label="Red eléctrica")
plt.scatter(meses_short, redd)

plt.plot(meses_short, autogen, label="Autogeneración")
plt.scatter(meses_short, autogen)

plt.plot(meses_short, ntbg, label="Net Billing")
plt.scatter(meses_short, ntbg)
plt.xlabel('Meses')
plt.ylabel("Miles de Pesos")
plt.title(f'Gasto mensual en energía por solución\n{nombre}')
plt.legend()
#plt.savefig(f"resultados/operacion_diaria_optima/{PTA.name}_gasto_mensual_optimo.png")
plt.show()
#plt.close()'''

'''redd = [n * (1 / 1000) for n in PTA.cost_months_energy_pta_grid]
autogen = [n * (1 / 1000) for n in PTA.cost_months_energy_pta_pvs_grid]
ntbg = [n * (1 / 1000) for n in PTA.cost_months_energy_pta_pvs_ntbg]
months_exce = [n * (1 / 1000) for n in PTA.months_exe_valorizados]
mont_exe_disp = [n * (1 / 1000) for n in PTA.months_exe_valorizados_disponibles]
months_monto_inyecc = [n * (1 / 1000) for n in PTA.months_monto_inyecciones]

plt.figure()
plt.grid(True)
plt.plot(meses_short, redd, label="Red eléctrica")
plt.scatter(meses_short, redd)

plt.plot(meses_short, months_exce, label="months_exce")
plt.scatter(meses_short, months_exce)

plt.plot(meses_short, ntbg, label="Net Billing")
plt.scatter(meses_short, ntbg)

plt.plot(meses_short, autogen, label="autogen")
plt.scatter(meses_short, autogen)

plt.plot(meses_short, mont_exe_disp, label="mont_exe_disp")
plt.scatter(meses_short, mont_exe_disp)

plt.plot(meses_short, months_monto_inyecc, label="months_monto_inyecc")
plt.scatter(meses_short, months_monto_inyecc)

plt.xlabel('Meses')
plt.ylabel("Miles de Pesos")
plt.title(f'Gasto mensual en energía por solución\n{nombre}')
plt.legend()
#plt.savefig(f"resultados/operacion_diaria_optima/{PTA.name}_gasto_mensual_optimo.png")
plt.show()
#plt.close()
print(months_exce)'''
'''analisis = eco.Econo(planta_de_tratamiento=PTA, n_years=20, tasa=0.06, porc_aumento_tarifa=0.03,
                     porc_aumento_demanda=0.04)

analisis.run_all_years()

list_year_ex_base = analisis.list_year_ex_base
list_year_ex_auto_gen = analisis.list_year_ex_auto_gen
list_year_ex_ntbg = analisis.list_year_ex_ntbg

list_months_ex_base = analisis.list_months_ex_base
list_months_ex_auto_gen = analisis.list_months_ex_auto_gen
list_months_ex_ntbg = analisis.list_months_ex_ntbg
lista_val_exe_not_used = analisis.lista_val_exe_not_used

list_months_ener_base = analisis.list_months_ener_base
list_months_ener_autogen =analisis. list_months_ener_autogen
list_months_ener_ntbg = analisis.list_months_ener_ntbg






# Energía consumida mensualmente
plt.figure()
plt.grid(True)

plt.plot(meses_short, list_months_ener_base[0], label="Red eléctrica")
plt.scatter(meses_short, list_months_ener_base[0])

plt.plot(meses_short, list_months_ener_autogen[0], label="Autogeneración")
plt.scatter(meses_short, list_months_ener_autogen[0])

plt.plot(meses_short, list_months_ener_ntbg[0], label="Netbilling")
plt.scatter(meses_short, list_months_ener_ntbg[0])

plt.xlabel('Meses')
plt.ylabel("Energía kWh")
plt.title(f'Energía consumida mensualmente\n{nombre}')
plt.legend()
#plt.savefig(f"resultados/operacion_diaria_optima/{PTA.name}_energia_mensual_optima.png")
plt.show()
#plt.close()


#Gasto mensual en energía por solución
redd = [n * (1 / 1000) for n in list_months_ex_base[0]]
autogen = [n * (1 / 1000) for n in list_months_ex_auto_gen[0]]
ntbg = [n * (1 / 1000) for n in list_months_ex_ntbg[0]]
#ntbg_not_used = [n * (1 / 1000) for n in lista_val_exe_not_used[0]]

plt.figure()
plt.grid(True)
plt.plot(meses_short, redd, label="Red eléctrica")
plt.scatter(meses_short, redd)

plt.plot(meses_short, autogen, label="Autogeneración")
plt.scatter(meses_short, autogen)

plt.plot(meses_short, ntbg, label="Net Billing")
plt.scatter(meses_short, ntbg)

#plt.plot(meses_short, ntbg_not_used, label="Excedentes no usados")
#plt.scatter(meses_short, ntbg_not_used)

plt.xlabel('Meses')
plt.ylabel("Miles de Pesos")
plt.title(f'Gasto mensual en energía por solución\n{nombre}')
plt.legend()
#plt.savefig(f"resultados/operacion_diaria_optima/{PTA.name}_gasto_mensual_optimo.png")
plt.show()
#plt.close()'''

'''
# Energía consumida mensualmente
plt.figure()
plt.grid(True)

plt.plot(meses_short, PTA.months_energy_dtg_pta_grid, label="Red eléctrica")
plt.scatter(meses_short, PTA.months_energy_dtg_pta_grid)

#plt.plot(meses_short, PTA.months_energy_dtg_pta_pvs_grid, label="Autogeneración")
#plt.scatter(meses_short, PTA.months_energy_dtg_pta_pvs_grid)

plt.plot(meses_short, PTA.months_energy_dtg_pta_pvs_ntbg, label="Net Billing")
plt.scatter(meses_short, PTA.months_energy_dtg_pta_pvs_ntbg)

plt.plot(meses_short, PTA.months_energy_exce, label="Excedentes Net Billing")
plt.scatter(meses_short, PTA.months_energy_exce)

plt.plot(meses_short, PTA.pta_pvs_ntbg_pv_system.months_energy_ac, label="Generación Net Billing")
plt.scatter(meses_short, PTA.pta_pvs_ntbg_pv_system.months_energy_ac)

plt.xlabel('Meses')
plt.ylabel("Energía kWh")
plt.title(f'Energía consumida mensualmente\n{nombre}')
plt.legend()
#plt.savefig(f"resultados/operacion_diaria_optima/{PTA.name}_energia_mensual_optima.png")
plt.show()
#plt.close()

'''

# Energía consumida mensualmente
plt.figure()
plt.grid(True)

plt.plot(meses_short, PTA.months_energy_dtg_pta_pvs_grid, label="Autogeneración")
plt.scatter(meses_short, PTA.months_energy_dtg_pta_pvs_grid)

plt.plot(meses_short, PTA.months_energy_dtg_pta_pvs_ntbg, label="Facturación neta")
plt.scatter(meses_short, PTA.months_energy_dtg_pta_pvs_ntbg)

plt.plot(meses_short, PTA.months_energy_dtg_pta_grid, label="Red eléctrica")
plt.scatter(meses_short, PTA.months_energy_dtg_pta_grid)

plt.xlabel('Meses')
plt.ylabel("Energía kWh")
#plt.title(f'Energía consumida mensualmente\n{nombre}')
plt.legend()
plt.savefig(f"resultados/operacion_diaria_optima/{PTA.name}_energia_mensual_optima.png")
#plt.show()
plt.close()


#Gasto mensual en energía por solución
redd = [n * (1 / 1000) for n in PTA.cost_months_energy_pta_grid]
autogen = [n * (1 / 1000) for n in PTA.cost_months_energy_pta_pvs_grid]
ntbg = [n * (1 / 1000) for n in PTA.cost_months_energy_pta_pvs_ntbg]

plt.figure()
plt.grid(True)
plt.plot(meses_short, autogen, label="Autogeneración")
plt.scatter(meses_short, autogen)

plt.plot(meses_short, ntbg, label="Facturación neta")
plt.scatter(meses_short, ntbg)

plt.plot(meses_short, redd, label="Red eléctrica")
plt.scatter(meses_short, redd)
plt.xlabel('Meses')
plt.ylabel("Miles de Pesos")
#plt.title(f'Gasto mensual en energía por solución\n{nombre}')
plt.legend()
plt.savefig(f"resultados/operacion_diaria_optima/{PTA.name}_gasto_mensual_optimo.png")
#plt.show()
plt.close()
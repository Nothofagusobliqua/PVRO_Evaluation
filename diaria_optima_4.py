import etapas
import planta
import matplotlib.pyplot as plt
import red_elec
import economics as eco
import pandas as pd
from tqdm import tqdm
import PV_systems_clear_sky as pvrsk

# HUARA
nombre = "Comité APR Tarapacá"

consumo = etapas.Consumo(consumo_diario=54, hora_i=8, hora_f=15)
bomba_1 = etapas.ACPump(6, em=0.85, ed=0.85, ep=0.85, fpa=0.95)
ro = etapas.ReverseOsmosisAlanood(effi_ERD=0.8, Pf_in_plant=9, RR1=0.8,
                                  RR2=0.8, Pcoef1=0.85, effi_hhp=0.75, effi_bp=0.75)
cloracion = etapas.MeteringPump(head=1, factor=0.0005)

red = red_elec.RedElec(cargo_fijo_mensual=1324.4, cargo_servicio_publico=0.701, cargo_transporte=21.67,
                       cargo_energia=84.154, cargo_potencia=17481.1, tarifa_inyeccion=70.718)

tmy = pd.read_csv("datos_chile/clima_huara.csv", index_col=0)
PTA = planta.PlantaTratamiento(name="Huara", altitude=1424, location=(-19.923209805, -69.5078211815),
                               bomba_elevadora=bomba_1, reverse_osmosis=ro,
                               clorado=cloracion, consumo=consumo, redelec=red,
                               capacidad_instalada1=6, capacidad_instalada2=22,
                               tilt=20, azimuth=9, tmy=tmy)

print(f"ejecutando {PTA.name}")
PTA.run_pta()  # calcula la energía consumida por la pta
print("run_pta")
PTA.run_pta_grid()  # calcula los gasto en electricidad caso solo con red eléctrica
print("run_pta_grid")
PTA.run_pta_pvs_grid()
print("run_pta_pvs_grid")
PTA.run_pta_pvs_ntbg()
print("run_pta_pvs_ntbg")

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
plt.savefig(f"resultados/operacion_diaria_optima/{PTA.name}_desempeno_anual_optimo_ntbg.png")
#plt.show()
plt.close()
'''
'''redd = [n * (1 / 1000) for n in PTA.cost_months_energy_pta_grid]
autogen = [n * (1 / 1000) for n in PTA.cost_months_energy_pta_pvs_grid]
ntbg = [n * (1 / 1000) for n in PTA.cost_months_energy_pta_pvs_ntbg]


year_red = 0
year_autogen = 0
year_ntbg = 0

for i in range(0, 12):
    year_red += redd[i]
    year_autogen += autogen[i]
    year_ntbg += ntbg[i]

print(f"year1_red {year_red}")
print(f"year_autogen {year_autogen}")
print(f"year_ntbg {year_ntbg}")'''

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
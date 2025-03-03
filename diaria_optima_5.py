import etapas
import planta
import matplotlib.pyplot as plt
import red_elec
import economics as eco
import pandas as pd
import PV_systems_clear_sky as pvrsk
from tqdm import tqdm
# Tamaya

nombre = "Comité APR Cerrillos de Tamaya"
consumo = etapas.Consumo(consumo_diario=450, hora_i=8, hora_f=23)

bomba_1 = etapas.ACPump(20, em=0.75, ed=0.75, ep=0.75, fpa=0.95)
bomba_2 = etapas.ACPump(109, em=0.75, ed=0.75, ep=0.75, fpa=0.95)


ro = etapas.ReverseOsmosisFixSEC(sec_ro=1.8, fpa=0.9)


cloracion = etapas.MeteringPump(head=1, factor=0.0005)

red = red_elec.RedElec(cargo_fijo_mensual=1324.4, cargo_servicio_publico=0.701, cargo_transporte=23.633,
                       cargo_energia=86.725, cargo_potencia=19111, tarifa_inyeccion=72.878)

'''red = red_elec.RedElec(cargo_fijo_mensual=1148.52, cargo_servicio_publico=0.709, cargo_transporte=0,
                       cargo_energia=84.954, cargo_potencia=12490.8, tarifa_inyeccion=72.878)  # AT2 2012 Ovalle'''

tmy = pd.read_csv("datos_chile/clima_tamaya.csv", index_col=0)

PTA = planta.PlantaTratamiento(name="Tamaya", altitude=288, location=(-30.5770162571, -71.4047606976),
                               bomba_elevadora=bomba_1, reverse_osmosis=ro, bomba_almacenamiento=bomba_2,
                               clorado=cloracion, consumo=consumo, redelec=red, fact_cap_inst_1=0,
                               fact_cap_inst_2=0, capacidad_instalada1=121, capacidad_instalada2=300,
                               tilt=29, azimuth=-24, tmy=tmy)

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
plt.close()'''


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
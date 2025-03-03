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

# DESEMPEÑO ANUAL ALTERNATIVAS
name = "huara"
potencias = []
ener_dtg_red = []
ener_dtg_autogen = []
ener_dtg_ntbg = []

gasto_red = []
gasto_autogen = []
gasto_ntbg = []

year_save_autogen = []
year_save_ntbg = []

for i in tqdm(range(2, 40, 2)):
    potencia = i
    potencias.append(potencia)

    PTA = planta.PlantaTratamiento(name="Huara", altitude=1424, location=(-19.923209805, -69.5078211815),
                                   bomba_elevadora=bomba_1, reverse_osmosis=ro,
                                   clorado=cloracion, consumo=consumo, redelec=red,
                                   capacidad_instalada1=potencia, capacidad_instalada2=potencia,
                                   tilt=20, azimuth=9, tmy=tmy)
    PTA.run_pta()  # calcula la energía consumida por la pta
    PTA.run_pta_grid()  # calcula los gasto en electricidad caso solo con red eléctrica
    PTA.run_pta_pvs_grid()
    PTA.run_pta_pvs_ntbg()

    ener_dtg_red.append(PTA.year_energy_dtg_pta_grid)
    ener_dtg_autogen.append(PTA.year_energy_dtg_pta_pvs_grid)
    ener_dtg_ntbg.append(PTA.year_energy_dtg_pta_pvs_ntbg)

    gasto_red.append(PTA.cost_year_energy_pta_grid)
    gasto_autogen.append(PTA.cost_year_energy_pta_pvs_grid)
    gasto_ntbg.append(PTA.cost_year_energy_pta_pvs_ntbg)

    year_save_autogen.append(PTA.cost_year_energy_pta_grid - PTA.cost_year_energy_pta_pvs_grid)
    year_save_ntbg.append(PTA.cost_year_energy_pta_grid - PTA.cost_year_energy_pta_pvs_ntbg)

# gasto anual en energía al aumenta la capacidad instlada
gasto_red_millones = [n * (1 / 1000000) for n in gasto_red]
gasto_autogen_millones = [n * (1 / 1000000) for n in gasto_autogen]
gasto_ntbg_millones = [n * (1 / 1000000) for n in gasto_ntbg]

plt.figure()
plt.grid(True)
plt.plot(potencias, gasto_autogen_millones, label="Autogeneración")
plt.plot(potencias, gasto_ntbg_millones, label="Facturación neta")
plt.plot(potencias, gasto_red_millones, label="Red eléctrica")
plt.xlabel('Capacidad instalada kW')
plt.ylabel("Millones de Pesos")
#plt.title(f'Gasto anual en energía según capacidad instalada\n{nombre}')
plt.legend()
plt.savefig(f"resultados/desempeno_anual/{name}_gasto_anual.png")
# plt.show()
plt.close()

# ahorro anual al aumenta la capacidad instlada
year_save_autogen_millones = [n * (1 / 1000000) for n in year_save_autogen]
year_save_ntbg_millones = [n * (1 / 1000000) for n in year_save_ntbg]

plt.figure()
plt.grid(True)
# plt.plot(potencias, gasto_red, label="Red eléctrica")
plt.plot(potencias, year_save_autogen_millones, label="Autogeneración")
plt.plot(potencias, year_save_ntbg_millones, label="Facturación neta")
plt.xlabel('Capacidad instalada kW')
plt.ylabel("Millones de Pesos")
#plt.title(f'Ahorro anual según capacidad instalada\n{nombre}')
plt.legend()
plt.savefig(f"resultados/desempeno_anual/{name}_ahorro_anual.png")
# plt.show()
plt.close()

print("Listo ", nombre)
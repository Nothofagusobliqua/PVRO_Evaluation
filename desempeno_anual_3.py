import etapas
import planta
import matplotlib.pyplot as plt
import red_elec
import economics as eco
import pandas as pd
from tqdm import tqdm
import PV_systems_clear_sky as pvrsk

# SAN JULIAN
nombre = "Comité APR San Julián"
# consumo diario = n arranques * 3.1 * 120 * 0.001
consumo = etapas.Consumo(consumo_diario=81, hora_i=8, hora_f=16)

bomba_1 = etapas.ACPump(50, em=0.85, ed=0.85, ep=0.85, fpa=0.95)
bomba_2 = etapas.ACPump(63, em=0.85, ed=0.85, ep=0.85, fpa=0.95)

# ro = etapas.ReverseOsmosisFixSEC(sec_ro=1.5, fpa=0.9)

ro = etapas.ReverseOsmosisAlanood(effi_ERD=0.85, Pf_in_plant=9, RR1=0.8,
                                  RR2=0.8, Pcoef1=0.85, effi_hhp=0.8, effi_bp=0.8)

# ro2 = etapas.ReverseOsmosisShaoChi(salinity=0.3, temperature=298, rejection_rate=0.99,
# water_recovery_rate=0.5, motor_effi=0.8, erd_effi=0.5)

cloracion = etapas.MeteringPump(head=1, factor=0.0005)

red = red_elec.RedElec(cargo_fijo_mensual=1324.4, cargo_servicio_publico=0.701, cargo_transporte=23.633,
                       cargo_energia=86.725, cargo_potencia=19111, tarifa_inyeccion=72.878)

'''red = red_elec.RedElec(cargo_fijo_mensual=1148.52, cargo_servicio_publico=0.709, cargo_transporte=0,
                       cargo_energia=84.954, cargo_potencia=12490.8, tarifa_inyeccion=72.878)  # AT2 2012 Ovalle'''

tmy = pd.read_csv("datos_chile/clima_san_julian.csv", index_col=0)

# DESEMPEÑO ANUAL ALTERNATIVAS
name = "san_julian"
potencias = []
ener_dtg_red = []
ener_dtg_autogen = []
ener_dtg_ntbg = []

gasto_red = []
gasto_autogen = []
gasto_ntbg = []

year_save_autogen = []
year_save_ntbg = []

for i in tqdm(range(2, 80, 2)):
    potencia = i
    potencias.append(potencia)

    PTA = planta.PlantaTratamiento(name="San_Julian", altitude=164, location=(-30.6440729017, -71.3464037089),
                                   bomba_elevadora=bomba_1, reverse_osmosis=ro, bomba_almacenamiento=bomba_2,
                                   clorado=cloracion, consumo=consumo, redelec=red, fact_cap_inst_1=0,
                                   fact_cap_inst_2=0, capacidad_instalada1=potencia, capacidad_instalada2=potencia,
                                   tilt=27, azimuth=-14, tmy=tmy)
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
plt.plot(potencias, gasto_red_millones, label="Red eléctrica")
plt.plot(potencias, gasto_autogen_millones, label="Autogeneración")
plt.plot(potencias, gasto_ntbg_millones, label="Net Billing")
plt.xlabel('Capacidad instalada kW')
plt.ylabel("Millones de Pesos")
plt.title(f'Gasto anual en energía según capacidad instalada\n{nombre}')
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
plt.plot(potencias, year_save_ntbg_millones, label="Net Billing")
plt.xlabel('Capacidad instalada kW')
plt.ylabel("Pesos")
plt.title(f'Ahorro anual según capacidad instalada\n{nombre}')
plt.legend()
plt.savefig(f"resultados/desempeno_anual/{name}_ahorro_anual.png")
# plt.show()
plt.close()

print("Listo ", nombre)
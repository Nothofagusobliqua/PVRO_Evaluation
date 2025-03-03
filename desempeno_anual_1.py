import etapas
import planta
import matplotlib.pyplot as plt
import red_elec
import economics as eco
import pandas as pd
from tqdm import tqdm
import PV_systems_clear_sky as pvrsk

# CHANAVAYITA

nombre = "Comité APR Chanavayita"


def cuenta(lista, valor):
    cuentaa = 0
    for i in range(0, len(lista)):
        if lista[i] <= valor:
            cuentaa += 1
    return cuentaa


consumo = etapas.Consumo(consumo_diario=261, hora_i=8, hora_f=17)

bomba_1 = etapas.ACPump(27, em=0.8, ed=0.8, ep=0.8, fpa=1.05)
bomba_2 = etapas.ACPump(20, em=0.8, ed=0.8, ep=0.8, fpa=1.05)

# coagula = etapas.Coagulation(t_det=30, motor_effi=0.8, G=800, dynamic_viscosity=0.00089,
# coag_dsty=1100, coag_head=1, m_pmp_effi=0.8, n_etapas=1, fpa=0.95)

# floc1 = etapas.Floculation(t_det=1000, motor_effi=0.8, G=30, n_etapas=2, fpa=0.95)
# floc2 = etapas.Floculation(t_det=1200, motor_effi=0.8, G=50, n_etapas=2, fpa=0.95)

# ro = etapas.ReverseOsmosisAlanood(effi_ERD=0, effi_hhp=0.65, effi_bp=0.65, Pf_in_plant=10)

ro = etapas.ReverseOsmosisFixSEC(sec_ro=3.6, fpa=1.05)

cloracion = etapas.MeteringPump(head=1, factor=0.0005)

red = red_elec.RedElec(cargo_fijo_mensual=1324.4, cargo_servicio_publico=0.701, cargo_transporte=21.67,
                       cargo_energia=79.162, cargo_potencia=17316.3, tarifa_inyeccion=66.523)

tmy = pd.read_csv("datos_chile/clima_chanavayita.csv", index_col=0)

# DESEMPEÑO ANUAL ALTERNATIVAS
name = "chanavayita"
potencias = []
ener_dtg_red = []
ener_dtg_autogen = []
ener_dtg_ntbg = []

gasto_red = []
gasto_autogen = []
gasto_ntbg = []

year_save_autogen = []
year_save_ntbg = []

for i in tqdm(range(5, 400, 2)):
    potencia = i
    potencias.append(potencia)

    PTA = planta.PlantaTratamiento(name="Chanavayita", altitude=28, location=(-20.7017973668, -70.1896160429),
                                   bomba_elevadora=bomba_1, reverse_osmosis=ro, bomba_almacenamiento=bomba_2,
                                   clorado=cloracion, consumo=consumo, redelec=red, fact_cap_inst_1=0,
                                   fact_cap_inst_2=0, capacidad_instalada1=potencia, capacidad_instalada2=potencia,
                                   tilt=16, azimuth=-17, tmy=tmy)
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
import etapas
import planta
import matplotlib.pyplot as plt
import red_elec
import economics as eco
import pandas as pd

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


ro = etapas.ReverseOsmosisFixSEC(sec_ro=3.6, fpa=1.05)

cloracion = etapas.MeteringPump(head=1, factor=0.0005)

red = red_elec.RedElec(cargo_fijo_mensual=1324.4, cargo_servicio_publico=0.701, cargo_transporte=21.67,
                       cargo_energia=79.162, cargo_potencia=17316.3, tarifa_inyeccion=66.523)

tmy = pd.read_csv("datos_chile/clima_chanavayita.csv", index_col=0)

PTA = planta.PlantaTratamiento(name="Chanavayita", altitude=28, location=(-20.7017973668, -70.1896160429),
                               bomba_elevadora=bomba_1, reverse_osmosis=ro, bomba_almacenamiento=bomba_2,
                               clorado=cloracion, consumo=consumo, redelec=red, fact_cap_inst_1=0,
                               fact_cap_inst_2=0, capacidad_instalada1=10, capacidad_instalada2=10,
                               tilt=16, azimuth=-17, tmy=tmy)
print(f"ejecutando {PTA.name}")
PTA.run_pta()  # calcula la energía consumida por la pta
print("run_pta")
PTA.run_pta_grid()  # calcula los gasto en electricidad caso solo con red eléctrica
print("run_pta_grid")
PTA.run_pta_pvs_grid()
print("run_pta_pvs_grid")
"""PTA.run_pta_pvs_ntbg()
print("run_pta_pvs_grid")"""
# PTA.run_pta_off_grid(dias_autonomia=2, factor=1.2)
# print("run_pta_off_grid")

meses_short = ["ENE", "FEB", "MAR", "ABR", "MAY",
               "JUN", "JUL", "AGO", "SEP",
               "OCT", "NOV", "DIC"]


t = range(0, 12)
plt.figure()
plt.grid(True)
plt.plot(meses_short, PTA.months_energy_dtg_pta_grid)
plt.scatter(meses_short, PTA.months_energy_dtg_pta_grid)
# plt.plot(t, PTA.months_energy_dtg_pta_grid, label="Red eléctrica")
# plt.plot(t, PTA.months_energy_dtg_pta_pvs_grid, label="Autogeneración")
# plt.plot(t, PTA.months_energy_dtg_pta_pvs_ntbg, label="Netbilling")
plt.xlabel('Meses')
plt.ylabel("Energía kWh")
plt.title(f'Energía consumida mensualmente\n{nombre}')
#plt.savefig(f"resultados_validacion/{PTA.name}_energia_mensual.png")
plt.show()
#plt.close()


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

# Comparación caudal de entrada versus salida
'''t = range(0, 24)
plt.figure()
plt.grid(True)
plt.plot(t, PTA.consumo.consumo_diario, label="Caudal de salida")
plt.plot(t, PTA.bomba_elevadora.consumo_con_perdidas[0:24], label="Caudal de entrada")
plt.xlabel('Horas')
plt.ylabel("m3/s")
plt.title(f'Caudales de entrada y salida de la planta de tratamiento\n{nombre}')
plt.legend()
plt.savefig(f"resultados/operacion_diaria/{PTA.name}_caudales_in_outpng")
#plt.show()
plt.close()'''


# grafica el consumo horario por etapa de la PTA
'''t = range(0, 24)
plt.figure()
plt.grid(True)
plt.plot(t, PTA.bomba_elevadora.year_power[0:24], label="Bomba elevadora")
plt.plot(t, PTA.bomba_almacenamiento.year_power[0:24], label="Bomba almacenamiento")
plt.plot(t, PTA.reverse_osmosis.year_power[0:24], label="Osmosis Inversa")
plt.plot(t, PTA.clorado.year_power[0:24], label="Cloración")
plt.plot(t, PTA.total_year_power[0:24], label="Total")
plt.xlabel('Horas')
plt.ylabel("Potencia kW")
plt.title(f'Potencia consumida por la planta de tratamiento\n{nombre}')
plt.legend()
plt.savefig(f"resultados/operacion_diaria/{PTA.name}_potencia_horaria_planta.png")
#plt.show()
plt.close()'''



meses_short = ["ENE", "FEB", "MAR", "ABR", "MAY",
               "JUN", "JUL", "AGO", "SEP",
               "OCT", "NOV", "DIC"]
# grafica el la energía demandada mensualmente a la red por la PTA
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
#plt.savefig(f"resultados/operacion_anual/{PTA.name}_energia_mensual.png")
plt.show()
#plt.close()
print("energía consumida primedio mes ", PTA.year_energy_dtg_pta_grid / 12)

# grafica el gasto mensual en energía
base = []
suma = 0
for i in range(0, 12):
    suma += PTA.cost_months_energy_pta_grid[i]
    base.append(PTA.cost_months_energy_pta_grid[i] / 1000000)

plt.figure()
plt.grid(True)
plt.plot(meses_short, base)
plt.scatter(meses_short, base)
plt.xlabel('Meses')
plt.ylabel("Millones de pesos")
plt.title(f'Gasto mensual en energía eléctrica\n{nombre}')
#plt.savefig(f"resultados/operacion_anual/{PTA.name}_boleta_luz.png")
plt.show()
#plt.close()

print("Gasto promedio mensual ", suma / 12)

'''
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

df = {"Meses": meses, "Energia consumida": PTA.months_energy_dtg_pta_grid, "Gasto mensual": PTA.cost_months_energy_pta_grid}

planillas = pd.DataFrame(df)
planillas.to_csv(f"resultados/operacion_anual/tabla_ener_gasto_{PTA.name}.csv", index=False)
'''


# DESEMPEÑO ANUAL ALTERNATIVAS
'''name = "chanavayita"
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
'''

# gasto anual en energía al aumenta la capacidad instlada
'''gasto_red_millones = [n * (1 / 1000000) for n in gasto_red]
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
plt.savefig(f"last_game/{name}_gasto_anual.png")
#plt.show()
plt.close()'''

# ahorro anual al aumenta la capacidad instlada
'''year_save_autogen_millones = [n * (1 / 1000000) for n in year_save_autogen]
year_save_ntbg_millones = [n * (1 / 1000000) for n in year_save_ntbg]

plt.figure()
plt.grid(True)
#plt.plot(potencias, gasto_red, label="Red eléctrica")
plt.plot(potencias, year_save_autogen_millones, label="Autogeneración")
plt.plot(potencias, year_save_ntbg_millones, label="Net Billing")
plt.xlabel('Capacidad instalada kW')
plt.ylabel("Pesos")
plt.title(f'Ahorro anual según capacidad instalada\n{nombre}')
plt.legend()
plt.savefig(f"last_game/{name}_ahorro_anual.png")
#plt.show()
plt.close()'''

# Energía demandada a la red al aumentar la capacidad instlaada
'''
plt.figure()
plt.grid(True)
plt.plot(potencias, ener_dtg_red, label="Red eléctrica")
plt.plot(potencias, ener_dtg_autogen, label="Autogeneración")
plt.plot(potencias, ener_dtg_ntbg, label="Net Billing")
plt.xlabel('Capacidad instalada kW')
plt.ylabel("Energía kWh")
plt.title(f'Energía demandada a la red según capacidad instalada\n{nombre}')
plt.legend()
#plt.savefig(f"resultados_validacion/{PTA.name}_energia_mensual.png")
plt.show()
#plt.close()'''

# Irradiancias típicas clear sky
'''pv = pvrsk.SolarSystem(latitude=PTA.latitude, longitude=PTA.longitude, altitude=PTA.altitude,
                       name=PTA.name, surface_tilt=PTA.tilt, surface_azimuth=PTA.azimuth)
pv.run()

datos_pvrsk = pv.modelchain.results.effective_irradiance
prom_verano1, prom_otono1, prom_invierno1, prom_primavera1 = etapas.promedios_estaciones(datos_pvrsk)

t = range(0, 24)
plt.figure()
plt.grid(True)
plt.plot(t, prom_verano1, label="Verano")
plt.plot(t, prom_otono1, label="Otoño")
plt.plot(t, prom_invierno1, label="Invierno")
plt.plot(t, prom_primavera1, label="Primavera")
plt.xlabel('Horas')
plt.ylabel("W/m2")
plt.title(f'Promedios estacionales irradiancia efectiva modelo "Clear Sky"\n{nombre}')
plt.legend()
plt.savefig(f"resultados_validacion/{PTA.name}_irradiancia_clear_sky.png")
#plt.show()
plt.close()'''

# Irradiancias típicas TMY
'''datos_irrad = PTA.pta_pvs_grid_pv_system.modelchain.results.effective_irradiance
prom_verano2, prom_otono2, prom_invierno2, prom_primavera2 = etapas.promedios_estaciones(datos_irrad)

promedio_irrad_anual = etapas.promedios([prom_verano2, prom_otono2,
                                         prom_primavera2, prom_primavera2])

t = range(0, 24)
plt.figure()
plt.grid(True)
plt.plot(t, prom_verano2, label="Verano")
plt.plot(t, prom_otono2, label="Otoño")
plt.plot(t, prom_invierno2, label="Invierno")
plt.plot(t, prom_primavera2, label="Primavera")
plt.plot(t, promedio_irrad_anual, label="Promedio anual")
plt.xlabel('Horas')
plt.ylabel("W/m2")
plt.title(f'Promedios estacionales irradiancia efectiva modelo  "TMY"\n{nombre}')
plt.legend()
plt.savefig(f"resultados/operacion_diaria/{PTA.name}_irradiancia_realista.png")
#plt.show()
plt.close()'''


# Comparación caudal de entrada versus salida
'''t = range(0, 24)
plt.figure()
plt.grid(True)
plt.plot(t, PTA.consumo.consumo_diario, label="Caudal de salida")
plt.plot(t, PTA.bomba_elevadora.consumo_con_perdidas[0:24], label="Caudal de entrada")
plt.xlabel('Horas')
plt.ylabel("m3/s")
plt.title(f'Caudales de entrada y salida de la planta de tratamiento\n{nombre}')
plt.legend()
plt.savefig(f"resultados_validacion/{PTA.name}_caudales_in_outpng")
#plt.show()
plt.close()


# grafica el consumo horario por etapa de la PTA
t = range(0, 24)
plt.figure()
plt.grid(True)
plt.plot(t, PTA.bomba_elevadora.year_power[0:24], label="Bomba elevadora")
plt.plot(t, PTA.bomba_almacenamiento.year_power[0:24], label="Bomba almacenamiento")
plt.plot(t, PTA.reverse_osmosis.year_power[0:24], label="Osmosis Inversa")
plt.plot(t, PTA.clorado.year_power[0:24], label="Cloración")
plt.plot(t, PTA.total_year_power[0:24], label="Total")
plt.xlabel('Horas')
plt.ylabel("Potencia kW")
plt.title(f'Potencia consumida por la planta de tratamiento\n{nombre}')
plt.legend()
plt.savefig(f"resultados_validacion/{PTA.name}_potencia_horaria.png")
#plt.show()
plt.close()

# Comparación horas de radiación y curva de producción
max_power = max(PTA.total_year_power)
max_irrad = max(prom_verano2)

power_norm = []
irrad_norm = []
for i in range(0, 8760):
    power_norm.append(PTA.total_year_power[i]/max_power)

for k in range(24):
    irrad_norm.append(prom_verano2[k]/max_irrad)

tttt = range(0, 24)
plt.figure()
plt.grid(True)
plt.plot(tttt, power_norm[0:24], label="Potencia normalizada")
plt.plot(tttt, irrad_norm, label="Irradiancia normalizada")
plt.xlabel('Horas')
plt.ylabel("p.u.")
plt.title(f'Comparación horas de radiación y curva de producción de agua\n{nombre}')
plt.legend()
plt.savefig(f"resultados_validacion/{PTA.name}_normalizados.png")
#plt.show()
plt.close()


# grafica el la energía demandada mensualmente a la red por la PTA

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
plt.savefig(f"resultados_validacion/{PTA.name}_energia_mensual.png")
#plt.show()
plt.close()

'''


'''t = range(0, 12)
plt.figure()
plt.grid(True)
plt.plot(meses_short, PTA.months_energy_dtg_pta_grid, label="Red eléctrica")
plt.scatter(meses_short, PTA.months_energy_dtg_pta_grid)

plt.plot(meses_short, PTA.months_energy_dtg_pta_pvs_grid, label="Autogeneración")
plt.scatter(meses_short, PTA.months_energy_dtg_pta_pvs_grid)

plt.plot(meses_short, PTA.months_energy_dtg_pta_pvs_ntbg, label="Net Billing")
plt.scatter(meses_short, PTA.months_energy_dtg_pta_pvs_ntbg)
plt.xlabel('Meses')
plt.ylabel("Energía kWh")
plt.title(f'Energía demandada mensualmente a la red por solución\n{nombre}')
plt.legend()
# plt.savefig(f"resultados_validacion/{PTA.name}_energia_mensual.png")
plt.show()
# plt.close()

redd = [n * (1 / 1000) for n in PTA.cost_months_energy_pta_grid]
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
# plt.savefig(f"resultados_validacion/{PTA.name}_energia_mensual.png")
plt.show()
# plt.close()'''

print("listo ", PTA.name)
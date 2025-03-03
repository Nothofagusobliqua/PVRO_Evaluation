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
                               capacidad_instalada1=5, capacidad_instalada2=30,
                               tilt=20, azimuth=9, tmy=tmy)

print(f"ejecutando {PTA.name}")
PTA.run_pta()  # calcula la energía consumida por la pta
print("run_pta")
PTA.run_pta_grid()  # calcula los gasto en electricidad caso solo con red eléctrica
print("run_pta_grid")
PTA.run_pta_pvs_grid()
print("run_pta_pvs_grid")
'''PTA.run_pta_pvs_ntbg()
print("run_pta_pvs_ntbg")'''

print(PTA.days_energy[0:10])

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
#plt.plot(t, PTA.bomba_almacenamiento.year_power[0:24], label="Bomba almacenamiento")
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


# grafica el la energía demandada mensualmente a la red por la PTA
'''
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
plt.savefig(f"resultados/operacion_anual/{PTA.name}_energia_mensual.png")
#plt.show()
plt.close()
print("energía consumida primedio mes ", PTA.year_energy_dtg_pta_grid / 12)'''

# grafica el gasto mensual en energía
'''base = []
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
plt.savefig(f"resultados/operacion_anual/{PTA.name}_boleta_luz.png")
#plt.show()
plt.close()'''

'''print("Gasto promedio mensual ", suma / 12)

meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

df = {"Meses": meses, "Energia consumida": PTA.months_energy_dtg_pta_grid, "Gasto mensual": PTA.cost_months_energy_pta_grid}

planillas = pd.DataFrame(df)
planillas.to_csv(f"resultados/operacion_anual/tabla_ener_gasto_{PTA.name}.csv", index=False)
'''


# DESEMPEÑO ANUAL ALTERNATIVAS
'''name = "huara"
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
    year_save_ntbg.append(PTA.cost_year_energy_pta_grid - PTA.cost_year_energy_pta_pvs_ntbg)'''


#gasto anual en energía al aumenta la capacidad instlada
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

#ahorro anual al aumenta la capacidad instlada
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

# Irradiancias típicas clear sky
'''
pv = pvrsk.SolarSystem(latitude=PTA.latitude, longitude=PTA.longitude, altitude=PTA.altitude,
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

# Irradiancias días típicos
'''t = range(0, 24)
plt.figure()
plt.grid(True)
plt.plot(t, datos_irrad[360:384], label="Enero")
plt.plot(t, datos_irrad[2400:2424], label="Abril")
plt.plot(t, datos_irrad[4560:4584], label="Julio")
plt.plot(t, datos_irrad[6840:6864], label="Octubre")
plt.xlabel('Horas')
plt.ylabel("W/m2")
plt.title(f'Días típicos irradiancia efectiva modelo "TMY"\n{nombre}')
plt.legend()
plt.savefig(f"resultados_validacion/{PTA.name}_irradiancia_realista_dias_tipicos.png")
#plt.show()
plt.close()'''


# Comparación horas de radiación y curva de producción
'''max_power = max(PTA.total_year_power)
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
#plt.savefig(f"resultados_validacion/{PTA.name}_energia_mensual.png")
plt.show()
#plt.close()


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
#plt.savefig(f"resultados_validacion/{PTA.name}_energia_mensual.png")
plt.show()
#plt.close()

coma_autogen = eco.coma_pv(PTA.pta_pvs_grid_pv_system)
coma_ntbg = eco.coma_pv(PTA.pta_pvs_ntbg_pv_system)

print("coma autoge ", coma_autogen)
print("coma_ntbg ", coma_ntbg)

year_save_autogen = PTA.cost_year_energy_pta_grid - PTA.cost_year_energy_pta_pvs_grid
year_save_ntbg = PTA.cost_year_energy_pta_grid - PTA.cost_year_energy_pta_pvs_ntbg

print("year_save_autogen  ", year_save_autogen)
print("year_save_ntbg ", year_save_ntbg)'''

'''lista_consumo_mes = PTA.months_energy
lista_gasto_mes = PTA.cost_months_energy_pta_grid

promedio_consumo_mes = etapas.promedio_lista(lista_consumo_mes)
promedio_gasto_mes = etapas.promedio_lista(lista_gasto_mes)

print("promedio_consumo_mes ", promedio_consumo_mes)
print("promedio_gasto_mes ", promedio_gasto_mes)'''

print("listo ", PTA.name)
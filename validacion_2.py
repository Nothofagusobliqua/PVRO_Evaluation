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
bomba_captacion = etapas.ACPump(26, em=0.75, ed=0.75, ep=0.75, fpa=0.99)
bomba_elevadora = etapas.ACPump(35, em=0.75, ed=0.75, ep=0.75, fpa=0.99)

ro = etapas.ReverseOsmosisFixSEC(sec_ro=2, fpa=1)

cloracion = etapas.MeteringPump(head=1, factor=0.0005)

red = red_elec.RedElec(cargo_fijo_mensual=1324.4, cargo_servicio_publico=0.701, cargo_transporte=23.633,
                       cargo_energia=91.856, cargo_potencia=18588.4, tarifa_inyeccion=77.19)

'''red = red_elec.RedElec(cargo_fijo_mensual=1142.69, cargo_servicio_publico=0.709, cargo_transporte=23.633,
                       cargo_energia=90.476, cargo_potencia=17400.6, tarifa_inyeccion=77.19)  # BT2 2012 Coquimbo'''

tmy = pd.read_csv("datos_chile/clima_puerto_aldea.csv", index_col=0)

PTA = planta.PlantaTratamiento(name="Puerto_Aldea", altitude=38, location=(-30.3034790642, -71.608649494),
                               bomba_elevadora=bomba_captacion, reverse_osmosis=ro,
                               bomba_almacenamiento=bomba_elevadora,
                               clorado=cloracion, consumo=consumo, redelec=red, fact_cap_inst_1=0,
                               fact_cap_inst_2=0, capacidad_instalada1=40, capacidad_instalada2=40,
                               tilt=29, azimuth=-31, tmy=tmy)

# print(f"ejecutando {PTA.name}")
PTA.run_pta()  # calcula la energía consumida por la pta
print("run_pta")
PTA.run_pta_grid()  # calcula los gasto en electricidad caso solo con red eléctrica
print("run_pta_grid")
PTA.run_pta_pvs_grid()
print("run_pta_pvs_grid")
PTA.run_pta_pvs_ntbg()
print("run_pta_pvs_grid")
# print(PTA.bomba_elevadora.year_energy)

a = PTA.year_energy_dtg_pta_grid  # energía que compré
b = PTA.months_energy_dtg_pta_grid  # energía que compré
j = PTA.pta_pvs_grid_pv_system.year_energy_ac
jj = PTA.pta_pvs_grid_pv_system.months_energy_ac
jjj = PTA.pta_pvs_grid_pv_system.year_power_ac
c = PTA.cost_year_energy_pta_grid
d = PTA.cost_months_energy_pta_grid

e = PTA.year_energy_dtg_pta_pvs_grid
f = PTA.months_energy_dtg_pta_pvs_grid

g = PTA.cost_year_energy_pta_pvs_grid
h = PTA.cost_months_energy_pta_pvs_grid


i = PTA.year_energy_dtg_pta_pvs_ntbg
k = PTA.months_energy_dtg_pta_pvs_ntbg

n = PTA.cost_year_energy_pta_pvs_ntbg
m = PTA.cost_months_energy_pta_pvs_ntbg

print("consumos energía planta only grid")
print(a)
print(b)
print("------------------------")

print("gastos only grid")
print(c/1000000)
print(d)
print("------------------------")

print(f"generacion energúa solar P= {PTA.pta_pvs_grid_pv_system.potencia}")
print(j)
print(jj)

print("------------------------")

print("energía caso autogeneración")
print(e)
print(f)

print("------------------------")

print("gastos caso autogen")
print(g/1000000)
print(h)

print("--------------------")
print("energía caso ntbg")
print(i)
print(k)
print("--------------------")
print("gastos caso ntbg")
print(n/1000000)
print(m)

meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

plt.figure(figsize=(8, 7))
plt.plot(meses, PTA.months_exe_valorizados, label="months_exe_valorizados")
plt.scatter(meses, PTA.months_exe_valorizados)
plt.plot(meses, PTA.months_exe_valorizados_disponibles, label="months_exe_valorizados_disponibles")
plt.scatter(meses, PTA.months_exe_valorizados_disponibles)
plt.grid(True)
plt.legend()
plt.xlabel("Meses")
plt.ylabel("Pesos chilenos")


plt.show()


'''flow = range(0, 8760)
bomba_captacion.run(flow)
print(bomba_captacion.year_energy)'''

# DESEMPEÑO ANUAL ALTERNATIVAS
'''name = "puerto_aldea"
potencias = []
ener_dtg_red = []
ener_dtg_autogen = []
ener_dtg_ntbg = []

gasto_red = []
gasto_autogen = []
gasto_ntbg = []

year_save_autogen = []
year_save_ntbg = []

for i in tqdm(range(5, 100, 2)):
    potencia = i
    potencias.append(potencia)

    PTA = planta.PlantaTratamiento(name="Puerto_Aldea", altitude=38, location=(-30.3034790642, -71.608649494),
                                   bomba_elevadora=bomba_captacion, reverse_osmosis=ro,
                                   bomba_almacenamiento=bomba_elevadora,
                                   clorado=cloracion, consumo=consumo, redelec=red, fact_cap_inst_1=0,
                                   fact_cap_inst_2=0, capacidad_instalada1=potencia, capacidad_instalada2=potencia,
                                   tilt=29, azimuth=-31, tmy=tmy)
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
plt.savefig(f"last_game/{name}_gasto_anual.png")
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
plt.savefig(f"last_game/{name}_ahorro_anual.png")
# plt.show()
plt.close()'''

# ANALISIS OPTIMOS -> INVERSION, VAN
'''analisis = eco.Econo(planta_de_tratamiento=PTA, n_years=20, tasa=0.06, porc_aumento_demanda=0.04,
                     porc_aumento_tarifa=0.03)

analisis.run_all_years()


I0_base, val_base = analisis.calc_van_base_separado()
I0_autogen, val_autogen = analisis.calc_van_autogen_separado()
I0_ntbg, val_ntbg = analisis.calc_van_ntbg_separado()
I0_off_grid, val_off_grid = analisis.calc_van_offgrid_separado()

print("I0_base ", I0_base)
print("I0_autogen ", I0_autogen)
print("I0_ntbg ", I0_ntbg)
print("I0_off_grid ", I0_off_grid)

print("val_base ", val_base)
print("val_autogen ", val_autogen)
print("val_ntbg ", val_ntbg)
print("val_off_grid ", val_off_grid)

print("coma_autoge ", round(eco.coma_pv(PTA.pta_pvs_grid_pv_system)))
print("coma_ntbg ",  round(eco.coma_pv(PTA.pta_pvs_ntbg_pv_system)))
print("coma_bat ",  round(eco.coma_pv(PTA.off_grid_pv_system) + eco.coma_bat_2(PTA.banco.capacidad)))

print("inv bat ", eco.inversion_baterias_2(PTA.banco.capacidad))'''

'''inversion_bat = eco.inversion_baterias_2(capacidad=PTA.banco.capacidad)
inversion_pv_bat = eco.inversion_pv(PTA.off_grid_pv_system)
print("capacidad ", PTA.banco.capacidad)
print(f"inversion_bat: {round(inversion_bat)}")
print(f"inversion_pv_bat: {round(inversion_pv_bat)}")'''

'''
inversion_bat = eco.inversion_baterias_2(capacidad=PTA.c_bat)
inversion_pv_bat = eco.inversion_pv(PTA.off_grid_pv_system)
print(f"inversion_bat: {round(inversion_bat)}")
print(f"inversion_pv_bat: {round(inversion_pv_bat)}")


print("base", I0_base, val_base)
print("autogen", I0_autogen, val_autogen)
print("ntbg", I0_ntbg, val_ntbg)
print("off_grid", I0_off_grid, val_off_grid)'''

'''print(f"ejecutando {PTA.name}")
PTA.run_pta()  # calcula la energía consumida por la pta
print("run_pta")
PTA.run_pta_grid()  # calcula los gasto en electricidad caso solo con red eléctrica
print("run_pta_grid")
PTA.run_pta_pvs_grid()
print("run_pta_pvs_grid")
PTA.run_pta_pvs_ntbg()
print("run_pta_pvs_ntbg")
PTA.desing_off_grid_system(dias_autonomia=1, factor_crecimiento=1.2)
PTA.run_pta_off_grid_2()
print("run_pta_off_grid_2")'''

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

'''meses_short = ["ENE", "FEB", "MAR", "ABR", "MAY",
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
plt.savefig(f"resultados/operacion_anual/{PTA.name}_energia_mensual.png")
#plt.show()
plt.close()
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
plt.savefig(f"resultados/operacion_anual/{PTA.name}_boleta_luz.png")
#plt.show()
plt.close()

print("Gasto promedio mensual ", suma / 12)

meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

df = {"Meses": meses, "Energia consumida": PTA.months_energy_dtg_pta_grid, "Gasto mensual": PTA.cost_months_energy_pta_grid}

planillas = pd.DataFrame(df)
planillas.to_csv(f"resultados/operacion_anual/tabla_ener_gasto_{PTA.name}.csv", index=False)'''

'''meses_short = ["ENE", "FEB", "MAR", "ABR", "MAY",
               "JUN", "JUL", "AGO", "SEP",
               "OCT", "NOV", "DIC"]

t = range(0, 12)
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
#plt.close()'''

'''
coma_autogen = eco.coma_pv(PTA.pta_pvs_grid_pv_system)
coma_ntbg = eco.coma_pv(PTA.pta_pvs_ntbg_pv_system)

print("coma autoge ", coma_autogen)
print("coma_ntbg ", coma_ntbg)

year_save_autogen = PTA.cost_year_energy_pta_grid - PTA.cost_year_energy_pta_pvs_grid
year_save_ntbg = PTA.cost_year_energy_pta_grid - PTA.cost_year_energy_pta_pvs_ntbg

print("year_save_autogen  ", year_save_autogen)
print("year_save_ntbg ", year_save_ntbg)'''

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
plt.close()'''

'''lista_consumo_mes = PTA.months_energy
lista_gasto_mes = PTA.cost_months_energy_pta_grid

promedio_consumo_mes = etapas.promedio_lista(lista_consumo_mes)
promedio_gasto_mes = etapas.promedio_lista(lista_gasto_mes)

print("promedio_consumo_mes ", promedio_consumo_mes)
print("promedio_gasto_mes ", promedio_gasto_mes)'''

print("listo ", PTA.name)

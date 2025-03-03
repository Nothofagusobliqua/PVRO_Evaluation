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
PTA.desing_off_grid_system()
PTA.run_pta_off_grid_2()
print("run_pta_off_grid_2")
print(" ")
analisis = eco.Econo(planta_de_tratamiento=PTA, n_years=20, tasa=0.06, porc_aumento_demanda=0.04,
                     porc_aumento_tarifa=0.03)

analisis.run_all_years()

I0_off_grid, vagf_off_grid = analisis.calc_van_offgrid_separado()
VAA_off_grid = I0_off_grid + vagf_off_grid

capacidad_banco = PTA.banco.capacidad
potencia_banco = PTA.banco.potencia
inversion_bat = eco.inversion_baterias_2(capacidad=capacidad_banco, potencia=potencia_banco)
inversion_pv_bat = eco.inversion_pv(PTA.off_grid_pv_system)

coma_bat = eco.coma_bat_2(PTA.banco)
coma_pv = eco.coma_pv(PTA.off_grid_pv_system)
coma_off_grid = coma_bat + coma_pv


print("dias_autonomia", 2)

print("capacidad_banco", round(capacidad_banco))
print("potencia_banco", round(potencia_banco))
print("capacidad_PV", round(PTA.off_grid_pv_system.potencia))

print(f"inversion_bat", round(inversion_bat))
print("inversion_pv_bat", round(inversion_pv_bat))
print("I0_off_grid", I0_off_grid)

print("coma_bat", round(coma_bat))
print("coma_pv", round(coma_pv))
print("coma_off_grid", round(coma_off_grid))


print("vagf_off_grid", vagf_off_grid)
print("VAA_off_grid", VAA_off_grid)
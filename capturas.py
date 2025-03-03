from etapas import Consumo
from etapas import ACPump
from etapas import ReverseOsmosisAlanood
import planta_copia as planta
import matplotlib.pyplot as plt
import red_elec
import economics as eco
import pandas as pd
from economics import Econo
from tqdm import tqdm
from PV_systems_realista import SolarSystem
from red_elec import RedElec

# CAPTURA PVSYSTEM

clima_csv = pd.read_csv("clima_puerto_aldea.csv", index_col=0)

arreglo_pv = SolarSystem(tmy=clima_csv, latitude=-30.303479,
                         longitude=-71.60864, altitude=38,
                         name="Puerto_Aldea",
                         surface_tilt=29, surface_azimuth=31,
                         modules_per_string=5, strings_per_inverter=5,
                         tz="America/Santiago")

arreglo_pv.run()  # ejecuta los cálculos

potenia_horaria = arreglo_pv.year_power_ac  # lista tamaño 8760
energia_mensual = arreglo_pv.months_energy_ac  # lista tamaño 12
energia_anual = arreglo_pv.year_energy_ac  # valor numérico

# CAPTURA REDELE

red = RedElec(cargo_fijo_mensual=1324.4, cargo_servicio_publico=0.701,
              cargo_transporte=23.633, cargo_energia=91.856,
              cargo_potencia=18588.4, tarifa_inyeccion=77.19)

gasto_mensual = red.elec_ex(months_energy=energia_mensual)  # calcula el gasto mensual

# Consumo de 90 m3 entre las 07:00 y 23:00
consumo = Consumo(consumo_diario=90, hora_i=7, hora_f=23)

# Pozo de 26 m y bomba de 75% de eficiencia
bomba_captacion = ACPump(head=26, em=0.75)

# estanque elevado de 35 m y bomba de 75% de eficiencia
bomba_elevadora = ACPump(head=35, em=0.75)

# Osmosis inversa sin ERD
osmosis_inversa = ReverseOsmosisAlanood(effi_ERD=0, Pf_in_plant=10,
                                        RR1=0.75, RR2=0.75, Pcoef1=0.85,
                                        effi_hhp=0.75, effi_bp=0.75)

# CAPTURA PLANTA
PTA = planta.PlantaTratamiento(name="Puerto_Aldea", altitude=38,
                               location=(-30.3034790642, -71.608649494),
                               bomba_captacion=ACPump(head=26, em=0.75),
                               bomba_almacenamiento=ACPump(head=35, em=0.75),
                               archivo_meteorologico=clima_csv,
                               reverse_osmosis=ReverseOsmosisAlanood(effi_ERD=0, Pf_in_plant=10,
                                                                     Pcoef1=0.85,
                                                                     effi_hhp=0.75, effi_bp=0.75),
                               consumo=Consumo(consumo_diario=90, hora_i=7, hora_f=23),
                               inclinacion=29, azimuth=-31,
                               capacidad_instalada_pv=10,
                               redelec=RedElec(cargo_fijo_mensual=1324.4, cargo_servicio_publico=0.701,
                                               cargo_transporte=23.633, cargo_energia=91.856,
                                               cargo_potencia=18588.4, tarifa_inyeccion=77.19))

PTA.run_pta()  # calcula la energía consumida por la pta
PTA.run_pta_grid()  # ejecuta análisis caso solo con red eléctrica
PTA.run_pta_pvs_grid()  # ejecuta análisis caso Autogeneración
PTA.run_pta_pvs_ntbg()  # ejecuta análisis caso Net Billing

# Define el objeto
evaluacion = Econo(planta_de_tratamiento=PTA, n_years=20, tasa=0.06,
                   porc_aumento_demanda=0.04, porc_aumento_tarifa=0.03)

# Ejecuta la evaluación económoca en el periodo dado
evaluacion.run_all_years()

# Calcula la inversión y el valor actual de la alternativa de Red Eléctrica
inv_redelec, val_act_base = evaluacion.calc_van_base_separado()

# Calcula la inversión y el valor actual de la alternativa de Autogeneración
inv_autogen, val_act_autogen = evaluacion.calc_van_autogen_separado()

# Calcula la inversión y el valor actual de la alternativa de Net Billing
inv_ntbg, val_act_ntbg = evaluacion.calc_van_ntbg_separado()

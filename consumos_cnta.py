import etapas
import planta as pta



def agua_anual_corregida(n_years, lista_consumos_anuales):
    suma = 0
    for i in range(0, n_years):
        a = lista_consumos_anuales[i] / ((1 + tasa) ** (i + 1))
        suma += a
    return suma


n_years = 20
tasa = 0.06

# PUERTO ALDEA
consumo_puerto_aldea = etapas.Consumo(consumo_diario=90, hora_i=7, hora_f=23)
consumo_puerto_aldea.proyeccion_lineal_consumos_2(n_years=n_years, porcentaje_anual=0.03)

lista_consumos_anuales_puerto_aldea = consumo_puerto_aldea.consumo_vida_util_lista(n_years=n_years)


A_vu_c_puerto_aldea = agua_anual_corregida(n_years, lista_consumos_anuales_puerto_aldea)
print("A_vu_corregida_puerto_aldea ", A_vu_c_puerto_aldea)

A_vu_puerto_aldea = sum(lista_consumos_anuales_puerto_aldea)
print("A_vu_puerto_aldea ", A_vu_puerto_aldea)


# HUARA
consumo_huara = etapas.Consumo(consumo_diario=54, hora_i=8, hora_f=15)
consumo_huara.proyeccion_lineal_consumos_2(n_years=n_years, porcentaje_anual=0.04)

lista_consumos_anuales_huara = consumo_huara.consumo_vida_util_lista(n_years=n_years)

A_vu_c_huara = agua_anual_corregida(n_years, lista_consumos_anuales_huara)
print("A_vu_corregida_huara ", A_vu_c_huara)

A_vu_huara = sum(lista_consumos_anuales_huara)
print("A_vu_huara ", A_vu_huara)

# TAMAYA
consumo_tamaya = etapas.Consumo(consumo_diario=450, hora_i=8, hora_f=23)
consumo_tamaya.proyeccion_lineal_consumos_2(n_years=n_years, porcentaje_anual=0.04)

lista_consumos_anuales_tamaya = consumo_tamaya.consumo_vida_util_lista(n_years=n_years)

A_vu_c_tamaya = agua_anual_corregida(n_years, lista_consumos_anuales_tamaya)
print("A_vu_corregida_tamaya ", A_vu_c_tamaya)

A_vu_tamaya = sum(lista_consumos_anuales_tamaya)
print("A_vu_tamaya ", A_vu_tamaya)

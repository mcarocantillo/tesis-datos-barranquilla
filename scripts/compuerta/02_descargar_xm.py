"""Descarga la demanda horaria regulada del mercado de Air-e desde la API pública de XM (servapibi.xm.com.co).

Series (horas en hora local de Colombia; Hour01 = 00:00-01:00, se guarda como hora 0):
  * DemaCome por MercadoComercializacion: 'CARIBE SOL' (Air-e: Atlántico, Magdalena y La Guajira, desde oct-2020)
    y 'COSTA CARIBE' (Electricaribe, siete departamentos, hasta 2020), mercados regulado y no regulado.
    La demanda comercial incluye las pérdidas asignadas al mercado.
  * DemaRealReg, PerdidasEnerReg y DemaComeReg por agente comercializador: Air-e (CSSC; CSIC desde la
    intervención de sep-2024) y Electricaribe (EDCC hasta nov-2016; EDIC, intervenida, hasta 2020).
    Sirven para 2015-2019, cuando el mercado 'CARIBE SOL' no existía.
  * Demanda no atendida programada y no programada por subárea (diaria): Atlántico y GCM (Guajira-Cesar-Magdalena).

Las respuestas se guardan por bloques de 31 días en datos/crudos/xm; si un bloque ya existe no se vuelve a pedir.
Uso:  python 02_descargar_xm.py [mercados] [agentes] [dna]   (sin argumentos: todo)
"""
import json
import sys
import time

import pandas as pd
import requests

from comun import CRUDOS, INICIO, PROC

URL = "https://servapibi.xm.com.co/{tipo}"
DIR = CRUDOS / "xm"
DIR.mkdir(parents=True, exist_ok=True)
FIN = (pd.Timestamp.today().normalize() - pd.Timedelta(days=5)).strftime("%Y-%m-%d")

AGENTES = ["EDCC", "EDIC", "CSSC", "CSIC"]
MERCADOS = ["CARIBE SOL", "COSTA CARIBE"]
SUBAREAS = ["SUBAREA ATLANTICO", "SUBAREA GCM"]


def pedir(tipo, metrica, entidad, ini, fin, filtro):
    archivo = DIR / f"{metrica}_{entidad}_{ini}.json"
    if archivo.exists():
        return json.loads(archivo.read_text(encoding="utf-8"))
    cuerpo = {"MetricId": metrica, "StartDate": ini, "EndDate": fin, "Entity": entidad, "Filter": filtro}
    for intento in range(5):
        try:
            r = requests.post(URL.format(tipo=tipo), json=cuerpo, timeout=180)
            r.raise_for_status()
            datos = r.json()
            # el bloque del mes en curso puede estar incompleto: no se guarda en caché
            if pd.Timestamp(fin) < pd.Timestamp(FIN):
                archivo.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
            return datos
        except Exception as e:  # noqa: BLE001
            print(f"  reintento {intento + 1} {metrica} {ini}: {e}")
            time.sleep(5 * (intento + 1))
    raise RuntimeError(f"No se pudo descargar {metrica} {entidad} {ini}")


def bloques(ini, fin, dias=31):
    a = pd.Timestamp(ini)
    while a <= pd.Timestamp(fin):
        b = min(a + pd.Timedelta(days=dias - 1), pd.Timestamp(fin))
        yield a.strftime("%Y-%m-%d"), b.strftime("%Y-%m-%d")
        a = b + pd.Timedelta(days=1)


def horarias(metrica, entidad, ini, filtro, conservar):
    filas = []
    for a, b in bloques(ini, FIN):
        d = pedir("hourly", metrica, entidad, a, b, filtro)
        for item in d.get("Items") or []:
            for e in item["HourlyEntities"]:
                v = e["Values"]
                if v["code"] not in conservar:
                    continue
                for h in range(1, 25):
                    x = v.get(f"Hour{h:02d}")
                    filas.append({"fecha": item["Date"], "hora": h - 1, "codigo": v["code"],
                                  "tipo_mercado": v.get("MarketType", ""),
                                  "kwh": float(x) if x not in (None, "") else float("nan")})
        print(f"  {metrica}/{entidad} {a}: {len(filas)} filas acumuladas", flush=True)
    df = pd.DataFrame(filas)
    df["metrica"] = metrica
    return df


def diarias(metrica, entidad, ini, conservar):
    filas = []
    for a, b in bloques(ini, FIN):
        d = pedir("daily", metrica, entidad, a, b, [])
        for item in d.get("Items") or []:
            for e in item["DailyEntities"]:
                if e.get("Name") in conservar:
                    filas.append({"fecha": item["Date"], "subarea": e["Name"], "metrica": metrica,
                                  "kwh": float(e["Value"])})
    return pd.DataFrame(filas)


def main(partes_pedidas):
    if "mercados" in partes_pedidas:
        print("Mercados de comercialización (DemaCome)")
        mc = horarias("DemaCome", "MercadoComercializacion", "2017-01-01", [], set(MERCADOS))
        mc.to_parquet(PROC / "xm_mercados_horario.parquet", index=False)

    if "agentes" in partes_pedidas:
        partes = []
        for m in ["DemaRealReg", "PerdidasEnerReg", "DemaComeReg"]:
            print(f"Agentes ({m})")
            partes.append(horarias(m, "Agente", INICIO, AGENTES, set(AGENTES)))
        pd.concat(partes).to_parquet(PROC / "xm_agentes_horario.parquet", index=False)

    if "dna" in partes_pedidas:
        partes = []
        for m in ["DemaNoAtenProg", "DemaNoAtenNoProg"]:
            print(f"Demanda no atendida ({m})")
            partes.append(diarias(m, "Subarea", INICIO, set(SUBAREAS)))
        pd.concat(partes).to_parquet(PROC / "xm_dna_diaria.parquet", index=False)
    print("Listo.")


if __name__ == "__main__":
    main(set(sys.argv[1:]) or {"mercados", "agentes", "dna"})

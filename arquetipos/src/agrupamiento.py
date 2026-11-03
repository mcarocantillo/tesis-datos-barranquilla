"""Agrupamiento del Paso 2 según la versión 2 del preregistro (Sección 7).

Cada estrato del algoritmo (la posición en el diseño plano; posición × bloque en el anidado) se agrupa por separado
con K-Means, k-prototypes y jerárquico con distancia de Gower, sobre una submuestra de una vivienda por edificio.
"""
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from kmodes.kprototypes import KPrototypes
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from sklearn.cluster import DBSCAN, KMeans

from .comun import DECISION, EPOCAS, SEMILLA

A = DECISION["agrupamiento_v2"]
NUM = ["log_area", "log_plantas", "log_piso"]
ORD = ["epoca_ord"]
NOM = ["tipo_bin", "ph"]
ALGORITMOS = ["kmeans", "kprototypes", "jerarquico"]


def preparar(v):
    """Variables de agrupamiento de todas las viviendas (Sección 7.3)."""
    x = pd.DataFrame(index=v.index)
    x["log_area"] = np.log(v["area_construida"])
    for col, nombre in [("total_plantas", "log_plantas"), ("planta_ubicacion", "log_piso")]:
        s = v[col].fillna(v.groupby("posicion", observed=True)[col].transform("median"))
        x[nombre] = np.log(s.clip(lower=1))
    x["epoca_ord"] = v["epoca"].map({e: i for i, e in enumerate(EPOCAS)}).astype(int)
    x["tipo_bin"] = (v["tipo"] == "multifamiliar").astype(int)
    x["ph"] = v["condicion_predio"].astype(str).str.startswith("PH").astype(int)
    return x


def submuestra(v, rng):
    """Una vivienda al azar por edificio dentro de cada posición, estratificada por tipo × bloque (Sección 7.2)."""
    s = A["submuestra"]
    elegidas = []
    for pos, n_pos in s["tamano"].items():
        una = v[v["posicion"] == pos].sample(frac=1, random_state=rng).drop_duplicates("edificio_id")
        e = una.groupby(["tipo", "bloque"]).size()
        cuota = np.minimum(e, np.maximum(np.round(n_pos * e / e.sum()), s["minimo_por_estrato"])).astype(int)
        for (t, b), n in cuota.items():
            elegidas.append(una[(una["tipo"] == t) & (una["bloque"] == b)].sample(n=n, random_state=rng).index)
    return np.concatenate(elegidas)


def gower(a, b, variables, rango):
    """Distancia de Gower entre las filas de a y de b (pesos iguales; numéricas y época por rango)."""
    d = np.zeros((len(a), len(b)), dtype=np.float32)
    for c in variables:
        x, y = a[c].to_numpy(np.float32), b[c].to_numpy(np.float32)
        if c in NOM:
            d += x[:, None] != y[None, :]
        else:
            d += np.minimum(np.abs(x[:, None] - y[None, :]) / rango[c], 1.0)
    return d / len(variables)


class Estrato:
    """Submuestra de un estrato del algoritmo con sus variables, escalas y distancia de Gower."""

    def __init__(self, nombre, x_muestra):
        self.nombre = nombre
        moda = x_muestra.apply(lambda s: s.value_counts(normalize=True).iloc[0])
        self.vars = [c for c in NUM + ORD + NOM if moda[c] < A["descartar_si_moda_cubre"]]
        self.num = [c for c in self.vars if c in NUM]
        self.cat = [c for c in self.vars if c not in NUM]
        self.x = x_muestra
        self.mu = x_muestra[self.vars].mean()
        self.sd = x_muestra[self.vars].std(ddof=0)
        self.rango = (x_muestra[self.vars].max() - x_muestra[self.vars].min()).replace(0, 1)
        self.D = gower(x_muestra, x_muestra, self.vars, self.rango)

    def z(self, x, cols):
        return ((x[cols] - self.mu[cols]) / self.sd[cols]).to_numpy(float)


def atipicos(est):
    """DBSCAN sobre Gower con min_samples = 2 × variables y ε en el codo de la curva de k-distancias (7.4)."""
    ms = 2 * len(est.vars)
    kd = np.sort(np.sort(est.D, axis=1)[:, ms - 1])
    x = np.linspace(0, 1, len(kd))
    y = (kd - kd[0]) / max(kd[-1] - kd[0], 1e-12)
    codo = int(np.argmax(x - y))  # punto más alejado (por debajo) de la recta entre los extremos
    eps = float(kd[codo])
    ruido = DBSCAN(eps=eps, min_samples=ms, metric="precomputed").fit(est.D).labels_ == -1
    return ruido, eps, ms


class Modelo:
    """Un agrupamiento ajustado: etiquetas de los puntos de ajuste y regla para asignar cualquier vivienda."""

    def __init__(self, alg, est, k, pos_ajuste):
        self.alg, self.est, self.k = alg, est, k
        xf = est.x.iloc[pos_ajuste]
        if k == 1:
            self.etiquetas = np.zeros(len(pos_ajuste), int)
            return
        if alg == "kprototypes" and not est.cat:
            alg = self.alg = "kmeans"  # sin variables categóricas, k-prototypes es K-Means
        if alg == "kmeans":
            self.m = KMeans(k, init="k-means++", n_init=A["kmeans"]["n_init"], random_state=SEMILLA).fit(est.z(xf, est.vars))
            self.etiquetas = self.m.labels_
        elif alg == "kprototypes":
            self.m = KPrototypes(n_clusters=k, init="Cao", n_init=A["kprototypes"]["n_init"], random_state=SEMILLA,
                                 n_jobs=1)
            self.etiquetas = self.m.fit_predict(self._matriz_kp(xf), categorical=self._cat_idx())
        else:
            sub = est.D[np.ix_(pos_ajuste, pos_ajuste)]
            z = linkage(squareform(sub, checks=False), method="average")
            self.etiquetas = fcluster(z, k, criterion="maxclust") - 1
            medoides = []
            for g in np.unique(self.etiquetas):
                miembros = np.flatnonzero(self.etiquetas == g)
                medoides.append(miembros[np.argmin(sub[np.ix_(miembros, miembros)].sum(1))])
            self.medoides = xf.iloc[medoides]

    def _cat_idx(self):
        return list(range(len(self.est.num), len(self.est.num) + len(self.est.cat)))

    def _matriz_kp(self, x):
        return np.column_stack([self.est.z(x, self.est.num), x[self.est.cat].to_numpy(float)])

    def asignar(self, x):
        """Grupo de cada fila de x (todas las viviendas del estrato), Sección 7.5."""
        if self.k == 1:
            return np.zeros(len(x), int)
        if self.alg == "kmeans":
            return self.m.predict(self.est.z(x, self.est.vars))
        if self.alg == "kprototypes":
            c = self.m.cluster_centroids_
            nn, m = len(self.est.num), self._matriz_kp(x)
            num = ((m[:, None, :nn] - c[None, :, :nn].astype(float)) ** 2).sum(-1)
            cat = (m[:, None, nn:] != c[None, :, nn:].astype(float)).sum(-1)
            return np.argmin(num + self.m.gamma * cat, axis=1)
        out = np.empty(len(x), int)
        for i in range(0, len(x), 50_000):
            out[i:i + 50_000] = np.argmin(gower(x.iloc[i:i + 50_000], self.medoides, self.est.vars, self.est.rango), 1)
        return out


def suma_cuadrados(y, grupos):
    y = np.asarray(y, float)
    medias = pd.Series(y).groupby(grupos).transform("mean").to_numpy()
    return float(((y - medias) ** 2).sum())


def frontera(ssw, sst):
    """Para cada K total, la combinación de k por estrato con mayor R² de la ciudad (Nota 3).

    ssw[e][k-1] es la suma de cuadrados dentro de los grupos del estrato e con k grupos. Como las sumas de los estratos
    se suman, la mejor combinación se obtiene exacta por programación dinámica. Devuelve (K, R², {estrato: k}) para K
    desde el número de estratos hasta la suma de los máximos.
    """
    mejor = {0: (0.0, {})}
    for e, s in ssw.items():
        nuevo = {}
        for K, (c, asig) in mejor.items():
            for k, sk in enumerate(s, 1):
                if K + k not in nuevo or c + sk < nuevo[K + k][0]:
                    nuevo[K + k] = (c + sk, {**asig, e: k})
        mejor = nuevo
    return [(K, 1 - c / sst, asig) for K, (c, asig) in sorted(mejor.items())]


def elegir_k(front, umbral):
    """Posición en la frontera del menor K a partir del cual todas las ganancias son menores que el umbral."""
    grandes = np.flatnonzero(np.diff([f[1] for f in front]) >= umbral)
    return 0 if len(grandes) == 0 else int(grandes[-1]) + 1


def jaccard(alg, est, k, pos_ajuste, etiquetas, b_total, frac):
    """Jaccard medio de cada grupo en b_total submuestras del 80 % sin reemplazo (Sección 7.7)."""
    k_real = int(etiquetas.max()) + 1  # el jerárquico puede dejar menos grupos que k
    if k_real == 1:
        return np.ones(1)

    def una(b):
        rng = np.random.default_rng(SEMILLA + b)
        sel = np.sort(rng.choice(len(pos_ajuste), size=int(round(frac * len(pos_ajuste))), replace=False))
        nuevas = Modelo(alg, est, k, pos_ajuste[sel]).etiquetas
        orig = etiquetas[sel]
        out = np.full(k_real, np.nan)
        for g in range(k_real):
            a = orig == g
            if a.any():
                out[g] = max((a & (nuevas == h)).sum() / (a | (nuevas == h)).sum() for h in np.unique(nuevas))
        return out

    res = Parallel(n_jobs=-1)(delayed(una)(b) for b in range(b_total))
    return np.nanmean(np.vstack(res), axis=0)

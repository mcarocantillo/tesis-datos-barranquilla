"""Figuras didácticas del capítulo «Marco teórico» (30_marco_teorico.md).

Todas las figuras son ilustrativas: usan fórmulas de los textos citados en el capítulo y datos sintéticos
generados con la semilla 42. No leen ninguna base de la tesis, de modo que el script corre sin datos internos.
Escribe las figuras en figuras/marco/ e imprime las cifras que cita el texto.

Uso:  python scripts/marco_teorico.py
"""
import sys
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import cdist

sys.path.insert(0, str(Path(__file__).resolve().parent / "eda"))
from estilo import PAL, REPO, TXT, TXT2, fmt, plt  # noqa: E402

FIG = REPO / "figuras" / "marco"
RNG = np.random.default_rng(42)
AZUL, NAR, VERDE, AMAR, ROSA, VERDE2, MORADO, ROJO = PAL
GRIS = "#9a9993"


def guardar(fig, nombre, nota="Figura ilustrativa con datos sintéticos (semilla 42)."):
    FIG.mkdir(parents=True, exist_ok=True)
    if nota:
        fig.text(0.012, 0.012, nota, fontsize=8.5, color=TXT2)
    fig.tight_layout(rect=(0, 0.035 if nota else 0, 1, 1))
    fig.savefig(FIG / nombre, dpi=160)
    plt.close(fig)
    print("  ->", nombre)


def caja(ax, x, y, w, h, texto, color, fs=10):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=color, ec="none", alpha=.16, zorder=1))
    ax.add_patch(plt.Rectangle((x, y), w, h, fc="none", ec=color, lw=1.6, zorder=2))
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=fs, color=TXT, zorder=3)


def flecha(ax, x0, y0, x1, y1, color=GRIS, texto=None, **kw):
    ax.annotate("", (x1, y1), (x0, y0), arrowprops=dict(arrowstyle="-|>", color=color, lw=1.4,
                                                        shrinkA=2, shrinkB=2, **kw))
    if texto:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2 + .12, texto, ha="center", fontsize=8.5, color=TXT2)


# ---------------------------------------------------------------------------------------------------------
# 1. Mapa de la tesis
# ---------------------------------------------------------------------------------------------------------
def fig_cadena():
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.2)
    ax.axis("off")
    ax.grid(False)
    fila = [(0.2, "Clima horario\nT, HR, radiación\n(termodinámica)", AMAR),
            (2.35, "Vivienda\nbalance de calor\n(red RC 5R1C)", NAR),
            (4.5, "Equipo\nA/C, ventilador,\nnevera (COP)", ROJO),
            (6.65, "Hogar\npersonas, horarios,\nconsigna (azar)", MORADO),
            (8.8, "Estrato y ciudad\nsuma de miles de\nhogares (Monte Carlo)", AZUL)]
    for x, t, c in fila:
        caja(ax, x, 2.9, 1.95, 1.35, t, c)
    for (x0, _, _), (x1, _, _) in zip(fila[:-1], fila[1:]):
        flecha(ax, x0 + 1.95, 3.575, x1, 3.575)
    caja(ax, 2.35, 0.55, 1.95, 1.2, "Arquetipos\nagrupamiento\n(aprendizaje automático)", VERDE)
    flecha(ax, 3.325, 1.75, 3.325, 2.9)
    caja(ax, 6.65, 0.55, 1.95, 1.2, "Encuestas (ECV, ENUT)\ndistribuciones previas\n(estadística)", VERDE2)
    flecha(ax, 7.625, 1.75, 7.625, 2.9)
    caja(ax, 8.8, 0.55, 1.95, 1.2, "Datos agregados\nSUI y XM\n(calibración bayesiana)", GRIS)
    flecha(ax, 9.775, 1.75, 9.775, 2.9, texto=None)
    ax.annotate("", (9.6, 1.75), (9.6, 2.9), arrowprops=dict(arrowstyle="-|>", color=GRIS, lw=1.4,
                                                              linestyle="--"))
    ax.text(10.85, 2.3, "comparar\ny ajustar", fontsize=8.5, color=TXT2, ha="right", va="center")
    ax.text(0.2, 4.75, "De la física de una habitación al perfil horario de un estrato", fontsize=13,
            fontweight="bold", color=TXT)
    ax.text(0.2, 4.45, "Cada caja usa una de las herramientas teóricas de este capítulo", fontsize=10, color=TXT2)
    guardar(fig, "mt_cadena.png", nota=None)


# ---------------------------------------------------------------------------------------------------------
# 2. Agregación: un hogar frente a muchos
# ---------------------------------------------------------------------------------------------------------
def perfiles_ac(n, rng):
    """Encendido del A/C de n hogares: entra en un rango de 20 a 24 h y sale de 4 a 7 h (minuto a minuto)."""
    minutos = np.arange(24 * 60)
    ini = rng.normal(22 * 60, 70, n)
    fin = rng.normal(5.5 * 60, 50, n) + 24 * 60
    pot = rng.uniform(0.9, 1.5, n)                    # kW eléctricos
    t = minutos[None, :]
    t2 = t + 24 * 60
    on = ((t >= ini[:, None]) & (t <= fin[:, None])) | ((t2 >= ini[:, None]) & (t2 <= fin[:, None]))
    # ciclos del compresor: apagado 30 % del tiempo en tramos de 10 minutos
    ciclo = rng.random((n, 24 * 6)) > 0.3
    on &= np.repeat(ciclo, 10, axis=1)
    return minutos / 60, on * pot[:, None]


def fig_agregacion():
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.8), sharey=False)
    for ax, n in zip(axs, [1, 30, 5000]):
        h, P = perfiles_ac(n, RNG)
        media = P.mean(axis=0)
        if n > 1:
            for i in range(min(n, 4)):
                ax.plot(h, P[i], color=GRIS, lw=.5, alpha=.5)
        ax.plot(h, media, color=AZUL, lw=1.6)
        ax.set_xlim(0, 24)
        ax.set_xticks(range(0, 25, 6))
        ax.set_xlabel("hora del día")
        pico = media.max()
        fc = pico / P.max(axis=1).mean()
        ax.set_title(f"{n:,} hogar{'es' if n > 1 else ''}".replace(",", "."), fontsize=12)
        ax.text(.5, .97, f"pico medio {fmt(pico, 2)} kW · factor de coincidencia {fmt(fc, 2)}",
                transform=ax.transAxes, fontsize=9, color=TXT2, va="top", ha="center",
                bbox=dict(fc="white", ec="none", alpha=.85))
        ax.set_ylim(0, 1.75)
    axs[0].set_ylabel("potencia media por hogar (kW)")
    fig.suptitle("Al sumar hogares, los encendidos individuales se vuelven un perfil suave",
                 x=.01, ha="left", fontweight="bold", fontsize=13)
    guardar(fig, "mt_agregacion.png")


# ---------------------------------------------------------------------------------------------------------
# 3. Temperatura sol-aire
# ---------------------------------------------------------------------------------------------------------
def dia_tipico():
    h = np.arange(0, 24, .25)
    T = 28.5 + 3.3 * np.cos(2 * np.pi * (h - 14.5) / 24)          # °C, máximo a las 14:30
    I = np.clip(950 * np.sin(np.pi * (h - 6) / 12.3), 0, None)   # W/m², horizontal
    return h, T, I


def fig_sol_aire():
    h, T, I = dia_tipico()
    ho, onda = 17.0, 3.9
    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    for alfa, nombre, c in [(0.9, "techo oscuro (α = 0,9)", ROJO), (0.6, "techo gris (α = 0,6)", NAR),
                            (0.25, "techo blanco (α = 0,25)", AZUL)]:
        ax.plot(h, T + alfa * I / ho - onda, color=c, lw=1.8, label=nombre)
    ax.plot(h, T, color=TXT, lw=1.8, ls="--", label="aire exterior")
    ax.set_xlim(0, 24)
    ax.set_xticks(range(0, 25, 3))
    ax.set_xlabel("hora del día")
    ax.set_ylabel("temperatura (°C)")
    ax.legend(loc="upper left", fontsize=9.5)
    ax2 = ax.twinx()
    ax2.fill_between(h, I, color=AMAR, alpha=.15, lw=0)
    ax2.set_ylabel("irradiancia horizontal (W/m²)", color=TXT2)
    ax2.set_ylim(0, 2600)
    ax2.grid(False)
    ax2.spines["right"].set_visible(True)
    ax.set_zorder(ax2.get_zorder() + 1)
    ax.patch.set_visible(False)
    ax.set_title("Temperatura sol-aire de una cubierta horizontal en un día despejado", fontweight="bold")
    guardar(fig, "mt_sol_aire.png", nota="Ilustrativa: h_o = 17 W/m²K y corrección de onda larga de 3,9 K "
                                         "(valores de diseño de ASHRAE). El área amarilla es la irradiancia.")
    i = np.argmax(I)
    print(f"  sol-aire al mediodía: aire {T[i]:.1f}, oscuro {T[i] + .9 * I[i] / ho - onda:.1f}, "
          f"blanco {T[i] + .25 * I[i] / ho - onda:.1f}")


# ---------------------------------------------------------------------------------------------------------
# 4. Inercia térmica (1R1C con exterior senoidal)
# ---------------------------------------------------------------------------------------------------------
def fig_inercia():
    dt = 1 / 60
    t = np.arange(0, 24 * 5, dt)
    Te = 28.5 + 3.3 * np.cos(2 * np.pi * (t - 14.5) / 24)
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw=dict(width_ratios=[1.5, 1]))
    ax = axs[0]
    ax.plot(t[-24 * 60 * 2:] - t[-24 * 60 * 2], Te[-24 * 60 * 2:], color=TXT, ls="--", lw=1.6,
            label="exterior")
    for tau, c in [(1, AMAR), (6, NAR), (24, ROJO)]:
        Ti = np.empty_like(t)
        Ti[0] = 28.5
        for k in range(1, len(t)):   # Euler explícito de C dTi/dt = (Te - Ti)/R  ->  dTi/dt = (Te - Ti)/tau
            Ti[k] = Ti[k - 1] + dt * (Te[k - 1] - Ti[k - 1]) / tau
        ax.plot(t[-24 * 60 * 2:] - t[-24 * 60 * 2], Ti[-24 * 60 * 2:], color=c, lw=1.8,
                label=f"interior, τ = RC = {tau} h")
    ax.set_xlim(0, 48)
    ax.set_xticks(range(0, 49, 6))
    ax.set_xlabel("hora (dos días)")
    ax.set_ylabel("temperatura (°C)")
    ax.legend(fontsize=9, ncol=2, loc="lower left")
    ax.set_title("Respuesta de un nodo con capacidad", fontweight="bold")
    ax = axs[1]
    taus = np.linspace(0, 30, 300)
    w = 2 * np.pi / 24
    ax.plot(taus, 1 / np.sqrt(1 + (w * taus) ** 2), color=AZUL, lw=1.8, label="amplitud interior / exterior")
    ax.set_xlabel("constante de tiempo τ (h)")
    ax.set_ylabel("razón de amplitudes", color=AZUL)
    ax.set_ylim(0, 1.05)
    ax2 = ax.twinx()
    ax2.plot(taus, np.arctan(w * taus) / w, color=NAR, lw=1.8)
    ax2.set_ylabel("retraso del máximo (h)", color=NAR)
    ax2.set_ylim(0, 6.3)
    ax2.grid(False)
    ax2.spines["right"].set_visible(True)
    ax.set_title("Amortiguamiento y retraso", fontweight="bold")
    guardar(fig, "mt_inercia.png", nota="Ilustrativa: exterior senoidal de 28,5 ± 3,3 °C sin sol ni "
                                        "ganancias internas; solución analítica en el panel derecho.")


# ---------------------------------------------------------------------------------------------------------
# 5. Esquema de la red 5R1C
# ---------------------------------------------------------------------------------------------------------
def resistencia(ax, x0, y0, x1, y1, etiqueta, lado=1):
    n = 7
    xs = np.linspace(x0, x1, 2 * n + 1)
    ys = np.linspace(y0, y1, 2 * n + 1)
    vx, vy = x1 - x0, y1 - y0
    L = np.hypot(vx, vy)
    nx, ny = -vy / L, vx / L
    zig = np.array([0] + [(.09 if i % 2 else -.09) for i in range(1, 2 * n)] + [0])
    m = np.zeros_like(xs, dtype=bool)
    m[2:-2] = True
    zx = np.where(m, xs + nx * zig, xs)
    zy = np.where(m, ys + ny * zig, ys)
    ax.plot(zx, zy, color=TXT, lw=1.3)
    ax.text((x0 + x1) / 2 + nx * .28 * lado, (y0 + y1) / 2 + ny * .28 * lado, etiqueta, ha="center",
            va="center", fontsize=10, color=TXT)


def nodo(ax, x, y, etiqueta, color, dx=0, dy=.32):
    ax.plot(x, y, "o", ms=11, color=color, zorder=5)
    ax.text(x + dx, y + dy, etiqueta, ha="center", va="center", fontsize=10.5, color=TXT, fontweight="bold")


def fig_5r1c():
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    ax.set_xlim(-.4, 9.2)
    ax.set_ylim(-.9, 5.2)
    ax.axis("off")
    ax.grid(False)
    Aire, Sup, Masa = (6.5, 4.0), (6.5, 2.2), (6.5, 0.3)
    Sum, Ext1, Ext2 = (1.0, 4.0), (1.0, 2.2), (1.0, 0.3)
    resistencia(ax, *Sum, *Aire, "$H_{ve}$  ventilación e infiltración")
    resistencia(ax, *Ext1, *Sup, "$H_{tr,w}$  ventanas")
    resistencia(ax, *Ext2, 4.2, 0.3, "$H_{tr,em}$  muros y techo (exterior)", lado=-1)
    ax.plot([4.2, Masa[0]], [0.3, 0.3], color=TXT, lw=1.3)
    resistencia(ax, *Aire, *Sup, "$H_{tr,is}$", lado=-1)
    resistencia(ax, *Sup, *Masa, "$H_{tr,ms}$", lado=-1)
    # capacidad
    ax.plot([Masa[0], Masa[0]], [0.3, -0.25], color=TXT, lw=1.3)
    ax.plot([6.2, 6.8], [-0.25, -0.25], color=TXT, lw=2)
    ax.plot([6.2, 6.8], [-0.4, -0.4], color=TXT, lw=2)
    ax.plot([Masa[0], Masa[0]], [-0.4, -0.7], color=TXT, lw=1.3)
    ax.text(7.0, -0.33, "$C_m$  capacidad de la masa", fontsize=10, va="center")
    nodo(ax, *Aire, "$\\theta_{air}$  aire interior", AZUL)
    nodo(ax, *Sup, "$\\theta_s$", NAR, dx=-.35, dy=.25)
    nodo(ax, *Masa, "$\\theta_m$", ROJO, dx=-.35, dy=.25)
    for (x, y), t in [(Sum, "$\\theta_{sup}$  aire que entra"), (Ext1, "$\\theta_e$  exterior"),
                      (Ext2, "$\\theta_e$  exterior")]:
        nodo(ax, x, y, t, GRIS)
    for (x, y), t in [(Aire, "$\\Phi_{ia} + \\Phi_{HC}$\nganancias al aire\ny equipo de A/C"),
                      (Sup, "$\\Phi_{st}$  sol y ganancias\nradiantes en superficies"),
                      (Masa, "$\\Phi_m$  ganancias\nque calientan la masa")]:
        ax.annotate("", (x, y), (x + 1.25, y), arrowprops=dict(arrowstyle="-|>", color=AMAR, lw=2))
        ax.text(x + 1.35, y, t, fontsize=9.5, va="center", color=TXT2)
    ax.text(-.35, 4.95, "Red 5R1C de la ISO 13790: cinco conductancias y una capacidad",
            fontsize=13, fontweight="bold")
    guardar(fig, "mt_5r1c.png", nota="Esquema según el anexo C de la ISO 13790. Las flechas amarillas "
                                     "son flujos de calor que entran a cada nodo.")


# ---------------------------------------------------------------------------------------------------------
# 6. Psicrometría
# ---------------------------------------------------------------------------------------------------------
def pvs(T):
    """Presión de vapor de saturación en hPa (fórmula de Magnus con los coeficientes de Alduchov y Eskridge)."""
    return 6.1094 * np.exp(17.625 * T / (T + 243.04))


def razon_humedad(T, HR, p=1013.25):
    pv = HR / 100 * pvs(T)
    return 0.622 * pv / (p - pv)


def fig_psicrometria():
    T = np.linspace(10, 40, 200)
    fig, ax = plt.subplots(figsize=(9.5, 5))
    for hr in range(10, 101, 10):
        w = razon_humedad(T, hr) * 1000
        ax.plot(T, w, color=AZUL if hr == 100 else GRIS, lw=1.6 if hr == 100 else .8)
        j = np.searchsorted(w, 28) - 1 if w.max() > 28 else -1
        ax.text(T[j], w[j], f"{hr} %", fontsize=8, color=TXT2, ha="right", va="bottom")
    ext = (31, 70)
    intr = (24, 50)
    we, wi = razon_humedad(*ext) * 1000, razon_humedad(*intr) * 1000
    ax.plot(*ext[:1], we, "o", color=ROJO, ms=9)
    ax.plot(*intr[:1], wi, "o", color=VERDE, ms=9)
    ax.annotate("exterior\n31 °C, 70 %", (ext[0], we), (ext[0] + 1.5, we + 3.5), fontsize=9.5,
                arrowprops=dict(arrowstyle="-", color=GRIS))
    ax.annotate("interior con A/C\n24 °C, 50 %", (intr[0], wi), (intr[0] - 7, wi + 6), fontsize=9.5,
                arrowprops=dict(arrowstyle="-", color=GRIS))
    ax.annotate("", (ext[0], wi), (ext[0], we), arrowprops=dict(arrowstyle="<->", color=MORADO, lw=1.5))
    ax.text(ext[0] + .4, (we + wi) / 2, "Δw: agua que hay\nque condensar\n(carga latente)", fontsize=9,
            color=MORADO, va="center")
    ax.annotate("", (ext[0], wi), (intr[0], wi), arrowprops=dict(arrowstyle="<->", color=NAR, lw=1.5))
    ax.text((ext[0] + intr[0]) / 2, wi - 1.3, "ΔT: carga sensible", fontsize=9, color=NAR, ha="center")
    ax.set_xlim(10, 40)
    ax.set_ylim(0, 30)
    ax.set_xlabel("temperatura de bulbo seco (°C)")
    ax.set_ylabel("razón de humedad w (g de agua / kg de aire seco)")
    ax.set_title("Carta psicrométrica simplificada a nivel del mar", fontweight="bold")
    guardar(fig, "mt_psicrometria.png", nota="Curvas de humedad relativa calculadas con la fórmula de Magnus "
                                              "(Alduchov y Eskridge) a 1013,25 hPa.")
    # cifras del ejemplo del texto
    V = 60 * 2.5
    mdot = 1.15 * V * 1.0 / 3600
    Qs = mdot * 1.006 * (ext[0] - intr[0])
    Ql = mdot * 2450 * (we - wi) / 1000
    print(f"  w ext {we:.1f} g/kg, w int {wi:.1f} g/kg; infiltración 1 ren/h en 150 m3: "
          f"sensible {Qs:.2f} kW, latente {Ql:.2f} kW (razón {Ql / Qs:.1f})")


# ---------------------------------------------------------------------------------------------------------
# 7. Ciclo de refrigeración: COP y carga parcial
# ---------------------------------------------------------------------------------------------------------
def fig_cop():
    Text = np.linspace(24, 38, 100)
    Tin = 24.0
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.3))
    ax = axs[0]
    Tev = Tin - 14 + 273.15
    Tco = Text + 15 + 273.15
    carnot = Tev / (Tco - Tev)
    ax.plot(Text, carnot, color=AZUL, lw=1.8, label="Carnot entre evaporador y condensador")
    ax.plot(Text, .45 * carnot, color=ROJO, lw=1.8, label="equipo real (≈ 45 % de Carnot)")
    ax.set_xlabel("temperatura exterior (°C)")
    ax.set_ylabel("COP (calor retirado / electricidad)")
    ax.set_ylim(0, 9)
    ax.legend(fontsize=9)
    ax.set_title("El COP baja cuando hace más calor afuera", fontweight="bold")
    ax = axs[1]
    plr = np.linspace(.05, 1, 200)
    cd = .25
    plf = 1 - cd * (1 - plr)
    ax.plot(plr * 100, plf, color=ROJO, lw=1.8, label="sin inversor: ciclos de encendido y apagado")
    pmin = .25
    curva = lambda x: 1 + .2 * (1 - ((x - .5) / .5) ** 2)  # noqa: E731
    inv = np.where(plr >= pmin, curva(plr), np.nan)
    inv_baja = np.where(plr <= pmin, curva(pmin) * (1 - cd * (1 - plr / pmin)), np.nan)
    ax.plot(plr * 100, inv, color=VERDE, lw=1.8, label="con inversor: modula la velocidad")
    ax.plot(plr * 100, inv_baja, color=VERDE, lw=1.8, ls=":", label="inversor bajo su mínimo: vuelve a ciclar")
    ax.axhline(1, color=GRIS, lw=.8)
    ax.set_xlabel("carga parcial (% de la capacidad)")
    ax.set_ylabel("eficiencia relativa a la nominal")
    ax.set_ylim(0.7, 1.35)
    ax.legend(fontsize=9, loc="upper right")
    ax.set_title("Eficiencia a carga parcial", fontweight="bold")
    guardar(fig, "mt_cop.png", nota="Ilustrativa: evaporador 14 K bajo el aire interior (24 °C), condensador "
                                    "15 K sobre el exterior, C_d = 0,25; la curva del inversor es una forma típica.")
    print(f"  COP Carnot ideal 24->32 °C: {(Tin + 273.15) / 8:.0f}; con aproximaciones a 32 °C: "
          f"{np.interp(32, Text, carnot):.1f}, real {np.interp(32, Text, .45 * carnot):.1f}")


# ---------------------------------------------------------------------------------------------------------
# 8. Nevera
# ---------------------------------------------------------------------------------------------------------
def fig_nevera():
    Ta = np.linspace(18, 36, 100)
    UA, Ti, puertas, Pcomp = 2.5, 3.0, 8.0, 110.0
    Q = UA * (Ta - Ti) + puertas
    cop = 2.0 - .035 * (Ta - 25)
    P = Q / cop
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.1))
    ax = axs[0]
    ax.plot(Ta, P / Pcomp * 100, color=AZUL, lw=1.8)
    ax.set_xlabel("temperatura del lugar donde está la nevera (°C)")
    ax.set_ylabel("fracción de tiempo con el compresor encendido (%)")
    ax.set_title("Ciclo de trabajo del compresor", fontweight="bold")
    ax = axs[1]
    E = P * 24 / 1000
    ax.plot(Ta, E, color=ROJO, lw=1.8)
    e25 = np.interp(25, Ta, E)
    for t in (25, 32):
        ax.plot(t, np.interp(t, Ta, E), "o", color=ROJO)
        ax.text(t, np.interp(t, Ta, E) + .05, f"{fmt(np.interp(t, Ta, E), 2)} kWh/día", ha="center",
                fontsize=9, va="bottom")
    ax.set_xlabel("temperatura del lugar donde está la nevera (°C)")
    ax.set_ylabel("energía diaria (kWh)")
    ax.set_title("Consumo diario", fontweight="bold")
    guardar(fig, "mt_nevera.png", nota="Ilustrativa: UA = 2,5 W/K, interior a 3 °C, 8 W por aperturas, "
                                       "compresor de 110 W y COP de 2,0 a 25 °C que baja 0,035 por °C.")
    print(f"  nevera: {e25:.2f} kWh/día a 25 °C, {np.interp(32, Ta, E):.2f} a 32 °C "
          f"({(np.interp(32, Ta, E) / e25 - 1) * 100 / 7:.1f} %/°C)")


# ---------------------------------------------------------------------------------------------------------
# 9. Confort adaptativo e índice de calor
# ---------------------------------------------------------------------------------------------------------
def fig_confort():
    Tm = np.linspace(10, 33.5, 100)
    Tc = .31 * Tm + 17.8
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    ax.fill_between(Tm, Tc - 3.5, Tc + 3.5, color=VERDE, alpha=.15, lw=0, label="80 % de aceptación (± 3,5 K)")
    ax.fill_between(Tm, Tc - 2.5, Tc + 2.5, color=VERDE, alpha=.25, lw=0, label="90 % de aceptación (± 2,5 K)")
    ax.plot(Tm, Tc, color=VERDE2, lw=1.8, label="temperatura operativa de confort")
    tb = (26.5 - 17.8) / .31
    ax.plot(tb, 26.5, "o", color=ROJO, ms=8)
    ax.annotate(f"media exterior ≈ {fmt(tb, 0)} °C\nconfort ≈ 26,5 °C", (tb, 26.5), (20.5, 30.5), fontsize=9.5,
                arrowprops=dict(arrowstyle="-", color=GRIS))
    ax.set_xlabel("temperatura media exterior predominante (°C)")
    ax.set_ylabel("temperatura operativa interior (°C)")
    ax.legend(fontsize=9, loc="upper left")
    ax.set_title("Modelo adaptativo de ASHRAE 55 (espacios ventilados naturalmente)", fontweight="bold")
    guardar(fig, "mt_confort.png", nota="Fórmula de ASHRAE 55-2020: T_conf = 0,31 · T_media + 17,8, válida "
                                        "entre 10 y 33,5 °C de media exterior.")


def indice_calor(Tc, HR):
    """Índice de calor de la NOAA (Rothfusz con ajustes; Steadman simplificada en calor moderado). °C."""
    T = np.asarray(Tc, float) * 9 / 5 + 32
    R = np.asarray(HR, float)
    simple = .5 * (T + 61 + (T - 68) * 1.2 + R * .094)
    hi = (-42.379 + 2.04901523 * T + 10.14333127 * R - .22475541 * T * R - .00683783 * T ** 2
          - .05481717 * R ** 2 + .00122874 * T ** 2 * R + .00085282 * T * R ** 2 - .00000199 * T ** 2 * R ** 2)
    baja = (R < 13) & (T > 80) & (T < 112)
    hi = np.where(baja, hi - (13 - R) / 4 * np.sqrt(np.clip((17 - np.abs(T - 95)) / 17, 0, None)), hi)
    alta = (R > 85) & (T > 80) & (T < 87)
    hi = np.where(alta, hi + (R - 85) / 10 * (87 - T) / 5, hi)
    hi = np.where((simple + T) / 2 < 80, simple, hi)
    return (hi - 32) * 5 / 9


def fig_indice_calor():
    T = np.linspace(22, 38, 321)
    R = np.linspace(30, 100, 141)
    TT, RR = np.meshgrid(T, R)
    HI = indice_calor(TT, RR)
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.6))
    ax = axs[0]
    cs = ax.contourf(TT, RR, HI, levels=np.arange(20, 62, 3), cmap="YlOrRd")
    cl = ax.contour(TT, RR, HI, levels=[27, 32, 41, 54], colors=TXT, linewidths=.8)
    ax.clabel(cl, fmt="%d °C", fontsize=8.5)
    fig.colorbar(cs, ax=ax, label="índice de calor (°C)")
    ax.set_xlabel("temperatura del aire (°C)")
    ax.set_ylabel("humedad relativa (%)")
    ax.grid(False)
    ax.set_title("Índice de calor de la NOAA", fontweight="bold")
    ax = axs[1]
    for hr, c in [(60, AMAR), (75, NAR), (90, ROJO)]:
        ax.plot(T, indice_calor(T, np.full_like(T, hr)), color=c, lw=1.8, label=f"HR = {hr} %")
    ax.plot(T, T, color=GRIS, ls="--", lw=1, label="índice = temperatura")
    ax.set_xlim(22, 34)
    ax.set_ylim(20, 50)
    ax.set_xlabel("temperatura del aire (°C)")
    ax.set_ylabel("índice de calor (°C)")
    ax.legend(fontsize=9)
    ax.set_title("Cortes a humedad fija", fontweight="bold")
    hi90 = indice_calor(T, np.full_like(T, 90.))
    salto = np.argmax(np.diff(hi90))
    ax.annotate(f"salto al pasar de la fórmula\nsimple a la de Rothfusz\n(≈ {fmt(T[salto], 1)} °C)",
                (T[salto], hi90[salto + 1]), (22.6, 40), fontsize=9,
                arrowprops=dict(arrowstyle="-", color=GRIS))
    guardar(fig, "mt_indice_calor.png", nota="Algoritmo del Weather Prediction Center de la NOAA "
                                             "(Rothfusz, 1990; Steadman, 1979).")
    print(f"  índice de calor: 31 °C y 70 % -> {float(indice_calor(31, 70)):.1f} °C; "
          f"salto con HR 90 % en {T[salto]:.2f} °C de {hi90[salto]:.2f} a {hi90[salto + 1]:.2f}")


def fig_cdh():
    h = np.arange(0, 72, 1.0)
    T = 28.5 + 3.3 * np.cos(2 * np.pi * (h - 14.5) / 24) + np.array([0] * 24 + [1.2] * 24 + [-0.8] * 24)
    HR = 78 - 14 * np.cos(2 * np.pi * (h - 14.5) / 24)
    HI = indice_calor(T, HR)
    Tb = 29.0
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(h, HI, color=ROJO, lw=1.8, label="índice de calor horario")
    ax.plot(h, T, color=GRIS, lw=1.2, ls="--", label="temperatura del aire")
    ax.axhline(Tb, color=AZUL, lw=1.3)
    ax.text(71, Tb - .9, f"$T_b$ = {fmt(Tb, 0)} °C", color=AZUL, ha="right", fontsize=10)
    ax.fill_between(h, Tb, HI, where=HI > Tb, color=ROJO, alpha=.18, lw=0, interpolate=True,
                    label="área = grados-hora")
    for d in range(3):
        cdh = np.clip(HI[d * 24:(d + 1) * 24] - Tb, 0, None).sum()
        ax.text(d * 24 + 12, 23.4, f"día {d + 1}: {fmt(cdh, 0)} °C·h", ha="center", fontsize=9.5, color=TXT2)
    ax.set_xlim(0, 71)
    ax.set_ylim(22.5, 44)
    ax.set_xticks(range(0, 73, 6))
    ax.set_xlabel("hora")
    ax.set_ylabel("°C")
    ax.legend(fontsize=9, loc="upper left", ncol=3)
    ax.set_title("Grados-hora de enfriamiento sobre una temperatura base", fontweight="bold")
    guardar(fig, "mt_cdh.png")


# ---------------------------------------------------------------------------------------------------------
# 10. Distribuciones de probabilidad
# ---------------------------------------------------------------------------------------------------------
def fig_distribuciones():
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.9))
    ax = axs[0]
    x = np.linspace(0, 1, 400)
    for (a, b), c in [((2, 18), AZUL), ((15, 35), NAR), ((60, 40), VERDE)]:
        ax.plot(x, stats.beta.pdf(x, a, b), color=c, lw=1.8, label=f"Beta({a}, {b}), media {fmt(a / (a + b), 2)}")
    ax.set_xlabel("proporción de hogares con A/C, p")
    ax.set_ylabel("densidad")
    ax.legend(fontsize=8.5)
    ax.set_title("Beta: proporciones", fontweight="bold")
    ax = axs[1]
    x = np.linspace(0.01, 4, 400)
    for (mu, s), c in [((np.log(.8), .3), AZUL), ((np.log(.8), .6), NAR)]:
        d = stats.lognorm(s=s, scale=np.exp(mu))
        ax.plot(x, d.pdf(x), color=c, lw=1.8, label=f"mediana 0,8; σ_ln = {fmt(s, 1)}")
    ax.set_xlabel("renovaciones de aire por hora")
    ax.legend(fontsize=8.5)
    ax.set_title("Lognormal: magnitudes positivas", fontweight="bold")
    ax = axs[2]
    x = np.linspace(24, 36, 400)
    for (u, lam, k), c in [((26, 3, 2), AZUL), ((26, 3, 4), NAR), ((28, 3, 2), VERDE)]:
        p = 1 - np.exp(-((np.clip(x - u, 0, None) / lam) ** k) * 1 / 6)
        ax.plot(x, p, color=c, lw=1.8, label=f"umbral {u} °C, k = {k}")
    ax.set_xlabel("índice de calor interior (°C)")
    ax.set_ylabel("probabilidad de encender en 10 min")
    ax.legend(fontsize=8.5)
    ax.set_title("Weibull: encendido del A/C", fontweight="bold")
    guardar(fig, "mt_distribuciones.png", nota="Parámetros ilustrativos; los de la tesis salen de las "
                                               "encuestas y la literatura (capítulo de insumos).")


# ---------------------------------------------------------------------------------------------------------
# 11. Monte Carlo
# ---------------------------------------------------------------------------------------------------------
def fig_montecarlo():
    # consumo diario de A/C de un hogar: 0 si no tiene, lognormal si tiene (p = 0,4)
    N = 20000
    tiene = RNG.random(N) < .4
    kwh = np.where(tiene, RNG.lognormal(np.log(6), .6, N), 0)
    n = np.arange(1, N + 1)
    media = np.cumsum(kwh) / n
    verdad = .4 * 6 * np.exp(.6 ** 2 / 2)
    sigma = kwh.std()
    fig, ax = plt.subplots(figsize=(9.5, 4))
    ax.fill_between(n, verdad - 1.96 * sigma / np.sqrt(n), verdad + 1.96 * sigma / np.sqrt(n), color=AZUL,
                    alpha=.15, lw=0, label="± 1,96 σ/√N")
    ax.plot(n, media, color=AZUL, lw=1.4, label="media de los hogares simulados")
    ax.axhline(verdad, color=TXT, ls="--", lw=1, label=f"valor esperado = {fmt(verdad, 2)} kWh")
    ax.set_xscale("log")
    ax.set_ylim(0, 6)
    ax.set_xlabel("número de hogares simulados, N")
    ax.set_ylabel("kWh/día de A/C por vivienda")
    ax.legend(fontsize=9)
    ax.set_title("Método de Monte Carlo: el error baja como 1/√N", fontweight="bold")
    guardar(fig, "mt_montecarlo.png")


# ---------------------------------------------------------------------------------------------------------
# 12. Bayes, equifinalidad y ABC
# ---------------------------------------------------------------------------------------------------------
def fig_bayes():
    a0, b0, n, k = 3, 12, 120, 30
    x = np.linspace(0, 1, 500)
    fig, ax = plt.subplots(figsize=(8.5, 4))
    ax.plot(x, stats.beta.pdf(x, a0, b0), color=GRIS, lw=1.8, label=f"previa Beta({a0}, {b0})")
    lik = stats.binom.pmf(k, n, x)
    ax.plot(x, lik / np.trapezoid(lik, x), color=NAR, lw=1.8, ls="--",
            label=f"verosimilitud: {k} de {n} hogares (normalizada)")
    ax.plot(x, stats.beta.pdf(x, a0 + k, b0 + n - k), color=AZUL, lw=2.2,
            label=f"posterior Beta({a0 + k}, {b0 + n - k})")
    ax.set_xlim(0, .6)
    ax.set_xlabel("proporción de hogares con A/C, p")
    ax.set_ylabel("densidad")
    ax.legend(fontsize=9)
    ax.set_title("Teorema de Bayes con una previa conjugada", fontweight="bold")
    guardar(fig, "mt_bayes.png")
    print(f"  Bayes: posterior media {(a0 + k) / (a0 + b0 + n):.3f}, "
          f"IC95 {stats.beta.ppf(.025, a0 + k, b0 + n - k):.3f}-{stats.beta.ppf(.975, a0 + k, b0 + n - k):.3f}")


def fig_equifinalidad():
    h = np.arange(24) + .5
    potencia = 1.2   # kW por equipo encendido
    a = np.where((h >= 20) | (h < 8), .20 * potencia, 0)            # 20 % de hogares, 12 h de noche
    b = np.where((h >= 13) & (h < 17), .60 * potencia, 0)           # 60 % de hogares, 4 h de tarde
    fig, ax = plt.subplots(figsize=(9.5, 4))
    ax.step(np.r_[h - .5, 24], np.r_[a, a[-1]], where="post", color=AZUL, lw=2, label="20 % de hogares × 12 h de noche")
    ax.step(np.r_[h - .5, 24], np.r_[b, b[-1]], where="post", color=ROJO, lw=2, label="60 % de hogares × 4 h de tarde")
    ax.set_xlim(0, 24)
    ax.set_xticks(range(0, 25, 3))
    ax.set_xlabel("hora del día")
    ax.set_ylabel("kW por vivienda promedio")
    ax.legend(fontsize=9.5, loc="upper left")
    ax.text(23.5, .76, f"energía diaria igual: {fmt(a.sum(), 2)} y {fmt(b.sum(), 2)} kWh",
            ha="right", fontsize=10, color=TXT2)
    ax.set_title("Equifinalidad: el mismo total con perfiles distintos", fontweight="bold")
    guardar(fig, "mt_equifinalidad.png", nota="Ilustrativa, con 1,2 kW por equipo encendido.")


def fig_abc():
    """ABC por rechazo con tolerancias decrecientes: estima las horas de uso diarias del A/C (θ)
    a partir del consumo mensual medio de 200 hogares simulados."""
    p_tiene, pot, n_hog = .4, 1.1, 1000

    def simular(theta, rng):
        tiene = rng.random(n_hog) < p_tiene
        horas = rng.gamma(4, theta / 4, n_hog)
        return (tiene * horas * pot).mean() * 30 + rng.normal(0, 1.5)

    obs = simular(6.0, np.random.default_rng(7))
    M = 12000
    theta = RNG.uniform(0, 14, M)
    sim = np.array([simular(t, RNG) for t in theta])
    dist = np.abs(sim - obs)
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.2))
    ax = axs[0]
    ax.scatter(theta, sim, s=2, color=GRIS, alpha=.25, lw=0)
    eps_l = [20, 8, 2]
    cols = [AMAR, NAR, ROJO]
    for e, c in zip(eps_l, cols):
        m = dist <= e
        ax.scatter(theta[m], sim[m], s=3, color=c, lw=0, label=f"aceptados con ε = {e} kWh")
    ax.axhline(obs, color=TXT, lw=1)
    ax.text(.2, obs + 3, "dato observado", fontsize=9)
    ax.set_xlabel("θ: horas de uso diarias del A/C (previa uniforme 0–14 h)")
    ax.set_ylabel("kWh/mes por vivienda simulado")
    ax.legend(fontsize=9, markerscale=4, loc="lower right")
    ax.set_title("Proponer, simular y comparar", fontweight="bold")
    ax = axs[1]
    bins = np.linspace(0, 14, 57)
    ax.hist(theta, bins=bins, density=True, color=GRIS, alpha=.35, label="previa")
    for e, c in zip(eps_l, cols):
        ax.hist(theta[dist <= e], bins=bins, density=True, histtype="step", color=c, lw=2,
                label=f"posterior aproximada, ε = {e}")
    ax.axvline(6, color=TXT, ls="--", lw=1)
    ax.text(5.8, ax.get_ylim()[1] * .9, "valor usado\npara crear el dato", fontsize=8.5, ha="right")
    ax.set_xlabel("θ (h/día)")
    ax.set_ylabel("densidad")
    ax.legend(fontsize=8.5, loc="center right")
    ax.set_title("Menor tolerancia, posterior más angosta", fontweight="bold")
    guardar(fig, "mt_abc.png")


# ---------------------------------------------------------------------------------------------------------
# 13. Sensibilidad global (función de Ishigami)
# ---------------------------------------------------------------------------------------------------------
def ishigami(X, a=7, b=.1):
    return np.sin(X[:, 0]) + a * np.sin(X[:, 1]) ** 2 + b * X[:, 2] ** 4 * np.sin(X[:, 0])


def fig_sensibilidad():
    a, b, d = 7, .1, 3
    V = a ** 2 / 8 + b * np.pi ** 4 / 5 + b ** 2 * np.pi ** 8 / 18 + .5
    V1 = .5 * (1 + b * np.pi ** 4 / 5) ** 2
    V2 = a ** 2 / 8
    VT3 = 8 * b ** 2 * np.pi ** 8 / 225
    S_an = np.array([V1, V2, 0]) / V
    ST_an = np.array([V1 + VT3, V2, VT3]) / V
    # Saltelli (2010) para S_i y Jansen para S_Ti
    N = 20000
    A = RNG.uniform(-np.pi, np.pi, (N, d))
    B = RNG.uniform(-np.pi, np.pi, (N, d))
    fA, fB = ishigami(A), ishigami(B)
    Vy = np.var(np.r_[fA, fB])
    S, ST = [], []
    for i in range(d):
        ABi = A.copy()
        ABi[:, i] = B[:, i]
        fABi = ishigami(ABi)
        S.append(np.mean(fB * (fABi - fA)) / Vy)
        ST.append(.5 * np.mean((fA - fABi) ** 2) / Vy)
    # Morris: r trayectorias, p = 4 niveles
    r, p = 60, 4
    delta = p / (2 * (p - 1))
    EE = [[] for _ in range(d)]
    for _ in range(r):
        x = RNG.integers(0, p - 1, d) / (p - 1)
        for i in RNG.permutation(d):
            paso = delta if x[i] + delta <= 1 else -delta
            x2 = x.copy()
            x2[i] += paso
            f1 = ishigami((x * 2 * np.pi - np.pi)[None, :])[0]
            f2 = ishigami((x2 * 2 * np.pi - np.pi)[None, :])[0]
            EE[i].append((f2 - f1) / paso)
            x = x2
    mu_s = [np.mean(np.abs(e)) for e in EE]
    sd = [np.std(e, ddof=1) for e in EE]
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.2))
    ax = axs[0]
    for i, c in enumerate([AZUL, NAR, VERDE]):
        ax.plot(mu_s[i], sd[i], "o", ms=10, color=c)
        ax.text(mu_s[i] + .4, sd[i], f"$x_{i + 1}$", fontsize=11, va="center")
    lim = max(max(mu_s), max(sd)) * 1.15
    ax.plot([0, lim], [0, lim], color=GRIS, lw=.8, ls="--")
    ax.text(lim * .97, lim * .9, "σ = μ*", color=TXT2, fontsize=9, ha="right")
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_xlabel("μ*: efecto medio absoluto")
    ax.set_ylabel("σ: no linealidad o interacción")
    ax.set_title("Método de Morris (cribado)", fontweight="bold")
    ax = axs[1]
    xs = np.arange(d)
    ax.bar(xs - .2, S, .38, color=AZUL, label="primer orden $S_i$ (estimado)")
    ax.bar(xs + .2, ST, .38, color=NAR, label="total $S_{Ti}$ (estimado)")
    ax.plot(xs - .2, S_an, "_", color=TXT, ms=22, mew=2, label="valor exacto")
    ax.plot(xs + .2, ST_an, "_", color=TXT, ms=22, mew=2)
    ax.set_xticks(xs, ["$x_1$", "$x_2$", "$x_3$"])
    ax.set_ylim(0, .7)
    ax.set_ylabel("fracción de la varianza de la salida")
    ax.legend(fontsize=9)
    ax.set_title("Índices de Sobol", fontweight="bold")
    guardar(fig, "mt_sensibilidad.png", nota="Función de prueba de Ishigami, f = sen x₁ + 7 sen² x₂ + "
                                             "0,1 x₃⁴ sen x₁, con x_i uniformes en [−π, π].")
    print("  Sobol S:", np.round(S, 3), "exacto", np.round(S_an, 3), "| ST:", np.round(ST, 3), "exacto",
          np.round(ST_an, 3))


# ---------------------------------------------------------------------------------------------------------
# 14. CRPS: cobertura y nitidez
# ---------------------------------------------------------------------------------------------------------
def crps_normal(mu, s, y):
    z = (y - mu) / s
    return s * (z * (2 * stats.norm.cdf(z) - 1) + 2 * stats.norm.pdf(z) - 1 / np.sqrt(np.pi))


def fig_crps():
    y = 210
    casos = [(205, 8, AZUL, "nítida y bien centrada"), (205, 40, NAR, "ancha: cubre, pero dice poco"),
             (180, 8, ROJO, "nítida pero sesgada")]
    x = np.linspace(100, 320, 600)
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    for mu, s, c, t in casos:
        axs[0].plot(x, stats.norm.pdf(x, mu, s), color=c, lw=1.8,
                    label=f"{t}: CRPS = {fmt(crps_normal(mu, s, y), 1)}")
        axs[1].plot(x, stats.norm.cdf(x, mu, s), color=c, lw=1.8)
    for ax in axs:
        ax.axvline(y, color=TXT, lw=1.2, ls="--")
        ax.set_xlabel("kWh/mes por vivienda")
    axs[0].text(y + 3, axs[0].get_ylim()[1] * .55, "observado", fontsize=9)
    axs[0].set_ylabel("densidad predictiva")
    axs[0].legend(fontsize=8.5, loc="upper left", bbox_to_anchor=(0, -.2), ncol=1)
    axs[0].set_title("Tres pronósticos de un mismo dato", fontweight="bold")
    axs[1].step([100, y, y, 320], [0, 0, 1, 1], color=TXT, lw=1.2, where="post")
    axs[1].set_ylabel("función de distribución acumulada")
    axs[1].set_title("El CRPS es el área del cuadrado de la diferencia", fontweight="bold")
    guardar(fig, "mt_crps.png", nota="Ilustrativa. CRPS con la fórmula cerrada para una normal "
                                     "(Gneiting y Raftery, 2007); menor es mejor.")


# ---------------------------------------------------------------------------------------------------------
# 15. Regresión y sobreajuste
# ---------------------------------------------------------------------------------------------------------
def fig_regresion():
    n = 300
    hi = RNG.normal(33, 2.2, n)
    finde = RNG.random(n) < 2 / 7
    lnL = np.log(30000) + .019 * (hi - 33) - .06 * finde + RNG.normal(0, .025, n)
    y = 100 * lnL
    X = np.c_[np.ones(n), hi, finde]
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    res = y - X @ beta
    r2 = 1 - res.var() / y.var()
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.2))
    ax = axs[0]
    for m, c, t in [(~finde, AZUL, "día hábil"), (finde, NAR, "fin de semana")]:
        ax.scatter(hi[m], y[m] - y.mean(), s=10, color=c, alpha=.6, lw=0, label=t)
        xx = np.linspace(hi.min(), hi.max(), 10)
        ax.plot(xx, beta[0] + beta[1] * xx + beta[2] * (t != "día hábil") - y.mean(), color=c, lw=1.8)
    ax.set_xlabel("índice de calor medio del día (°C)")
    ax.set_ylabel("100 · ln(demanda), centrado")
    ax.legend(fontsize=9)
    ax.set_title(f"MCO: pendiente {fmt(beta[1], 2)} % por °C, R² = {fmt(r2, 2)}", fontweight="bold")
    # sobreajuste
    ax = axs[1]
    m = 30
    x = np.sort(RNG.uniform(-1, 1, m))
    f = lambda z: np.sin(2.5 * z) + .3 * z  # noqa: E731
    ytr = f(x) + RNG.normal(0, .25, m)
    xte = RNG.uniform(-1, 1, 2000)
    yte = f(xte) + RNG.normal(0, .25, 2000)
    grados = range(0, 16)
    etr, ete = [], []
    for g in grados:
        c = np.polynomial.polynomial.polyfit(x, ytr, g)
        etr.append(np.sqrt(np.mean((np.polynomial.polynomial.polyval(x, c) - ytr) ** 2)))
        ete.append(np.sqrt(np.mean((np.polynomial.polynomial.polyval(xte, c) - yte) ** 2)))
    ax.plot(grados, etr, "o-", color=AZUL, lw=1.6, ms=4, label="error en entrenamiento")
    ax.plot(grados, ete, "o-", color=ROJO, lw=1.6, ms=4, label="error en datos nuevos (prueba)")
    ax.set_yscale("log")
    ax.set_xlabel("complejidad del modelo (grado del polinomio)")
    ax.set_ylabel("RMSE")
    ax.legend(fontsize=9)
    ax.set_title("Sobreajuste: más complejo no siempre es mejor", fontweight="bold")
    guardar(fig, "mt_regresion.png")
    print(f"  regresión: pendiente {beta[1]:.2f} %/°C, efecto fin de semana {beta[2]:.1f} %")


# ---------------------------------------------------------------------------------------------------------
# 16. Agrupamiento
# ---------------------------------------------------------------------------------------------------------
def kmeans(X, k, rng, n_init=10, it=100):
    mejor = None
    for _ in range(n_init):
        C = X[rng.choice(len(X), k, replace=False)]
        for _ in range(it):
            lab = cdist(X, C).argmin(1)
            C2 = np.array([X[lab == j].mean(0) if np.any(lab == j) else C[j] for j in range(k)])
            if np.allclose(C2, C):
                break
            C = C2
        J = ((X - C[lab]) ** 2).sum()
        if mejor is None or J < mejor[0]:
            mejor = (J, lab, C)
    return mejor


def silueta(X, lab):
    D = cdist(X, X)
    s = np.zeros(len(X))
    for i in range(len(X)):
        mismo = lab == lab[i]
        if mismo.sum() <= 1:
            continue
        a = D[i, mismo].sum() / (mismo.sum() - 1)
        b = min(D[i, lab == j].mean() for j in np.unique(lab) if j != lab[i])
        s[i] = (b - a) / max(a, b)
    return s.mean()


def dbscan(X, eps, minpts):
    D = cdist(X, X)
    vec = [np.flatnonzero(D[i] <= eps) for i in range(len(X))]
    nucleo = np.array([len(v) >= minpts for v in vec])
    lab = np.full(len(X), -1)
    g = 0
    for i in range(len(X)):
        if lab[i] != -1 or not nucleo[i]:
            continue
        lab[i] = g
        pila = list(vec[i])
        while pila:
            j = pila.pop()
            if lab[j] == -1:
                lab[j] = g
                if nucleo[j]:
                    pila.extend(vec[j])
        g += 1
    return lab, nucleo


def fig_kmeans():
    centros = np.array([[60, 1], [110, 2.5], [180, 1.6]])
    escal = np.array([14, .35])
    X = np.vstack([c + RNG.normal(0, 1, (90, 2)) * escal for c in centros])
    Z = (X - X.mean(0)) / X.std(0)
    fig, axs = plt.subplots(1, 3, figsize=(13.5, 4))
    ax = axs[0]
    ax.scatter(X[:, 0], X[:, 1], s=12, color=GRIS, lw=0)
    ax.set_xlabel("área construida (m²)")
    ax.set_ylabel("número de pisos (con ruido)")
    ax.set_title("1. Viviendas sin etiqueta", fontweight="bold")
    J, lab, C = kmeans(Z, 3, RNG)
    ax = axs[1]
    for j, c in enumerate([AZUL, NAR, VERDE]):
        ax.scatter(X[lab == j, 0], X[lab == j, 1], s=12, color=c, lw=0)
    Cx = C * X.std(0) + X.mean(0)
    ax.plot(Cx[:, 0], Cx[:, 1], "X", color=TXT, ms=12, mec="white")
    ax.set_xlabel("área construida (m²)")
    ax.set_title("2. K-Means con k = 3 (X = centroide)", fontweight="bold")
    ax = axs[2]
    ks = range(2, 9)
    inercia, sil = [], []
    for k in ks:
        Jk, labk, _ = kmeans(Z, k, RNG)
        inercia.append(Jk)
        sil.append(silueta(Z, labk))
    ax.plot(list(ks), sil, "o-", color=AZUL, lw=1.6, label="silueta media")
    ax.set_xlabel("número de grupos k")
    ax.set_ylabel("silueta media", color=AZUL)
    ax2 = ax.twinx()
    ax2.plot(list(ks), 1 - np.array(inercia) / ((Z - Z.mean(0)) ** 2).sum(), "s-", color=NAR, lw=1.6)
    ax2.set_ylabel("R² = 1 − SSW/SST", color=NAR)
    ax2.grid(False)
    ax2.spines["right"].set_visible(True)
    ax.set_title("3. Elegir k", fontweight="bold")
    guardar(fig, "mt_kmeans.png", nota="Ilustrativa: tres grupos sintéticos; las variables se estandarizan "
                                       "antes de agrupar.")


def fig_densidad_jerarquico():
    n = 160
    t = RNG.uniform(0, np.pi, n)
    lunas = np.vstack([np.c_[np.cos(t), np.sin(t)], np.c_[1 - np.cos(t), .45 - np.sin(t)]])
    lunas += RNG.normal(0, .07, lunas.shape)
    ruido = RNG.uniform([-1.4, -1], [2.4, 1.4], (14, 2))
    X = np.vstack([lunas, ruido])
    fig, axs = plt.subplots(1, 3, figsize=(13.5, 4))
    _, lab, _ = kmeans(X, 2, RNG)
    ax = axs[0]
    for j, c in enumerate([AZUL, NAR]):
        ax.scatter(X[lab == j, 0], X[lab == j, 1], s=10, color=c, lw=0)
    ax.set_title("K-Means (k = 2): corta las formas", fontweight="bold")
    lab, nucleo = dbscan(X, .2, 5)
    ax = axs[1]
    for j, c in zip(range(lab.max() + 1), [AZUL, NAR, VERDE, MORADO]):
        ax.scatter(X[lab == j, 0], X[lab == j, 1], s=10, color=c, lw=0)
    ax.scatter(X[lab == -1, 0], X[lab == -1, 1], s=22, marker="x", color=ROJO, lw=1.2, label="atípicos")
    ax.legend(fontsize=9, loc="lower left")
    ax.set_title("DBSCAN (ε = 0,2; mín. 5): sigue la densidad", fontweight="bold")
    for ax in axs[:2]:
        ax.set_xticks([])
        ax.set_yticks([])
    ax = axs[2]
    sub = np.r_[RNG.choice(len(lunas) // 2, 12, replace=False),
                len(lunas) // 2 + RNG.choice(len(lunas) // 2, 12, replace=False)]
    Lk = linkage(X[sub], method="average")
    dendrogram(Lk, ax=ax, color_threshold=.9, above_threshold_color=GRIS, no_labels=True,
               link_color_func=None)
    ax.axhline(.9, color=ROJO, ls="--", lw=1)
    ax.text(ax.get_xlim()[1] * .98, .95, "corte", color=ROJO, ha="right", fontsize=9)
    ax.set_ylabel("distancia de fusión")
    ax.set_title("Jerárquico (enlace promedio)", fontweight="bold")
    ax.grid(False)
    guardar(fig, "mt_densidad_jerarquico.png")


def main():
    print("Figuras del marco teórico en", FIG)
    for f in [fig_cadena, fig_agregacion, fig_sol_aire, fig_inercia, fig_5r1c, fig_psicrometria, fig_cop,
              fig_nevera, fig_confort, fig_indice_calor, fig_cdh, fig_distribuciones, fig_montecarlo,
              fig_bayes, fig_equifinalidad, fig_abc, fig_sensibilidad, fig_crps, fig_regresion, fig_kmeans,
              fig_densidad_jerarquico]:
        f()


if __name__ == "__main__":
    main()

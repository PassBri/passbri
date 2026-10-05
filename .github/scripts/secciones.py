"""Genera las secciones SVG del perfil de GitHub de PassBri con estilo de página web."""
import base64, glob, io, os
from PIL import Image, ImageFont
import cairosvg

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = f'{REPO}/assets/web'
os.makedirs(OUT, exist_ok=True)
FP = glob.glob('/usr/share/fonts/**/DejaVuSans.ttf', recursive=True)[0]
FAM = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
AZUL, ORO, MAG, LILA = '#3aa0ff', '#ffc83d', '#c239b3', '#7c8cff'
TXT, SUAVE, TENUE = '#eef4ff', '#a9b8d0', '#7f93b3'


def ancho(t, s, peso=400):
    f = ImageFont.truetype(FP, s)
    return f.getlength(t) * (0.97 if peso >= 600 else 0.93)


def envolver(texto, s, maxw):
    lineas, actual = [], ''
    for p in texto.split():
        prueba = (actual + ' ' + p).strip()
        if ancho(prueba, s) > maxw and actual:
            lineas.append(actual); actual = p
        else:
            actual = prueba
    lineas.append(actual)
    return lineas


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def fondo(w, h, acento=AZUL, cx='15%'):
    return f'''<defs>
<radialGradient id="f" cx="{cx}" cy="0%" r="120%"><stop offset="0" stop-color="#13305e"/><stop offset=".5" stop-color="#0a1530"/><stop offset="1" stop-color="#05070d"/></radialGradient>
<radialGradient id="halo" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{acento}" stop-opacity=".22"/><stop offset="1" stop-color="{acento}" stop-opacity="0"/></radialGradient>
<linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{AZUL}"/><stop offset="1" stop-color="{MAG}"/></linearGradient>
<pattern id="p" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{AZUL}" fill-opacity=".10"/></pattern>
<clipPath id="c"><rect width="{w}" height="{h}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#f)"/><rect width="{w}" height="{h}" fill="url(#p)"/></g>
<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="22" fill="none" stroke="{acento}" stroke-opacity=".3" stroke-width="1.5"/>'''


def etiqueta(num, titulo, x=56, y=68, color=ORO):
    return (f'<path d="M{x+6} {y-12}l6 6-6 6-6-6z" fill="{color}"/>'
            f'<text x="{x+24}" y="{y}" font-size="15" letter-spacing="6" font-weight="600" fill="{color}">{num} · {titulo}</text>')


def chip(x, y, t, c, s=17, h=36):
    w = ancho(t, s) / 0.93 + 46
    return w, (f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h}" rx="{h/2}" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-opacity=".55"/>'
               f'<circle cx="{x+17:.0f}" cy="{y+h/2:.0f}" r="4" fill="{c}"/>'
               f'<text x="{x+29:.0f}" y="{y+h/2+s*0.35:.0f}" font-size="{s}" fill="#e6edf7">{esc(t)}</text>')


def chips(items, x0, y0, maxx, s=17, h=36, gap=10):
    x, y, out = x0, y0, []
    for t, c in items:
        w = ancho(t, s) / 0.93 + 46
        if x + w > maxx and x > x0:
            x, y = x0, y + h + gap
        out.append(chip(x, y, t, c, s, h)[1]); x += w + gap
    return ''.join(out), y + h


def guardar(nombre, w, h, cuerpo, alt):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(alt)}">'
           f'<g font-family="{FAM}">{cuerpo}</g></svg>')
    open(f'{OUT}/{nombre}.svg', 'w', encoding='utf-8').write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.devnull)


def img64(ruta, px):
    if ruta.endswith('.svg'):
        im = Image.open(io.BytesIO(cairosvg.svg2png(url=ruta, output_width=px)))
    else:
        im = Image.open(ruta)
    im = im.convert('RGBA').resize((px, px), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()


# ---------- 1. Métricas (franja bajo el banner) ----------
def metricas():
    W, H = 1200, 170
    datos = [('22', 'años en el aula', 'educación pública colombiana', AZUL),
             ('4', 'productos digitales', 'web, Android y Word', ORO),
             ('+30', 'deportes', 'en LordTraining', MAG),
             ('PDI', 'modelo propio', 'de periodización', LILA)]
    col = W / 4; c = fondo(W, H)
    for i, (n, a, b, color) in enumerate(datos):
        x = i * col + 48
        if i: c += f'<line x1="{i*col:.0f}" y1="40" x2="{i*col:.0f}" y2="{H-40}" stroke="{AZUL}" stroke-opacity=".18"/>'
        c += (f'<text x="{x:.0f}" y="88" font-size="50" font-weight="600" fill="{color}">{n}</text>'
              f'<text x="{x:.0f}" y="118" font-size="19" fill="{TXT}">{a}</text>'
              f'<text x="{x:.0f}" y="142" font-size="15" fill="{TENUE}">{b}</text>')
    guardar('metricas', W, H, c, '22 años en el aula pública; 4 productos digitales; más de 30 deportes en LordTraining; PDI, modelo propio de periodización.')


# ---------- 2. Sobre mí ----------
def sobre_mi():
    W, H = 1200, 452
    c = fondo(W, H) + etiqueta('01', 'SOBRE MÍ')
    c += (f'<text x="56" y="128" font-size="36" font-weight="300" fill="{TXT}">Soy docente de aula.</text>'
          f'<text x="56" y="174" font-size="36" font-weight="300" fill="{TXT}">Pienso como <tspan fill="#5fb3ff" font-weight="600">investigador</tspan> y</text>'
          f'<text x="56" y="220" font-size="36" font-weight="300" fill="{TXT}">construyo como <tspan fill="{ORO}" font-weight="600">desarrollador</tspan>.</text>'
          f'<rect x="56" y="242" width="90" height="3" rx="1.5" fill="url(#l)"/>'
          f'<text x="56" y="280" font-size="18" fill="{SUAVE}">Me interesa el cruce entre la pedagogía,</text>'
          f'<text x="56" y="305" font-size="18" fill="{SUAVE}">las ciencias del deporte y la inteligencia artificial.</text>')
    c += chips([("Docente de Educación Física", AZUL), ("Investigador", LILA), ("Desarrollador", MAG), ("Artista plástico", ORO)], 56, 330, 660)[0]
    ic = {'aula': '<path d="M3 9l9-5 9 5-9 5z"/><path d="M7 11v5c0 1.5 2.5 3 5 3s5-1.5 5-3v-5"/>',
          'form': '<path d="M4 5h6a2 2 0 0 1 2 2v12a2 2 0 0 0-2-2H4z"/><path d="M20 5h-6a2 2 0 0 0-2 2v12a2 2 0 0 1 2-2h6z"/>',
          'apr': '<path d="M8 8l-4 4 4 4"/><path d="M16 8l4 4-4 4"/><path d="M13.5 6l-3 12"/>',
          'ubi': '<path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z"/><circle cx="12" cy="10" r="2.2"/>'}
    filas = [('aula', 'AULA', ['22 años en la educación', 'pública colombiana'], AZUL),
             ('form', 'FORMACIÓN', ['Licenciatura en Educación Física'], ORO),
             ('apr', 'APRENDIENDO', ['Tecnólogo en Análisis y Desarrollo', 'de Software · SENA'], MAG),
             ('ubi', 'UBICACIÓN', ['Santander, Colombia'], AZUL)]
    total = sum(52 + 24 * (len(v) - 1) for _, _, v, _ in filas)
    gap = (H - 100 - total) / 3; ry = 50
    c += f'<line x1="690" y1="56" x2="690" y2="{H-56}" stroke="{AZUL}" stroke-opacity=".2"/>'
    for k, lab, vals, col in filas:
        c += (f'<rect x="736" y="{ry:.0f}" width="52" height="52" rx="14" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-opacity=".45"/>'
              f'<g transform="translate(750 {ry+14:.0f})" fill="none" stroke="{col}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ic[k]}</g>'
              f'<text x="806" y="{ry+18:.0f}" font-size="13" letter-spacing="2.5" font-weight="600" fill="{TENUE}">{lab}</text>')
        c += ''.join(f'<text x="806" y="{ry+42+i*24:.0f}" font-size="19" fill="#e6edf7">{v}</text>' for i, v in enumerate(vals))
        ry += 52 + 24 * (len(vals) - 1) + gap
    guardar('sobre-mi', W, H, c, 'Sobre mí: soy docente de aula; pienso como investigador y construyo como desarrollador. Docente de Educación Física, investigador, desarrollador y artista plástico. 22 años en la educación pública colombiana. Licenciatura en Educación Física. Aprendiendo Tecnólogo en Análisis y Desarrollo de Software en el SENA. Santander, Colombia.')


# ---------- 3. Encabezado de sección ----------
def encabezado(nombre, num, titulo, frase):
    W, H = 1200, 150
    c = fondo(W, H) + etiqueta(num, titulo, y=62)
    c += f'<text x="56" y="112" font-size="34" font-weight="300" fill="{TXT}">{esc(frase)}</text>'
    c += f'<rect x="{W-56-90}" y="74" width="90" height="3" rx="1.5" fill="url(#l)"/>'
    guardar(nombre, W, H, c, f'{titulo.capitalize()}: {frase}')


# ---------- 4. Tarjetas de proyecto ----------
def proyecto(nombre, icono, titulo, sub, desc, tecs, cta, acento, acento2):
    W, H = 600, 400
    c = fondo(W, H, acento, cx='85%')
    c += f'<g clip-path="url(#c)"><circle cx="{W-40}" cy="40" r="190" fill="url(#halo)"/></g>'
    c += (f'<rect x="40" y="40" width="96" height="96" rx="24" fill="#ffffff" fill-opacity=".04" stroke="{acento}" stroke-opacity=".35"/>'
          f'<image href="{icono}" x="48" y="48" width="80" height="80"/>')
    c += (f'<text x="160" y="84" font-size="34" font-weight="600" fill="{TXT}">{esc(titulo)}</text>'
          f'<text x="161" y="116" font-size="14" letter-spacing="2.5" font-weight="600" fill="{acento}">{esc(sub.upper())}</text>')
    lineas = envolver(desc, 21, W - 96)
    assert len(lineas) <= 5, (titulo, lineas)
    for i, l in enumerate(lineas):
        c += f'<text x="40" y="{186+i*31}" font-size="21" fill="{SUAVE}">{esc(l)}</text>'
    ch, fin = chips(tecs, 40, 186 + len(lineas) * 31 - 4, W - 40, s=15, h=32, gap=8)
    c += ch
    assert fin < H - 70, (titulo, fin)
    c += f'<line x1="40" y1="{H-66}" x2="{W-40}" y2="{H-66}" stroke="{acento}" stroke-opacity=".2"/>'
    c += (f'<text x="40" y="{H-30}" font-size="18" font-weight="600" fill="{acento2}">{esc(cta)}</text>'
          f'<g transform="translate({W-76} {H-50})"><rect width="36" height="28" rx="14" fill="{acento2}"/>'
          f'<path d="M11 14h14M20 9l5 5-5 5" fill="none" stroke="#0a1530" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></g>')
    guardar(nombre, W, H, c, f'{titulo}: {sub}. {desc}')


def proyectos():
    base = f'{REPO}/assets/proyectos'
    proyecto('p-romus', img64(f'{base}/romus.svg', 160), 'Romus', 'Asistente de voz para Word',
             'Dices «Ok Romus» y lee, corrige, resume, redacta y da formato a tus documentos. Funciona con Claude, GPT, Gemini o una IA local.',
             [('Office.js', '#2b8cff'), ('JavaScript', ORO), ('IA de voz', MAG)], 'Ver repositorio', AZUL, AZUL)
    proyecto('p-lordtraining', img64(f'{base}/lordtraining.png', 160), 'LordTraining', 'Periodización deportiva · SaaS',
             'Plataforma basada en mi modelo PDI: cinco metodologías de periodización, control de carga ACWR, más de 30 deportes y módulo de scouting.',
             [('SaaS', AZUL), ('Ciencias del deporte', ORO), ('ACWR', MAG)], 'Visitar lordtraining.com', ORO, ORO)
    proyecto('p-rutacima', img64(f'{base}/rutacima.png', 160), 'Ruta a la Cima', 'App de desarrollo personal',
             'Tu vida hasta los 120 años, vista año por año y día por día. El método Ruta a la Cima en el celular: 7 fases × 6 ejes, con versión web conectada.',
             [('Android', '#d9a441'), ('Kotlin', LILA), ('Jetpack Compose', '#c0573e')], 'Ver repositorio', '#d9a441', '#e2b65a')
    proyecto('p-eggchecker', img64(f'{base}/eggchecker.png', 160), 'EggChecker', 'Gestión avícola · SENA ADSO',
             'Plataforma desarrollada en equipo con backend en FastAPI y app Android. Lidero la documentación de ingeniería de software bajo normas ISO/IEC/IEEE.',
             [('Python · FastAPI', '#2bb3a0'), ('Kotlin', LILA), ('Documentación', ORO)], 'Ver repositorio', '#f5c242', '#f5c242')


# ---------- 5. Obra académica ----------
def obra():
    W, H = 1200, 430
    c = fondo(W, H, ORO) + etiqueta('03', 'OBRA ACADÉMICA')
    items = [('PDI', 'Periodización Dual Integrada', 'Modelo original de planificación del entrenamiento. Es la base de LordTraining.', AZUL,
              '<path d="M3 20h18"/><path d="M6 16l4-5 4 3 5-7"/><circle cx="19" cy="7" r="1.2"/>'),
             ('LIBRO', 'Propositivismo Episistémico', 'Libro de filosofía de la educación.', ORO,
              '<path d="M4 5h6a2 2 0 0 1 2 2v12a2 2 0 0 0-2-2H4z"/><path d="M20 5h-6a2 2 0 0 0-2 2v12a2 2 0 0 1 2-2h6z"/>'),
             ('NOVELA', 'QOÁNIMA', 'Ciencia ficción en proceso, parte de la Serie de la teoría del viaje transformativo.', MAG,
              '<path d="M12 3l2.2 5.6L20 9.3l-4.5 3.8 1.4 5.9L12 15.9 7.1 19l1.4-5.9L4 9.3l5.8-.7z"/>')]
    cw = (W - 112 - 2 * 32) / 3
    for i, (tag, tit, desc, col, ic) in enumerate(items):
        x = 56 + i * (cw + 32); y = 104
        c += (f'<rect x="{x:.0f}" y="{y}" width="{cw:.0f}" height="{H-y-48}" rx="18" fill="{col}" fill-opacity=".06" stroke="{col}" stroke-opacity=".35"/>'
              f'<rect x="{x+28:.0f}" y="{y+28}" width="48" height="48" rx="13" fill="{col}" fill-opacity=".14"/>'
              f'<g transform="translate({x+40:.0f} {y+40})" fill="none" stroke="{col}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ic}</g>'
              f'<text x="{x+92:.0f}" y="{y+58}" font-size="13" letter-spacing="3" font-weight="600" fill="{col}">{tag}</text>')
        tl = envolver(tit, 23, cw - 56)
        for j, l in enumerate(tl):
            c += f'<text x="{x+28:.0f}" y="{y+118+j*29}" font-size="23" font-weight="600" fill="{TXT}">{esc(l)}</text>'
        dl = envolver(desc, 17, cw - 56)
        assert len(dl) <= 4, dl
        for j, l in enumerate(dl):
            c += f'<text x="{x+28:.0f}" y="{y+118+len(tl)*29+12+j*25}" font-size="17" fill="{SUAVE}">{esc(l)}</text>'
    guardar('obra', W, H, c, 'Obra académica: Periodización Dual Integrada (PDI), modelo de planificación del entrenamiento; Propositivismo Episistémico, libro de filosofía de la educación; QOÁNIMA, novela de ciencia ficción en proceso.')


# ---------- 6. Herramientas ----------
def herramientas():
    W = 1200
    grupos = [('LENGUAJES', [('HTML', '#e8663d'), ('CSS', '#3c8cff'), ('JavaScript', ORO), ('Python', '#4b8bbe'), ('Kotlin', LILA)]),
              ('FRAMEWORKS', [('FastAPI', '#2bb3a0'), ('Jetpack Compose', '#4285f4'), ('Office.js', '#2b8cff'), ('GitHub Pages', '#a9b8d0')]),
              ('ENTORNO', [('Git', '#f05033'), ('GitHub', '#e6edf7'), ('VS Code', '#2fa3f2'), ('Android Studio', '#3ddc84'), ('Figma', '#a259ff')]),
              ('INTELIGENCIA ARTIFICIAL', [('Claude', '#d97757'), ('Gemini', '#8e75b2'), ('OpenAI', '#74aa9c')])]
    filas = ''; y = 108
    for nom, items in grupos:
        filas += f'<text x="56" y="{y+23}" font-size="13" letter-spacing="2.5" font-weight="600" fill="{TENUE}">{nom}</text>'
        ch, fin = chips(items, 330, y, W - 56)
        filas += ch; y = fin + 26
    H = y + 30
    c = fondo(W, H) + etiqueta('04', 'HERRAMIENTAS') + filas
    guardar('herramientas', W, H, c, 'Herramientas: HTML, CSS, JavaScript, Python, Kotlin; FastAPI, Jetpack Compose, Office.js, GitHub Pages; Git, GitHub, VS Code, Android Studio, Figma; Claude, Gemini, OpenAI.')


# ---------- 7. Más allá del código ----------
def mas_alla():
    W, H = 1200, 380
    c = fondo(W, H, MAG) + etiqueta('05', 'MÁS ALLÁ DEL CÓDIGO')
    # Frailejón estilizado (motivo de su serie)
    def frailejon(x, base, alto, esc_):
        hojas = ''.join(f'<ellipse cx="0" cy="-{16*esc_:.1f}" rx="{4.2*esc_:.1f}" ry="{16*esc_:.1f}" transform="rotate({a})" fill="#a7c4a5" fill-opacity=".9"/>'
                        for a in range(-80, 81, 20))
        return (f'<g transform="translate({x} {base})"><rect x="{-5*esc_:.1f}" y="{-alto}" width="{10*esc_:.1f}" height="{alto}" rx="{4*esc_:.1f}" fill="#7a6146"/>'
                f'<g transform="translate(0 {-alto})">{hojas}<circle r="{3.2*esc_:.1f}" fill="{ORO}"/></g></g>')
    fr = (f'<g clip-path="url(#c)">'
          f'<path d="M880 380 L990 230 L1030 262 L1090 196 L1150 250 L1200 222 L1200 380 Z" fill="{AZUL}" fill-opacity=".08"/>'
          f'<path d="M880 380 L990 230 L1030 262 L1090 196 L1150 250 L1200 222" fill="none" stroke="{AZUL}" stroke-opacity=".35" stroke-width="2"/>'
          f'<path d="M840 380 Q1000 316 1200 328 L1200 380 Z" fill="#5fd39a" fill-opacity=".07"/>'
          + frailejon(985, 334, 70, 1.0) + frailejon(1060, 330, 104, 1.35) + frailejon(1135, 334, 58, 0.9) + '</g>')
    c += fr
    cols = [('ARTE', MAG, 'Pinto desde niño, formado por mi padre. Trabajo óleo sobre lienzo con conceptos abstractos y he expuesto en el Museo de Arte Moderno de Bucaramanga. Mi serie de frailejones habla del páramo y de la violencia extractiva.'),
            ('TERRITORIO', '#5fd39a', 'Defiendo los páramos de Santander y participo en el debate público sobre la educación en Colombia.')]
    x = 56
    for tag, col, txt in cols:
        cw = 450 if tag == 'ARTE' else 330
        c += f'<rect x="{x}" y="112" width="4" height="40" rx="2" fill="{col}"/><text x="{x+20}" y="140" font-size="16" letter-spacing="4" font-weight="600" fill="{col}">{tag}</text>'
        for j, l in enumerate(envolver(txt, 19, cw)):
            c += f'<text x="{x}" y="{190+j*29}" font-size="19" fill="{SUAVE}">{esc(l)}</text>'
        x += cw + 50
    guardar('mas-alla', W, H, c, 'Más allá del código. Arte: pinto óleo sobre lienzo con conceptos abstractos, expuse en el Museo de Arte Moderno de Bucaramanga; mi serie de frailejones habla del páramo. Territorio: defiendo los páramos de Santander y participo en el debate público sobre la educación en Colombia.')


# ---------- 8. Pie ----------
def pie():
    W, H = 1200, 200
    c = fondo(W, H)
    a, b = 'Del aula pública ', 'al código.'
    wa, wb = ancho(a, 30), ancho(b, 30, 600)
    x0 = 600 - (wa + wb) / 2
    c += (f'<text x="{x0:.0f}" y="86" font-size="30" font-weight="300" fill="{TXT}">{a}</text>'
          f'<text x="{x0+wa:.0f}" y="86" font-size="30" font-weight="600" fill="{ORO}">{b}</text>'
          f'<text x="600" y="122" text-anchor="middle" font-size="17" fill="{SUAVE}">Educación × Ciencias del deporte × Inteligencia artificial</text>'
          f'<rect x="555" y="142" width="90" height="3" rx="1.5" fill="url(#l)"/>'
          f'<text x="600" y="174" text-anchor="middle" font-size="13" letter-spacing="4" font-weight="600" fill="{TENUE}">BRIAN SUÁREZ · SANTANDER, COLOMBIA</text>')
    guardar('pie', W, H, c, 'Del aula pública al código. Educación, ciencias del deporte e inteligencia artificial. Brian Suárez, Santander, Colombia.')


metricas(); sobre_mi(); proyectos(); obra(); herramientas(); mas_alla(); pie()
encabezado('h-proyectos', '02', 'PROYECTOS', 'Lo que estoy construyendo')
print('ok')

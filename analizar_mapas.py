#!/usr/bin/env python3
"""PercepMap: 3 mapas de calor + 3 mapas individuais por informante.

Uso: python3 analizar_percepmap_completo.py
Instalación Linux Mint: sudo apt install python3-numpy python3-pil python3-cairosvg
Non modifica respostas.json. Coordenadas locais Leaflet CRS.Simple (800 x 1000).
"""
import argparse
import io
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    import cairosvg
except ImportError as e:
    sys.exit(f'Falta unha biblioteca: {e}\nInstala: sudo apt install python3-numpy python3-pil python3-cairosvg')

MAPAS = {
    'espana': ('España', ('españa.svg', 'espana.svg')),
    'america': ('América', ('américa.svg', 'america.svg')),
    'galicia': ('Galicia', ('galicia.svg',)),
}
CORES = ['#C8463C', '#2878B7', '#26966B', '#9A5BC0', '#D48C23', '#5066BB',
         '#B74D7A', '#738C2D', '#138C9B', '#9A6636', '#664F9B', '#CB704E']
CALOR = ['#d6e9f4', '#a6cfe6', '#70afd2', '#327fae', '#084c80']
W0, H0 = 800, 1000


def slug(s):
    s = unicodedata.normalize('NFKD', str(s))
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^A-Za-z0-9_-]+', '_', s).strip('_')[:80] or 'sen_id'


def fonte(t):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
              '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'):
        if Path(p).is_file():
            return ImageFont.truetype(p, t)
    return ImageFont.load_default()


def xeometrias(v):
    if not isinstance(v, dict):
        return []
    f = v.get('xeometria') or {}
    if not isinstance(f, dict):
        return []
    g = f.get('geometry', f)
    if not isinstance(g, dict):
        return []
    c = g.get('coordinates', [])
    if g.get('type') == 'Polygon':
        return [c]
    if g.get('type') == 'MultiPolygon':
        return c
    return []


def puntos(anel, w, h):
    resultado = []
    for p in anel:
        try:
            x, y = float(p[0]), float(p[1])
            if math.isfinite(x) and math.isfinite(y):
                resultado.append((round(x * w / W0), round((H0-y) * h / H0)))
        except (TypeError, ValueError, IndexError):
            continue
    return resultado


def mascara(v, w, h):
    im = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(im)
    contornos = []
    for pol in xeometrias(v):
        if not isinstance(pol, list) or not pol:
            continue
        ext = puntos(pol[0], w, h)
        if len(ext) < 3:
            continue
        d.polygon(ext, fill=255)
        contornos.append(ext)
        for burato in pol[1:]:
            inte = puntos(burato, w, h)
            if len(inte) >= 3:
                d.polygon(inte, fill=0)
    return im, contornos


def fondo(carpeta, nomes, w, h):
    for n in nomes:
        p = carpeta / 'img' / n
        if p.is_file():
            try:
                b = cairosvg.svg2png(url=str(p), output_width=w, output_height=h)
                img = Image.open(io.BytesIO(b)).convert('RGBA')
                branco = Image.new('RGBA', (w, h), 'white')
                branco.alpha_composite(img)
                return branco, p.name
            except Exception as e:
                raise RuntimeError(f'Non se puido abrir o SVG {p}: {e}') from e
    return Image.new('RGBA', (w, h), '#f7f9fc'), None


def folla_mapa(base, titulo, subtitulo, lenda, destino, aviso=None):
    """Engade cabeceira e lenda baixo o mapa; non tapa as xeometrías."""
    w, h = base.size
    escala = w / 1400
    marxe = max(22, round(38 * escala))
    alto_cabeceira = max(85, round(115 * escala))
    alto_fila = max(32, round(43 * escala))
    alto_lenda = max(110, round(92 * escala) + max(1, len(lenda)) * alto_fila)
    if aviso:
        alto_lenda += alto_fila
    final = Image.new('RGB', (w + 2 * marxe, alto_cabeceira + h + alto_lenda), 'white')
    d = ImageDraw.Draw(final)
    f1, f2, f3 = fonte(max(21, round(32 * escala))), fonte(max(15, round(21 * escala))), fonte(max(14, round(19 * escala)))
    d.text((marxe, 16), titulo, font=f1, fill='#1b3042')
    d.text((marxe, max(52, round(66 * escala))), subtitulo, font=f3, fill='#4f6476')
    final.paste(base.convert('RGB'), (marxe, alto_cabeceira))
    y = alto_cabeceira + h + 18
    d.text((marxe, y), 'Lenda', font=f2, fill='#1b3042')
    y += max(34, round(45 * escala))
    for cor, texto in lenda:
        lado = max(18, round(22 * escala))
        d.rectangle((marxe, y + 2, marxe + lado, y + lado + 2), fill=cor)
        # Axusta só a presentación da lenda; nunca cambia o JSON.
        max_w = w - lado - 20
        texto = str(texto).replace('\n', ' ')
        while texto and d.textbbox((0, 0), texto, font=f3)[2] > max_w:
            texto = texto[:-2]
        d.text((marxe + lado + 14, y), texto, font=f3, fill='#263b4c')
        y += alto_fila
    if aviso:
        d.text((marxe, y), aviso, font=f3, fill='#a34b25')
    destino.parent.mkdir(parents=True, exist_ok=True)
    final.save(destino, dpi=(300, 300), optimize=True)


def mapa_individual(base, titulo, ident, variedades, destino, aviso):
    w, h = base.size
    rexistro = []
    for i, v in enumerate(variedades):
        if not isinstance(v, dict):
            continue
        cor = CORES[i % len(CORES)]
        mask, contornos = mascara(v, w, h)
        if not contornos:
            continue
        capa = Image.new('RGBA', (w, h), cor)
        mask = mask.point(lambda a: round(a * .33))
        base.paste(capa, (0, 0), mask)
        d = ImageDraw.Draw(base)
        for contorno in contornos:
            d.line(contorno + [contorno[0]], fill=cor, width=max(3, round(w / 450)), joint='curve')
        nome = str(v.get('nome') or 'Sen nome')
        descricion = str(v.get('descricion') or '')
        rexistro.append((cor, nome + (f' — {descricion}' if descricion else '')))
    if not rexistro:
        rexistro = [('#d5dce2', 'Sen variedades delimitadas')]
    folla_mapa(base, f'PercepMap · {titulo}',
               f'Informante: {ident} · {sum(1 for v in variedades if xeometrias(v))} variedades',
               rexistro, destino, aviso)


def mapa_calor(base, titulo, persoas, chave, destino, aviso):
    w, h = base.size
    conta = np.zeros((h, w), dtype=np.uint16 if len(persoas) <= 65535 else np.uint32)
    for mapas in persoas.values():
        voto = np.zeros((h, w), dtype=bool)
        for v in mapas[chave]:
            mask, _ = mascara(v, w, h)
            voto |= np.asarray(mask, dtype=np.uint8) > 0
        conta += voto
    n = len(persoas)
    fraccion = conta.astype(np.float32) * (100.0 / n) if n else np.zeros((h, w), dtype=np.float32)
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    from PIL import ImageColor
    for i, cor in enumerate(CALOR):
        minimo, maximo = i * 20, (i + 1) * 20
        sel = (conta > 0) & (fraccion > minimo) & (fraccion <= maximo)
        rgba[sel, :3] = ImageColor.getrgb(cor)
        rgba[sel, 3] = 190
    # Composición RGBA sen alterar o fondo.
    base.alpha_composite(Image.fromarray(rgba, 'RGBA'))
    lenda = [(cor, texto) for cor, texto in zip(CALOR,
             ('>0–20 %', '>20–40 %', '>40–60 %', '>60–80 %', '>80–100 %'))]
    folla_mapa(base, f'PercepMap · Coincidencias · {titulo}',
               f'{n} informantes · todas as variedades · unha persoa conta unha vez por zona',
               lenda, destino, aviso)
    return int(conta.max()) if n else 0


def main():
    p = argparse.ArgumentParser(description='3 mapas de calor e 3 mapas por informante, coas denominacións')
    p.add_argument('respostas', nargs='?', default='respostas.json')
    p.add_argument('--saida', default='resultados_percepmap')
    p.add_argument('--ancho', type=int, default=1400, help='Ancho do mapa en píxeles (por defecto 1400)')
    args = p.parse_args()
    if not 600 <= args.ancho <= 2400:
        p.error('--ancho debe estar entre 600 e 2400')
    entrada = Path(args.respostas).expanduser().resolve()
    if not entrada.is_file():
        p.error(f'Non se atopa {entrada}. Executa na carpeta do cuestionario.')
    try:
        respostas = json.loads(entrada.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as e:
        p.error(f'Non se puido ler respostas.json: {e}')
    if not isinstance(respostas, list):
        p.error('respostas.json debe conter unha lista')
    persoas = {}
    for i, r in enumerate(respostas, 1):
        if not isinstance(r, dict):
            continue
        ident = str(r.get('participanteId') or f'sen_id_{i}')
        mapas = persoas.setdefault(ident, {chave: [] for chave in MAPAS})
        for chave in MAPAS:
            if isinstance(r.get(chave), list):
                mapas[chave].extend(r[chave])
    if not persoas:
        p.error('Non hai participantes no ficheiro')
    w, h = args.ancho, round(args.ancho * H0 / W0)
    saida = Path(args.saida).expanduser().resolve()
    fondos = {}
    for chave, (titulo, nomes) in MAPAS.items():
        try:
            img, nome_svg = fondo(entrada.parent, nomes, w, h)
        except RuntimeError as e:
            p.error(str(e))
        aviso = None if nome_svg else f'ATENCIÓN: falta o SVG de {titulo} na carpeta img/. Fondo neutro.'
        if aviso:
            print(aviso, flush=True)
        fondos[chave] = (img, aviso)
    print(f'Informantes: {len(persoas)}. Xerando mapas de calor...', flush=True)
    for chave, (titulo, _) in MAPAS.items():
        img, aviso = fondos[chave]
        maximo = mapa_calor(img.copy(), titulo, persoas, chave,
                            saida / 'coincidencias' / f'coincidencias_{chave}.png', aviso)
        print(f'  {titulo}: coincidencia máxima {maximo} informantes', flush=True)
    print('Xerando mapas individuais...', flush=True)
    usados = set()
    for ident, mapas in persoas.items():
        nome_ficheiro = slug(ident)
        if nome_ficheiro.lower() in usados:
            p.error(f'Colisión de nomes de ficheiro ao normalizar o ID {ident}. Revisa os IDs.')
        usados.add(nome_ficheiro.lower())
        for chave, (titulo, _) in MAPAS.items():
            img, aviso = fondos[chave]
            mapa_individual(img.copy(), titulo, ident, mapas[chave],
                            saida / 'informantes' / chave / f'{nome_ficheiro}_{chave}.png', aviso)
        print(f'  {ident}: 3 mapas', flush=True)
    print(f'REMATADO. 3 mapas de calor e {len(persoas) * 3} individuais en: {saida}', flush=True)


if __name__ == '__main__':
    main()

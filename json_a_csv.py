#!/usr/bin/env python3
"""Converte respostas.json de PercepMap nunha matriz 0/1 para LibreOffice Calc.
Uso: python3 json_a_csv.py
"""
import csv
import json
import unicodedata
from pathlib import Path

BASE = Path(__file__).resolve().parent
ENTRADA = BASE / 'respostas.json'
SAIDA = BASE / 'percepmap_para_calc.csv'
MAPAS = [('España', ('espana', 'españa')), ('América', ('america', 'américa')), ('Galicia', ('galicia',))]
SOCIO = [
    ('Provincia nacemento', 'provinciaNacemento'),
    ('Concello nacemento', 'concelloNacemento'),
    ('Outro nacemento', 'outroNacemento'),
    ('Texto outro nacemento', 'textoOutroNacemento'),
    ('Provincia residencia', 'provinciaResidencia'),
    ('Concello residencia', 'concelloResidencia'),
    ('Outra residencia', 'outraResidencia'),
    ('Texto outra residencia', 'textoOutraResidencia'),
    ('Xénero', 'xenero'),
    ('Lingua materna', 'linguaMaterna'),
    ('Outra lingua materna', 'outraLinguaMaterna'),
    ('Lingua habitual', 'linguaHabitual'),
    ('Outra lingua habitual', 'outraLinguaHabitual'),
    ('Identificación con variedades do español (máis e menos)', 'identificacion'),
    ('Identificación con variedades do galego (máis e menos)', 'identificacionGalego'),
]


def normalizar(texto):
    """Unifica maiúsculas, espazos e acentos para contar variantes ortográficas simples."""
    texto = ' '.join(str(texto or '').split()).casefold()
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn')


def variedades_de(participante, claves):
    """Le as posibles grafías da clave sen duplicar variedades."""
    resultado = []
    for clave in claves:
        valor = participante.get(clave, [])
        if isinstance(valor, list):
            resultado.extend(x for x in valor if isinstance(x, dict))
    return resultado


def main():
    if not ENTRADA.is_file():
        raise SystemExit(f'Non atopo {ENTRADA.name} na carpeta do programa.')
    try:
        with ENTRADA.open(encoding='utf-8-sig') as f:
            participantes = json.load(f)
    except (ValueError, UnicodeError) as exc:
        raise SystemExit(f'Non se pode ler o JSON: {exc}')
    if not isinstance(participantes, list):
        raise SystemExit('O JSON debe conter unha lista de participantes.')
    if not all(isinstance(p, dict) for p in participantes):
        raise SystemExit('Hai entradas que non son obxectos de participante.')

    # Construír o vocabulario de denominacións por mapa, sen mesturar mapas.
    # Conservamos como cabeceira a primeira grafía atopada.
    vocabulario = {mapa: {} for mapa, _ in MAPAS}
    for p in participantes:
        for mapa, claves in MAPAS:
            for v in variedades_de(p, claves):
                nome = ' '.join(str(v.get('nome') or '').split())
                chave = normalizar(nome)
                if chave and chave not in vocabulario[mapa]:
                    vocabulario[mapa][chave] = nome

    columnas = [(mapa, chave, nome)
                for mapa, _ in MAPAS
                for chave, nome in sorted(vocabulario[mapa].items(), key=lambda par: par[0])]
    cabeceiras = (['Código do informante'] + [titulo for titulo, _ in SOCIO]
                  + [f'{mapa}_{nome}' for mapa, _, nome in columnas]
                  + ['Total España', 'Total América', 'Total Galicia', 'Total variedades'])

    with SAIDA.open('w', encoding='utf-8-sig', newline='') as f:
        escritor = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        escritor.writerow(cabeceiras)
        for p in participantes:
            socio = p.get('datosPersoais') or {}
            if not isinstance(socio, dict):
                socio = {}
            presentes = {}
            for mapa, claves in MAPAS:
                presentes[mapa] = {normalizar(v.get('nome')) for v in variedades_de(p, claves)
                                   if normalizar(v.get('nome'))}
            fila = [p.get('participanteId', '')]
            for _, campo in SOCIO:
                valor = socio.get(campo, '')
                if isinstance(valor, bool):
                    valor = 'Si' if valor else 'Non'
                fila.append('' if valor is None else valor)
            fila.extend(int(chave in presentes[mapa]) for mapa, chave, _ in columnas)
            totais = [len(presentes[mapa]) for mapa, _ in MAPAS]
            fila.extend(totais + [sum(totais)])
            escritor.writerow(fila)

    print(f'Feito: {SAIDA}')
    print(f'Informantes: {len(participantes)}')
    print(f'Columnas de variedades: {len(columnas)}')
    print('Abre o CSV en Calc e escolle o separador punto e coma (;).')


if __name__ == '__main__':
    main()

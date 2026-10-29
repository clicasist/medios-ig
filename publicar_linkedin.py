# -*- coding: utf-8 -*-
"""Publica en la página de empresa de LinkedIn (Grupo Clic) por la API, sin navegador.

A diferencia de Instagram, LinkedIn **sí nos deja subir el archivo**: por eso aquí
se lee el archivo del repo y se sube en tres pasos (API versionada):

    1. se registra la subida   POST /rest/images?action=initializeUpload
       (owner = la organización)  →  devuelve `uploadUrl` + `image` (urn:li:image:…)
    2. se suben los bytes      PUT <uploadUrl>   (un solo uso; responde 201 vacío)
    3. se crea el post         POST /rest/posts  (author = la organización, con la imagen)

**El token nunca se imprime.** Se lee de un archivo o del entorno y se le quita a
cualquier texto antes de mostrarlo.

    python publicar_linkedin.py --verificar        comprueba el token y la organización
    python publicar_linkedin.py --ensayo           enseña qué haría, sin publicar
    python publicar_linkedin.py --pendientes       publica todo lo que ya tocaba
    python publicar_linkedin.py --fecha 2026-12-26
    python publicar_linkedin.py --una linkedin/reservas-clicas.png
"""
import argparse
import datetime
import io
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

# Versión de la API de LinkedIn (formato AAAAMM). LinkedIn mantiene cada versión
# ~1 año; si un día responde «version not supported», sube este número a una
# vigente (ver developer.linkedin.com → Versioning).
VERSION_LI = os.environ.get('LINKEDIN_VERSION', '202606')
API = 'https://api.linkedin.com'

AQUI = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.expanduser(os.path.join('~', '.linkedin', 'token.txt'))
ORG = (os.environ.get('LINKEDIN_ORG') or '146745171')      # id de la página Grupo Clic
AUTOR = 'urn:li:organization:%s' % ORG

PLAN = os.path.join(AQUI, 'linkedin-plan.json')
REGISTRO = os.path.join(AQUI, 'publicado-linkedin.json')

HUSO = -3                 # Chile, horario de verano (septiembre a abril)


# ── token ────────────────────────────────────────────────────────────────────
def leer_token():
    t = (os.environ.get('LINKEDIN_TOKEN') or '').strip()
    if t:
        return t
    if not os.path.exists(TOKEN_FILE):
        raise SystemExit(
            'No encuentro el token de LinkedIn.\n'
            'Guárdelo en %s (solo el token, nada más).\n'
            'No me lo pegue en el chat.' % TOKEN_FILE)
    t = io.open(TOKEN_FILE, encoding='utf-8').read().strip()
    if not t:
        raise SystemExit('El archivo del token está vacío: %s' % TOKEN_FILE)
    return t


def ahora_chile():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=HUSO)


def limpiar(texto, token):
    return texto.replace(token, '«token oculto»') if token else texto


def cabeceras(token, extra=None):
    h = {'Authorization': 'Bearer %s' % token,
         'LinkedIn-Version': VERSION_LI,
         'X-Restli-Protocol-Version': '2.0.0'}
    if extra:
        h.update(extra)
    return h


def pedir(metodo, url, token, cuerpo=None, cabe=None, espera_json=True):
    pedido = urllib.request.Request(url, data=cuerpo, method=metodo)
    for k, v in cabeceras(token, cabe).items():
        pedido.add_header(k, v)
    try:
        with urllib.request.urlopen(pedido, timeout=120) as r:
            crudo = r.read().decode('utf-8', 'replace')
            cab = dict(r.headers)
            return (json.loads(crudo) if (espera_json and crudo.strip()) else crudo), cab
    except urllib.error.HTTPError as e:
        detalle = limpiar(e.read().decode('utf-8', 'replace'), token)
        raise RuntimeError('LinkedIn respondió %s: %s' % (e.code, detalle))
    except urllib.error.URLError as e:
        raise RuntimeError('no se pudo conectar: %s' % limpiar(str(e.reason), token))


# ── publicación ──────────────────────────────────────────────────────────────
def subir_imagen(ruta, token):
    """Pasos 1 y 2: registra la subida y manda los bytes. Devuelve el urn de la imagen."""
    cuerpo = json.dumps({'initializeUploadRequest': {'owner': AUTOR}}).encode('utf-8')
    d, _ = pedir('POST', API + '/rest/images?action=initializeUpload', token,
                 cuerpo=cuerpo, cabe={'Content-Type': 'application/json'})
    val = d['value']
    url_subida, urn = val['uploadUrl'], val['image']
    with open(os.path.join(AQUI, ruta), 'rb') as f:
        datos = f.read()
    pedir('PUT', url_subida, token, cuerpo=datos,
          cabe={'Content-Type': 'application/octet-stream'}, espera_json=False)
    return urn


def publicar(e, token):
    urn = subir_imagen(e['archivo'], token)
    post = {
        'author': AUTOR,
        'commentary': e.get('texto') or '',
        'visibility': 'PUBLIC',
        'distribution': {'feedDistribution': 'MAIN_FEED',
                         'targetEntities': [], 'thirdPartyDistributionChannels': []},
        'content': {'media': {'id': urn, 'altText': e.get('alt', '')[:300]}},
        'lifecycleState': 'PUBLISHED',
        'isReshareDisabledByAuthor': False,
    }
    cuerpo = json.dumps(post).encode('utf-8')
    _, cab = pedir('POST', API + '/rest/posts', token,
                   cuerpo=cuerpo, cabe={'Content-Type': 'application/json'}, espera_json=False)
    return cab.get('x-restli-id') or cab.get('X-RestLi-Id') or cab.get('x-linkedin-id') or 'publicado'


# ── registro ─────────────────────────────────────────────────────────────────
def cargar_registro():
    return json.load(io.open(REGISTRO, encoding='utf-8')) if os.path.exists(REGISTRO) else {}


def guardar_registro(reg):
    io.open(REGISTRO, 'w', encoding='utf-8').write(json.dumps(reg, ensure_ascii=False, indent=1))


# ── principal ────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument('--verificar', action='store_true')
    p.add_argument('--ensayo', action='store_true')
    p.add_argument('--pendientes', action='store_true')
    p.add_argument('--fecha')
    p.add_argument('--una')
    args = p.parse_args()

    if args.verificar:
        token = leer_token()
        d, _ = pedir('GET', API + '/rest/organizations/%s?fields=localizedName,vanityName' % ORG, token)
        print('token: válido')
        print('organización: %s  (urn %s)' % (d.get('localizedName', '?'), AUTOR))
        return

    plan = json.load(io.open(PLAN, encoding='utf-8'))
    todas = plan['publicaciones']

    if args.una:
        elegidas = [e for e in todas if e['archivo'] == args.una]
    elif args.pendientes:
        ahora = ahora_chile()
        elegidas = [e for e in todas
                    if datetime.datetime.fromisoformat(e['fecha'] + 'T' + e['hora']) <= ahora]
        print('son las %s en Chile' % ahora.strftime('%Y-%m-%d %H:%M'))
    else:
        elegidas = [e for e in todas if e['fecha'] == args.fecha] if args.fecha else todas
    if not elegidas:
        print('no hay nada que publicar con ese criterio')
        return

    reg = cargar_registro()
    pendientes = [e for e in elegidas if e['archivo'] not in reg]
    if len(elegidas) - len(pendientes):
        print('%d ya estaban publicadas, se saltan' % (len(elegidas) - len(pendientes)))

    if args.ensayo:
        for e in pendientes:
            print('%s %s  %-11s %s' % (e['fecha'], e['hora'], e.get('marca', ''), e['archivo']))
        print('\nensayo: %d publicaciones. No se envió nada.' % len(pendientes))
        return

    token = leer_token()
    for e in pendientes:
        try:
            pid = publicar(e, token)
            reg[e['archivo']] = dict(id=pid, cuando=datetime.datetime.now().isoformat(timespec='seconds'))
            guardar_registro(reg)
            print('  OK  %-11s %s -> %s' % (e.get('marca', ''), e['archivo'], pid), flush=True)
        except RuntimeError as err:
            print('  FALLA %-11s %s -> %s' % (e.get('marca', ''), e['archivo'], err), flush=True)


if __name__ == '__main__':
    main()

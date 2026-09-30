# -*- coding: utf-8 -*-
"""Publica en Instagram por la API, sin navegador.

Meta **no acepta que le subamos el archivo**: le pasamos una dirección pública y
sus servidores se lo descargan solos. Por eso este programa no necesita ningún
navegador, ni ventana de «elegir archivo», ni que nadie esté delante.

El recorrido de cada pieza es siempre el mismo:

    1. se crea un «contenedor»   POST /<ig_id>/media
    2. se espera a que Meta termine de procesar el video
       (`status_code` = FINISHED)  GET /<contenedor>?fields=status_code
    3. se publica                POST /<ig_id>/media_publish

**El token nunca se imprime.** Se lee de un archivo y no aparece en la pantalla,
ni en los registros, ni en los mensajes de error: antes de mostrar cualquier
texto de Meta se le quita.

    python publicar_instagram.py --verificar        comprueba el token y la cuenta
    python publicar_instagram.py --ensayo           enseña qué haría, sin publicar
    python publicar_instagram.py --hoy              publica lo que toca hoy
    python publicar_instagram.py --fecha 2026-10-03
    python publicar_instagram.py --una clicas/dia-1-reel.mp4
"""
import argparse
import datetime
import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

VERSION = 'v21.0'
# Ojo: el token es de «Instagram con inicio de sesión de Instagram», así que la
# puerta es graph.INSTAGRAM.com, no graph.facebook.com. Con la de Facebook
# responde «Cannot parse access token», que despista bastante.
GRAFO = 'https://graph.instagram.com/' + VERSION

AQUI = os.path.dirname(os.path.abspath(__file__))
ESCRITORIO = r'C:\Users\user\Desktop\dominique\instagram-semana'

# El mismo programa corre en dos sitios: en el computador de casa, con los
# archivos en el Escritorio, y en los servidores de GitHub, con los archivos
# junto al programa. Manda lo que exista.
_EN_CASA = os.path.exists(os.path.join(ESCRITORIO, 'plan-publicacion.json')) \
    and not os.path.exists(os.path.join(AQUI, 'plan-publicacion.json'))
_BASE = ESCRITORIO if _EN_CASA else AQUI

TOKEN = os.path.expanduser(os.path.join('~', '.meta', 'ig_token.txt'))
PLAN = os.path.join(_BASE, 'plan-publicacion.json')
REGISTRO = os.path.join(_BASE, 'publicado.json')

HUSO = -3                 # Chile en horario de verano (septiembre a abril)
ESPERA_MAX = 300          # Meta recomienda no sondear más de 5 minutos
ESPERA_PASO = 20


# ── token ────────────────────────────────────────────────────────────────────
def leer_token():
    """Del entorno cuando corre en GitHub; del archivo cuando corre en casa."""
    t = (os.environ.get('IG_TOKEN') or '').strip()
    if t:
        return t
    if not os.path.exists(TOKEN):
        raise SystemExit(
            'No encuentro el token.\n'
            'Guárdelo en %s (solo el token, nada más).\n'
            'No me lo pegue en el chat.' % TOKEN)
    t = io.open(TOKEN, encoding='utf-8').read().strip()
    if not t:
        raise SystemExit('El archivo del token está vacío: %s' % TOKEN)
    return t


def ahora_chile():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=HUSO)


def limpiar(texto, token):
    """Quita el token de cualquier texto antes de enseñarlo."""
    return texto.replace(token, '«token oculto»') if token else texto


# ── llamadas ─────────────────────────────────────────────────────────────────
def llamar(ruta, token, datos=None, **params):
    url = GRAFO + ruta
    params['access_token'] = token
    cuerpo = None
    if datos is not None:
        datos = dict(datos, access_token=token)
        cuerpo = urllib.parse.urlencode(datos).encode('utf-8')
    else:
        url += '?' + urllib.parse.urlencode(params)
    pedido = urllib.request.Request(url, data=cuerpo)
    try:
        with urllib.request.urlopen(pedido, timeout=120) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        detalle = limpiar(e.read().decode('utf-8', 'replace'), token)
        raise RuntimeError('Meta respondió %s: %s' % (e.code, detalle))
    except urllib.error.URLError as e:
        raise RuntimeError('no se pudo conectar: %s' % limpiar(str(e.reason), token))


def cuenta(token):
    """La cuenta a la que apunta el token.

    Con inicio de sesión de Instagram la cuenta es «yo» directamente: no hay
    página de Facebook de por medio ni hay que recorrer `/me/accounts`.
    """
    d = llamar('/me', token, fields='user_id,username,account_type,followers_count')
    ig = d.get('user_id')
    if not ig:
        raise RuntimeError(
            'El token es válido pero no devuelve ninguna cuenta. Revise que la '
            'cuenta de Instagram sea profesional y siga autorizada.')
    if d.get('account_type') not in ('BUSINESS', 'MEDIA_CREATOR'):
        raise RuntimeError(
            'La cuenta @%s no es profesional (%s): la API no puede publicar en '
            'ella.' % (d.get('username', '?'), d.get('account_type')))
    return ig, d.get('username', '?'), d.get('followers_count')


# ── publicación ──────────────────────────────────────────────────────────────
def esperar(contenedor, token):
    esperado = 0
    while esperado < ESPERA_MAX:
        d = llamar('/' + contenedor, token, fields='status_code,status')
        estado = d.get('status_code')
        if estado == 'FINISHED':
            return
        if estado in ('ERROR', 'EXPIRED'):
            raise RuntimeError('Meta no pudo procesar el archivo (%s): %s'
                               % (estado, d.get('status', '')))
        time.sleep(ESPERA_PASO)
        esperado += ESPERA_PASO
    raise RuntimeError('Meta sigue procesando después de %d s' % ESPERA_MAX)


def publicar(e, ig_id, token):
    campos = {'media_type': e['media_type']}
    if e['archivo'].endswith('.mp4'):
        campos['video_url'] = e['url']
    else:
        campos['image_url'] = e['url']
    if e.get('texto'):
        campos['caption'] = e['texto']
    contenedor = llamar('/%s/media' % ig_id, token, datos=campos)['id']
    esperar(contenedor, token)
    return llamar('/%s/media_publish' % ig_id, token,
                  datos={'creation_id': contenedor})['id']


# ── registro, para no publicar dos veces lo mismo ────────────────────────────
def cargar_registro():
    if os.path.exists(REGISTRO):
        return json.load(io.open(REGISTRO, encoding='utf-8'))
    return {}


def guardar_registro(reg):
    io.open(REGISTRO, 'w', encoding='utf-8').write(
        json.dumps(reg, ensure_ascii=False, indent=1))


# ── principal ────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument('--verificar', action='store_true')
    p.add_argument('--ensayo', action='store_true')
    p.add_argument('--pendientes', action='store_true')
    p.add_argument('--hoy', action='store_true')
    p.add_argument('--fecha')
    p.add_argument('--una')
    args = p.parse_args()

    plan = json.load(io.open(PLAN, encoding='utf-8'))
    todas = plan['publicaciones']

    if args.verificar:
        token = leer_token()
        ig_id, usuario, seguidores = cuenta(token)
        print('token: válido')
        print('cuenta de Instagram: @%s  (id %s)' % (usuario, ig_id))
        print('seguidores: %s' % seguidores)
        print('publicaciones en el plan: %d' % len(todas))
        return

    if args.una:
        elegidas = [e for e in todas if e['archivo'] == args.una]
    elif args.pendientes:
        # Todo lo que ya tocaba y sigue sin salir. Así da igual que el reloj de
        # GitHub llegue tarde o que un día no corra: al día siguiente se pone al
        # día solo, en vez de perderse esa publicación.
        ahora = ahora_chile()
        elegidas = [e for e in todas
                    if datetime.datetime.fromisoformat(e['fecha'] + 'T' + e['hora']) <= ahora]
        print('son las %s en Chile' % ahora.strftime('%Y-%m-%d %H:%M'))
    else:
        dia = args.fecha or (ahora_chile().date().isoformat() if args.hoy else None)
        elegidas = [e for e in todas if e['fecha'] == dia] if dia else todas
    if not elegidas:
        print('no hay nada que publicar con ese criterio')
        return

    reg = cargar_registro()
    pendientes = [e for e in elegidas if e['archivo'] not in reg]
    ya = len(elegidas) - len(pendientes)
    if ya:
        print('%d ya estaban publicadas, se saltan' % ya)

    if args.ensayo:
        for e in pendientes:
            print('%s %s  %-11s %-8s %s' % (e['fecha'], e['hora'], e['marca'],
                                            e['tipo'], e['url']))
        print()
        print('ensayo: %d publicaciones. No se envió nada.' % len(pendientes))
        return

    token = leer_token()
    ig_id, usuario, _ = cuenta(token)
    print('publicando en @%s' % usuario, flush=True)
    for e in pendientes:
        try:
            media = publicar(e, ig_id, token)
            reg[e['archivo']] = dict(id=media, cuando=datetime.datetime.now().isoformat(
                timespec='seconds'))
            guardar_registro(reg)
            print('  OK  %-11s %-8s día %d -> %s' % (e['marca'], e['tipo'], e['dia'], media),
                  flush=True)
        except RuntimeError as err:
            print('  FALLA %-11s %-8s día %d -> %s' % (e['marca'], e['tipo'], e['dia'], err),
                  flush=True)


if __name__ == '__main__':
    main()

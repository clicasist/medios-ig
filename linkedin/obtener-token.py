# -*- coding: utf-8 -*-
"""Obtiene (o renueva) el token de LinkedIn para publicar en la página de empresa.

Hace el OAuth de 3 pasos por ti: abre LinkedIn en tu navegador, tú autorizas con tu
usuario ADMIN de la página, y el programa recibe el permiso en un servidor local,
lo canjea por el token y lo guarda. Tu contraseña la pones en LinkedIn, nunca aquí.

Antes de correrlo, en tu app de developer.linkedin.com:
  · Auth → «Authorized redirect URLs» → añade:  http://localhost:8765/callback
  · Products → pide «Community Management API» (basta el tier Development)
  · copia el «Client ID» y el «Client Secret»

Uso:
  python obtener-token.py --id <CLIENT_ID> --secret <CLIENT_SECRET>
  python obtener-token.py --refrescar          (renueva con el refresh token guardado)

Guarda:
  ~/.linkedin/token.txt     el access token   (lo que lee publicar_linkedin.py / el secreto)
  ~/.linkedin/refresh.txt   el refresh token   (para renovar sin volver a autorizar)
  ~/.linkedin/app.txt       id y secret (una línea cada uno) si los pasas una vez
"""
import argparse, http.server, io, json, os, secrets, sys, threading
import urllib.parse, urllib.request, urllib.error, webbrowser

CARPETA = os.path.expanduser(os.path.join('~', '.linkedin'))
F_TOKEN   = os.path.join(CARPETA, 'token.txt')
F_REFRESH = os.path.join(CARPETA, 'refresh.txt')
F_APP     = os.path.join(CARPETA, 'app.txt')
REDIR = 'http://localhost:8765/callback'
PUERTO = 8765
SCOPES = 'w_organization_social r_organization_social'
AUTH  = 'https://www.linkedin.com/oauth/v2/authorization'
TOKEN = 'https://www.linkedin.com/oauth/v2/accessToken'


def guardar(ruta, texto):
    os.makedirs(CARPETA, exist_ok=True)
    io.open(ruta, 'w', encoding='utf-8').write(texto.strip())


def credenciales(args):
    if args.id and args.secret:
        guardar(F_APP, '%s\n%s' % (args.id, args.secret))
        return args.id, args.secret
    if os.path.exists(F_APP):
        ls = [l.strip() for l in io.open(F_APP, encoding='utf-8') if l.strip()]
        if len(ls) >= 2:
            return ls[0], ls[1]
    raise SystemExit('Faltan --id y --secret (o guárdalos una vez con --id/--secret).')


def canjear(datos, token_url=TOKEN):
    cuerpo = urllib.parse.urlencode(datos).encode('utf-8')
    pedido = urllib.request.Request(token_url, data=cuerpo,
                                    headers={'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        with urllib.request.urlopen(pedido, timeout=60) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise SystemExit('LinkedIn respondió %s: %s' % (e.code, e.read().decode('utf-8', 'replace')))


def anotar(d):
    guardar(F_TOKEN, d['access_token'])
    msg = 'Token guardado en %s' % F_TOKEN
    if d.get('refresh_token'):
        guardar(F_REFRESH, d['refresh_token'])
        msg += '\nRefresh token en %s' % F_REFRESH
    dias = d.get('expires_in', 0) // 86400
    print(msg)
    print('Caduca en ~%d días.' % dias)
    print('\nAhora pégalo como secreto en GitHub:')
    print('  repo clicasist/medios-ig → Settings → Secrets and variables → Actions')
    print('  New repository secret → nombre: LINKEDIN_TOKEN')
    print('\nEl valor está en: %s' % F_TOKEN)


def flujo_navegador(cid, secret):
    estado = secrets.token_urlsafe(16)
    url = AUTH + '?' + urllib.parse.urlencode({
        'response_type': 'code', 'client_id': cid, 'redirect_uri': REDIR,
        'scope': SCOPES, 'state': estado})
    recibido = {}

    class Maneja(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            recibido.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            ok = 'code' in recibido and recibido.get('state') == estado
            self.wfile.write(('<h2>%s</h2><p>Ya puedes cerrar esta pestaña y volver a la terminal.</p>'
                              % ('Listo, autorización recibida.' if ok else 'Hubo un problema.')
                              ).encode('utf-8'))
        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(('localhost', PUERTO), Maneja)
    print('Abriendo LinkedIn en el navegador para que autorices…')
    print('Si no se abre solo, pega esta dirección:\n  %s\n' % url)
    webbrowser.open(url)
    threading.Thread(target=srv.handle_request, daemon=True).start()
    import time
    for _ in range(300):
        if recibido:
            break
        time.sleep(1)
    srv.server_close()
    if recibido.get('error'):
        raise SystemExit('LinkedIn devolvió un error: %s — %s'
                         % (recibido['error'], recibido.get('error_description', '')))
    if 'code' not in recibido:
        raise SystemExit('No llegó el permiso (¿cerraste la pestaña?). Vuelve a intentar.')
    if recibido.get('state') != estado:
        raise SystemExit('El «state» no coincide; por seguridad no sigo. Reintenta.')
    d = canjear({'grant_type': 'authorization_code', 'code': recibido['code'],
                 'redirect_uri': REDIR, 'client_id': cid, 'client_secret': secret})
    anotar(d)


def refrescar(cid, secret):
    if not os.path.exists(F_REFRESH):
        raise SystemExit('No hay refresh token guardado (%s). Corre sin --refrescar una vez.' % F_REFRESH)
    rt = io.open(F_REFRESH, encoding='utf-8').read().strip()
    d = canjear({'grant_type': 'refresh_token', 'refresh_token': rt,
                 'client_id': cid, 'client_secret': secret})
    anotar(d)


def main():
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument('--id')
    p.add_argument('--secret')
    p.add_argument('--refrescar', action='store_true')
    a = p.parse_args()
    cid, secret = credenciales(a)
    (refrescar if a.refrescar else flujo_navegador)(cid, secret)


if __name__ == '__main__':
    main()

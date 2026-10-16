# Medios temporales — campaña de Instagram, 1 al 21 de octubre de 2026

Repositorio **temporal**. Está aquí por dos motivos:

1. **Meta no acepta que le subamos un archivo.** Para publicar por la API hay
   que darle una **dirección pública** y sus servidores se lo descargan solos.
   Esa dirección es `https://clicasist.github.io/medios-ig/…`.
2. **La API de Instagram no sabe programar.** Hay que llamarla en el momento
   exacto, así que el reloj vive aquí: `.github/workflows/publicar.yml` corre
   dos veces al día en los servidores de GitHub. **No hace falta tener ningún
   computador encendido.**

## Qué hay

| | |
|---|---|
| `clicas/`, `clichotel/`, `clicvet/` | 7 reels y 7 historias por marca |
| `plan-publicacion.json` | las 42 publicaciones con fecha, hora, archivo y texto |
| `publicar_instagram.py` | el publicador |
| `publicado.json` | lo ya publicado; evita duplicar |
| `.github/workflows/publicar.yml` | el reloj |

## Ojo: el anuncio narrado va a mano

`clicas/anuncio-narrado.mp4` (19 s, con voz) es la unica pieza que **no** sale
de `semana_instagram.py`. Se agrego a mano a `plan-publicacion.json` como
historia del **1 de octubre a las 13:00**, delante de la historia del dia 1.

Si se vuelve a generar el plan con `plan_publicacion.py`, **esa entrada
desaparece** y hay que volver a agregarla. El generador no la conoce.

Sale como historia y no como reel a peticion del usuario. Las historias no
aceptan pie de foto por la API, asi que va sin texto: la direccion
`clicas.app/estetica` esta dentro del propio video, grande y sostenida hasta el
ultimo cuadro.

## Horario

Una historia a las **13:00** y un reel a las **20:30**, hora de Chile,
alternando ClicAs → Clic Hotel → ClicVet. Del **1 al 21 de octubre de 2026**.

El programa publica **todo lo que ya tocaba y sigue sin salir**, así que si
GitHub se retrasa o un día no corre, al siguiente se pone al día solo en vez de
perder esa publicación.

## El token

Está en el secreto **`IG_TOKEN`** del repositorio. No está en ningún archivo.
Es de la cuenta `@grupo.clic` y **caduca a los 60 días**; se renueva con:

    curl "https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=EL_TOKEN"

Para revocarlo: Instagram → Configuración → **Aplicaciones y sitios web** →
«Clic Publicador-IG» → Suprimir.

## Al terminar la campaña

Borrar este repositorio. Los medios originales están en
`Escritorio\dominique\instagram-semana`.

## Anuncios por estilo (15-10-2026)

`estilos/` — cuatro anuncios hechos con `clic-herramientas/generador-instagram/anuncios_estilos/`.
Las cuatro **historias** se publicaron el 15-10 a mano (`--una`). Los reels del 24 al 27-10 se
quitaron el 16-10 (ver abajo) y en su lugar las cuatro vuelven a salir como historias del 30-10 al
02-11, con nombre `N-historia-b.png` porque el registro ya tiene `N-historia.png` como publicada.
El publicador sigue aceptando `portada_ms` → `thumb_offset` para elegir la portada de un reel.

**Segunda tanda (16-10-2026), piezas 5 a 12:** cada app en los cuatro estilos (la máquina va rosa en
ClicAs, lila en ClicVet y celeste en Clic Hotel). Solo como **historias**, a las 13:00 del 22 al 29-10.
Sin reels a propósito: el dueño pidió que los reels mantengan el estilo de lo ya publicado para no
desordenar la cuadrícula del perfil (los mp4 quedan fuera del repo, en Downloads/anuncios-estilos/reels).

**Reels de los 12 anuncios (16-10-2026):** `estilos/N-reel-oscuro.mp4`. El MISMO diseño y texto que
las historias, pero con los tonos oscuros de la serie del perfil (`anuncios_estilos/render-vertical.mjs
reels oscuro`: el fondo de `fondo()` de marcas_instagram.py copiado en CSS, medido contra un cuadro real).
Salen a las 20:30 del 24-10 al 04-11, con `portada_ms: 8000`. (Una primera versión con las escenas de
la serie, `N-reel-serie.mp4`, se reemplazó el mismo día a pedido del dueño.)

**Orden de los reels (16-10-2026, pedido del dueño): una serie por fila de la cuadrícula** y uno por día,
siempre ClicAs → Clic Hotel → ClicVet dentro de cada fila (así cada fila se lee ClicVet | Clic Hotel | ClicAs).
Filas: titular gigante 22-24/10 · página de reservas 25-27/10 · lista + teléfono 28-30/10 · máquinas
31/10-02/11 (la de ClicAs ahora es VERDE) · rubros oscuros 03-05/11 · recorrido de las tres apps 06-08/11 ·
lanzamiento + cuentas (Grupo Clic y ClicAs) 09-11/11. Antes de mover un reel, contar: si una fila queda
con menos de tres, todo lo de abajo se corre.

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

# Cómo activar la publicación automática en LinkedIn (una sola vez)

El publicador de LinkedIn (`publicar_linkedin.py` + workflow `Publicar en LinkedIn`) ya
está listo. Solo falta **el token**, igual que Instagram necesitó el `IG_TOKEN` de Meta.
Esto hay que hacerlo **una vez** (y renovar el token cuando caduque).

> Publicar en una **página de empresa** exige el permiso `w_organization_social`, que
> LinkedIn **tiene con aprobación**. Quien autorice debe ser **administrador** de la
> página Grupo Clic (id `146745171`).

## Pasos

1. **App de LinkedIn** — entra a https://developer.linkedin.com → *My apps* → crea una app
   (o reutiliza una) y asóciala a la **página de empresa Grupo Clic**.

2. **Pide el producto "Community Management API"** en la pestaña *Products* de la app.
   - Primero te dan el **tier Development**, que ya permite publicar en las páginas que tú
     administras (suficiente para esto). Si más adelante quieres más volumen, se sube a Standard.
   - Scopes que necesitas: **`w_organization_social`** (publicar) y `r_organization_social` (leer).

3. **Genera el token de acceso** (OAuth 2.0) autorizando esos scopes con tu usuario admin.
   - Puedes usar el *OAuth 2.0 token generator* de la propia app (Auth → *Token Generator*),
     o el flujo de 3 pasos (`/oauth/v2/authorization` → `/oauth/v2/accessToken`).
   - El token de acceso **caduca (~60 días)**; guarda también el *refresh token* para renovarlo.

4. **Guarda el token en el repositorio** (nunca en el chat):
   - GitHub → repo `clicasist/medios-ig` → *Settings* → *Secrets and variables* → *Actions*
   - **New repository secret**: nombre `LINKEDIN_TOKEN`, valor = el token.
   - (Opcional) **Variables** → `LINKEDIN_ORG` = `146745171` (ya es el valor por defecto).

5. **Prueba sin publicar**: en *Actions* → *Publicar en LinkedIn* → *Run workflow* con
   «ensayo = true». Debe listar lo pendiente. Para publicar de verdad, el reloj lo hace solo
   a las 13:05 de Chile (o corre el workflow con ensayo = false).

## Probar en tu computador (opcional)
Guarda el token en `C:\Users\user\.linkedin\token.txt` (solo el token) y corre:

```bash
python publicar_linkedin.py --verificar      # comprueba token + organización
python publicar_linkedin.py --ensayo         # enseña qué haría
```

## Qué hay programado
`linkedin-plan.json`: ClicAs 26-dic, Clic Hotel 27-dic, ClicVet 28-dic, 13:00, serie
«Aumenta tus reservas» (texto en *usted*). Para añadir más, agrega entradas a ese archivo.

## Si LinkedIn responde «version not supported»
Sube `VERSION_LI` en `publicar_linkedin.py` (formato AAAAMM) a una versión vigente
(developer.linkedin.com → Versioning). Hoy está en `202606`.

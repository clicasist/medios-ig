# Activar LinkedIn automático — checklist (una sola vez)

Todo el código ya está. Falta **el token**. El paso difícil (OAuth) está resuelto por
`linkedin/obtener-token.py`: abre LinkedIn, tú autorizas y guarda el token solo.

> Debes ser **administrador** de la página Grupo Clic (id `146745171`). Tu contraseña la
> pones en LinkedIn, nunca en el chat ni en el repo.

## 1) Crear la app de LinkedIn
- https://developer.linkedin.com → **Create app** (o usa una existente).
- Asóciala a la **página de empresa Grupo Clic**.
- Pestaña **Products** → pide **«Community Management API»** (te dan el tier *Development*, que ya
  deja publicar en las páginas que administras — suficiente).
- Pestaña **Auth**:
  - En **Authorized redirect URLs** añade exactamente: `http://localhost:8765/callback`
  - Copia el **Client ID** y el **Client Secret**.

## 2) Obtener el token (un comando)
En tu computador:

```bash
python linkedin/obtener-token.py --id TU_CLIENT_ID --secret TU_CLIENT_SECRET
```

Se abre LinkedIn, autorizas los permisos (`w_organization_social`, `r_organization_social`),
y el token queda guardado en `C:\Users\user\.linkedin\token.txt`.
(Para renovarlo cuando caduque, ~60 días: `python linkedin/obtener-token.py --refrescar`.)

## 3) Guardar el token en GitHub
- repo **clicasist/medios-ig** → **Settings** → **Secrets and variables** → **Actions**
- **New repository secret** → nombre `LINKEDIN_TOKEN`, valor = el contenido de `token.txt`.
- (Opcional) **Variables** → `LINKEDIN_ORG` = `146745171` (ya es el valor por defecto).

## 4) Probar
- **Actions** → **Publicar en LinkedIn** → **Run workflow** con *ensayo = true* → debe listar lo pendiente.
- Para publicar de verdad lo hace solo a las **13:05 de Chile** en las fechas del plan.

## Comprobaciones locales (opcional)
```bash
python publicar_linkedin.py --verificar   # token + organización
python publicar_linkedin.py --ensayo      # qué publicaría
```

## Qué está programado
`linkedin-plan.json`: **ClicAs 26-dic, Clic Hotel 27-dic, ClicVet 28-dic (13:00)**, serie
«Aumente sus reservas» (texto en *usted*). Para añadir más, agrega entradas ahí.

## Si LinkedIn dice «version not supported»
Sube `VERSION_LI` (formato AAAAMM) en `publicar_linkedin.py` a una versión vigente
(developer.linkedin.com → Versioning). Hoy está en `202606`.

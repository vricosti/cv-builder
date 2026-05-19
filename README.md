# cv-builder

Pipeline de génération de CV : **YAML** (contenu) → **HTML** (template Jinja2) → **PDF** (Chromium) + **DOCX** (LibreOffice).

Ce repo contient uniquement le moteur de rendu et un exemple. **Vos données restent chez vous** : aucun CV personnel n'est versionné ici.

## Fichiers

```
cv.example.yaml         # exemple à copier en cv.yaml pour démarrer
templates/cv.html.j2    # template + CSS (à toucher pour changer le look)
build.py                # script de génération
pyproject.toml          # déclaration des dépendances (gérée par uv)
uv.lock                 # versions verrouillées (versionnée)
output/                 # cv.html, cv.pdf, cv.docx générés (gitignored)
.venv/                  # environnement Python créé par `uv sync` (gitignored)
```

Le `.gitignore` exclut `cv.yaml` et `cv-*.yaml` : vos données ne risquent pas d'être poussées par accident.

## Installation

```bash
# Une seule fois : installer uv (https://docs.astral.sh/uv/)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Puis dans le repo : crée .venv et installe les dépendances
uv sync
```

Dépendances système :
- `chromium` ou `google-chrome` (pour le PDF)
- `libreoffice` (pour le DOCX)

## Démarrage rapide

```bash
# Copiez l'exemple et éditez-le avec vos données
cp cv.example.yaml cv.yaml
$EDITOR cv.yaml

# Génère HTML + PDF + DOCX
uv run build.py

# Pendant l'édition, plus rapide : seulement le HTML
uv run build.py --format html

# Juste le PDF
uv run build.py --format pdf

# Variante (ex. CV en anglais) — `cv-*.yaml` est aussi gitignored
cp cv.yaml cv-en.yaml
uv run build.py cv-en.yaml
```

Astuce : ouvrez `output/cv.html` dans un navigateur pendant l'édition pour itérer rapidement sur le style.

## Édition

- **Modifier le contenu** : éditez votre `cv.yaml`, relancez `build.py`.
- **Modifier le style** (couleurs, polices, espacements) : éditez le `<style>` dans `templates/cv.html.j2`.
- **Modifier la structure** : éditez la partie `<body>` du template (boucles Jinja `{% for %}`).

## Garder son CV dans un repo séparé (optionnel)

Si vous voulez versionner votre CV dans un repo privé tout en restant synchronisé avec `cv-builder`, vous pouvez le monter en sous-module dans `data/` :

```bash
git submodule add git@github.com:vous/votre-cv-prive.git data
uv run build.py data/cv.yaml
```

C'est exactement le setup utilisé par le mainteneur : un repo privé `cv-builder-vrichomme` monté dans `data/`. Si vous clonez ce repo sans avoir accès au sous-module, `git clone` continuera quand même — `data/` sera simplement vide et vous pourrez utiliser `cv.yaml` à la racine à la place.

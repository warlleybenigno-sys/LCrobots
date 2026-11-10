# LC Robot & Eventos — site

Site estático (HTML/CSS/JS + `build.py` em Python, sem dependências). Publica no Netlify.

## Estado
Página completa implementada (fase 2). Faltam só os itens de "Pendências" abaixo.

- Textos: `data/conteudo.json` · Dados comerciais: `data/config.json`
- Imagens: rode `.venv/bin/python tools/prep_images.py` para recortar/otimizar a partir de `lc media/` (resultado já versionado em `static/img/`)
- Vídeo do hero: coloque o MP4 em `static/video/` e informe `hero_video` no config

## Rodar localmente
```bash
cd "/Users/warlleybenigno/Documents/LC ROBOTS" && python3 build.py && python3 -m http.server 8330 --directory dist
```
Abra <http://localhost:8330>.

## Publicar no Netlify
Conecte a pasta (ou arraste `dist/` em app.netlify.com/drop). O `netlify.toml` já roda `python3 build.py` e publica `dist/`.

## Pendências antes de publicar
- `data/config.json` -> `whatsapp_numero` (só dígitos, ex.: 5511999999999)
- Confirmar Instagram (`instagram_confirmado`)
- `dominio`
- Endereço completo, só se for para publicar
- `modo_revisao` -> `false` antes do lançamento

O `build.py` lista as pendências no terminal.

## Materiais
Coloque os originais em `materiais/` (uma subpasta por atração). Essa pasta não é publicada.

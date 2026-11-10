#!/usr/bin/env python3
"""Recorta e otimiza as imagens de /Users/warlleybenigno/Documents/lc media -> static/img (WebP).

Roda só no computador de quem edita (precisa do Pillow: .venv/bin/python tools/prep_images.py).
As imagens geradas ficam versionadas, então o Netlify NÃO precisa rodar isto.
"""
import json
from pathlib import Path
from PIL import Image

ORIGEM = Path("/Users/warlleybenigno/Documents/lc media")
DESTINO = Path(__file__).resolve().parent.parent / "static" / "img"
LARGURAS = (480, 800, 1280, 1600)


def larguras_de(im):
    """Larguras padrão que cabem + a largura original, se for maior que 480 e não coincidir."""
    ws = [w for w in LARGURAS if w <= im.width] or [LARGURAS[0]]
    if im.width > ws[-1]:
        ws.append(im.width)
    return ws


R1 = "Generating_robot_party_images_7438831b_2K.jpg"
R2 = "Generating_robot_party_versions_97f22d64_2K.jpg"
R3 = "Generating_robot_party_versions_cffc8128_2K.jpg"
R4 = "Generating_robot_party_images_a8db1438_2K.jpg"
P1 = "Improve_Paris_track_image_resolu…_f088fbab_2K.jpg"
P2 = "Generate_LED_dance_floor_images_86c8d6af_2K.jpg"
P3 = "Generate_LED_dance_floor_images_99fc9c1b_2K.jpg"
D1 = "Generate_images_of_DJ_9959dafd_2K.jpg"
D2 = "Generate_images_of_DJ_bd379400.jpg"
V360 = "Generating_360_photo_booth_images_67b82c43_2K.jpg"

# nome -> (arquivo, (esq, topo, dir, base)) ; None = imagem inteira
CORTES = {
    "robo-casamento-bolo": (R1, (0, 0, 1536, 903)),
    "robo-festa-infantil-dupla": (R1, (0, 917, 1536, 1829)),
    "robo-balada-dupla": (R1, (0, 1843, 1536, 2752)),
    "robo-casamento-pista": (R2, (32, 37, 1506, 903)),
    "robo-led-vermelho-criancas": (R2, (32, 940, 1506, 1812)),
    "robo-noite-ao-ar-livre": (R2, (32, 1851, 1506, 2713)),
    "robo-amarelo-noivos": (R3, (0, 0, 767, 1376)),
    "robo-amarelo-criancas": (R3, (768, 0, 1536, 1376)),
    "robo-led-vermelho-balada": (R3, (0, 1377, 767, 2752)),
    "robo-amarelo-salao-roxo": (R3, (768, 1377, 1536, 2752)),
    "robo-amarelo-vertical": (R4, None),
    "pista-paris-salao": (P1, None),
    "pista-paris-estrutura": (P2, (0, 0, 1536, 910)),
    "pista-paris-detalhe": (P2, (0, 920, 762, 1830)),
    "pista-paris-mesas": (P3, (10, 15, 1530, 908)),
    "pista-paris-sapatos": (P3, (10, 925, 1530, 1930)),
    # foto externa (Unsplash, Jason Mavrommatis, licença Unsplash): usada só como ilustração do drone
    "drone-ilustrativo": ("web/drone-unsplash-jason-mavrommatis.jpg", None),
    "dj-controladora": (D1, (0, 0, 767, 1376)),
    "dj-ao-ar-livre": (D1, (768, 0, 1536, 1376)),
    "dj-pista-publico": (D2, None),
    "plataforma-360": (V360, None),
}


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    manifesto = {}
    for nome, (arq, box) in CORTES.items():
        im = Image.open(ORIGEM / arq).convert("RGB")
        if box:
            im = im.crop(box)
        manifesto[nome] = {"w": im.width, "h": im.height,
                           "larguras": larguras_de(im)}
        for w in larguras_de(im):
            h = round(im.height * w / im.width)
            im.resize((min(w, im.width), h), Image.LANCZOS).save(
                DESTINO / f"{nome}-{w}.webp", "WEBP", quality=78, method=6)
        print(f"{nome}: {im.width}x{im.height}")

    # logo nova: recorta o miolo e transforma o preto de fundo em transparência (sem mexer no desenho)
    logo = Image.open(ORIGEM / "logo-nova-original.webp").convert("RGB").crop((150, 120, 1110, 1135))
    mx = logo.convert("RGB").point(lambda v: v).split()
    from PIL import ImageChops
    mx = ImageChops.lighter(ImageChops.lighter(mx[0], mx[1]), mx[2])
    alfa = mx.point(lambda v: 0 if v <= 22 else min(255, int((v - 22) * 255 / 40)))
    logo = logo.convert("RGBA")
    logo.putalpha(alfa)
    bbox = logo.getbbox()
    if bbox:
        logo = logo.crop(bbox)
    for w in (160, 320, 640):
        h = round(logo.height * w / logo.width)
        logo.resize((w, h), Image.LANCZOS).save(DESTINO / f"logo-{w}.webp", "WEBP", quality=92)
    logo.resize((64, round(64 * logo.height / logo.width)), Image.LANCZOS).save(DESTINO / "favicon.png")
    print("logo:", logo.size)
    manifesto["_logo"] = {"w": logo.width, "h": logo.height}
    (DESTINO.parent.parent / "data" / "imagens.json").write_text(
        json.dumps(manifesto, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()

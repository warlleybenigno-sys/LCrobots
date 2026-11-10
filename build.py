#!/usr/bin/env python3
"""Build do site LC Robot & Eventos -> dist/. Só biblioteca padrão.

Uso: python3 build.py
Lê data/config.json, data/conteudo.json e data/imagens.json, monta o HTML
e copia static/ para dist/. Lista no terminal o que falta preencher.
"""
import hashlib
import json
import shutil
import sys
from html import escape as e
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).parent
DIST = RAIZ / "dist"
CFG = json.loads((RAIZ / "data" / "config.json").read_text(encoding="utf-8"))
CT = json.loads((RAIZ / "data" / "conteudo.json").read_text(encoding="utf-8"))
IMG = json.loads((RAIZ / "data" / "imagens.json").read_text(encoding="utf-8"))

NUMERO = "".join(c for c in CFG["whatsapp_numero"] if c.isdigit())
REVISAO = CFG["modo_revisao"]
SERV = CT["servicos"]


# ---------- helpers ----------
def wa(chave="geral"):
    """Link do WhatsApp. Sem número confirmado, aponta para a seção de contato (nunca um link falso)."""
    if not NUMERO:
        return "#contato"
    return f"https://wa.me/{NUMERO}?text={quote(CFG['mensagens_whatsapp'][chave])}"


def pic(nome, alt, sizes="100vw", cls="", eager=False, extra=""):
    m = IMG[nome]
    ws = m["larguras"]
    srcset = ", ".join(f"img/{nome}-{w}.webp {min(w, m['w'])}w" for w in ws)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="img/{nome}-{ws[-1]}.webp" srcset="{srcset}" sizes="{sizes}" '
            f'width="{m["w"]}" height="{m["h"]}" alt="{e(alt)}" {load} {extra}>')


def botao(texto, chave, cls="btn", extra=""):
    pend = ' data-pendente="true"' if not NUMERO else ""
    ext = ' target="_blank" rel="noopener"' if NUMERO else ""
    return f'<a class="{cls}" href="{wa(chave)}"{ext}{pend} {extra}>{e(texto)}</a>'


def s(chave):
    return SERV[chave]


def txt_servico(chave, h="h3", cls=""):
    d = s(chave)
    aviso = f'<p class="aviso">{e(d["aviso"])}</p>' if d.get("aviso") else ""
    return (f'<div class="serv-txt {cls}"><{h}>{e(d["nome"])}</{h}><p>{e(d["descricao"])}</p>'
            f'<p class="beneficio">{e(d["beneficio"])}</p>{aviso}</div>')


# ---------- seções ----------
def header():
    nav = [("#empresa", "A empresa"), ("#atracoes", "Atrações"), ("#galeria", "Galeria"), ("#contato", "Contato")]
    links = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in nav)
    return f"""
<header class="topo" id="topo">
  <div class="topo-in">
    <a class="marca" href="#inicio" aria-label="LC Robot &amp; Eventos, ir para o início">
      <img src="img/logo-160.webp" srcset="img/logo-160.webp 160w, img/logo-320.webp 320w" sizes="82px" width="160" height="{round(160 * IMG['_logo']['h'] / IMG['_logo']['w'])}" alt="LC Robot &amp; Eventos">
    </a>
    <nav id="menu" class="menu" aria-label="Principal"><ul>{links}</ul>
      {botao("Solicitar orçamento", "geral", "btn btn-menu")}
    </nav>
    <button class="burger" type="button" aria-expanded="false" aria-controls="menu" aria-label="Abrir menu"><span></span><span></span></button>
  </div>
</header>"""


def hero():
    h = CT["hero"]
    video = CFG.get("hero_video", "").strip()
    midia = ""
    if video:
        midia = (f'<video class="hero-video" autoplay muted loop playsinline preload="metadata" '
                 f'poster="img/{h["imagem_desktop"]}-1280.webp" aria-hidden="true"><source src="video/{e(video)}" type="video/mp4"></video>')
    mob = IMG[h["imagem_mobile"]]
    des = IMG[h["imagem_desktop"]]
    m_src = f'img/{h["imagem_mobile"]}-800.webp 800w, img/{h["imagem_mobile"]}-1280.webp 1280w'
    d_src = f'img/{h["imagem_desktop"]}-1280.webp 1280w'
    return f"""
<section class="hero" id="inicio">
  <picture class="hero-img">
    <source media="(min-width: 760px)" srcset="{d_src}" sizes="100vw">
    <img src="img/{h['imagem_mobile']}-800.webp" srcset="{m_src}" sizes="100vw" width="{mob['w']}" height="{mob['h']}" alt="{e(h['alt'])}" fetchpriority="high">
  </picture>
  {midia}
  <div class="hero-vel"></div>
  <div class="hero-txt wrap">
    <h1>{e(h['titulo'])}</h1>
    <p class="hero-sub">{e(h['subtitulo'])}</p>
    <div class="hero-acoes">
      {botao("Solicitar orçamento", "geral", "btn btn-grande")}
      <a class="btn btn-fantasma" href="#atracoes">Conhecer atrações</a>
    </div>
  </div>
</section>"""


def empresa():
    d = CT["empresa"]
    ps = "".join(f"<p>{e(p)}</p>" for p in d["paragrafos"])
    a, b = d["imagens"]
    return f"""
<section class="secao empresa" id="empresa">
  <div class="wrap grade-empresa">
    <div class="empresa-txt reveal">
      <p class="rotulo">{e(d['rotulo'])}</p>
      <h2>{e(d['titulo'])}</h2>
      {ps}
      <ol class="indice" aria-label="Famílias de atrações">
        {''.join(f'<li><a href="#fam-{f["id"]}"><span>{f["rotulo"]}</span>{e(f["titulo"])}</a></li>' for f in CT['familias'])}
      </ol>
    </div>
    <div class="empresa-fotos reveal">
      {pic(a['nome'], a['alt'], '(min-width: 900px) 30vw, 60vw', 'foto-a')}
      {pic(b['nome'], b['alt'], '(min-width: 900px) 24vw, 45vw', 'foto-b')}
    </div>
  </div>
</section>"""


def familia_titulo(i):
    f = CT["familias"][i]
    return (f'<div class="fam-tit wrap reveal" id="fam-{f["id"]}"><span class="fam-n">{f["rotulo"]}</span>'
            f'<h2>{e(f["titulo"])}</h2></div>')


def robos():
    d = s("robos_led")
    fotos = CT["imagens_de_servico"]["robos_led"]
    tira = "".join(f'<li>{pic(f["nome"], f["alt"], "(min-width: 900px) 30vw, 90vw")}</li>' for f in fotos)
    return f"""
<section class="atracao robos" id="robos-led">
  {familia_titulo(0)}
  <div class="robos-palco">
    {pic('robo-noite-ao-ar-livre', 'Robô amarelo e robô com LEDs coloridos dançando à noite em festa ao ar livre, com luzes e fumaça', '100vw', 'robos-bg')}
    <div class="robos-cartao wrap reveal">
      <div class="robos-txt">
        <p class="rotulo">Destaque</p>
        <h3>{e(d['nome'])}</h3>
        <p>{e(d['descricao'])}</p>
        <p class="beneficio">{e(d['beneficio'])}</p>
      </div>
    </div>
  </div>
  <ul class="tira wrap">{tira}</ul>
</section>"""


def estrutura():
    paris = txt_servico("pista_paris")
    dj = txt_servico("dj")
    return f"""
<section class="atracao estrutura">
  {familia_titulo(1)}
  <div class="wrap paris reveal" id="pista-paris">
    <div class="paris-fotos">
      {pic('pista-paris-salao', 'Pista Paris em salão de festas: módulos iluminados no piso, com mesa de doces ao fundo', '(min-width: 900px) 34vw, 70vw', 'paris-a')}
      {pic('pista-paris-detalhe', 'Detalhe dos módulos da Pista Paris, com luzes alinhadas em profundidade', '(min-width: 900px) 24vw, 50vw', 'paris-b')}
    </div>
    {paris}
  </div>
  <div class="wrap dj-bloco reveal" id="dj">
    <div class="dj-foto">{pic('dj-pista-publico', 'DJ na controladora diante do público em pista iluminada', '(min-width: 900px) 28vw, 80vw')}</div>
    {dj}
  </div>
  <div class="wrap trio reveal">
    <div class="trio-item" id="sonorizacao">{txt_servico('sonorizacao')}</div>
    <div class="trio-item" id="iluminacao">
      {pic('pista-paris-estrutura', 'Estrutura de iluminação com moving heads e globos de espelho sobre a pista', '(min-width: 900px) 28vw, 90vw')}
      {txt_servico('iluminacao')}
    </div>
    <div class="trio-item" id="co2">{txt_servico('co2')}{'<span class="provisorio">Foto em breve</span>' if REVISAO else ''}</div>
  </div>
</section>"""


def experiencias():
    return f"""
<section class="atracao experiencias">
  {familia_titulo(2)}
  <div class="wrap exp reveal" id="plataforma-360">
    <div class="exp-foto">{pic('plataforma-360', 'Três amigas posando na plataforma 360º com luz azul, em festa de aniversário', '(min-width: 900px) 30vw, 70vw')}</div>
    {txt_servico('plataforma_360')}
  </div>
  <div class="wrap drone reveal" id="drone">
    <figure class="drone-foto">
      {pic('drone-ilustrativo', 'Drone com câmera em voo ao pôr do sol, com céu alaranjado e montanhas ao fundo', '(min-width: 900px) 34vw, 90vw')}
      <figcaption>Imagem ilustrativa. Foto: Jason Mavrommatis / Unsplash.</figcaption>
    </figure>
    {txt_servico('drone')}
    {'<span class="provisorio">Imagens aéreas em breve</span>' if REVISAO else ''}
  </div>
</section>"""


def eventos():
    d = CT["eventos"]
    cards = "".join(
        f'<li class="ev reveal"><h3>{e(i["nome"])}</h3><p>{e(i["texto"])}</p></li>' for i in d["itens"])
    return f"""
<section class="secao eventos" id="eventos">
  <div class="wrap">
    <p class="rotulo">{e(d['rotulo'])}</p>
    <h2>{e(d['titulo'])}</h2>
    <ul class="ev-lista">{cards}</ul>
    <p class="nota">{e(d['nota'])}</p>
  </div>
</section>"""


def galeria():
    d = CT["galeria"]
    itens = "".join(
        f'<li class="g {i["span"]}"><button type="button" data-lightbox="img/{i["nome"]}-{IMG[i["nome"]]["larguras"][-1]}.webp" '
        f'data-alt="{e(i["alt"])}" aria-label="Ampliar: {e(i["alt"])}">{pic(i["nome"], i["alt"], "(min-width: 900px) 50vw, (min-width: 600px) 66vw, 100vw" if i["span"] == "wide" else "(min-width: 900px) 25vw, (min-width: 600px) 33vw, 50vw")}</button></li>'
        for i in d["itens"])
    return f"""
<section class="secao galeria" id="galeria">
  <div class="wrap">
    <p class="rotulo">{e(d['rotulo'])}</p>
    <h2>{e(d['titulo'])}</h2>
  </div>
  <ul class="g-grade wrap">{itens}</ul>
  <div class="wrap g-cta">
    <p>Viu algo que combina com a sua festa? Fale com a equipe.</p>
    {botao("Solicitar orçamento", "geral", "btn")}
  </div>
</section>
<dialog class="lb" id="lb" aria-label="Imagem ampliada">
  <button type="button" class="lb-fechar" aria-label="Fechar">×</button>
  <img alt="" src="">
</dialog>"""


def prova():
    d = CT["prova_social"]
    if not d["ativo"]:
        return ""
    return f"""
<section class="secao prova">
  <div class="wrap prova-in reveal">
    <p class="rotulo">{e(d['rotulo'])}</p>
    <h2>{e(d['titulo'])}</h2>
    <p>{e(d['texto'])}</p>
    <a class="link-cta" href="{e(d['link'])}" target="_blank" rel="noopener">{e(d['link_texto'])}</a>
  </div>
</section>"""


def passos():
    d = CT["passos"]
    li = "".join(f'<li class="reveal"><span class="pn">{n}</span><h3>{e(i["titulo"])}</h3><p>{e(i["texto"])}</p></li>'
                 for n, i in enumerate(d["itens"], 1))
    return f"""
<section class="secao passos" id="orcamento">
  <div class="wrap">
    <p class="rotulo">{e(d['rotulo'])}</p>
    <h2>{e(d['titulo'])}</h2>
    <ol class="p-lista">{li}</ol>
    {botao("Chamar a equipe", "geral", "btn")}
  </div>
</section>"""


def faq():
    itens = "".join(f'<details><summary>{e(i["p"])}</summary><p>{e(i["r"])}</p></details>' for i in CT["faq"])
    return f"""
<section class="secao faq" id="faq">
  <div class="wrap faq-in">
    <div><p class="rotulo">Perguntas frequentes</p><h2>Antes de chamar, talvez você queira saber.</h2></div>
    <div class="faq-lista">{itens}</div>
  </div>
</section>"""


def cta_final():
    d = CT["cta_final"]
    return f"""
<section class="cta-final" id="contato">
  {pic(d['imagem'], d['alt'], '100vw', 'cta-bg')}
  <div class="cta-vel"></div>
  <div class="wrap cta-txt reveal">
    <h2>{e(d['titulo'])}</h2>
    <p>{e(d['texto'])}</p>
    {botao(d['botao'], 'geral', 'btn btn-grande')}
    {'<p class="aviso-config">Atenção: o número de WhatsApp ainda não foi configurado (data/config.json).</p>' if (REVISAO and not NUMERO) else ''}
  </div>
</section>"""


def rodape():
    insta = ""
    if CFG["instagram_url"].strip():
        insta = f'<li><a href="{e(CFG["instagram_url"])}" target="_blank" rel="noopener">Instagram</a></li>'
    zap = f'<li><a href="{wa("geral")}" target="_blank" rel="noopener">WhatsApp</a></li>' if NUMERO else ""
    end = CFG["endereco_completo"].strip() or CFG["localizacao_publica"]
    return f"""
<footer class="rodape">
  <div class="wrap rodape-in">
    <div class="rodape-marca">
      <img src="img/logo-320.webp" width="106" height="{round(106 * IMG['_logo']['h'] / IMG['_logo']['w'])}" alt="LC Robot &amp; Eventos" loading="lazy">
      <p>{e(CFG['nome'])}</p>
      <p class="mudo">{e(end)}</p>
    </div>
    <ul class="rodape-links">
      <li><a href="#empresa">A empresa</a></li><li><a href="#atracoes">Atrações</a></li>
      <li><a href="#galeria">Galeria</a></li><li><a href="#faq">Perguntas</a></li>{insta}{zap}
    </ul>
  </div>
  <p class="wrap direitos">© {2026} {e(CFG['nome'])}. Todos os direitos reservados.</p>
</footer>
<div class="barra-zap"><a class="btn btn-grande" href="{wa('geral')}"{' target="_blank" rel="noopener"' if NUMERO else ''}>Solicitar orçamento</a></div>"""


def jsonld():
    dom = CFG["dominio"].strip().rstrip("/")
    if not dom:
        return ""
    d = {"@context": "https://schema.org", "@type": "EntertainmentBusiness", "name": CFG["nome"], "url": dom + "/",
         "address": {"@type": "PostalAddress", "addressLocality": "Embu das Artes", "addressRegion": "SP", "addressCountry": "BR"}}
    if CFG["instagram_confirmado"]:
        d["sameAs"] = [CFG["instagram_url"]]
    return f'<script type="application/ld+json">{json.dumps(d, ensure_ascii=False)}</script>'


def versao(caminho):
    """Hash curto do arquivo: muda quando o CSS/JS muda e evita cache antigo no celular."""
    return hashlib.md5((RAIZ / "static" / caminho).read_bytes()).hexdigest()[:8]


def pagina():
    seo = CT["seo"]
    dom = CFG["dominio"].strip().rstrip("/")
    og = f'<meta property="og:image" content="{dom}/img/{CT["hero"]["imagem_desktop"]}-1280.webp">' if dom else ""
    canon = f'<link rel="canonical" href="{dom}/">' if dom else ""
    robots = "" if dom else '<meta name="robots" content="noindex">'
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(seo['titulo'])}</title>
<meta name="description" content="{e(seo['descricao'])}">
<meta name="theme-color" content="#09060f">
{robots}{canon}
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{e(seo['titulo'])}">
<meta property="og:description" content="{e(seo['descricao'])}">
{og}
<link rel="icon" type="image/png" href="img/favicon.png">
<link rel="preload" as="image" href="img/{CT['hero']['imagem_mobile']}-800.webp" media="(max-width: 759px)">
<link rel="preload" as="font" type="font/woff2" href="fonts/barlow-condensed-800.woff2" crossorigin>
<link rel="stylesheet" href="css/style.css?v={versao("css/style.css")}">
{jsonld()}
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
{header()}
<main id="conteudo">
{hero()}
{empresa()}
<div id="atracoes">{robos()}{estrutura()}{experiencias()}</div>
{eventos()}
{galeria()}
{prova()}
{passos()}
{faq()}
{cta_final()}
</main>
{rodape()}
<script src="js/main.js?v={versao("js/main.js")}" defer></script>
</body>
</html>
"""


def pendencias():
    p = []
    if not NUMERO:
        p.append("WhatsApp: preencher data/config.json -> whatsapp_numero (botões apontam para #contato até lá)")
    if not CFG["instagram_confirmado"]:
        p.append("Instagram: confirmar o link e marcar instagram_confirmado")
    if not CFG["dominio"].strip():
        p.append("Domínio: preencher 'dominio' (canonical, Open Graph, sitemap e dados estruturados; sem ele o site sai com noindex)")
    if not CFG.get("hero_video", "").strip():
        p.append("Vídeo do hero: colocar o MP4 em static/video/ e informar em config.json -> hero_video")
    if REVISAO:
        p.append("modo_revisao está true: mudar para false antes de publicar")
    p += [
        "Confirmar origem/autorização das imagens e se os robôs verde e vermelho (LEDs) existem",
        "Robô amarelo lembra personagem licenciado (Transformers): validar uso comercial",
        "DJ: autorização de uso de imagem",
        "Casamentos.com.br: confirmar uso do selo e das avaliações",
        "Sem fotos reais: sonorização, CO₂ e drone",
    ]
    return p


def main():
    DIST.mkdir(exist_ok=True)
    for item in DIST.iterdir():  # limpa o conteúdo sem apagar a pasta (servidores locais continuam válidos)
        shutil.rmtree(item) if item.is_dir() else item.unlink()
    shutil.copytree(RAIZ / "static", DIST, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".gitkeep", ".DS_Store"))
    (DIST / "index.html").write_text(pagina(), encoding="utf-8")
    dom = CFG["dominio"].strip().rstrip("/")
    if dom:
        (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {dom}/sitemap.xml\n", encoding="utf-8")
        (DIST / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"<url><loc>{dom}/</loc></url></urlset>\n", encoding="utf-8")
    print(f"OK: build gerado em {DIST}")
    print("\nPENDÊNCIAS ANTES DE PUBLICAR:")
    for x in pendencias():
        print(f"  - {x}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

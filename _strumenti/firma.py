#!/usr/bin/env python3
"""Aggiunge firma, licenza e caratteri incorporati a un gioco HTML di Lettere in gioco.

Uso: python3 _strumenti/firma.py ingresso.html uscita.html "Titolo del gioco"

- toglie i caratteri caricati da Google Fonts e li incorpora nel file (niente richieste
  esterne: funziona offline ed è coerente con la pagina Privacy del sito);
- aggiunge commento di licenza e meta autore/copyright;
- aggiunge una riga di firma in fondo alla pagina (quarto argomento facoltativo: CSS extra,
  per esempio per ridurre di 22px l'altezza di un gioco a tutto schermo);
- aggiunge la sezione "Crediti e licenza" in fondo alla Guida per chi insegna, se c'è.
"""
import base64, re, sys
from pathlib import Path

ANNO = 2026
SITO = "https://lettereingioco.it"
LICENZA = "https://creativecommons.org/licenses/by-nc-sa/4.0/deed.it"
FONT_DIR = Path(__file__).resolve().parent / "font-giochi"
FONT = {  # famiglia CSS -> [(file, peso, stile)]
    "Grenze Gotisch": [("grenze-gotisch-latin-500-normal", 500, "normal"), ("grenze-gotisch-latin-700-normal", 700, "normal")],
    "Alegreya": [("alegreya-latin-400-normal", 400, "normal"), ("alegreya-latin-600-normal", 600, "normal"), ("alegreya-latin-400-italic", 400, "italic")],
    "DM Serif Display": [("dm-serif-display-latin-400-normal", 400, "normal"), ("dm-serif-display-latin-400-italic", 400, "italic")],
    "Special Elite": [("special-elite-latin-400-normal", 400, "normal")],
    "Atkinson Hyperlegible": [("atkinson-hyperlegible-latin-400-normal", 400, "normal"), ("atkinson-hyperlegible-latin-700-normal", 700, "normal"), ("atkinson-hyperlegible-latin-400-italic", 400, "italic")],
}

CREDITI = f"""<h3>Crediti e licenza</h3>
  <p>Gioco ideato da Giorgio Guerra e realizzato con l'aiuto di Claude (Anthropic). Licenza <a href="{LICENZA}" target="_blank" rel="noopener">CC BY-NC-SA 4.0</a>: si può usare e adattare citando l'autore, senza scopi commerciali, condividendo le modifiche con la stessa licenza. Altri giochi gratuiti su <a href="{SITO}" target="_blank" rel="noopener">lettereingioco.it</a>.</p>
  """

FIRMA_CSS = """
.lig-firma{text-align:center;font:12px/22px "Atkinson Hyperlegible",system-ui,sans-serif;height:22px;padding:0 8px;background:#f4f4f0;color:#2b2b2b;border-top:1px solid rgba(0,0,0,.12);overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
.lig-firma a{color:inherit}
"""


def font_face(html):
    usati = [f for f in FONT if f in html]
    regole = []
    for fam in usati:
        for nome, peso, stile in FONT[fam]:
            dati = base64.b64encode((FONT_DIR / f"{nome}.woff2").read_bytes()).decode()
            regole.append(f'@font-face{{font-family:"{fam}";font-style:{stile};font-weight:{peso};font-display:swap;src:url(data:font/woff2;base64,{dati}) format("woff2")}}')
    return "\n".join(regole), usati


def firma(html, titolo, extra_css=""):
    # 1. via Google Fonts
    html = re.sub(r'<link[^>]+fonts\.(googleapis|gstatic)\.com[^>]*>\s*', "", html)
    ff, usati = font_face(html)
    # 2. commento e meta subito dopo <head>
    testa = (f'<!-- "{titolo}" · ideato da Giorgio Guerra · Lettere in gioco · {SITO}\n'
             f'     Licenza CC BY-NC-SA 4.0 · {LICENZA} -->\n'
             f'<meta name="author" content="Giorgio Guerra">\n'
             f'<meta name="copyright" content="© {ANNO} Giorgio Guerra · CC BY-NC-SA 4.0">\n'
             f'<style>{ff}\n{FIRMA_CSS}</style>\n')
    html = re.sub(r"<head>", "<head>\n" + testa, html, count=1)
    # 3. riga di firma: in fondo alla pagina, nel flusso normale (non copre i comandi del gioco) prima di </body> (o in fondo)
    riga = (f'<div class="lig-firma">© {ANNO} Giorgio Guerra · '
            f'<a href="{LICENZA}" target="_blank" rel="noopener">CC BY-NC-SA 4.0</a> · '
            f'<a href="{SITO}" target="_blank" rel="noopener">lettereingioco.it</a></div>\n')
    if extra_css:  # in fondo, dopo gli stili del gioco, così può correggerli
        riga += f"<style>{extra_css}</style>\n"
    if "</body>" in html:
        i = html.rfind("</body>"); html = html[:i] + riga + html[i:]
    else:
        html += riga
    # 4. crediti in fondo alla guida per chi insegna
    m = re.search(r'<h2 id="h[^"]*">Guida per chi insegna</h2>', html)
    if m:
        fine = html.find("</div></div>", m.end())
        if fine > 0:
            html = html[:fine] + CREDITI + html[fine:]
    return html, usati


if __name__ == "__main__":
    ingresso, uscita, titolo = sys.argv[1], sys.argv[2], sys.argv[3]
    extra = sys.argv[4] if len(sys.argv) > 4 else ""  # CSS facoltativo, es. per giochi a tutta altezza
    html = Path(ingresso).read_text(encoding="utf-8")
    html, usati = firma(html, titolo, extra)
    Path(uscita).parent.mkdir(parents=True, exist_ok=True)
    Path(uscita).write_text(html, encoding="utf-8")
    print(f"{uscita}: firmato, caratteri incorporati: {', '.join(usati) or 'nessuno'}")

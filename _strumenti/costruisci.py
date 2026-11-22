#!/usr/bin/env python3
"""Genera le pagine del sito Lettere in gioco a partire da giochi.json.

Uso:  python3 _strumenti/costruisci.py
Per aggiungere un gioco: una voce in giochi.json, il file HTML in giochi/<slug>/gioco.html
e "stato": "pronto". Poi si rilancia lo script.
"""
import json
from html import escape
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
GIOCHI = json.loads((RADICE / "_strumenti" / "giochi.json").read_text(encoding="utf-8"))
ANNO = 2026
DISCIPLINE = ["Storia", "Italiano", "Geografia"]
EMAIL_CONTATTO = ""  # da inserire: indirizzo personale per i contatti
NEWSLETTER = "https://lettereingioco.substack.com/subscribe"
LICENZA_URL = "https://creativecommons.org/licenses/by-nc-sa/4.0/deed.it"

OCA = ('<svg class="oca" viewBox="0 0 40 32" aria-hidden="true"><path fill="currentColor" '
       'd="M3 22c0-4 4-7 10-7h9c3 0 5-2 5-5V7c0-3 2-5 5-5 2 0 4 1 4 3l3 1-3 2v5c0 9-5 15-14 15H9c-3 0-6-2-6-6z"/></svg>')
MARCHIO = ('<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="4" y="4" width="26" height="26" rx="5" fill="#1e4636"/>'
           '<rect x="1.5" y="1.5" width="26" height="26" rx="5" fill="#8cc084" stroke="#1e4636" stroke-width="2.5"/>'
           '<text x="14.5" y="22.5" text-anchor="middle" font-family="Young Serif, Georgia, serif" font-size="19" fill="#1e4636">L</text></svg>')


def pronto(g):
    return g.get("stato") == "pronto"


def pagina(titolo, descrizione, corpo, livello=0, attivo=""):
    r = "../" * livello
    def voce(href, nome, chiave):
        cur = ' aria-current="page"' if chiave == attivo else ""
        return f'<li><a href="{r}{href}"{cur}>{nome}</a></li>'
    titolo_completo = "Lettere in gioco" if not titolo else f"{titolo} | Lettere in gioco"
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titolo_completo)}</title>
<meta name="description" content="{escape(descrizione)}">
<meta name="author" content="Giorgio Guerra">
<link rel="icon" href="{r}assets/icona.svg" type="image/svg+xml">
<link rel="preload" href="{r}assets/fonts/young-serif-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{r}assets/stile.css">
</head>
<body>
<a class="salta" href="#principale">Vai al contenuto</a>
<header class="testata">
  <div class="contenitore">
    <a class="marchio" href="{r}index.html">{MARCHIO}Lettere in gioco</a>
    <nav aria-label="Menu principale"><ul class="menu">
      {voce("index.html#giochi", "Giochi", "giochi")}
      {voce("index.html#in-classe", "In classe", "")}
      {voce("chi-sono/index.html", "Chi sono", "chi-sono")}
    </ul></nav>
  </div>
</header>
<main id="principale">
{corpo}
</main>
<footer class="piede">
  <div class="contenitore">
    <p>© {ANNO} Giorgio Guerra. Giochi e testi con licenza <a href="{LICENZA_URL}" target="_blank" rel="noopener">CC BY-NC-SA 4.0</a>: si possono usare e adattare citando l'autore, senza scopi commerciali.</p>
    <ul>
      <li><a href="{r}chi-sono/index.html">Chi sono</a></li>
      <li><a href="{r}privacy/index.html">Privacy</a></li>
      <li><a href="{NEWSLETTER}" target="_blank" rel="noopener">Newsletter</a></li>
      <li><a href="https://www.youtube.com/@lettereingioco" target="_blank" rel="noopener">YouTube</a></li>
      <li><a href="https://www.instagram.com/lettereingioco/" target="_blank" rel="noopener">Instagram</a></li>
      <li><a href="https://www.facebook.com/lettereingioco" target="_blank" rel="noopener">Facebook</a></li>
    </ul>
  </div>
</footer>
</body>
</html>
"""


def dati_gioco(g):
    parti = [f'<span class="disciplina">{escape(g["disciplina"])}</span>', f'classe {escape(g["classe"])}']
    if g.get("durata"):
        parti.append(escape(g["durata"].split(",")[0]))
    return ", ".join(parti)


def tabellone():
    caselle = []
    for i in range(15):
        n = i + 1
        riga, col = i // 5 + 1, (i % 5) + 1 if (i // 5) % 2 == 0 else 5 - (i % 5)
        pos = f'style="--r:{riga};--c:{col}"'
        if i < len(GIOCHI) and i < 14:
            g = GIOCHI[i]
            caselle.append(f'<li class="casella gioco" {pos}><span class="numero">{n}</span>'
                           f'<a href="giochi/{g["slug"]}/index.html">{escape(g["titolo"])}</a></li>')
        elif n == 15:
            caselle.append(f'<li class="casella arrivo" {pos}><span class="numero">{n}</span><span>e poi altre caselle</span></li>')
        else:
            oca = OCA if n in (5, 9, 14) else ""
            caselle.append(f'<li class="casella libera" {pos} aria-hidden="true"><span class="numero">{n}</span>{oca}</li>')
    return ('<figure class="tabellone"><ol class="caselle" aria-label="I giochi pubblicati">'
            + "".join(caselle)
            + '</ol><figcaption>Ogni casella è un gioco. Ne arriva uno nuovo ogni settimana.</figcaption></figure>')


def scheda_catalogo(g):
    stato = '' if pronto(g) else '<span class="stato">In arrivo</span>'
    return f"""<li class="scheda" data-disciplina="{escape(g["disciplina"])}">
  <h3><a href="giochi/{g["slug"]}/index.html">{escape(g["titolo"])}</a>{stato}</h3>
  <p class="dati">{dati_gioco(g)}. {escape(g["argomento"])}.</p>
  <p>{escape(g["sintesi"])}</p>
  <a class="pulsante secondario" href="giochi/{g["slug"]}/index.html">Apri la scheda del gioco</a>
</li>"""


def home():
    filtri = '<button type="button" class="filtro" aria-pressed="true" data-filtro="tutti">Tutti</button>' + "".join(
        f'<button type="button" class="filtro" aria-pressed="false" data-filtro="{d}">{d}</button>' for d in DISCIPLINE)
    corpo = f"""
<section class="apertura">
  <div class="contenitore">
    <div>
      <h1>Giochi per l'ora di Lettere, pronti da portare in classe</h1>
      <p class="sottotitolo">Avventure di storia, dialoghi con gli autori, indagini sui generi letterari. Sono gratuiti, si giocano nel browser oppure si scaricano per Google Classroom e funzionano anche senza connessione.</p>
      <p>Li progetta Giorgio Guerra, docente di Lettere e formatore, con l'aiuto dell'intelligenza artificiale e una revisione didattica di ogni scena.</p>
      <div class="azioni">
        <a class="pulsante" href="#giochi">Sfoglia i giochi</a>
        <a class="pulsante secondario" href="#in-classe">Come si usano in classe</a>
      </div>
    </div>
    {tabellone()}
  </div>
</section>

<section class="sezione" id="giochi" aria-labelledby="titolo-giochi">
  <div class="contenitore">
    <div class="intro">
      <h2 id="titolo-giochi">I giochi</h2>
      <p>Ogni gioco ha una scheda didattica con classe, obiettivi, durata e modalità di valutazione.</p>
    </div>
    <fieldset class="filtri">
      <legend>Mostra i giochi di</legend>
      {filtri}
    </fieldset>
    <ul class="schede">
      {"".join(scheda_catalogo(g) for g in GIOCHI)}
    </ul>
    <p class="vuoto" id="nessun-gioco" hidden>Il primo gioco di questa disciplina è in preparazione.</p>
  </div>
</section>

<section class="sezione" id="in-classe" aria-labelledby="titolo-classe">
  <div class="contenitore">
    <div class="intro">
      <h2 id="titolo-classe">Come si usano in classe</h2>
      <p>Bastano una LIM o un computer ogni due persone. Una partita dura in genere una lezione, e si può dividere in due.</p>
    </div>
    <ol class="passi">
      <li><h3>Scegli il gioco</h3><p>Leggi la scheda didattica e prova la prima scena da sola o da solo: bastano cinque minuti.</p></li>
      <li><h3>Organizza la classe</h3><p>Funziona bene a coppie, con due ruoli: chi legge e chi decide. In alternativa si gioca tutti insieme alla LIM.</p></li>
      <li><h3>Chiudi con il punteggio</h3><p>La schermata finale dà un punteggio su base 50 con tre livelli e indica le pagine del manuale da ripassare.</p></li>
    </ol>
  </div>
</section>

<section class="newsletter" aria-labelledby="titolo-newsletter">
  <div class="contenitore">
    <h2 id="titolo-newsletter">Un gioco nuovo ogni settimana</h2>
    <p>Con la newsletter della domenica ricevi il gioco della settimana, un'idea per usarlo in classe e il prompt con cui è nato. La prima uscita è il 17 gennaio 2027.</p>
    <a class="pulsante" href="{NEWSLETTER}" target="_blank" rel="noopener">Iscriviti alla newsletter</a>
  </div>
</section>

<script>
(function () {{
  var bottoni = document.querySelectorAll('.filtro');
  var schede = document.querySelectorAll('.scheda');
  var vuoto = document.getElementById('nessun-gioco');
  bottoni.forEach(function (b) {{
    b.addEventListener('click', function () {{
      var f = b.getAttribute('data-filtro'), visibili = 0;
      bottoni.forEach(function (x) {{ x.setAttribute('aria-pressed', String(x === b)); }});
      schede.forEach(function (s) {{
        var mostra = f === 'tutti' || s.getAttribute('data-disciplina') === f;
        s.hidden = !mostra; if (mostra) visibili++;
      }});
      vuoto.hidden = visibili > 0;
    }});
  }});
}})();
</script>
"""
    return pagina("", "Giochi didattici gratuiti per italiano, storia e geografia nella scuola secondaria di primo grado, pronti da usare in classe o su Google Classroom.", corpo, 0, "giochi")


def pagina_gioco(g):
    def lista(v):
        return "<ul>" + "".join(f"<li>{escape(x)}</li>" for x in v) + "</ul>"
    righe = [("Disciplina", escape(g["disciplina"])), ("Classe", escape(g["classe"])),
             ("Argomento", escape(g["argomento"])), ("Tipo di gioco", escape(g["genere"]))]
    if g.get("durata"):
        righe.append(("Durata", escape(g["durata"])))
    righe += [("Che cosa si fa", lista(g["attivita"])), ("Obiettivi", lista(g["obiettivi"]))]
    if g.get("valutazione"):
        righe.append(("Valutazione", escape(g["valutazione"])))
    scheda = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in righe)
    if pronto(g):
        azioni = (f'<a class="pulsante" href="gioco.html">Gioca nel browser</a>'
                  f'<a class="pulsante secondario" href="gioco.html" download="{g["slug"]}.html">Scarica per Classroom</a>')
        nota = '<p class="nota">Il file scaricato si carica su Google Classroom come allegato e funziona anche senza connessione.</p>'
    else:
        azioni = ('<span class="pulsante" aria-disabled="true">Gioca nel browser</span>'
                  '<span class="pulsante secondario" aria-disabled="true">Scarica per Classroom</span>')
        nota = '<p class="nota">Il gioco è in preparazione e sarà disponibile a breve.</p>'
    corpo = f"""
<article class="pagina">
  <div class="contenitore contenuto">
    <p class="briciole"><a href="../../index.html#giochi">Tutti i giochi</a></p>
    <h1>{escape(g["titolo"])}</h1>
    <p class="dati">{dati_gioco(g)}. {escape(g["argomento"])}.</p>
    <p class="sottotitolo">{escape(g["sintesi"])}</p>
    <div class="azioni">{azioni}</div>
    {nota}
    <h2>Scheda didattica</h2>
    <dl class="scheda-didattica">{scheda}</dl>
    <h2>Licenza</h2>
    <p>Gioco ideato da Giorgio Guerra e realizzato con l'aiuto di Claude (Anthropic). Licenza <a href="{LICENZA_URL}" target="_blank" rel="noopener">CC BY-NC-SA 4.0</a>: puoi usarlo e adattarlo citando l'autore, senza scopi commerciali, condividendo le modifiche con la stessa licenza.</p>
  </div>
</article>
"""
    return pagina(g["titolo"], g["sintesi"], corpo, 2, "giochi")


def chi_sono():
    contatto = (f'<p>Per proposte di formazione o collaborazioni scrivi a <a href="mailto:{EMAIL_CONTATTO}">{EMAIL_CONTATTO}</a>.</p>'
                if EMAIL_CONTATTO else '<p>Per proposte di formazione o collaborazioni: indirizzo email in arrivo.</p>')
    corpo = f"""
<article class="pagina">
  <div class="contenitore contenuto">
    <h1>Chi sono</h1>
    <p class="sottotitolo">Sono Giorgio Guerra, insegno Lettere nella scuola secondaria di primo grado e da oltre dieci anni mi occupo di formazione docenti.</p>
    <p>Lavoro con gli ambiti territoriali e gli Uffici scolastici di Lombardia e Liguria, e insegno nei percorsi abilitanti per docenti dell'Università Cattolica di Brescia. Mi occupo di didattica per competenze, gestione della classe e uso delle nuove tecnologie, compresa l'intelligenza artificiale.</p>
    <p>Sono autore della grammatica <i>Siamo parole</i>, sono stato autore di prove INVALSI e collaboro con l'editoria scolastica per i manuali di italiano e geografia.</p>
    <h2>Come nascono i giochi</h2>
    <p>Ogni gioco parte da un argomento del programma e da un obiettivo preciso. L'intelligenza artificiale mi aiuta a scrivere il codice, le scene e i personaggi; io progetto la struttura didattica, verifico date e fatti e controllo che ogni attività si possa risolvere con quello che la classe ha trovato giocando.</p>
    <p>Quando chi gioca sbaglia, la storia prosegue comunque come è andata davvero: la spiegazione dell'errore è il momento in cui si impara.</p>
    <h2>Formazione</h2>
    <p>Propongo percorsi per scuole, reti e ambiti sull'uso didattico e consapevole dell'intelligenza artificiale nell'insegnamento di Lettere, con i giochi come esempi da smontare e rifare.</p>
    {contatto}
  </div>
</article>
"""
    return pagina("Chi sono", "Giorgio Guerra, docente di Lettere e formatore: chi progetta i giochi di Lettere in gioco e come nascono.", corpo, 1, "chi-sono")


def privacy():
    titolare = f" Per qualunque richiesta puoi scrivere a {EMAIL_CONTATTO}." if EMAIL_CONTATTO else ""
    corpo = f"""
<article class="pagina">
  <div class="contenitore contenuto">
    <h1>Privacy</h1>
    <p class="sottotitolo">Questo sito non usa cookie, non traccia le visite e non raccoglie direttamente dati personali.</p>
    <h2>Titolare</h2>
    <p>Il sito è curato da Giorgio Guerra.{titolare}</p>
    <h2>Cookie e statistiche</h2>
    <p>Il sito non installa cookie e non usa strumenti di statistica o di pubblicità. I caratteri tipografici sono ospitati sul sito stesso, senza richieste a servizi esterni.</p>
    <h2>Ospitalità del sito</h2>
    <p>Il sito è pubblicato tramite GitHub Pages, servizio di GitHub, Inc. Come ogni server, GitHub può registrare l'indirizzo IP di chi visita il sito per ragioni di sicurezza e funzionamento. I dettagli sono nella <a href="https://docs.github.com/it/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener">informativa sulla privacy di GitHub</a>.</p>
    <h2>I giochi</h2>
    <p>I giochi non chiedono nomi né account. Alcuni salvano i progressi della partita nella memoria del browser, solo sul dispositivo in uso: nessun dato viene inviato al sito. Per cancellarli basta il pulsante "Nuova partita" o la pulizia dei dati del browser.</p>
    <h2>Newsletter</h2>
    <p>La newsletter è gestita con Substack, servizio di Substack, Inc. L'iscrizione avviene sul sito di Substack, a cui il pulsante "Iscriviti alla newsletter" rimanda: questo sito non raccoglie direttamente nessun indirizzo.</p>
    <p>Per iscriversi basta l'indirizzo email, che serve solo per inviare la newsletter. Ogni email contiene il link per cancellarsi in qualunque momento. Il trattamento dei dati da parte di Substack è descritto nella sua <a href="https://substack.com/privacy" target="_blank" rel="noopener">informativa sulla privacy</a>.</p>
    <p class="nota">Ultimo aggiornamento: novembre 2026.</p>
  </div>
</article>
"""
    return pagina("Privacy", "Informativa sulla privacy del sito Lettere in gioco.", corpo, 1)


def non_trovata():
    corpo = """
<article class="pagina">
  <div class="contenitore contenuto">
    <h1>Questa casella è vuota</h1>
    <p>La pagina che cerchi non esiste o è stata spostata.</p>
    <p><a class="pulsante" href="/index.html">Torna ai giochi</a></p>
  </div>
</article>
"""
    return pagina("Pagina non trovata", "Pagina non trovata.", corpo, 0)


def scrivi(percorso, testo):
    p = RADICE / percorso
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(testo, encoding="utf-8")


if __name__ == "__main__":
    scrivi("index.html", home())
    for g in GIOCHI:
        scrivi(f"giochi/{g['slug']}/index.html", pagina_gioco(g))
    scrivi("chi-sono/index.html", chi_sono())
    scrivi("privacy/index.html", privacy())
    scrivi("404.html", non_trovata())
    (RADICE / "assets" / "icona.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30">' + MARCHIO.split(">", 1)[1].rsplit("</svg>", 1)[0] + "</svg>",
        encoding="utf-8")
    print(f"Pagine generate: {len(GIOCHI)} giochi + home, chi sono, privacy, 404")

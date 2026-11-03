#!/usr/bin/env python3
"""Generate site/en/index.html and site/it/index.html from the Slovenian source.

site/index.html (Slovenian) is the only file to edit. After any text change there,
run:  python3 tools/build_i18n.py

Strings are replaced only where they are a whole unit: a text node, an attribute
value or a JS string literal. Every Slovenian key must be found, otherwise the build
stops, so new or edited copy can't silently stay untranslated.
Product names (Korec gladek, Kraški korec, Go pro, ...) are brand names and stay as they are.
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site" / "index.html"

# Slovenian -> (English, Italian)
T = {
    # meta + navigation
    "Opečna kritina in zidni elementi iz spodnje Vipavske doline. Od 1948.": (
        "Clay roof tiles and masonry blocks from the lower Vipava Valley. Since 1948.",
        "Coppi in laterizio ed elementi murari dalla bassa valle del Vipacco. Dal 1948."),
    "Goriške opekarne — domov": ("Goriške opekarne — home", "Goriške opekarne — home"),
    "Glavna navigacija": ("Main navigation", "Navigazione principale"),
    "Izdelki": ("Products", "Prodotti"),
    "Zgodba": ("Story", "Storia"),
    "Reference": ("References", "Referenze"),
    "Novice": ("News", "Notizie"),
    "Katalogi": ("Catalogues", "Cataloghi"),
    "Prodajna mesta": ("Dealers", "Rivenditori"),
    "Povleci": ("Drag", "Trascina"),
    "Sonce": ("Sun", "Sole"),

    # hero + statement
    "Lepa na pogled, preizkušeno dobra.": ("Beautiful to look at, proven to last.", "Bella da vedere, collaudata nel tempo."),
    "Lepa na pogled,": ("Beautiful to look at,", "Bella da vedere,"),
    "preizkušeno": ("proven", "collaudata"),
    "dobra.": ("to last.", "nel tempo."),
    "Iz gline spodnje Vipavske doline, kjer se opeka žge že od rimskih časov.": (
        "From the clay of the lower Vipava Valley, where bricks have been fired since Roman times.",
        "Dall'argilla della bassa valle del Vipacco, dove i laterizi si cuociono fin dall'epoca romana."),
    "Peta fasada": ("The fifth façade", "La quinta facciata"),
    "— o strehi": ("— on the roof", "— sul tetto"),
    "Vsaki hiši je treba dati peto fasado: streho. Ta jo dokončno umesti v prostor. Zato jo že več kot sedemdeset let žgemo iz iste zemlje, ki obdaja vaš dom.": (
        "Every house needs a fifth façade: its roof. It is what finally settles a home into its landscape. That is why, for more than seventy years, we have fired it from the same earth that surrounds your home.",
        "Ogni casa ha bisogno di una quinta facciata: il tetto. È lui a inserirla davvero nel paesaggio. Per questo da oltre settant'anni lo cuociamo dalla stessa terra che circonda la vostra casa."),

    # history
    "Zgodovina opekarstva na Goriškem": ("A history of brickmaking in the Goriška region", "Storia dei laterizi nel Goriziano"),
    "Dva tisoč let ognja": ("Two thousand years of fire", "Duemila anni di fuoco"),
    "Plasti gline v nahajališču spodnje Vipavske doline": ("Clay layers in a pit in the lower Vipava Valley", "Strati di argilla in una cava della bassa valle del Vipacco"),
    "Korci se sušijo na lesenih policah v opekarni": ("Canal tiles drying on wooden racks in the brickworks", "Coppi che asciugano su scaffali di legno nella fornace"),
    "Roke, ki oblikujejo glino": ("Hands shaping clay", "Mani che modellano l'argilla"),
    "Korci v žareči opekarski peči": ("Canal tiles in a glowing kiln", "Coppi in un forno incandescente"),
    "Prekrivajoči se opečni korci": ("Overlapping clay canal tiles", "Coppi in laterizio sovrapposti"),
    "Sodobna hiša na Krasu s streho iz korcev": ("A modern Karst house with a canal-tile roof", "Una casa moderna sul Carso con tetto in coppi"),
    "Obdobja": ("Eras", "Epoche"),
    "Pri pečeh": ("At the kilns", "Presso le fornaci"),
    "Rimsko obdobje": ("Roman era", "Epoca romana"),
    "Na rimski cesti iz Akvileje v Emono je bila tretja postaja imenovana Ad fornulus — Pri pečeh. Nekje med Biljami in Bukovico.": (
        "On the Roman road from Aquileia to Emona, the third station was called Ad fornulus — “at the kilns”. Somewhere between Bilje and Bukovica.",
        "Sulla strada romana da Aquileia a Emona, la terza stazione si chiamava Ad fornulus — “presso le fornaci”. Da qualche parte tra Bilje e Bukovica."),
    "15. st.": ("15th c.", "XV sec."),
    "15. stoletje": ("15th century", "XV secolo"),
    "Ponovni razcvet": ("A new flowering", "Una nuova rinascita"),
    "Po razpadu rimskega imperija opekarstvo upade, v 15. stoletju pa znova oživi. Industrijska revolucija potrdi vsestranskost opeke.": (
        "Brickmaking declined after the fall of the Roman Empire and revived in the 15th century. The Industrial Revolution confirmed how versatile brick could be.",
        "Dopo la caduta dell'Impero romano la produzione di laterizi declina e rinasce nel XV secolo. La rivoluzione industriale ne conferma la versatilità."),
    "Avstro-Ogrska": ("Austria-Hungary", "Austria-Ungheria"),
    "Opekarn na Goriškem": ("Brickworks in the Goriška region", "Fornaci nel Goriziano"),
    "V času monarhije na tem območju deluje 47 opekarskih obratov.": (
        "Under the monarchy, 47 brickworks operate in the area.",
        "Sotto la monarchia, nella zona operano 47 fornaci."),
    "Prva ljudska opekarna": ("The first people's brickworks", "La prima fornace popolare"),
    "V Biljah začne delovati prva ljudska opekarna z 41 sovlagatelji. Žganje se preseli iz poljskih peči v hrovatinke in nato v Hoffmannove krožne peči.": (
        "The first people's brickworks opens in Bilje with 41 co-investors. Firing moves from field kilns to Croatian-style kilns and then to Hoffmann ring kilns.",
        "A Bilje apre la prima fornace popolare con 41 soci. La cottura passa dai forni da campo ai forni di tipo croato e poi ai forni anulari Hoffmann."),
    "Ustanovitev": ("Founded", "Fondazione"),
    "Odločba vlade LRS združi opekarne v Renčah, Biljah, Vrtojbi, Bukovici in Dombravi v eno podjetje.": (
        "A decision of the government of the People's Republic of Slovenia unites the brickworks in Renče, Bilje, Vrtojba, Bukovica and Dombrava into one company.",
        "Una decisione del governo della Repubblica Popolare di Slovenia riunisce le fornaci di Renče, Bilje, Vrtojba, Bukovica e Dombrava in un'unica azienda."),
    "Danes": ("Today", "Oggi"),
    "Ista glina, nov čas": ("The same clay, a new age", "La stessa argilla, un tempo nuovo"),
    "Sodobna proizvodnja korcev, strešnikov in opečnih blokov — za hiše, ki bodo stale stoletje.": (
        "Modern production of canal tiles, roof tiles and clay blocks — for houses built to stand for a century.",
        "Produzione moderna di coppi, tegole e blocchi in laterizio — per case che dureranno un secolo."),

    # firing
    "Korci na lesenih policah: sveža, mokra siva glina": ("Canal tiles on wooden racks: fresh, wet grey clay", "Coppi su scaffali di legno: argilla grigia, fresca e umida"),
    "Glina": ("Clay", "Argilla"),
    "Iz nahajališč spodnje Vipavske doline — iste plasti, ki so jih uporabljali že Rimljani.": (
        "From the pits of the lower Vipava Valley — the same layers the Romans used.",
        "Dalle cave della bassa valle del Vipacco — gli stessi strati usati dai Romani."),
    "Oblikovanje": ("Shaping", "Formatura"),
    "Stiskanje in počasno sušenje. Vsak korec dobi svojo krivino.": (
        "Pressing and slow drying. Every tile takes on its own curve.",
        "Pressatura ed essiccazione lenta. Ogni coppo prende la sua curva."),
    "Žganje": ("Firing", "Cottura"),
    "Pri približno tisoč stopinjah glina postane opeka — trda, zračna in obstojna.": (
        "At around a thousand degrees, clay becomes brick — hard, breathable and durable.",
        "A circa mille gradi l'argilla diventa laterizio — duro, traspirante e resistente."),
    "Streha": ("Roof", "Tetto"),
    "Desetletja varuje dom pred burjo, soncem in dežjem.": (
        "For decades it shields the home from the bora wind, sun and rain.",
        "Per decenni protegge la casa da bora, sole e pioggia."),

    # products
    "Dve družini, en material. Opeka, ki diha, hrani toploto in se stara lepo.": (
        "Two families, one material. Clay that breathes, holds warmth and ages beautifully.",
        "Due famiglie, un solo materiale. Laterizio che respira, trattiene il calore e invecchia con eleganza."),
    "Opečna kritina": ("Clay roofing", "Coperture in laterizio"),
    "Opečni zidni elementi": ("Clay masonry blocks", "Elementi murari in laterizio"),
    "Korci": ("Canal tiles", "Coppi"),
    "4 modeli": ("4 models", "4 modelli"),
    "Barvani korci": ("Coloured canal tiles", "Coppi colorati"),
    "7 tonov": ("7 shades", "7 tonalità"),
    "Strešniki": ("Roof tiles", "Tegole"),
    "Dodatni elementi": ("Accessories", "Accessori"),
    "Sleme & prezračevanje": ("Ridge & ventilation", "Colmo e ventilazione"),
    "Brušena opeka": ("Ground brick", "Laterizio rettificato"),
    "Termo bloki": ("Thermal blocks", "Blocchi termici"),
    "Pregradni": ("Partition", "Divisori"),
    "Več o izdelku": ("More about this product", "Scopri il prodotto"),
    "Korec gladek, korec s črto, reliefni korec in korec z nosom — naravna žgana glina.": (
        "Korec gladek, Korec s črto, Reliefni korec and Korec z nosom — natural fired clay.",
        "Korec gladek, Korec s črto, Reliefni korec e Korec z nosom — argilla cotta naturale."),
    "Antični, francoski, istrski, korintos, kraški, primorski in soški — barve krajev, iz katerih prihajajo.": (
        "Antični, Francoski, Istrski, Korintos, Kraški, Primorski and Soški — the colours of the places they come from.",
        "Antični, Francoski, Istrski, Korintos, Kraški, Primorski e Soški — i colori dei luoghi da cui provengono."),
    "Strešnik Alpe Jadran in široki strešnik Alpe Jadran za hitrejše polaganje.": (
        "Alpe Jadran roof tile and the wide Alpe Jadran roof tile for faster laying.",
        "Tegola Alpe Jadran e tegola Alpe Jadran larga per una posa più rapida."),
    "Slemenjaki, prezračevalni korec in zaključni elementi — streha do zadnjega detajla.": (
        "Ridge tiles, ventilation tiles and finishing pieces — a roof down to the last detail.",
        "Colmi, coppi di ventilazione ed elementi di finitura — il tetto fino all'ultimo dettaglio."),
    "Brušena opeka za suho gradnjo z lepilom. Debeline 29, 25, 19, 15 in 11,5 cm.": (
        "Ground brick for thin-joint construction with adhesive. Thicknesses of 29, 25, 19, 15 and 11.5 cm.",
        "Laterizio rettificato per posa a colla. Spessori 29, 25, 19, 15 e 11,5 cm."),
    "Termo bloki za nosilne zunanje stene. Go term 25 in 29.": (
        "Thermal blocks for load-bearing exterior walls. Go term 25 and 29.",
        "Blocchi termici per pareti esterne portanti. Go term 25 e 29."),
    "Kompaktni bloki za hitro zidanje. Go mini 25 in 29.": (
        "Compact blocks for fast bricklaying. Go mini 25 and 29.",
        "Blocchi compatti per una muratura rapida. Go mini 25 e 29."),
    "Nenosilni pregradni elementi od 8 do 19 cm za notranje stene.": (
        "Non-load-bearing partition blocks from 8 to 19 cm for interior walls.",
        "Elementi divisori non portanti da 8 a 19 cm per pareti interne."),
    "Modularni blok Go modul 29-19 za natančno zidanje v modulu.": (
        "The Go modul 29-19 modular block for precise modular bricklaying.",
        "Blocco modulare Go modul 29-19 per una muratura modulare precisa."),

    # configurator
    "Premikajte miško — sonce čez streho": ("Move your mouse — sun across the roof", "Muovete il mouse — il sole sul tetto"),
    "Kraški korec — izdelek": ("Kraški korec — product", "Kraški korec — prodotto"),
    "Barvani korec": ("Coloured canal tile", "Coppo colorato"),
    "Naravni korec": ("Natural canal tile", "Coppo naturale"),
    "Preizkusite streho": ("Try a roof", "Provate il tetto"),
    "Vaša streha,": ("Your roof,", "Il vostro tetto,"),
    "pod vašim soncem.": ("under your sun.", "sotto il vostro sole."),
    "Deset korcev iz naše proizvodnje. Izberite enega in poglejte, kako zaživi na strehi.": (
        "Ten canal tiles from our own production. Pick one and see it come alive on a roof.",
        "Dieci coppi della nostra produzione. Sceglietene uno e guardatelo prendere vita sul tetto."),
    "Naravni korci": ("Natural canal tiles", "Coppi naturali"),
    "Fotografije strehe so vizualizacije, ustvarjene na podlagi fotografij izdelkov. Barve v živo si oglejte pri najbližjem prodajalcu.": (
        "Roof images are visualisations made from product photos. See the real colours at your nearest dealer.",
        "Le immagini dei tetti sono visualizzazioni create dalle foto dei prodotti. I colori reali si vedono presso il rivenditore più vicino."),
    "Pošlji povpraševanje": ("Send an enquiry", "Richiedi un preventivo"),
    "Katalogi in ceniki": ("Catalogues & price lists", "Cataloghi e listini"),

    # references
    "Vse reference": ("All references", "Tutte le referenze"),
    "Stanovanjska hiša": ("Family house", "Casa unifamiliare"),
    "Obnova kulturnovarstveno zaščitenega objekta": ("Restoration of a protected heritage building", "Restauro di un edificio tutelato"),
    "Turistični objekt": ("Tourist building", "Struttura turistica"),
    "Streha štirikapnica": ("Hipped roof", "Tetto a padiglione"),
    "Uporabljen": ("Tile used", "Prodotto"),
    "Soški in kraški korec · Strešnik Alpe Jadran": ("Soški and Kraški korec · Alpe Jadran roof tile", "Soški e Kraški korec · tegola Alpe Jadran"),

    # news
    "Aktualno": ("Latest", "Novità"),
    "Arhiv novic": ("News archive", "Archivio notizie"),
    "Najnovejše": ("Newest", "Più recente"),
    "Avg": ("Aug", "Ago"),
    "19. Jun": ("19 Jun", "19 giu"),
    "09. Jun": ("9 Jun", "9 giu"),
    "11. Jul": ("11 Jul", "11 lug"),
    "Streha s kraškim korcem na družinski hiši": ("A family house roofed with Kraški korec", "Una casa unifamiliare con copertura in Kraški korec"),
    "Kraški korec na družinski hiši": ("Kraški korec on a family house", "Kraški korec su una casa unifamiliare"),
    "Nova referenca — značaj kraškega korca na sodobni družinski hiši.": (
        "A new reference — the character of Kraški korec on a modern family house.",
        "Una nuova referenza — il carattere del Kraški korec su una casa moderna."),
    "Preberi več": ("Read more", "Leggi di più"),
    "Odlično prezračevanje za prijetnejše bivanje": ("Good ventilation for a more comfortable home", "Una buona ventilazione per vivere meglio"),
    "Pravilno prezračena streha ohrani prijetno bivalno okolje tudi v poletni pripeki.": (
        "A properly ventilated roof keeps the home comfortable even in the summer heat.",
        "Un tetto ben ventilato mantiene la casa confortevole anche nella calura estiva."),
    "Nova streha za OŠ Vojke Šmuc Izola": ("A new roof for Vojka Šmuc Primary School in Izola", "Un nuovo tetto per la scuola elementare Vojka Šmuc di Isola"),
    "Prenova strehe, ki bo še vrsto let zagotavljala zanesljivo zaščito in večje udobje.": (
        "A roof renovation that will provide reliable protection and more comfort for years to come.",
        "Un rifacimento del tetto che garantirà per molti anni una protezione affidabile e più comfort."),
    "Kritina Korec zdaj z EPD certifikatom": ("Korec roofing now EPD certified", "La copertura Korec ora con certificazione EPD"),
    "Okoljska deklaracija izdelka za opečno kritino Korec.": (
        "An Environmental Product Declaration for Korec clay roofing.",
        "Una dichiarazione ambientale di prodotto per la copertura in laterizio Korec."),

    # roof ring
    "Strehe Goriških opekarn": ("Roofs by Goriške opekarne", "Tetti di Goriške opekarne"),
    "Stanovanjska hiša — Primorski korec": ("Family house — Primorski korec", "Casa unifamiliare — Primorski korec"),
    "Stanovanjska hiša — Francoski korec": ("Family house — Francoski korec", "Casa unifamiliare — Francoski korec"),
    "Antični korec med nasadi jabolk — Antični korec": ("Antični korec among apple orchards", "Antični korec tra i meleti"),
    "Obnova kulturnovarstveno zaščitenega objekta — Korec gladek": ("Restored heritage building — Korec gladek", "Edificio tutelato restaurato — Korec gladek"),
    "Stanovanjska hiša — Kraški korec": ("Family house — Kraški korec", "Casa unifamiliare — Kraški korec"),
    "Nova streha za OŠ Vojke Šmuc Izola — Opečna kritina Korec": ("New roof for Vojka Šmuc Primary School, Izola — Korec roofing", "Nuovo tetto della scuola Vojka Šmuc di Isola — copertura Korec"),
    "Stanovanjska hiša — Soški in kraški korec": ("Family house — Soški and Kraški korec", "Casa unifamiliare — Soški e Kraški korec"),
    "Stanovanjska hiša — Istrski korec": ("Family house — Istrski korec", "Casa unifamiliare — Istrski korec"),
    "Kraški korec na družinski hiši — Kraški korec": ("Kraški korec on a family house", "Kraški korec su una casa unifamiliare"),
    "Turistični objekt — Korec gladek": ("Tourist building — Korec gladek", "Struttura turistica — Korec gladek"),
    "Prezračevanje, ki ohladi poletje — Opečna kritina Korec": ("Ventilation that cools the summer — Korec roofing", "Ventilazione che rinfresca l'estate — copertura Korec"),
    "Streha štirikapnica — Soški korec": ("Hipped roof — Soški korec", "Tetto a padiglione — Soški korec"),

    # footer
    "Goriške opekarne — na vrh": ("Goriške opekarne — back to top", "Goriške opekarne — torna su"),
    "Noga strani": ("Footer", "Piè di pagina"),
    "Od 1948": ("Since 1948", "Dal 1948"),
    "Ostali izdelki": ("Other products", "Altri prodotti"),
    "Trgovina": ("Shop", "Negozio"),
    "Spoznajte nas": ("About us", "Chi siamo"),
    "Zgodovina": ("History", "Storia"),
    "Zakaj izbrati nas?": ("Why choose us?", "Perché sceglierci?"),
    "Predstavitveni video": ("Company video", "Video aziendale"),
    "O podjetju": ("Company", "Azienda"),
    "Osebna izkaznica": ("Company profile", "Profilo aziendale"),
    "Kontaktne osebe": ("Contact people", "Referenti"),
    "Kje smo": ("Where we are", "Dove siamo"),
    "Zaposlitev": ("Careers", "Lavora con noi"),
    "Ostalo": ("More", "Altro"),
    "Center gradbenih odpadkov": ("Construction waste centre", "Centro rifiuti edili"),
    "Prijava na e-novice": ("Newsletter sign-up", "Iscrizione alla newsletter"),
    "E-novice": ("Newsletter", "Newsletter"),
    "E-poštni naslov": ("Email address", "Indirizzo e-mail"),
    "Prijava": ("Sign up", "Iscriviti"),
    "Novosti, reference in akcije Goriških opekarn — enkrat na mesec.": (
        "News, references and offers from Goriške opekarne — once a month.",
        "Novità, referenze e offerte di Goriške opekarne — una volta al mese."),
    "Kontakt": ("Contact", "Contatti"),
    "© 2026 Goriške opekarne d.o.o. Vse pravice pridržane.": (
        "© 2026 Goriške opekarne d.o.o. All rights reserved.",
        "© 2026 Goriške opekarne d.o.o. Tutti i diritti riservati."),
    "Sledite nam": ("Follow us", "Seguiteci"),
}

# template literals and other code-level text that isn't a whole string unit
RAW = {
    "`Streha s korcem ${t.name}`": ("`Roof with ${t.name}`", "`Tetto con ${t.name}`"),
    "`${t.name} — izdelek`": ("`${t.name} — product`", "`${t.name} — prodotto`"),
}
ADDRESS = {"5292 Renče, Slovenija": ("5292 Renče, Slovenia", "5292 Renče, Slovenia")}

LANGS = {"en": 0, "it": 1}
SWITCH_SRC = '<div class="lang mono"><a class="on" href="./">SI</a><a href="it/">IT</a><a href="en/">EN</a></div>'


def switcher(cur):
    pre = "../" if cur != "sl" else ""
    links = [("sl", "SI", pre or "./"), ("it", "IT", pre + "it/"), ("en", "EN", pre + "en/")]
    on = ' class="on"'
    a = "".join(f'<a{on if c == cur else ""} href="{h}" hreflang="{c}" lang="{c}">{t}</a>' for c, t, h in links)
    return f'<div class="lang mono">{a}</div>'


def build(src, lang):
    i = LANGS[lang]
    table = {**T, **ADDRESS}
    hits = {k: 0 for k in table}

    def sub_text(m):
        lead, raw, trail = m.group(1), m.group(2), m.group(3)
        key = html.unescape(raw)
        if key in table:
            hits[key] += 1
            return ">" + lead + html.escape(table[key][i], quote=False) + trail + "<"
        return m.group(0)

    def sub_attr(m):
        name, raw = m.group(1), m.group(2)
        key = html.unescape(raw)
        if key in table:
            hits[key] += 1
            return f'{name}="{html.escape(table[key][i])}"'
        return m.group(0)

    def sub_js(m):
        q, raw = m.group(1), m.group(2)
        if raw in table:
            hits[raw] += 1
            return q + table[raw][i].replace("\\", "\\\\").replace(q, "\\" + q) + q
        return m.group(0)

    head, rest = src.split("<body", 1)
    body, tail = rest.rsplit("</body>", 1)
    # split body into markup and inline scripts so each gets the right kind of replacement
    parts = re.split(r"(<script>.*?</script>)", body, flags=re.S)
    out = []
    for p in parts:
        if p.startswith("<script>"):
            for k, v in RAW.items():
                if k in p:
                    hits.setdefault(k, 0); hits[k] = hits.get(k, 0) + 1
                    p = p.replace(k, v[i])
            p = re.sub(r"(')((?:[^'\\\n]|\\.)*)'", sub_js, p)
        else:
            p = re.sub(r">(\s*)([^<>]*?[^\s<>])(\s*)<", sub_text, p)
            p = re.sub(r'\b(alt|aria-label|placeholder|title|data-spec|data-group|data-cursor)="([^"]*)"', sub_attr, p)
        out.append(p)
    body = "".join(out)
    head = re.sub(r'(name="description" content=")([^"]*)(")',
                  lambda m: m.group(1) + html.escape(table[m.group(2)][i]) + m.group(3) if m.group(2) in table else m.group(0), head)
    if "Opečna kritina in zidni elementi iz spodnje Vipavske doline. Od 1948." in table:
        hits["Opečna kritina in zidni elementi iz spodnje Vipavske doline. Od 1948."] += 1
    page = head + "<body" + body + "</body>" + tail

    missing = [k for k, n in hits.items() if n == 0]
    if missing:
        sys.exit(f"[{lang}] Slovenian strings not found in site/index.html (edited or removed?):\n  - " + "\n  - ".join(missing))

    page = page.replace('<html lang="sl">', f'<html lang="{lang}">', 1)
    page = page.replace(SWITCH_SRC, switcher(lang), 1)
    page = page.replace("assets/", "../assets/")
    return page


def main():
    src = SRC.read_text(encoding="utf-8")
    if SWITCH_SRC not in src:
        sys.exit("Language switcher markup in site/index.html changed; update SWITCH_SRC in tools/build_i18n.py")
    for lang in LANGS:
        out = ROOT / "site" / lang / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(build(src, lang), encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

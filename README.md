# Goriške opekarne — website redesign

A single-page redesign concept for [goriske.si](https://www.goriske.si/), the clay roof tile and brick manufacturer from Renče, Slovenia.

## Run it

It's a static site: open `site/index.html`, or serve the folder:

```bash
npx serve site
```

## What's inside

- `site/index.html` — the whole page in Slovenian (HTML, CSS and JS in one file); **the only page to edit**
- `site/en/`, `site/it/` — English and Italian pages, generated from the Slovenian one
- `tools/build_i18n.py` — the translation table and generator
- `site/assets/` — photos, product packshots, roof visualisations, hero video and fonts

Built with GSAP + ScrollTrigger and Lenis (loaded from CDN). Type: Canela Light (display) and Roboto (text).

## Languages

Slovenian is the source. After changing any text in `site/index.html`, regenerate the other languages:

```bash
python3 tools/build_i18n.py
```

The build stops and lists any Slovenian string it can't find, so edited copy can't silently stay untranslated; add or update its EN/IT entry in the table. Product names (Korec gladek, Kraški korec, Go pro, ...) stay as they are in every language. Links to goriske.si still point to the Slovenian pages.

## Image sources

- Product packshots, reference projects and news photos: goriske.si
- Hero video, history and process imagery, and the configurator roof visualisations: generated with Higgsfield

## Fonts

`site/assets/fonts/` contains **Canela trial files** from Commercial Type. The trial licence covers evaluation only; a web licence is required before this goes live. The trial lacks č, š and ž, which fall back to Gilda Display.

# The site

Decisions about the site's pages, design and size, moved word for word from AGENTS.md on 20 Nov 2026 (the
maintainer's decision, so that an agent reads the rules and only the decisions of the part it works on: AGENTS.md
had grown to 97 KB). **Keep it current:** a decision made or changed is added here, at the end of the section it
belongs to, in the same commit as the change. The principles and the rules of work are in AGENTS.md.

## Site

- **Static pages in two scripts:** Latin (the default) and Cyrillic (`i18n.BUILT`). Every string also exists in
  English (`i18n.LOCALES`), but the English pages are not built since 8 Nov 2026: they were 291 MB of a 962 MB site
  against GitHub Pages' 1 GB. Putting "en" back into `BUILT` brings them back.
  - Serbian text is written once in Cyrillic; the Latin pages are the whole page transliterated.
  - Links to RIK are percent-encoded, so transliteration can't break them.
  - There is no JavaScript framework. Charts are SVG drawn when the site is built, except on the Explore page:
    its own script (`static/explore.js`, no library) draws in the browser from `api/r/<id>/stations.json` and
    `api/geo/municipalities.json`, with the strings and lists the page carries in its language. The stations'
    names in `api/` are as RIK wrote them, so the script transliterates them as `translit.py` does.
  - **Explore never chooses a list.** A measure that needs one waits for the reader, and picking another election
    clears the choice (ballot numbers belong to one election). Measures and filters are the same for every list.
    Its ready-made analyses are questions grouped by theme (`THEMES` in the script), its measures sit in groups
    (`MGROUPS`), and every measure, view, theme and question has its words in `i18n.py` (`m_desc_*`,
    `view_desc_*`, `preset_theme_*`, `preset_q_*`); a test reads the script and checks that none is missing.
    Unknown is not zero: a station whose board decision wasn't read has no controller value, and an election
    whose observers' records weren't read has none for them.
- **Results by kind of settlement** (`bysettlement.py`, `r/<id>/settlements.html`): every contestant's share and
  controllers by the class of its stations' settlements (type, population, change since 2011), in the order of
  their votes, nothing ranked or flagged. The census's figures are read from the archived tables when the site is
  built (`settlements.load_figures`), so the tables and each round's `settlements.json` are inputs of the round's
  pages. Explore's filters use the same classes (`bysettlement.CLASSES`); for a municipality a census measure counts
  each of its settlements with stations once, and census measures aren't compared between elections. Controllers
  are shown for a class only where at least half of its stations' decisions (and at least 10) were read: Belgrade's
  2024 decisions were mostly never published.
- **Incremental build:** each page's inputs are fingerprinted in `_site.state.json`.
  - **Every input of a page must be in its fingerprint.** On 3 Nov 2026 the place pages missed their board
    decisions, so the 2026 pages kept the old version.
  - The incremental test compares with a full build. When you add an input, extend that test.
- **The languages are built side by side** in forked processes (`Site.side_by_side`). Windows, or
  `IZBORI_SERIAL=1`, builds them one after another. The result is the same file for file.
- **The guide for controllers and observers** (`guide.sr.html`, `guide.en.html`) gives the article or RIK document
  for every rule, and says which month it was checked against. When the law or RIK's instructions change, update
  both languages and that line. Rules come from the law and RIK only; a party's handbook may suggest what to cover,
  never what the rule is, and its partisan advice stays out.
- **Size budget:** GitHub Pages allows 1 GB, and the site is about 660 MB with about 40,000 files (Nov 2026).
  - Keep repeated markup out of per-row HTML: cell labels live in the generated `static/labels.css`, links carry no
    per-link `rel`, and a `title` appears only where it adds something.
  - The municipality's lists keep to the documents of the vote. Decisions on polling boards are listed only on the
    place's page.
- **Hosting:** GitHub Pages through Actions at **izbornipodaci.rs** (since 8 Nov 2026); the previous build is kept
  in the Actions cache. The domain is registered at Loopia. Since 22 Nov 2026 its DNS is at Cloudflare, with
  Cloudflare's proxy in front of the site: the four GitHub Pages A records for the apex and `www` as a CNAME to
  javni-uvid.github.io, all proxied, SSL "Full (strict)", HSTS and the headers of `osnova/security.md`. Until then
  Loopia had one of the four A records and `www` as an A record too. **pages** tells Cloudflare to forget the cached
  files after each publishing (`CLOUDFLARE_API_TOKEN`, which can only purge this zone's cache, and the variable
  `CLOUDFLARE_ZONE_ID`); a failure there is only a warning. The custom domain is set in the repository's Pages
  settings (an Actions deployment needs no CNAME file). `SITE_URL` in config.py is the only place the address
  lives in code: feeds, the 404 page, the mail and the map image's source line all take it from there.
  - The purge asks for the whole zone (22 Nov 2026): the first run's purge by hosts was refused ("Request must
    contain one of purge_everything, files, tags, hosts or prefixes", code 1012) while the zone was still
    pending, and the zone holds only this site, so forgetting all of it costs nothing more.
  - Cloudflare Pages' free plan doesn't fit, with its limit of 20,000 files. Workers' paid plan (100,000 files) or
    a VPS are the fallback if the site outgrows 1 GB.
  - AI crawlers, agents and assistants are allowed (22 Nov 2026, the maintainer's decision; unlike zailiprotiv,
    which blocks training crawlers): Cloudflare's AI Crawl Control lets all through and the managed robots.txt adds
    nothing.

## Design rules

What the pages keep to (20 Nov 2026, taken at the maintainer's request from javni-uvid/zailiprotiv, whose rules
came from looks at its site against WCAG 2.2, NN/g, GOV.UK, Stanford's credibility guidelines, the Trust Project
and ProPublica's principles for news graphics), adapted to this site's readers (the curious visitor or
controller, the coordinator, the statistician: 7–8 Nov 2026) and, since 20 Nov 2026, zailiprotiv's look. They are working
rules, changed as readers show otherwise, unlike the principles in AGENTS.md. A change to a page is checked
against them.

1. **One scale of letter sizes.** A size is a step of the scale (`--t-1` … `--t-8`, `--t-h1`, `--t-d1` in
   `site.css`, zailiprotiv's own); body text is 16 px; grey (`--ink-2`) is for what is secondary. A test
   (`tests/test_design.py`) refuses a size outside the scale; an SVG's labels in px are the exception.
2. **A colour means a kind of content, never a list's merit.** Black ink on a white page, grey for what is
   secondary and for the cards, the data in grey and black (bars, meters, the Explore map's scale); red only for
   warnings, each group of checks in its colour beside its name and symbol; a list's own colour only on the
   settlement maps (`data/list_colours.csv`, with a key that names it) and the seats (by size). White text only on
   colours dark in both themes. Text 4.5:1 or more against its background, a form control's edge 3:1, in both
   themes: `tests/test_design.py` checks the tokens' pairs.
3. **The most important first.** A page says what it is and gives its main fact in the first screen (the latest
   election first, the result before the details); then the reasons, then the details and the documents.
4. **A number never stands alone.** It says what it is counted of, has something to compare it with (the
   municipality, the country, the election before, similar settlements), and a way to how it is computed. Unknown
   is not zero: a figure the data can't support is left out or said to be unknown.
5. **A trend is drawn, a table is kept.** Where the point is how something changed, bars from zero come first and
   the table follows (folded when long). No chart without its numbers.
6. **The phone first.** Every change is looked at at 320 and 390 px in both scripts; no page is wider than its
   screen; things to press are 44 px high; a long list shows its first rows and a way to the rest.
7. **Everything can be checked.** Each figure leads to its RIK document or its rule; a warning says what to
   check, never what happened (principle 2); nothing is ranked by preference (principle 1).
8. **For every reader.** Keyboard and screen reader reach everything; every page works without its script
   (`site.js` only adds); nothing moves by the clock that the reader can't stop; the reader is not addressed as a
   man or a woman. The keyboard's place is outlined in ink on every element, the first Tab skips to the page
   (`.skip`), and a reader who asked for less motion gets none; a map whose settlements are buttons is a group of
   them, not an image. A change to a template is run through axe-core's WCAG 2.2 AA rules on every kind of page.
9. **Measured, then changed.** The size budget and, once there are any, visit counts from the host or the edge
   (principle 5) are read before a change to how a page is laid out, and after it.

## Decisions log

- **5 Nov 2026:** the observer guide became the guide for controllers and observers, at the maintainer's request:
  written from the law (14/2022 and the 2026 amendments) and RIK's 2026 handbook for polling boards and instruction
  on handovers, with the topics of a controllers' handbook he shared. That handbook's partisan advice is left out,
  and the old guide's objection rule is corrected: a request to annul a station's vote goes to the local commission
  within 72 hours of closing (Art. 148). The same day it gained a section on local elections, from the Law on Local
  Elections (14/2022, 35/2024, 47/2026): that law leaves the procedure at the station to the parliamentary law
  (its Art. 8), so the section lists only what differs, each with its article.
- **5 Nov 2026, home page:** the maintainer chose to add the latest election's state beside the search, the
  archive in numbers, the next election from `data/elections.csv`, and three cards (controllers by list,
  municipalities, data and alerts); he passed on a feed of the latest events and on a card for changes after
  publication. The next election's deadlines are counted back from voting day (N days: that date; 24 and 48
  hours: two days before) and the strip says the commission's calendar is the authority. The municipalities
  page is new, sorted in Serbian alphabetical order per script. On phones the nav says only "Guide".
  - Later that day he removed the latest election's state: the space beside the search shows the next election
    only when one is entered, and stays empty otherwise. The phones' short "Guide" comes from a `data-short`
    attribute through CSS, so the link's text is the whole name everywhere else (copying, reader views, a stale
    stylesheet): two spans in one link showed both names when the CSS didn't apply.
- **5 Nov 2026, Explore page:** the maintainer asked for a tab where visitors run their own analyses and chose,
  for the first version: the election fingerprint (turnout against the largest share of any list), two elections
  compared, municipalities across elections as a heat table, filters with a CSV download, and a map of
  municipalities; ready-made analyses as well as free choice; controllers and observers' records as criteria for
  every list alike; OpenStreetMap's boundaries; Kosovo and Metohija by RIK's municipalities (pending RGZ's data).
  An earlier session had started a "Compare" page (the `geo` command and its data); the work continued as this
  page, and that session's unfinished strings and nav link were replaced.
- **5 Nov 2026, new checks and the commissions:** of the projects proposed for the data already archived, the
  maintainer chose new checks in the numbers and a page on the municipal commissions.
  - **Same votes as another station** (`identical_results`, unusual, weight 2) is a station flag: every contestant
    with the same votes at two stations of one municipality, with at least 50 votes and 3 contestants with votes.
    Two contestants match by chance too often (a two-way race); no archived election has a pair even at 10 votes.
  - **Round percentages and last digits stay statistics, never station flags:** a test over many stations can't say
    which one is unusual. Round percentages are now compared with the count expected from each station's
    denominator, exactly; the old note's "about 10% by chance" was wrong for small ones (of 500 votes, 20%). Per
    municipality both are tested and corrected for the number of municipalities (Bonferroni); none of the
    archived elections has one below 0.05.
  - **The commissions page has no score,** in keeping with "a flag is a question": each column is a fact, and cells
    are highlighted by absolute rules (something missing, a median over 12 hours, minutes after a day, changes), not
    by rank, so no municipality is marked only for being slower than others. A commission with no document isn't
    marked: RIK lists a city commission's documents under the city (Niš's, for its five city municipalities; the
    Belgrade city election of 2024), which the results don't have. At the maintainer's request they are shown with
    the city's municipalities ("+ city's"), apart from their own: the store keeps RIK's name of such a city, after
    one full pass of the register per election, and `commission.city_parts` joins a city to its city
    municipalities by every election's names ("Ниш-Медијана") and districts ("Град Београд"), or, where the city
    has a code, to the city municipality of its district (Kostolac to Požarevac, Sevojno to Užice). Vranjska Banja
    (2023 only, with no district in that file) stays alone. Hours come from the
    upload stamp in each document's link: the register of minutes shows the same time for almost every document,
    but days later for some (Bačka Palanka 2023: register 20 Dec, files 18 Dec). Abroad and prisons are left out
    (RIK runs them). Explore gained the same hours as a measure, a median per municipality.
- **6 Nov 2026, a list's votes on Explore:** the maintainer asked to see how many people voted for a list, not
  only its share, and to compare a list's fall between two elections. A list's votes are a measure like its share
  (a count, added up per municipality); the table shows each beside the other. In two elections a count changes by
  a number and in per cent (a share in percentage points, as before), the largest changes rank by either, and the
  summary gives both elections' totals over every chosen station, matched or not, so a list's national result
  reads directly. The ready-made "a list's votes in two elections" still waits for the reader to choose the lists.
- **6 Nov 2026, the municipality page:** the maintainer chose its order: the result in per cent first (with who
  voted: registered, voted, turnout, invalid ballots, which replace the tiles), then the polling stations (the
  first ten and a full-width button for the rest), then the votes of the three lists with most votes at each
  station as numbers instead of shares (same columns, shaded by share, now with a total row), then every list at
  every station behind a full-width button, and everything else below (controllers by list, the commission's
  documents). The button and the CSV of the whole table are `static/site.js`, which only adds to a page: without
  it every station shows and the CSV button stays hidden. A link to a station further down opens the list, as the
  pages across elections link to `#bm-<number>`. The same day the analyses moved towards the site: the maintainer
  wants what is relevant there, joined with the census where it shows something, not in separate dashboards.
  Phones: `.table-wrap` is positioned, so a visually hidden header label inside a scrolling table no longer
  widens the page (municipality and round pages scrolled sideways at 390 px, by up to 124 px), the
  round page's statistics tables scroll inside their own box, and the vote list's national share has the width
  of the votes and the share.
- **6 Nov 2026, analyses on the site:** of four analyses offered for the site (controllers against votes by list,
  the settlement on the station's page, results and controllers by kind of settlement, the census on Explore), the
  maintainer chose the last two first. Each election has a Settlements page: shares and controllers by the
  settlement's type, population and change since 2011, with the urban-other difference within municipalities,
  which keeps a list strong in rural municipalities from looking strong in villages everywhere, and the other way
  round: in 2026 two lists' controllers covered about as many village stations as town stations in the country's
  totals, yet 10 to 12 points fewer of the village stations than of the town stations within the same
  municipality. Explore gained the census's measures (an
  urban settlement, its people, its change since 2011, its share aged 65 or more) and filters by the same classes.
  The research dashboard of the same day is not kept up: the site is where the analyses go.
- **6 Nov 2026, Explore reorganised:** the maintainer asked for Explore to be conceptually ordered, more relevant
  and easier to use. The twelve ready-made analyses in one row became twenty questions in six themes (turnout,
  lists, voter register, controllers, settlements, minutes and checks), the question titling its answer; the form
  reads election, measure, view; the sixteen measures sit in five groups with a sentence each, and each view has
  one; the filters are grouped, and those in use show as removable chips with one reset; the notes that matter
  for what is shown stand beside it. Nothing new is computed, and every list is still the reader's choice.
- **7–8 Nov 2026, the redesign and its readers:** the maintainer defined three readers and asked for the site to
  serve each: (1) a curious visitor or a controller, who comes through a link to the site, wants their station or
  municipality, how it compares and anything that stands out, with little text and nothing to decode; (2) a
  coordinator of 30–60 controllers (the maintainer counts himself here), who works by municipality or part of one
  and needs the weak spots of its stations, ranked by his order (warnings repeated across elections, near-unanimous
  votes with a high turnout, no controller of his list, a sudden rise in registered voters, a turnout far from the
  surroundings), comparisons with the municipality, similar settlements and the country, and the history of its
  stations; (3) a statistician or a curious reader who wants the long view: data to download and Explore. Of two
  concepts sketched on a design canvas (one page in layers; three entrances), he chose **three entrances**: the
  navigation reads *Moje mesto · Za kontrolore i koordinatore · Analize i podaci · Vodič*, the home page is the
  search, three doors and what stands out. His other decisions: a neutral title ("every polling station in Serbia,
  through every election since 2022"), no example of a station page and no "what you get in three lines" on the
  first door but a short story instead; no "what's new since your last visit" anywhere, since it would look like
  tracking (what the browser keeps is shown as shortcuts only, with a forget button); the strip with the latest
  election's figures dropped; **"upozorenje" replaces "oznaka"** as the word for a flag (clearer, a mildly negative
  connotation accepted) — the pages still say "oznaka" and change in a separate commit; the cards must be clear
  to someone who doesn't yet know what a warning is, so they say "brojke ukazuju na nešto neobično" and name the
  places; lists may be named; the cards are the four in `highlights.py`, in the style of the canvas's fourth
  variant (a big line, a sentence, the figures below), with a palette where a colour means a kind of content and
  never a list: ink, sand, amber, brick (only for unusual numbers), teal, and yellow on dark. Build order he set:
  home → the station's page → the municipality → analyses.
- **8 Nov 2026, the palette for the whole site.** Three schemes were drawn on the canvas over the same home page and
  a table: A ink and sand (what the home page had), B newsprint with one accent, C navy and gold. Marko chose **C**.
  The roles are fixed in the tokens so every page follows: navy for the brand and the data, gold for the one thing
  to look at, red only for warnings, teal for the lists; the header sits on navy with a gold rule; `--gold`,
  `--gold-ink`, `--brand`, `--on-brand` and `--warn-track` were added, and warnings no longer share the data colour
  (`td.warn`, `tr.flagged` use `--critical`). The first tab is *Početna*: a tab that brings you back should say so.
- **8 Nov 2026, replaced minutes are a document, not a warning.** Marko asked why a replaced minutes document
  counted as a warning: it lifted some municipalities' averages without saying anything about the numbers (Bački
  Petrovac stood at 11 of 11 flagged in 2026 only because its commission re-uploaded every set of minutes). The
  `minutes_replaced` check is retired; the earlier minutes stay on the station as a document (*Ранији записник*,
  "Earlier minutes"), so both versions can still be opened and compared, and old feed entries keep the entry but
  drop that line. Remarks on the minutes stay a flag (he accepts that one, with some doubt: it says a document
  exists, not what it says).
- **8 Nov 2026, "upozorenje" on every page.** The Serbian pages now say *upozorenje* for a flag everywhere (the
  strings, the about page, the guide); English keeps "flag". Neuter noun, so the adjectives and verbs around it
  changed with it ("isto upozorenje", "pojavilo").
- **8 Nov 2026, Izbori back in the header.** Marko asked for it: *Početna · Izbori · Za kontrolore i koordinatore ·
  Analize i podaci · Vodič*. Izbori is current on the elections page and every round page; the coordinators' tab
  on the municipalities' pages. Five tabs fit a 390 px phone with the short names; at 360 px the row scrolls.
- **8 Nov 2026, the station's page.** Second step of the build order. Drawn on the canvas ("Strana biračkog mesta")
  and approved as proposed: the latest election first and open, in a block with the result and bars, three tiles
  against the municipality, each flag as a sentence with what to check right under it (the "What to check" list at
  the bottom is gone), controllers with the lists that have none (a coordinator's weak spot), documents; then "In
  short" and the trends; then the earlier elections folded into the same block. The wide history table is gone
  from this page (it stays on the municipality's history page and in the JSON). Rules kept: every contestant alike
  (shown when at least 1% here, the first three always), names shortened by the same rule as in sentences.
- **8 Nov 2026, the coordinator's municipality page, and two checks.** Third step of the build order, drawn on the
  canvas ("Pregled opštine za koordinatora") and approved with the order as drawn, the sixth card kept, and similar
  municipalities by five size classes × town/not. A look at izbori26.rs (notes in the project doc
  `claude/izbori26-analiza.md`) fed two things: the per-list deviation chart against the municipality, and the
  register check. New checks, same for every list: `registered_jump` (register up 15% more than the municipality's
  median change at the same place, under 40%: above that the area was most likely redrawn) and `turnout_apart`
  (20 points from the median of the other stations in the same census settlement, at least two of them). Both
  weight 1, group "unusual". A municipality-wide fallback for `turnout_apart` was measured and dropped: towns differ
  from villages everywhere and it flagged 400 stations in 2026 against 55 for the settlement rule. "My list" lives
  only in the reader's browser (`viewed.lists`), consistent with the no-tracking principle; the page is rendered
  for the leading list so it reads without scripts. The near-unanimity card is the `near_unanimity` rule alone,
  since that rule already requires turnout of 90%.
- **8 Nov 2026, the size budget: English dropped from the build, indentation stripped.** The station page redesign
  took the places' pages from 441 to 674 MB and the site to 962 MB (Cyrillic 332, English 291, Latin 286, API 52).
  Measured options: without English and Cyrillic the site is ~340 MB; stripping the templates' indentation saves
  5.5%. Marko chose: drop English for now, keep Cyrillic, strip the indentation. `i18n.BUILT` lists what is built;
  the English strings, templates and tests of the strings stay. `site.compact` removes indentation only (a line
  break stays a line break), never the space between tags on one line, so inline elements don't run together.
  Expected: ~650 MB.
- **8 Nov 2026, how every settlement voted.** A Reddit post that drew a crowd was a map of one region's villages
  with a list "which list is first in which villages", made by hand from izbori26.rs's data; people answered about
  their own village. The municipality's page now gives that material to anyone: a sentence naming the settlements
  each list is first in, and a table per census settlement. Next: settlement boundaries (OSM `ref:RS:naselje`) for a
  map per municipality, then an image to download and an `og:image`, so a link carries the map.
  Done the same day: `izbori geo --settlements` (4,720 boundaries, 7 without a census match), the map on the page
  (`maps.py`; colour = the list's rank in the whole election, lighter under 5 points, grey without a result), names
  where they fit, and "Download the image (PNG)" drawn on a canvas in the browser. `og:image` still needs a raster
  made at build time; not done. Known gap seen on Novi Sad: Kovilj's stations are not placed in Kovilj
  (settlements.py), so it draws grey.
- **8 Nov 2026, lists' colours on the maps.** Marko asked for the Student list in red and United Serbia in blue
  on the settlement maps. The maps had coloured by rank in the election to keep colour from meaning a list; a
  map people share is read against what they expect, so the two largest lists' colours are now set by hand per
  election in `data/list_colours.csv` (round, number, colour), and every other list still takes the next free
  colour by rank. The rule is the same for every list — any list can be given a colour there — and it stays out
  of the checks, which never look at who gains. The file is in the round pages' fingerprint.
- **8 Nov 2026, charts in the shared map image.** The PNG a reader downloads now has the map on the left and
  two charts on the right: the municipality's result with the country's share as a tick, and turnout by
  settlement with the municipality's turnout as a line. Both are drawn on the canvas from the page's own JSON
  (`#mun-data` carries each list's colour slot and country share, and the municipality's and country's turnout),
  so the image needs no server and no third party, and it is the same for every municipality and every list.
  The page itself does not gain the charts: the image is the thing people pass around, the page has the table.
- **8 Nov 2026, custom domain.** The site moved to izbornipodaci.rs, the name of the GitHub organisation
  spelled as one word; GitHub Pages stays the host and the old github.io address redirects. The address lives in
  `SITE_URL` alone, and the image people download names the new host so a shared picture leads back to the site.
- **9 Nov 2026, the shared map image.** Marko: the numbered settlements looked like a bug (a key with no heading,
  among the facts), the country tick wasn't explained, Vranje's 90 settlements were a crowd, and the no-result grey
  was too close to the blue list. Now: the map is drawn 1.6× with names at their size and cropped to the outline;
  a name that would cover a wider settlement's name becomes a number (`maps.label_box`, judged at that scale),
  numbered row by row; the key sits beside the map under the charts, small, with a heading; the tick is explained
  under the chart's title and labelled on the first bar; `--mp-none` is a neutral grey (light #e6e3de, dark #3b3a38).
  Same day: on Pirot's map the Student list (red, set by hand) and Faktor stabilnosti (orange, by rank) read as one
  colour. `maps.slots` now pushes a hand-set colour's look-alikes (`ALIKE`: red–orange–pink, blue–purple,
  green–dark green, orange–yellow) to the end of the free slots, and with colours set by hand takes yellow and green
  first (`PREFER`), apart from red and blue for most eyes. Without hand-set colours the order stays the seats'.
  Same day: the image's source line names the page (izbornipodaci.rs/pirot, `mun_url`), so a shared image leads back
  to it. The turnout chart beside the map gave way to how the twelve largest settlements voted: a 100% bar each,
  split among the four largest lists in their map colours (Marko chose this of three drafts: the settlements named
  per leading list, which repeated the legend; the two largest lists' difference, one-sided where one list leads
  everywhere). Turnout stays in the facts under the map. The share beside each bar is in the leading list's colour (yellow and pink darkened), so it says whose it is.
- **9 Nov 2026, shades on the settlement map.** Marko asked for gradients showing how strong a settlement is. A
  first version had two modes behind buttons ("who leads", "my list"); Marko wanted one map and one image showing
  everything, no buttons for now. So: the leader's colour by opacity in four fixed steps of the leader's share
  (`maps.LEAD_STEPS`, fixed so maps compare across municipalities), drawn at build time, the legend giving each list
  its four shades and one line with the steps; the numbers per settlement are in the chart beside the map in the
  image. Opacity over the page rather than a mixed colour, so both themes work.
- **8 Nov 2026, the search opens the newest election's municipality page.** Marko: whoever picks their
  municipality or station in the search should land on the page just built, with the map. A municipality in the
  search, in the municipalities index and in a station page's crumbs now opens `r/<newest>/m/<code>.html`; the page
  across elections (`m/<code>.html`) stays one link away, as the station page keeps its earlier elections folded.
  Merged the same evening (next entry).
- **8 Nov 2026, one page per municipality and per place.** Marko: the previous designs go out of use; a municipality
  or a place found by the search shows the new page. `m/<code>.html` is now the coordinator's page for the newest
  election with the municipality's other elections at the end (narrative, trends, the table of elections and the
  places across elections, folded), and `r/<id>/m/<code>.html` is the same page for that election (the history only
  on the newest); `municipality_history.html` is gone. Both come from `Site.municipality_context` (per municipality)
  over `Site.round_shared` (per election and language, cached), so the two addresses can't drift apart. Under the
  title, a table of contents and a strip of the municipality's elections; the station page got the same strip, each
  election leading to its block (a link to a folded block opens it, `site.js`). "My list by station" was redrawn:
  bars of the list's share from zero, strongest first, a line at the municipality's share, six strongest and six
  weakest shown — Marko found the symmetric deviation chart unclear at first sight. The header has six sections
  again: "Places to watch" (`repeat.html`, until now "Station history"; the name says what the list is for without
  calling a place guilty, which "problematic places" would) is back between coordinators and analyses, the guide
  shows as "Vodič", and short names take over below 1150 px.
- **8 Nov 2026, cities split into municipalities.** Marko: Belgrade or Niš should come up in the search even
  though RIK splits them into municipalities, and asked how to treat "urban" against "territorial" Belgrade. The
  city is whatever the results put under it (`commission.city_parts`, from the names and districts of every
  archived election), so Belgrade is its 17 municipalities, as RIK counts; the page adds them up by a
  municipality's arithmetic (`cities.py`) and never computes a second "urban Belgrade" total. The customary split
  into ten central and seven outer municipalities is shown only as two groups with subtotals in the table, and the
  page says so. A city with a code of its own and one city municipality beside it (Požarevac + Kostolac, Užice +
  Sevojno) gets the same page, its own row first and marked. One address per city, `g/<slug>.html`; no per-election
  city pages, the table at the end has every election.
- **8 Nov 2026, three small ones from the principles.** The weak-spot cards say what to check, as the station page
  does (same rule, same sentence). The municipality a reader viewed last is remembered from the canonical address
  too (the script only knew `r/<id>/m/`). "Places to watch" filters by municipality and links back; the
  municipality's first card leads there with `#m-<code>`.
- **8 Nov 2026, addresses by name.** Marko: izbornipodaci.rs/beograd, /novisad. Every municipality and city
  is at `/<name>/` (`cities.name_slug`, `cities.slugs`; `<name>/index.html`, since Pages serves folders);
  `m/<code>.html` and `g/<slug>.html` became one-line pages with a meta refresh, so nothing shared breaks, and the
  run-together spelling (`/novisad/`) leads to the hyphenated one. The template helpers `mun_href(code)` and
  `city_href(slug)` are the only way to link a municipality or a city; `r/<id>/m/<code>.html` stays for earlier
  elections (and the newest, with `#bm-N` anchors from the check page). Size: the newest election's municipality
  page now exists twice (by name, and under r/); making the r/ copy a redirect would save ~30 MB but lose the
  anchors unless a script carries the hash — a lever if the budget tightens.
  The same evening the polling places followed: `/<municipality>/<number>/` (`Site.place_path`), `s/<place>.html`
  a redirect. A redirect page is a bare 300-byte file, not a page on the base template: with 8,000 places in two
  scripts the template cost 60 MB.
- **11 Nov 2026, local elections only where they belong (Marko).** A local election isn't shown where it isn't
  relevant: Novi Sad's page said it "didn't vote in" Lokalni 2024 (Belgrade's), and Places to watch had a column for
  every local round that all other stations were "not part of". A municipality's "didn't vote in" now leaves out
  every local election, and Places to watch compares only the elections of the whole country, the province or
  Belgrade; a local round read from a municipality's documents stays on that municipality's and its stations'
  pages. Places to watch lost its worked example: one lede, and the four terms the table rests on set apart in a
  box (flag, elections flagged k / n, the same flag again, the cells).
- **20 Nov 2026, one scale of letter sizes, as zailiprotiv's.** The maintainer asked for the site's design to be
  closer to zailiprotiv's. Its type scale came first: `site.css` had 36 sizes, now every one is a step of the same
  scale as zailiprotiv's (12.8, 14, 16, 18, 20, 24, 30, 36 px; the page's title `--t-h1` and the big numbers and
  the home's headline `--t-d1` as clamps), each old size taken to the nearest step (0.95rem to 16 px, 0.925rem to
  14 px, 1.6rem to 24 px …), headings set a little tighter (letter-spacing -0.015em), and `tests/test_design.py`
  keeps it so. On phones the tabs stay 14 px so five fit a 390 px row. The palette of 8 Nov (navy header with the
  gold rule) is unchanged: zailiprotiv's white header with a black rule, black ink and grey cards would replace
  it, and that is the maintainer's choice. Checked at 320, 390 and 1280 px, both scripts, light and dark, on a
  site built from round 680072: no page wider than its screen.
- **20 Nov 2026, zailiprotiv's look, and an audit against the design rules.** The maintainer asked for the site to
  look more like zailiprotiv and to follow every UX and UI principle; this replaces the palette of 8 Nov (navy
  header, gold rule, teal for the lists) with zailiprotiv's newspaper look: a white page and black ink (`#111`,
  dark `#f1f1ee` on `#111318`), grey (`#555`) for what is secondary, grey cards (`#f3f3f1`) with a 10 px radius, the
  header white with a 3 px black rule as wide as the text, the name and headings in Literata 700 (served from the
  site, OFL; IBM Plex Sans and Source Serif 4 are gone, the text is the reader's system font), black buttons,
  table headers small and uppercase over a 2 px rule, form controls square with a `--ink-2` edge. The data went
  from navy to grey and black, as zailiprotiv draws a count; "look here" (the big number, the doors' labels) is
  ink; red stays the warnings' only, and the "unusual numbers" card is grey with its words in red. Why: one
  organisation, one look, and the reader of either site knows how to read the other; zailiprotiv's look was
  already held to the rules above. The audit (axe-core 4, WCAG 2.2 AA and best practice, every kind of page at
  320 and 1280 px, light and dark, on a site built from round 567956): no contrast failure before or after; the
  settlement map was an image holding buttons (now a group of them); there was no skip link, no focus style of
  the site's own and no reduced-motion rule (all three added); on phones the sixth tab was cut off at the screen's
  edge (the tabs now wrap to a second row). No page is wider than 320 px. The 404 page's targets look small only
  when it is opened from disk (its stylesheet's address is the site's). Size: the test site grew 0.3% (the skip
  link on every page), the fonts shrank from 14 files to 4.
- **22 Nov 2026, Cloudflare in front, and visits counted.** The maintainer moved the domain's DNS to Cloudflare,
  with its proxy in front of GitHub Pages (as zailiprotiv's), and made principle 5's exception zailiprotiv has:
  Cloudflare Web Analytics counts visits, without cookies and only as totals per page. Its script is on every page
  only when the build has the site token (the repository's variable `CLOUDFLARE_ANALYTICS_SITE_TOKEN`; the token is
  in `code_version`, so setting it rebuilds every page); the footer, the home page's "no tracking" and the about
  page's principle say so, and say otherwise without it. **visits** reads the counts by hand (`tools/visits.py`,
  from zailiprotiv's, asking only for this site's hosts).
- **22 Nov 2026, how fast the pages are.** **visits** also prints Core Web Vitals as Cloudflare Web Analytics
  measured them (`tools/vitals.py`, from zailiprotiv's): LCP, INP and CLS as shares of loads good, middling and poor,
  by device and by kind of page in Latin and Cyrillic (home, municipality or city, polling station across elections,
  polling place, a round's pages, Explore, the guide, the lists), since one of the site's 67,000 pages is seldom
  opened often enough to say; for a kind under the line (good for fewer than 75% of loads) the elements Cloudflare
  names. Sums only, no row measured fewer than 20 times; the two readings run as separate steps, so one failing
  doesn't stop the other.

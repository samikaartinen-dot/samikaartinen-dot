# HANDOFF – Sami's Workshop (elävä GitHub-profiili)

Tämä tiedosto kertoo, mihin asti projekti on tehty Clauden chat-keskustelussa
(23.11.2026) ja mitä Claude Coden kanssa tehdään seuraavaksi.

## Tavoite
Oma GitHub-profiili (`samikaartinen-dot/samikaartinen-dot`), jonka yläosassa on
**isometrinen tekninen paja**, joka päivittyy itsestään oikealla datalla: GitHub-
aktiivisuus, sää, vuorokaudenaika, liputus- ja juhlapäivät. Näyttävä, "minun näköiseni",
ja samalla Python-portfolionäyte.

## Tilanne nyt
| Osa | Tila |
|---|---|
| Piirtäminen (`generator/workshop.py`) | ✅ valmis ja testattu (Chrome-renderöinti) |
| Teemapäivät (`generator/themes.py`) | ✅ valmis, 8 teemaa testattu |
| Config (`config.yml`) + `build.py --offline` | ✅ testattu |
| Datan haku (`build.py`, live-tila) | ✅ toimii Actionissa (GitHub + Open-Meteo), ensimmäinen ajo 23.11.2026 |
| GitHub Action (`.github/workflows/workshop.yml`) | ✅ ajettu onnistuneesti, commitoi workshop.svg:n |
| README-teksti | ✅ luonnos, LinkedIn-linkki puuttuu |
| Projektikortit README:hen (`generator/cards.py`) | ✅ 3 isometristä korttia, prosentit configista |
| Vierailijalaskuri | ✅ README:n laskurimerkki + omat haut vähennetään (`data/state.json`) |
| Testit (`tests/`, pytest) | ✅ 15 testiä, ajetaan Actionissa ennen piirtämistä |

## Pajan sisältö (päätetty)
- **MANEK-lauta pöydällä**: 8×8 LEDiä = viimeiset 64 päivää GitHub-aktiivisuutta, tämä päivä sykkii
- **Split-flap-taulu** vasemmalla seinällä: tervehdys kellonajan mukaan (HUOMENTA/PÄIVÄÄ/ILTAA/YÖVUORO), alarivi kiertää sanoja + sää + nykyinen projekti
- **Liiga-tulostaulu** (CODE 7 – 2 BUGS, configista) + **seinäkalenteri** (päivä + lähtölaskenta, oletus jouluun)
- **Hylly**: pallolamppu (hehkuu illalla) + kielilaatikot (koko = osuus)
- **Ikkuna**: oikea sää (lumi/sade/selkeä/pilvi), Helsingin vuorokausirytmi, kaupungin siluetti
- **NOW BUILDING -taulu** + edistymispalkki, **pokaalihylly** (6 paikkaa, himmeät = saavuttamatta)
- **Työpöytä**: monitori (viimeisin commit + tämän päivän commitit), post-it-laput (todo), Nano ESP32 + Nano R4 koekytkentälevyllä, juotosasema (350°/OFF) + kolvi + tinarulla + sieni, yleismittari (päivän commitit), **yksi** kahvikuppi (höyry = päivän commitit, kylmä jos 0), riippuvalaisin, vanerinippu pöydän alla
- **Laser** (Sculpfun-tyylinen avorunko): portaali liikkuu, kaivertaa viimeksi päivitetyn repon nimen + kuvion (manek → siili, liiga → mailat+kiekko, muut → ratas)
- **Kappalepino** = viikon commitit
- **PCB-kärry**: MANEK V2 -schema sinikopiona + leijuvat 3D-piirilevyt (LED, Command, Controller)
- **Steampunk-rattaat** + **nixie-vierailijalaskuri**, **jääkiekkomaila + kiekko**
- **Manek-siili**: 4 reittiä (`ROUTES` workshop.py:ssä: patrol, roam, stool, peek), reitti arvotaan päivämäärä+tunti-siemenellä → vaihtuu 2 h välein; kantaa vanerinpalaa jos ≥3 committia tänään, nukkuu laatikossa jos 3 pv ilman committeja. Jakkarareitti ohitetaan, jos teemapäivän esine on jakkaralla. Piiloreitti käyttää clipPathia `#cratehide` (steampunk-laatikko).
- **HUD**: nimi, tagline, kaupunki+sää+pvm, 4 tilastokorttia, PROJECTS-paneeli prosentteineen, selitteet

## Teemapäivät (`themes.py`)
- Liputuspäivät (sisäministeriön lista, viralliset + vakiintuneet) → Suomen lippu ikkunassa + nimi HUDissa. Juhannuksena lippu jo aattona klo 18.
- Itsenäisyyspäivä: kynttilät ikkunalla, kakku "Suomi N v" (lasketaan 1917:stä), ONNEA / SUOMI / N V
- Joulukuu: jouluvalot, tonttulakki, piparit; 13.12.–6.1. kuusi; 24.–26.12. lahjat + HYVÄÄ JOULUA
- Uusivuosi 31.12.–1.1.: ilotulitus, juhlahattu, tinanvalanta jakkaralla
- Pääsiäinen (palmusunnuntai–2. pääsiäispäivä): virpojanoita-siili, pajunkissat, munat, VIRVON VARVON
- Vappu 30.4.–1.5.: serpentiinit, ilmapallot, ylioppilaslakki, kuohuviini (korkki lentää)
- Juhannus: koivunoksat, kokko, kukkaseppele, hyttynen, makkara
- Runebergin päivä: torttu

Esikatselu: `python generator/build.py --offline --date 2027-05-01 --hour 13 --out /tmp/vappu.svg`

## TODO – järjestyksessä
1. ✅ Repo luotu ja pushattu 23.11.2026.
2. ✅ **Live-haku testattu**: aja Action käsin (Actions → Update workshop → Run workflow).
   - Tarkista että `contributions` ei ole tyhjä. Jos GITHUB_TOKEN ei riitä GraphQL-kyselyyn,
     tee fine-grained token (ei oikeuksia, vain julkinen data) → repo secret `WORKSHOP_TOKEN`.
   - Tarkista Open-Meteo (pitäisi toimia ilman avainta).
   - komarev-laskurin numeron parsiminen SVG:stä on kokeellinen – korjaa regex tarvittaessa
     tai vaihda laskuripalvelu.
3. ✅ Testit.
4. **README**: lisää LinkedIn-tunnus kun Sami haluaa; linkit vain julkisiin repoihin.
5. ✅ Projektikortit.
6. ✅ Välimuisti tarkistettu 23.11.2026: `workshop.svg` ja kortit ovat suhteellisia polkuja,
   joten ne eivät kulje camo-välimuistin kautta – uusi kuva näkyi profiilissa heti Action-ajon jälkeen.
   Vain komarev-laskurimerkki kulkee camon kautta.

## Työtapa
- Työ tehdään joko Clauden chatissa (pilvi: kloonaa repo, muokkaa, testaa, pushaa) tai Claude Codessa.
- Tämä tiedosto on ainoa "muisti": päivitetään jokaisen julkaisun yhteydessä.
- Isomman kokonaisuuden jälkeen aloitetaan uusi keskustelu: "jatketaan GitHub-pajaa".

## Tehty 23.11.2026 illalla (pilvessä)
- Yksityiset contributionit päälle profiilissa → LED-lauta syttyi (342 contributionia).
- Kielihylly lukee kielet `config.yml`:stä (`languages`), koska koodirepot ovat yksityisiä.
- Vierailijat: README:n alareunan laskurimerkki laskee oikeat käynnit; Action vähentää omat
  hakunsa (`data/state.json` → `own_counter_fetches`). Kuka kävi, ei voi tietää – vain määrä.
- Alateksti: "auto-updated every 2 hours".
- Projektikortit: MANEK V2, Liigamanageri, Learning Python (`cards/*.svg`).
- Iso nixie-VISITORS-näyttö pajan vasempaan reunaan; isompi laskurimerkki, klikkaus pysyy profiilissa.

## Tehty 23.11.2026 myöhään illalla (pilvessä)
- Action päivitetty Node 24 -versioihin: `actions/checkout@v6`, `actions/setup-python@v6` → ei enää vanhenemisvaroituksia.
- Workflow ajetaan nyt myös, kun itse workflow-tiedostoa muutetaan (push-polku lisätty).
- Live-tarkistus: profiilin kuva päivittyy heti, camo ei hidasta.

## Tehty 24.11.2026 (pilvessä)
- Siili kiertelee: 4 reittiä (vanha kierros, iso kierros, jakkaralle hyppy + katsoo katsojaa, piiloutuu laatikon taakse ja kurkistaa). Edestä katsova sprite `hedgehog_front`.
- Tekstit luettaviksi profiilin ~600 px leveydessä: isommat tilasto-/projektitekstit, alareunaan vain LED-selite + "redrawn every 2 h by Python".
- README:n siilirivi päivitetty. 3 uutta testiä.
- Esikatsele tiettyä reittiä: monkeypatchaa `workshop.pick_route` (ks. testi `test_only_peek_route_uses_crate_clip`).

## Ideat (backlog)
Samin ideoita, joita ei ole vielä toteutettu. Lisää uudet tänne, poista kun tehty.
- (tyhjä – lisää seuraava idea)

## Tunnetut asiat / sudenkuopat
- Vierailijalaskuri näyttää 0, kunnes profiilissa käydään: laskurimerkki on README:n alareunassa.
- Cron on UTC:ssä; `build.py` muuntaa ajan Europe/Helsinki-aikaan (`zoneinfo`).
- Action ajetaan 2 h välein, jotta päivä/yö ja valot seuraavat oikeaa aikaa. Bot-commitit
  eivät näy omissa contributioneissa.
- Jos commit-historia paisuu liikaa, vaihtoehto: kuva erilliseen `output`-haaraan.
- SVG on ~100 kt, animaatiot ovat SMIL/CSS – toimivat GitHubin `<img>`-näkymässä.

## Turvallisuus (julkinen repo)
- Ei koskaan avaimia/tokeneita koodiin tai configiin → vain GitHub Secrets.
- Workflow: `permissions: contents: write` (vain tämä repo), ei `pull_request_target`-triggeriä.
- Kuvaan vain julkista tietoa: kaupunkitaso, ei tarkkaa sijaintia; post-it-lappuihin vain julkisia asioita;
  työhön liittyviä tai yksityisiä projekteja ei linkitetä eikä mainita.
- Kaikki muut repot ovat yksityisiä: README:ssä ei linkkejä niihin (404 muille).
- Profiilirepo sisältää vain piirtokoodin – mitään ei ajeta kenenkään koneella, Action ajetaan GitHubin palvelimilla.
- `show_clock: false` piilottaa kellonajan, jos ei halua näyttää aktiivisuusrytmiä.

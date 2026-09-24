# Zwaardere auto, hoger brandstofverbruik?

Case 2 — hbo-minor Data Science, Introduction to Data Science en Visual Analytics.

**Onderzoeksvraag:** wat is het verband tussen leeggewicht en geregistreerd gecombineerd brandstofverbruik van uitsluitend-benzinepersonenauto’s in het RDW-register?

Wie een auto zoekt, wil weten hoe zuinig die is. We verwachten dat zwaardere auto’s gemiddeld meer brandstof verbruiken. Dit project beschrijft het verband; het voorspelt geen praktijkverbruik en bewijst geen oorzaak.

## Resultaten van een eerdere API-run

Opgehaald op **24 september 2026**, tussen 14:09 en 14:28. De opgehaalde aantallen van beide volledige brontabellen komen overeen met de afzonderlijk gecontroleerde API-tellingen tijdens deze run.

| Stap                                                 |              Aantal |
| ---------------------------------------------------- | ------------------: |
| Personenautorijen opgehaald                          |          10.809.079 |
| Brandstofrijen opgehaald, alle voertuigsoorten       |          16.990.477 |
| Uitsluitend-benzinepersonenauto’s na koppelen       |           7.333.644 |
| Verwijderd wegens onbruikbaar gewicht en/of verbruik |           1.360.677 |
| Auto’s in de uiteindelijke analyse                  | **5.972.967** |

Er zijn geen exacte dubbele rijen of conflicterende voertuigrijen gevonden. Bij de gekoppelde benzinepersonenauto’s ontbreken 150 gewichten en 1.360.669 verbruiken. De 150 ontbrekende gewichten overlappen met ontbrekende verbruiken. Daarnaast zijn acht verbruiken nul of negatief. Eén bruikbare auto heeft geen geldig toelatingsjaar; die blijft in de hoofdanalyse.

**Antwoord op de onderzoeksvraag:** in deze selectie gaan zwaardere auto’s samen met een hoger geregistreerd gecombineerd verbruik. De Pearson-correlatie is **r = 0,711**. Het gemiddelde verbruik is **5,81 l/100 km**, de mediaan **5,50 l/100 km**. Dat is een beschrijvend verband, geen bewijs dat alleen gewicht dit veroorzaakt.

| Gewichtsklasse  | Gemiddeld verbruik (l/100 km) |   Auto’s |
| --------------- | ----------------------------: | --------: |
| < 1.000 kg      |                          4,85 | 2.103.016 |
| 1.000–1.249 kg |                          5,64 | 2.028.713 |
| 1.250–1.499 kg |                          6,65 | 1.441.257 |
| 1.500–1.749 kg |                          8,15 |   331.680 |
| ≥ 1.750 kg     |                         11,28 |    68.301 |

De zwaarste klasse ligt **6,43 l/100 km** boven de lichtste. Let op de ongelijke groepsgroottes en de open grenzen van de uiterste klassen. Binnen de toelatingsperiodes t/m 2009, 2010–2016 en vanaf 2017 is r respectievelijk **0,864**, **0,819** en **0,819**. Deze grove uitsplitsing neemt de positieve richting dus niet weg; zij sluit invloed van leeftijd, uitvoering of motorvermogen niet uit.

**Opvallende waarden:** het behouden gewicht loopt van 485 tot 7.647 kg, het verbruik van 0,1 tot 99 l/100 km. Vooral de uitersten vragen inhoudelijke controle. Ze zijn niet stilzwijgend gewist of als bewezen betrouwbare waarden bestempeld. Daarom moet de groep ook de mediaan, de uitersten en deze beperking bespreken. Er is geen gevoeligheidsanalyse uitgevoerd die bewijst dat de precieze waarde van r ongevoelig is voor zulke registraties.

Deze cijfers komen uit een eerdere API-run zonder dashboardfilters. Een nieuwe download kan andere cijfers geven. De vereenvoudigde versie haalt altijd opnieuw op wanneer het app-proces start; de eerste ophaal- en verwerkingsstap kan veel tijd en geheugen kosten. Start, merk/modelafhankelijkheid, gewichtselectie, het aan- en uitzetten van de trendlijn en een model met één gewicht zijn gecontroleerd. Ook de opschoonlogica voor dubbele rijen, hybride registraties en onbruikbare metingen is gecontroleerd. Er zijn geen controlebestanden aan het project toegevoegd. Een live publicatie en een visuele controle op het uiteindelijke hostingaccount zijn nog niet uitgevoerd.

## Bestanden in de repository

| Bestand              | Functie                                                                                           |
| -------------------- | ------------------------------------------------------------------------------------------------- |
| `data.py`          | RDW-pagina’s ophalen, op kenteken koppelen en opschonen. Geeft twee tabellen rechtstreeks terug. |
| `app.py`           | Dashboard met filters, grafieken en conclusie.                                                    |
| `requirements.txt` | De vier benodigde Python-pakketten.                                                               |
| `README.md`        | Projectuitleg, verantwoording en presentatiescript.                                               |

Er staat geen dataset, tijdelijke CSV of kwaliteitsbestand in de repository. De kwaliteitstellingen worden tegelijk met de auto’s berekend en als tabel aan het dashboard doorgegeven.

## Databronnen en afbakening

De bronnen zijn twee afzonderlijke openbare tabellen van dezelfde organisatie. Dit voldoet aan de eis om tabellen te combineren die niet uit hetzelfde bestand komen. De datasets zijn door de groep gekozen.

| Bron                                                                    | Openbare API                                        | Opgevraagde velden                                                                                     |
| ----------------------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| [Gekentekende voertuigen](https://opendata.rdw.nl/d/m9d7-ebf2)           | `https://opendata.rdw.nl/resource/m9d7-ebf2.json` | `kenteken`, `merk`, `handelsbenaming`, `massa_ledig_voertuig`, `datum_eerste_toelating`      |
| [Gekentekende voertuigen brandstof](https://opendata.rdw.nl/d/8ys7-d773) | `https://opendata.rdw.nl/resource/8ys7-d773.json` | `kenteken`, `brandstof_volgnummer`, `brandstof_omschrijving`, `brandstofverbruik_gecombineerd` |

Alle geregistreerde personenauto’s worden opgehaald, zonder jaar-, merk-, model-, gewichts- of verbruiksgrens. Daarna selecteren we kentekens met precies één eenduidige brandstofrij, met de omschrijving `Benzine`. Daarmee vallen registraties met bijvoorbeeld Benzine én Elektriciteit, of Benzine én LPG, af. Dit is een afbakening op de registratie: we kunnen geen aandrijftechniek uitsluiten die niet als tweede brandstof is vastgelegd.

De analyse omvat vervolgens alleen de auto’s met bruikbaar leeggewicht én verbruik. “Alle benzineauto’s ophalen” betekent dus niet dat iedere auto uiteindelijk een punt in de analyse kan zijn. De uitval wordt geteld. De bron is het register, geen telling van alle auto’s die werkelijk rijden. Er is geen selectie op APK, verzekering of exportstatus.

**Meetkeuze:** we gebruiken uitsluitend `brandstofverbruik_gecombineerd`, in liter per 100 km. De RDW omschrijft dit als het verbruik tijdens een combinatie van gestandaardiseerde stadsrit en rit buiten de stad op een rollenbank. We voegen het aparte `brandstof_verbruik_gecombineerd_wltp` niet toe en vullen ontbrekende waarden er niet mee aan. Eén veld beperkt het mengen van definities, maar bewijst niet dat alle onderliggende historische tests exact gelijk waren. Noem de data daarom niet zonder meer “allemaal dezelfde NEDC-test”.

Volgens de [RDW-uitleg](https://www.rdw.nl/paginas/uitleg-voertuigrapport) is massa ledig voertuig het gewicht zonder mensen, lading en brandstof. De eerste toelating is de eerste registratie, ook buiten Nederland, en niet noodzakelijk het productiejaar. `Model` in het dashboard is de geregistreerde handelsbenaming. Verschillende uitvoeringen of schrijfwijzen worden niet automatisch samengevoegd tot één commercieel model.

## Ophalen: waarom een lus nodig blijft

1. `maak_dataset()` loopt door de cijfers 0–9 en letters A–Z waarmee een kenteken kan beginnen. Dit is een verdeling van het werk, geen selectie van een onderzoeksjaar of merk.
2. `ophalen()` vraagt beide API’s per kentekendeel in pagina’s van maximaal 100.000 rijen op. `$limit` is de grootte van één pagina; met `$offset` volgt de volgende pagina. `$order` houdt de volgorde vast zolang de bron tijdens het ophalen niet verandert.
3. Alleen de voertuigentabel selecteert `voertuigsoort='Personenauto'`. De brandstoftabel bevat alle brandstoffen, zodat de code combinaties zoals benzine en elektriciteit kan uitsluiten.
4. `vraag_api()` wacht bij een tijdelijke fout vijf seconden en probeert maximaal drie keer. Als een aanvraag definitief mislukt, toont de app een foutmelding in plaats van een gedeeltelijke conclusie.
5. Per beginteken koppelt `opschonen()` de twee tabellen en telt wat er afvalt. Daarna zet `pd.concat()` de schone delen onder elkaar. `return auto, controle` geeft beide tabellen **direct** aan `app.py`: er wordt niets op schijf geschreven.

Verwerken per beginteken voorkomt dat beide volledige ruwe brontabellen tegelijk in het geheugen moeten staan. Toch is de totale analyse groot: ongeveer zes miljoen bruikbare auto’s in de eerdere run. De API kan tijdens het ophalen veranderen. Paginering met `$offset` is daardoor geen vaste historische momentopname; een nieuwe run kan andere cijfers geven.

## Koppelen en datakwaliteit

De eenheid is één geregistreerde auto, niet één uniek automodel. Veel voorkomende uitvoeringen tellen dus vaker mee. De sleutel is `kenteken`; na de brandstofselectie gebruiken we een inner join met `validate='one_to_one'`. Daarmee weigert pandas een onbedoelde vermenigvuldiging van rijen.

| Controle                                           | Keuze en reden                                                                                                 |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Exact dubbele rijen                                | Eén exemplaar houden, anders telt dezelfde registratie vaker mee.                                             |
| Verschillende voertuigrijen met hetzelfde kenteken | Alle betrokken rijen uitsluiten; niet willekeurig een gewicht kiezen.                                          |
| Meerdere brandstofrijen per kenteken               | Uitsluiten volgens de afbakening uitsluitend benzine; ook onduidelijke meervoudige registraties vallen af.     |
| Ontbrekend of niet-numeriek gewicht/verbruik       | Uitsluiten: de onderzoeksvraag vereist beide metingen.                                                         |
| Gewicht/verbruik ≤ 0                              | Uitsluiten: niet bruikbaar als benzineverbruik of leeggewicht.                                                 |
| Hoge positieve waarden                             | Behouden: zonder inhoudelijk bewijs geen willekeurige bovengrens opleggen.                                     |
| Ontbrekend merk/model                              | “Onbekend”; bruikbare metingen behouden.                                                                     |
| Ontbrekend/ongeldig toelatingsjaar                 | Bewaren als 0; wel in hoofdanalyse, niet in periodevergelijking. Jaren buiten 1886–huidig jaar zijn ongeldig. |

De rechtstreeks berekende tellingen in de uitklap van de app tonen aantallen vóór en na de join, ontbrekende waarden, niet-numerieke waarden, duplicaten en hoeveel unieke auto’s wegens onbruikbare metingen verdwijnen. Losse probleemtellingen kunnen overlappen: tel die niet op als totale uitval. De app berekent het bereik, gemiddelde en de mediaan van de auto’s bij het openen.

**Dragende variabelen:** gewicht en verbruik. Merk en handelsbenaming dienen voor selecties; eerste toelating helpt een alternatieve verklaring onderzoeken. Kenteken dient alleen voor koppelen en ontbreekt in het analysebestand. We corrigeren geen merknamen op gevoel, vullen geen verbruik met gemiddelden in en verwijderen geen zeldzame uitvoeringen. Zulke ingrepen kunnen het verband veranderen.

## Analyse en dashboard

1. **Scatterplot bovenaan:** gewicht tegenover verbruik. Maximaal 5.000 reproduceerbaar gekozen punten houden de browser vlot. Transparantie vermindert overlap. De correlatie gebruikt alle geselecteerde auto’s, dus geen steekproefschatting van r.
2. **Nieuwe variabele gewichtsklasse:** `<1.000`, `1.000–1.249`, `1.250–1.499`, `1.500–1.749`, `≥1.750 kg`. De balken tonen altijd het gemiddelde verbruik; aantallen staan bij aanwijzen. Een annotatie vergelijkt de zwaarste met de lichtste aanwezige klasse in l/100 km. Dit is een groepsverschil, geen causaal effect of tijdsverandering. Vaste grenzen maken merken vergelijkbaar; gemiddelden hangen wel af van de gekozen klassen.
3. **Alternatieve verklaring:** bereken hetzelfde verband binnen eerste-toelatingsperiodes t/m 2009, 2010–2016 en vanaf 2017. Als het teken gelijk blijft, verdwijnt het patroon niet door deze grove uitsplitsing. Dat sluit invloed van leeftijd niet uit. De groepen zijn bewust breed en geen precieze wettelijke grenzen tussen testregimes. Groepen met minder dan 30 auto’s of zonder variatie krijgen geen r-balk.
4. **Conclusie:** verandert mee met de selectie en bevat beperkingen.
5. **Uitklap:** één tabel met de kwaliteitstellingen, het minimum en maximum. De drie hoofdgrafieken beantwoorden samen de vraag; de verdeling wordt niet in een extra grafiek getoond.

### De statistiek uitleggen

Pearson-correlatie `r` ligt tussen −1 en +1. Bij een positieve waarde gaan hogere gewichten samen met hogere verbruiken; bij een negatieve waarde met lagere verbruiken. Rond 0 is er weinig rechtlijnig verband, maar er kan nog een niet-lineair verband zijn. De grens ±0,10 in de tekst is alleen een praktische formulering voor “weinig lineair verband”, geen statistische toets. We tonen daarom altijd de werkelijke r.

Het **gemiddelde** is de som gedeeld door het aantal waarden. De **mediaan** is de middelste waarde na sorteren (bij een even aantal het gemiddelde van de twee middelste). Voor `[4, 5, 15]` is het gemiddelde 8 en de mediaan 5. In de code zijn dit `.mean()` en `median()`. De balken gebruiken altijd het gemiddelde; de mediaan staat alleen bij de beschrijvende cijfers en in de kwaliteitsuitklap.

We hebben geen p-waardes of betrouwbaarheidsintervallen toegevoegd. Bij miljoenen registraties is een heel klein verschil al snel statistisch aantoonbaar, terwijl selectievertekening en praktisch effect hier belangrijker zijn. Dit is bovendien geen aselecte steekproef van alle auto’s op de weg.

### Interactie en ontwerp

- **Dropdown merk:** beperkt de auto’s en de beschikbare modellen.
- **Dropdown model:** beperkt daarna de selectie; model en gewichtsbereik resetten bij een andere bovenliggende keuze.
- **Slider gewicht:** werkt door in de figuren, statistieken en conclusie. Bij één mogelijk gewicht staat een melding in plaats van een ongeldige slider.
- **Checkbox trendlijn:** Toont of verbergt de oranje gestreepte trendlijn in de puntenwolk.

We gebruiken één rustige blauwe kleur, tekstlabels, een nul-lijn in de correlatiegrafiek en logische posities. De interpretatie hangt niet van rood/groen af. De hoofdfiguren staan onder elkaar, waardoor ze op kleinere schermen beter leesbaar blijven. Geen grote kentekentabel, kaart, extra voorspelling of uitgebreid bedieningspaneel: die zijn niet nodig voor deze vraag.

## Grenzen en reflectie

- Ontbrekend verbruik kan vooral bij bepaalde leeftijden, merken of importauto’s voorkomen. De bruikbare selectie kan daardoor afwijken van alle benzinepersonenauto’s.
- Het register en de gemeten verbruiken zijn geen actuele praktijkmetingen. Rijgedrag, onderhoud en omstandigheden beïnvloeden praktijkverbruik.
- Gewicht is niet experimenteel veranderd. Motorvermogen, aerodynamica en uitvoering kunnen zowel gewicht als verbruik beïnvloeden.
- De periodeanalyse is een eerste controle, geen volledige correctie voor verstorende variabelen.
- Uitschieters blijven behouden en kunnen Pearson r en gemiddelden beïnvloeden. Een volgende stap is onderzoeken welke extreme registraties inhoudelijk kloppen en vergelijken met rangcorrelatie of medianen per klasse.
- Een verdere verbetering is missings per merk en toelatingsperiode vergelijken, of motorvermogen toevoegen. Dat valt buiten deze compacte weekopdracht.

## Presentatiescript — maximaal 10 minuten

| Tijd        | Wat laten we zien en vertellen?                                                                                                                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0:00–1:00  | Stel de groep voor. “We onderzoeken of zwaardere benzinepersonenauto’s meer geregistreerd brandstofverbruik hebben. Dit is relevant voor iemand die een auto vergelijkt.”                                       |
| 1:00–2:00  | Open kwaliteitsuitklap. Benoem de twee API’s, kenteken als sleutel, uitsluitend benzine, aantal voor/na join en uiteindelijke analyseomvang. Lees de echte waarden uit de app.                                    |
| 2:00–4:00  | Wijs de scatterplot aan. Noem r, richting en gemiddeld verbruik uit de actuele selectie. Zet de trendlijn uit en aan: alleen de oranje lijn verandert. Leg uit dat alleen het aantal getekende punten begrensd is. |
| 4:00–5:00  | Kies een bekend merk en daarna een model. Maak het gewichtsbereik smaller. Leg uit dat dezelfde filters alle analyses veranderen.                                                                                  |
| 5:00–7:00  | Wijs de lichtste en zwaarste aanwezige klasse en de verschilannotatie aan. Noem het verschil tussen de gemiddelde verbruiken in l/100 km.                                                                          |
| 7:00–8:00  | Zet merk en model terug op alle. Bespreek of de richting binnen toelatingsperiodes gelijk blijft. Dit controleert een mogelijke andere verklaring.                                                                 |
| 8:00–9:00  | Beantwoord de hoofdvraag met de getoonde r en het klassenverschil. Noem ontbrekende verbruiken, testverbruik versus praktijk en correlatie versus oorzaak.                                                         |
| 9:00–10:00 | Reflectie: “We kozen een beperkte set grafieken en één verbruiksveld. Een volgende stap is ontbrekende waarden per leeftijd onderzoeken of motorvermogen toevoegen.”                                           |

## Bronnen en hulp bij code

Gebruikte technische patronen zijn aangepast aan deze RDW-data:

- [Socrata paginering met limit](https://dev.socrata.com/docs/queries/limit.html) en [vaste sortering](https://dev.socrata.com/docs/queries/order.html): paginagrootte, offset en volgorde in `ophalen`.
- [Requests quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/): parameters, timeout en HTTP-foutafhandeling in `vraag_api`.
- [pandas merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html): inner join en controle op één-op-éénrelatie.
- [pandas cut](https://pandas.pydata.org/docs/reference/api/pandas.cut.html) en [corr](https://pandas.pydata.org/docs/reference/api/pandas.Series.corr.html): klassen en correlatie.
- [Streamlit cache_data](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data) en [widgets](https://docs.streamlit.io/develop/api-reference/widgets): cache en bedieningen.
- [Plotly scatterplots](https://plotly.com/python/line-and-scatter/) en [annotaties](https://plotly.com/python/text-and-annotations/): interactieve grafieken en verschilannotatie.
- [Streamlit publiceren](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy): GitHub → Community Cloud.

## Code in gewone taal

Lees eerst `data.py` van boven naar beneden en daarna `app.py`. Bij `def` wordt een functie beschreven; de regels worden pas uitgevoerd wanneer die functie wordt aangeroepen.

| Codebegrip                              | Betekenis in dit project                                                                                                           |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `DataFrame`                           | Een tabel, vergelijkbaar met een werkblad.                                                                                         |
| `for` en `while`                    | Hetzelfde werk herhalen voor kentekendelen en API-pagina’s.                                                                       |
| `pd.to_numeric(..., errors='coerce')` | Probeer tekst een getal te maken; wat niet lukt wordt ontbrekend.                                                                  |
| `.loc[voorwaarde]`                    | Alleen rijen bewaren die aan een voorwaarde voldoen.                                                                               |
| `.merge(..., on='kenteken')`          | Twee tabellen verbinden via hetzelfde kenteken.                                                                                    |
| `.groupby(...)`                       | De tabel in groepen verdelen. De lus behandelt iedere groep apart en berekent het gemiddelde.                                      |
| `pd.cut(...)`                         | Getallen indelen in vooraf gekozen intervallen.                                                                                    |
| `@st.cache_data`                      | De uitkomst in het geheugen onthouden, zodat niet bij iedere klik opnieuw wordt gedownload. Bij een herstart vervalt die uitkomst. |

De code gebruikt geen machinelearningmodel. Het verband wordt rechtstreeks berekend met de pandas-functie `.corr()`. Verschillen tussen correlaties in de periodegrafiek kunnen ook door verschillende gewichtsbereiken ontstaan: vergelijk r niet alsof het een verbruiksverschil in liters is.

## Leesroute voor de eenvoudigere code

De bestanden hebben nu korte uitlegblokken direct bij de moeilijke regels. Er zijn meer commentaarregels en witregels om de stappen afzonderlijk te lezen.

1. Begin in `data.py` met `opschonen`. Hier zie je hoe een tabel wordt gefilterd, wat de koppeling op kenteken doet en welke rijen afvallen.
2. Lees `vraag_api` en `ophalen`. De instellingen met een `$` horen bij de RDW-API. De `while`-lus haalt steeds de volgende pagina op. Die lus is nodig om alle rijen te gebruiken.
3. Lees `maak_dataset`. De `for`-lus herhaalt het werk voor ieder eerste kentekenteken en telt de kwaliteitscijfers op. De laatste regel geeft de autodata en de tellingen direct terug aan de app.
4. Lees `app.py` vanaf `# 1. VRAAG EN DATA LADEN`. De genummerde blokken volgen de volgorde van het dashboard.
5. Zoek in de code de merkselectie, `bereken_verband` en de lus over de gewichtsklassen. Leg voor ieder blok in één zin uit welke tabel erin gaat en welk resultaat eruit komt.

### Constructies die je echt moet begrijpen

- `auto['gewicht']` kiest één kolom. `auto[auto['gewicht'] > 1000]` kiest de rijen die aan de voorwaarde voldoen.
- `&` is **en**, `|` is **of** bij voorwaarden op pandas-kolommen. Zet iedere vergelijking tussen haakjes.
- `len(tabel)` telt rijen. `tabel['kolom'].nunique()` telt verschillende waarden.
- `isna()` herkent ontbrekende waarden. Bij `True`/`False`-waarden telt `.sum()` hoeveel keer de voorwaarde waar is.
- `concat` zet tabellen onder elkaar; `merge` koppelt kolommen via dezelfde sleutel.
- `regels.append(...)` voegt één resultaat aan een lijst toe. `pd.DataFrame(regels)` maakt daarna de resultatentabel.
- `iloc[0]` kiest de eerste rij; `iloc[-1]` de laatste rij.
- `f'{waarde:.2f}'` maakt tekst van een getal en toont twee decimalen.
- `try/except` vangt een fout op; `raise` geeft de fout door; `st.stop()` stopt het dashboard netjes.
- `@st.cache_resource` onthoudt de tabellen in het geheugen zolang het app-proces draait. Een herstart downloadt opnieuw. `@st.cache_resource` bewaart één gedeelde dataset zonder voor iedere aanroep een nieuwe kopie te maken. Daarom lezen we `auto` en `controle` alleen; vóór het toevoegen van analysekolommen maken we een eigen kopie van de selectie met `.copy()`.

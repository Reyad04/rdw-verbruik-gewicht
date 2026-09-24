# STAP 2: dashboard met Streamlit.
# Lees van boven naar beneden: laden → filters → grafieken → conclusie.
# In pandas betekent tabel['kolom'] dat je één kolom uit een tabel kiest.

import pandas as pd
import plotly.express as px
import streamlit as st
from data import maak_dataset

st.set_page_config(page_title='Gewicht en verbruik', layout='centered')
BLAUW = '#17628a'
LABELS = {'gewicht': 'Leeggewicht (kg)', 'verbruik': 'Verbruik (l/100 km)', 'klasse': 'Gewichtsklasse (kg)', 'aantal': 'Aantal auto’s'}

# Streamlit bewaart één gedeelde versie van de tabellen in het geheugen.
# We lezen auto en controle alleen. Verderop krijgt de selectie een eigen copy().
# Een filterklik start de download dus niet opnieuw; een herstart wel.
@st.cache_resource(max_entries=1, show_spinner='RDW-data via de API ophalen. Dit kan lang duren; de voortgang staat in de logs.')
def laden():
    # De twee tabellen komen rechtstreeks uit data.py terug naar dit dashboard.
    return maak_dataset()

def bereken_verband(tabel):
    """Geef Pearson r terug, of None als berekenen niet zinvol is."""
    if len(tabel) < 3:
        return None
    # nunique telt het aantal VERSCHILLENDE waarden. Zonder variatie bestaat r niet.
    if tabel['gewicht'].nunique() < 2 or tabel['verbruik'].nunique() < 2:
        return None
    return tabel['gewicht'].corr(tabel['verbruik'])

def toon_grafiek(figuur):
    """Dezelfde rustige opmaak voor de drie grafieken."""
    figuur.update_layout(template='plotly_white', showlegend=False, height=380, font_size=13, margin=dict(l=10, r=10, t=45, b=10))
    st.plotly_chart(figuur, width='stretch')

# 1. VRAAG EN DATA LADEN
st.title('Zwaardere auto, hoger verbruik?')
st.write('Wat is het verband tussen leeggewicht en geregistreerd gecombineerd ' 'brandstofverbruik van uitsluitend-benzinepersonenauto’s in het RDW-register?')
st.caption('Leeggewicht is zonder mensen, lading en brandstof. Het verbruik is ' 'rollenbankverbruik in liter per 100 km; praktijkverbruik kan afwijken.')
try:
    auto, controle = laden()
except Exception as fout:
    st.error('Ophalen is niet gelukt. Probeer later opnieuw; de app begint dan opnieuw bij de RDW-API.')
    with st.expander('Technische melding'):
        st.write(str(fout))
    # Voer de grafiekcode niet uit als de data niet beschikbaar zijn.
    st.stop()

# 2. FILTERS: ieder volgend filter werkt op de overgebleven auto’s.
st.sidebar.header('Kies je vergelijking')
# Unieke merken, alfabetisch gesorteerd.
merken = sorted(auto['merk'].unique().tolist())
merk = st.sidebar.selectbox('Merk', ['Alle merken'] + merken)
selectie = auto
modellen = []
if merk != 'Alle merken':
    selectie = selectie[selectie['merk'] == merk]
    modellen = sorted(selectie['model'].unique().tolist())

# Een key geeft een widget een identiteit. Bij een ander merk reset het model.
model = st.sidebar.selectbox('Model (RDW-handelsbenaming)', ['Alle modellen'] + modellen, key=f'model-{merk}', disabled=(merk == 'Alle merken'), help='Kies eerst een merk.')
if model != 'Alle modellen':
    selectie = selectie[selectie['model'] == model]

minimum = int(selectie['gewicht'].min())
maximum = int(selectie['gewicht'].max())
if minimum < maximum:
    van, tot = st.sidebar.slider('Leeggewicht (kg)', minimum, maximum, (minimum, maximum), key=f'gewicht-{merk}-{model}')
    # & betekent EN: een auto moet aan beide voorwaarden voldoen.
    binnen_bereik = (selectie['gewicht'] >= van) & (selectie['gewicht'] <= tot)
    selectie = selectie[binnen_bereik]
else:
    st.sidebar.caption(f'Alle geselecteerde auto’s wegen {minimum} kg.')

# De checkbox toont of verbergt een duidelijke lijn in de puntenwolk.
toon_trendlijn = st.sidebar.checkbox('Toon trendlijn', value=True)
st.sidebar.caption('Merk, model en gewicht werken op alle grafieken. ' 'Het vinkje toont de gestreepte lijn in de puntenwolk.')
if selectie.empty:
    st.warning('Geen auto’s in dit bereik. Kies een ruimer gewichtsbereik.')
    st.stop()

# copy voorkomt dat nieuwe analysekolommen de oorspronkelijke tabel wijzigen.
selectie = selectie.copy()
r = bereken_verband(selectie)
if r is None:
    r_tekst = 'Niet berekenbaar'
else:
    # .2f betekent: toon twee cijfers achter de komma.
    r_tekst = f'{r:.2f}'

kolom1, kolom2, kolom3 = st.columns(3)
kolom1.metric('Auto’s in selectie', f'{len(selectie):,}')
kolom2.metric('Gemiddeld verbruik', f'{selectie["verbruik"].mean():.2f} l/100 km')
kolom2.metric('Mediaan verbruik', f'{selectie["verbruik"].median():.2f} l/100 km')
kolom3.metric('Verband (r)', r_tekst)
st.caption(f'RDW-data opgehaald op {controle["einde"].iloc[0]}. ' 'r ligt tussen −1 en +1: het teken geeft de richting, de afstand tot 0 de lineaire sterkte.')

# 3. SCATTERPLOT: GEWICHT TEGENOVER VERBRUIK
st.subheader('1. Gewicht en verbruik vergelijken')
titel = 'Weinig lineair verband'
if r is not None:
    if r >= 0.10:
        titel = 'Hoger gewicht, hoger verbruik'
    elif r <= -0.10:
        titel = 'Hoger gewicht, lager verbruik'

# Miljoenen punten tekenen maakt de browser traag. Alleen deze TEKENING krijgt
# maximaal 5.000 willekeurige punten. Alle berekeningen gebruiken de hele selectie.
# random_state=42 zorgt bij dezelfde dataset voor dezelfde gekozen punten.
aantal_punten = min(5000, len(selectie))
punten = selectie.sample(n=aantal_punten, random_state=42)
figuur = px.scatter(punten, x='gewicht', y='verbruik', title=titel, labels=LABELS, hover_data=['merk', 'model', 'jaar'], opacity=0.25, color_discrete_sequence=[BLAUW])
if toon_trendlijn and r is not None:
    # De rechte lijn gebruiken we als samenvatting van ALLE geselecteerde auto’s.
    # De uiteinden liggen bij de getekende punten, zodat de schaal leesbaar blijft.
    helling = selectie['gewicht'].cov(selectie['verbruik']) / selectie['gewicht'].var()
    begin = selectie['verbruik'].mean() - helling * selectie['gewicht'].mean()
    links = punten['gewicht'].min()
    rechts = punten['gewicht'].max()
    figuur.add_scatter(x=[links, rechts], y=[begin + helling * links, begin + helling * rechts], mode='lines', line=dict(color='#D55E00', width=4, dash='dash'))
toon_grafiek(figuur)
st.write(f'De grafiek toont {aantal_punten:,} punten. De correlatie r = {r_tekst} ' f'is berekend over alle {len(selectie):,} geselecteerde auto’s. ' 'Transparantie maakt overlappende punten zichtbaar.')

# 4. NIEUWE VARIABELE: GEWICHTSKLASSE
st.subheader('2. Hoeveel verschillen gewichtsklassen?')
# cut deelt getallen in klassen in. right=False betekent dat de linkergrens
# meetelt: 1.000 kg hoort dus bij 1.000–1.249. inf betekent geen bovengrens.
selectie['klasse'] = pd.cut(selectie['gewicht'], bins=[0, 1000, 1250, 1500, 1750, float('inf')], right=False, labels=['< 1.000', '1.000–1.249', '1.250–1.499', '1.500–1.749', '≥ 1.750'])
# groupby verdeelt de tabel in groepen. In de lus bekijken we één klasse tegelijk.
# observed=True slaat lege klassen over. Elke append voegt één resultaatrij toe.
regels = []
for naam, groep in selectie.groupby('klasse', observed=True):
    waarde = groep['verbruik'].mean()
    regels.append({'klasse': str(naam), 'verbruik': waarde, 'aantal': len(groep)})
klassen = pd.DataFrame(regels)
figuur = px.bar(klassen, x='klasse', y='verbruik', text_auto='.2f', hover_data=['aantal'], labels=LABELS, title='Gemiddeld verbruik: licht naar zwaar', color_discrete_sequence=[BLAUW])
# Een balk begint bij nul voor een eerlijke vergelijking.
figuur.update_yaxes(rangemode='tozero')

if len(klassen) > 1:
    # iloc[0] kiest de eerste rij; iloc[-1] de laatste rij.
    lichtste = klassen.iloc[0]
    zwaarste = klassen.iloc[-1]
    verschil = zwaarste['verbruik'] - lichtste['verbruik']
    figuur.add_annotation(x=zwaarste['klasse'], y=zwaarste['verbruik'], showarrow=True, text=f'Verschil met lichtste klasse:<br>{verschil:+.2f} l/100 km', ay=-55)
    st.write(f'Het gemiddelde verbruik in de zwaarste aanwezige klasse verschilt ' f'{verschil:+.2f} l/100 km van de lichtste. Dit is een verschil tussen groepen.')
toon_grafiek(figuur)
st.caption('Vaste klassen houden merken vergelijkbaar. Het aantal auto’s staat bij aanwijzen ' 'van een balk.')

# 5. ANDERE MOGELIJKE VERKLARING: EERSTE TOELATING
st.subheader('3. Kan het toelatingsjaar het patroon verklaren?')
st.write('Nieuwere auto’s kunnen andere motortechniek hebben. We berekenen daarom het ' 'verband ook binnen drie toelatingsperiodes. Eerste toelating is niet noodzakelijk productiejaar.')
selectie['periode'] = pd.cut(selectie['jaar'], bins=[1885, 2009, 2016, 9999], labels=['t/m 2009', '2010–2016', 'vanaf 2017'])
regels = []
for naam, groep in selectie.groupby('periode', observed=True):
    waarde = bereken_verband(groep)
    if waarde is not None and len(groep) >= 30:
        regels.append({'periode': str(naam), 'r': waarde, 'aantal': len(groep)})

if len(regels) > 0:
    periodes = pd.DataFrame(regels)
    figuur = px.bar(periodes, x='periode', y='r', text_auto='.2f', hover_data=['aantal'], title='Verband per toelatingsperiode', color_discrete_sequence=[BLAUW], labels={'periode': 'Eerste toelating', 'r': 'Verband gewicht–verbruik (r)'})
    figuur.update_yaxes(range=[-1, 1])
    figuur.add_hline(y=0, line_color='#333333')
    toon_grafiek(figuur)
    # all controleert of een voorwaarde voor ALLE getoonde periodes geldt.
    alle_positief = (periodes['r'] > 0).all()
    alle_negatief = (periodes['r'] < 0).all()
    if r is not None and ((r > 0 and alle_positief) or (r < 0 and alle_negatief)):
        st.write('De richting blijft in alle getoonde periodes gelijk aan het totaal. ' 'Deze grove uitsplitsing neemt het patroon dus niet weg.')
    else:
        st.write('De richting is niet overal gelijk aan het totaal. ' 'De samenstelling naar toelatingsperiode kan meespelen.')
else:
    st.info('Te weinig auto’s of variatie per periode om een verband te tonen.')
st.caption('Een onbekend jaar telt wel mee in de hoofdanalyse. Per periode zijn minimaal ' '30 auto’s nodig: een praktische ondergrens, geen statistische significantietoets.')

# 6. CONCLUSIE EN VERANTWOORDING
st.subheader('Conclusie voor jouw selectie')
if r is None:
    st.write('Er zijn te weinig auto’s of verschillende waarden om r te berekenen.')
elif r >= 0.10:
    st.write(f'r = {r:.2f}: zwaardere auto’s hebben gemiddeld een hoger geregistreerd verbruik.')
    st.write(f'Jouw selectie: gemiddeld {selectie["verbruik"].mean():.2f}, ' f'mediaan {selectie["verbruik"].median():.2f} l/100 km. ' 'Hoge positieve waarden zijn behouden; zonder inhoudelijke controle zijn ze niet als fout verwijderd.')
elif r <= -0.10:
    st.write(f'r = {r:.2f}: zwaardere auto’s hebben gemiddeld een lager geregistreerd verbruik.')
    st.write(f'Jouw selectie: gemiddeld {selectie["verbruik"].mean():.2f}, ' f'mediaan {selectie["verbruik"].median():.2f} l/100 km. ' 'Hoge positieve waarden zijn behouden; zonder inhoudelijke controle zijn ze niet als fout verwijderd.')
else:
    st.write(f'r = {r:.2f}: er is weinig lineair verband tussen gewicht en verbruik.')
    st.write(f'Jouw selectie: gemiddeld {selectie["verbruik"].mean():.2f}, ' f'mediaan {selectie["verbruik"].median():.2f} l/100 km. ' 'Hoge positieve waarden zijn behouden; zonder inhoudelijke controle zijn ze niet als fout verwijderd.')
st.write('Dit bewijst geen oorzaak. Motorvermogen, uitvoering en toelatingsjaar kunnen meespelen. ' 'Auto’s zonder bruikbare metingen ontbreken; testverbruik kan afwijken van praktijkverbruik.')

with st.expander('Gegevenskwaliteit en bronnen'):
    st.write('Deze tellingen horen bij de volledige download, vóór dashboardfilters. ' 'Afzonderlijke probleemtellingen kunnen overlappen.')
    st.dataframe(controle[['controle', 'aantal']], hide_index=True, width='stretch')
    st.write(f'Gewicht in de volledige analyse: {auto["gewicht"].min():.0f}–{auto["gewicht"].max():.0f} kg. ' f'Verbruik: {auto["verbruik"].min():.1f}–{auto["verbruik"].max():.1f} l/100 km.')
    st.markdown('[RDW voertuigen](https://opendata.rdw.nl/d/m9d7-ebf2) · ' '[RDW brandstof](https://opendata.rdw.nl/d/8ys7-d773) · ' '[Uitleg voertuigrapport](https://www.rdw.nl/paginas/uitleg-voertuigrapport)')
    st.caption('Meetveld: brandstofverbruik_gecombineerd. Het afzonderlijke WLTP-veld ' 'wordt niet toegevoegd of gebruikt als vervanging. Zie README voor keuzes en bronnen.')

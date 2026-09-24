# STAP 1: RDW-data ophalen, koppelen en opschonen.
# Lees de functies in deze volgorde: vraag_api → ophalen → opschonen → maak_dataset.
# Een functie is een stukje code met een naam. Die wordt pas uitgevoerd als je het aanroept, bijvoorbeeld met maak_dataset().

import time
import pandas as pd
import requests

# De data blijft alleen in het geheugen. Er wordt geen CSV-bestand gemaakt.
VOERTUIGEN = 'm9d7-ebf2'
BRANDSTOF = '8ys7-d773'
PAGINAGROOTTE = 100000

# Een dictionary verbindt een sleutel (datasetcode) aan een waarde (kolomlijst).
# Alleen deze kolommen zijn nodig; minder kolommen betekent minder downloadwerk.
KOLOMMEN = {
    VOERTUIGEN: ['kenteken', 'merk', 'handelsbenaming', 
                'massa_ledig_voertuig', 'datum_eerste_toelating'],
    BRANDSTOF: ['kenteken', 'brandstof_volgnummer', 
                'brandstof_omschrijving', 'brandstofverbruik_gecombineerd'],
}

def vraag_api(dataset, instellingen):
    # Vraag één pagina op. Probeer bij een storing maximaal drie keer.
    url = f'https://opendata.rdw.nl/resource/{dataset}.json'
    for poging in range(3):
        try:
            # params voegt de instellingen aan het webadres toe.
            # timeout voorkomt dat één aanvraag eindeloos blijft wachten.
            antwoord = requests.get(url, params=instellingen, timeout=180)
            # Een HTTP-fout gaat naar het except-blok.
            antwoord.raise_for_status()
            # De API-tekst wordt een Python-lijst.
            return antwoord.json()
        except (requests.RequestException, ValueError):
            # range(3) telt 0, 1, 2: dit is poging 3.
            if poging == 2:
                # Geef de fout door aan het dashboard.
                raise
            # Wacht vijf seconden vóór een nieuwe poging.
            time.sleep(5)


def ophalen(dataset, teken):
    # Haal alle rijen op waarvan het kenteken met dit teken begint.
    paginas = []
    overgeslagen = 0
    selectie = f"starts_with(kenteken, '{teken}')"
    if dataset == VOERTUIGEN:
        selectie += " AND voertuigsoort = 'Personenauto'"
    while True:
        # Dit zijn instellingen van de RDW-API:
        # select = kolommen; where = selectie; order = vaste rijvolgorde;
        # limit = rijen per pagina; offset = al opgehaalde rijen overslaan.
        instellingen = {
            '$select': ','.join(KOLOMMEN[dataset]),
            '$where': selectie,
            '$order': 'kenteken, :id',
            '$limit': PAGINAGROOTTE,
            '$offset': overgeslagen,
        }
        rijen = vraag_api(dataset, instellingen)
        if len(rijen) == 0:
            break
        # Maak van de lijst een tabel. columns bewaart ook lege bronkolommen.
        pagina = pd.DataFrame(rijen, columns=KOLOMMEN[dataset])
        paginas.append(pagina)
        overgeslagen = overgeslagen + len(pagina)
        if len(pagina) < PAGINAGROOTTE:
            # Een onvolledige pagina is de laatste pagina.
            break
    if len(paginas) == 0:
        tabel = pd.DataFrame(columns=KOLOMMEN[dataset])
    else:
        # concat zet tabellen ONDER elkaar; dit is nog geen koppeling op kenteken.
        tabel = pd.concat(paginas, ignore_index=True)
    # Deze tabel gaat direct terug naar maak_dataset; niets wordt opgeslagen.
    return tabel

def opschonen(voertuigen, brandstof):
    # Koppel de tabellen en tel wat bij iedere stap overblijft.
    telling = {}
    telling['Opgehaalde personenautorijen'] = len(voertuigen)
    telling['Opgehaalde brandstofrijen (alle voertuigsoorten)'] = len(brandstof)
    # duplicated geeft True bij een herhaalde rij. sum telt de True-waarden.
    telling['Exact dubbele rijen voertuigen'] = int(voertuigen.duplicated().sum())
    telling['Exact dubbele rijen brandstof'] = int(brandstof.duplicated().sum())
    voertuigen = voertuigen.drop_duplicates()
    brandstof = brandstof.drop_duplicates()
    # keep=False markeert ALLE rijen van een dubbel kenteken.
    # Bij verschillende voertuigrijen kiezen we niet willekeurig één gewicht.
    dubbel = voertuigen['kenteken'].duplicated(keep=False)
    telling['Conflicterende voertuigrijen verwijderd'] = int(dubbel.sum())
    voertuigen = voertuigen[dubbel == False]
    telling['Unieke personenauto’s voor join'] = len(voertuigen)
    # Een benzinehybride heeft ook een andere brandstofrij.
    # Verwijder daarom eerst kentekens met meerdere rijen; selecteer daarna Benzine.
    enkel = brandstof.drop_duplicates(subset='kenteken', keep=False)
    benzine = enkel[enkel['brandstof_omschrijving'] == 'Benzine']
    telling['Unieke uitsluitend-benzinekentekens voor join (alle soorten)'] = len(benzine)
    # merge zet bij hetzelfde kenteken de kolommen NAAST elkaar.
    # inner houdt alleen kentekens uit beide tabellen.
    # one_to_one controleert dat iedere auto hoogstens één match heeft.
    auto = voertuigen.merge(benzine, on='kenteken', how='inner', validate='one_to_one')
    telling['Benzinepersonenauto’s na join'] = len(auto)
    telling['Personenauto’s zonder eenduidige uitsluitend-benzinematch'] = len(voertuigen) - len(auto)
    auto = auto.rename(columns={
        'massa_ledig_voertuig': 'gewicht',
        'brandstofverbruik_gecombineerd': 'verbruik',
        'handelsbenaming': 'model',
    })
    for kolom in ['gewicht', 'verbruik']:
        oorspronkelijk = auto[kolom]
        # errors='coerce' maakt onleesbare getallen ontbrekend (NaN).
        auto[kolom] = pd.to_numeric(oorspronkelijk, errors='coerce')
        telling[f'{kolom}: ontbrekend'] = int(oorspronkelijk.isna().sum())
        niet_numeriek = oorspronkelijk.notna() & auto[kolom].isna()
        telling[f'{kolom}: niet numeriek'] = int(niet_numeriek.sum())
        telling[f'{kolom}: nul of negatief'] = int((auto[kolom] <= 0).sum())
    # & betekent EN voor pandas-kolommen. Beide voorwaarden krijgen haakjes.
    # Een ontbrekend getal is niet groter dan nul en valt dus ook af.
    bruikbaar = (auto['gewicht'] > 0) & (auto['verbruik'] > 0)
    telling['Verwijderd wegens onbruikbaar gewicht of verbruik (uniek)'] = int((bruikbaar == False).sum())
    auto = auto[bruikbaar].copy()
    for kolom in ['merk', 'model']:
        telling[f'{kolom}: ontbrekend in analyse'] = int(auto[kolom].isna().sum())
        auto[kolom] = auto[kolom].fillna('Onbekend')
        auto[kolom] = auto[kolom].replace('', 'Onbekend')
    # Bijvoorbeeld: 20150623 wordt een datum en daarna het jaar 2015.
    datum = pd.to_datetime(auto['datum_eerste_toelating'], format='%Y%m%d', errors='coerce')
    auto['jaar'] = datum.dt.year
    auto['jaar'] = auto['jaar'].fillna(0)
    ongeldig_jaar = (auto['jaar'] < 1886) | (auto['jaar'] > pd.Timestamp.now().year)
    # | betekent OF. loc kiest hier eerst de rijen en dan de kolom die we wijzigen.
    auto.loc[ongeldig_jaar, 'jaar'] = 0
    auto['jaar'] = auto['jaar'].astype(int)
    telling['Jaar onbekend of ongeldig in analyse (behouden)'] = int((auto['jaar'] == 0).sum())
    telling['Bruikbare auto’s voor analyse'] = len(auto)
    # Kenteken was alleen nodig voor het koppelen en wordt niet verder bewaard.
    return auto[['merk', 'model', 'gewicht', 'verbruik', 'jaar']], telling

def maak_dataset():
    # Voer alle stappen uit. Alle cijfers en letters worden meegenomen.
    delen = []
    totalen = {}
    # Per beginteken verwerken beperkt het geheugengebruik.
    # Dit is GEEN steekproef: de lus neemt alle 36 mogelijke begintekens mee.
    for teken in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        print(f'RDW ophalen: kentekens beginnend met {teken}', flush=True)
        voertuigen = ophalen(VOERTUIGEN, teken)
        brandstof = ophalen(BRANDSTOF, teken)
        schoon, telling = opschonen(voertuigen, brandstof)
        # Sla herhaalde merknamen en modellen meteen op als categoriecodes.
        # Zo bewaren we niet miljoenen losse teksten tot het einde van de download.
        for kolom in ['merk', 'model']:
            schoon[kolom] = schoon[kolom].astype('category')
        delen.append(schoon)
        print(f'Deel {teken} verwerkt: {len(schoon):,} bruikbare auto’s.', flush=True)
        # De ruwe tabellen zijn verwerkt en hoeven niet in het geheugen te blijven.
        del voertuigen, brandstof
        for naam, aantal in telling.items():
            if naam not in totalen:
                totalen[naam] = 0
            totalen[naam] = totalen[naam] + aantal
    print('Download verwerkt. Delen samenvoegen...', flush=True)
    # Geef alle delen dezelfde lijst met categorieën voordat we ze samenvoegen.
    # Anders kan pandas de compacte codes weer omzetten naar losse teksten.
    for kolom in ['merk', 'model']:
        namen = []
        for deel in delen:
            namen.extend(deel[kolom].cat.categories)
        namen = pd.Index(namen).unique()
        for deel in delen:
            deel[kolom] = deel[kolom].cat.set_categories(namen)
    auto = pd.concat(delen, ignore_index=True)
    del delen, schoon, deel
    if auto.empty:
        raise ValueError('Geen bruikbare auto’s gevonden. Controleer de RDW-verbinding.')
    # Van de telling-dictionary maken we een tabel die mee naar de app gaat.
    controle = pd.DataFrame(totalen.items(), columns=['controle', 'aantal'])
    controle['einde'] = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
    geheugen_mb = auto.memory_usage(deep=True).sum() / 1_000_000
    print(f'Dataset klaar: {len(auto):,} auto’s; tabel circa {geheugen_mb:.0f} MB. Dashboard starten...', flush=True)
    return auto, controle

# Met 'python data.py' kun je de ophaalstap ook los uitvoeren.
if __name__ == '__main__':
    autos, tellingen = maak_dataset()
    print(f'Klaar: {len(autos):,} auto’s. Er zijn geen bestanden geschreven.')

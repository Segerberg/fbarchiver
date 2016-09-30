
# Arkivskript för Facebookgrupper

Detta verktyg läser ner data och filer från en öppen Facebookgrupp till en katalog på en dator. Endast filer (bilder och videoklipp) som är direktuppladdade i gruppen laddas ner (dvs inte länkat material som Youtubeklipp, länkar till andra webbplatser mm).


## Installation

Installera Python (se URL).

Installera nödvändiga python-bibliotek med:

$ pip install -r requirements.txt


## Användning

Konfigurera inställningar i filen config.py (utgå från config.py.sample). Du behöver en token från Facebook som ger access till gruppinformationen.

För att arkivera en grupp, ta reda på gruppens ID-nummer och kör:

$ python archive_group.py 1505183853108568

Resultatet sparas i en katalog med namnet <grupp-ID>_<tidsstämpel>. I katalogen hittar du en json-fil med data från Facebook samt en mediakatalog med de filer som hämtats ner.

För att skapa en läsversion i HTML av arkivdatat går det att använda den bifogade mallen och köra.

$ handlebars archive_1505183853108568.json < ../template.html > index.html

Filen index.html är en läsversion av json-datat för att underlätta för användare att snabbt få en överblick av innehållet.

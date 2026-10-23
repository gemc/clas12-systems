<!-- TRANSLATIONS:START (managed by bin/translate) -->
**Languages:** [EN](README.md) · **IT** · [日本語](README.ja.md) · [FR](README.fr.md) · [中文](README.zh.md)
<!-- TRANSLATIONS:END -->

# Sistemi GEMC CLAS12

[![Test][badge-test]][workflow-test]
[![Confronto delle geometrie ASCII][badge-ascii-geometry]][workflow-ascii-geometry]
[![Deployment][badge-deploy]][workflow-deploy]
[![Sanitizzazione][badge-sanitize]][workflow-sanitize]
[![CodeQL avanzato][badge-codeql]][workflow-codeql]
[![Doxygen][badge-doxygen]][workflow-doxygen]
[![Archivi tar dei binari][badge-binary-tarballs]][workflow-binary-tarballs]
[![Release di sviluppo notturna][badge-dev-release]][workflow-dev-release]
[![Confronto degli istogrammi HIPO][badge-hipo-histos]][workflow-hipo-histos]
[![Archivio tar per macOS][badge-macos-tarball]][workflow-macos-tarball]
[![Profilazione con Valgrind][badge-valgrind-profile]][workflow-valgrind-profile]

[badge-test]: https://github.com/gemc/clas12-systems/actions/workflows/test.yml/badge.svg
[badge-ascii-geometry]: https://github.com/gemc/clas12-systems/workflows/ASCII%20Geometry%20Comparison/badge.svg
[badge-deploy]: https://github.com/gemc/clas12-systems/actions/workflows/deploy.yml/badge.svg
[badge-sanitize]: https://github.com/gemc/clas12-systems/actions/workflows/sanitize.yml/badge.svg
[badge-codeql]: https://github.com/gemc/clas12-systems/actions/workflows/codeql.yml/badge.svg
[badge-doxygen]: https://github.com/gemc/clas12-systems/actions/workflows/doxygen.yml/badge.svg
[badge-binary-tarballs]: https://github.com/gemc/clas12-systems/actions/workflows/binary_tarballs.yml/badge.svg
[badge-dev-release]: https://github.com/gemc/clas12-systems/actions/workflows/dev_release.yml/badge.svg
[badge-hipo-histos]: https://github.com/gemc/clas12-systems/actions/workflows/hipo_histos_compare.yml/badge.svg
[badge-macos-tarball]: https://github.com/gemc/clas12-systems/actions/workflows/macos_tarball.yml/badge.svg
[badge-valgrind-profile]: https://github.com/gemc/clas12-systems/actions/workflows/valgrind_profile.yml/badge.svg
[workflow-test]: https://github.com/gemc/clas12-systems/actions/workflows/test.yml
[workflow-ascii-geometry]: https://github.com/gemc/clas12-systems/actions/workflows/clas12_geo_compare.yml
[workflow-deploy]: https://github.com/gemc/clas12-systems/actions/workflows/deploy.yml
[workflow-sanitize]: https://github.com/gemc/clas12-systems/actions/workflows/sanitize.yml
[workflow-codeql]: https://github.com/gemc/clas12-systems/actions/workflows/codeql.yml
[workflow-doxygen]: https://github.com/gemc/clas12-systems/actions/workflows/doxygen.yml
[workflow-binary-tarballs]: https://github.com/gemc/clas12-systems/actions/workflows/binary_tarballs.yml
[workflow-dev-release]: https://github.com/gemc/clas12-systems/actions/workflows/dev_release.yml
[workflow-hipo-histos]: https://github.com/gemc/clas12-systems/actions/workflows/hipo_histos_compare.yml
[workflow-macos-tarball]: https://github.com/gemc/clas12-systems/actions/workflows/macos_tarball.yml
[workflow-valgrind-profile]: https://github.com/gemc/clas12-systems/actions/workflows/valgrind_profile.yml

CLAS12 GEMC Systems contiene l'implementazione GEMC3 delle geometrie dei sistemi di rivelatori CLAS12 e dei
relativi plugin specifici. È il repository dedicato a CLAS12 che affianca l'applicazione GEMC principale e
l'API Python per la geometria:

- [`gemc/src`](https://github.com/gemc/src) fornisce l'applicazione C++ GEMC, l'integrazione con Geant4,
  i caricatori di geometrie SQLite/ASCII/CAD/GDML, l'infrastruttura per i plugin dinamici, gli streamer e
  l'ambiente `pygemc` incluso.
- [`gemc/pygemc`](https://github.com/gemc/pygemc) fornisce l'API Python usata per definire geometrie e materiali,
  scrivere database GEMC, visualizzare in anteprima la geometria con PyVista ed esportare scene VTK.js.
- [`gemc/home`](https://github.com/gemc/home) contiene il sito web pubblico di GEMC, le pagine di installazione,
  i tutorial, gli esempi e le risorse generate per la documentazione.

<br/>

## Ambito attuale

Questo repository è in fase di migrazione attiva da [`gemc/clas12Tags`](https://github.com/gemc/clas12Tags).

| Sistema | Stato | Note |
|---------|---------------------------|-----------------------------------------------------|
| `beamline` | geometria passiva | In arrivo nella prossima release: mesh native e CAD |
| `dc` | geometria e plugin | Usa coatjava come sorgente della geometria |
| `ec` | geometria e plugin | Usa coatjava e il plugin condiviso `ecal` |
| `field` | plugin | Campo magnetico mappato di CLAS12 tramite la libreria cMag |
| `ft` | geometria e plugin | In arrivo nella prossima release: FTCAL, FTHODO e FTTRK |
| `ftof` | geometria e plugin | Usa coatjava come sorgente della geometria |
| `ltcc` | geometria e plugin | Geometria nativa e CAD con superfici ottiche |
| `magnets` | geometria passiva | In arrivo nella prossima release: solenoide e tutte le mesh CAD |
| `pcal` | geometria e plugin condiviso | Usa coatjava e il plugin condiviso `ecal` |


<br/>

## GEMC

Il repository GEMC principale, [`gemc/src`](https://github.com/gemc/src), gestisce il comportamento a runtime.
Ciò include:

- la costruzione di solidi, volumi logici e posizionamenti fisici Geant4
- i plugin C++ dinamici
- la generazione di eventi, i rivelatori sensibili e gli streamer di output

Questo repository gestisce gli input specifici di CLAS12 per tale ambiente di esecuzione:

- geometria dei rivelatori, definizioni dei materiali,
- mappature di run e varianti necessarie a riprodurre la geometria CLAS12
- validazione rispetto alla geometria e all'output di riferimento CLAS12 di GEMC2

Il repository [`gemc/pygemc`](https://github.com/gemc/pygemc) definisce l'API Python.

> **Compilazione da zero — non è richiesta un'installazione preesistente di GEMC.** A partire dalla prossima
> release, i sistemi CLAS12 possono essere compilati e installati in un ambiente con il solo Geant4
> (ad esempio un'immagine `ghcr.io/gemc/g4install`) **senza GEMC installato**: quando non viene trovata
> un'installazione di GEMC, la procedura di build lo compila automaticamente dal sottoprogetto `gemc` e lo
> installa nello stesso prefisso. GEMC viene individuato in quest'ordine: un percorso esplicito
> `-Duse-gemc-location=<dir>`, poi un GEMC già installato (pkg-config o il binario `gemc` su `PATH`) e
> infine il sottoprogetto compilato dai sorgenti. **Geant4 non viene mai compilato**: deve essere già
> disponibile, altrimenti la configurazione fallisce. Tutti i workflow CI basati su container usano questa
> procedura su immagini g4install per tutte le distribuzioni supportate.

<br/>

## Workflow della geometria

Ogni sistema di rivelatori è autonomo all'interno di `geometry_src/<system>`.

In arrivo nella prossima release: [magnets](geometry_src/magnets/README.md) fornisce il solenoide nativo e
39 mesh CAD, con posizionamenti passivi e le tre configurazioni di run di GEMC2. Le sei membrane posteriori
della regione 1 del DC e i sei supporti ora appartengono a [DC](geometry_src/dc/README.md); ciascun gruppo usa
un file STL e cinque copie passive. Le schermature duplicate
`DSShield*` e `apex` sono fornite dal sistema beamline. Le piastre a monte e a valle e le camicie da vuoto
mantengono i nomi originali come mesh ottimizzate separate, con i fori degli elementi di fissaggio riempiti.

In arrivo nella prossima release: l'importazione di beamline preserva la geometria nativa di GEMC2 e fornisce 49
file STL, incluse le tre alternative del magnete trasversale. Ventuno risorse di beamline hanno
triangolazioni ridotte; il mozzo e l'adattatore sono rinominati
`Apex_Shield_Hub` e `Beamline_Adapter_1`. Le altre 28 mesh mantengono i byte originali, incluso il
riempimento in piombo della schermatura di uscita, la cui mesh è già grossolana e i cui ridotti giochi rispetto
all'involucro sono preservati. Le tre mesh del regolatore FT sono sostituite da un unico `ft_adjuster`
semplificato, con un volume uguale a quello dell'unione di riferimento.
I nove bulloni della schermatura interna usano i nomi da `FTInnerShieldAndFlange_Bolt1` a `Bolt9`, con gambi lisci
e teste semplificate che mantengono i rispettivi volumi in rame e lasciano spazio rispetto alla schermatura.
L'assieme della schermatura interna e della flangia è rinominato `FTInnerShieldAndFlange`, preservando la cavità
racchiusa al suo interno.
La flangia esterna è rinominata `FTOuterFlange` e semplificata riempiendo i suoi dodici fori per bulloni.
Il supporto esterno è rinominato `FTOuterMount`, riparato e scavato per evitare interferenze con la flangia esterna.
La schermatura interna FT a valle è rinominata `FTInnerShield`, con i fori dei bulloni chiusi,
entrambe le facce della flangia lisce e le scanalature longitudinali mantenute.
Il cono di Moller è rinominato `moller_cone`, con i fori superficiali riempiti e l'apertura allargata per evitare
interferenze con la schermatura interna FT a valle. Non è presente un plugin di digitizzazione per volumi sensibili.
Vedi le [note su beamline](geometry_src/beamline/README.md) per
le varianti, le schede di configurazione,
i controlli di qualità delle mesh, il benchmark con primari identici e gli avvisi residui sulle mesh grezze.

Una directory di sistema tipica contiene:

| File | Ruolo |
|----------------------------------------------|--------------------------------------------------------------------------------------|
| `<system>.py` | Script principale eseguibile; crea `autogeometry()` e pubblica materiali e volumi |
| `geometry.py` | Codice di costruzione della geometria |
| `materials.py` | Definizioni dei materiali del sistema |
| `variations.py` | Mappatura opzionale di run e varianti |
| `<system>.yaml` | Scheda di configurazione GEMC per esecuzioni locali rapide |
| `../coatjava_factories/CoatjavaFactory.java` | Interfaccia coatjava opzionale per i servizi di geometria Java |
| `plugin/meson.build` | Registrazione opzionale di plugin C++ per digitizzazione o altre estensioni a runtime |

Lo script principale dovrebbe essere eseguibile e avviabile direttamente dalla sua directory:

```shell
cd geometry_src/dc
./dc.py 
```

Usa le opzioni PyVista di `pygemc` quando un sistema è pronto per l'ispezione visiva:

```shell
./dc.py -pvb
```

Esegui GEMC con la scheda di configurazione locale:

```shell
gemc dc.yaml
gemc dc.yaml -gui
```

Le righe relative ai volumi sensibili selezionano il plugin di runtime tramite il campo `digitization` del volume.
La chiave opzionale `digitization` in una voce YAML `gsystem` ha uno scopo più specifico: indica a GEMC quale
plugin con un nome diverso interrogare prima di analizzare le opzioni, come quando i sistemi `ec` e `pcal`
condividono `ecal.gplugin`. FT ha tre nomi per i volumi sensibili (`ft_cal`, `ft_hodo` e `ft_trk`), quindi il suo YAML
mantiene una semplice voce `name: ft`. Il plugin `ft.gplugin`, dedicato alle sole opzioni, registra tutti e tre
i domini durante l'interrogazione iniziale; il caricamento della geometria individua e carica quindi i tre
digitizzatori a partire dalle righe dei volumi sensibili.

<br/>

## Controlli di riferimento

Usa `scripts/compare_ascii_databases.py` per confrontare i database ASCII GEMC3 generati (geometria e
materiali) con i file di riferimento corrispondenti di [`gemc/clas12Tags`](https://github.com/gemc/clas12Tags):

```shell
scripts/compare_ascii_databases.py dc
```

Senza argomenti che specifichino i sistemi, lo script controlla ogni implementazione locale
`geometry_src/<system>/<system>.py`. Lo script associa le colonne ASCII di GEMC2 e GEMC3 a campi geometrici
comuni — nome, volume madre, posizione, rotazione, solido, dimensioni, materiale, digitizzazione
(`sensitivity` di GEMC2) e identificatore (`identifiers` di GEMC2, espanso nella forma canonica `name=value`) —
e confronta solo i valori di tali campi per nome di volume, così che differenze di formattazione e di ordine
delle colonne non nascondano corrispondenze effettive tra le geometrie. I materiali vengono confrontati allo stesso
modo per nome (densità, componenti, proprietà ottiche e di scintillazione), per i sistemi che definiscono
materiali personalizzati. Le rappresentazioni numeriche e gli ordini degli array dei policoni di GEMC2/GEMC3
vengono normalizzati prima del confronto.

Quando un campo differisce, lo script stampa le discrepanze per ciascun campo e termina con codice di uscita `1`;
un'esecuzione in cui tutto corrisponde termina con codice di uscita `0`.

<br/>

## Posizionamento e rotazioni

GEMC3 supporta entrambe le convenzioni di posizionamento Geant4 tramite `GVolume.g4placement_type`:

| Valore | Significato |
|-----------|----------------------------------------------------------------------------------------|
| `active` | Comportamento GEMC3 predefinito; usa `G4Transform3D(rotation, translation)` |
| `passive` | Comportamento compatibile con GEMC2/clas12Tags; usa `G4PVPlacement(rotation, translation, ...)` |

I volumi dei rivelatori CLAS12 trasferiti da GEMC2 dovrebbero usare la convenzione di posizionamento passivo:

```python
gvolume.g4placement_type = "passive"
```

Mantieni nel database la sequenza delle rotazioni ordinate. Ad esempio, non ridurre a un'unica rotazione:

```text
ordered: yxz, 0*deg, 0*deg, 6*deg
```

GEMC applica le rotazioni ordinate nell'ordine specificato. Ciò è necessario per il DC e si prevede che sia
rilevante anche per altri sistemi CLAS12 trasferiti da `clas12Tags`.

<br/>

## Coatjava

Alcuni sistemi CLAS12 usano coatjava affinché la geometria della simulazione segua lo stesso servizio di geometria
Java usato dalla ricostruzione. Questo repository mantiene una copia locale di coatjava in `geometry_src`:

```shell
./geometry_src/install_coatjava.sh -l
```

La configurazione di Meson installa coatjava automaticamente se `geometry_src/coatjava` è assente. La CI e le
immagini Docker devono prima fornire i prerequisiti:

- Java
- Maven
- git-lfs
- jq

Gli script di supporto sono:

| Percorso | Scopo |
|------------------------------------|-------------------------------------------------------------------|
| `geometry_src/install_coatjava.sh` | Installa la copia locale di coatjava |
| `ci/install_coatjava_deps.sh` | Installa Java, Maven, git-lfs e jq nelle immagini CI supportate |
| `ci/setup_coatjava.sh` | Script CI che installa i prerequisiti e poi coatjava, se necessario |

Non rimuovere un'installazione coatjava esistente a meno che il flag di reset non sia esplicitamente richiesto.

<br/>

## Compilazione e test

Questo repository viene compilato con Meson e usa le dipendenze GEMC e Geant4 configurate in `meson/`.

Solo **Geant4** deve essere già presente (carica il suo modulo / rendi disponibile `geant4-config` su `PATH`).
GEMC **non** deve essere preinstallato: se non viene trovato, viene compilato dal sottoprogetto `gemc` e installato
nello stesso `--prefix`. Ciò consente di installare i sistemi CLAS12 da zero in un ambiente con il solo Geant4
(vedi il riquadro nella sezione [GEMC](#gemc)).

Configura, compila ed esegui i test:

```shell
meson setup build --prefix="$PWD/install"
meson compile -C build
meson install -C build
meson test -C build --suite clas12 --print-errorlogs
```

**Test CLAS12 e test del core GEMC.** I test di questo repository appartengono tutti alla suite `clas12`
(generazione della geometria, costruzione dei rivelatori in GEMC, connettività CCDB e controlli SRO), motivo per cui
il comando precedente e la CI (`ci/build.sh`) eseguono `--suite clas12`. I test del **core** GEMC appartengono a
`gemc/src` e non fanno parte di questo repository: quando GEMC viene compilato qui come sottoprogetto `gemc`,
non registra **nessuno** dei propri test — questi verificano il GEMC non installato nell'albero di build e sono
responsabilità della CI di `gemc/src`. Un semplice `meson test -C build` qui esegue quindi solo la suite `clas12`;
la sede di riferimento per eseguire la suite del core GEMC è il repository
[`gemc/src`](https://github.com/gemc/src) stesso. (L'opzione `-Dinclude-subproject-tests=true` controlla gli altri
sottoprogetti inclusi — CCDB, HIPO, clas12-cmag — e non GEMC.)

In arrivo nella prossima release: ogni rivelatore ha uno smoke test `gemc_<system>` nelle suite `clas12` e `gemc`.
Dopo la generazione della geometria, il test avvia il GEMC installato, costruisce la geometria nativa e CAD
e carica i plugin del rivelatore con zero eventi e nessun campo magnetico in una directory temporanea isolata.
Una volta che i test di geometria hanno popolato `build/clas12.db`, riesegui solo la costruzione con
`meson test -C build --suite gemc --print-errorlogs`. Quando GEMC è compilato come sottoprogetto, installalo prima
di eseguire i test, affinché l'eseguibile disponga della struttura di directory richiesta a runtime.

Per riutilizzare un'installazione GEMC esistente invece di compilarla, passa `-Duse-gemc-location=<dir>` (oppure
rendi disponibile il suo binario `gemc` su `PATH`).

Usa queste opzioni indipendenti per riutilizzare installazioni di librerie e mappe del campo magnetico esistenti.
Le tre opzioni per le librerie e il percorso predefinito configurabile del plugin di campo sono in arrivo
nella prossima release.

| Opzione Meson | Percorso da fornire |
| --- | --- |
| `-Duse-gemc-location=<dir>` | Prefisso di installazione di GEMC |
| `-Duse-ccdb-location=<dir>` | Prefisso di installazione di CCDB |
| `-Duse-hipo-location=<dir>` | Prefisso di installazione di HIPO |
| `-Duse-clas12-cmag-location=<dir>` | Prefisso di installazione di clas12-cmag |
| `-Duse-fields-location=<dir>` | Directory contenente le mappe del campo magnetico di CLAS12 |

Ad esempio, per riutilizzare tutte e quattro le risorse:

```shell
meson setup build --prefix="$PWD/install" \
  -Duse-ccdb-location=/absolute/path/to/ccdb \
  -Duse-hipo-location=/absolute/path/to/hipo \
  -Duse-clas12-cmag-location=/absolute/path/to/clas12-cmag \
  -Duse-fields-location=/absolute/path/to/magfield
```

Ogni opzione è vuota per impostazione predefinita e può essere impostata indipendentemente. Un'opzione di libreria
vuota preserva la configurazione esistente della dipendenza. Se viene fornito un percorso di libreria, questo deve
essere assoluto e il relativo sottoprogetto viene saltato; installazioni non valide fanno fallire la configurazione.
Gli header sono attesi in `include/` (anche `includes/` per installazioni meno recenti di clas12-cmag) e le librerie
in `lib/` o `lib64/`. L'opzione `-Dprefer_static=true` di Meson preferisce le librerie statiche quando entrambi i tipi
sono installati; le librerie statiche usate dai plugin devono essere compilate con codice indipendente dalla
posizione. Un'installazione di CCDB richiede gli strumenti di sviluppo del client MySQL/MariaDB e SQLite;
un'installazione di HIPO richiede i pacchetti di sviluppo LZ4 e fmt. Le installazioni esterne non vengono copiate
da `meson install`.

Con `-Duse-fields-location=<dir>`, nessuna mappa viene scaricata o installata e il plugin di campo usa quella
directory per impostazione predefinita. Un parametro di campo `dir` esplicito ha comunque la precedenza.
Quando l'opzione è vuota, le mappe provengono dal sottoprogetto git-lfs `magfield` e vengono installate in
`<prefix>/fields`; il plugin individua tale directory rispetto alla propria posizione di installazione.
Lo scaricamento delle mappe richiede git-lfs.

GEMC stesso viene individuato in modo analogo. `-Duse-gemc-location=<dir>` usa il GEMC installato in quel prefisso
assoluto (dove è atteso `lib/pkgconfig/gemc.pc`). Quando l'opzione è vuota, viene usato un GEMC già installato se
trovato tramite pkg-config o tramite il binario `gemc` su `PATH`; altrimenti il sottoprogetto `gemc` viene compilato
dai sorgenti. Geant4 non viene mai compilato: deve essere già disponibile (carica il modulo Geant4 prima della
configurazione) e la configurazione fallisce se è assente.

In arrivo nella prossima release: il CCDB incluso usa SQLite di sistema tramite `ccdb_system_sqlite.patch`,
evitando la propria copia privata di SQLite in forma amalgamata. I checkout esistenti del sottoprogetto CCDB
privi delle patch devono essere ricreati prima di ricompilare:

```shell
meson subprojects purge --confirm ccdb
```

Poi configura una directory di build pulita affinché Meson scarichi CCDB e applichi le patch dei wrap.

I test di geometria eseguono ogni sistema Python registrato e scrivono il database SQLite combinato:

```shell
meson test -C build geometry_dc --print-errorlogs
sqlite3 build/clas12.db "select system, variation, run, count(*) from geometry group by 1,2,3;"
```

Il registro dei sistemi CLAS12 è attualmente in `meson.build`:

```meson
clas12_systems = [
    'beamline',
    'dc',
    'ec',
    'ft',
    'ftof',
    'ltcc',
    'magnets',
    'pcal',
]
```

Aggiungi il nome di un rivelatore a questo elenco solo quando `geometry_src/<system>/<system>.py` è pronto
a generare una geometria GEMC valida.

<br/>

## Costanti di calibrazione CCDB

I plugin di digitizzazione dei rivelatori (`dc`, `ecal`, `ft_cal`, `ft_hodo`, `ftof`, `ltcc`) caricano le proprie
costanti di calibrazione da CCDB. Per impostazione predefinita si connettono al database di JLab all'indirizzo
`mysql://clas12reader@clasdb.jlab.org/clas12`; imposta la variabile d'ambiente
`CCDB_CONNECTION` per puntare a un server diverso o a uno snapshot SQLite locale
(`sqlite:///path/to/ccdb.sqlite`). Si tratta del database CCDB, non del database dei rivelatori
`clas12.sqlite` di GEMC2 — puntare a quest'ultimo restituisce costanti vuote. In caso di qualsiasi errore CCDB
(host irraggiungibile, database errato, tabella vuota), i plugin ora interrompono l'esecuzione con un messaggio
di errore chiaro invece di produrre silenziosamente un output digitizzato vuoto.

### Connettore MariaDB e MySQL a confronto (macOS)

La libreria client CCDB richiede attenzione su macOS. L'account `clas12reader` si autentica con
`mysql_native_password`, uno schema che Oracle ha **rimosso** dalla libreria client MySQL nella versione 9.0
(è basato su SHA1 ed era deprecato per motivi di sicurezza). Un CCDB collegato a MySQL 9.x non può quindi
autenticarsi su clasdb e fallisce al momento della connessione — si tratta di una limitazione della libreria
client, non di un bug di CCDB, e nessuna modifica ai sorgenti CCDB può ripristinare una funzionalità esclusa
dalla libreria in fase di compilazione. Installa un connettore che la fornisca ancora:

```shell
brew install mariadb-connector-c   # preferred: maintained; supports native_password and caching_sha2_password
# or
brew install mysql-client@8.4      # Oracle LTS that still ships native_password
```

La procedura di build Meson seleziona automaticamente il connettore CCDB (`meson/meson.build`), preferendo,
nell'ordine, `mariadb-connector-c`, `mysql-client@8.4`, `mysql-client` e infine `mysql`, così che una build pulita
si colleghi a un client funzionante senza dover ripetere manualmente il collegamento. Se è installato solo
MySQL 9.x, CCDB viene comunque compilato, ma la connessione a clasdb fallisce con un errore chiaro finché non
viene installato un connettore compatibile (o l'account del server non passa a `caching_sha2_password`).

Esiste una seconda insidia, indipendente dalla prima e specifica di MariaDB: `mariadb-connector-c`
**impone TLS per impostazione predefinita**, mentre clasdb opera senza SSL, quindi una build MariaDB con le
impostazioni predefinite fallisce con `Error 2026 (SSL is required, but the
server does not support it)`. Al sottoprogetto `ccdb` viene applicata una patch (tramite
`subprojects/ccdb.wrap` `diff_files` → `subprojects/packagefiles/ccdb_ssl_no_enforce.patch`) per disabilitare
l'obbligo di TLS quando viene compilato con MariaDB, riproducendo il comportamento predefinito di
libmysqlclient di Oracle, che consente il ripiego su una connessione in chiaro. La patch è protetta da
`#ifdef LIBMARIADB`, quindi non ha effetto sui client MySQL/Oracle (che hanno rimosso tale opzione e comunque
non impongono TLS). Con questa patch, `mariadb-connector-c` si connette a clasdb ed è il connettore consigliato.

<br/>

## Percorso dei plugin

I plugin dei sistemi CLAS12 vengono installati come librerie condivise `.gplugin` in `<prefix>/lib/`. GEMC
individua i plugin cercando, nell'ordine: `GEMC_PLUGIN_PATH`, le proprie directory `lib/` e `build/`, quindi il
percorso di ricerca delle librerie dinamiche del sistema operativo (`LD_LIBRARY_PATH` su Linux,
`DYLD_LIBRARY_PATH` su macOS).

La configurazione più semplice consiste nell'installare i sistemi CLAS12 nello stesso prefisso di GEMC, così che
le librerie `.gplugin` si trovino nella directory `lib/` in cui GEMC cerca già, senza richiedere variabili
a runtime. Il prefisso di GEMC si trova un livello sopra la sua directory `bin/`, quindi può essere ricavato
a partire da `command -v gemc`:

```shell
meson setup build --prefix="$(dirname "$(dirname "$(command -v gemc)")")"
meson install -C build
gemc dc.yaml
```

Se GEMC è su `PATH` ma è configurato un prefisso diverso, Meson stampa un avviso durante la configurazione.
In tal caso imposta `GEMC_PLUGIN_PATH` sulla directory delle librerie dei sistemi CLAS12 prima di eseguire `gemc`:

```shell
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
gemc dc.yaml
```

Oppure passa il percorso sulla riga di comando:

```shell
gemc dc.yaml -plugin_path=/path/to/clas12-systems/lib
```

Se un plugin non viene trovato, GEMC stampa il valore corrente di `GEMC_PLUGIN_PATH` insieme all'errore per
aiutare a diagnosticare i problemi di percorso.

Il prefisso di installazione di una build Meson espone la directory dei plugin tramite un file pkg-config:

```shell
# After: meson install -C build --prefix=/my/clas12/prefix
export PKG_CONFIG_PATH=/my/clas12/prefix/lib/pkgconfig:$PKG_CONFIG_PATH
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
```

<br/>


## Modello di build dei plugin

I plugin di sistema usano un modello basato su un registro:

1. Il file `geometry_src/<system>/plugin/meson.build` di ciascun rivelatore aggiunge dizionari a `clas12_plugins`.
2. Il `meson.build` di primo livello è l'unico punto che trasforma tali voci in librerie condivise installate.
3. I plugin GEMC installati devono usare il suffisso `.gplugin`.

Ciò rende coerente l'installazione dei plugin tra i sistemi CLAS12 ed evita che ogni rivelatore definisca una
propria logica di build.

### Modelli per i messaggi di log

In arrivo nella prossima release: il logging dei plugin usa l'API `GLogger` basata su messaggi completi.
Mantieni unita la frase in inglese e passa i valori tramite segnaposto numerati:

```cpp
log->info(1, "Loaded %1 constants for run %2.", count, runno);
```

`debug`, `warning`, `error` e `critical` usano le stesse regole per i segnaposto. Ricompila i plugin usando gli
header GEMC corrispondenti; le precedenti chiamate basate sulla concatenazione devono essere migrate.
Il testo diagnostico dinamico può essere passato come valore con `log->warning("%1", text)`, affinché i suoi
segni di percentuale rimangano letterali.

Il catalogo inglese generato si trova in `translations/en.yaml`; `translations/catalog.yaml` seleziona i
sorgenti dei plugin a cui appartengono i messaggi. Rigeneralo o verificalo usando l'estrattore condiviso
dall'albero dei sorgenti GEMC nella directory adiacente:

```shell
../src/build/subprojects/pygemc/python_env/bin/python ../src/ci/extract_messages.py extract --root .
../src/build/subprojects/pygemc/python_env/bin/python ../src/ci/extract_messages.py extract --root . --check
../src/build/subprojects/pygemc/python_env/bin/python ../src/ci/extract_messages.py validate-tree --root .
```

Modifica i messaggi inglesi in C++, anziché nel catalogo generato. Vedi la
[guida al catalogo](https://github.com/gemc/src/blob/main/translations/README.md) per la validazione delle traduzioni.
Il logging a runtime seleziona automaticamente la lingua; `-language=it` seleziona l'italiano e `-language=en`
forza l'inglese. I messaggi mancanti mantengono il testo inglese. Meson installa i cataloghi dei plugin in
`<prefix>/share/gemc/translations/clas12`; i percorsi di ricerca dei plugin esistenti rendono accessibili i cataloghi
in altri prefissi di installazione. Ricompila i plugin usando gli header GEMC corrispondenti e la nuova libreria
`glogging`. Il workflow condiviso Claude/Codex genera i cataloghi delle lingue tramite il processo cron esistente
nei giorni feriali; la voce `gemc/clas12-messages` usa lotti validati e riprendibili e tiene traccia del commit git
dei sorgenti. Anche il workflow Test valida ogni catalogo generato senza agenti, controllando i file delle lingue
richieste, le chiavi, i segnaposto, le sequenze di escape dei segni di percentuale e gli spazi bianchi.
Per i messaggi mancanti viene riportata la copertura, con ripiego sull'inglese; l'accuratezza delle traduzioni
resta parte della revisione degli agenti.

<br/>

## Campo magnetico

CLAS12 usa un campo magnetico **mappato** — le mappe misurate del campo del solenoide e del toroide — anziché un
modello analitico. Il campo è fornito dal plugin `gfieldclas12-cmag` in `plugins/field/`, che legge le mappe binarie
del solenoide e del toroide CLAS12 tramite la libreria [cMag](https://github.com/JeffersonLab/clas12-cmag)
di David Heddle (il sottoprogetto `clas12-cmag`) e restituisce il campo risultante in ogni punto di avanzamento.

Il campo viene configurato con il nodo generico `gfields` del core GEMC, selezionando questo plugin con
`type: clas12-cmag`:

```yaml
gfields:
  - name: clas12
    type: clas12-cmag
    solenoid: Symm_solenoid_r601_phi1_z1201_13June2018
    torus: Symm_torus_r2501_phi16_z251_24Apr2018
    solenoid_scale: 1
    torus_scale: 1

global_field: clas12
```

Il valore di `global_field` è il nome del campo configurato (`clas12` nell'esempio), non i nomi delle mappe del
solenoide e del toroide. I nomi delle mappe e i fattori di scala per ciascuna mappa appartengono alla voce `gfields`.
Questo sostituisce lo stile GEMC2 `global_field: Symm_solenoid_...:Symm_torus_...` e i vecchi nomi codificati
direttamente per l'applicazione dei fattori di scala, `binary_torus` / `binary_solenoid`, con i parametri espliciti
`torus`, `solenoid`, `torus_scale` e `solenoid_scale`.

Qualsiasi chiave scalare aggiuntiva (spostamenti per ciascuna mappa, origine/rotazione complessiva, `interpolation`)
viene inoltrata senza modifiche al plugin.

Le mappe del campo provengono dal sottoprogetto git-lfs `magfield` e vengono copiate in `<prefix>/fields` durante
`meson
install` (vedi `meson/install_fields.py`); il plugin le legge dalla directory `fields` installata accanto
a esso (`<plugin_dir>/../fields`). La configurazione con `-Duse-fields-location=<dir>` salta il sottoprogetto e
punta invece a una directory di mappe esistente (nulla viene clonato o installato). Non sono necessarie variabili
d'ambiente `FIELD` o `FIELD_DIR` a runtime; un parametro `dir` esplicito può sostituire il percorso predefinito.

<br/>

## Lettura in streaming (SRO)

**In arrivo nella prossima release.** I sistemi CLAS12 possono emettere frame di lettura in streaming (SRO) nel
formato binario DAQ di JLAB al posto dell'output ordinario per eventi, oppure insieme a esso. GEMC gestisce lo
streamer generico `sro`; un plugin di sistema fornisce i payload esportando un `GSROImplementationFactory`
accanto al proprio digitizzatore. Attualmente solo **FT-Cal** fornisce payload SRO (tramite `ft_cal.gplugin`);
gli altri digitizzatori FT mantengono il normale output senza un modello SRO.

Attiva SRO dalla riga di comando selezionando il formato streamer `sro` e il plugin che fornisce i payload, e
assegnando all'acquisizione un intervallo temporale tra gli eventi diverso da zero:

```shell
gemc geometry_src/ft/ft.yaml -n=10000 \
  -gstreamer='[{format: sro, filename: ftcal_sro, implementation: ft_cal}]' \
  -eventTimeWidth='10*ns'
```

- `format: sro` seleziona lo streamer SRO di GEMC; `implementation: ft_cal` specifica il plugin che produce i
  payload; `filename` è il nome base dell'output.
- `-eventTimeWidth` imposta la distanza tra eventi consecutivi sulla linea temporale dell'acquisizione.
  Il valore predefinito, pari a zero, impedisce un'esecuzione SRO, quindi deve essere impostato esplicitamente
  (il `10*ns` dell'esempio non è un parametro misurato del fascio CLAS12). Le esecuzioni con output ordinario
  non ne hanno bisogno.
- I file di output vengono scritti per ciascun crate come `<basename>_r<resolved_run>_crate<crate>.ev`;
  riutilizzare un nome base e un run li sovrascrive.

Il componente FT di registrazione iniziale `ft.gplugin` fornisce le opzioni per `ft_cal.gplugin`, quindi non
è necessario alcun nodo aggiuntivo per le opzioni. Vedi
[`geometry_src/sro/README.md`](geometry_src/sro/README.md) per la convenzione della tabella di traduzione,
il modello temporale dei worker (incluso `ft_cal_sro_min_signal_time`), il formato binario e la suite di test `sro`;
le definizioni DAQ trasferite e la loro provenienza si trovano in
[`geometry_src/sro/daq/README.md`](geometry_src/sro/daq/README.md).

<br/>

## Validazione

Per ogni rivelatore trasferito, valida sia le righe del database prodotte sia il comportamento della geometria
a runtime.

Controlli consigliati:

- Confronta le righe della geometria generate con il riferimento GEMC2 in `geometry_source/<system>` in
  [`gemc/clas12Tags`](https://github.com/gemc/clas12Tags).
- Conferma che nomi, volumi madre, descrizioni, posizioni, rotazioni, solidi, parametri e materiali corrispondano
  per i campi comuni.
- Verifica che le mappature di run e varianti siano locali alla directory del sistema.
- Usa le esportazioni PyVista per controlli rapidi del posizionamento prima di eseguire una simulazione Geant4
  completa.
- Esegui GEMC in modalità batch e GUI quando un rivelatore dispone di geometria sufficiente da ispezionare.

Per il DC, la geometria predefinita generata dovrebbe corrispondere a livello di token a:

```text
https://github.com/gemc/clas12Tags/blob/main/geometry_source/dc/dc__geometry_default.txt
```

Requisiti noti per il DC:

- il run predefinito è `11`
- tutti i volumi DC usano `g4placement_type = "passive"`
- le rotazioni ordinate sono preservate come `ordered: ...`
- la variante obsoleta `original` non è supportata

<br/>

## CI e release

In arrivo nella prossima release: tutti i workflow basati su container compilano GEMC e i sistemi CLAS12 dai
sorgenti su immagini base Geant4 pubblicate da [`gemc/g4install`](https://github.com/gemc/g4install).
La [guida ai workflow](.github/workflows/README.md) documenta i trigger, l'autorizzazione al deployment,
i contratti tra repository, i permessi, i nuovi tentativi e le esecuzioni che ci si aspetta vengano saltate.

Automazioni rilevanti:

| Workflow | Scopo |
|-----------------------|-------------------------------------------------------------------------------------|
| `deploy.yml` | Compila GEMC e i sistemi CLAS12 in immagini base Geant4, poi pubblica le immagini |
| `pr-docker-image.yml` | Crea un'immagine di anteprima per ogni PR, per testare il branch senza build locale |
| `sanitize.yml` | Esegue build CLAS12 con sanitizer, escludendo i sottoprogetti di terze parti |
| `codeql.yml` | Analisi statica |
| `doxygen.yml` | Generazione della documentazione |
| `binary_tarballs.yml` | Ricompila GEMC ed esegue uno smoke test dopo il deployment |
| `dev_release.yml` | Automazione delle release di sviluppo |

Le immagini di deployment usano lo schema:

```text
ghcr.io/gemc/clas12-systems:<gemc-tag>-<os>-<version>[-<arch>]
```

Le immagini base provengono da:

```text
ghcr.io/gemc/g4install
```

Ogni pull request pubblica inoltre un'immagine di anteprima multiarchitettura pronta all'uso, creata dal branch
(`ghcr.io/gemc/clas12-systems:<gemc-tag>-almalinux-<version>-pr-<number>`), così che autori e revisori possano
testarla senza una build locale — vedi [Immagine container di anteprima](CONTRIBUTING.md#preview-container-image)
nella guida ai contributi. L'immagine viene eliminata automaticamente quando la pull request viene chiusa.

<br/>


## Documentazione

- [Guida ai workflow CI](.github/workflows/README.md)
- [Homepage GEMC](https://gemc.github.io/home/)
- [Repository dell'API Python](https://github.com/gemc/pygemc)
- [Repository GEMC2 / CLAS12](https://github.com/gemc/clas12Tags)

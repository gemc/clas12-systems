<!-- TRANSLATIONS:START (managed by bin/translate) -->
**Languages:** [EN](README.md) · **IT** · [日本語](README.ja.md) · [FR](README.fr.md) · [中文](README.zh.md)
<!-- TRANSLATIONS:END -->

# CLAS12 GEMC Systems

[![Test][badge-test]][workflow-test]
[![Confronto della geometria ASCII][badge-ascii-geometry]][workflow-ascii-geometry]
[![Distribuzione][badge-deploy]][workflow-deploy]
[![Sanitizer][badge-sanitize]][workflow-sanitize]
[![CodeQL avanzato][badge-codeql]][workflow-codeql]
[![Doxygen][badge-doxygen]][workflow-doxygen]
[![Archivi binari tar][badge-binary-tarballs]][workflow-binary-tarballs]
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

CLAS12 GEMC Systems contiene l'implementazione GEMC3 dei sistemi geometrici dei rivelatori CLAS12 e dei relativi
plugin specifici. È il repository complementare per CLAS12 dell'applicazione principale GEMC e dell'API Python
per la geometria:

- [`gemc/src`](https://github.com/gemc/src) fornisce l'applicazione C++ GEMC, l'integrazione con Geant4, i
  caricatori di geometria SQLite/ASCII/CAD/GDML, l'infrastruttura per i plugin dinamici, gli streamer e l'ambiente
  `pygemc` incluso.
- [`gemc/pygemc`](https://github.com/gemc/pygemc) fornisce l'API Python usata per definire geometria e materiali,
  scrivere database GEMC, visualizzare in anteprima la geometria con PyVista ed esportare scene VTK.js.
- [`gemc/home`](https://github.com/gemc/home) contiene il sito web pubblico di GEMC, le pagine di installazione,
  i tutorial, gli esempi e le risorse generate per la documentazione.

<br/>

## Ambito attuale

Questo repository è in fase di migrazione attiva da [`gemc/clas12Tags`](https://github.com/gemc/clas12Tags).

| Sistema | Stato                       | Note                                                     |
|---------|-----------------------------|----------------------------------------------------------|
| `dc`    | geometria e plugin          | Usa coatjava come sorgente della geometria                |
| `ec`    | geometria e plugin          | Usa coatjava e il plugin condiviso `ecal`                  |
| `field` | plugin                      | Campo magnetico CLAS12 basato su mappe tramite cMag        |
| `ft`    | geometria e plugin          | In arrivo nella prossima release: FTCAL, FTHODO e FTTRK    |
| `ftof`  | geometria e plugin          | Usa coatjava come sorgente della geometria                |
| `ltcc`  | geometria e plugin          | Geometria nativa e CAD con superfici ottiche               |
| `pcal`  | geometria e plugin condiviso | Usa coatjava e il plugin condiviso `ecal`                  |


<br/>

## GEMC

Il repository principale di GEMC, [`gemc/src`](https://github.com/gemc/src), gestisce il comportamento a runtime.
Questo comprende:

- la costruzione dei solidi, dei volumi logici e dei posizionamenti fisici di Geant4
- i plugin C++ dinamici
- la generazione degli eventi, i rivelatori sensibili e gli streamer di output

Questo repository gestisce gli input specifici di CLAS12 per quel runtime:

- la geometria dei rivelatori, le definizioni dei materiali,
- le mappature di run e variazioni necessarie per riprodurre la geometria di CLAS12
- la validazione rispetto alla geometria e all'output di riferimento di CLAS12 in GEMC2

Il repository [`gemc/pygemc`](https://github.com/gemc/pygemc) definisce l'API Python.

> **Compilazione da zero — nessuna preinstallazione di GEMC richiesta.** A partire dalla prossima release, i
> sistemi CLAS12 possono essere compilati e installati in un ambiente con solo Geant4 (per esempio un'immagine
> `ghcr.io/gemc/g4install`) **senza GEMC presente**: quando non viene trovata un'installazione di GEMC, il processo
> di compilazione lo compila automaticamente dal sottoprogetto `gemc` e lo installa nello stesso prefisso.
> GEMC viene individuato in questo ordine — un'opzione esplicita `-Duse-gemc-location=<dir>`, poi un GEMC già
> installato (tramite pkg-config o il binario `gemc` in `PATH`), e infine il sottoprogetto compilato dai sorgenti.
> **Geant4 non viene mai compilato**: deve essere già disponibile, altrimenti la configurazione fallisce. Tutti
> i workflow CI basati su container seguono questa procedura sulle immagini g4install delle distribuzioni
> supportate.

<br/>

## Flusso di lavoro per la geometria

Ogni sistema di rivelatori è autonomo all'interno di `geometry_src/<system>`.

Una tipica directory di sistema contiene:

| File                                         | Ruolo                                                                                |
|----------------------------------------------|--------------------------------------------------------------------------------------|
| `<system>.py`                                | Script principale eseguibile; crea `autogeometry()` e pubblica materiali e volumi    |
| `geometry.py`                                | Codice di costruzione della geometria                                                |
| `materials.py`                               | Definizioni dei materiali del sistema                                                |
| `variations.py`                              | Mappatura opzionale di run e variazioni                                               |
| `<system>.yaml`                              | File di configurazione GEMC per esecuzioni locali rapide                              |
| `../coatjava_factories/CoatjavaFactory.java` | Interfaccia opzionale verso coatjava quando si usano servizi di geometria Java        |
| `plugin/meson.build`                         | Registrazione opzionale dei plugin C++ per la digitizzazione o altre estensioni a runtime |

Lo script principale dovrebbe essere eseguibile e avviabile direttamente dalla sua directory:

```shell
cd geometry_src/dc
./dc.py 
```

Usa le opzioni PyVista di `pygemc` quando un sistema è pronto per l'ispezione visiva:

```shell
./dc.py -pvb
```

Esegui GEMC con il file di configurazione locale:

```shell
gemc dc.yaml
gemc dc.yaml -gui
```

Le righe della geometria sensibile selezionano il plugin da usare a runtime tramite il campo `digitization` del
volume. La chiave opzionale `digitization` in una voce YAML `gsystem` ha uno scopo più circoscritto: indica a
GEMC quale plugin con un nome diverso verificare prima di analizzare le opzioni, come quando i sistemi `ec` e
`pcal` condividono `ecal.gplugin`. FT ha tre nomi per la geometria sensibile (`ft_cal`, `ft_hodo` e `ft_trk`),
quindi il suo YAML mantiene una semplice voce `name: ft`. Il plugin `ft.gplugin`, dedicato esclusivamente alle
opzioni, registra tutti e tre i domini durante la verifica iniziale di bootstrap; il caricamento della geometria
individua poi e carica i tre digitizzatori dalle righe sensibili.

<br/>

## Confronti con i riferimenti

Usa `scripts/compare_ascii_databases.py` per confrontare i database ASCII GEMC3 generati (geometria e
materiali) con i corrispondenti file di riferimento di [`gemc/clas12Tags`](https://github.com/gemc/clas12Tags):

```shell
scripts/compare_ascii_databases.py dc
```

Senza argomenti che specifichino i sistemi, lo script controlla ogni implementazione locale
`geometry_src/<system>/<system>.py`. Lo script mappa le colonne ASCII di GEMC2 e GEMC3 su campi geometrici
comuni — nome, volume madre, posizione, rotazione, solido, dimensioni, materiale, digitizzazione (GEMC2
`sensitivity`) e identificatore (GEMC2 `identifiers`, espanso nella forma canonica `name=value`) — e confronta
solo i valori di quei campi per nome del volume, in modo che le differenze di formattazione e di ordine delle
colonne non nascondano effettive corrispondenze geometriche. I materiali vengono confrontati allo stesso modo
per nome del materiale (densità, componenti, proprietà ottiche e di scintillazione), per i sistemi che
definiscono materiali personalizzati. Le rappresentazioni numeriche e gli ordini degli array dei policoni
GEMC2/GEMC3 vengono normalizzati prima del confronto.

Quando un qualsiasi campo differisce, lo script stampa le discrepanze per campo e termina con codice di uscita
`1`; un'esecuzione in cui tutti i valori corrispondono termina con codice di uscita `0`.

<br/>

## Posizionamento e rotazioni

GEMC3 supporta entrambe le convenzioni di posizionamento di Geant4 tramite `GVolume.g4placement_type`:

| Valore    | Significato                                                                            |
|-----------|----------------------------------------------------------------------------------------|
| `active`  | Comportamento predefinito di GEMC3; usa `G4Transform3D(rotation, translation)`            |
| `passive` | Comportamento compatibile con GEMC2/clas12Tags; usa `G4PVPlacement(rotation, translation, ...)` |

I volumi dei rivelatori CLAS12 portati da GEMC2 dovrebbero usare la convenzione di posizionamento passiva:

```python
gvolume.g4placement_type = "passive"
```

Preserva nel database l'ordine delle rotazioni ordinate. Per esempio, non appiattire la sequenza:

```text
ordered: yxz, 0*deg, 0*deg, 6*deg
```

GEMC applica le rotazioni ordinate nell'ordine specificato. Questo è necessario per DC e si prevede che sia
rilevante anche per altri sistemi CLAS12 portati da `clas12Tags`.

<br/>

## Coatjava

Alcuni sistemi CLAS12 usano coatjava affinché la geometria della simulazione segua lo stesso servizio di
geometria Java usato dalla ricostruzione. Questo repository mantiene una copia locale di coatjava in
`geometry_src`:

```shell
./geometry_src/install_coatjava.sh -l
```

La configurazione di Meson installa coatjava automaticamente se `geometry_src/coatjava` è assente. Le immagini
CI e Docker devono prima fornire i prerequisiti:

- Java
- Maven
- git-lfs
- jq

Gli script di supporto sono:

| Percorso                           | Scopo                                                             |
|------------------------------------|-------------------------------------------------------------------|
| `geometry_src/install_coatjava.sh` | Installa la copia locale di coatjava                              |
| `ci/install_coatjava_deps.sh`      | Installa Java, Maven, git-lfs e jq nelle immagini CI supportate    |
| `ci/setup_coatjava.sh`             | Script di supporto CI che installa i prerequisiti e poi coatjava se necessario |

Non rimuovere un'installazione esistente di coatjava a meno che non sia richiesto esplicitamente il flag di
ripristino.

<br/>

## Compilazione e test

Questo repository viene compilato con Meson e usa le dipendenze GEMC e Geant4 configurate in `meson/`.

Solo **Geant4** deve essere già presente (carica il suo modulo / rendi disponibile `geant4-config` in `PATH`).
GEMC **non** deve essere preinstallato: se non viene trovato, viene compilato dal sottoprogetto `gemc` e
installato nello stesso `--prefix`. Questo permette di installare i sistemi CLAS12 da zero in un ambiente con
solo Geant4 (vedi il riquadro nella sezione [GEMC](#gemc)).

Configura, compila ed esegui i test:

```shell
meson setup build --prefix="$PWD/install"
meson compile -C build
meson install -C build
meson test -C build --suite clas12 --print-errorlogs
```

**Test CLAS12 e test del core GEMC.** I test di questo repository appartengono tutti alla suite `clas12`
(generazione della geometria, costruzione dei rivelatori in GEMC, connettività CCDB e controlli SRO), ed è per
questo che il comando sopra e la CI (`ci/build.sh`) eseguono `--suite clas12`. I test del **core** GEMC
appartengono a `gemc/src` e non fanno parte di questo repository: quando GEMC viene compilato qui come
sottoprogetto `gemc`, non registra **nessuno** dei propri test — questi verificano il GEMC non installato
nell'albero di compilazione e sono responsabilità della CI di `gemc/src`. Un semplice `meson test -C build`
qui esegue quindi solo la suite `clas12`; la sede di riferimento per eseguire la suite del core GEMC è il
repository [`gemc/src`](https://github.com/gemc/src) stesso. (L'opzione `-Dinclude-subproject-tests=true`
regola gli altri sottoprogetti inclusi — CCDB, HIPO, clas12-cmag — non GEMC.)

In arrivo nella prossima release: ogni rivelatore ha uno smoke test `gemc_<system>` nelle suite `clas12` e
`gemc`. Dopo la generazione della geometria, il test avvia il GEMC installato, costruisce la geometria nativa e
CAD e carica i plugin del rivelatore con zero eventi e senza campo magnetico in una directory temporanea isolata.
Una volta che i test di geometria hanno popolato `build/clas12.db`, riesegui solo la costruzione con
`meson test -C build --suite gemc --print-errorlogs`. Quando GEMC viene compilato come sottoprogetto,
installalo prima dei test affinché l'eseguibile disponga della struttura di directory richiesta a runtime.

Per riutilizzare un'installazione GEMC esistente invece di compilarla, passa `-Duse-gemc-location=<dir>` (oppure
rendi disponibile il suo binario `gemc` in `PATH`).

Usa queste opzioni indipendenti per riutilizzare installazioni di librerie esistenti e mappe del campo magnetico.
Le tre opzioni per le librerie e il percorso predefinito configurato per il plugin del campo sono in arrivo nella
prossima release.

| Opzione Meson | Percorso da fornire |
| --- | --- |
| `-Duse-gemc-location=<dir>` | Prefisso di installazione di GEMC |
| `-Duse-ccdb-location=<dir>` | Prefisso di installazione di CCDB |
| `-Duse-hipo-location=<dir>` | Prefisso di installazione di HIPO |
| `-Duse-clas12-cmag-location=<dir>` | Prefisso di installazione di clas12-cmag |
| `-Duse-fields-location=<dir>` | Directory contenente le mappe del campo magnetico CLAS12 |

Per esempio, per riutilizzare tutte e quattro le risorse:

```shell
meson setup build --prefix="$PWD/install" \
  -Duse-ccdb-location=/absolute/path/to/ccdb \
  -Duse-hipo-location=/absolute/path/to/hipo \
  -Duse-clas12-cmag-location=/absolute/path/to/clas12-cmag \
  -Duse-fields-location=/absolute/path/to/magfield
```

Ogni opzione è vuota per impostazione predefinita e può essere impostata indipendentemente. Un'opzione per una
libreria lasciata vuota mantiene la configurazione delle dipendenze esistente. Il percorso fornito per una
libreria deve essere assoluto e fa saltare il relativo sottoprogetto; installazioni non valide fanno fallire la
configurazione. Gli header devono trovarsi in `include/` (anche in `includes/` per le installazioni meno recenti
di clas12-cmag), e le librerie in `lib/` o `lib64/`. L'opzione `-Dprefer_static=true` di Meson preferisce le
librerie statiche quando entrambi i tipi sono installati; le librerie statiche usate dai plugin devono essere
compilate con codice indipendente dalla posizione. Un'installazione di CCDB richiede gli strumenti di sviluppo
del client MySQL/MariaDB e SQLite; un'installazione di HIPO richiede i pacchetti di sviluppo LZ4 e fmt. Le
installazioni esterne non vengono copiate da `meson install`.

Con `-Duse-fields-location=<dir>`, nessuna mappa viene scaricata o installata e il plugin del campo usa quella
directory per impostazione predefinita. Un parametro `dir` esplicito per il campo ha comunque la precedenza.
Quando l'opzione è vuota, le mappe provengono dal sottoprogetto git-lfs `magfield` e vengono installate in
`<prefix>/fields`; il plugin individua quella directory rispetto alla propria posizione di installazione.
Il recupero delle mappe richiede git-lfs.

GEMC stesso viene individuato in modo analogo. `-Duse-gemc-location=<dir>` usa il GEMC installato in quel
prefisso assoluto (dove deve essere presente `lib/pkgconfig/gemc.pc`). Quando l'opzione è vuota, viene usato
un GEMC già installato se trovato tramite pkg-config o il binario `gemc` in `PATH`; altrimenti il
sottoprogetto `gemc` viene compilato dai sorgenti. Geant4 non viene mai compilato: deve essere già disponibile
(carica il modulo Geant4 prima di configurare), e la configurazione fallisce se è assente.

In arrivo nella prossima release: il CCDB incluso usa SQLite di sistema tramite `ccdb_system_sqlite.patch`,
evitando la propria versione amalgamata di SQLite. I checkout esistenti del sottoprogetto CCDB senza patch
devono essere aggiornati prima di ricompilare:

```shell
meson subprojects purge --confirm ccdb
```

Poi configura una directory di compilazione pulita affinché Meson recuperi CCDB e applichi le patch dei wrap.

I test di geometria eseguono ogni sistema Python registrato e scrivono il database SQLite combinato:

```shell
meson test -C build geometry_dc --print-errorlogs
sqlite3 build/clas12.db "select system, variation, run, count(*) from geometry group by 1,2,3;"
```

Il registro dei sistemi CLAS12 si trova attualmente in `meson.build`:

```meson
clas12_systems = [
    'dc',
    'ec',
    'ft',
    'ftof',
    'ltcc',
    'pcal',
]
```

Aggiungi il nome di un rivelatore a questo elenco solo quando `geometry_src/<system>/<system>.py` è pronto a
generare geometria GEMC valida.

<br/>

## Costanti di calibrazione CCDB

I plugin di digitizzazione dei rivelatori (`dc`, `ecal`, `ft_cal`, `ft_hodo`, `ftof`, `ltcc`) caricano le proprie
costanti di calibrazione da CCDB. Per impostazione predefinita si collegano al database JLab all'indirizzo
`mysql://clas12reader@clasdb.jlab.org/clas12`; imposta la variabile d'ambiente
`CCDB_CONNECTION` per puntare a un server diverso o a uno snapshot SQLite locale
(`sqlite:///path/to/ccdb.sqlite`). Si tratta del database CCDB, non del database dei rivelatori
`clas12.sqlite` di GEMC2 — puntare a quest'ultimo restituisce costanti vuote. In caso di qualsiasi errore CCDB
(host irraggiungibile, database errato, tabella vuota), i plugin ora interrompono l'esecuzione con un errore
chiaro invece di produrre silenziosamente output digitizzato vuoto.

### Connettore MariaDB e MySQL a confronto (macOS)

La libreria client di CCDB richiede attenzione su macOS. L'account `clas12reader` si autentica con
`mysql_native_password`, uno schema che Oracle ha **rimosso** dalla libreria client MySQL nella versione 9.0
(è basato su SHA1 ed era deprecato per motivi di sicurezza). Un CCDB collegato a MySQL 9.x non può quindi
autenticarsi su clasdb e fallisce al momento della connessione — questa è una limitazione della libreria client,
non un bug di CCDB, e nessuna modifica ai sorgenti di CCDB può ripristinare una funzionalità esclusa dalla
libreria in fase di compilazione. Installa un connettore che la fornisca ancora:

```shell
brew install mariadb-connector-c   # preferred: maintained; supports native_password and caching_sha2_password
# or
brew install mysql-client@8.4      # Oracle LTS that still ships native_password
```

Il processo di compilazione Meson seleziona automaticamente il connettore CCDB (`meson/meson.build`),
preferendo, nell'ordine, `mariadb-connector-c`, `mysql-client@8.4`, `mysql-client`, poi `mysql`, in modo che
una compilazione pulita si colleghi a un client funzionante senza dover ripetere manualmente il linking. Se è
installato solo MySQL 9.x, CCDB viene comunque compilato, ma la connessione a clasdb fallisce con un errore
chiaro finché non viene installato un connettore compatibile (o l'account del server non migra a
`caching_sha2_password`).

C'è un secondo problema indipendente, specifico di MariaDB: `mariadb-connector-c` **impone TLS per impostazione
predefinita**, mentre clasdb opera senza SSL, quindi una compilazione con MariaDB nella configurazione standard
fallisce con `Error 2026 (SSL is required, but the
server does not support it)`. Al sottoprogetto `ccdb` viene applicata una patch (tramite
`subprojects/ccdb.wrap` `diff_files` → `subprojects/packagefiles/ccdb_ssl_no_enforce.patch`) per disabilitare
l'obbligo di TLS quando viene compilato con MariaDB, in linea con il comportamento predefinito di libmysqlclient
di Oracle, che consente il ripiego su una connessione in chiaro. La patch è protetta da `#ifdef LIBMARIADB`,
quindi non ha effetto sui client MySQL/Oracle (che hanno rimosso quell'opzione e comunque non impongono TLS).
Con questa modifica, `mariadb-connector-c` si collega a clasdb ed è il connettore consigliato.

<br/>

## Percorso dei plugin

I plugin dei sistemi CLAS12 vengono installati come librerie condivise `.gplugin` in `<prefix>/lib/`. GEMC
individua i plugin cercando, nell'ordine: `GEMC_PLUGIN_PATH`, le proprie directory `lib/` e `build/`, e poi
il percorso di ricerca delle librerie dinamiche del sistema operativo (`LD_LIBRARY_PATH` su Linux,
`DYLD_LIBRARY_PATH` su macOS).

La configurazione più semplice consiste nell'installare i sistemi CLAS12 nello stesso prefisso di GEMC, in modo
che le librerie `.gplugin` si trovino nella directory `lib/` in cui GEMC cerca già e non serva alcuna variabile
a runtime. Il prefisso di GEMC si trova un livello sopra la sua directory `bin/`, quindi lo si può ricavare
da `command -v gemc`:

```shell
meson setup build --prefix="$(dirname "$(dirname "$(command -v gemc)")")"
meson install -C build
gemc dc.yaml
```

Se GEMC è in `PATH` ma viene configurato un prefisso diverso, Meson stampa un avviso durante la configurazione.
In quel caso imposta `GEMC_PLUGIN_PATH` sulla directory delle librerie dei sistemi CLAS12 prima di eseguire
`gemc`:

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

Il prefisso di installazione di una compilazione Meson espone la directory dei plugin tramite un file pkg-config:

```shell
# After: meson install -C build --prefix=/my/clas12/prefix
export PKG_CONFIG_PATH=/my/clas12/prefix/lib/pkgconfig:$PKG_CONFIG_PATH
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
```

<br/>


## Modello di compilazione dei plugin

I plugin di sistema usano un modello basato su un registro:

1. Un file `geometry_src/<system>/plugin/meson.build` specifico del rivelatore aggiunge dizionari a `clas12_plugins`.
2. Il file `meson.build` di primo livello è l'unico punto che trasforma quelle voci in librerie condivise installate.
3. I plugin GEMC installati devono usare il suffisso `.gplugin`.

Questo mantiene coerente l'installazione dei plugin tra i sistemi CLAS12 ed evita che ogni rivelatore definisca
una propria logica di compilazione.

<br/>

## Campo magnetico

CLAS12 usa un campo magnetico **basato su mappe** — le mappe misurate dei campi del solenoide e del toro —
anziché un modello analitico. Il campo è fornito dal plugin `gfieldclas12-cmag` in `plugins/field/`, che legge
le mappe binarie del solenoide e del toro di CLAS12 tramite la libreria
[cMag](https://github.com/JeffersonLab/clas12-cmag) di David Heddle (il sottoprogetto `clas12-cmag`) e
restituisce il campo risultante in ogni punto del passo di simulazione.

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

Il valore di `global_field` è il nome del campo configurato (`clas12` qui sopra), non i nomi delle mappe del
solenoide e del toro. I nomi delle mappe e i fattori di scala per ciascuna mappa appartengono alla voce
`gfields`. Questo sostituisce lo stile GEMC2 `global_field: Symm_solenoid_...:Symm_torus_...` e i vecchi
destinatari dei fattori di scala codificati direttamente, `binary_torus` / `binary_solenoid`, con i parametri
espliciti `torus`, `solenoid`, `torus_scale` e `solenoid_scale`.

Qualsiasi chiave scalare aggiuntiva (spostamenti per ciascuna mappa, origine/rotazione complessiva,
`interpolation`) viene inoltrata al plugin senza modifiche.

Le mappe del campo provengono dal sottoprogetto git-lfs `magfield` e vengono copiate in `<prefix>/fields`
durante `meson
install` (vedi `meson/install_fields.py`); il plugin le legge dalla directory `fields` installata accanto
a esso (`<plugin_dir>/../fields`). La configurazione con `-Duse-fields-location=<dir>` salta il sottoprogetto
e punta invece a una directory di mappe esistente (nulla viene clonato o installato). Non serve alcuna variabile
d'ambiente `FIELD` o `FIELD_DIR` a runtime; un parametro `dir` esplicito può sostituire il percorso predefinito.

<br/>

## Streaming Readout (SRO)

**In arrivo nella prossima release.** I sistemi CLAS12 possono emettere frame di lettura in streaming (SRO) nel
formato binario DAQ di JLAB al posto del normale output a eventi o insieme a esso. GEMC gestisce lo streamer
generico `sro`; un plugin di sistema fornisce i payload esportando una `GSROImplementationFactory` accanto
al proprio digitizzatore. Attualmente solo **FT-Cal** fornisce payload SRO (tramite `ft_cal.gplugin`); gli altri
digitizzatori FT mantengono il normale output senza un modello SRO.

Attiva SRO dalla riga di comando selezionando il formato streamer `sro` e il plugin che fornisce i payload, e
assegnando all'acquisizione un'ampiezza temporale degli eventi diversa da zero:

```shell
gemc geometry_src/ft/ft.yaml -n=10000 \
  -gstreamer='[{format: sro, filename: ftcal_sro, implementation: ft_cal}]' \
  -eventTimeWidth='10*ns'
```

- `format: sro` seleziona lo streamer SRO di GEMC; `implementation: ft_cal` indica il plugin che produce i
  payload; `filename` è il nome di base dell'output.
- `-eventTimeWidth` imposta la spaziatura tra eventi consecutivi sulla linea temporale di acquisizione. Il valore
  predefinito zero impedisce un'esecuzione SRO, quindi deve essere impostato esplicitamente (il `10*ns` sopra è
  un esempio, non un parametro misurato del fascio di CLAS12). Le esecuzioni con output ordinario non ne hanno
  bisogno.
- I file di output vengono scritti per ciascun crate come `<basename>_r<resolved_run>_crate<crate>.ev`;
  riutilizzare lo stesso nome di base e lo stesso run li sovrascrive.

Il componente di registrazione del bootstrap FT `ft.gplugin` fornisce le opzioni per `ft_cal.gplugin`, quindi
non serve alcun nodo aggiuntivo per le opzioni. Vedi [`geometry_src/sro/README.md`](geometry_src/sro/README.md)
per la convenzione della tabella di conversione, il modello temporale dei worker (incluso
`ft_cal_sro_min_signal_time`), la struttura binaria e la suite di test `sro`; le definizioni DAQ portate e la
loro provenienza si trovano in [`geometry_src/sro/daq/README.md`](geometry_src/sro/daq/README.md).

<br/>

## Validazione

Per ciascun rivelatore portato, valida sia le righe prodotte nel database sia il comportamento della geometria
a runtime.

Controlli consigliati:

- Confronta le righe di geometria generate con il riferimento GEMC2 in `geometry_source/<system>` all'interno di
  [`gemc/clas12Tags`](https://github.com/gemc/clas12Tags).
- Conferma che nomi, volumi madre, descrizioni, posizioni, rotazioni, solidi, parametri e materiali corrispondano
  nei campi condivisi.
- Verifica che le mappature di run e variazioni siano contenute nella directory del sistema.
- Usa le esportazioni PyVista per controlli rapidi del posizionamento prima di eseguire una simulazione Geant4
  completa.
- Esegui GEMC in modalità batch e GUI quando un rivelatore ha geometria sufficiente da ispezionare.

Per DC, la geometria predefinita generata dovrebbe corrispondere, token per token, a:

```text
https://github.com/gemc/clas12Tags/blob/main/geometry_source/dc/dc__geometry_default.txt
```

Comportamenti attesi per DC:

- il run predefinito è `11`
- tutti i volumi DC usano `g4placement_type = "passive"`
- le rotazioni ordinate vengono preservate come `ordered: ...`
- la variazione obsoleta `original` non è supportata

<br/>

## CI e release

In arrivo nella prossima release: tutti i workflow basati su container compilano GEMC e i sistemi CLAS12 dai
sorgenti su immagini base Geant4 pubblicate da [`gemc/g4install`](https://github.com/gemc/g4install).
La [guida ai workflow](.github/workflows/README.md) documenta le condizioni di attivazione, l'autorizzazione alla
distribuzione, gli accordi tra repository, i permessi, i tentativi successivi e le esecuzioni che vengono
prevedibilmente saltate.

Automazioni rilevanti:

| Workflow              | Scopo                                                                             |
|-----------------------|-----------------------------------------------------------------------------------|
| `deploy.yml`          | Compila GEMC e i sistemi CLAS12 nelle immagini base Geant4, poi pubblica le immagini |
| `pr-docker-image.yml` | Crea un'immagine di anteprima per ogni PR affinché i revisori possano testare il branch senza compilare localmente |
| `sanitize.yml`        | Esegue compilazioni dei sistemi CLAS12 con sanitizer senza applicarli ai sottoprogetti di terze parti |
| `codeql.yml`          | Analisi statica                                                                    |
| `doxygen.yml`         | Generazione della documentazione                                                   |
| `binary_tarballs.yml` | Ricompila GEMC ed esegue smoke test dopo la distribuzione                           |
| `dev_release.yml`     | Automazione delle release di sviluppo                                              |

Le immagini distribuite usano lo schema:

```text
ghcr.io/gemc/clas12-systems:<gemc-tag>-<os>-<version>[-<arch>]
```

Le immagini base provengono da:

```text
ghcr.io/gemc/g4install
```

Ogni pull request pubblica inoltre un'immagine di anteprima pronta all'uso per più architetture, compilata dal
branch (`ghcr.io/gemc/clas12-systems:<gemc-tag>-almalinux-<version>-pr-<number>`), affinché autori e revisori
possano testarla senza compilare localmente — vedi [Immagine container di anteprima](CONTRIBUTING.md#preview-container-image)
nella guida ai contributi. L'immagine viene eliminata automaticamente quando la pull request viene chiusa.

<br/>


## Documentazione

- [Guida ai workflow CI](.github/workflows/README.md)
- [Homepage di GEMC](https://gemc.github.io/home/)
- [Repository dell'API Python](https://github.com/gemc/pygemc)
- [Repository GEMC2 / CLAS12](https://github.com/gemc/clas12Tags)

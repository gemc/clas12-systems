<!-- TRANSLATIONS:START (managed by bin/translate) -->
**Languages:** [EN](README.md) · [IT](README.it.md) · [日本語](README.ja.md) · **FR** · [中文](README.zh.md)
<!-- TRANSLATIONS:END -->

# Systèmes GEMC de CLAS12

[![Test][badge-test]][workflow-test]
[![Comparaison de géométrie ASCII][badge-ascii-geometry]][workflow-ascii-geometry]
[![Déploiement][badge-deploy]][workflow-deploy]
[![Vérification par sanitizers][badge-sanitize]][workflow-sanitize]
[![CodeQL Advanced][badge-codeql]][workflow-codeql]
[![Doxygen][badge-doxygen]][workflow-doxygen]
[![Archives binaires][badge-binary-tarballs]][workflow-binary-tarballs]
[![Version de développement nocturne][badge-dev-release]][workflow-dev-release]
[![Comparaison d'histogrammes HIPO][badge-hipo-histos]][workflow-hipo-histos]
[![Archive macOS][badge-macos-tarball]][workflow-macos-tarball]
[![Profil Valgrind][badge-valgrind-profile]][workflow-valgrind-profile]

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

CLAS12 GEMC Systems contient l'implémentation GEMC3 des systèmes de géométrie des détecteurs de CLAS12 ainsi
que leurs plugins spécifiques. Il s'agit du dépôt compagnon pour CLAS12 de l'application GEMC principale et de
l'API Python de géométrie :

- [`gemc/src`](https://github.com/gemc/src) fournit l'application C++ GEMC, l'intégration de Geant4, les
  chargeurs de géométrie SQLite/ASCII/CAD/GDML, l'infrastructure de plugins dynamiques, les streamers et
  l'environnement `pygemc` embarqué.
- [`gemc/pygemc`](https://github.com/gemc/pygemc) fournit l'API Python utilisée pour définir la géométrie et les
  matériaux, écrire des bases de données GEMC, prévisualiser la géométrie avec PyVista et exporter des scènes
  VTK.js.
- [`gemc/home`](https://github.com/gemc/home) contient le site web public de GEMC, les pages d'installation, les
  tutoriels, les exemples et les ressources de documentation générées.

<br/>

## Périmètre actuel

Ce dépôt est en cours de migration active depuis [`gemc/clas12Tags`](https://github.com/gemc/clas12Tags).

| Système | Statut | Notes |
|---------|---------------------------|-----------------------------------------------------|
| `beamline` | géométrie passive | À venir dans la prochaine version : maillages natifs et CAD |
| `dc` | géométrie et plugin | Utilise coatjava comme source de géométrie |
| `ec` | géométrie et plugin | Utilise coatjava et le plugin partagé `ecal` |
| `field` | plugin | Champ magnétique cartographié de CLAS12 via la bibliothèque cMag |
| `ft` | géométrie et plugins | À venir dans la prochaine version : FTCAL, FTHODO et FTTRK |
| `ftof` | géométrie et plugin | Utilise coatjava comme source de géométrie |
| `ltcc` | géométrie et plugin | Géométrie native et CAD avec surfaces optiques |
| `magnets` | géométrie passive | À venir dans la prochaine version : solénoïde et ensemble des maillages CAD |
| `pcal` | géométrie et plugin partagé | Utilise coatjava et le plugin partagé `ecal` |


<br/>

## GEMC

Le dépôt GEMC principal, [`gemc/src`](https://github.com/gemc/src), est responsable du comportement à
l'exécution. Cela comprend :

- la construction des solides, des volumes logiques et des placements physiques de Geant4
- les plugins C++ dynamiques
- la génération d'événements, les détecteurs sensibles et les streamers de sortie

Ce dépôt est responsable des données d'entrée propres à CLAS12 utilisées à l'exécution :

- la géométrie des détecteurs, les définitions de matériaux,
- les correspondances de run et de variation nécessaires pour reproduire la géométrie de CLAS12
- la validation par rapport à la géométrie et aux données de sortie de référence CLAS12 de GEMC2

Le dépôt [`gemc/pygemc`](https://github.com/gemc/pygemc) définit l'API Python.

> **Compilation à partir de zéro — aucune installation préalable de GEMC requise.** À partir de la prochaine
> version, les systèmes CLAS12 pourront être compilés et installés dans un simple environnement Geant4 (par
> exemple une image `ghcr.io/gemc/g4install`) **sans installation de GEMC** : lorsqu'aucune installation de GEMC
> n'est trouvée, le processus de compilation le compile automatiquement à partir du sous-projet `gemc` et
> l'installe dans le même préfixe. GEMC est recherché dans cet ordre — un emplacement explicite
> `-Duse-gemc-location=<dir>`, puis un GEMC déjà installé (pkg-config ou le binaire `gemc` dans `PATH`), et
> enfin le sous-projet compilé depuis les sources. **Geant4 n'est jamais compilé** : il doit déjà être
> disponible, faute de quoi la configuration échoue. Tous les workflows CI en conteneur utilisent cette méthode
> sur des images g4install pour les distributions prises en charge.

<br/>

## Workflow de géométrie

Chaque système de détecteur est autonome sous `geometry_src/<system>`.

À venir dans la prochaine version : [magnets](geometry_src/magnets/README.md) fournit le solénoïde natif et
39 maillages CAD, avec des placements passifs et les trois configurations de run de GEMC2. Les six membranes
arrière de la région 1 du DC et les six supports appartiennent désormais à [DC](geometry_src/dc/README.md),
chaque groupe utilisant un STL et cinq copies passives. Les blindages en double
`DSShield*` et `apex` sont fournis par le système beamline. Les plaques amont et aval ainsi que les enveloppes
de vide conservent leurs noms d'origine sous forme de maillages optimisés distincts aux trous de fixation comblés.

À venir dans la prochaine version : l'import de beamline préserve la géométrie native de GEMC2 et fournit 49
fichiers STL, dont les trois variantes de l'aimant transverse. Vingt et un éléments de beamline ont des
triangulations réduites ; le moyeu et l'adaptateur sont renommés
`Apex_Shield_Hub` et `Beamline_Adapter_1`. Les 28 autres maillages conservent leurs octets d'origine, y compris
le remplissage en plomb du blindage de sortie, dont le maillage est déjà grossier et dont les faibles jeux avec
l'enveloppe sont préservés. Les trois maillages du dispositif de réglage FT sont remplacés par un unique
`ft_adjuster` simplifié, dont le volume de l'union correspond à celui de référence.
Les neuf boulons du blindage interne utilisent `FTInnerShieldAndFlange_Bolt1` à `Bolt9`, avec des tiges lisses
et des têtes simplifiées qui respectent leurs volumes de cuivre et préservent un jeu avec le blindage.
L'ensemble blindage interne et bride est renommé `FTInnerShieldAndFlange`, avec sa cavité fermée préservée.
La bride externe est renommée `FTOuterFlange` et simplifiée en comblant ses douze trous de boulons.
Le support externe est renommé `FTOuterMount`, réparé et évidé pour dégager la bride externe.
Le blindage interne FT aval est renommé `FTInnerShield`, avec les trous de boulons fermés,
les deux faces de bride lisses et les rainures longitudinales conservées.
Le cône de Moller est renommé `moller_cone`, avec les trous de surface comblés et l'ouverture élargie pour
dégager le blindage interne FT aval. Il n'y a pas de plugin de numérisation pour les volumes sensibles.
Consultez les [notes sur beamline](geometry_src/beamline/README.md) pour
les variations, les cartes de pilotage,
les contrôles de qualité des maillages, le test de performance à particules primaires identiques et les
avertissements restants concernant les maillages bruts.

Un répertoire de système type contient :

| Fichier | Rôle |
|----------------------------------------------|--------------------------------------------------------------------------------------|
| `<system>.py` | Script principal exécutable ; crée `autogeometry()` et publie les matériaux et les volumes |
| `geometry.py` | Code de construction de la géométrie |
| `materials.py` | Définitions des matériaux du système |
| `variations.py` | Correspondances optionnelles de run et de variation |
| `<system>.yaml` | Carte de pilotage GEMC pour des exécutions locales rapides |
| `../coatjava_factories/CoatjavaFactory.java` | Passerelle coatjava optionnelle pour les services de géométrie Java |
| `plugin/meson.build` | Enregistrement optionnel d'un plugin C++ de numérisation ou d'autres extensions d'exécution |

Le script principal doit être exécutable et pouvoir être lancé directement depuis son répertoire :

```shell
cd geometry_src/dc
./dc.py 
```

Utilisez les options PyVista de `pygemc` lorsqu'un système est prêt pour une inspection visuelle :

```shell
./dc.py -pvb
```

Lancez GEMC avec la carte de pilotage locale :

```shell
gemc dc.yaml
gemc dc.yaml -gui
```

Les lignes de géométrie sensible sélectionnent leur plugin d'exécution via le champ `digitization` du volume.
La clé optionnelle `digitization` d'une entrée YAML `gsystem` a un rôle plus restreint : elle indique à GEMC
quel plugin portant un nom différent sonder avant d'analyser les options, comme lorsque les systèmes `ec` et
`pcal` partagent `ecal.gplugin`. FT possède trois noms sensibles (`ft_cal`, `ft_hodo` et `ft_trk`), c'est pourquoi
son YAML conserve une simple entrée `name: ft`. Le plugin `ft.gplugin`, réservé aux options, enregistre les
trois domaines lors du sondage d'amorçage ; le chargement de la géométrie découvre et charge ensuite les trois
numériseurs à partir des lignes sensibles.

<br/>

## Contrôles de référence

Utilisez `scripts/compare_ascii_databases.py` pour comparer les bases de données ASCII GEMC3 générées
(géométrie et matériaux) aux fichiers de référence correspondants de
[`gemc/clas12Tags`](https://github.com/gemc/clas12Tags) :

```shell
scripts/compare_ascii_databases.py dc
```

Sans argument de système, le script vérifie chaque implémentation locale `geometry_src/<system>/<system>.py`.
Le script met en correspondance les colonnes ASCII de GEMC2 et GEMC3 avec des champs de géométrie communs — nom,
volume mère, position, rotation, solide, dimensions, matériau, numérisation (`sensitivity` de GEMC2) et
identifiant (`identifiers` de GEMC2, développé sous une forme canonique `name=value`) — et compare uniquement
ces valeurs de champs par nom de volume, afin que les différences de mise en forme et d'ordre des colonnes ne
masquent pas les correspondances géométriques réelles. Les matériaux sont comparés de la même façon par nom de
matériau (densité, composants, propriétés optiques et de scintillation), pour les systèmes qui définissent des
matériaux personnalisés. Les représentations numériques et l'ordre des tableaux des polycônes GEMC2/GEMC3 sont
normalisés avant comparaison.

Lorsqu'un champ diffère, le script affiche les écarts champ par champ et se termine avec le code `1` ; une
exécution où tout concorde se termine avec le code `0`.

<br/>

## Placement et rotations

GEMC3 prend en charge les deux conventions de placement de Geant4 via `GVolume.g4placement_type` :

| Valeur | Signification |
|-----------|----------------------------------------------------------------------------------------|
| `active` | Comportement GEMC3 par défaut ; utilise `G4Transform3D(rotation, translation)` |
| `passive` | Comportement compatible avec GEMC2/clas12Tags ; utilise `G4PVPlacement(rotation, translation, ...)` |

Les volumes de détecteur CLAS12 portés depuis GEMC2 devraient utiliser la convention de placement passive :

```python
gvolume.g4placement_type = "passive"
```

Conservez les rotations ordonnées sous forme ordonnée dans la base de données. Par exemple, n'aplatissez pas :

```text
ordered: yxz, 0*deg, 0*deg, 6*deg
```

GEMC applique les rotations ordonnées dans l'ordre spécifié. C'est indispensable pour le DC et devrait aussi
avoir une incidence sur d'autres systèmes CLAS12 portés depuis `clas12Tags`.

<br/>

## Coatjava

Certains systèmes CLAS12 utilisent coatjava afin que la géométrie de simulation suive le même service de
géométrie Java que celui utilisé pour la reconstruction. Ce dépôt conserve coatjava localement dans
`geometry_src` :

```shell
./geometry_src/install_coatjava.sh -l
```

La configuration Meson installe coatjava automatiquement si `geometry_src/coatjava` est absent. La CI et les
images Docker doivent d'abord fournir les prérequis :

- Java
- Maven
- git-lfs
- jq

Les scripts auxiliaires sont :

| Chemin | Objectif |
|------------------------------------|-------------------------------------------------------------------|
| `geometry_src/install_coatjava.sh` | Installe la copie locale de coatjava |
| `ci/install_coatjava_deps.sh` | Installe Java, Maven, git-lfs et jq dans les images CI prises en charge |
| `ci/setup_coatjava.sh` | Script auxiliaire CI qui installe les prérequis, puis coatjava si nécessaire |

Ne supprimez pas une installation coatjava existante à moins que l'option de réinitialisation ne soit
explicitement demandée.

<br/>

## Compilation et tests

Ce dépôt est compilé avec Meson et utilise les dépendances GEMC et Geant4 configurées sous `meson/`.

Seul **Geant4** doit être présent au préalable (chargez son module / assurez-vous que `geant4-config` est dans
`PATH`). GEMC n'a **pas** besoin d'être préinstallé : s'il n'est pas trouvé, il est compilé à partir du
sous-projet `gemc` et installé dans le même `--prefix`. Cela permet d'installer les systèmes CLAS12 à partir de
zéro dans un environnement ne contenant que Geant4 (voir l'encadré de la section [GEMC](#gemc)).

Configurez, compilez et testez :

```shell
meson setup build --prefix="$PWD/install"
meson compile -C build
meson install -C build
meson test -C build --suite clas12 --print-errorlogs
```

**Tests CLAS12 et tests du cœur de GEMC.** Les tests propres à ce dépôt appartiennent tous à la suite `clas12`
(génération de géométrie, construction des détecteurs dans GEMC, connectivité CCDB et contrôles SRO), c'est
pourquoi la commande ci-dessus et la CI (`ci/build.sh`) exécutent `--suite clas12`. Les tests du **cœur** de GEMC
appartiennent à `gemc/src` et ne font pas partie de ce dépôt : lorsque GEMC est compilé ici comme sous-projet
`gemc`, il n'enregistre **aucun** de ses propres tests — ceux-ci testent le GEMC non installé de l'arbre de
compilation et relèvent de la CI de `gemc/src`. Un simple `meson test -C build` ici n'exécute donc que la suite
`clas12` ; le dépôt de référence pour exécuter la suite du cœur de GEMC est
[`gemc/src`](https://github.com/gemc/src) lui-même. (L'option `-Dinclude-subproject-tests=true` régit les autres
sous-projets embarqués — CCDB, HIPO, clas12-cmag — et non GEMC.)

À venir dans la prochaine version : chaque détecteur dispose d'un test de bon fonctionnement `gemc_<system>`
dans les suites `clas12` et `gemc`. Après la génération de la géométrie, il démarre le GEMC installé, construit
la géométrie native et CAD, puis charge les plugins du détecteur avec zéro événement et sans champ magnétique,
dans un répertoire temporaire isolé. Une fois que les tests de géométrie ont rempli `build/clas12.db`, relancez
uniquement la construction de la géométrie avec `meson test -C build --suite gemc --print-errorlogs`. Lorsque
GEMC est compilé en tant que sous-projet, installez-le avant les tests afin que l'exécutable dispose de
l'organisation des répertoires nécessaire à son exécution.

Pour réutiliser une installation GEMC existante au lieu de le compiler, passez `-Duse-gemc-location=<dir>` (ou
placez son binaire `gemc` dans `PATH`).

Utilisez ces options indépendantes pour réutiliser des installations de bibliothèques existantes et des cartes
de champ magnétique. Les trois options de bibliothèque et la configuration de l'emplacement par défaut pour le
plugin de champ sont à venir dans la prochaine version.

| Option Meson | Chemin à fournir |
| --- | --- |
| `-Duse-gemc-location=<dir>` | Préfixe d'installation de GEMC |
| `-Duse-ccdb-location=<dir>` | Préfixe d'installation de CCDB |
| `-Duse-hipo-location=<dir>` | Préfixe d'installation de HIPO |
| `-Duse-clas12-cmag-location=<dir>` | Préfixe d'installation de clas12-cmag |
| `-Duse-fields-location=<dir>` | Répertoire contenant les cartes de champ magnétique de CLAS12 |

Par exemple, pour réutiliser les quatre :

```shell
meson setup build --prefix="$PWD/install" \
  -Duse-ccdb-location=/absolute/path/to/ccdb \
  -Duse-hipo-location=/absolute/path/to/hipo \
  -Duse-clas12-cmag-location=/absolute/path/to/clas12-cmag \
  -Duse-fields-location=/absolute/path/to/magfield
```

Chaque option est vide par défaut et peut être définie indépendamment. Une option de bibliothèque vide préserve
la configuration existante des dépendances. Un chemin de bibliothèque fourni doit être absolu et permet
d'omettre ce sous-projet ; les installations invalides font échouer la configuration. Les en-têtes sont attendus
sous `include/` (également `includes/` pour les anciennes installations de clas12-cmag), et les bibliothèques sous
`lib/` ou `lib64/`. L'option Meson `-Dprefer_static=true` privilégie les bibliothèques statiques lorsque les deux
types sont installés ; les bibliothèques statiques utilisées par les plugins doivent être compilées avec du
code indépendant de la position. Une installation de CCDB nécessite les outils de développement du client
MySQL/MariaDB et SQLite ; une installation de HIPO nécessite les paquets de développement LZ4 et fmt.
Les installations externes ne sont pas copiées par `meson install`.

Avec `-Duse-fields-location=<dir>`, aucune carte n'est récupérée ni installée, et le plugin de champ utilise ce
répertoire par défaut. Un paramètre de champ `dir` explicite reste prioritaire. Lorsque l'option est vide, les
cartes proviennent du sous-projet git-lfs `magfield` et sont installées sous `<prefix>/fields` ; le plugin
localise ce répertoire par rapport à son propre emplacement d'installation. La récupération des cartes nécessite
git-lfs.

GEMC lui-même est recherché de la même manière. `-Duse-gemc-location=<dir>` utilise le GEMC installé sous ce
préfixe absolu (le fichier `lib/pkgconfig/gemc.pc` est attendu). Lorsque l'option est vide, un GEMC déjà installé
est utilisé s'il est trouvé via pkg-config ou le binaire `gemc` dans `PATH` ; sinon, le sous-projet `gemc` est
compilé à partir des sources. Geant4 n'est jamais compilé : il doit déjà être disponible (chargez le module
Geant4 avant la configuration), et la configuration échoue s'il est absent.

À venir dans la prochaine version : la version embarquée de CCDB utilise SQLite du système via
`ccdb_system_sqlite.patch`, évitant ainsi sa propre amalgamation SQLite. Les copies de travail existantes du
sous-projet CCDB qui n'ont pas reçu ce correctif doivent être renouvelées avant toute recompilation :

```shell
meson subprojects purge --confirm ccdb
```

Configurez ensuite un répertoire de compilation propre afin que Meson récupère CCDB et applique les correctifs
du wrap.

Les tests de géométrie exécutent chaque système Python enregistré et écrivent la base de données SQLite
combinée :

```shell
meson test -C build geometry_dc --print-errorlogs
sqlite3 build/clas12.db "select system, variation, run, count(*) from geometry group by 1,2,3;"
```

Le registre des systèmes CLAS12 se trouve actuellement dans `meson.build` :

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

N'ajoutez un nom de détecteur à cette liste que lorsque `geometry_src/<system>/<system>.py` est prêt à générer
une géométrie GEMC valide.

<br/>

## Constantes de calibration CCDB

Les plugins de numérisation des détecteurs (`dc`, `ecal`, `ft_cal`, `ft_hodo`, `ftof`, `ltcc`) chargent leurs
constantes de calibration depuis CCDB. Par défaut, ils se connectent à la base de données du JLab à
`mysql://clas12reader@clasdb.jlab.org/clas12` ; définissez la variable d'environnement `CCDB_CONNECTION` pour
pointer vers un autre serveur ou vers un instantané SQLite local (`sqlite:///path/to/ccdb.sqlite`). Il s'agit
de la base de données CCDB, et non de la base de données des détecteurs `clas12.sqlite` de GEMC2 — pointer vers
cette dernière renvoie des constantes vides. En cas d'échec de CCDB (hôte injoignable, mauvaise base de données,
table vide), les plugins interrompent désormais l'exécution avec un message d'erreur clair au lieu de produire
silencieusement une sortie numérisée vide.

### Connecteur MariaDB ou MySQL (macOS)

La bibliothèque cliente CCDB nécessite une attention particulière sur macOS. Le compte `clas12reader`
s'authentifie avec `mysql_native_password`, un mécanisme qu'Oracle a **supprimé** de la bibliothèque cliente
MySQL dans la version 9.0 (il repose sur SHA1 et a été déprécié pour des raisons de sécurité). Une bibliothèque
CCDB liée à MySQL 9.x ne peut donc pas s'authentifier auprès de clasdb et échoue au moment de la connexion —
c'est une limitation de la bibliothèque cliente, et non un bug de CCDB, et aucune modification du code source
de CCDB ne peut restaurer une fonctionnalité exclue lors de la compilation de la bibliothèque. Installez un
connecteur qui la fournit encore :

```shell
brew install mariadb-connector-c   # preferred: maintained; supports native_password and caching_sha2_password
# or
brew install mysql-client@8.4      # Oracle LTS that still ships native_password
```

Le processus de compilation Meson sélectionne automatiquement le connecteur CCDB (`meson/meson.build`), en
privilégiant, dans l'ordre, `mariadb-connector-c`, `mysql-client@8.4`, `mysql-client`, puis `mysql`, de sorte
qu'une compilation propre lie un client fonctionnel sans nouvelle édition de liens manuelle. Si seul MySQL 9.x
est installé, CCDB compile tout de même, mais la connexion à clasdb échoue avec un message d'erreur clair
jusqu'à ce qu'un connecteur compatible soit installé (ou que le compte serveur migre vers
`caching_sha2_password`).

Il existe une seconde difficulté, indépendante de la première et propre à MariaDB : `mariadb-connector-c`
**impose TLS par défaut**, alors que clasdb fonctionne sans SSL ; une compilation avec MariaDB sans adaptation
échoue donc avec `Error 2026 (SSL is required, but the
server does not support it)`. Le sous-projet `ccdb` reçoit un correctif (via `subprojects/ccdb.wrap`
`diff_files` → `subprojects/packagefiles/ccdb_ssl_no_enforce.patch`) pour désactiver l'obligation d'utiliser TLS
lorsqu'il est compilé avec MariaDB, conformément au repli par défaut vers une connexion en clair de
libmysqlclient d'Oracle. Le correctif est conditionné par `#ifdef LIBMARIADB` et reste donc sans effet pour les
clients MySQL/Oracle (qui ont supprimé cette option et n'imposent de toute façon pas TLS). Avec ce correctif,
`mariadb-connector-c` se connecte à clasdb et constitue le connecteur recommandé.

<br/>

## Chemin des plugins

Les plugins des systèmes CLAS12 sont installés sous forme de bibliothèques partagées `.gplugin` dans
`<prefix>/lib/`. GEMC localise les plugins en cherchant, dans l'ordre : `GEMC_PLUGIN_PATH`, ses propres
répertoires `lib/` et `build/`, puis le chemin de recherche des bibliothèques dynamiques du système
d'exploitation (`LD_LIBRARY_PATH` sous Linux, `DYLD_LIBRARY_PATH` sous macOS).

La configuration la plus simple consiste à installer les systèmes CLAS12 dans le préfixe de GEMC, afin que les
bibliothèques `.gplugin` se trouvent dans le répertoire `lib/` que GEMC parcourt déjà et qu'aucune variable
d'exécution ne soit nécessaire. Le préfixe de GEMC se situe un niveau au-dessus de son répertoire `bin/` ;
il peut donc être déduit à partir de `command -v gemc` :

```shell
meson setup build --prefix="$(dirname "$(dirname "$(command -v gemc)")")"
meson install -C build
gemc dc.yaml
```

Si GEMC est dans `PATH` mais qu'un préfixe différent est configuré, Meson affiche un avertissement lors de la
configuration. Dans ce cas, définissez `GEMC_PLUGIN_PATH` sur le répertoire des bibliothèques des systèmes CLAS12
avant de lancer `gemc` :

```shell
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
gemc dc.yaml
```

Ou passez-le en ligne de commande :

```shell
gemc dc.yaml -plugin_path=/path/to/clas12-systems/lib
```

Si un plugin est introuvable, GEMC affiche la valeur actuelle de `GEMC_PLUGIN_PATH` avec l'erreur pour aider à
diagnostiquer les problèmes de chemin.

Le préfixe d'installation d'une compilation Meson expose le répertoire des plugins via un fichier pkg-config :

```shell
# After: meson install -C build --prefix=/my/clas12/prefix
export PKG_CONFIG_PATH=/my/clas12/prefix/lib/pkgconfig:$PKG_CONFIG_PATH
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
```

<br/>


## Modèle de compilation des plugins

Les plugins des systèmes utilisent un modèle de registre :

1. Un fichier `geometry_src/<system>/plugin/meson.build` propre au détecteur ajoute des dictionnaires à
   `clas12_plugins`.
2. Le fichier `meson.build` de premier niveau est le seul endroit qui transforme ces entrées en bibliothèques
   partagées installées.
3. Les plugins GEMC installés doivent utiliser le suffixe `.gplugin`.

Cela garantit une installation cohérente des plugins entre les systèmes CLAS12 et évite que chaque détecteur
définisse sa propre logique de compilation.

### Modèles de journalisation

À venir dans la prochaine version : la journalisation des plugins utilise l'API `GLogger` à messages complets.
Gardez la phrase anglaise d'un seul tenant et passez les valeurs à l'aide de paramètres de substitution
numérotés :

```cpp
log->info(1, "Loaded %1 constants for run %2.", count, runno);
```

`debug`, `warning`, `error` et `critical` suivent les mêmes règles de substitution. Recompilez les plugins avec
les en-têtes GEMC correspondants ; les anciens appels par concaténation doivent être migrés. Le texte de
diagnostic dynamique peut être passé comme valeur avec `log->warning("%1", text)` afin que ses signes de
pourcentage restent littéraux.

Le catalogue anglais généré se trouve dans `translations/en.yaml` ; `translations/catalog.yaml` sélectionne les
fichiers sources des plugins dont les messages sont issus. Régénérez-le ou vérifiez-le à l'aide de l'extracteur
partagé de l'arbre source GEMC voisin :

```shell
../src/build/subprojects/pygemc/python_env/bin/python ../src/ci/extract_messages.py extract --root .
../src/build/subprojects/pygemc/python_env/bin/python ../src/ci/extract_messages.py extract --root . --check
../src/build/subprojects/pygemc/python_env/bin/python ../src/ci/extract_messages.py validate-tree --root .
```

Modifiez les messages anglais dans le code C++, plutôt que dans le catalogue généré. Consultez le
[guide du catalogue](https://github.com/gemc/src/blob/main/translations/README.md) pour la validation des
traductions. La journalisation à l'exécution sélectionne la langue automatiquement ; `-language=it` sélectionne
l'italien et `-language=en` force l'anglais. Les messages manquants conservent leur texte anglais. Meson installe
les catalogues des plugins sous `<prefix>/share/gemc/translations/clas12` ; les chemins de recherche existants
des plugins rendent accessibles les catalogues situés dans d'autres préfixes d'installation. Recompilez les
plugins avec les en-têtes GEMC correspondants et la nouvelle bibliothèque `glogging`. Le workflow Claude/Codex
partagé génère les catalogues de langues via la tâche cron existante exécutée les jours de semaine ; son entrée
`gemc/clas12-messages` utilise des lots validés dont le traitement peut reprendre après interruption et suit le
commit git source. Le workflow Test valide également chaque catalogue généré sans agents, en vérifiant les
fichiers de langue requis, les clés, les paramètres de substitution, les échappements des signes de pourcentage
et les caractères d'espacement. Les messages manquants donnent lieu à un rapport de couverture avec repli vers
l'anglais ; l'exactitude des traductions reste du ressort de la révision par agent.

<br/>

## Champ magnétique

CLAS12 utilise un champ magnétique **cartographié** — les cartes de champ mesurées du solénoïde et du tore —
plutôt qu'un modèle analytique. Le champ est fourni par le plugin `gfieldclas12-cmag` sous `plugins/field/`, qui
lit les cartes binaires du solénoïde et du tore de CLAS12 via la bibliothèque
[cMag](https://github.com/JeffersonLab/clas12-cmag) de David Heddle (le sous-projet `clas12-cmag`) et renvoie le
champ résultant à chaque point de pas.

Le champ est configuré avec le nœud générique `gfields` du cœur de GEMC, en sélectionnant ce plugin avec
`type: clas12-cmag` :

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

La valeur de `global_field` est le nom du champ configuré (`clas12` ci-dessus), et non les noms des cartes du
solénoïde et du tore. Les noms des cartes et les facteurs d'échelle par carte appartiennent à l'entrée
`gfields`. Cela remplace le style GEMC2 `global_field: Symm_solenoid_...:Symm_torus_...` et les anciennes cibles
d'échelle codées en dur `binary_torus` / `binary_solenoid` par les paramètres explicites `torus`, `solenoid`,
`torus_scale` et `solenoid_scale`.

Toute clé scalaire supplémentaire (déplacements par carte, origine/rotation globale, `interpolation`) est
transmise telle quelle au plugin.

Les cartes de champ proviennent du sous-projet git-lfs `magfield` et sont copiées vers `<prefix>/fields` lors de
`meson
install` (voir `meson/install_fields.py`) ; le plugin les lit depuis le répertoire `fields` installé à côté de
lui (`<plugin_dir>/../fields`). La configuration avec `-Duse-fields-location=<dir>` omet le sous-projet et pointe
à la place vers un répertoire de cartes existant (rien n'est cloné ni installé). Aucune variable
d'environnement `FIELD` ou `FIELD_DIR` n'est nécessaire à l'exécution ; un paramètre `dir` explicite peut
redéfinir l'emplacement.

<br/>

## Lecture en flux (SRO)

**À venir dans la prochaine version.** Les systèmes CLAS12 peuvent émettre des trames de lecture en flux (SRO)
au format binaire DAQ du JLAB à la place de la sortie d'événements ordinaire, ou en complément de celle-ci.
GEMC gère le streamer générique `sro` ; un plugin de système fournit les charges utiles en exportant une
`GSROImplementationFactory` à côté de son numériseur. Actuellement, seul **FT-Cal** fournit des charges utiles
SRO (via `ft_cal.gplugin`) ; les autres numériseurs FT conservent leur sortie normale sans modèle SRO.

Activez SRO depuis la ligne de commande en sélectionnant le format de streamer `sro` et le plugin qui fournit
les charges utiles, et en attribuant à l'acquisition une largeur temporelle d'événement non nulle :

```shell
gemc geometry_src/ft/ft.yaml -n=10000 \
  -gstreamer='[{format: sro, filename: ftcal_sro, implementation: ft_cal}]' \
  -eventTimeWidth='10*ns'
```

- `format: sro` sélectionne le streamer SRO de GEMC ; `implementation: ft_cal` désigne le plugin qui produit les
  charges utiles ; `filename` est le nom de base des fichiers de sortie.
- `-eventTimeWidth` fixe l'espacement entre les événements consécutifs sur la chronologie d'acquisition. Sa
  valeur par défaut, zéro, entraîne le rejet d'une exécution SRO ; elle doit donc être définie explicitement
  (le `10*ns` ci-dessus est un exemple, et non un paramètre mesuré du faisceau de CLAS12). Les exécutions à sortie
  ordinaire n'en ont pas besoin.
- Les fichiers de sortie sont écrits par châssis sous `<basename>_r<resolved_run>_crate<crate>.ev` ; réutiliser
  un nom de base et un run les écrase.

Le module d'enregistrement d'amorçage FT `ft.gplugin` fournit les options de `ft_cal.gplugin`, de sorte qu'aucun
nœud d'options supplémentaire n'est nécessaire. Consultez
[`geometry_src/sro/README.md`](geometry_src/sro/README.md) pour la convention des tables de correspondance, le
modèle temporel des threads de travail (y compris `ft_cal_sro_min_signal_time`), la structure binaire et la
suite de tests `sro` ; les définitions DAQ portées et leur provenance se trouvent dans
[`geometry_src/sro/daq/README.md`](geometry_src/sro/daq/README.md).

<br/>

## Validation

Pour chaque détecteur porté, validez à la fois les lignes de base de données produites et le comportement de la
géométrie à l'exécution.

Contrôles recommandés :

- Comparez les lignes de géométrie générées à la référence GEMC2 sous `geometry_source/<system>` dans
  [`gemc/clas12Tags`](https://github.com/gemc/clas12Tags).
- Confirmez que les noms, volumes mères, descriptions, positions, rotations, solides, paramètres et matériaux
  concordent pour les champs communs.
- Vérifiez que les correspondances de run et de variation sont locales au répertoire du système.
- Utilisez les exports PyVista pour vérifier rapidement les placements avant d'exécuter une simulation Geant4 complète.
- Lancez GEMC en mode batch et en mode graphique lorsqu'un détecteur possède suffisamment de géométrie à inspecter.

Pour le DC, la géométrie par défaut générée devrait correspondre jeton par jeton à :

```text
https://github.com/gemc/clas12Tags/blob/main/geometry_source/dc/dc__geometry_default.txt
```

Propriétés attendues pour le DC :

- le run par défaut est `11`
- tous les volumes du DC utilisent `g4placement_type = "passive"`
- les rotations ordonnées sont préservées sous la forme `ordered: ...`
- la variation obsolète `original` n'est pas prise en charge

<br/>

## CI et versions

À venir dans la prochaine version, tous les workflows en conteneur compilent GEMC et les systèmes CLAS12 à
partir des sources sur des images de base Geant4 publiées par
[`gemc/g4install`](https://github.com/gemc/g4install).
Le [guide des workflows](.github/workflows/README.md) documente les déclencheurs, l'autorisation de déploiement,
les contrats entre dépôts, les permissions, les nouvelles tentatives et les cas où les exécutions sont
normalement ignorées.

Automatisations pertinentes :

| Workflow | Objectif |
|-----------------------|-------------------------------------------------------------------------------------|
| `deploy.yml` | Compile GEMC et les systèmes CLAS12 dans des images de base Geant4, puis publie les images |
| `pr-docker-image.yml` | Crée une image d'aperçu par PR pour tester la branche sans compilation locale |
| `sanitize.yml` | Compile les systèmes CLAS12 avec des sanitizers sans instrumenter les sous-projets tiers |
| `codeql.yml` | Analyse statique |
| `doxygen.yml` | Génération de la documentation |
| `binary_tarballs.yml` | Recompile GEMC et vérifie son bon fonctionnement après le déploiement |
| `dev_release.yml` | Automatisation des versions de développement |

Les images de déploiement utilisent le modèle :

```text
ghcr.io/gemc/clas12-systems:<gemc-tag>-<os>-<version>[-<arch>]
```

Les images de base proviennent de :

```text
ghcr.io/gemc/g4install
```

Chaque pull request publie en outre une image d'aperçu multiarchitecture prête à l'emploi, compilée à partir de
la branche (`ghcr.io/gemc/clas12-systems:<gemc-tag>-almalinux-<version>-pr-<number>`), afin que les auteurs et les
relecteurs puissent la tester sans compilation locale — consultez
[Image de conteneur d'aperçu](CONTRIBUTING.md#preview-container-image) dans le guide de contribution.
L'image est supprimée automatiquement à la fermeture de la pull request.

<br/>


## Documentation

- [Guide des workflows CI](.github/workflows/README.md)
- [Page d'accueil de GEMC](https://gemc.github.io/home/)
- [Dépôt de l'API Python](https://github.com/gemc/pygemc)
- [Dépôt GEMC2 / CLAS12](https://github.com/gemc/clas12Tags)

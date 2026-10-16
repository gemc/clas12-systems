<!-- TRANSLATIONS:START (managed by bin/translate) -->
**Languages:** [EN](README.md) · [IT](README.it.md) · [日本語](README.ja.md) · **FR** · [中文](README.zh.md)
<!-- TRANSLATIONS:END -->

# Systèmes GEMC de CLAS12

[![Test][badge-test]][workflow-test]
[![Comparaison des géométries ASCII][badge-ascii-geometry]][workflow-ascii-geometry]
[![Déploiement][badge-deploy]][workflow-deploy]
[![Vérification par sanitizers][badge-sanitize]][workflow-sanitize]
[![CodeQL avancé][badge-codeql]][workflow-codeql]
[![Doxygen][badge-doxygen]][workflow-doxygen]
[![Archives binaires][badge-binary-tarballs]][workflow-binary-tarballs]
[![Version de développement nocturne][badge-dev-release]][workflow-dev-release]
[![Comparaison des histogrammes HIPO][badge-hipo-histos]][workflow-hipo-histos]
[![Archive macOS][badge-macos-tarball]][workflow-macos-tarball]
[![Profilage Valgrind][badge-valgrind-profile]][workflow-valgrind-profile]

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

CLAS12 GEMC Systems contient l'implémentation GEMC3 des systèmes de géométrie des détecteurs de CLAS12 et
leurs plugins spécifiques. Il s'agit du dépôt complémentaire pour CLAS12 de l'application GEMC principale et de
l'API Python de géométrie :

- [`gemc/src`](https://github.com/gemc/src) fournit l'application C++ GEMC, l'intégration Geant4, les
  chargeurs de géométrie SQLite/ASCII/CAD/GDML, l'infrastructure de plugins dynamiques, les modules de
  diffusion des données et l'environnement `pygemc` intégré.
- [`gemc/pygemc`](https://github.com/gemc/pygemc) fournit l'API Python permettant de définir la géométrie et
  les matériaux, d'écrire les bases de données GEMC, de prévisualiser la géométrie avec PyVista et d'exporter des
  scènes VTK.js.
- [`gemc/home`](https://github.com/gemc/home) contient le site web public de GEMC, les pages d'installation,
  les tutoriels, les exemples et les ressources de documentation générées.

<br/>

## Périmètre actuel

Ce dépôt fait l'objet d'une migration active depuis [`gemc/clas12Tags`](https://github.com/gemc/clas12Tags).

| Système | Statut | Remarques |
|---------|---------------------------|-----------------------------------------------------|
| `beamline` | géométrie passive | À venir dans la prochaine version : maillages natifs et CAD |
| `dc` | géométrie et plugin | Utilise coatjava comme source de géométrie |
| `ec` | géométrie et plugin | Utilise coatjava et le plugin partagé `ecal` |
| `field` | plugin | Champ magnétique cartographié de CLAS12 via la bibliothèque cMag |
| `ft` | géométrie et plugins | À venir dans la prochaine version : FTCAL, FTHODO et FTTRK |
| `ftof` | géométrie et plugin | Utilise coatjava comme source de géométrie |
| `ltcc` | géométrie et plugin | Géométrie native et CAD avec surfaces optiques |
| `pcal` | géométrie et plugin partagé | Utilise coatjava et le plugin partagé `ecal` |


<br/>

## GEMC

Le dépôt GEMC principal, [`gemc/src`](https://github.com/gemc/src), définit le comportement à l'exécution.
Cela comprend :

- la construction des solides, des volumes logiques et des placements physiques Geant4
- les plugins C++ dynamiques
- la génération d'événements, les détecteurs sensibles et les modules de diffusion des données de sortie

Ce dépôt fournit les données d'entrée propres à CLAS12 pour ce moteur d'exécution :

- la géométrie des détecteurs, les définitions de matériaux,
- les correspondances de run et de variation nécessaires pour reproduire la géométrie de CLAS12
- la validation par rapport à la géométrie et aux données de sortie de référence CLAS12 de GEMC2

Le dépôt [`gemc/pygemc`](https://github.com/gemc/pygemc) définit l'API Python.

> **Compilation à partir de zéro — aucune installation préalable de GEMC requise.** À compter de la prochaine
> version, les systèmes CLAS12 pourront être compilés et installés dans un environnement Geant4 de base
> (par exemple une image `ghcr.io/gemc/g4install`) **sans installation de GEMC** : lorsqu'aucune installation
> de GEMC n'est trouvée, le processus de compilation le compile automatiquement à partir du sous-projet `gemc`
> et l'installe dans le même préfixe. GEMC est recherché dans cet ordre : un emplacement explicite
> `-Duse-gemc-location=<dir>`, puis une installation existante de GEMC (via pkg-config ou le binaire `gemc`
> dans `PATH`), et enfin le sous-projet compilé depuis les sources. **Geant4 n'est jamais compilé** : il doit
> déjà être disponible, sinon la configuration échoue. Tous les workflows CI en conteneur suivent cette
> procédure sur des images g4install pour les distributions prises en charge.

<br/>

## Flux de travail de géométrie

Chaque système de détecteur est autonome dans `geometry_src/<system>`.

À venir dans la prochaine version : l'importation de la ligne de faisceau préserve la géométrie native de GEMC2
et fournit 49 fichiers STL, dont les trois variantes de l'aimant transverse. Vingt et un éléments de la ligne
de faisceau ont des triangulations réduites ; le moyeu et l'adaptateur sont renommés
`Apex_Shield_Hub` et `Beamline_Adapter_1`. Les 28 autres maillages conservent leurs octets d'origine, y compris
le remplissage en plomb du blindage de sortie, dont le maillage est déjà grossier et dont les faibles jeux avec
l'enveloppe sont préservés. Les trois maillages de pièces de réglage FT sont remplacés par un seul maillage
simplifié `ft_adjuster`, dont le volume correspond à celui de l'union de référence.
Les neuf boulons du blindage interne utilisent les noms `FTInnerShieldAndFlange_Bolt1` à `Bolt9`, avec des tiges
lisses et des têtes simplifiées qui préservent leurs volumes de cuivre et laissent un jeu avec le blindage.
L'ensemble blindage interne et bride est renommé `FTInnerShieldAndFlange`, et sa cavité fermée est préservée.
La bride externe est renommée `FTOuterFlange` et simplifiée en comblant ses douze trous de boulons.
Le support externe est renommé `FTOuterMount`, réparé et évidé pour éviter toute interférence avec la bride externe.
Le blindage interne FT en aval est renommé `FTInnerShield` ; ses trous de boulons sont obturés,
les deux faces de sa bride sont lissées et ses rainures longitudinales sont conservées.
Le cône de Møller est renommé `moller_cone` ; ses trous de surface sont comblés et son ouverture est agrandie
pour éviter toute interférence avec le blindage interne FT en aval. Aucun plugin de numérisation n'est associé
à un détecteur sensible.
Voir les [notes sur la ligne de faisceau](geometry_src/beamline/README.md) pour les
variations, les cartes de pilotage,
les contrôles de qualité des maillages, le test de performance à particules primaires identiques et les
avertissements restants sur les maillages bruts.

Un répertoire de système type contient :

| Fichier | Rôle |
|----------------------------------------------|--------------------------------------------------------------------------------------|
| `<system>.py` | Script principal exécutable ; crée `autogeometry()` et publie les matériaux et les volumes |
| `geometry.py` | Code de construction de la géométrie |
| `materials.py` | Définitions des matériaux du système |
| `variations.py` | Correspondance facultative des runs et des variations |
| `<system>.yaml` | Carte de pilotage GEMC pour des exécutions locales rapides |
| `../coatjava_factories/CoatjavaFactory.java` | Passerelle coatjava facultative pour les services de géométrie Java |
| `plugin/meson.build` | Enregistrement facultatif d'un plugin C++ de numérisation ou d'autres extensions d'exécution |

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

Les lignes de géométrie des volumes sensibles sélectionnent leur plugin d'exécution via le champ `digitization`
du volume. La clé facultative `digitization` d'une entrée YAML `gsystem` a un rôle plus restreint : elle indique
à GEMC quel plugin portant un nom différent sonder avant d'analyser les options, comme lorsque les systèmes
`ec` et `pcal` partagent `ecal.gplugin`. FT comporte trois noms de détecteurs sensibles (`ft_cal`, `ft_hodo` et
`ft_trk`), de sorte que son YAML conserve une simple entrée `name: ft`. Le plugin `ft.gplugin`, consacré
uniquement aux options, enregistre les trois domaines lors du sondage d'amorçage ; le chargement de la géométrie
découvre et charge ensuite les trois modules de numérisation à partir des lignes des volumes sensibles.

<br/>

## Contrôles de référence

Utilisez `scripts/compare_ascii_databases.py` pour comparer les bases de données ASCII GEMC3 générées
(géométrie et matériaux) aux fichiers de référence correspondants de
[`gemc/clas12Tags`](https://github.com/gemc/clas12Tags) :

```shell
scripts/compare_ascii_databases.py dc
```

Sans argument désignant un système, le script vérifie chaque implémentation locale
`geometry_src/<system>/<system>.py`. Il met en correspondance les colonnes ASCII de GEMC2 et GEMC3 avec des
champs de géométrie communs — nom, volume mère, position, rotation, solide, dimensions, matériau, numérisation
(`sensitivity` dans GEMC2) et identifiant (`identifiers` dans GEMC2, développé sous la forme canonique
`name=value`) — et compare uniquement les valeurs de ces champs par nom de volume, afin que les différences de
formatage et d'ordre des colonnes ne masquent pas les correspondances réelles de géométrie. Les matériaux sont
comparés de la même manière par nom de matériau (densité, composants, propriétés optiques et de scintillation),
pour les systèmes qui définissent des matériaux personnalisés. Les représentations numériques et les ordres
des tableaux de polycônes GEMC2/GEMC3 sont normalisés avant la comparaison.

Lorsqu'un champ diffère, le script affiche les écarts champ par champ et se termine avec le code de retour `1` ;
une exécution sans différence se termine avec le code de retour `0`.

<br/>

## Placement et rotations

GEMC3 prend en charge les deux conventions de placement de Geant4 via `GVolume.g4placement_type` :

| Valeur | Signification |
|-----------|----------------------------------------------------------------------------------------|
| `active` | Comportement par défaut de GEMC3 ; utilise `G4Transform3D(rotation, translation)` |
| `passive` | Comportement compatible avec GEMC2/clas12Tags ; utilise `G4PVPlacement(rotation, translation, ...)` |

Les volumes des détecteurs CLAS12 portés depuis GEMC2 doivent utiliser la convention de placement passive :

```python
gvolume.g4placement_type = "passive"
```

Conservez l'ordre des rotations ordonnées dans la base de données. Par exemple, ne réduisez pas cette séquence :

```text
ordered: yxz, 0*deg, 0*deg, 6*deg
```

GEMC applique les rotations ordonnées dans l'ordre indiqué. Cela est nécessaire pour le DC et devrait aussi
avoir une incidence sur les autres systèmes CLAS12 portés depuis `clas12Tags`.

<br/>

## Coatjava

Certains systèmes CLAS12 utilisent coatjava afin que la géométrie de simulation suive le même service de
géométrie Java que celui utilisé par la reconstruction. Ce dépôt conserve coatjava localement dans
`geometry_src` :

```shell
./geometry_src/install_coatjava.sh -l
```

La configuration Meson installe coatjava automatiquement si `geometry_src/coatjava` est absent. Les images CI
et Docker doivent d'abord fournir les prérequis :

- Java
- Maven
- git-lfs
- jq

Les scripts utilitaires sont :

| Chemin | Rôle |
|------------------------------------|-------------------------------------------------------------------|
| `geometry_src/install_coatjava.sh` | Installe la copie locale de coatjava |
| `ci/install_coatjava_deps.sh` | Installe Java, Maven, git-lfs et jq dans les images CI prises en charge |
| `ci/setup_coatjava.sh` | Utilitaire CI qui installe les prérequis, puis coatjava si nécessaire |

Ne supprimez pas une installation coatjava existante sauf si l'option de réinitialisation est explicitement
demandée.

<br/>

## Compilation et tests

Ce dépôt est compilé avec Meson et utilise les dépendances GEMC et Geant4 configurées dans `meson/`.

Seul **Geant4** doit être présent au préalable (chargez son module / rendez `geant4-config` accessible dans
`PATH`). GEMC n'a **pas** besoin d'être préinstallé : s'il est introuvable, il est compilé à partir du
sous-projet `gemc` et installé dans le même `--prefix`. Cela permet d'installer les systèmes CLAS12 à partir de
zéro dans un environnement Geant4 de base (voir l'encadré de la section [GEMC](#gemc)).

Configurez, compilez et testez :

```shell
meson setup build --prefix="$PWD/install"
meson compile -C build
meson install -C build
meson test -C build --suite clas12 --print-errorlogs
```

**Tests CLAS12 et tests du cœur de GEMC.** Les tests propres à ce dépôt appartiennent tous à la suite `clas12`
(génération de géométrie, construction des détecteurs dans GEMC, connectivité CCDB et contrôles SRO), ce qui
explique pourquoi la commande ci-dessus et la CI (`ci/build.sh`) exécutent `--suite clas12`. Les tests du
**cœur** de GEMC appartiennent à `gemc/src` et ne font pas partie de ce dépôt : lorsque GEMC est compilé ici en
tant que sous-projet `gemc`, il n'enregistre **aucun** de ses propres tests — ceux-ci testent le GEMC non installé
de l'arbre de compilation et relèvent de la CI propre à `gemc/src`. Un simple `meson test -C build` exécuté ici
ne lance donc que la suite `clas12` ; le dépôt [`gemc/src`](https://github.com/gemc/src) lui-même est l'endroit
de référence pour exécuter la suite du cœur de GEMC. (L'option `-Dinclude-subproject-tests=true` régit les autres
sous-projets intégrés — CCDB, HIPO, clas12-cmag — et non GEMC.)

À venir dans la prochaine version : chaque détecteur dispose d'un test de bon fonctionnement `gemc_<system>`
dans les suites `clas12` et `gemc`. Après la génération de la géométrie, il démarre le GEMC installé, construit
la géométrie native et CAD, et charge les plugins du détecteur avec zéro événement et sans champ magnétique
dans un répertoire temporaire isolé. Une fois que les tests de géométrie ont rempli `build/clas12.db`, relancez
uniquement la construction avec `meson test -C build --suite gemc --print-errorlogs`. Lorsque GEMC est compilé
en tant que sous-projet, installez-le avant les tests afin que l'exécutable dispose de l'arborescence de
répertoires requise à l'exécution.

Pour réutiliser une installation GEMC existante au lieu de la compiler, passez `-Duse-gemc-location=<dir>` (ou
placez son binaire `gemc` dans `PATH`).

Utilisez ces options indépendantes pour réutiliser des installations de bibliothèques et des cartes de champ
magnétique existantes. Les trois options de bibliothèque et la valeur par défaut configurable du plugin de
champ sont à venir dans la prochaine version.

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

Chaque option a pour valeur par défaut une chaîne vide et peut être définie indépendamment. Une option de
bibliothèque vide préserve la configuration existante des dépendances. Un chemin de bibliothèque fourni doit
être absolu et permet d'omettre le sous-projet correspondant ; une installation non valide fait échouer la
configuration. Les en-têtes sont attendus dans `include/` (également dans `includes/` pour les anciennes
installations de clas12-cmag), et les bibliothèques dans `lib/` ou `lib64/`. L'option `-Dprefer_static=true` de
Meson privilégie les bibliothèques statiques lorsque les deux types sont installés ; les bibliothèques statiques
utilisées par les plugins doivent être compilées avec du code indépendant de la position. Une installation
existante de CCDB nécessite les outils de développement du client MySQL/MariaDB et SQLite ; une installation
existante de HIPO nécessite les paquets de développement LZ4 et fmt. Les installations externes ne sont pas
copiées par `meson install`.

Avec `-Duse-fields-location=<dir>`, aucune carte n'est récupérée ni installée, et le plugin de champ utilise ce
répertoire par défaut. Un paramètre de champ `dir` explicite reste prioritaire. Lorsque l'option est vide,
les cartes proviennent du sous-projet git-lfs `magfield` et sont installées dans `<prefix>/fields` ; le plugin
localise ce répertoire relativement à son propre emplacement d'installation. La récupération des cartes
nécessite git-lfs.

GEMC lui-même est recherché de la même manière. `-Duse-gemc-location=<dir>` utilise le GEMC installé sous ce
préfixe absolu (le fichier `lib/pkgconfig/gemc.pc` doit y être présent). Lorsque l'option est vide, une
installation existante de GEMC est utilisée si elle est trouvée via pkg-config ou le binaire `gemc` dans
`PATH` ; sinon, le sous-projet `gemc` est compilé depuis les sources. Geant4 n'est jamais compilé : il doit
déjà être disponible (chargez le module Geant4 avant la configuration), sinon la configuration échoue.

À venir dans la prochaine version : le CCDB intégré utilise SQLite du système via `ccdb_system_sqlite.patch`,
ce qui évite d'utiliser sa propre version amalgamée de SQLite. Les copies de travail existantes du sous-projet
CCDB auxquelles les correctifs n'ont pas été appliqués doivent être renouvelées avant toute recompilation :

```shell
meson subprojects purge --confirm ccdb
```

Configurez ensuite un répertoire de compilation vierge afin que Meson récupère CCDB et applique les correctifs
des fichiers wrap.

Les tests de géométrie exécutent chaque système Python enregistré et écrivent la base de données SQLite combinée :

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
    'pcal',
]
```

N'ajoutez un nom de détecteur à cette liste que lorsque `geometry_src/<system>/<system>.py` est prêt à générer
une géométrie GEMC valide.

<br/>

## Constantes d'étalonnage CCDB

Les plugins de numérisation des détecteurs (`dc`, `ecal`, `ft_cal`, `ft_hodo`, `ftof`, `ltcc`) chargent leurs
constantes d'étalonnage depuis CCDB. Par défaut, ils se connectent à la base de données de JLab à l'adresse
`mysql://clas12reader@clasdb.jlab.org/clas12` ; définissez la variable d'environnement
`CCDB_CONNECTION` pour utiliser un autre serveur ou un instantané SQLite local
(`sqlite:///path/to/ccdb.sqlite`). Il s'agit de la base de données CCDB, et non de la base de données des
détecteurs GEMC2 `clas12.sqlite` — utiliser cette dernière renvoie des constantes vides. En cas d'échec de CCDB
(hôte injoignable, mauvaise base de données, table vide), les plugins interrompent désormais l'exécution avec
un message d'erreur clair au lieu de produire silencieusement une sortie numérisée vide.

### Connecteur MariaDB ou MySQL (macOS)

La bibliothèque cliente CCDB demande des précautions sur macOS. Le compte `clas12reader` s'authentifie avec
`mysql_native_password`, un mécanisme qu'Oracle a **supprimé** de la bibliothèque cliente MySQL dans la
version 9.0 (il repose sur SHA1 et avait été déprécié pour des raisons de sécurité). Un CCDB lié à MySQL 9.x ne
peut donc pas s'authentifier auprès de clasdb et échoue à la connexion — il s'agit d'une limitation de la
bibliothèque cliente, et non d'un bogue de CCDB ; aucune modification du code source de CCDB ne peut rétablir
une fonctionnalité exclue de la bibliothèque à la compilation. Installez un connecteur qui la fournit toujours :

```shell
brew install mariadb-connector-c   # preferred: maintained; supports native_password and caching_sha2_password
# or
brew install mysql-client@8.4      # Oracle LTS that still ships native_password
```

Le système de compilation Meson sélectionne automatiquement le connecteur CCDB (`meson/meson.build`), en
privilégiant, dans cet ordre, `mariadb-connector-c`, `mysql-client@8.4`, `mysql-client`, puis `mysql`. Une
compilation propre se lie ainsi à un client fonctionnel sans réédition manuelle des liens. Si seul MySQL 9.x
est installé, CCDB se compile tout de même, mais la connexion à clasdb échoue avec un message d'erreur clair
jusqu'à l'installation d'un connecteur compatible (ou la migration du compte serveur vers
`caching_sha2_password`).

Une seconde difficulté, indépendante de la première, est propre à MariaDB : `mariadb-connector-c` **impose TLS
par défaut**, alors que clasdb fonctionne sans SSL ; une compilation avec MariaDB sans adaptation échoue donc
avec `Error 2026 (SSL is required, but the
server does not support it)`. Un correctif est appliqué au sous-projet `ccdb` (via
`subprojects/ccdb.wrap` `diff_files` → `subprojects/packagefiles/ccdb_ssl_no_enforce.patch`) pour désactiver
l'obligation d'utiliser TLS lors de la compilation avec MariaDB, conformément au repli par défaut vers une
connexion en clair de libmysqlclient d'Oracle. Le correctif est protégé par `#ifdef LIBMARIADB` et n'a donc
aucun effet avec les clients MySQL/Oracle (qui ont supprimé cette option et n'imposent de toute façon pas TLS).
Avec ce correctif, `mariadb-connector-c` se connecte à clasdb et constitue le connecteur recommandé.

<br/>

## Chemin des plugins

Les plugins des systèmes CLAS12 sont installés sous forme de bibliothèques partagées `.gplugin` dans
`<prefix>/lib/`. GEMC recherche les plugins dans cet ordre : `GEMC_PLUGIN_PATH`, ses propres répertoires `lib/`
et `build/`, puis le chemin de recherche des bibliothèques dynamiques du système d'exploitation
(`LD_LIBRARY_PATH` sous Linux, `DYLD_LIBRARY_PATH` sous macOS).

La configuration la plus simple consiste à installer les systèmes CLAS12 dans le même préfixe que GEMC, afin
que les bibliothèques `.gplugin` se trouvent dans le répertoire `lib/` déjà parcouru par GEMC et qu'aucune
variable d'environnement ne soit nécessaire à l'exécution. Le préfixe de GEMC se trouve un niveau au-dessus
de son répertoire `bin/` ; on peut donc le déduire à partir de `command -v gemc` :

```shell
meson setup build --prefix="$(dirname "$(dirname "$(command -v gemc)")")"
meson install -C build
gemc dc.yaml
```

Si GEMC est dans `PATH`, mais qu'un préfixe différent est configuré, Meson affiche un avertissement lors de la
configuration. Dans ce cas, définissez `GEMC_PLUGIN_PATH` sur le répertoire des bibliothèques des systèmes
CLAS12 avant de lancer `gemc` :

```shell
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
gemc dc.yaml
```

Ou passez-le sur la ligne de commande :

```shell
gemc dc.yaml -plugin_path=/path/to/clas12-systems/lib
```

Si un plugin est introuvable, GEMC affiche la valeur actuelle de `GEMC_PLUGIN_PATH` avec le message d'erreur
pour faciliter le diagnostic des problèmes de chemin.

L'installation issue d'une compilation Meson expose le répertoire des plugins via un fichier pkg-config :

```shell
# After: meson install -C build --prefix=/my/clas12/prefix
export PKG_CONFIG_PATH=/my/clas12/prefix/lib/pkgconfig:$PKG_CONFIG_PATH
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
```

<br/>


## Modèle de compilation des plugins

Les plugins des systèmes utilisent un mécanisme de registre :

1. Le fichier `geometry_src/<system>/plugin/meson.build` propre à chaque détecteur ajoute des dictionnaires à
   `clas12_plugins`.
2. Le fichier `meson.build` à la racine est le seul endroit qui transforme ces entrées en bibliothèques
   partagées installées.
3. Les plugins GEMC installés doivent utiliser le suffixe `.gplugin`.

Cela assure une installation cohérente des plugins pour tous les systèmes CLAS12 et évite que chaque détecteur
définisse sa propre logique de compilation.

### Modèles de messages de journalisation

À venir dans la prochaine version : la journalisation des plugins utilise l'API `GLogger` à messages complets.
Conservez la phrase anglaise entière et transmettez les valeurs à l'aide de paramètres de substitution numérotés :

```cpp
log->info(1, "Loaded %1 constants for run %2.", count, runno);
```

`debug`, `warning`, `error` et `critical` suivent les mêmes règles de substitution. Recompilez les plugins avec
les en-têtes GEMC correspondants ; les anciens appels par concaténation doivent être migrés. Un texte de
diagnostic dynamique peut être transmis comme valeur avec `log->warning("%1", text)` afin que ses signes de
pourcentage restent littéraux.

Le catalogue anglais généré se trouve dans `translations/en.yaml` ; `translations/catalog.yaml` sélectionne
les fichiers sources des plugins dont les messages relèvent. Régénérez-le ou vérifiez-le à l'aide de
l'extracteur partagé de l'arbre source GEMC voisin :

```shell
../src/build/subprojects/pygemc/python_env/bin/python ../src/ci/extract_messages.py extract --root .
../src/build/subprojects/pygemc/python_env/bin/python ../src/ci/extract_messages.py extract --root . --check
../src/build/subprojects/pygemc/python_env/bin/python ../src/ci/extract_messages.py validate-tree --root .
```

Modifiez les messages anglais dans le code C++, plutôt que dans le catalogue généré. Consultez le
[guide du catalogue](https://github.com/gemc/src/blob/main/translations/README.md) pour la validation des
traductions. La journalisation sélectionne automatiquement la langue à l'exécution ; `-language=it`
sélectionne l'italien et `-language=en` impose l'anglais. Les messages manquants conservent leur texte anglais.
Meson installe les catalogues des plugins dans `<prefix>/share/gemc/translations/clas12` ; les chemins de
recherche existants des plugins donnent accès aux catalogues situés dans d'autres préfixes d'installation.
Recompilez les plugins avec les en-têtes GEMC correspondants et la nouvelle bibliothèque `glogging`. Le
workflow partagé Claude/Codex génère les catalogues de langues via la tâche cron existante exécutée les jours
de semaine ; son entrée `gemc/clas12-messages` utilise des lots validés dont le traitement peut être repris et
suit le commit git des sources. Le workflow Test valide également chaque catalogue généré sans recourir à des
agents, en vérifiant les fichiers de langue requis, les clés, les paramètres de substitution, les échappements
des signes de pourcentage et les caractères d'espacement. Les messages manquants donnent lieu à un rapport de
couverture avec repli vers l'anglais ; l'exactitude des traductions reste vérifiée lors de la revue par les agents.

<br/>

## Champ magnétique

CLAS12 utilise un champ magnétique **cartographié** — les cartes mesurées du champ du solénoïde et du tore —
plutôt qu'un modèle analytique. Le champ est fourni par le plugin `gfieldclas12-cmag` dans `plugins/field/`, qui
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
solénoïde et du tore. Les noms des cartes et leurs facteurs d'échelle respectifs appartiennent à l'entrée
`gfields`. Cela remplace la notation GEMC2 `global_field: Symm_solenoid_...:Symm_torus_...` et les anciennes
cibles de mise à l'échelle codées en dur `binary_torus` / `binary_solenoid` par les paramètres explicites
`torus`, `solenoid`, `torus_scale` et `solenoid_scale`.

Toutes les clés scalaires supplémentaires (déplacements par carte, origine/rotation globales, `interpolation`)
sont transmises telles quelles au plugin.

Les cartes de champ proviennent du sous-projet git-lfs `magfield` et sont copiées dans `<prefix>/fields` lors de
`meson
install` (voir `meson/install_fields.py`) ; le plugin les lit depuis le répertoire `fields` installé à côté de
lui (`<plugin_dir>/../fields`). Une configuration avec `-Duse-fields-location=<dir>` omet le sous-projet et
utilise à la place un répertoire de cartes existant (rien n'est cloné ni installé). Aucune variable
d'environnement `FIELD` ou `FIELD_DIR` n'est nécessaire à l'exécution ; un paramètre `dir` explicite peut
remplacer cet emplacement.

<br/>

## Lecture en flux (SRO)

**À venir dans la prochaine version.** Les systèmes CLAS12 peuvent émettre des trames de lecture en flux (SRO)
au format binaire du système d'acquisition de données (DAQ) de JLAB, à la place des données de sortie
événementielles ordinaires ou en complément de celles-ci. GEMC fournit le module de diffusion générique `sro` ;
un plugin de système fournit les charges utiles en exportant une `GSROImplementationFactory` aux côtés de son
module de numérisation. Actuellement, seul **FT-Cal** fournit des charges utiles SRO (via `ft_cal.gplugin`) ;
les autres modules de numérisation FT conservent leur sortie habituelle sans modèle SRO.

Activez SRO depuis la ligne de commande en sélectionnant le format de diffusion `sro` et le plugin qui fournit
les charges utiles, et en définissant une largeur temporelle d'événement non nulle pour l'acquisition :

```shell
gemc geometry_src/ft/ft.yaml -n=10000 \
  -gstreamer='[{format: sro, filename: ftcal_sro, implementation: ft_cal}]' \
  -eventTimeWidth='10*ns'
```

- `format: sro` sélectionne le module de diffusion SRO de GEMC ; `implementation: ft_cal` désigne le plugin qui
  produit les charges utiles ; `filename` est le nom de base des fichiers de sortie.
- `-eventTimeWidth` définit l'espacement entre événements consécutifs sur l'axe temporel de l'acquisition. Sa
  valeur par défaut, zéro, entraîne le rejet d'une exécution SRO ; elle doit donc être définie explicitement
  (la valeur `10*ns` ci-dessus est un exemple, et non un paramètre mesuré du faisceau CLAS12). Les exécutions
  produisant une sortie ordinaire n'en ont pas besoin.
- Les fichiers de sortie sont écrits par châssis sous la forme `<basename>_r<resolved_run>_crate<crate>.ev` ;
  réutiliser le même nom de base et le même run écrase ces fichiers.

Le module d'enregistrement d'amorçage FT `ft.gplugin` fournit les options pour `ft_cal.gplugin` ; aucun nœud
d'options supplémentaire n'est donc nécessaire. Consultez
[`geometry_src/sro/README.md`](geometry_src/sro/README.md) pour la convention de table de correspondance, le
modèle temporel des processus de travail (y compris `ft_cal_sro_min_signal_time`), le format binaire et la suite
de tests `sro` ; les définitions DAQ portées et leur provenance se trouvent dans
[`geometry_src/sro/daq/README.md`](geometry_src/sro/daq/README.md).

<br/>

## Validation

Pour chaque détecteur porté, validez à la fois les lignes produites dans la base de données et le comportement
de la géométrie à l'exécution.

Contrôles recommandés :

- Comparez les lignes de géométrie générées à la référence GEMC2 dans `geometry_source/<system>` du dépôt
  [`gemc/clas12Tags`](https://github.com/gemc/clas12Tags).
- Confirmez que les noms, volumes mères, descriptions, positions, rotations, solides, paramètres et matériaux
  correspondent pour les champs communs.
- Vérifiez que les correspondances de run et de variation sont locales au répertoire du système.
- Utilisez les exports PyVista pour des contrôles rapides du placement avant de lancer une simulation Geant4
  complète.
- Lancez GEMC en mode batch et en mode graphique lorsqu'un détecteur possède suffisamment de géométrie à inspecter.

Pour le DC, la géométrie par défaut générée doit correspondre jeton par jeton à :

```text
https://github.com/gemc/clas12Tags/blob/main/geometry_source/dc/dc__geometry_default.txt
```

Comportements attendus pour le DC :

- le run par défaut est `11`
- tous les volumes DC utilisent `g4placement_type = "passive"`
- les rotations ordonnées sont préservées sous la forme `ordered: ...`
- la variation obsolète `original` n'est pas prise en charge

<br/>

## CI et versions

À venir dans la prochaine version : tous les workflows en conteneur compilent GEMC et les systèmes CLAS12
depuis les sources sur des images de base Geant4 publiées par
[`gemc/g4install`](https://github.com/gemc/g4install).
Le [guide des workflows](.github/workflows/README.md) documente les déclencheurs, l'autorisation de déploiement,
les contrats entre dépôts, les permissions, les nouvelles tentatives et les cas où une exécution est
normalement ignorée.

Automatisations pertinentes :

| Workflow | Rôle |
|-----------------------|-------------------------------------------------------------------------------------|
| `deploy.yml` | Compiler GEMC et les systèmes CLAS12 dans des images de base Geant4, puis publier les images |
| `pr-docker-image.yml` | Construire une image d'aperçu par PR pour tester la branche sans compilation locale |
| `sanitize.yml` | Compiler les systèmes CLAS12 avec les sanitizers sans instrumenter les sous-projets tiers |
| `codeql.yml` | Analyse statique |
| `doxygen.yml` | Génération de la documentation |
| `binary_tarballs.yml` | Recompiler GEMC et vérifier son bon fonctionnement après le déploiement |
| `dev_release.yml` | Automatisation des versions de développement |

Les images de déploiement suivent le modèle :

```text
ghcr.io/gemc/clas12-systems:<gemc-tag>-<os>-<version>[-<arch>]
```

Les images de base proviennent de :

```text
ghcr.io/gemc/g4install
```

Chaque pull request publie en outre une image d'aperçu multiarchitecture prête à l'emploi, construite à partir
de la branche (`ghcr.io/gemc/clas12-systems:<gemc-tag>-almalinux-<version>-pr-<number>`), afin que les auteurs et
les relecteurs puissent la tester sans compilation locale — voir
[Image de conteneur d'aperçu](CONTRIBUTING.md#preview-container-image) dans le guide de contribution.
L'image est supprimée automatiquement à la fermeture de la pull request.

<br/>


## Documentation

- [Guide des workflows CI](.github/workflows/README.md)
- [Page d'accueil de GEMC](https://gemc.github.io/home/)
- [Dépôt de l'API Python](https://github.com/gemc/pygemc)
- [Dépôt GEMC2 / CLAS12](https://github.com/gemc/clas12Tags)

<!-- TRANSLATIONS:START (managed by bin/translate) -->
**Languages:** [EN](README.md) · [IT](README.it.md) · **日本語** · [FR](README.fr.md) · [中文](README.zh.md)
<!-- TRANSLATIONS:END -->

# CLAS12 GEMC Systems

[![Test][badge-test]][workflow-test]
[![ASCII Geometry Comparison][badge-ascii-geometry]][workflow-ascii-geometry]
[![Deploy][badge-deploy]][workflow-deploy]
[![Sanitize][badge-sanitize]][workflow-sanitize]
[![CodeQL Advanced][badge-codeql]][workflow-codeql]
[![Doxygen][badge-doxygen]][workflow-doxygen]
[![Binary Tarballs][badge-binary-tarballs]][workflow-binary-tarballs]
[![Nightly Dev Release][badge-dev-release]][workflow-dev-release]
[![HIPO Histos Comparison][badge-hipo-histos]][workflow-hipo-histos]
[![macOS Tarball][badge-macos-tarball]][workflow-macos-tarball]
[![Valgrind Profile][badge-valgrind-profile]][workflow-valgrind-profile]

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

CLAS12 GEMC Systems は、CLAS12 検出器のジオメトリシステムと各システム固有のプラグインの GEMC3 実装を
含みます。コアとなる GEMC アプリケーションおよび Python ジオメトリ API を CLAS12 向けに補完する
リポジトリです。

- [`gemc/src`](https://github.com/gemc/src) は、GEMC C++ アプリケーション、Geant4 統合、
  SQLite/ASCII/CAD/GDML ジオメトリローダー、動的プラグイン基盤、ストリーマ、および同梱の `pygemc`
  環境を提供します。
- [`gemc/pygemc`](https://github.com/gemc/pygemc) は、ジオメトリと材料の定義、GEMC データベースの書き出し、
  PyVista によるジオメトリのプレビュー、VTK.js シーンのエクスポートに使用する Python API を提供します。
- [`gemc/home`](https://github.com/gemc/home) は、公開 GEMC ウェブサイト、インストールページ、
  チュートリアル、例、および生成されたドキュメント用アセットを含みます。

<br/>

## 現在の対応範囲

本リポジトリでは、[`gemc/clas12Tags`](https://github.com/gemc/clas12Tags) からの移行を進めています。

| システム | 状態 | 備考 |
|---------|---------------------------|-----------------------------------------------------|
| `beamline` | パッシブジオメトリ | 次期リリースで提供予定: ネイティブジオメトリと CAD メッシュ |
| `dc` | ジオメトリとプラグイン | ジオメトリのソースとして coatjava を使用 |
| `ec` | ジオメトリとプラグイン | coatjava と共有の `ecal` プラグインを使用 |
| `field` | プラグイン | cMag ライブラリによる CLAS12 の磁場マップ |
| `ft` | ジオメトリと複数のプラグイン | 次期リリースで提供予定: FTCAL、FTHODO、FTTRK |
| `ftof` | ジオメトリとプラグイン | ジオメトリのソースとして coatjava を使用 |
| `ltcc` | ジオメトリとプラグイン | 光学表面を備えたネイティブおよび CAD ジオメトリ |
| `pcal` | ジオメトリと共有プラグイン | coatjava と共有の `ecal` プラグインを使用 |


<br/>

## GEMC

コアとなる GEMC リポジトリ [`gemc/src`](https://github.com/gemc/src) が実行時の動作を担当します。
これには以下が含まれます。

- Geant4 のソリッド、論理ボリューム、物理配置の構築
- 動的 C++ プラグイン
- イベント生成、感応検出器、出力ストリーマ

本リポジトリは、その実行環境に渡す CLAS12 固有の入力を担当します。

- 検出器ジオメトリ、材料定義
- CLAS12 ジオメトリの再現に必要なランとバリエーションのマッピング
- GEMC2 の CLAS12 参照ジオメトリおよび出力との比較検証

[`gemc/pygemc`](https://github.com/gemc/pygemc) リポジトリが Python API を定義します。

> **ゼロからビルド — GEMC の事前インストールは不要。** 次期リリースから、CLAS12 システムは、
> **GEMC が存在しない**最小限の Geant4 環境（例えば `ghcr.io/gemc/g4install` イメージ）上で
> ビルド・インストールできます。インストール済みの GEMC が見つからない場合、ビルド処理が `gemc`
> サブプロジェクトから自動的に GEMC をコンパイルし、同じプレフィックスにインストールします。
> GEMC は、明示的な `-Duse-gemc-location=<dir>`、インストール済みの GEMC（pkg-config または
> `PATH` 上の `gemc` バイナリ）、ソースからビルドするサブプロジェクトの順に解決されます。
> **Geant4 がビルドされることはありません**。事前に利用可能である必要があり、なければ構成に失敗します。
> すべてのコンテナ CI ワークフローは、サポート対象の各ディストリビューションの g4install イメージ上で
> この方式を使用します。

<br/>

## ジオメトリのワークフロー

各検出器システムは `geometry_src/<system>` 配下に自己完結しています。

次期リリースで提供予定: beamline のインポートでは、ネイティブの GEMC2 ジオメトリを保持し、
横方向磁石の 3 つの代替形状を含む 49 個の STL ファイルを提供します。21 個の beamline アセットでは
三角形数を削減し、ハブとアダプタの名前を `Apex_Shield_Hub` および `Beamline_Adapter_1` に変更しています。
残り 28 個のメッシュは元のバイト列をそのまま保持します。これには、もともと粗いメッシュの出口シールドの
鉛充填部も含まれ、ケーシングとの狭いクリアランスが保持されます。3 つの FT アジャスターメッシュは、
参照形状の和集合と体積を一致させた、簡略化された 1 つの `ft_adjuster` に置き換えられます。
9 本の内側シールドボルトには `FTInnerShieldAndFlange_Bolt1` から `Bolt9` までの名前を使用します。
滑らかな軸と簡略化した頭部により、それぞれの銅の体積を一致させ、シールドとのクリアランスを確保しています。
内側シールドとフランジのアセンブリは `FTInnerShieldAndFlange` に改名し、内部のポケットを保持しています。
外側フランジは `FTOuterFlange` に改名し、12 個のボルト穴を埋めて簡略化しています。
外側マウントは `FTOuterMount` に改名し、修復したうえで、外側フランジとの干渉を避ける逃げを設けています。
下流側の FT 内側シールドは `FTInnerShield` に改名し、ボルト穴を塞ぎ、両方のフランジ面を滑らかにしつつ、
縦方向の溝を保持しています。
Moller コーンは `moller_cone` に改名し、表面の穴を埋め、下流側の FT 内側シールドとの干渉を避けるように
開口部を広げています。感応検出器用のデジタイゼーションプラグインはありません。
バリエーション、ステアリングカード、メッシュ品質チェック、一次粒子の条件を揃えたベンチマーク、
および未加工メッシュについて残っている警告は、[beamline の説明](geometry_src/beamline/README.md)
を参照してください。

一般的なシステムディレクトリには以下が含まれます。

| ファイル | 役割 |
|----------------------------------------------|--------------------------------------------------------------------------------------|
| `<system>.py` | 実行可能なメインスクリプト。`autogeometry()` を生成し、材料とボリュームを公開する |
| `geometry.py` | ジオメトリ構築コード |
| `materials.py` | システムの材料定義 |
| `variations.py` | ランとバリエーションのマッピング（任意） |
| `<system>.yaml` | ローカルで手軽に実行するための GEMC ステアリングカード |
| `../coatjava_factories/CoatjavaFactory.java` | Java ジオメトリサービスを使う場合の coatjava ブリッジ（任意） |
| `plugin/meson.build` | デジタイゼーションやその他の実行時拡張のための C++ プラグイン登録（任意） |

メインスクリプトには実行権限を付与し、そのディレクトリから直接実行できるようにしてください。

```shell
cd geometry_src/dc
./dc.py 
```

システムを目視確認できる段階になったら、`pygemc` の PyVista オプションを使用してください。

```shell
./dc.py -pvb
```

ローカルのステアリングカードで GEMC を実行します。

```shell
gemc dc.yaml
gemc dc.yaml -gui
```

感応ボリュームのジオメトリ行は、そのボリュームの `digitization` フィールドで実行時のプラグインを選択します。
YAML の `gsystem` エントリに指定できる `digitization` キーの用途は、これより限定的です。
`ec` と `pcal` システムが `ecal.gplugin` を共有する場合のように、オプションの解析前に、
名前の異なるどのプラグインを GEMC が調べるべきかを指定します。FT には 3 つの感応ボリューム用の名前
（`ft_cal`、`ft_hodo`、`ft_trk`）があるため、YAML では単純な `name: ft` エントリを使用します。
オプション専用の `ft.gplugin` が初期化時の調査で 3 つのドメインすべてを登録し、その後のジオメトリ読み込みで
感応ボリュームの行から 3 つのデジタイザを検出して読み込みます。

<br/>

## 参照データとの比較

生成された GEMC3 ASCII データベース（ジオメトリと材料）を、対応する
[`gemc/clas12Tags`](https://github.com/gemc/clas12Tags) の参照ファイルと比較するには、
`scripts/compare_ascii_databases.py` を使用します。

```shell
scripts/compare_ascii_databases.py dc
```

システム引数を指定しない場合、スクリプトはローカルのすべての `geometry_src/<system>/<system>.py` 実装を
チェックします。GEMC2 と GEMC3 の ASCII 列を、名前、母ボリューム、位置、回転、ソリッド、
寸法、材料、デジタイゼーション（GEMC2 の `sensitivity`）、識別子（GEMC2 の `identifiers` を
標準化された `name=value` 形式に展開）という共通のジオメトリフィールドにマッピングし、
ボリューム名をキーに、それらのフィールド値だけを比較します。そのため、書式や列順の違いによって、
実際には一致するジオメトリが不一致と判定されることはありません。独自の材料を定義するシステムでは、
材料についても、材料名をキーに同じ方法で比較します（密度、構成成分、光学特性およびシンチレーション特性）。
数値の表記と GEMC2/GEMC3 のポリコーン配列の順序は、比較前に正規化されます。

いずれかのフィールドが異なる場合、スクリプトはフィールド単位の不一致を出力し、ステータス `1` で終了します。
すべて一致した場合はステータス `0` で終了します。

<br/>

## 配置と回転

GEMC3 は `GVolume.g4placement_type` を通じて、Geant4 の 2 つの配置規約をサポートします。

| 値 | 意味 |
|-----------|----------------------------------------------------------------------------------------|
| `active` | GEMC3 のデフォルトの動作。`G4Transform3D(rotation, translation)` を使用 |
| `passive` | GEMC2/clas12Tags と互換性のある動作。`G4PVPlacement(rotation, translation, ...)` を使用 |

GEMC2 から移植した CLAS12 検出器ボリュームでは、パッシブ配置規約を使用してください。

```python
gvolume.g4placement_type = "passive"
```

順序付き回転は、データベース内でも順序付きのまま保持してください。例えば、次の表現をフラット化しないでください。

```text
ordered: yxz, 0*deg, 0*deg, 6*deg
```

GEMC は順序付き回転を指定された順序で適用します。これは DC では必須であり、`clas12Tags` から移植する
他の CLAS12 システムでも重要になると考えられます。

<br/>

## Coatjava

一部の CLAS12 システムは coatjava を使用し、シミュレーションのジオメトリが、再構成で使用するものと同じ
Java ジオメトリサービスに従うようにしています。本リポジトリでは coatjava を `geometry_src` 配下に
ローカルに配置します。

```shell
./geometry_src/install_coatjava.sh -l
```

`geometry_src/coatjava` が存在しない場合、Meson の構成処理が coatjava を自動的にインストールします。
CI および Docker イメージでは、先に以下の前提ソフトウェアを用意する必要があります。

- Java
- Maven
- git-lfs
- jq

ヘルパースクリプトは以下のとおりです。

| パス | 用途 |
|------------------------------------|-------------------------------------------------------------------|
| `geometry_src/install_coatjava.sh` | ローカルの coatjava コピーをインストールする |
| `ci/install_coatjava_deps.sh` | サポート対象の CI イメージに Java、Maven、git-lfs、jq をインストールする |
| `ci/setup_coatjava.sh` | 前提ソフトウェアをインストールし、必要に応じて coatjava をインストールする CI ヘルパー |

リセットフラグが明示的に指定されない限り、既存の coatjava インストールを削除しないでください。

<br/>

## ビルドとテスト

本リポジトリは Meson でビルドし、`meson/` 配下で構成された GEMC および Geant4 の依存関係を使用します。

事前に必要なのは **Geant4** のみです（モジュールをロードするか、`geant4-config` を `PATH` に通してください）。
GEMC の事前インストールは**不要**です。見つからない場合は `gemc` サブプロジェクトからコンパイルされ、
同じ `--prefix` にインストールされます。これにより、最小限の Geant4 環境に CLAS12 システムを
ゼロからインストールできます（[GEMC](#gemc) セクションの囲み記事を参照）。

構成、ビルド、テストを実行します。

```shell
meson setup build --prefix="$PWD/install"
meson compile -C build
meson install -C build
meson test -C build --suite clas12 --print-errorlogs
```

**CLAS12 テストと GEMC コアテスト。** 本リポジトリ独自のテストはすべて `clas12` スイートに属します
（ジオメトリ生成、GEMC での検出器構築、CCDB 接続性、SRO チェック）。そのため、上記のコマンドと
CI（`ci/build.sh`）は `--suite clas12` を実行します。GEMC の**コア**テストは `gemc/src` に属し、
本リポジトリには含まれません。GEMC をここで `gemc` サブプロジェクトとしてコンパイルする場合、
GEMC 独自のテストは**一切**登録されません。これらのテストは、未インストールのビルドツリー内の GEMC を
検証するものであり、`gemc/src` 自身の CI が担当します。したがって、ここで単に `meson test -C build` を
実行すると、`clas12` スイートだけが実行されます。GEMC コアスイートを実行する正式な場所は、
[`gemc/src`](https://github.com/gemc/src) リポジトリ自体です。
（`-Dinclude-subproject-tests=true` オプションが制御するのは、GEMC ではなく、
同梱される他のサブプロジェクトである CCDB、HIPO、clas12-cmag です。）

次期リリースで提供予定: 各検出器には、`clas12` および `gemc` スイートに属する
`gemc_<system>` スモークテストが用意されます。ジオメトリ生成後、独立した一時ディレクトリで、
インストール済みの GEMC を起動し、ネイティブおよび CAD ジオメトリを構築して、
イベント数ゼロ・磁場なしで検出器プラグインを読み込みます。
ジオメトリテストによって `build/clas12.db` にデータが書き込まれたら、
`meson test -C build --suite gemc --print-errorlogs` で構築だけを再実行できます。
GEMC をサブプロジェクトとしてビルドする場合は、実行ファイルに必要な実行時ディレクトリ構成を整えるため、
テスト前にインストールしてください。

GEMC をビルドする代わりに既存の GEMC インストールを再利用するには、`-Duse-gemc-location=<dir>` を渡します
（または、その `gemc` バイナリを `PATH` に通します）。

既存のライブラリインストールと磁場マップを再利用するには、以下の独立したオプションを使用します。
3 つのライブラリオプションと、構成時に設定する磁場プラグインのデフォルト値は、次期リリースで提供予定です。

| Meson オプション | 指定するパス |
| --- | --- |
| `-Duse-gemc-location=<dir>` | GEMC のインストールプレフィックス |
| `-Duse-ccdb-location=<dir>` | CCDB のインストールプレフィックス |
| `-Duse-hipo-location=<dir>` | HIPO のインストールプレフィックス |
| `-Duse-clas12-cmag-location=<dir>` | clas12-cmag のインストールプレフィックス |
| `-Duse-fields-location=<dir>` | CLAS12 磁場マップを含むディレクトリ |

例えば、4 つすべてを再利用するには、次のようにします。

```shell
meson setup build --prefix="$PWD/install" \
  -Duse-ccdb-location=/absolute/path/to/ccdb \
  -Duse-hipo-location=/absolute/path/to/hipo \
  -Duse-clas12-cmag-location=/absolute/path/to/clas12-cmag \
  -Duse-fields-location=/absolute/path/to/magfield
```

各オプションのデフォルトは空で、個別に設定できます。ライブラリオプションが空の場合は、
既存の依存関係設定を維持します。ライブラリパスには絶対パスを指定する必要があり、
指定すると対応するサブプロジェクトはスキップされます。指定したインストールが無効な場合は構成に失敗します。
ヘッダは `include/` 配下（古い clas12-cmag インストールでは `includes/` も可）、
ライブラリは `lib/` または `lib64/` 配下にある必要があります。Meson の `-Dprefer_static=true` は、
両方の種類がインストールされている場合に静的ライブラリを優先します。プラグインで使用する静的ライブラリは、
位置独立コードでビルドされている必要があります。インストール済みの CCDB には、
MySQL/MariaDB クライアント開発ツールと SQLite が必要です。インストール済みの HIPO には、
LZ4 と fmt の開発パッケージが必要です。外部のインストールは `meson install` ではコピーされません。

`-Duse-fields-location=<dir>` を指定すると、マップの取得もインストールも行われず、
磁場プラグインはデフォルトでそのディレクトリを使用します。磁場の `dir` パラメータを明示的に指定した場合は、
そちらが優先されます。オプションが空の場合、マップは `magfield` git-lfs サブプロジェクトから取得され、
`<prefix>/fields` 配下にインストールされます。プラグインは、自身のインストール場所からの相対位置で
そのディレクトリを特定します。マップの取得には git-lfs が必要です。

GEMC 自体も同様の方式で解決されます。`-Duse-gemc-location=<dir>` は、指定した絶対パスのプレフィックスに
インストールされた GEMC を使用します（`lib/pkgconfig/gemc.pc` が必要です）。オプションが空の場合、
pkg-config または `PATH` 上の `gemc` バイナリで見つかったインストール済みの GEMC を使用します。
見つからなければ、`gemc` サブプロジェクトをソースからビルドします。Geant4 がビルドされることはありません。
事前に利用可能である必要があり（構成前に Geant4 モジュールをロードしてください）、
見つからない場合は構成に失敗します。

次期リリースで提供予定: 同梱の CCDB は `ccdb_system_sqlite.patch` によりシステムの SQLite を使用し、
独自に同梱する SQLite の単一ソース版（amalgamation）を使用しなくなります。
パッチ未適用の既存の CCDB サブプロジェクトのチェックアウトは、再ビルド前に更新する必要があります。

```shell
meson subprojects purge --confirm ccdb
```

その後、空のビルドディレクトリで構成を実行し、Meson が CCDB を取得して wrap パッチを適用するようにします。

ジオメトリテストは、登録された各 Python システムを実行し、統合された SQLite データベースを書き出します。

```shell
meson test -C build geometry_dc --print-errorlogs
sqlite3 build/clas12.db "select system, variation, run, count(*) from geometry group by 1,2,3;"
```

CLAS12 システムレジストリは、現在 `meson.build` にあります。

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

`geometry_src/<system>/<system>.py` が有効な GEMC ジオメトリを生成できるようになってから、
このリストに検出器名を追加してください。

<br/>

## CCDB 較正定数

検出器のデジタイゼーションプラグイン（`dc`、`ecal`、`ft_cal`、`ft_hodo`、`ftof`、`ltcc`）は、
較正定数を CCDB から読み込みます。デフォルトでは JLab のデータベース
`mysql://clas12reader@clasdb.jlab.org/clas12` に接続します。
別のサーバーやローカルの SQLite スナップショット（`sqlite:///path/to/ccdb.sqlite`）を使用するには、
`CCDB_CONNECTION` 環境変数を設定してください。これは CCDB データベースであり、
GEMC2 の `clas12.sqlite` 検出器データベースではない点に注意してください。後者を指定すると定数が空になります。
CCDB に関する障害（ホストに到達できない、データベースが間違っている、テーブルが空など）が発生した場合、
プラグインは黙って空のデジタイゼーション出力を生成する代わりに、明確なエラーを出して実行を中止するようになりました。

### MariaDB と MySQL のコネクタの比較（macOS）

macOS では CCDB クライアントライブラリに注意が必要です。`clas12reader` アカウントは
`mysql_native_password` で認証します。この方式は SHA1 ベースで、セキュリティ上の理由から非推奨となり、
Oracle が MySQL クライアントライブラリのバージョン 9.0 で**削除**しました。
したがって、MySQL 9.x にリンクした CCDB は clasdb で認証できず、接続時に失敗します。
これは CCDB のバグではなくクライアントライブラリの制限です。ライブラリのコンパイル時に除外された機能を、
CCDB のソース変更で復元することはできません。この機能を引き続き提供するコネクタをインストールしてください。

```shell
brew install mariadb-connector-c   # preferred: maintained; supports native_password and caching_sha2_password
# or
brew install mysql-client@8.4      # Oracle LTS that still ships native_password
```

Meson ビルドは CCDB コネクタを自動的に選択します（`meson/meson.build`）。
優先順位は `mariadb-connector-c`、`mysql-client@8.4`、`mysql-client`、`mysql` の順です。
そのため、クリーンビルドでは手動で再リンクすることなく、動作するクライアントにリンクされます。
MySQL 9.x だけがインストールされている場合でも CCDB はビルドできますが、互換性のあるコネクタを
インストールするか、サーバーのアカウントを `caching_sha2_password` に移行するまで、
clasdb への接続は明確なエラーを出して失敗します。

これとは別に、MariaDB 固有の注意点があります。`mariadb-connector-c` は**デフォルトで TLS を必須とします**が、
clasdb は SSL なしで動作するため、変更を加えていない MariaDB を使ったビルドでは、
`Error 2026 (SSL is required, but the
server does not support it)` で接続に失敗します。`ccdb` サブプロジェクトには、
MariaDB にリンクしてビルドした場合に TLS の強制を無効にするパッチが適用されています
（`subprojects/ccdb.wrap` の `diff_files` → `subprojects/packagefiles/ccdb_ssl_no_enforce.patch`）。
これにより、Oracle libmysqlclient の、平文接続へのフォールバックを許可するデフォルト動作に合わせています。
パッチは `#ifdef LIBMARIADB` で保護されているため、MySQL/Oracle クライアントでは何も変更しません
（これらのクライアントでは該当オプションが削除されており、そもそも TLS は強制されません）。
この対応により、`mariadb-connector-c` は clasdb に接続でき、推奨コネクタとなっています。

<br/>

## プラグインパス

CLAS12 システムプラグインは、`<prefix>/lib/` 配下に `.gplugin` 共有ライブラリとしてインストールされます。
GEMC は、`GEMC_PLUGIN_PATH`、自身の `lib/` および `build/` ディレクトリ、
OS の動的ライブラリ検索パス（Linux では `LD_LIBRARY_PATH`、macOS では `DYLD_LIBRARY_PATH`）
の順に検索してプラグインを見つけます。

最も簡単な構成は、CLAS12 システムを GEMC 自体と同じプレフィックスにインストールすることです。
これにより、`.gplugin` ライブラリは GEMC がすでに検索する `lib/` ディレクトリに配置され、
実行時の環境変数は不要になります。GEMC のプレフィックスは `bin/` ディレクトリの 1 つ上の階層なので、
`command -v gemc` から求められます。

```shell
meson setup build --prefix="$(dirname "$(dirname "$(command -v gemc)")")"
meson install -C build
gemc dc.yaml
```

GEMC が `PATH` 上にあるものの、異なるプレフィックスが設定されている場合、Meson は構成時に警告を出力します。
その場合は、`gemc` を実行する前に `GEMC_PLUGIN_PATH` を CLAS12 システムのライブラリディレクトリに設定します。

```shell
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
gemc dc.yaml
```

または、コマンドラインで指定します。

```shell
gemc dc.yaml -plugin_path=/path/to/clas12-systems/lib
```

プラグインが見つからない場合、GEMC はパスの問題を診断しやすいように、
エラーとともに `GEMC_PLUGIN_PATH` の現在の値を出力します。

Meson ビルドのインストール先プレフィックスでは、pkg-config ファイルを通じてプラグインディレクトリを取得できます。

```shell
# After: meson install -C build --prefix=/my/clas12/prefix
export PKG_CONFIG_PATH=/my/clas12/prefix/lib/pkgconfig:$PKG_CONFIG_PATH
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
```

<br/>


## プラグインのビルドモデル

システムプラグインはレジストリパターンを使用します。

1. 検出器固有の `geometry_src/<system>/plugin/meson.build` が `clas12_plugins` に辞書を追加します。
2. トップレベルの `meson.build` だけが、これらのエントリからインストール対象の共有ライブラリを生成します。
3. インストールする GEMC プラグインには `.gplugin` サフィックスを使用する必要があります。

これにより、CLAS12 システム全体でプラグインのインストールを統一し、
各検出器が独自のビルドロジックを用意することを避けられます。

### ロギングテンプレート

次期リリースで提供予定: プラグインのロギングでは、メッセージ全体を渡す `GLogger` API を使用します。
英文を分割せず、値は番号付きプレースホルダを通じて渡してください。

```cpp
log->info(1, "Loaded %1 constants for run %2.", count, runno);
```

`debug`、`warning`、`error`、`critical` も同じプレースホルダ規則を使用します。
対応する GEMC ヘッダでプラグインを再ビルドしてください。従来の文字列を連結する呼び出しは移行が必要です。
動的な診断テキストは `log->warning("%1", text)` で値として渡せます。
これにより、そのテキスト内のパーセント記号はそのまま保持されます。

生成される英語カタログは `translations/en.yaml` にあり、`translations/catalog.yaml` が、
メッセージの定義元となるプラグインソースを選択します。隣接する GEMC ソースツリーの共有抽出ツールを使用して、
再生成またはチェックを行います。

```shell
../src/build/subprojects/pygemc/python_env/bin/python ../src/ci/extract_messages.py extract --root .
../src/build/subprojects/pygemc/python_env/bin/python ../src/ci/extract_messages.py extract --root . --check
../src/build/subprojects/pygemc/python_env/bin/python ../src/ci/extract_messages.py validate-tree --root .
```

英語メッセージは、生成されたカタログではなく C++ 内で編集してください。翻訳の検証については
[カタログガイド](https://github.com/gemc/src/blob/main/translations/README.md) を参照してください。
実行時のロギングでは言語が自動的に選択されます。`-language=it` はイタリア語を選択し、
`-language=en` は英語を強制します。翻訳のないメッセージは英語のまま表示されます。
Meson はプラグインカタログを `<prefix>/share/gemc/translations/clas12` 配下にインストールします。
既存のプラグイン検索パスを通じて、他のインストールプレフィックスにあるカタログも見つけられます。
対応する GEMC ヘッダと新しい `glogging` ライブラリでプラグインを再ビルドしてください。
共有の Claude/Codex ワークフローは、既存の平日 cron ジョブを通じて言語カタログを生成します。
その `gemc/clas12-messages` エントリでは、検証付きの再開可能なバッチ処理を使用し、
ソースの git コミットを追跡します。Test ワークフローも、エージェントを使わずに生成済みの全カタログを検証し、
必要な言語ファイル、キー、プレースホルダ、パーセント記号のエスケープ、空白をチェックします。
翻訳のないメッセージについては、英語へのフォールバックを示すカバレッジが報告されます。
翻訳の正確さは、引き続きエージェントによるレビューで確認します。

<br/>

## 磁場

CLAS12 は、解析モデルではなく、測定されたソレノイドおよびトロイダル磁場の
**マップに基づく**磁場を使用します。磁場は `plugins/field/` 配下の `gfieldclas12-cmag`
プラグインが提供します。このプラグインは、David Heddle の
[cMag](https://github.com/JeffersonLab/clas12-cmag) ライブラリ（`clas12-cmag` サブプロジェクト）を
通じて CLAS12 のソレノイドおよびトロイダル磁場のバイナリマップを読み込み、
各ステップ点での合成磁場を返します。

磁場は GEMC コアの汎用 `gfields` ノードで設定し、`type: clas12-cmag` でこのプラグインを選択します。

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

`global_field` の値は、ソレノイドやトロイダル磁場のマップ名ではなく、設定した磁場の名前
（上記では `clas12`）です。マップ名とマップごとのスケール係数は `gfields` エントリに指定します。
これにより、GEMC2 の `global_field: Symm_solenoid_...:Symm_torus_...` 形式と、
従来ハードコードされていたスケール指定先の `binary_torus` / `binary_solenoid` は、
明示的な `torus`、`solenoid`、`torus_scale`、`solenoid_scale` パラメータに置き換えられます。

追加のスカラーキー（マップごとの変位、全体の原点・回転、`interpolation`）は、
そのままプラグインに渡されます。

磁場マップは `magfield` git-lfs サブプロジェクトから取得し、`meson
install` 時に `<prefix>/fields` へコピーします（`meson/install_fields.py` を参照）。
プラグインは、自身の隣にインストールされた `fields` ディレクトリ（`<plugin_dir>/../fields`）から
マップを読み込みます。`-Duse-fields-location=<dir>` を指定して構成すると、サブプロジェクトをスキップし、
代わりに既存のマップディレクトリを使用します（クローンもインストールも行いません）。
実行時に `FIELD` や `FIELD_DIR` 環境変数は不要です。明示的な `dir` パラメータで場所を上書きできます。

<br/>

## ストリーミングリードアウト（SRO）

**次期リリースで提供予定。** CLAS12 システムは、通常のイベント出力の代わりに、またはそれと並行して、
JLAB DAQ バイナリ形式のストリーミングリードアウト（SRO）フレームを出力できます。
GEMC が汎用 `sro` ストリーマを提供し、システムプラグインはデジタイザとともに
`GSROImplementationFactory` をエクスポートしてペイロードを供給します。
現在、SRO ペイロードを供給するのは **FT-Cal** だけです（`ft_cal.gplugin` 経由）。
他の FT デジタイザは SRO モデルを持たず、通常の出力を維持します。

コマンドラインから SRO を有効にするには、`sro` ストリーマ形式とペイロードを提供するプラグインを選択し、
データ収集のイベント時間幅をゼロ以外に設定します。

```shell
gemc geometry_src/ft/ft.yaml -n=10000 \
  -gstreamer='[{format: sro, filename: ftcal_sro, implementation: ft_cal}]' \
  -eventTimeWidth='10*ns'
```

- `format: sro` は GEMC の SRO ストリーマを選択します。`implementation: ft_cal` はペイロードを生成する
  プラグイン名を指定し、`filename` は出力のベース名を指定します。
- `-eventTimeWidth` は、データ収集の時間軸上で連続するイベント間の間隔を設定します。
  デフォルト値のゼロでは SRO 実行が拒否されるため、明示的な設定が必要です
  （上記の `10*ns` は例であり、測定された CLAS12 ビームパラメータではありません）。
  通常の出力を行う実行では設定不要です。
- 出力ファイルは、クレートごとに `<basename>_r<resolved_run>_crate<crate>.ev` として書き込まれます。
  同じベース名とランを再利用すると上書きされます。

FT の初期登録用プラグイン `ft.gplugin` が `ft_cal.gplugin` のオプションを提供するため、
追加のオプションノードは不要です。変換テーブルの規約、ワーカーのタイミングモデル
（`ft_cal_sro_min_signal_time` を含む）、バイナリレイアウト、および `sro` テストスイートについては、
[`geometry_src/sro/README.md`](geometry_src/sro/README.md) を参照してください。
移植された DAQ 定義とその由来は、
[`geometry_src/sro/daq/README.md`](geometry_src/sro/daq/README.md) にあります。

<br/>

## 検証

移植した各検出器について、生成されたデータベースの行と、実行時のジオメトリの動作の両方を検証してください。

推奨する確認事項:

- 生成されたジオメトリ行を、[`gemc/clas12Tags`](https://github.com/gemc/clas12Tags) の
  `geometry_source/<system>` 配下にある GEMC2 の参照データと比較する。
- 共通のフィールドについて、名前、母ボリューム、説明、位置、回転、ソリッド、パラメータ、材料が
  一致することを確認する。
- ランとバリエーションのマッピングが、システムディレクトリ内で完結していることを確認する。
- Geant4 で本格的に実行する前に、PyVista のエクスポートを使って配置を手早く確認する。
- 検出器に確認可能な量のジオメトリが揃ったら、GEMC をバッチモードと GUI モードで実行する。

DC では、生成されたデフォルトジオメトリが、次の参照データとトークン単位で一致する必要があります。

```text
https://github.com/gemc/clas12Tags/blob/main/geometry_source/dc/dc__geometry_default.txt
```

DC で想定される既知の仕様:

- デフォルトのランは `11`
- すべての DC ボリュームは `g4placement_type = "passive"` を使用する
- 順序付き回転は `ordered: ...` として保持される
- 廃止された `original` バリエーションはサポートされない

<br/>

## CI とリリース

次期リリースで提供予定: すべてのコンテナワークフローは、
[`gemc/g4install`](https://github.com/gemc/g4install) が公開する Geant4 ベースイメージ上で、
GEMC と CLAS12 システムをソースからビルドします。
[ワークフローガイド](.github/workflows/README.md) では、トリガー、デプロイの認可、
リポジトリ間の取り決め、権限、再試行、および想定どおりに実行がスキップされる場合を説明しています。

関連する自動化:

| ワークフロー | 用途 |
|-----------------------|-------------------------------------------------------------------------------------|
| `deploy.yml` | Geant4 ベースイメージ内で GEMC と CLAS12 システムをビルドし、イメージを公開する |
| `pr-docker-image.yml` | PR ごとのプレビューイメージをビルドし、レビュアーがローカルビルドなしでブランチをテストできるようにする |
| `sanitize.yml` | サードパーティのサブプロジェクトにはサニタイザを適用せず、CLAS12 システムのサニタイザビルドを実行する |
| `codeql.yml` | 静的解析 |
| `doxygen.yml` | ドキュメント生成 |
| `binary_tarballs.yml` | デプロイ後に GEMC を再ビルドし、スモークテストを実行する |
| `dev_release.yml` | 開発リリースの自動化 |

デプロイイメージには次のパターンを使用します。

```text
ghcr.io/gemc/clas12-systems:<gemc-tag>-<os>-<version>[-<arch>]
```

ベースイメージの取得元:

```text
ghcr.io/gemc/g4install
```

各プルリクエストではさらに、ブランチからビルドした、そのまま実行可能なマルチアーキテクチャ対応の
プレビューイメージ（`ghcr.io/gemc/clas12-systems:<gemc-tag>-almalinux-<version>-pr-<number>`）を公開します。
これにより、作成者とレビュアーはローカルビルドなしでテストできます。貢献ガイドの
[プレビューコンテナイメージ](CONTRIBUTING.md#preview-container-image) を参照してください。
このイメージは、プルリクエストがクローズされると自動的に削除されます。

<br/>


## ドキュメント

- [CI ワークフローガイド](.github/workflows/README.md)
- [GEMC ホームページ](https://gemc.github.io/home/)
- [Python API リポジトリ](https://github.com/gemc/pygemc)
- [GEMC2 / CLAS12 リポジトリ](https://github.com/gemc/clas12Tags)

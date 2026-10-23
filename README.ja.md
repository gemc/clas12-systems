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

CLAS12 GEMC Systems は、CLAS12 検出器ジオメトリシステムの GEMC3 実装と、各システム固有のプラグインを
収録しています。コアとなる GEMC アプリケーションおよび Python ジオメトリ API を補完する、
CLAS12 向けのリポジトリです。

- [`gemc/src`](https://github.com/gemc/src) は、GEMC C++ アプリケーション、Geant4 連携、
  SQLite/ASCII/CAD/GDML ジオメトリローダー、動的プラグイン基盤、ストリーマー、同梱の `pygemc`
  環境を提供します。
- [`gemc/pygemc`](https://github.com/gemc/pygemc) は、ジオメトリとマテリアルの定義、
  GEMC データベースの書き出し、PyVista によるジオメトリのプレビュー、
  VTK.js シーンのエクスポートに用いる Python API を提供します。
- [`gemc/home`](https://github.com/gemc/home) は、公開 GEMC ウェブサイト、インストールページ、
  チュートリアル、サンプル、生成されたドキュメントアセットを収録しています。

<br/>

## 現在の対象範囲

このリポジトリでは、[`gemc/clas12Tags`](https://github.com/gemc/clas12Tags) からの移行作業が進行中です。

| システム | 状態 | 備考 |
|---------|---------------------------|-----------------------------------------------------|
| `beamline` | パッシブジオメトリ | 次リリース予定: ネイティブおよび CAD メッシュ |
| `dc` | ジオメトリとプラグイン | ジオメトリソースとして coatjava を使用 |
| `ec` | ジオメトリとプラグイン | coatjava と共有の `ecal` プラグインを使用 |
| `field` | プラグイン | cMag ライブラリによる CLAS12 の磁場マップ |
| `ft` | ジオメトリとプラグイン | 次リリース予定: FTCAL、FTHODO、FTTRK |
| `ftof` | ジオメトリとプラグイン | ジオメトリソースとして coatjava を使用 |
| `ltcc` | ジオメトリとプラグイン | 光学サーフェス付きのネイティブおよび CAD ジオメトリ |
| `magnets` | パッシブジオメトリ | 次リリース予定: ソレノイドおよびすべての CAD ジオメトリ |
| `pcal` | ジオメトリと共有プラグイン | coatjava と共有の `ecal` プラグインを使用 |


<br/>

## GEMC

コアとなる GEMC リポジトリ [`gemc/src`](https://github.com/gemc/src) が実行時の動作を担当します。
これには以下が含まれます。

- Geant4 のソリッド、論理ボリューム、物理配置の構築
- 動的 C++ プラグイン
- イベント生成、有感検出器、出力ストリーマー

このリポジトリは、そのランタイムに渡す CLAS12 固有の入力を管理します。

- 検出器ジオメトリ、マテリアル定義
- CLAS12 ジオメトリを再現するために必要な run および variation のマッピング
- GEMC2 CLAS12 の参照ジオメトリおよび出力との比較検証

[`gemc/pygemc`](https://github.com/gemc/pygemc) リポジトリが Python API を定義します。

> **ゼロからのビルド — GEMC の事前インストールは不要。** 次リリースから、CLAS12 システムは
> **GEMC が存在しない** Geant4 のみの環境（例えば `ghcr.io/gemc/g4install` イメージ）上でビルドおよび
> インストールできます。インストール済みの GEMC が見つからない場合、ビルド時に `gemc`
> サブプロジェクトから GEMC を自動的にコンパイルし、同じインストールプレフィックスにインストールします。
> GEMC は、明示的な `-Duse-gemc-location=<dir>`、インストール済みの GEMC（pkg-config または
> `PATH` 上の `gemc` バイナリ）、最後にソースからビルドするサブプロジェクトの順に解決されます。
> **Geant4 はビルドされません**。あらかじめ利用可能でなければ、構成に失敗します。
> すべてのコンテナ CI ワークフローは、サポート対象の各ディストリビューションの g4install イメージ上で
> この方法を使用します。

<br/>

## ジオメトリワークフロー

各検出器システムは `geometry_src/<system>` 配下で自己完結しています。

次リリース予定: [magnets](geometry_src/magnets/README.md) は、ネイティブソレノイドと
39 個の CAD メッシュを、パッシブ配置と 3 つの GEMC2 run 構成とともに提供します。
領域 1 の DC の 6 枚の背面膜と 6 個の支持部材は、現在 [DC](geometry_src/dc/README.md) に属しており、
各グループは 1 つの STL と 5 つのパッシブコピーを使用します。重複する
`DSShield*` および `apex` シールドは beamline システムが提供します。
上流および下流のプレートと真空ジャケットは、締結具の穴を埋めた個別の最適化メッシュとして、
元の名前を維持します。

次リリース予定: beamline のインポートでは、元の GEMC2 ジオメトリを保持し、
3 種類の横磁石の選択肢を含む 49 個の STL ファイルを提供します。
21 個の beamline アセットでは三角形数を削減し、ハブとアダプターの名前を
`Apex_Shield_Hub` および `Beamline_Adapter_1` に変更しています。
残りの 28 個のメッシュは、元のバイト列をそのまま保持します。これには、もともと粗いメッシュである
出口シールドの鉛充填部も含まれ、筐体との狭いクリアランスも維持されます。
3 つの FT アジャスターメッシュは、参照形状の和集合と体積を一致させた、
1 つの簡略化メッシュ `ft_adjuster` に置き換えられます。
9 個の内側シールドボルトには `FTInnerShieldAndFlange_Bolt1` から `Bolt9` までの名前を使用します。
軸部を滑らかにし、頭部を簡略化しながら、銅部分の体積を一致させ、シールドとのクリアランスを確保します。
内側シールドとフランジのアセンブリは、内部のポケットを保持したまま `FTInnerShieldAndFlange` に改名されます。
外側フランジは `FTOuterFlange` に改名され、12 個のボルト穴を埋めて簡略化されます。
外側マウントは `FTOuterMount` に改名され、修復され、外側フランジとの干渉を避けるために逃がし加工されます。
下流の FT 内側シールドは `FTInnerShield` に改名され、ボルト穴を塞ぎ、
両方のフランジ面を滑らかにしつつ、長手方向の溝を保持します。
Moller コーンは `moller_cone` に改名され、表面の穴を埋め、
下流の FT 内側シールドとの干渉を避けるために開口部を拡大します。
有感検出器用のデジタイズプラグインはありません。
variation、ステアリングカード、メッシュ品質チェック、同一の一次粒子条件によるベンチマーク、
残存する未加工メッシュの警告については、[beamline の説明](geometry_src/beamline/README.md) を
参照してください。

典型的なシステムディレクトリには以下が含まれます。

| ファイル | 役割 |
|----------------------------------------------|--------------------------------------------------------------------------------------|
| `<system>.py` | 実行可能なメインスクリプト。`autogeometry()` を作成し、マテリアルとボリュームを公開 |
| `geometry.py` | ジオメトリ構築コード |
| `materials.py` | システムのマテリアル定義 |
| `variations.py` | 任意の run および variation マッピング |
| `<system>.yaml` | ローカルで手軽に実行するための GEMC ステアリングカード |
| `../coatjava_factories/CoatjavaFactory.java` | Java ジオメトリサービス利用時に使用する任意の coatjava ブリッジ |
| `plugin/meson.build` | デジタイズやその他の実行時拡張のための任意の C++ プラグイン登録 |

メインスクリプトには実行権限を付け、そのディレクトリから直接実行できるようにしてください。

```shell
cd geometry_src/dc
./dc.py 
```

システムの目視確認ができる段階になったら、`pygemc` の PyVista オプションを使用します。

```shell
./dc.py -pvb
```

ローカルのステアリングカードで GEMC を実行します。

```shell
gemc dc.yaml
gemc dc.yaml -gui
```

有感ボリュームのジオメトリ行では、ボリュームの `digitization` フィールドで実行時プラグインを選択します。
YAML の `gsystem` エントリに指定できる任意の `digitization` キーには、より限定された役割があります。
これは、`ec` と `pcal` のシステムが `ecal.gplugin` を共有する場合のように、
オプションを解析する前に、システム名とは異なる名前のどのプラグインを調べるかを GEMC に伝えます。
FT には 3 つの有感検出器名（`ft_cal`、`ft_hodo`、`ft_trk`）があるため、
その YAML では単純な `name: ft` エントリを使用します。
オプション専用の `ft.gplugin` は、初期化時のプローブで 3 つのドメインすべてを登録します。
その後、ジオメトリの読み込み時に有感ボリュームの行から 3 つのデジタイザーを検出し、読み込みます。

<br/>

## 参照データとの比較

生成された GEMC3 ASCII データベース（ジオメトリおよびマテリアル）を、対応する
[`gemc/clas12Tags`](https://github.com/gemc/clas12Tags) の参照ファイルと比較するには、
`scripts/compare_ascii_databases.py` を使用します。

```shell
scripts/compare_ascii_databases.py dc
```

システム引数を指定しない場合、スクリプトはローカルのすべての `geometry_src/<system>/<system>.py` 実装を
チェックします。スクリプトは GEMC2 および GEMC3 の ASCII 列を共通のジオメトリフィールド、
すなわち名前、親ボリューム、位置、回転、ソリッド、寸法、マテリアル、デジタイズ
（GEMC2 の `sensitivity`）、識別子（GEMC2 の `identifiers` を正規の `name=value` 形式に展開）に
マッピングし、それらのフィールド値のみをボリューム名ごとに比較します。
そのため、書式や列順の違いによって、実際には一致しているジオメトリを見落とすことはありません。
カスタムマテリアルを定義するシステムでは、マテリアルについても名前ごとに同じ方法で、
密度、成分、光学特性、シンチレーション特性を比較します。
数値の表記や GEMC2/GEMC3 のポリコーン配列の順序は、比較前に正規化されます。

いずれかのフィールドが異なる場合、スクリプトはフィールド単位の不一致を表示し、ステータス `1` で終了します。
すべて一致した場合はステータス `0` で終了します。

<br/>

## 配置と回転

GEMC3 は `GVolume.g4placement_type` を通じて、Geant4 の 2 つの配置規約をサポートします。

| 値 | 意味 |
|-----------|----------------------------------------------------------------------------------------|
| `active` | GEMC3 のデフォルト動作。`G4Transform3D(rotation, translation)` を使用 |
| `passive` | GEMC2/clas12Tags 互換の動作。`G4PVPlacement(rotation, translation, ...)` を使用 |

GEMC2 から移植した CLAS12 検出器ボリュームには、パッシブ配置規約を使用してください。

```python
gvolume.g4placement_type = "passive"
```

順序付き回転は、データベース内でも順序を保持してください。例えば、以下をフラット化してはいけません。

```text
ordered: yxz, 0*deg, 0*deg, 6*deg
```

GEMC は順序付き回転を指定された順序で適用します。これは DC では必須であり、
`clas12Tags` から移植される他の CLAS12 システムでも重要になると見込まれます。

<br/>

## Coatjava

一部の CLAS12 システムは coatjava を使用し、シミュレーションのジオメトリが、
再構成で使われるものと同じ Java ジオメトリサービスに従うようにしています。
このリポジトリでは、coatjava を `geometry_src` 配下にローカルに保持します。

```shell
./geometry_src/install_coatjava.sh -l
```

`geometry_src/coatjava` が存在しない場合、Meson の構成処理が coatjava を自動的にインストールします。
CI と Docker イメージでは、まず以下の前提ソフトウェアを用意する必要があります。

- Java
- Maven
- git-lfs
- jq

ヘルパースクリプトは以下のとおりです。

| パス | 目的 |
|------------------------------------|-------------------------------------------------------------------|
| `geometry_src/install_coatjava.sh` | ローカルの coatjava コピーをインストール |
| `ci/install_coatjava_deps.sh` | サポート対象の CI イメージに Java、Maven、git-lfs、jq をインストール |
| `ci/setup_coatjava.sh` | 前提ソフトウェアをインストールし、必要に応じて coatjava をインストールする CI ヘルパー |

リセットフラグが明示的に要求されない限り、既存の coatjava インストールを削除しないでください。

<br/>

## ビルドとテスト

このリポジトリは Meson でビルドされ、`meson/` 配下で構成された GEMC および Geant4 の依存関係を使用します。

事前に必要なのは **Geant4** だけです（モジュールをロードするか、`geant4-config` を `PATH` 上に置きます）。
GEMC を事前にインストールしておく**必要はありません**。見つからない場合は、
`gemc` サブプロジェクトからコンパイルされ、同じ `--prefix` にインストールされます。
これにより、Geant4 のみの環境に CLAS12 システムをゼロからインストールできます
（[GEMC](#gemc) セクションの注記を参照）。

構成、ビルド、テストを実行します。

```shell
meson setup build --prefix="$PWD/install"
meson compile -C build
meson install -C build
meson test -C build --suite clas12 --print-errorlogs
```

**CLAS12 テストと GEMC コアテストの違い。** このリポジトリ自身のテストはすべて `clas12` スイートに属し、
ジオメトリ生成、GEMC での検出器構築、CCDB 接続、SRO のチェックを行います。
そのため、上記のコマンドおよび CI（`ci/build.sh`）は `--suite clas12` を実行します。
GEMC の**コア**テストは `gemc/src` に属し、このリポジトリには含まれません。
GEMC をここで `gemc` サブプロジェクトとしてコンパイルする場合、GEMC 自身のテストは**一つも**
登録されません。それらは未インストールのビルドツリー内の GEMC を対象とし、
`gemc/src` 自身の CI が担当します。したがって、ここで単に `meson test -C build` を実行すると、
`clas12` スイートのみが実行されます。GEMC コアスイートの正式な実行場所は、
[`gemc/src`](https://github.com/gemc/src) リポジトリ自体です。
（`-Dinclude-subproject-tests=true` オプションが制御するのは、
GEMC 以外の同梱サブプロジェクト、CCDB、HIPO、clas12-cmag です。）

次リリース予定: 各検出器に、`clas12` および `gemc` スイートの `gemc_<system>` スモークテストを用意します。
ジオメトリ生成後、隔離された一時ディレクトリでインストール済みの GEMC を起動し、
イベント数ゼロ、磁場なしでネイティブおよび CAD ジオメトリを構築し、検出器プラグインを読み込みます。
ジオメトリテストによって `build/clas12.db` にデータが格納されたら、
`meson test -C build --suite gemc --print-errorlogs` で構築のみを再実行できます。
GEMC をサブプロジェクトとしてビルドする場合は、実行ファイルに必要な実行時ディレクトリ構成を整えるため、
テスト前にインストールしてください。

GEMC をビルドする代わりに既存のインストールを再利用するには、`-Duse-gemc-location=<dir>` を渡します
（または、その `gemc` バイナリを `PATH` 上に置きます）。

既存のライブラリインストールや磁場マップを再利用するには、以下の独立したオプションを使用します。
3 つのライブラリオプションと、磁場プラグインのデフォルトパス設定は次リリース予定です。

| Meson オプション | 指定するパス |
| --- | --- |
| `-Duse-gemc-location=<dir>` | GEMC のインストールプレフィックス |
| `-Duse-ccdb-location=<dir>` | CCDB のインストールプレフィックス |
| `-Duse-hipo-location=<dir>` | HIPO のインストールプレフィックス |
| `-Duse-clas12-cmag-location=<dir>` | clas12-cmag のインストールプレフィックス |
| `-Duse-fields-location=<dir>` | CLAS12 磁場マップを含むディレクトリ |

例えば、4 つすべてを再利用するには以下のようにします。

```shell
meson setup build --prefix="$PWD/install" \
  -Duse-ccdb-location=/absolute/path/to/ccdb \
  -Duse-hipo-location=/absolute/path/to/hipo \
  -Duse-clas12-cmag-location=/absolute/path/to/clas12-cmag \
  -Duse-fields-location=/absolute/path/to/magfield
```

各オプションのデフォルトは空で、個別に設定できます。ライブラリオプションが空の場合、
既存の依存関係設定を維持します。ライブラリパスを指定する場合は絶対パスが必要で、
対応するサブプロジェクトはスキップされます。インストールが無効な場合は構成に失敗します。
ヘッダーは `include/`（古い clas12-cmag インストールでは `includes/` も）配下、
ライブラリは `lib/` または `lib64/` 配下に配置されている必要があります。
Meson の `-Dprefer_static=true` は、両方の種類がインストールされている場合に静的ライブラリを優先します。
プラグインで使用する静的ライブラリは、位置独立コードでビルドされている必要があります。
インストール済みの CCDB には MySQL/MariaDB クライアント開発ツールと SQLite が必要です。
インストール済みの HIPO には LZ4 と fmt の開発パッケージが必要です。
外部インストールは `meson install` によってコピーされません。

`-Duse-fields-location=<dir>` を指定すると、マップの取得やインストールは行われず、
磁場プラグインはデフォルトでそのディレクトリを使用します。
磁場の `dir` パラメータを明示的に指定した場合は、そちらが優先されます。
オプションが空の場合、マップは `magfield` git-lfs サブプロジェクトから取得され、
`<prefix>/fields` 配下にインストールされます。
プラグインは、自身のインストール位置を基準にそのディレクトリを探します。マップの取得には git-lfs が必要です。

GEMC 自体も同様の方法で解決されます。`-Duse-gemc-location=<dir>` は、
指定された絶対パスのプレフィックスにインストールされた GEMC を使用します
（`lib/pkgconfig/gemc.pc` が必要です）。オプションが空の場合、pkg-config または
`PATH` 上の `gemc` バイナリを通じてインストール済みの GEMC が見つかれば、それを使用します。
見つからない場合は `gemc` サブプロジェクトをソースからビルドします。
Geant4 はビルドされません。あらかじめ利用可能である必要があり
（構成前に Geant4 モジュールをロードしてください）、見つからなければ構成に失敗します。

次リリース予定: 同梱の CCDB は `ccdb_system_sqlite.patch` によりシステムの SQLite を使用し、
独自に同梱する SQLite アマルガメーションを使用しなくなります。
既存の未パッチの CCDB サブプロジェクトのチェックアウトは、再ビルド前に更新する必要があります。

```shell
meson subprojects purge --confirm ccdb
```

その後、新しいビルドディレクトリで構成を行うと、Meson が CCDB を取得し、wrap パッチを適用します。

ジオメトリテストは、登録された各 Python システムを実行し、統合された SQLite データベースを書き出します。

```shell
meson test -C build geometry_dc --print-errorlogs
sqlite3 build/clas12.db "select system, variation, run, count(*) from geometry group by 1,2,3;"
```

CLAS12 システムレジストリは現在 `meson.build` にあります。

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

このリストに検出器名を追加するのは、`geometry_src/<system>/<system>.py` が有効な GEMC ジオメトリを
生成できるようになってからにしてください。

<br/>

## CCDB 較正定数

検出器のデジタイズプラグイン（`dc`、`ecal`、`ft_cal`、`ft_hodo`、`ftof`、`ltcc`）は、
較正定数を CCDB から読み込みます。デフォルトでは、JLab データベース
`mysql://clas12reader@clasdb.jlab.org/clas12` に接続します。
別のサーバーやローカルの SQLite スナップショット（`sqlite:///path/to/ccdb.sqlite`）を使用するには、
`CCDB_CONNECTION` 環境変数を設定します。これは CCDB データベースであり、
GEMC2 の `clas12.sqlite` 検出器データベースではないことに注意してください。
後者を指定すると、定数が取得できません。CCDB で何らかの失敗
（ホストに到達できない、データベースが異なる、テーブルが空など）が起きた場合、
プラグインは黙って空のデジタイズ出力を生成する代わりに、明確なエラーを表示して実行を中止するようになりました。

### MariaDB と MySQL のコネクタ比較（macOS）

macOS では、CCDB クライアントライブラリに注意が必要です。
`clas12reader` アカウントは `mysql_native_password` で認証しますが、
Oracle はバージョン 9.0 でこの方式を MySQL クライアントライブラリから**削除**しました
（SHA1 ベースの方式で、セキュリティ上の理由から非推奨とされていました）。
そのため、MySQL 9.x にリンクされた CCDB は clasdb で認証できず、接続時に失敗します。
これは CCDB のバグではなくクライアントライブラリの制限であり、
ライブラリのビルド時に除外された機能を CCDB のソース変更で復元することはできません。
この認証方式を引き続き提供するコネクタをインストールしてください。

```shell
brew install mariadb-connector-c   # preferred: maintained; supports native_password and caching_sha2_password
# or
brew install mysql-client@8.4      # Oracle LTS that still ships native_password
```

Meson ビルドは CCDB コネクタを自動的に選択します（`meson/meson.build`）。
優先順位は `mariadb-connector-c`、`mysql-client@8.4`、`mysql-client`、`mysql` の順です。
そのため、クリーンビルドでは手動で再リンクしなくても、動作するクライアントがリンクされます。
MySQL 9.x しかインストールされていない場合でも CCDB はビルドされますが、
互換コネクタがインストールされるか、サーバーアカウントが `caching_sha2_password` に移行するまで、
clasdb への接続は明確なエラーで失敗します。

MariaDB には、これとは別の注意点があります。`mariadb-connector-c` は**デフォルトで TLS を必須**としますが、
clasdb は SSL なしで動作するため、未変更の MariaDB を使ったビルドでは
`Error 2026 (SSL is required, but the
server does not support it)` で接続に失敗します。`ccdb` サブプロジェクトには、
MariaDB にリンクしてビルドする場合に TLS の必須化を無効にするパッチが適用されています
（`subprojects/ccdb.wrap` の `diff_files` → `subprojects/packagefiles/ccdb_ssl_no_enforce.patch`）。
これにより、Oracle libmysqlclient のデフォルトである平文接続へのフォールバックに動作を合わせています。
パッチは `#ifdef LIBMARIADB` でガードされているため、
MySQL/Oracle クライアントには影響しません
（それらではこのオプションが削除されており、そもそも TLS は必須ではありません）。
このパッチにより `mariadb-connector-c` は clasdb に接続できるため、推奨コネクタとなっています。

<br/>

## プラグインパス

CLAS12 システムプラグインは、`<prefix>/lib/` 配下に `.gplugin` 共有ライブラリとしてインストールされます。
GEMC は、`GEMC_PLUGIN_PATH`、自身の `lib/` および `build/` ディレクトリ、
OS の動的ライブラリ検索パス（Linux では `LD_LIBRARY_PATH`、macOS では `DYLD_LIBRARY_PATH`）の順に
プラグインを検索します。

最も簡単な設定は、CLAS12 システムを GEMC 自身のプレフィックスにインストールすることです。
これにより、`.gplugin` ライブラリは GEMC がすでに検索する `lib/` ディレクトリに配置され、
実行時の変数設定が不要になります。GEMC のプレフィックスは、その `bin/` ディレクトリの 1 階層上なので、
`command -v gemc` の結果から導出できます。

```shell
meson setup build --prefix="$(dirname "$(dirname "$(command -v gemc)")")"
meson install -C build
gemc dc.yaml
```

GEMC が `PATH` 上にあるものの、異なるプレフィックスが構成されている場合、
Meson は構成時に警告を表示します。その場合は、`gemc` を実行する前に、
`GEMC_PLUGIN_PATH` を CLAS12 システムのライブラリディレクトリに設定してください。

```shell
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
gemc dc.yaml
```

または、コマンドラインで指定します。

```shell
gemc dc.yaml -plugin_path=/path/to/clas12-systems/lib
```

プラグインが見つからない場合、GEMC はパスの問題を診断しやすくするため、
エラーとともに `GEMC_PLUGIN_PATH` の現在値を表示します。

Meson ビルドのインストール先プレフィックスでは、pkg-config ファイルからプラグインディレクトリを取得できます。

```shell
# After: meson install -C build --prefix=/my/clas12/prefix
export PKG_CONFIG_PATH=/my/clas12/prefix/lib/pkgconfig:$PKG_CONFIG_PATH
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
```

<br/>


## プラグインのビルドモデル

システムプラグインはレジストリパターンを使用します。

1. 検出器固有の `geometry_src/<system>/plugin/meson.build` が `clas12_plugins` に辞書を追加します。
2. トップレベルの `meson.build` だけが、それらのエントリからインストール対象の共有ライブラリを生成します。
3. インストールされる GEMC プラグインは `.gplugin` サフィックスを使用しなければなりません。

これにより、CLAS12 システム全体でプラグインのインストール方法を統一し、
各検出器が独自のビルドロジックを用意する必要をなくします。

### ロギングテンプレート

次リリース予定: プラグインのロギングは、メッセージ全体を一度に渡す `GLogger` API を使用します。
英語の文を分割せずにまとめて記述し、値は番号付きプレースホルダーを通じて渡してください。

```cpp
log->info(1, "Loaded %1 constants for run %2.", count, runno);
```

`debug`、`warning`、`error`、`critical` も同じプレースホルダールールを使用します。
対応するバージョンの GEMC ヘッダーを使ってプラグインを再ビルドしてください。
従来の文字列連結形式の呼び出しは移行が必要です。
動的な診断テキストは `log->warning("%1", text)` のように値として渡すと、
その中のパーセント記号を文字どおりに保持できます。

生成される英語カタログは `translations/en.yaml` にあります。
`translations/catalog.yaml` は、対象となるプラグインのソースを選択します。
同じ親ディレクトリにある GEMC ソースツリーの共有抽出ツールを使って、再生成またはチェックします。

```shell
../src/build/subprojects/pygemc/python_env/bin/python ../src/ci/extract_messages.py extract --root .
../src/build/subprojects/pygemc/python_env/bin/python ../src/ci/extract_messages.py extract --root . --check
../src/build/subprojects/pygemc/python_env/bin/python ../src/ci/extract_messages.py validate-tree --root .
```

英語メッセージは、生成されたカタログではなく C++ 内で編集してください。翻訳の検証については、
[カタログガイド](https://github.com/gemc/src/blob/main/translations/README.md) を参照してください。
実行時のロギングでは言語が自動的に選択されます。`-language=it` はイタリア語を選択し、
`-language=en` は英語を強制します。翻訳のないメッセージは英語のまま表示されます。
Meson はプラグインカタログを `<prefix>/share/gemc/translations/clas12` 配下にインストールします。
既存のプラグイン検索パスを通じて、別のインストールプレフィックスにあるカタログも利用できます。
対応する GEMC ヘッダーと新しい `glogging` ライブラリを使ってプラグインを再ビルドしてください。
共有の Claude/Codex ワークフローは、既存の平日 cron ジョブを通じて言語カタログを生成します。
その `gemc/clas12-messages` エントリは、検証付きで再開可能なバッチ処理を使用し、
ソースの git コミットを追跡します。Test ワークフローも、エージェントを使用せずに生成された全カタログを検証し、
必須の言語ファイル、キー、プレースホルダー、パーセントエスケープ、空白をチェックします。
翻訳のないメッセージについては、英語へのフォールバックを伴う翻訳カバレッジが報告されます。
翻訳の正確性は、引き続きエージェントレビューで確認します。

<br/>

## 磁場

CLAS12 は、解析的なモデルではなく、測定されたソレノイドおよびトーラスの
**磁場マップに基づく**磁場を使用します。磁場は `plugins/field/` 配下の
`gfieldclas12-cmag` プラグインが提供します。このプラグインは、David Heddle の
[cMag](https://github.com/JeffersonLab/clas12-cmag) ライブラリ（`clas12-cmag` サブプロジェクト）を通じて
CLAS12 のソレノイドおよびトーラスのバイナリマップを読み込み、各ステップ点での合成磁場を返します。

磁場はコア GEMC の汎用 `gfields` ノードで設定し、`type: clas12-cmag` でこのプラグインを選択します。

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

`global_field` の値は、ソレノイドやトーラスのマップ名ではなく、設定した磁場名（上記の `clas12`）です。
マップ名とマップごとのスケール係数は `gfields` エントリに指定します。
これは、GEMC2 の `global_field: Symm_solenoid_...:Symm_torus_...` 形式と、
従来のハードコードされたスケール設定対象 `binary_torus` /
`binary_solenoid` を、明示的な `torus`、`solenoid`、`torus_scale`、
`solenoid_scale` パラメータで置き換えるものです。

追加のスカラーキー（マップごとの変位、全体の原点や回転、`interpolation`）は、
そのままプラグインに渡されます。

磁場マップは `magfield` git-lfs サブプロジェクトから取得され、`meson
install` 時に `<prefix>/fields` にコピーされます（`meson/install_fields.py` を参照）。
プラグインは、自身の隣にインストールされた `fields` ディレクトリ（`<plugin_dir>/../fields`）から
マップを読み込みます。`-Duse-fields-location=<dir>` を指定して構成すると、
サブプロジェクトをスキップし、代わりに既存のマップディレクトリを使用します
（クローンやインストールは行われません）。
実行時に `FIELD` や `FIELD_DIR` 環境変数を設定する必要はありません。
明示的な `dir` パラメータで場所を上書きできます。

<br/>

## ストリーミングリードアウト（SRO）

**次リリース予定。** CLAS12 システムは、通常のイベント出力の代わりに、またはそれと並行して、
JLAB DAQ バイナリ形式のストリーミングリードアウト（SRO）フレームを出力できます。
GEMC は汎用の `sro` ストリーマーを提供し、システムプラグインはデジタイザーとともに
`GSROImplementationFactory` をエクスポートすることでペイロードを供給します。
現在、SRO ペイロードを供給するのは **FT-Cal** のみです（`ft_cal.gplugin` を通じて）。
他の FT デジタイザーは SRO モデルを持たず、通常の出力を維持します。

コマンドラインから SRO を有効にするには、`sro` ストリーマー形式と、
ペイロードを提供するプラグインを選択し、データ収集のイベント時間幅にゼロ以外の値を指定します。

```shell
gemc geometry_src/ft/ft.yaml -n=10000 \
  -gstreamer='[{format: sro, filename: ftcal_sro, implementation: ft_cal}]' \
  -eventTimeWidth='10*ns'
```

- `format: sro` は GEMC の SRO ストリーマーを選択します。
  `implementation: ft_cal` はペイロードを生成するプラグインを指定し、`filename` は出力のベース名です。
- `-eventTimeWidth` は、データ収集のタイムライン上で連続するイベント間の間隔を設定します。
  デフォルト値のゼロでは SRO の実行が拒否されるため、明示的な設定が必要です
  （上記の `10*ns` は一例であり、測定された CLAS12 ビームパラメータではありません）。
  通常の出力では設定不要です。
- 出力ファイルはクレートごとに `<basename>_r<resolved_run>_crate<crate>.ev` として書き出されます。
  同じベース名と run を再利用すると、ファイルが上書きされます。

FT の初期登録を行う `ft.gplugin` が `ft_cal.gplugin` のオプションを提供するため、
追加のオプションノードは不要です。変換テーブルの規約、
ワーカーのタイミングモデル（`ft_cal_sro_min_signal_time` を含む）、バイナリレイアウト、
`sro` テストスイートについては [`geometry_src/sro/README.md`](geometry_src/sro/README.md) を
参照してください。移植された DAQ 定義とその出典は
[`geometry_src/sro/daq/README.md`](geometry_src/sro/daq/README.md) にあります。

<br/>

## 検証

移植した各検出器について、生成されたデータベース行と実行時のジオメトリ動作の両方を検証してください。

推奨するチェック項目:

- 生成されたジオメトリ行を、[`gemc/clas12Tags`](https://github.com/gemc/clas12Tags) の
  `geometry_source/<system>` 配下にある GEMC2 の参照データと比較する。
- 共通のフィールドについて、名前、親ボリューム、説明、位置、回転、ソリッド、パラメータ、マテリアルが
  一致することを確認する。
- run および variation のマッピングがシステムディレクトリ内で完結していることを確認する。
- Geant4 で本格的に実行する前に、PyVista エクスポートを使って配置を手早く確認する。
- 検出器のジオメトリが確認可能な程度まで整ったら、GEMC をバッチモードと GUI モードで実行する。

DC については、生成されたデフォルトジオメトリが、次の参照データとトークン単位で一致する必要があります。

```text
https://github.com/gemc/clas12Tags/blob/main/geometry_source/dc/dc__geometry_default.txt
```

DC で満たすべき既知の条件:

- デフォルトの run は `11`
- すべての DC ボリュームで `g4placement_type = "passive"` を使用する
- 順序付き回転を `ordered: ...` として保持する
- 廃止された `original` variation はサポートしない

<br/>

## CI とリリース

次リリースから、すべてのコンテナワークフローは、
[`gemc/g4install`](https://github.com/gemc/g4install) が公開する Geant4 ベースイメージ上で、
GEMC と CLAS12 システムをソースからビルドします。
[ワークフローガイド](.github/workflows/README.md) では、トリガー、デプロイの認可、
リポジトリ間の取り決め、権限、再試行、想定される実行スキップについて説明しています。

関連する自動化:

| ワークフロー | 目的 |
|-----------------------|-------------------------------------------------------------------------------------|
| `deploy.yml` | Geant4 ベースイメージ上で GEMC と CLAS12 システムをビルドし、イメージを公開 |
| `pr-docker-image.yml` | PR ごとのプレビューイメージをビルドし、ローカルビルドなしでブランチをレビュー可能にする |
| `sanitize.yml` | サードパーティのサブプロジェクトを対象外として、CLAS12 システムのサニタイザービルドを実行 |
| `codeql.yml` | 静的解析 |
| `doxygen.yml` | ドキュメント生成 |
| `binary_tarballs.yml` | デプロイ後に GEMC を再ビルドし、スモークテストを実行 |
| `dev_release.yml` | 開発リリースの自動化 |

デプロイイメージは次のパターンを使用します。

```text
ghcr.io/gemc/clas12-systems:<gemc-tag>-<os>-<version>[-<arch>]
```

ベースイメージは次から取得されます。

```text
ghcr.io/gemc/g4install
```

各プルリクエストではさらに、ブランチからビルドされた、すぐに実行可能なマルチアーキテクチャの
プレビューイメージ（`ghcr.io/gemc/clas12-systems:<gemc-tag>-almalinux-<version>-pr-<number>`）を
公開します。これにより、作成者とレビュアーはローカルビルドなしでテストできます。
貢献ガイドの[プレビューコンテナイメージ](CONTRIBUTING.md#preview-container-image) を参照してください。
このイメージは、プルリクエストがクローズされると自動的に削除されます。

<br/>


## ドキュメント

- [CI ワークフローガイド](.github/workflows/README.md)
- [GEMC ホームページ](https://gemc.github.io/home/)
- [Python API リポジトリ](https://github.com/gemc/pygemc)
- [GEMC2 / CLAS12 リポジトリ](https://github.com/gemc/clas12Tags)

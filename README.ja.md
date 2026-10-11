<!-- TRANSLATIONS:START (managed by bin/translate) -->
**Languages:** [EN](README.md) · [IT](README.it.md) · **日本語** · [FR](README.fr.md) · [中文](README.zh.md)
<!-- TRANSLATIONS:END -->

# CLAS12 GEMC Systems

[![テスト][badge-test]][workflow-test]
[![ASCII ジオメトリ比較][badge-ascii-geometry]][workflow-ascii-geometry]
[![デプロイ][badge-deploy]][workflow-deploy]
[![サニタイザ検査][badge-sanitize]][workflow-sanitize]
[![CodeQL 詳細解析][badge-codeql]][workflow-codeql]
[![Doxygen][badge-doxygen]][workflow-doxygen]
[![バイナリ tarball][badge-binary-tarballs]][workflow-binary-tarballs]
[![開発版のナイトリーリリース][badge-dev-release]][workflow-dev-release]
[![HIPO ヒストグラム比較][badge-hipo-histos]][workflow-hipo-histos]
[![macOS tarball][badge-macos-tarball]][workflow-macos-tarball]
[![Valgrind プロファイリング][badge-valgrind-profile]][workflow-valgrind-profile]

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
収録しています。コアとなる GEMC アプリケーションおよび Python ジオメトリ API を補完する、CLAS12 用の
リポジトリです。

- [`gemc/src`](https://github.com/gemc/src) は、GEMC C++ アプリケーション、Geant4 統合、
  SQLite/ASCII/CAD/GDML ジオメトリローダー、動的プラグイン基盤、ストリーマー、同梱の `pygemc`
  環境を提供します。
- [`gemc/pygemc`](https://github.com/gemc/pygemc) は、ジオメトリとマテリアルの定義、GEMC データベースの
  書き込み、PyVista によるジオメトリのプレビュー、VTK.js シーンのエクスポートに用いる Python API を
  提供します。
- [`gemc/home`](https://github.com/gemc/home) には、公開 GEMC ウェブサイト、インストールページ、
  チュートリアル、例、および生成されたドキュメントアセットが含まれます。

<br/>

## 現在の対応範囲

このリポジトリでは、[`gemc/clas12Tags`](https://github.com/gemc/clas12Tags) からの移行作業が進行中です。

| システム | 対応状況                   | 備考                                                |
|---------|---------------------------|-----------------------------------------------------|
| `dc`    | ジオメトリとプラグイン        | ジオメトリの生成元として coatjava を使用                 |
| `ec`    | ジオメトリとプラグイン        | coatjava と共有 `ecal` プラグインを使用                  |
| `field` | プラグイン                  | cMag ライブラリ経由で CLAS12 の磁場マップを使用           |
| `ft`    | ジオメトリとプラグイン        | 次リリース予定: FTCAL、FTHODO、FTTRK                    |
| `ftof`  | ジオメトリとプラグイン        | ジオメトリの生成元として coatjava を使用                 |
| `ltcc`  | ジオメトリとプラグイン        | 光学サーフェス付きのネイティブおよび CAD ジオメトリ        |
| `pcal`  | ジオメトリと共有プラグイン    | coatjava と共有 `ecal` プラグインを使用                  |


<br/>

## GEMC

コアとなる GEMC リポジトリ [`gemc/src`](https://github.com/gemc/src) が実行時の動作を担当します。
これには以下が含まれます。

- Geant4 のソリッド、論理ボリューム、物理配置の構築
- 動的 C++ プラグイン
- イベント生成、感応検出器、出力ストリーマー

このリポジトリは、その実行環境への CLAS12 固有の入力を担当します。

- 検出器ジオメトリ、マテリアル定義
- CLAS12 ジオメトリを再現するために必要な run および variation のマッピング
- GEMC2 CLAS12 の参照ジオメトリおよび出力との照合

[`gemc/pygemc`](https://github.com/gemc/pygemc) リポジトリが Python API を定義します。

> **ゼロからのビルド — GEMC の事前インストールは不要。** 次リリースから、CLAS12 システムは Geant4 のみを
> 用意した環境（例えば `ghcr.io/gemc/g4install` イメージ）上で、**GEMC が存在しない状態でも** ビルドおよび
> インストールできます。インストール済み GEMC が見つからない場合、ビルド時に `gemc` サブプロジェクトから
> 自動的に GEMC をコンパイルし、同じプレフィックスにインストールします。GEMC は次の順序で解決されます —
> 明示的な `-Duse-gemc-location=<dir>`、次にインストール済み GEMC（pkg-config または `PATH` 上の `gemc`
> バイナリ）、最後にソースからビルドするサブプロジェクトです。**Geant4 はビルドされません**: 事前に
> 利用可能になっている必要があり、そうでない場合は構成に失敗します。すべてのコンテナ CI ワークフローは、
> サポート対象の各ディストリビューションの g4install イメージ上で、この方法を使用します。

<br/>

## ジオメトリワークフロー

各検出器システムは `geometry_src/<system>` 配下で自己完結しています。

典型的なシステムディレクトリには以下が含まれます。

| ファイル                                     | 役割                                                                                 |
|----------------------------------------------|--------------------------------------------------------------------------------------|
| `<system>.py`                                | 実行可能なメインスクリプト。`autogeometry()` を作成し、マテリアルとボリュームを公開する        |
| `geometry.py`                                | ジオメトリ構築コード                                                                     |
| `materials.py`                               | システムのマテリアル定義                                                                 |
| `variations.py`                              | 任意の run および variation マッピング                                                   |
| `<system>.yaml`                              | ローカルで手軽に実行するための GEMC ステアリングカード                                      |
| `../coatjava_factories/CoatjavaFactory.java` | 任意の coatjava ブリッジ（Java ジオメトリサービスを使う場合）                                |
| `plugin/meson.build`                         | デジタイズやその他の実行時拡張のための任意の C++ プラグイン登録                               |

メインスクリプトには実行権限を付与し、そのディレクトリから直接実行できるようにしてください。

```shell
cd geometry_src/dc
./dc.py 
```

システムのジオメトリを視覚的に確認できる段階になったら、`pygemc` の PyVista オプションを使用します。

```shell
./dc.py -pvb
```

ローカルのステアリングカードで GEMC を実行します。

```shell
gemc dc.yaml
gemc dc.yaml -gui
```

感応ボリュームのジオメトリ行は、ボリュームの `digitization` フィールドを通じて実行時のプラグインを選択します。
YAML の `gsystem` エントリに指定できる `digitization` キーの役割は、これより限定的です。
`ec` と `pcal` システムが `ecal.gplugin` を共有する場合のように、システム名と異なる名前のどのプラグインを
オプション解析前に調べるべきかを GEMC に伝えます。FT には 3 つの感応名（`ft_cal`、`ft_hodo`、`ft_trk`）が
あるため、その YAML では通常の `name: ft` エントリを使います。オプション専用の `ft.gplugin` は、
初期化時の探索で 3 つのドメインすべてを登録します。その後、ジオメトリのロード時に感応ボリュームの行から
3 つのデジタイザを検出してロードします。

<br/>

## 参照データとの照合

生成された GEMC3 ASCII データベース（ジオメトリとマテリアル）を、対応する
[`gemc/clas12Tags`](https://github.com/gemc/clas12Tags) の参照ファイルと比較するには、
`scripts/compare_ascii_databases.py` を使用します。

```shell
scripts/compare_ascii_databases.py dc
```

システム引数を指定しない場合、スクリプトはローカルのすべての `geometry_src/<system>/<system>.py` 実装を
チェックします。スクリプトは GEMC2 と GEMC3 の ASCII 列を共通のジオメトリフィールド — 名前、親ボリューム、
位置、回転、ソリッド、寸法、マテリアル、デジタイズ（GEMC2 の `sensitivity`）、識別子（GEMC2 の `identifiers`。
正規化された `name=value` 形式に展開）— にマッピングし、ボリューム名をキーとして各フィールド値のみを比較します。
そのため、書式や列順序の違いによって、実際には一致しているジオメトリが不一致と判定されることはありません。
カスタムマテリアルを定義するシステムでは、マテリアルも同様に名前をキーとして、密度、構成要素、光学特性、
シンチレーション特性を比較します。数値表記と GEMC2/GEMC3 のポリコーン配列の順序は、比較前に正規化されます。

いずれかのフィールドが異なる場合、スクリプトはフィールドごとの不一致を出力し、ステータス `1` で終了します。
すべて一致した場合はステータス `0` で終了します。

<br/>

## 配置と回転

GEMC3 は `GVolume.g4placement_type` を通じて、Geant4 の 2 つの配置規約をサポートします。

| 値        | 意味                                                                                   |
|-----------|----------------------------------------------------------------------------------------|
| `active`  | GEMC3 のデフォルト動作。`G4Transform3D(rotation, translation)` を使用                   |
| `passive` | GEMC2/clas12Tags 互換の動作。`G4PVPlacement(rotation, translation, ...)` を使用         |

GEMC2 から移植された CLAS12 検出器ボリュームでは、受動的な配置規約を使用してください。

```python
gvolume.g4placement_type = "passive"
```

順序付き回転はデータベース内でも順序付きのまま保持してください。例えば、以下をフラット化してはいけません。

```text
ordered: yxz, 0*deg, 0*deg, 6*deg
```

GEMC は順序付き回転を指定された順序で適用します。これは DC で必須であり、`clas12Tags` から移植された
他の CLAS12 システムでも重要になると予想されます。

<br/>

## Coatjava

一部の CLAS12 システムは、再構成で使われるものと同じ Java ジオメトリサービスにシミュレーションジオメトリを
合わせるために、coatjava を使用します。このリポジトリでは、coatjava を `geometry_src` 配下に配置します。

```shell
./geometry_src/install_coatjava.sh -l
```

Meson の構成時に `geometry_src/coatjava` が存在しない場合、coatjava は自動的にインストールされます。
CI と Docker イメージでは、事前に以下の必須ツールを用意する必要があります。

- Java
- Maven
- git-lfs
- jq

ヘルパースクリプトは以下のとおりです。

| パス                               | 用途                                                              |
|------------------------------------|-------------------------------------------------------------------|
| `geometry_src/install_coatjava.sh` | ローカルの coatjava コピーをインストールする                        |
| `ci/install_coatjava_deps.sh`      | サポート対象の CI イメージに Java、Maven、git-lfs、jq をインストールする |
| `ci/setup_coatjava.sh`             | 必須ツールをインストールし、必要なら coatjava をインストールする CI ヘルパー |

リセットフラグが明示的に要求されない限り、既存の coatjava インストールを削除しないでください。

<br/>

## ビルドとテスト

このリポジトリは Meson でビルドされ、`meson/` 配下で構成された GEMC および Geant4 の依存関係を使用します。

事前に用意する必要があるのは **Geant4** のみです（そのモジュールをロードするか、`geant4-config` を
`PATH` に置いてください）。GEMC の事前インストールは **不要** です。見つからない場合は
`gemc` サブプロジェクトからコンパイルされ、同じ `--prefix` にインストールされます。これにより、CLAS12
システムを Geant4 のみの環境にゼロからインストールできます（[GEMC](#gemc) セクションの補足説明を
参照）。

構成、ビルド、テスト:

```shell
meson setup build --prefix="$PWD/install"
meson compile -C build
meson install -C build
meson test -C build --suite clas12 --print-errorlogs
```

**CLAS12 テストと GEMC コアテスト。** このリポジトリ自身のテストはすべて `clas12` スイート（ジオメトリ
生成、GEMC での検出器構築、CCDB 接続確認、SRO チェック）に属します。このため、上記のコマンドおよび CI
（`ci/build.sh`）では `--suite clas12` を実行します。GEMC の **コア** テストは `gemc/src` に属し、
このリポジトリには含まれません。GEMC がここで `gemc` サブプロジェクトとしてコンパイルされる際、GEMC は
自身のテストを **一切** 登録しません。これらのテストは、ビルドツリー内の未インストールの GEMC を対象とし、
`gemc/src` 自身の CI が担当します。したがって、ここで `meson test -C build` のみを実行すると、`clas12`
スイートだけが実行されます。GEMC コアスイートを実行する正式な場所は、[`gemc/src`](https://github.com/gemc/src)
リポジトリそのものです。（`-Dinclude-subproject-tests=true` オプションは、他の同梱サブプロジェクト — CCDB、
HIPO、clas12-cmag — を制御するものであり、GEMC は対象外です。）

次リリース予定: 各検出器に、`clas12` および `gemc` スイートに属する `gemc_<system>` スモークテストが追加されます。
ジオメトリ生成後、インストール済みの GEMC を起動し、ネイティブおよび CAD ジオメトリを構築し、分離された
一時ディレクトリ内でイベント数ゼロ・磁場なしで検出器プラグインをロードします。ジオメトリテストによって
`build/clas12.db` にデータが書き込まれたら、
`meson test -C build --suite gemc --print-errorlogs` で構築テストのみを再実行できます。
GEMC をサブプロジェクトとしてビルドした場合は、必要な実行時ディレクトリ構成を整えるため、
テストの前にインストールしてください。

GEMC をビルドする代わりに既存の GEMC インストールを再利用するには、`-Duse-gemc-location=<dir>` を渡すか、
`gemc` バイナリを `PATH` に置いてください。

既存のライブラリインストールと磁場マップを再利用するには、以下の独立したオプションを使用します。3 つの
ライブラリオプションと、構成時に指定する磁場プラグインのデフォルトのマップディレクトリは、次リリースで導入予定です。

| Meson オプション | 指定するパス |
| --- | --- |
| `-Duse-gemc-location=<dir>` | GEMC インストールプレフィックス |
| `-Duse-ccdb-location=<dir>` | CCDB インストールプレフィックス |
| `-Duse-hipo-location=<dir>` | HIPO インストールプレフィックス |
| `-Duse-clas12-cmag-location=<dir>` | clas12-cmag インストールプレフィックス |
| `-Duse-fields-location=<dir>` | CLAS12 磁場マップを含むディレクトリ |

例えば、4 つすべてを再利用するには:

```shell
meson setup build --prefix="$PWD/install" \
  -Duse-ccdb-location=/absolute/path/to/ccdb \
  -Duse-hipo-location=/absolute/path/to/hipo \
  -Duse-clas12-cmag-location=/absolute/path/to/clas12-cmag \
  -Duse-fields-location=/absolute/path/to/magfield
```

各オプションのデフォルトは空で、独立して設定できます。ライブラリオプションが空の場合、既存の依存関係設定を
維持します。ライブラリパスを指定する場合は絶対パスが必要で、対応するサブプロジェクトはスキップされます。
指定先のインストールが無効な場合、構成に失敗します。ヘッダーは `include/`（古い clas12-cmag インストールでは
`includes/` も）、ライブラリは `lib/` または `lib64/` 配下にある必要があります。Meson の
`-Dprefer_static=true` は、両種類のライブラリがインストールされている場合に静的ライブラリを優先します。
プラグインが使用する静的ライブラリは、位置独立コードでビルドされている必要があります。インストール済み CCDB には
MySQL/MariaDB クライアント開発ツールと SQLite が必要です。インストール済み HIPO には LZ4 と fmt の開発
パッケージが必要です。外部インストールは `meson install` によってコピーされません。

`-Duse-fields-location=<dir>` を指定すると、マップは取得もインストールもされず、磁場プラグインは
デフォルトでそのディレクトリを使用します。磁場に明示的に指定した `dir` パラメータが引き続き優先されます。
オプションが空の場合、マップは `magfield` git-lfs サブプロジェクトから取得され、`<prefix>/fields` 配下に
インストールされます。プラグインは、自身のインストール場所を基準とした相対位置からそのディレクトリを特定します。
マップの取得には git-lfs が必要です。

GEMC 自体も同様の方法で解決されます。`-Duse-gemc-location=<dir>` は、その絶対プレフィックスにインストール
された GEMC を使用します（`lib/pkgconfig/gemc.pc` が存在する必要があります）。オプションが空の場合、
pkg-config または `PATH` 上の `gemc` バイナリを通じてインストール済み GEMC が見つかればそれを使用し、
そうでなければ `gemc` サブプロジェクトをソースからビルドします。Geant4 はビルドされません。事前に
利用可能になっている必要があり（構成前に Geant4 モジュールをロードしてください）、見つからない場合は
構成に失敗します。

次リリース予定: 同梱の CCDB は `ccdb_system_sqlite.patch` によりシステムの SQLite を使用し、
独自に同梱する SQLite アマルガメーションを使用しなくなります。既存のパッチ未適用の CCDB サブプロジェクトの
チェックアウトは、再ビルド前に取得し直す必要があります。

```shell
meson subprojects purge --confirm ccdb
```

その後、新しいビルドディレクトリで構成を行い、Meson が CCDB を取得して wrap パッチを適用するようにします。

ジオメトリテストは、登録された各 Python システムを実行し、統合された SQLite データベースを書き込みます。

```shell
meson test -C build geometry_dc --print-errorlogs
sqlite3 build/clas12.db "select system, variation, run, count(*) from geometry group by 1,2,3;"
```

CLAS12 システムレジストリは現在 `meson.build` にあります。

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

検出器名をこのリストに追加するのは、`geometry_src/<system>/<system>.py` が有効な GEMC ジオメトリを生成
できる状態になってからにしてください。

<br/>

## CCDB 較正定数

検出器のデジタイズプラグイン（`dc`、`ecal`、`ft_cal`、`ft_hodo`、`ftof`、`ltcc`）は、較正定数を CCDB から
ロードします。デフォルトでは、JLab データベース
`mysql://clas12reader@clasdb.jlab.org/clas12` に接続します。
別のサーバーまたはローカルの SQLite スナップショット（`sqlite:///path/to/ccdb.sqlite`）を使用するには、
`CCDB_CONNECTION` 環境変数を設定します。これは CCDB データベースであり、GEMC2 の `clas12.sqlite` 検出器
データベースではないことに注意してください。後者を指定すると定数が取得できません。CCDB 関連の障害（到達不能な
ホスト、誤ったデータベース、空のテーブル）が発生した場合、プラグインは何も通知せず空のデジタイズ出力を生成する
代わりに、明確なエラーを出して実行を中止するようになりました。

### MariaDB と MySQL のコネクタ（macOS）

macOS では、CCDB クライアントライブラリの選択に注意が必要です。`clas12reader` アカウントは
`mysql_native_password` で認証しますが、Oracle はこの方式を MySQL クライアントライブラリのバージョン 9.0 で
**削除** しました（SHA1 ベースであり、セキュリティ上の理由から非推奨とされていました）。そのため、MySQL 9.x に
リンクされた CCDB は clasdb で認証できず、接続時に失敗します。これはクライアントライブラリの制限であり、
CCDB のバグではありません。ライブラリのビルド時に除去された機能を CCDB のソース変更で復元することはできません。
この機能を引き続き提供するコネクタをインストールしてください。

```shell
brew install mariadb-connector-c   # preferred: maintained; supports native_password and caching_sha2_password
# or
brew install mysql-client@8.4      # Oracle LTS that still ships native_password
```

Meson ビルドは CCDB コネクタを自動的に選択します（`meson/meson.build`）。優先順位は `mariadb-connector-c`、
`mysql-client@8.4`、`mysql-client`、`mysql` の順で、クリーンビルドでは手動でリンクし直すことなく、動作する
クライアントがリンクされます。MySQL 9.x しかインストールされていない場合でも CCDB はビルドされますが、
互換性のあるコネクタがインストールされるまで（またはサーバーアカウントが `caching_sha2_password` に移行
するまで）、clasdb への接続は明確なエラーで失敗します。

これとは別に、MariaDB 固有の注意点があります。`mariadb-connector-c` は **デフォルトで TLS を必須にする**
一方、clasdb は SSL なしで動作するため、そのままの MariaDB ビルドは `Error 2026 (SSL is required, but the
server does not support it)` で失敗します。`ccdb` サブプロジェクトには、MariaDB にリンクしてビルドする場合に
TLS の必須化を無効にするパッチが適用されます（`subprojects/ccdb.wrap` の `diff_files` →
`subprojects/packagefiles/ccdb_ssl_no_enforce.patch` を経由）。これにより、Oracle libmysqlclient の
デフォルトである平文接続へのフォールバックと動作を合わせます。このパッチは `#ifdef LIBMARIADB` で
ガードされているため、MySQL/Oracle クライアント（このオプションを削除しており、そもそも TLS を必須にしない）
には影響しません。このパッチにより `mariadb-connector-c` は clasdb に接続でき、推奨コネクタとなります。

<br/>

## プラグインパス

CLAS12 システムプラグインは、`<prefix>/lib/` 配下に `.gplugin` 共有ライブラリとしてインストールされます。
GEMC はプラグインを次の順序で探索します: `GEMC_PLUGIN_PATH`、自身の `lib/` および `build/` ディレクトリ、
OS の動的ライブラリ検索パス（Linux では `LD_LIBRARY_PATH`、macOS では `DYLD_LIBRARY_PATH`）。

最も簡単な設定は、CLAS12 システムを GEMC 自身のプレフィックスにインストールすることです。そうすれば
`.gplugin` ライブラリは GEMC がすでに探索する `lib/` ディレクトリに配置され、実行時の変数設定は不要です。
GEMC のプレフィックスは `bin/` ディレクトリの 1 つ上の階層なので、`command -v gemc` から求められます。

```shell
meson setup build --prefix="$(dirname "$(dirname "$(command -v gemc)")")"
meson install -C build
gemc dc.yaml
```

GEMC が `PATH` 上にあり、別のプレフィックスが構成されている場合、Meson は構成時に警告を出力します。
その場合は、`gemc` を実行する前に `GEMC_PLUGIN_PATH` を CLAS12 システムのライブラリディレクトリに設定します。

```shell
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
gemc dc.yaml
```

または、コマンドラインで渡します。

```shell
gemc dc.yaml -plugin_path=/path/to/clas12-systems/lib
```

プラグインが見つからない場合、GEMC はパスの問題を診断しやすくするため、エラーとともに現在の
`GEMC_PLUGIN_PATH` の値を出力します。

Meson ビルドのインストール先プレフィックスでは、pkg-config ファイルを通じてプラグインディレクトリを
取得できます。

```shell
# After: meson install -C build --prefix=/my/clas12/prefix
export PKG_CONFIG_PATH=/my/clas12/prefix/lib/pkgconfig:$PKG_CONFIG_PATH
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
```

<br/>


## プラグインビルドモデル

システムプラグインはレジストリパターンを使用します。

1. 検出器固有の `geometry_src/<system>/plugin/meson.build` が `clas12_plugins` に辞書を追加します。
2. トップレベルの `meson.build` だけが、それらのエントリからインストール対象の共有ライブラリを作成します。
3. インストールされる GEMC プラグインは `.gplugin` サフィックスを使用する必要があります。

これにより、CLAS12 システム全体でプラグインのインストール方法を統一し、各検出器で独自のビルドロジックを
作成する必要がなくなります。

<br/>

## 磁場

CLAS12 は、解析的なモデルではなく **マップに基づく** 磁場 — 実測されたソレノイドおよびトーラスの磁場マップ —
を使用します。磁場は `plugins/field/` 配下の `gfieldclas12-cmag` プラグインによって提供されます。この
プラグインは、David Heddle の [cMag](https://github.com/JeffersonLab/clas12-cmag) ライブラリ
（`clas12-cmag` サブプロジェクト）を通じて CLAS12 ソレノイドとトーラスのバイナリマップを読み取り、各ステップの
位置での合成磁場を返します。

磁場は、コア GEMC の汎用 `gfields` ノードで設定し、`type: clas12-cmag` でこのプラグインを選択します。

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

`global_field` の値は、設定された磁場名（上記の `clas12`）であり、ソレノイド/トーラスのマップ名ではありません。
マップ名とマップごとのスケール係数は `gfields` エントリに指定します。これは GEMC2 の
`global_field: Symm_solenoid_...:Symm_torus_...` 形式と、従来のハードコードされた `binary_torus` /
`binary_solenoid` というスケール指定の対象を、明示的な `torus`、`solenoid`、`torus_scale`、`solenoid_scale`
パラメータに置き換えるものです。

追加のスカラーキー（マップごとの変位、全体の原点/回転、`interpolation`）は、すべてそのままプラグインに
渡されます。

磁場マップは `magfield` git-lfs サブプロジェクトから取得され、`meson
install` の実行時に `<prefix>/fields` にコピーされます（`meson/install_fields.py` を参照）。
プラグインは、自身に隣接してインストールされた `fields` ディレクトリ（`<plugin_dir>/../fields`）から
マップを読み取ります。`-Duse-fields-location=<dir>` で構成すると、サブプロジェクトをスキップして
既存のマップディレクトリを使用します（クローンもインストールも行われません）。実行時に `FIELD` や `FIELD_DIR`
環境変数は不要です。明示的な `dir` パラメータで場所を上書きできます。

<br/>

## ストリーミングリードアウト（SRO）

**次リリース予定。** CLAS12 システムは、通常のイベント出力の代わりに、またはそれと併せて、JLAB DAQ バイナリ
形式でストリーミングリードアウト（SRO）フレームを出力できます。GEMC が汎用 `sro` ストリーマーを担当し、
システムプラグインがデジタイザとともに `GSROImplementationFactory` をエクスポートしてペイロードを
提供します。現在、SRO ペイロードを提供するのは **FT-Cal** のみです（`ft_cal.gplugin` を通じて）。他の FT
デジタイザは、SRO モデルを持たず、通常の出力を継続します。

コマンドラインから SRO を有効にするには、`sro` ストリーマー形式とペイロードを提供するプラグインを選択し、
データ収集に対してゼロ以外のイベント時間幅を指定します。

```shell
gemc geometry_src/ft/ft.yaml -n=10000 \
  -gstreamer='[{format: sro, filename: ftcal_sro, implementation: ft_cal}]' \
  -eventTimeWidth='10*ns'
```

- `format: sro` は GEMC の SRO ストリーマーを選択します。`implementation: ft_cal` はペイロードを生成する
  プラグインを指定します。`filename` は出力のベース名です。
- `-eventTimeWidth` は、データ収集の時間軸上で連続するイベント間の間隔を設定します。デフォルト値のゼロでは
  SRO の実行が拒否されるため、明示的に設定する必要があります（上記の `10*ns` は一例であり、実測された CLAS12
  ビームパラメータではありません）。通常の出力を行う実行では不要です。
- 出力ファイルはクレートごとに `<basename>_r<resolved_run>_crate<crate>.ev` として書き込まれます。同じベース名と
  run を再利用すると上書きされます。

FT の初期化用登録プラグイン `ft.gplugin` が `ft_cal.gplugin` のオプションを提供するため、追加のオプション
ノードは不要です。変換テーブルの規約、ワーカーのタイミングモデル（`ft_cal_sro_min_signal_time` を含む）、
バイナリレイアウト、`sro` テストスイートについては [`geometry_src/sro/README.md`](geometry_src/sro/README.md)
を参照してください。移植された DAQ 定義とその出典は
[`geometry_src/sro/daq/README.md`](geometry_src/sro/daq/README.md) にあります。

<br/>

## 検証

移植された各検出器について、生成されたデータベース行と実行時のジオメトリの動作の両方を検証します。

推奨チェック:

- 生成されたジオメトリ行を、[`gemc/clas12Tags`](https://github.com/gemc/clas12Tags) の
  `geometry_source/<system>` にある GEMC2 参照データと比較する。
- 共通するフィールドについて、名前、親ボリューム、説明、位置、回転、ソリッド、パラメータ、マテリアルが
  一致することを確認する。
- run および variation のマッピングがシステムディレクトリ内に保持されていることを確認する。
- Geant4 による本格的な実行の前に、PyVista エクスポートで配置を手早くチェックする。
- 検出器に検査できるだけのジオメトリがある場合、GEMC をバッチモードと GUI モードで実行する。

DC については、生成されたデフォルトジオメトリが以下とトークン単位で一致する必要があります。

```text
https://github.com/gemc/clas12Tags/blob/main/geometry_source/dc/dc__geometry_default.txt
```

DC で期待される既知の仕様:

- デフォルトの run は `11`
- すべての DC ボリュームは `g4placement_type = "passive"` を使用する
- 順序付き回転は `ordered: ...` として保持される
- 廃止された `original` バリエーションはサポートされない

<br/>

## CI とリリース

次リリースから、すべてのコンテナワークフローは、[`gemc/g4install`](https://github.com/gemc/g4install)
が公開する Geant4 ベースイメージ上で、GEMC と CLAS12 システムをソースからビルドします。
[ワークフローガイド](.github/workflows/README.md) では、トリガー、デプロイの認可、リポジトリ間の取り決め、
権限、再試行、想定どおりにスキップされる実行について説明しています。

関連する自動化:

| ワークフロー          | 用途                                                                                |
|-----------------------|-------------------------------------------------------------------------------------|
| `deploy.yml`          | Geant4 ベースイメージで GEMC と CLAS12 システムをビルドし、イメージを公開する            |
| `pr-docker-image.yml` | PR ごとのプレビューイメージをビルドし、レビュアーがローカルビルドなしでブランチをテストできるようにする |
| `sanitize.yml`        | サードパーティのサブプロジェクトを対象にせず、CLAS12 システムのサニタイザビルドを実行する |
| `codeql.yml`          | 静的解析                                                                             |
| `doxygen.yml`         | ドキュメント生成                                                                      |
| `binary_tarballs.yml` | デプロイ後に GEMC を再ビルドしてスモークテストする                                      |
| `dev_release.yml`     | 開発リリースの自動化                                                                   |

デプロイイメージは次のパターンを使用します。

```text
ghcr.io/gemc/clas12-systems:<gemc-tag>-<os>-<version>[-<arch>]
```

ベースイメージは以下から取得されます。

```text
ghcr.io/gemc/g4install
```

各プルリクエストでは追加で、ブランチからビルドされた、そのまま実行できるマルチアーキテクチャのプレビューイメージ
（`ghcr.io/gemc/clas12-systems:<gemc-tag>-almalinux-<version>-pr-<number>`）を公開するため、作成者と
レビュアーはローカルビルドなしでテストできます。貢献ガイドの
[プレビューコンテナイメージ](CONTRIBUTING.md#preview-container-image) を参照してください。このイメージは、
プルリクエストがクローズされると自動的に削除されます。

<br/>


## ドキュメント

- [CI ワークフローガイド](.github/workflows/README.md)
- [GEMC ホームページ](https://gemc.github.io/home/)
- [Python API リポジトリ](https://github.com/gemc/pygemc)
- [GEMC2 / CLAS12 リポジトリ](https://github.com/gemc/clas12Tags)

<!-- TRANSLATIONS:START (managed by bin/translate) -->
**Languages:** [EN](README.md) · [IT](README.it.md) · [日本語](README.ja.md) · [FR](README.fr.md) · **中文**
<!-- TRANSLATIONS:END -->

# CLAS12 GEMC Systems

[![测试][badge-test]][workflow-test]
[![ASCII 几何比对][badge-ascii-geometry]][workflow-ascii-geometry]
[![部署][badge-deploy]][workflow-deploy]
[![Sanitizer 检查][badge-sanitize]][workflow-sanitize]
[![CodeQL 高级分析][badge-codeql]][workflow-codeql]
[![Doxygen][badge-doxygen]][workflow-doxygen]
[![二进制归档包][badge-binary-tarballs]][workflow-binary-tarballs]
[![每夜开发版发布][badge-dev-release]][workflow-dev-release]
[![HIPO 直方图比对][badge-hipo-histos]][workflow-hipo-histos]
[![macOS 归档包][badge-macos-tarball]][workflow-macos-tarball]
[![Valgrind 性能分析][badge-valgrind-profile]][workflow-valgrind-profile]

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

CLAS12 GEMC Systems 包含 CLAS12 探测器几何系统的 GEMC3 实现及其各系统专属插件。它是核心 GEMC 应用程序和
Python 几何 API 的 CLAS12 配套仓库：

- [`gemc/src`](https://github.com/gemc/src) 提供 GEMC C++ 应用程序、Geant4 集成、
  SQLite/ASCII/CAD/GDML 几何加载器、动态插件基础设施、流式输出器，以及捆绑的 `pygemc`
  环境。
- [`gemc/pygemc`](https://github.com/gemc/pygemc) 提供用于定义几何和材料、写入 GEMC 数据库、
  使用 PyVista 预览几何，以及导出 VTK.js 场景的 Python API。
- [`gemc/home`](https://github.com/gemc/home) 包含 GEMC 公共网站、安装页面、教程、
  示例，以及生成的文档资源。

<br/>

## 当前范围

本仓库正持续推进从 [`gemc/clas12Tags`](https://github.com/gemc/clas12Tags) 的迁移。

| 系统    | 状态                        | 说明                                                |
|---------|---------------------------|-----------------------------------------------------|
| `dc`    | 几何和插件                  | 使用 coatjava 作为几何来源                           |
| `ec`    | 几何和插件                  | 使用 coatjava 和共享的 `ecal` 插件                  |
| `field` | 插件                        | 通过 cMag 库提供基于场图的 CLAS12 磁场               |
| `ft`    | 几何和插件                  | 下一版本推出：FTCAL、FTHODO 和 FTTRK                 |
| `ftof`  | 几何和插件                  | 使用 coatjava 作为几何来源                           |
| `ltcc`  | 几何和插件                  | 带光学表面的原生几何和 CAD 几何                      |
| `pcal`  | 几何和共享插件              | 使用 coatjava 和共享的 `ecal` 插件                  |


<br/>

## GEMC

核心 GEMC 仓库 [`gemc/src`](https://github.com/gemc/src) 负责运行时行为，包括：

- Geant4 实体、逻辑体和物理放置的构建
- 动态 C++ 插件
- 事件生成、灵敏探测器和流式输出器

本仓库负责向该运行时提供 CLAS12 专属输入：

- 探测器几何、材料定义，
- 重现 CLAS12 几何所需的运行编号和几何变体映射
- 与 GEMC2 CLAS12 参考几何和输出的比对验证

[`gemc/pygemc`](https://github.com/gemc/pygemc) 仓库定义 Python API。

> **从零构建——无需预装 GEMC。** 从下一版本起，CLAS12 系统可以在仅有 Geant4 的环境
> （例如 `ghcr.io/gemc/g4install` 镜像）中构建并安装，**无需预装
> GEMC**：当找不到已安装的 GEMC 时，构建过程会自动从 `gemc` 子项目编译它，并安装到同一前缀下。
> GEMC 按以下顺序查找：显式指定的 `-Duse-gemc-location=<dir>`，然后是已安装的 GEMC
> （通过 pkg-config 或 `PATH` 上的 `gemc` 二进制文件），最后是从源码构建的子项目。
> **构建过程绝不会构建 Geant4**：它必须已经可用，否则配置失败。
> 所有容器 CI 工作流都在各受支持发行版的 g4install 镜像上采用这种构建方式。

<br/>

## 几何工作流

每个探测器系统都在 `geometry_src/<system>` 下自成一体。

一个典型的系统目录包含：

| 文件                                         | 作用                                                                                 |
|----------------------------------------------|--------------------------------------------------------------------------------------|
| `<system>.py`                                | 可执行主脚本；创建 `autogeometry()` 并发布材料和几何体                                |
| `geometry.py`                                | 几何构建代码                                                                         |
| `materials.py`                               | 系统材料定义                                                                         |
| `variations.py`                              | 可选的运行编号和几何变体映射                                                         |
| `<system>.yaml`                              | 用于快速本地运行的 GEMC 运行控制卡                                                   |
| `../coatjava_factories/CoatjavaFactory.java` | 可选的 coatjava 桥接，用于采用 Java 几何服务的情形                                    |
| `plugin/meson.build`                         | 可选的 C++ 插件注册，用于数字化或其他运行时扩展                                       |

主脚本应具有可执行权限，并能直接从其所在目录运行：

```shell
cd geometry_src/dc
./dc.py 
```

当某个系统已准备好进行可视化检查时，使用 `pygemc` 提供的 PyVista 选项：

```shell
./dc.py -pvb
```

使用本地运行控制卡运行 GEMC：

```shell
gemc dc.yaml
gemc dc.yaml -gui
```

灵敏几何体的数据行通过几何体的 `digitization` 字段选择其运行时插件。YAML `gsystem` 条目中可选的
`digitization` 键用途更为有限：它告诉 GEMC 在解析选项之前应探测哪个与系统名称不同的插件，例如
`ec` 和 `pcal` 系统共享 `ecal.gplugin` 的情况。FT 有三个灵敏名称（`ft_cal`、`ft_hodo` 和 `ft_trk`），
因此其 YAML 保留普通的 `name: ft` 条目。仅提供选项的 `ft.gplugin` 在启动探测期间注册这三个域；
随后，几何加载过程从灵敏几何体的数据行中发现并加载这三个数字化器。

<br/>

## 参考比对

使用 `scripts/compare_ascii_databases.py` 将生成的 GEMC3 ASCII 数据库（几何和材料）与相应的
[`gemc/clas12Tags`](https://github.com/gemc/clas12Tags) 参考文件进行比对：

```shell
scripts/compare_ascii_databases.py dc
```

不传入系统参数时，该脚本会检查所有本地的 `geometry_src/<system>/<system>.py` 实现。
脚本将 GEMC2 和 GEMC3 的 ASCII 列映射到共同的几何字段——名称、母体、位置、旋转、实体、
尺寸、材料、数字化（GEMC2 的 `sensitivity`）以及标识符（GEMC2 的 `identifiers`，展开为规范的
`name=value` 形式）——并按几何体名称仅比对这些字段值，因此格式和列顺序的差异不会掩盖实际一致的几何。
对于定义了自定义材料的系统，材料也以相同方式按材料名称比对（密度、组分、光学和闪烁属性）。
比对前会对数值的表示形式以及 GEMC2/GEMC3 的 polycone 数组顺序进行规范化。

任何字段存在差异时，脚本都会打印字段级别的不匹配信息，并以状态 `1` 退出；全部匹配时以状态 `0` 退出。

<br/>

## 放置与旋转

GEMC3 通过 `GVolume.g4placement_type` 支持两种 Geant4 放置约定：

| 值        | 含义                                                                                   |
|-----------|----------------------------------------------------------------------------------------|
| `active`  | GEMC3 默认行为；使用 `G4Transform3D(rotation, translation)`                             |
| `passive` | 兼容 GEMC2/clas12Tags 的行为；使用 `G4PVPlacement(rotation, translation, ...)`          |

从 GEMC2 移植的 CLAS12 探测器几何体应使用被动放置约定：

```python
gvolume.g4placement_type = "passive"
```

在数据库中保留有序旋转的顺序。例如，不要展平以下表示：

```text
ordered: yxz, 0*deg, 0*deg, 6*deg
```

GEMC 会按指定顺序应用有序旋转。这对 DC 是必需的，预计对其他从 `clas12Tags` 移植的 CLAS12 系统也很重要。

<br/>

## Coatjava

部分 CLAS12 系统使用 coatjava，使模拟几何采用与重建相同的 Java 几何服务。本仓库将 coatjava 安装在本地的
`geometry_src` 下：

```shell
./geometry_src/install_coatjava.sh -l
```

如果 `geometry_src/coatjava` 缺失，Meson 配置阶段会自动安装 coatjava。CI 和 Docker 镜像必须先提供以下依赖：

- Java
- Maven
- git-lfs
- jq

辅助脚本如下：

| 路径                               | 用途                                                              |
|------------------------------------|-------------------------------------------------------------------|
| `geometry_src/install_coatjava.sh` | 安装本地 coatjava 副本                                            |
| `ci/install_coatjava_deps.sh`      | 在受支持的 CI 镜像中安装 Java、Maven、git-lfs 和 jq                 |
| `ci/setup_coatjava.sh`             | CI 辅助脚本，先安装依赖，再按需安装 coatjava                       |

除非明确要求使用重置标志，否则不要删除已有的 coatjava 安装。

<br/>

## 构建与测试

本仓库使用 Meson 构建，并使用在 `meson/` 下配置的 GEMC 和 Geant4 依赖。

事先只需具备 **Geant4**（加载其模块，或确保 `geant4-config` 位于 `PATH` 上）。GEMC **无需**
预装：如果未找到，它会从 `gemc` 子项目编译并安装到同一 `--prefix` 下。这使 CLAS12 系统能够在
仅有 Geant4 的环境中从零安装（参见 [GEMC](#gemc) 一节中的提示框）。

配置、构建并测试：

```shell
meson setup build --prefix="$PWD/install"
meson compile -C build
meson install -C build
meson test -C build --suite clas12 --print-errorlogs
```

**CLAS12 测试与 GEMC 核心测试。** 本仓库自身的测试全部属于 `clas12` 套件（几何生成、
GEMC 中的探测器构建、CCDB 连通性以及 SRO 检查），这也是上面的命令和 CI（`ci/build.sh`）
运行 `--suite clas12` 的原因。GEMC **核心**测试属于 `gemc/src`，不是本仓库的一部分：
当 GEMC 在此作为 `gemc` 子项目编译时，它**不会注册任何自身的测试**——这些测试针对构建目录中
尚未安装的 GEMC，由 `gemc/src` 自己的 CI 负责。因此，在此处直接执行 `meson test -C build`
只会运行 `clas12` 套件；运行 GEMC 核心测试套件的正式位置是
[`gemc/src`](https://github.com/gemc/src) 仓库本身。（`-Dinclude-subproject-tests=true`
选项控制的是其他捆绑子项目——CCDB、HIPO、clas12-cmag，而非 GEMC。）

下一版本推出：每个探测器在 `clas12` 和 `gemc` 套件中都有一个 `gemc_<system>` 冒烟测试。
几何生成后，该测试会启动已安装的 GEMC，构建原生几何和 CAD 几何，并在隔离的临时目录中
以零事件、无磁场的方式加载探测器插件。几何测试填充 `build/clas12.db` 后，可用
`meson test -C build --suite gemc --print-errorlogs` 仅重新运行几何构建测试。当 GEMC 作为子项目构建时，
请在测试前先安装它，以便可执行文件具备所需的运行时目录布局。

要复用现有的 GEMC 安装而非重新构建它，可传入 `-Duse-gemc-location=<dir>`（或将其 `gemc`
二进制文件置于 `PATH` 上）。

使用以下彼此独立的选项来复用现有的库安装和磁场图。这三个库选项以及可配置的磁场插件默认目录将在下一版本推出。

| Meson 选项 | 需提供的路径 |
| --- | --- |
| `-Duse-gemc-location=<dir>` | GEMC 安装前缀 |
| `-Duse-ccdb-location=<dir>` | CCDB 安装前缀 |
| `-Duse-hipo-location=<dir>` | HIPO 安装前缀 |
| `-Duse-clas12-cmag-location=<dir>` | clas12-cmag 安装前缀 |
| `-Duse-fields-location=<dir>` | 包含 CLAS12 磁场图的目录 |

例如，要同时复用全部四项：

```shell
meson setup build --prefix="$PWD/install" \
  -Duse-ccdb-location=/absolute/path/to/ccdb \
  -Duse-hipo-location=/absolute/path/to/hipo \
  -Duse-clas12-cmag-location=/absolute/path/to/clas12-cmag \
  -Duse-fields-location=/absolute/path/to/magfield
```

每个选项默认为空，可独立设置。库选项为空时会保留现有的依赖配置。提供的库路径必须为绝对路径，
并会跳过对应子项目；无效的安装会导致配置失败。头文件应位于 `include/` 下（较旧的 clas12-cmag
安装也支持 `includes/`），库应位于 `lib/` 或 `lib64/` 下。Meson 的 `-Dprefer_static=true`
会在静态库和动态库均已安装时优先选择静态库；插件使用的静态库必须以位置无关代码构建。
已安装的 CCDB 需要 MySQL/MariaDB 客户端开发工具和 SQLite；已安装的 HIPO 需要 LZ4 和 fmt 开发包。
`meson install` 不会复制这些外部安装。

使用 `-Duse-fields-location=<dir>` 时，不会获取或安装任何磁场图，磁场插件默认使用该目录。
显式指定的磁场 `dir` 参数仍然优先。当该选项为空时，磁场图来自 `magfield` git-lfs 子项目，
并安装在 `<prefix>/fields` 下；插件会相对于自身安装位置定位该目录。获取磁场图需要 git-lfs。

GEMC 本身也以相同方式查找。`-Duse-gemc-location=<dir>` 使用安装在该绝对路径前缀下的 GEMC
（要求存在 `lib/pkgconfig/gemc.pc`）。当该选项为空时，如果通过 pkg-config 或 `PATH` 上的
`gemc` 二进制文件找到已安装的 GEMC，则使用它；否则从源码构建 `gemc` 子项目。
构建过程绝不会构建 Geant4：它必须已经可用（配置前先加载 Geant4 模块），缺失时配置会失败。

下一版本推出：捆绑的 CCDB 通过 `ccdb_system_sqlite.patch` 使用系统 SQLite，避免使用其私有的
SQLite 合并源码版。已有的未打补丁的 CCDB 子项目检出副本必须在重新构建前刷新：

```shell
meson subprojects purge --confirm ccdb
```

然后配置一个干净的构建目录，让 Meson 获取 CCDB 并应用 wrap 补丁。

几何测试会运行每个已注册的 Python 系统，并写入合并后的 SQLite 数据库：

```shell
meson test -C build geometry_dc --print-errorlogs
sqlite3 build/clas12.db "select system, variation, run, count(*) from geometry group by 1,2,3;"
```

CLAS12 系统注册表目前位于 `meson.build`：

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

只有当 `geometry_src/<system>/<system>.py` 已准备好生成有效的 GEMC 几何时，才将探测器名称加入此列表。

<br/>

## CCDB 标定常数

探测器数字化插件（`dc`、`ecal`、`ft_cal`、`ft_hodo`、`ftof`、`ltcc`）从 CCDB 加载其标定常数。
默认情况下，它们连接到 JLab 数据库 `mysql://clas12reader@clasdb.jlab.org/clas12`；
设置 `CCDB_CONNECTION` 环境变量可指向其他服务器或本地 SQLite 快照
（`sqlite:///path/to/ccdb.sqlite`）。请注意，这是 CCDB 数据库，而不是 GEMC2 的
`clas12.sqlite` 探测器数据库——指向后者会导致标定常数为空。发生任何 CCDB 故障
（主机不可达、数据库错误、表为空）时，插件现在都会给出明确的错误信息并中止运行，
而不是静默地产生空的数字化输出。

### MariaDB 与 MySQL 连接器（macOS）

CCDB 客户端库在 macOS 上需要特别注意。`clas12reader` 账户使用 `mysql_native_password` 认证。
该方案基于 SHA1，因安全原因被弃用，Oracle 已在 MySQL 客户端库 9.0 版中将其**移除**。
因此，链接到 MySQL 9.x 的 CCDB 无法通过 clasdb 的身份认证，并在连接时失败——这是客户端库的限制，
而非 CCDB 的缺陷；任何 CCDB 源码改动都无法恢复库在编译时已移除的功能。
请安装仍然提供该功能的连接器：

```shell
brew install mariadb-connector-c   # preferred: maintained; supports native_password and caching_sha2_password
# or
brew install mysql-client@8.4      # Oracle LTS that still ships native_password
```

Meson 构建会自动选择 CCDB 连接器（`meson/meson.build`），按以下顺序优先选用：
`mariadb-connector-c`、`mysql-client@8.4`、`mysql-client`，最后是 `mysql`，
因此全新构建会链接到可用的客户端，无需手动重新链接。如果只安装了 MySQL 9.x，CCDB 仍能构建，
但连接 clasdb 时会失败并给出明确的错误信息，直到安装兼容的连接器
（或服务器账户迁移到 `caching_sha2_password`）。

还有另一个与此无关、仅涉及 MariaDB 的问题：`mariadb-connector-c` **默认强制使用 TLS**，
而 clasdb 不使用 SSL，因此未经额外配置的 MariaDB 构建会报错
`Error 2026 (SSL is required, but the
server does not support it)`。`ccdb` 子项目已通过 `subprojects/ccdb.wrap` 的 `diff_files` →
`subprojects/packagefiles/ccdb_ssl_no_enforce.patch` 应用补丁，在针对 MariaDB 构建时禁用 TLS 强制要求，
与 Oracle libmysqlclient 默认回退到明文连接的行为一致。该补丁受 `#ifdef LIBMARIADB` 条件保护，
因此对 MySQL/Oracle 客户端无影响（它们已移除该选项，且本来也不强制使用 TLS）。
应用该补丁后，`mariadb-connector-c` 即可连接到 clasdb，因此它是推荐的连接器。

<br/>

## 插件路径

CLAS12 系统插件以 `.gplugin` 共享库的形式安装在 `<prefix>/lib/` 下。GEMC 按以下顺序搜索插件：
`GEMC_PLUGIN_PATH`、自身的 `lib/` 和 `build/` 目录，然后是操作系统的动态库搜索路径
（Linux 上为 `LD_LIBRARY_PATH`，macOS 上为 `DYLD_LIBRARY_PATH`）。

最简单的设置是将 CLAS12 系统安装到 GEMC 自己的前缀下，这样 `.gplugin` 库就会位于 GEMC 已搜索的
`lib/` 目录中，无需设置运行时变量。GEMC 的前缀位于其 `bin/` 目录的上一级，
因此可根据 `command -v gemc` 的结果推导出来：

```shell
meson setup build --prefix="$(dirname "$(dirname "$(command -v gemc)")")"
meson install -C build
gemc dc.yaml
```

如果 GEMC 在 `PATH` 上，但配置了不同的前缀，Meson 会在配置时打印警告。这种情况下，
在运行 `gemc` 之前将 `GEMC_PLUGIN_PATH` 设置为 CLAS12 系统的库目录：

```shell
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
gemc dc.yaml
```

或者在命令行上传入：

```shell
gemc dc.yaml -plugin_path=/path/to/clas12-systems/lib
```

如果找不到插件，GEMC 会在错误信息旁打印 `GEMC_PLUGIN_PATH` 的当前值，以帮助诊断路径问题。

Meson 构建的安装前缀通过 pkg-config 文件提供插件目录信息：

```shell
# After: meson install -C build --prefix=/my/clas12/prefix
export PKG_CONFIG_PATH=/my/clas12/prefix/lib/pkgconfig:$PKG_CONFIG_PATH
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
```

<br/>


## 插件构建模型

系统插件使用注册表模式：

1. 探测器专属的 `geometry_src/<system>/plugin/meson.build` 向 `clas12_plugins` 追加字典。
2. 顶层的 `meson.build` 是唯一将这些条目转化为待安装共享库的地方。
3. 已安装的 GEMC 插件必须使用 `.gplugin` 后缀。

这使各 CLAS12 系统的插件安装保持一致，避免每个探测器各自实现一套构建逻辑。

<br/>

## 磁场

CLAS12 使用**基于场图的**磁场——即测量得到的螺线管和环形磁场图，而非解析模型。
磁场由 `plugins/field/` 下的 `gfieldclas12-cmag` 插件提供，该插件通过 David Heddle 的
[cMag](https://github.com/JeffersonLab/clas12-cmag) 库（`clas12-cmag` 子项目）
读取 CLAS12 螺线管和环形磁场的二进制场图，并返回每个步进点处的合成磁场。

磁场通过核心 GEMC 的通用 `gfields` 节点配置，用 `type: clas12-cmag` 选择此插件：

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

`global_field` 的值是已配置的磁场名称（上面的 `clas12`），而非螺线管或环形磁场图的名称。
场图名称和各场图的缩放因子属于 `gfields` 条目。这取代了 GEMC2 的
`global_field: Symm_solenoid_...:Symm_torus_...` 写法，以及旧的硬编码缩放目标
`binary_torus` / `binary_solenoid`，改用显式的 `torus`、`solenoid`、`torus_scale` 和
`solenoid_scale` 参数。

任何额外的标量键（各场图的位移、整体原点和旋转、`interpolation`）都会原样转发给插件。

场图来自 `magfield` git-lfs 子项目，并在 `meson
install` 期间复制到 `<prefix>/fields`（参见 `meson/install_fields.py`）；插件从安装在其旁边的
`fields` 目录（`<plugin_dir>/../fields`）读取它们。使用 `-Duse-fields-location=<dir>` 配置时，
会跳过该子项目，转而指向现有的场图目录（不会克隆或安装任何内容）。运行时无需设置
`FIELD` 或 `FIELD_DIR` 环境变量；显式的 `dir` 参数可以覆盖该位置。

<br/>

## 流式读出（SRO）

**下一版本推出。** CLAS12 系统可以输出 JLAB DAQ 二进制格式的流式读出（SRO）帧，
以替代普通事件输出，或与普通事件输出同时使用。GEMC 负责通用的 `sro` 流式输出器；
系统插件通过在其数字化器旁导出 `GSROImplementationFactory` 来提供有效载荷。
目前只有 **FT-Cal** 提供 SRO 有效载荷（通过 `ft_cal.gplugin`）；其他 FT 数字化器保持常规输出，
不提供 SRO 模型。

从命令行启用 SRO 时，需要选择 `sro` 流式输出器格式和提供有效载荷的插件，
并为采集设置非零的事件时间宽度：

```shell
gemc geometry_src/ft/ft.yaml -n=10000 \
  -gstreamer='[{format: sro, filename: ftcal_sro, implementation: ft_cal}]' \
  -eventTimeWidth='10*ns'
```

- `format: sro` 选择 GEMC 的 SRO 流式输出器；`implementation: ft_cal` 指定产生有效载荷的插件；
  `filename` 是输出文件的基本名称。
- `-eventTimeWidth` 设置采集时间轴上连续事件之间的间隔。其默认值为零，会导致 SRO 运行被拒绝，
  因此必须显式设置（上面的 `10*ns` 仅为示例，并非实测的 CLAS12 束流参数）。
  普通输出运行不需要该参数。
- 输出文件按机箱分别写入 `<basename>_r<resolved_run>_crate<crate>.ev`；
  重用同一基本名称和运行编号会覆盖这些文件。

FT 启动注册器 `ft.gplugin` 为 `ft_cal.gplugin` 提供选项，因此无需额外的选项节点。
转换表约定、工作单元时序模型（包括 `ft_cal_sro_min_signal_time`）、二进制布局和 `sro`
测试套件详见 [`geometry_src/sro/README.md`](geometry_src/sro/README.md)；
移植的 DAQ 定义及其来源记录在 [`geometry_src/sro/daq/README.md`](geometry_src/sro/daq/README.md) 中。

<br/>

## 验证

对于每个移植的探测器，应同时验证生成的数据库行和运行时几何行为。

推荐检查：

- 将生成的几何行与 [`gemc/clas12Tags`](https://github.com/gemc/clas12Tags) 中
  `geometry_source/<system>` 下的 GEMC2 参考数据进行比对。
- 确认名称、母体、描述、位置、旋转、实体、参数和材料在双方共有的字段上匹配。
- 验证运行编号和几何变体映射保存在系统目录内。
- 在运行完整的 Geant4 模拟之前，使用 PyVista 导出快速检查放置情况。
- 当探测器已有足够的几何可供检查时，以批处理模式和 GUI 模式运行 GEMC。

对于 DC，生成的默认几何应与以下内容逐词元匹配：

```text
https://github.com/gemc/clas12Tags/blob/main/geometry_source/dc/dc__geometry_default.txt
```

已知的 DC 预期行为：

- 默认运行编号为 `11`
- 所有 DC 几何体都使用 `g4placement_type = "passive"`
- 有序旋转保留为 `ordered: ...`
- 不支持已过时的 `original` 几何变体

<br/>

## CI 与发布

从下一版本起，所有容器工作流都将在 [`gemc/g4install`](https://github.com/gemc/g4install)
发布的 Geant4 基础镜像上从源码构建 GEMC 和 CLAS12 系统。
[工作流指南](.github/workflows/README.md) 说明了触发条件、部署授权、
跨仓库契约、权限、重试，以及预期会被跳过的运行。

相关自动化：

| 工作流                | 用途                                                                                |
|-----------------------|-------------------------------------------------------------------------------------|
| `deploy.yml`          | 在 Geant4 基础镜像中构建 GEMC 和 CLAS12 系统，然后发布镜像                           |
| `pr-docker-image.yml` | 为每个 PR 构建预览镜像，使审阅者无需本地构建即可测试该分支                           |
| `sanitize.yml`        | 对 CLAS12 系统运行启用 Sanitizer 的构建，但不对第三方子项目启用 Sanitizer           |
| `codeql.yml`          | 静态分析                                                                            |
| `doxygen.yml`         | 文档生成                                                                            |
| `binary_tarballs.yml` | 部署后重新构建 GEMC 并运行冒烟测试                                                   |
| `dev_release.yml`     | 开发版发布自动化                                                                    |

部署镜像使用以下命名模式：

```text
ghcr.io/gemc/clas12-systems:<gemc-tag>-<os>-<version>[-<arch>]
```

基础镜像来自：

```text
ghcr.io/gemc/g4install
```

每个拉取请求还会从其分支构建并发布一个可直接运行的多架构预览镜像
（`ghcr.io/gemc/clas12-systems:<gemc-tag>-almalinux-<version>-pr-<number>`），
使作者和审阅者无需本地构建即可测试——参见贡献指南中的
[预览容器镜像](CONTRIBUTING.md#preview-container-image)。该镜像会在拉取请求关闭时自动删除。

<br/>


## 文档

- [CI 工作流指南](.github/workflows/README.md)
- [GEMC 主页](https://gemc.github.io/home/)
- [Python API 仓库](https://github.com/gemc/pygemc)
- [GEMC2 / CLAS12 仓库](https://github.com/gemc/clas12Tags)

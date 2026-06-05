#!/usr/bin/env python3
"""Generate a CLAS12 systems deployment Dockerfile."""

import argparse


def create_dockerfile(base_image: str) -> str:
    return f"""FROM {base_image} AS final
LABEL maintainer="Maurizio Ungaro <ungaro@jlab.org>"

SHELL ["/bin/bash", "-c"]

COPY . /root/clas12-systems
RUN cd /root/clas12-systems \\
    && ./ci/setup_coatjava.sh \\
    && ./ci/build.sh \\
    && mkdir -p /opt/clas12-systems \\
    && cp -a install/. /opt/clas12-systems/

RUN printf '%s\\n' \\
    'export CLAS12_SYSTEMS=/opt/clas12-systems' \\
    'export PATH=${{CLAS12_SYSTEMS}}/bin:${{PATH}}' \\
    'export LD_LIBRARY_PATH=${{CLAS12_SYSTEMS}}/lib:${{LD_LIBRARY_PATH:-}}' \\
    'export PKG_CONFIG_PATH=${{CLAS12_SYSTEMS}}/lib/pkgconfig:${{PKG_CONFIG_PATH:-}}' \\
    >> /usr/local/bin/additional-entrycommands.sh

FROM scratch AS logs-export
COPY --from=final /root/clas12-systems/logs /logs
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-image", required=True, help="Published GEMC base image, e.g. ghcr.io/gemc/src:dev-fedora-44")
    args = parser.parse_args()
    print(create_dockerfile(args.base_image))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

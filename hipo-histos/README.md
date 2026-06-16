# hipo-histos

`hipo-histos` reads one HIPO file for a subsystem and writes ROOT histograms plus optional PNG plots.
For comparisons, pass exactly two HIPO files and `--compare-system <name>`; comparable 1D histograms are
overlaid into comparison PNGs.

Current subsystem support:

- `dc`: reads `MC::True` and `DC::tdc`; writes z-vertex rates by region, occupancy summaries by region, r-vs-z
  maps, and a layer-wire occupancy map.

Example:

```shell
hipo-histos dc input.hipo --label input -o dc_histos.root --plot-dir dc_plots
```

Comparison example:

```shell
hipo-histos --compare-system dc first.hipo second.hipo --label first --label second -o dc_compare.root
```

Useful options:

- `-n, --max-events N`: limit processed events per input file.
- `--compare-system NAME`: compare exactly two HIPO files for one subsystem, for example `dc`.
- `--time-window NS`: simulated event time window in ns. The DC default is 250 ns.
- `--no-plots`: write only the ROOT output file.

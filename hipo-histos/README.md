# hipo-histos

`hipo-histos` reads one HIPO file for a subsystem and writes ROOT histograms plus optional PNG plots.
For comparisons, pass exactly two HIPO files and `--compare-system <name>`. Comparable 1D histograms are
overlaid into comparison PNGs, while comparable 2D histograms are drawn as a three-panel canvas with the first
input, the second input, and the signed normalized bin difference `2*(N1-N2)/(N1+N2)`.

Current subsystem support:

- `dc`: reads `MC::True` and `DC::tdc`; writes a 3x3 summary PNG with occupancy, r-vs-z, and z-vertex rows
  across region columns R1, R2, and R3. It also writes the ROOT histograms, a TDC PNG with sector columns and
  region rows, a layer-wire occupancy map, and a comparison TDC PNG when comparing two files.
- `ec`: reads `ECAL::adc` and `ECAL::tdc`. The EC system has hipo layers 4..9 (EC inner U/V/W = 4/5/6, EC
  outer U/V/W = 7/8/9), each with 36 components. It writes a 6x6 ADC matrix PNG and a 6x6 TDC matrix PNG for
  each paired same-view layer set (U 4+7, V 5+8, W 6+9), plus higher-statistics TDC summaries summed by layer,
  view, and all EC channels. It also writes a component-vs-layer hit-count PNG with one pad per sector, plus
  generated primary phi/theta plots, and sector-summary diagnostics for generated primary phi, true EC-hit phi,
  and ADC row sector. When comparing two files, it writes the paired-view ADC/TDC comparison grids, the summed
  TDC comparison grids, the primary-kinematic and sector-summary comparisons, and per-sector hit-count
  comparison maps. The 2D channel maps store raw hit counts (not occupancy percentages) so the comparison runs
  on Poisson-distributed counts.
- `pcal`: reads the same `ECAL::adc` and `ECAL::tdc` banks, restricted to PCAL hipo layers 1..3. It writes
  summed ADC and TDC plots for U, V, W, and all PCAL channels, plus per-sector component-vs-layer hit-count
  maps and a global true-hit XY map. In comparison mode it writes the same summed ADC/TDC comparison plots and
  per-sector hit-count comparison maps.
- `ftof`: reads `FTOF::adc` and `FTOF::tdc`. FTOF has three panels (layer 1 = 1A with 23 paddles, 2 = 1B with
  62, 3 = 2 with 5). It writes ADC and TDC spectra per panel and for all panels combined, a paddle-vs-panel
  hit-count map per sector, and a global true-hit y-vs-x map (as in `ec`). In comparison mode the per-panel and
  combined ADC/TDC spectra are overlaid and the per-sector hit-count and y-vs-x maps are compared.

Example:

```shell
hipo-histos dc input.hipo --label input -o dc_histos.root --plot-dir dc_plots
hipo-histos ec input.hipo --label input -o ec_histos.root --plot-dir ec_plots
hipo-histos pcal input.hipo --label input -o pcal_histos.root --plot-dir pcal_plots
hipo-histos ftof input.hipo --label input -o ftof_histos.root --plot-dir ftof_plots
```

Comparison example:

```shell
hipo-histos --compare-system dc first.hipo second.hipo --label first --label second -o dc_compare.root
```

CI diagnostic example:

```shell
hipo-histos --compare-system dc first.hipo second.hipo --diagnostics --fail-on-diff --no-plots
```

The diagnostic mode runs by default when comparing two files. It compares the subsystem's registered 1D and
2D histograms and prints `passed` or `failed` for each histogram, along with the comparison statistics
(`chi2/ndf`, `ndf`, occupied bins, and median entries per occupied bin for each input). If the two inputs have
different event counts, the comparison is made after normalizing histograms by event count, matching the
plotting behavior. In 2D comparison plots, the third panel is not a content ratio; each bin is the symmetric
difference `2*(N1-N2)/(N1+N2)`, where `N1` and `N2` are the plotted bin values from the first and second input.
This keeps equal bins at 0 and bounds one-sided bins at +/-2. The 1D ROOT histograms store propagated bin
uncertainties for the written ROOT file and PNG plots. DC z-vertex and occupancy-summary errors are computed
from event-to-event fluctuations, not from individual hit counting errors, because hits in the same simulated
event are correlated.

For DC z-vertex and occupancy summaries, each simulated event first contributes an event-local bin total. The
z-vertex content is the raw number of simulated events in each z bin; comparison plots and diagnostics divide by
the number of processed events only when the two input files have different event counts. Occupancy content is
still normalized to percent. For a bin with event values `x_i`, the code stores `sum(x_i^2)` while the histogram
stores `sum(x_i)`. At finalization it computes the unbiased event variance
`(sum(x_i^2) - sum(x_i)^2 / N) / (N - 1)`. For raw z-vertex counts the displayed bin error is
`sqrt(N * variance)`. For normalized quantities the bin error is the standard error of the mean,
`sqrt(variance / N)`, times the same normalization scale used for the bin content. This is the important
distinction: the independent samples are events, not individual DC hits.

The default diagnostic parameters are quick regression-test cuts, not a formal statement that two independent
simulations came from different parent distributions. The default chi2/ndf limit is 5.0, which is deliberately
loose for ordinary bin-by-bin fluctuations while still catching large shape changes. The default relative
integral difference limit is 0.05, which catches large total rate or occupancy changes. The absolute single-bin
difference and minimum-entries gates are disabled by default because they are more analysis-specific. Short GEMC
samples can fail the 5% integral cut even when two runs are statistically compatible, especially after splitting
hits by detector region and sector. In that case, process more events, loosen `--max-integral-diff`, or inspect
the printed chi2/ndf and plots before treating the failure as a detector difference.

Useful options:

- `-n, --max-events N`: limit processed events per input file.
- `--compare-system NAME`: compare exactly two HIPO files for one subsystem, for example `dc`.
- `--diagnostics`: print `passed` or `failed` comparisons for registered histograms.
- `--fail-on-diff`: return a nonzero exit status when a diagnostic comparison does not pass.
- `--printn N`: set the progress print interval. Default: 10000.
- `--max-chi2-ndf VALUE`: set the maximum bin-by-bin chi2 divided by the number of compared bins. Default: 5.0.
- `--max-integral-diff VALUE`: set the maximum relative difference between the two histogram integrals. This
  tests total rate or occupancy independently of the bin-by-bin shape. Default: 0.05.
- `--max-integral-sigma VALUE`: a relative integral difference is only treated as a failure when it is also
  significant at more than `VALUE` Poisson sigma (`|Ia-Ib| / sqrt(errA^2 + errB^2)`, reported as
  `integral_sigma`). This stops low-statistics histograms, where a handful of counts gives a large relative
  swing, from failing on pure noise, while still catching genuine rate shifts in well-populated histograms.
  Set negative to disable (relative-difference-only behavior). Default: 5.0.
- `--min-chi2-bins N`: apply the chi2/ndf gate only when at least `N` bins survive the entries floor. With one
  or two surviving bins a single outlier inflates chi2/ndf, so such histograms are not failed on chi2 alone.
  Default: 3.
- `--max-bin-diff VALUE`: set an optional maximum absolute difference in any single bin. This catches isolated
  bin excursions even when the global chi2 and integral checks pass. Default: disabled.
- `--min-entries-per-bin VALUE`: ignore bins with fewer than `VALUE` raw entries. This is a
  statistical-soundness floor: low-statistics bins are dropped from the chi2, integral, and max-bin-diff
  checks (a bin is skipped when either histogram is below the floor), and the same bins are masked in 2D
  comparison plots. The number of skipped bins is reported as `skipped_bins`. Default: disabled; CI uses 10.
- `--interactive`: show the ROOT canvases and keep the GUI open after writing output.
- `--time-window NS`: simulated event time window in ns. The DC default is 250 ns.
- `--no-plots`: write only the ROOT output file.
- `--plot-format EXT`: plot file format/extension (default `png`). Use a vector format such as `pdf` or
  `svg` when running against a ROOT build without the `asimage` feature, which cannot write `png`/`jpg`
  (`SaveAs` silently produces nothing). The CI comparison uses `pdf`.

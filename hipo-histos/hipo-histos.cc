#include "common.h"
#include "histos_compare.h"
#include "subsystems.h"

#include "TApplication.h"
#include "TFile.h"
#include "TH1.h"
#include "TH2.h"

#include <array>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

void help()
{
    std::cout
        << "Usage: hipo-histos [options] <subsystem> <file.hipo>\n"
        << "       hipo-histos [options] --compare-system <subsystem> <file1.hipo> <file2.hipo>\n"
        << "\n"
        << "Options:\n"
        << "  --subsystem NAME       Subsystem to analyze. Currently supported: dc, ec.\n"
        << "  --compare-system NAME  Compare this subsystem using exactly two HIPO files.\n"
        << "  -o, --output FILE      ROOT output file. Default: hipo-histos.root.\n"
        << "  --plot-dir DIR         Directory for plots. Default: hipo-histos-plots.\n"
        << "  --plot-format EXT      Plot file format/extension. Default: png. Use pdf or svg\n"
        << "                         where ROOT lacks png support (no asimage feature).\n"
        << "  --label LABEL          Input label. May be specified once per input file.\n"
        << "  -n, --max-events N     Maximum events per input file. Default: all.\n"
        << "  --time-window NS       Simulated event time window in ns. Default: 250.\n"
        << "  --printn N             Progress print interval. Default: 10000.\n"
        << "  --interactive          Show ROOT canvases and keep the GUI open.\n"
        << "  --no-plots             Write ROOT output only.\n"
        << "  --diagnostics          Compare histograms and print passed/failed results.\n"
        << "  --fail-on-diff         Return nonzero if any diagnostic comparison does not pass.\n"
        << "  --max-chi2-ndf VALUE   Diagnostic chi2/ndf limit. Default: 5.\n"
        << "  --max-integral-diff V  Diagnostic relative integral difference limit. Default: 0.05.\n"
        << "  --max-bin-diff VALUE   Optional diagnostic max absolute bin difference limit.\n"
        << "  --min-entries-per-bin V Ignore bins with fewer than V raw entries in the\n"
        << "                         bin-by-bin comparison (statistical-soundness floor). Default: off.\n"
        << "  --max-integral-sigma V Only count an integral difference as a failure when it is also\n"
        << "                         significant at more than V Poisson sigma. Negative disables. Default: 5.\n"
        << "  --min-chi2-bins N      Apply the chi2/ndf gate only when at least N bins survive the\n"
        << "                         entries floor. Default: 3.\n"
        << "  -h, --help             Show this help.\n";
}

std::string require_value(int &index, int argc, char **argv, const std::string &option)
{
    if (index + 1 >= argc) {
        throw std::runtime_error("Missing value for " + option);
    }
    return argv[++index];
}

RunOptions parse_args(int argc, char **argv)
{
    RunOptions options;
    std::vector<std::string> positional;
    std::vector<std::string> labels;
    bool diagnostics_requested = false;

    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "-h" || arg == "--help") {
            help();
            std::exit(EXIT_SUCCESS);
        } else if (arg == "--subsystem") {
            options.subsystem = require_value(i, argc, argv, arg);
        } else if (arg == "--compare-system") {
            options.compare_system = require_value(i, argc, argv, arg);
        } else if (arg == "-o" || arg == "--output") {
            options.output_root = require_value(i, argc, argv, arg);
        } else if (arg == "--plot-dir") {
            options.plot_dir = require_value(i, argc, argv, arg);
        } else if (arg == "--plot-format") {
            options.plot_format = require_value(i, argc, argv, arg);
        } else if (arg == "--label") {
            labels.push_back(require_value(i, argc, argv, arg));
        } else if (arg == "-n" || arg == "--max-events") {
            options.max_events = std::stol(require_value(i, argc, argv, arg));
        } else if (arg == "--time-window") {
            options.time_window_ns = std::stod(require_value(i, argc, argv, arg));
        } else if (arg == "--printn") {
            options.print_interval = std::stoi(require_value(i, argc, argv, arg));
        } else if (arg == "--interactive") {
            options.interactive = true;
        } else if (arg == "--no-plots") {
            options.make_plots = false;
        } else if (arg == "--diagnostics") {
            diagnostics_requested = true;
            options.diagnostics = true;
        } else if (arg == "--fail-on-diff") {
            diagnostics_requested = true;
            options.diagnostics = true;
            options.fail_on_diff = true;
        } else if (arg == "--max-chi2-ndf") {
            options.compare_options.max_chi2_ndf = std::stod(require_value(i, argc, argv, arg));
        } else if (arg == "--max-integral-diff") {
            options.compare_options.max_rel_integral_diff = std::stod(require_value(i, argc, argv, arg));
        } else if (arg == "--max-bin-diff") {
            options.compare_options.max_abs_bin_diff = std::stod(require_value(i, argc, argv, arg));
        } else if (arg == "--min-entries-per-bin") {
            options.compare_options.min_entries_per_bin = std::stod(require_value(i, argc, argv, arg));
        } else if (arg == "--max-integral-sigma") {
            options.compare_options.max_integral_sigma = std::stod(require_value(i, argc, argv, arg));
        } else if (arg == "--min-chi2-bins") {
            options.compare_options.min_chi2_bins = std::stoi(require_value(i, argc, argv, arg));
        } else if (!arg.empty() && arg[0] == '-') {
            throw std::runtime_error("Unknown option: " + arg);
        } else {
            positional.push_back(arg);
        }
    }

    if (!positional.empty() && positional.front().find(".hipo") == std::string::npos) {
        options.subsystem = positional.front();
        positional.erase(positional.begin());
    }

    if (!options.compare_system.empty()) {
        options.subsystem = options.compare_system;
        if (positional.size() != 2) {
            throw std::runtime_error("--compare-system requires exactly two HIPO input files.");
        }
    } else if (positional.size() != 1) {
        throw std::runtime_error("Pass one HIPO input file, or use --compare-system with two HIPO files.");
    }

    if (options.interactive && !options.make_plots) {
        throw std::runtime_error("--interactive requires plots; remove --no-plots.");
    }
    if (diagnostics_requested && options.compare_system.empty()) {
        throw std::runtime_error("--diagnostics and --fail-on-diff require --compare-system.");
    }
    if (!options.compare_system.empty()) {
        options.diagnostics = true;
    }

    for (std::size_t i = 0; i < positional.size(); ++i) {
        InputSpec input;
        input.path = positional[i];
        input.label = i < labels.size() ? labels[i] : file_stem(positional[i]);
        options.inputs.push_back(input);
    }

    return options;
}

std::string comparison_header(const std::vector<SubsystemHistos *> &histos, bool normalize)
{
    if (histos.size() != 2) {
        return "";
    }

    if (!normalize) {
        return "Events: " + std::to_string(histos[0]->events()) + " in both files";
    }

    return "Events: " + histos[0]->label() + "=" + std::to_string(histos[0]->events()) + ", " +
           histos[1]->label() + "=" + std::to_string(histos[1]->events()) + "; normalized";
}

void save_comparison(const std::vector<SubsystemHistos *> &histos, const std::string &plot_dir,
                     const std::string &header, bool normalize, const DiagnosticSummary &diagnostics)
{
    if (histos.size() != 2) {
        return;
    }

    const auto names = histos.front()->comparison_names();
    std::vector<std::string> labels;
    for (const auto *histo_set : histos) {
        labels.push_back(histo_set->label());
    }

    for (std::size_t index = 0; index < names.size(); ++index) {
        std::vector<TH1 *> comparison;
        std::vector<std::unique_ptr<TH1>> scaled;
        for (const auto *histo_set : histos) {
            auto *histo = histo_set->comparison_histos()[index];
            const double scale = histo_set->comparison_plot_scale(names[index], normalize);
            if (histo != nullptr && scale != 1.0) {
                auto clone = std::unique_ptr<TH1>(static_cast<TH1 *>(histo->Clone()));
                clone->SetDirectory(nullptr);
                clone->Scale(scale);
                comparison.push_back(clone.get());
                scaled.push_back(std::move(clone));
            } else {
                comparison.push_back(histo);
            }
        }
        const bool log_y = names[index].find("z_vertex") != std::string::npos;
        const auto status = diagnostics.statuses.find(names[index]);
        const bool has_status = status != diagnostics.statuses.end();
        const bool passed = has_status && status->second;
        draw_overlay(comparison, labels, names[index], plot_file(plot_dir, "compare_" + names[index]), log_y,
                     header, has_status, passed);
    }

    const auto names_2d = histos.front()->comparison_2d_names();
    if (names_2d.empty()) {
        return;
    }
    const std::vector<TH2 *> histos_2d_a = histos[0]->comparison_2d_histos();
    const std::vector<TH2 *> histos_2d_b = histos[1]->comparison_2d_histos();
    if (names_2d.size() != histos_2d_a.size() || names_2d.size() != histos_2d_b.size()) {
        throw std::runtime_error("Subsystem returned inconsistent 2D comparison histogram lists.");
    }

    for (std::size_t index = 0; index < names_2d.size(); ++index) {
        std::vector<TH2 *> comparison;
        std::vector<std::unique_ptr<TH2>> scaled;
        const std::array<TH2 *, 2> source_histos = {histos_2d_a[index], histos_2d_b[index]};
        for (std::size_t histo_index = 0; histo_index < histos.size(); ++histo_index) {
            auto *histo = source_histos[histo_index];
            if (histo == nullptr) {
                throw std::runtime_error("Subsystem returned a null 2D comparison histogram: " +
                                         names_2d[index]);
            }
            const double scale = histos[histo_index]->comparison_plot_scale(names_2d[index], normalize);
            if (histo != nullptr && scale != 1.0) {
                auto clone = std::unique_ptr<TH2>(static_cast<TH2 *>(histo->Clone()));
                clone->SetDirectory(nullptr);
                clone->Scale(scale);
                comparison.push_back(clone.get());
                scaled.push_back(std::move(clone));
            } else {
                comparison.push_back(histo);
            }
        }

        const auto status = diagnostics.statuses.find(names_2d[index]);
        const bool has_status = status != diagnostics.statuses.end();
        const bool passed = has_status && status->second;
        draw_2d_comparison(comparison[0], comparison[1], labels, names_2d[index],
                           plot_file(plot_dir, "compare_" + names_2d[index]), header,
                           has_status, passed);
    }
}

DiagnosticSummary run_diagnostics(const std::vector<SubsystemHistos *> &histos, const RunOptions &options,
                                  bool normalize)
{
    DiagnosticSummary summary;
    if (histos.size() != 2) {
        return summary;
    }

    std::cout << "Diagnostic histogram comparison";
    if (normalize) {
        std::cout << " (normalized by event count)";
    }
    std::cout << ":\n";

    const auto names_1d = histos.front()->diagnostic_names();
    const auto histos_1d_a = histos[0]->diagnostic_histos();
    const auto histos_1d_b = histos[1]->diagnostic_histos();
    if (names_1d.size() != histos_1d_a.size() || names_1d.size() != histos_1d_b.size()) {
        throw std::runtime_error("Subsystem returned inconsistent 1D diagnostic histogram lists.");
    }

    for (std::size_t index = 0; index < names_1d.size(); ++index) {
        if (histos_1d_a[index] == nullptr || histos_1d_b[index] == nullptr) {
            throw std::runtime_error("Subsystem returned a null 1D diagnostic histogram: " +
                                     names_1d[index]);
        }
        auto compare_options = options.compare_options;
        compare_options.scale_a = histos[0]->diagnostic_scale(names_1d[index], normalize);
        compare_options.scale_b = histos[1]->diagnostic_scale(names_1d[index], normalize);
        auto result = compare_th1(*histos_1d_a[index], *histos_1d_b[index], compare_options);
        result.name = names_1d[index];
        print_compare_result(result, std::cout);
        summary.statuses[result.name] = result.passed;
        summary.passed = summary.passed && result.passed;
    }

    const auto names_2d = histos.front()->diagnostic_2d_names();
    const auto histos_2d_a = histos[0]->diagnostic_2d_histos();
    const auto histos_2d_b = histos[1]->diagnostic_2d_histos();
    if (names_2d.size() != histos_2d_a.size() || names_2d.size() != histos_2d_b.size()) {
        throw std::runtime_error("Subsystem returned inconsistent 2D diagnostic histogram lists.");
    }

    for (std::size_t index = 0; index < names_2d.size(); ++index) {
        if (histos_2d_a[index] == nullptr || histos_2d_b[index] == nullptr) {
            throw std::runtime_error("Subsystem returned a null 2D diagnostic histogram: " +
                                     names_2d[index]);
        }
        auto compare_options = options.compare_options;
        compare_options.scale_a = histos[0]->diagnostic_scale(names_2d[index], normalize);
        compare_options.scale_b = histos[1]->diagnostic_scale(names_2d[index], normalize);
        auto result = compare_th2(*histos_2d_a[index], *histos_2d_b[index], compare_options);
        result.name = names_2d[index];
        print_compare_result(result, std::cout);
        summary.statuses[result.name] = result.passed;
        summary.passed = summary.passed && result.passed;
    }

    return summary;
}

bool run_subsystem(const RunOptions &options)
{
    auto subsystem = make_subsystem(options.subsystem);
    std::vector<std::unique_ptr<SubsystemHistos>> owned_histos;
    std::vector<SubsystemHistos *> histo_views;

    for (const auto &input : options.inputs) {
        auto histos = subsystem->create_histos(input, options);
        std::cout << "Processing " << input.path << " as " << input.label << "\n";
        subsystem->process_file(options, input, *histos);
        histo_views.push_back(histos.get());
        owned_histos.push_back(std::move(histos));
    }

    const bool compare = !options.compare_system.empty();
    const bool normalize_comparison = compare && histo_views.size() == 2 &&
                                      histo_views[0]->events() != histo_views[1]->events();
    const auto compare_header = comparison_header(histo_views, normalize_comparison);
    DiagnosticSummary diagnostics;

    // Finalization applies content normalization and replaces DC z/occupancy bin errors with event-level
    // standard errors. Diagnostics must run after this step so chi2 uses the same propagated errors as plots.
    for (const auto &histos : owned_histos) {
        histos->finalize();
    }

    if (options.diagnostics && !normalize_comparison) {
        diagnostics = run_diagnostics(histo_views, options, false);
    }
    if (options.diagnostics && normalize_comparison) {
        diagnostics = run_diagnostics(histo_views, options, true);
    }

    if (options.make_plots && compare && !normalize_comparison) {
        ensure_directory(options.plot_dir);
        save_comparison(histo_views, options.plot_dir, compare_header, false, diagnostics);
        subsystem->save_comparison_plots(histo_views, options.plot_dir, compare_header, false,
                                         diagnostics);
    }

    TFile output(options.output_root.c_str(), "RECREATE");
    if (output.IsZombie()) {
        throw std::runtime_error("Could not create ROOT output file: " + options.output_root);
    }

    for (const auto &histos : owned_histos) {
        histos->write(&output);
    }
    output.Write();
    output.Close();

    if (options.make_plots) {
        ensure_directory(options.plot_dir);
        for (const auto &histos : owned_histos) {
            histos->save_plots(options.plot_dir);
        }
        if (compare && normalize_comparison) {
            save_comparison(histo_views, options.plot_dir, compare_header, true, diagnostics);
            subsystem->save_comparison_plots(histo_views, options.plot_dir, compare_header, true,
                                             diagnostics);
        }
    }

    return diagnostics.passed;
}

} // namespace

int main(int argc, char **argv)
{
    try {
        const auto options = parse_args(argc, argv);
        int root_argc = 1;
        char app_name[] = "hipo-histos";
        char *root_argv[] = {app_name};
        std::unique_ptr<TApplication> root_app;

        if (options.interactive) {
            root_app = std::make_unique<TApplication>("hipo-histos", &root_argc, root_argv);
        }

        set_root_style(options.interactive);
        set_plot_extension(options.plot_format);
        const bool diagnostics_passed = run_subsystem(options);
        std::cout << "Wrote " << options.output_root << "\n";
        if (options.make_plots) {
            std::cout << "Wrote plots under " << options.plot_dir << "\n";
        }
        if (options.diagnostics) {
            std::cout << "Diagnostics: " << (diagnostics_passed ? "passed" : "failed") << "\n";
        }
        if (root_app != nullptr) {
            std::cout << "Interactive ROOT mode is active. Close the ROOT windows to exit.\n";
            root_app->Run();
        }
        if (options.fail_on_diff && !diagnostics_passed) {
            return EXIT_FAILURE;
        }
    } catch (const std::exception &error) {
        std::cerr << "hipo-histos: " << error.what() << "\n\n";
        help();
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}

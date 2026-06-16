#include "common.h"
#include "subsystems.h"

#include "TFile.h"

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
        << "  --subsystem NAME       Subsystem to analyze. Currently supported: dc.\n"
        << "  --compare-system NAME  Compare this subsystem using exactly two HIPO files.\n"
        << "  -o, --output FILE      ROOT output file. Default: hipo-histos.root.\n"
        << "  --plot-dir DIR         Directory for PNG plots. Default: hipo-histos-plots.\n"
        << "  --label LABEL          Input label. May be specified once per input file.\n"
        << "  -n, --max-events N     Maximum events per input file. Default: all.\n"
        << "  --time-window NS       Simulated event time window in ns. Default: 250.\n"
        << "  --printn N             Progress print interval. Default: 10000.\n"
        << "  --no-plots             Write ROOT output only.\n"
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
        } else if (arg == "--label") {
            labels.push_back(require_value(i, argc, argv, arg));
        } else if (arg == "-n" || arg == "--max-events") {
            options.max_events = std::stol(require_value(i, argc, argv, arg));
        } else if (arg == "--time-window") {
            options.time_window_ns = std::stod(require_value(i, argc, argv, arg));
        } else if (arg == "--printn") {
            options.print_interval = std::stoi(require_value(i, argc, argv, arg));
        } else if (arg == "--no-plots") {
            options.make_plots = false;
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

    for (std::size_t i = 0; i < positional.size(); ++i) {
        InputSpec input;
        input.path = positional[i];
        input.label = i < labels.size() ? labels[i] : file_stem(positional[i]);
        options.inputs.push_back(input);
    }

    return options;
}

void save_comparison(const std::vector<SubsystemHistos *> &histos, const std::string &plot_dir)
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
        for (const auto *histo_set : histos) {
            comparison.push_back(histo_set->comparison_histos()[index]);
        }
        const bool log_y = names[index].find("z_vertex") != std::string::npos;
        draw_overlay(comparison, labels, names[index], plot_dir + "/compare_" + names[index] + ".png", log_y);
    }
}

void run_subsystem(const RunOptions &options)
{
    auto subsystem = make_subsystem(options.subsystem);
    std::vector<std::unique_ptr<SubsystemHistos>> owned_histos;
    std::vector<SubsystemHistos *> histo_views;

    for (const auto &input : options.inputs) {
        auto histos = subsystem->create_histos(input, options);
        std::cout << "Processing " << input.path << " as " << input.label << "\n";
        subsystem->process_file(options, input, *histos);
        histos->finalize();
        histo_views.push_back(histos.get());
        owned_histos.push_back(std::move(histos));
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
        if (!options.compare_system.empty()) {
            save_comparison(histo_views, options.plot_dir);
        }
    }
}

} // namespace

int main(int argc, char **argv)
{
    try {
        set_root_style();
        const auto options = parse_args(argc, argv);
        run_subsystem(options);
        std::cout << "Wrote " << options.output_root << "\n";
        if (options.make_plots) {
            std::cout << "Wrote plots under " << options.plot_dir << "\n";
        }
    } catch (const std::exception &error) {
        std::cerr << "hipo-histos: " << error.what() << "\n\n";
        help();
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}

#ifndef HIPO_HISTOS_COMMON_H
#define HIPO_HISTOS_COMMON_H

#include <map>
#include <string>
#include <vector>

class TCanvas;
class TDirectory;
class TH1;
class TH2;

#include "histos_compare.h"

struct InputSpec {
    std::string path;
    std::string label;
};

struct RunOptions {
    std::string subsystem = "dc";
    std::string compare_system;
    std::vector<InputSpec> inputs;
    std::string output_root = "hipo-histos.root";
    std::string plot_dir = "hipo-histos-plots";
    std::string plot_format = "png";
    long max_events = -1;
    int print_interval = 10000;
    double time_window_ns = 250.0;
    bool make_plots = true;
    bool interactive = false;
    bool diagnostics = false;
    bool fail_on_diff = false;
    HistoCompareOptions compare_options;
};

struct DiagnosticSummary {
    bool passed = true;
    std::map<std::string, bool> statuses;
};

class SubsystemHistos {
  public:
    virtual ~SubsystemHistos() = default;

    virtual const std::string &label() const = 0;
    virtual long events() const = 0;
    virtual void finalize() = 0;
    virtual void write(TDirectory *directory) const = 0;
    virtual void save_plots(const std::string &plot_dir) const = 0;
    virtual std::vector<TH1 *> comparison_histos() const = 0;
    virtual std::vector<std::string> comparison_names() const = 0;
    virtual double comparison_plot_scale(const std::string &name, bool normalize) const;
    virtual std::vector<TH2 *> comparison_2d_histos() const { return {}; }
    virtual std::vector<std::string> comparison_2d_names() const { return {}; }
    virtual std::vector<TH1 *> diagnostic_histos() const { return comparison_histos(); }
    virtual std::vector<std::string> diagnostic_names() const { return comparison_names(); }
    virtual std::vector<TH2 *> diagnostic_2d_histos() const { return comparison_2d_histos(); }
    virtual std::vector<std::string> diagnostic_2d_names() const { return comparison_2d_names(); }
    virtual double diagnostic_scale(const std::string &name, bool normalize) const;
};

std::string file_stem(const std::string &path);
std::string sanitize_root_name(const std::string &name);
void ensure_directory(const std::string &path);
// Plot output format (file extension) used by all SaveAs calls. Default "png"; ROOT builds
// without the asimage feature cannot write png/jpg and need a vector format (e.g. pdf, svg).
void set_plot_extension(const std::string &ext);
std::string plot_file(const std::string &dir, const std::string &stem);
void set_root_style(bool interactive);
TCanvas *make_canvas(const std::string &name, const std::string &title, int width = 1100, int height = 800);
void draw_canvas_header(TCanvas *canvas, const std::string &header);
void draw_status_label(bool passed);
void show_canvas(TCanvas *canvas);
void draw_overlay(const std::vector<TH1 *> &histos, const std::vector<std::string> &labels,
                  const std::string &title, const std::string &output_path, bool log_y = false,
                  const std::string &header = "", bool has_status = false, bool passed = false);
void draw_2d(TH2 *histo, const std::string &title, const std::string &output_path);
void draw_2d_comparison(TH2 *first, TH2 *second, const std::vector<std::string> &labels,
                        const std::string &title, const std::string &output_path,
                        const std::string &header = "", bool has_status = false,
                        bool passed = false);

#endif

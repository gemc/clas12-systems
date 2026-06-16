#ifndef HIPO_HISTOS_COMMON_H
#define HIPO_HISTOS_COMMON_H

#include <string>
#include <vector>

class TCanvas;
class TDirectory;
class TH1;
class TH2;

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
    long max_events = -1;
    int print_interval = 10000;
    double time_window_ns = 250.0;
    bool make_plots = true;
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
};

std::string file_stem(const std::string &path);
std::string sanitize_root_name(const std::string &name);
void ensure_directory(const std::string &path);
void set_root_style();
TCanvas *make_canvas(const std::string &name, const std::string &title, int width = 1100, int height = 800);
void draw_overlay(const std::vector<TH1 *> &histos, const std::vector<std::string> &labels,
                  const std::string &title, const std::string &output_path, bool log_y = false);
void draw_2d(TH2 *histo, const std::string &title, const std::string &output_path);

#endif

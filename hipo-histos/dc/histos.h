#ifndef HIPO_HISTOS_DC_HISTOS_H
#define HIPO_HISTOS_DC_HISTOS_H

#include "common.h"
#include "subsystems.h"

#include "hipo4/reader.h"
#include "TH1D.h"
#include "TH2D.h"

#include <array>
#include <memory>
#include <string>
#include <vector>

class TDirectory;

class DCHistos final : public SubsystemHistos {
  public:
    DCHistos(const std::string &label, double time_window_ns);

    const std::string &label() const override { return label_; }
    long events() const override { return events_; }

    void fill(const hipo::bank &mc_true, hipo::bank &dc_tdc,
              const hipo::bank &mc_particle);
    void finalize() override;
    void write(TDirectory *directory) const override;
    void save_plots(const std::string &plot_dir) const override;

    std::vector<TH1 *> comparison_histos() const override;
    std::vector<std::string> comparison_names() const override;
    double comparison_plot_scale(const std::string &name, bool normalize) const override;
    std::vector<TH2 *> comparison_2d_histos() const override;
    std::vector<std::string> comparison_2d_names() const override;
    std::vector<TH1 *> diagnostic_histos() const override;
    std::vector<std::string> diagnostic_names() const override;
    double diagnostic_scale(const std::string &name, bool normalize) const override;
    TH1D *tdc_histo(int region, int sector) const;

  private:
    static constexpr int kDetectorId = 6;
    static constexpr int kRegions = 3;
    static constexpr int kSectors = 6;
    static constexpr int kLayers = 36;
    static constexpr int kWires = 112;
    static constexpr int kBins = 300;
    static constexpr int kZBins = kBins / 2;
    static constexpr int kXYBins = 100;
    static constexpr double kXYRange = 5000.0;

    std::string label_;
    std::string safe_label_;
    double time_window_ns_ = 250.0;
    long events_ = 0;
    bool normalized_ = false;
    bool warned_local_layers_ = false;

    std::array<double, kRegions> thresholds_mev_ = {0.0001, 0.0001, 0.0001};
    std::array<double, kRegions> electronics_window_ns_ = {250.0, 500.0, 500.0};
    std::array<double, kRegions> z_min_ = {-200.0, -200.0, -300.0};
    std::array<double, kRegions> z_max_ = {3000.0, 5000.0, 8000.0};
    std::array<double, kRegions> r_min_ = {-50.0, -100.0, -100.0};
    std::array<double, kRegions> r_max_ = {1950.0, 3000.0, 4800.0};

    std::array<std::unique_ptr<TH1D>, kRegions> z_vertex_;
    std::array<std::array<double, kZBins>, kRegions> z_vertex_event_sum_sq_ = {};
    std::array<std::unique_ptr<TH1D>, kRegions> occupancy_summary_;
    std::array<std::array<double, kSectors>, kRegions> occupancy_event_sum_sq_ = {};
    std::array<std::array<std::unique_ptr<TH1D>, kSectors>, kRegions> tdc_;
    std::array<std::unique_ptr<TH2D>, kRegions> rz_vertex_;
    std::unique_ptr<TH2D> xy_global_;
    std::unique_ptr<TH2D> layer_wire_;
    std::unique_ptr<TH1D> mc_particle_momentum_;
    std::unique_ptr<TH1D> mc_particle_theta_;
    std::unique_ptr<TH1D> mc_particle_phi_;

    void book();
    void fill_mc_particles(const hipo::bank &mc_particle);
};

class DCSubsystem final : public Subsystem {
  public:
    const std::string &name() const override { return name_; }
    std::unique_ptr<SubsystemHistos> create_histos(const InputSpec &input,
                                                   const RunOptions &options) const override;
    void process_file(const RunOptions &options, const InputSpec &input,
                      SubsystemHistos &histos) const override;
    void save_comparison_plots(const std::vector<SubsystemHistos *> &histos,
                               const std::string &plot_dir, const std::string &header,
                               bool normalize, const DiagnosticSummary &diagnostics) const override;

  private:
    std::string name_ = "dc";
};

#endif

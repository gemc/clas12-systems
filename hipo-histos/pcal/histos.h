#ifndef HIPO_HISTOS_PCAL_HISTOS_H
#define HIPO_HISTOS_PCAL_HISTOS_H

#include "common.h"
#include "subsystems.h"

#include "TH1D.h"
#include "TH2D.h"
#include "hipo4/reader.h"

#include <array>
#include <memory>
#include <string>
#include <vector>

class TDirectory;

class PCALHistos final : public SubsystemHistos {
  public:
    explicit PCALHistos(const std::string &label);

    const std::string &label() const override { return label_; }
    long events() const override { return events_; }

    void fill(const hipo::bank &ecal_adc, const hipo::bank &ecal_tdc, const hipo::bank &mc_true,
              const hipo::bank &mc_particle);
    void finalize() override;
    void write(TDirectory *directory) const override;
    void save_plots(const std::string &plot_dir) const override;

    std::vector<TH1 *> comparison_histos() const override;
    std::vector<std::string> comparison_names() const override;
    std::vector<TH2 *> comparison_2d_histos() const override;
    std::vector<std::string> comparison_2d_names() const override;
    std::vector<TH1 *> diagnostic_histos() const override;
    std::vector<std::string> diagnostic_names() const override;
    double diagnostic_scale(const std::string &name, bool normalize) const override;

    TH1D *adc_histo(int layer_index, int component) const;
    TH1D *tdc_histo(int layer_index, int component) const;
    TH1D *adc_layer_histo(int layer_index) const;
    TH1D *adc_all_histo() const;
    TH1D *tdc_layer_histo(int layer_index) const;
    TH1D *tdc_all_histo() const;
    TH1D *edep_all_histo() const;

    static constexpr int layers() { return kLayers; }
    static constexpr int components() { return kComponents; }
    static int layer_number(int layer_index) { return kLayerMin + layer_index; }
    static std::string view_name(int layer_index);

  private:
    static constexpr int kSectors = 6;
    static constexpr int kLayerMin = 1;
    static constexpr int kLayerMax = 3;
    static constexpr int kLayers = kLayerMax - kLayerMin + 1;
    static constexpr int kComponents = 68;
    // The ecal digitization plugin writes both EC and PCAL true hits with the ecal detector id.
    static constexpr int kEcalDetectorId = 7;
    static constexpr int kXYBins = 100;
    static constexpr double kXYRange = 5000.0;
    static constexpr int kAdcBins = 100;
    static constexpr double kAdcMax = 35000.0;
    static constexpr int kTdcBins = 100;
    static constexpr double kTdcMax = 6000.0;
    static constexpr int kEdepBins = 200;
    static constexpr double kEdepMax = 100.0;

    std::string label_;
    std::string safe_label_;
    long events_ = 0;
    bool normalized_ = false;

    std::array<std::array<std::unique_ptr<TH1D>, kComponents>, kLayers> adc_;
    std::array<std::array<std::unique_ptr<TH1D>, kComponents>, kLayers> tdc_;
    std::array<std::unique_ptr<TH1D>, kLayers> adc_layer_;
    std::unique_ptr<TH1D> adc_all_;
    std::array<std::unique_ptr<TH1D>, kLayers> tdc_layer_;
    std::unique_ptr<TH1D> tdc_all_;
    std::unique_ptr<TH1D> edep_all_;
    std::unique_ptr<TH1D> primary_phi_;
    std::unique_ptr<TH1D> primary_theta_;
    std::unique_ptr<TH1D> primary_phi_sector_;
    std::unique_ptr<TH1D> true_phi_sector_;
    std::unique_ptr<TH1D> adc_sector_;
    std::array<std::unique_ptr<TH2D>, kSectors> occupancy_;
    std::unique_ptr<TH2D> xy_global_;

    void book();
    static int phi_sector(double x, double y);
};

class PCALSubsystem final : public Subsystem {
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
    std::string name_ = "pcal";
};

#endif

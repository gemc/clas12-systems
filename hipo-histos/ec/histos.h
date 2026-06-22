#ifndef HIPO_HISTOS_EC_HISTOS_H
#define HIPO_HISTOS_EC_HISTOS_H

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

class ECHistos final : public SubsystemHistos {
  public:
    explicit ECHistos(const std::string &label);

    const std::string &label() const override { return label_; }
    long events() const override { return events_; }

    void fill(const hipo::bank &ecal_adc, const hipo::bank &ecal_tdc, const hipo::bank &mc_true);
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

    TH1D *adc_histo(int component) const;
    TH1D *tdc_histo(int component) const;

    // The "first EC layer" rendered as the 6x6 ADC/TDC component matrices.
    static constexpr int first_layer() { return kFirstLayer; }

  private:
    static constexpr int kSectors = 6;
    static constexpr int kLayerMin = 4;
    static constexpr int kLayerMax = 9;
    static constexpr int kLayers = kLayerMax - kLayerMin + 1;
    static constexpr int kComponents = 36;
    static constexpr int kMatrix = 6;
    // The EC system has no hipo layers 1..3 (those are PCAL). The first EC layer is the inner U view
    // (hipo layer 4) and has exactly 36 components, i.e. a 6x6 matrix.
    static constexpr int kFirstLayer = kLayerMin;
    // ecal hit type in the GEMC hipo detector-id map (MC::True "detector" column).
    static constexpr int kEcalDetectorId = 7;
    static constexpr int kXYBins = 100;
    static constexpr double kXYRange = 5000.0;
    static constexpr int kAdcBins = 100;
    static constexpr double kAdcMax = 35000.0;
    static constexpr int kTdcBins = 100;
    static constexpr double kTdcMax = 6000.0;

    std::string label_;
    std::string safe_label_;
    long events_ = 0;
    bool normalized_ = false;

    std::array<std::unique_ptr<TH1D>, kComponents> adc_;
    std::array<std::unique_ptr<TH1D>, kComponents> tdc_;
    std::array<std::unique_ptr<TH2D>, kSectors> occupancy_;
    std::unique_ptr<TH2D> xy_global_;

    void book();
};

class ECSubsystem final : public Subsystem {
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
    std::string name_ = "ec";
};

#endif

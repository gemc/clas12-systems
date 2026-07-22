#ifndef HIPO_HISTOS_LTCC_HISTOS_H
#define HIPO_HISTOS_LTCC_HISTOS_H

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

class LTCCHistos final : public SubsystemHistos {
  public:
    explicit LTCCHistos(const std::string &label);

    const std::string &label() const override { return label_; }
    long events() const override { return events_; }

    void fill(const hipo::bank &ltcc_adc, const hipo::bank &ltcc_tdc, const hipo::bank &mc_true);
    void finalize() override;
    void write(TDirectory *directory) const override;
    void save_plots(const std::string &plot_dir) const override;

    std::vector<TH1 *> comparison_histos() const override;
    std::vector<std::string> comparison_names() const override;
    std::vector<TH2 *> comparison_2d_histos() const override;
    std::vector<std::string> comparison_2d_names() const override;

    static std::string side_name(int side_index);

  private:
    static constexpr int kSectors = 6;
    static constexpr int kSides = 2;              // half sector: 1 or 2 (LTCC::adc "layer")
    static constexpr int kSegments = 18;          // PMT segment per half sector (LTCC::adc "component")
    // LTCC hit type in the GEMC hipo detector-id map (MC::True "detector" column,
    // org.jlab.detector.base.DetectorType.LTCC).
    static constexpr int kLtccDetectorId = 16;
    static constexpr int kAdcBins = 100;
    static constexpr double kAdcMax = 4000.0;
    // LTCC digitized TDC (hit time / tdc_conv) is positive, so the axis starts at the origin.
    static constexpr int kTdcBins = 100;
    static constexpr double kTdcMax = 4000.0;
    static constexpr int kXYBins = 100;
    static constexpr double kXYRange = 5000.0;
    // True hit times (MC::True avgT) peak at the ~7 ns flight time to the mirrors; late secondaries
    // fall in the overflow bin, which both inputs accumulate identically.
    static constexpr int kTrueTimeBins = 100;
    static constexpr double kTrueTimeMax = 100.0;

    std::string label_;
    std::string safe_label_;
    long events_ = 0;

    std::array<std::unique_ptr<TH1D>, kSides> adc_side_;
    std::array<std::unique_ptr<TH1D>, kSides> tdc_side_;
    std::unique_ptr<TH1D> adc_all_;
    std::unique_ptr<TH1D> tdc_all_;
    std::array<std::unique_ptr<TH2D>, kSectors> occupancy_;
    std::unique_ptr<TH2D> xy_global_;
    std::unique_ptr<TH1D> true_time_;

    void book();
};

class LTCCSubsystem final : public Subsystem {
  public:
    const std::string &name() const override { return name_; }
    std::unique_ptr<SubsystemHistos> create_histos(const InputSpec &input,
                                                   const RunOptions &options) const override;
    void process_file(const RunOptions &options, const InputSpec &input,
                      SubsystemHistos &histos) const override;

  private:
    std::string name_ = "ltcc";
};

#endif

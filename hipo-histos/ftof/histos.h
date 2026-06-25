#ifndef HIPO_HISTOS_FTOF_HISTOS_H
#define HIPO_HISTOS_FTOF_HISTOS_H

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

class FTOFHistos final : public SubsystemHistos {
  public:
    explicit FTOFHistos(const std::string &label);

    const std::string &label() const override { return label_; }
    long events() const override { return events_; }

    void fill(const hipo::bank &ftof_adc, const hipo::bank &ftof_tdc, const hipo::bank &mc_true);
    void finalize() override;
    void write(TDirectory *directory) const override;
    void save_plots(const std::string &plot_dir) const override;

    std::vector<TH1 *> comparison_histos() const override;
    std::vector<std::string> comparison_names() const override;
    std::vector<TH2 *> comparison_2d_histos() const override;
    std::vector<std::string> comparison_2d_names() const override;

    static std::string panel_name(int panel_index);

  private:
    static constexpr int kSectors = 6;
    static constexpr int kPanels = 3;             // 1 = 1A, 2 = 1B, 3 = 2
    static constexpr int kMaxPaddles = 62;        // panel 1B has the most paddles
    // FTOF hit type in the GEMC hipo detector-id map (MC::True "detector" column).
    static constexpr int kFtofDetectorId = 12;
    static constexpr int kAdcBins = 100;
    static constexpr double kAdcMax = 8000.0;
    // FTOF TDC values are offset-dominated and largely negative, so the axis spans a window centered
    // below zero rather than starting at the origin.
    static constexpr int kTdcBins = 100;
    static constexpr double kTdcMin = -6000.0;
    static constexpr double kTdcMax = 2000.0;
    static constexpr int kXYBins = 100;
    static constexpr double kXYRange = 5000.0;

    static constexpr std::array<int, kPanels> kPaddles = {23, 62, 5};

    std::string label_;
    std::string safe_label_;
    long events_ = 0;

    std::array<std::unique_ptr<TH1D>, kPanels> adc_panel_;
    std::array<std::unique_ptr<TH1D>, kPanels> tdc_panel_;
    std::unique_ptr<TH1D> adc_all_;
    std::unique_ptr<TH1D> tdc_all_;
    std::array<std::unique_ptr<TH2D>, kSectors> occupancy_;
    std::unique_ptr<TH2D> xy_global_;

    void book();
};

class FTOFSubsystem final : public Subsystem {
  public:
    const std::string &name() const override { return name_; }
    std::unique_ptr<SubsystemHistos> create_histos(const InputSpec &input,
                                                   const RunOptions &options) const override;
    void process_file(const RunOptions &options, const InputSpec &input,
                      SubsystemHistos &histos) const override;

  private:
    std::string name_ = "ftof";
};

#endif

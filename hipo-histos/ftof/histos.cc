#include "ftof/histos.h"

#include "TCanvas.h"
#include "TDirectory.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TLatex.h"
#include "TPad.h"

#include <iostream>
#include <stdexcept>
#include <string>

namespace {

void draw_pad_label(const std::string &label)
{
    TLatex latex;
    latex.SetNDC(true);
    latex.SetTextFont(43);
    latex.SetTextSize(16);
    latex.DrawLatex(0.14, 0.92, label.c_str());
}

void draw_spectra(TCanvas *canvas, const std::vector<TH1D *> &histos,
                  const std::vector<std::string> &labels)
{
    canvas->Divide(2, 2, 0.001, 0.001);
    for (std::size_t index = 0; index < histos.size(); ++index) {
        canvas->cd(static_cast<int>(index + 1));
        gPad->SetGrid();
        gPad->SetTopMargin(0.12);
        histos[index]->SetLineColor(kBlue + 1);
        histos[index]->SetLineWidth(2);
        histos[index]->SetMinimum(0.0);
        histos[index]->DrawCopy("hist");
        draw_pad_label(labels[index]);
    }
}

} // namespace

constexpr std::array<int, FTOFHistos::kPanels> FTOFHistos::kPaddles;

FTOFHistos::FTOFHistos(const std::string &label) :
    label_(label),
    safe_label_(sanitize_root_name(label))
{
    book();
}

void FTOFHistos::book()
{
    for (int panel = 0; panel < kPanels; ++panel) {
        const auto name = panel_name(panel);
        adc_panel_[panel] = std::make_unique<TH1D>(
            (safe_label_ + "_ftof_p" + name + "_adc").c_str(),
            ("FTOF panel " + name + " ADC;ADC;hits").c_str(),
            kAdcBins,
            0.0,
            kAdcMax);
        adc_panel_[panel]->Sumw2();

        tdc_panel_[panel] = std::make_unique<TH1D>(
            (safe_label_ + "_ftof_p" + name + "_tdc").c_str(),
            ("FTOF panel " + name + " TDC;TDC;hits").c_str(),
            kTdcBins,
            kTdcMin,
            kTdcMax);
        tdc_panel_[panel]->Sumw2();
    }

    adc_all_ = std::make_unique<TH1D>(
        (safe_label_ + "_ftof_all_adc").c_str(),
        "FTOF all panels ADC;ADC;hits",
        kAdcBins,
        0.0,
        kAdcMax);
    adc_all_->Sumw2();

    tdc_all_ = std::make_unique<TH1D>(
        (safe_label_ + "_ftof_all_tdc").c_str(),
        "FTOF all panels TDC;TDC;hits",
        kTdcBins,
        kTdcMin,
        kTdcMax);
    tdc_all_->Sumw2();

    for (int sector = 0; sector < kSectors; ++sector) {
        const int s = sector + 1;
        occupancy_[sector] = std::make_unique<TH2D>(
            (safe_label_ + "_ftof_s" + std::to_string(s) + "_occupancy").c_str(),
            ("FTOF sector " + std::to_string(s) + " hit counts;paddle;panel;counts").c_str(),
            kMaxPaddles,
            0.5,
            kMaxPaddles + 0.5,
            kPanels,
            0.5,
            kPanels + 0.5);
        occupancy_[sector]->Sumw2();
    }

    xy_global_ = std::make_unique<TH2D>(
        (safe_label_ + "_ftof_xy_global").c_str(),
        "FTOF hit y vs x (global);x [mm];y [mm];entries",
        kXYBins,
        -kXYRange,
        kXYRange,
        kXYBins,
        -kXYRange,
        kXYRange);
    xy_global_->Sumw2();
}

void FTOFHistos::fill(const hipo::bank &ftof_adc, const hipo::bank &ftof_tdc, const hipo::bank &mc_true)
{
    ++events_;

    for (int row = 0; row < ftof_adc.getRows(); ++row) {
        const int sector = ftof_adc.getInt("sector", row);
        const int panel = ftof_adc.getInt("layer", row);
        const int paddle = ftof_adc.getInt("component", row);
        if (sector < 1 || sector > kSectors || panel < 1 || panel > kPanels ||
            paddle < 1 || paddle > kPaddles[panel - 1]) {
            continue;
        }

        const int adc = ftof_adc.getInt("ADC", row);
        adc_panel_[panel - 1]->Fill(adc);
        adc_all_->Fill(adc);
        occupancy_[sector - 1]->Fill(paddle, panel);
    }

    for (int row = 0; row < ftof_tdc.getRows(); ++row) {
        const int sector = ftof_tdc.getInt("sector", row);
        const int panel = ftof_tdc.getInt("layer", row);
        const int paddle = ftof_tdc.getInt("component", row);
        if (sector < 1 || sector > kSectors || panel < 1 || panel > kPanels ||
            paddle < 1 || paddle > kPaddles[panel - 1]) {
            continue;
        }

        const int tdc = ftof_tdc.getInt("TDC", row);
        tdc_panel_[panel - 1]->Fill(tdc);
        tdc_all_->Fill(tdc);
    }

    // Raw global hit position (y vs x) for FTOF true hits, unweighted, so the two-file comparison
    // runs on raw bin entries.
    for (int row = 0; row < mc_true.getRows(); ++row) {
        if (mc_true.getInt("detector", row) != kFtofDetectorId) {
            continue;
        }
        xy_global_->Fill(mc_true.getDouble("avgX", row), mc_true.getDouble("avgY", row));
    }
}

void FTOFHistos::finalize()
{
    // The ADC/TDC spectra and 2D maps are kept as raw counts; per-event normalization is applied by
    // the comparison framework via the default scale when the two inputs have different event counts.
}

void FTOFHistos::write(TDirectory *directory) const
{
    TDirectory *saved_dir = gDirectory;
    directory->cd();

    auto *subdir = directory->mkdir(safe_label_.c_str());
    subdir->cd();
    for (int panel = 0; panel < kPanels; ++panel) {
        adc_panel_[panel]->Write();
        tdc_panel_[panel]->Write();
    }
    adc_all_->Write();
    tdc_all_->Write();
    for (int sector = 0; sector < kSectors; ++sector) {
        occupancy_[sector]->Write();
    }
    xy_global_->Write();
    saved_dir->cd();
}

void FTOFHistos::save_plots(const std::string &plot_dir) const
{
    std::vector<TH1D *> adc_histos;
    std::vector<TH1D *> tdc_histos;
    std::vector<std::string> spectra_labels;
    for (int panel = 0; panel < kPanels; ++panel) {
        adc_histos.push_back(adc_panel_[panel].get());
        tdc_histos.push_back(tdc_panel_[panel].get());
        spectra_labels.push_back("panel " + panel_name(panel));
    }
    adc_histos.push_back(adc_all_.get());
    tdc_histos.push_back(tdc_all_.get());
    spectra_labels.emplace_back("all panels");

    auto *adc_canvas = make_canvas("c_" + safe_label_ + "_ftof_adc", label_ + " FTOF ADC", 1800, 1200);
    draw_spectra(adc_canvas, adc_histos, spectra_labels);
    adc_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_ftof_adc").c_str());
    show_canvas(adc_canvas);

    auto *tdc_canvas = make_canvas("c_" + safe_label_ + "_ftof_tdc", label_ + " FTOF TDC", 1800, 1200);
    draw_spectra(tdc_canvas, tdc_histos, spectra_labels);
    tdc_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_ftof_tdc").c_str());
    show_canvas(tdc_canvas);

    auto *occupancy_canvas = make_canvas("c_" + safe_label_ + "_ftof_occupancy",
                                         label_ + " FTOF hit counts", 2100, 1300);
    occupancy_canvas->Divide(3, 2, 0.001, 0.001);
    for (int sector = 0; sector < kSectors; ++sector) {
        occupancy_canvas->cd(sector + 1);
        gPad->SetGrid();
        gPad->SetRightMargin(0.15);
        gPad->SetTopMargin(0.10);
        occupancy_[sector]->DrawCopy("colz");
        draw_pad_label("S" + std::to_string(sector + 1) + " counts");
    }
    occupancy_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_ftof_occupancy").c_str());
    show_canvas(occupancy_canvas);

    draw_2d(xy_global_.get(), label_ + " FTOF hit y vs x (global)",
            plot_file(plot_dir, safe_label_ + "_ftof_xy_global"));
}

std::vector<TH1 *> FTOFHistos::comparison_histos() const
{
    std::vector<TH1 *> histos;
    for (int panel = 0; panel < kPanels; ++panel) {
        histos.push_back(adc_panel_[panel].get());
    }
    histos.push_back(adc_all_.get());
    for (int panel = 0; panel < kPanels; ++panel) {
        histos.push_back(tdc_panel_[panel].get());
    }
    histos.push_back(tdc_all_.get());
    return histos;
}

std::vector<std::string> FTOFHistos::comparison_names() const
{
    std::vector<std::string> names;
    for (int panel = 0; panel < kPanels; ++panel) {
        names.push_back("ftof_p" + panel_name(panel) + "_adc");
    }
    names.emplace_back("ftof_all_adc");
    for (int panel = 0; panel < kPanels; ++panel) {
        names.push_back("ftof_p" + panel_name(panel) + "_tdc");
    }
    names.emplace_back("ftof_all_tdc");
    return names;
}

std::vector<TH2 *> FTOFHistos::comparison_2d_histos() const
{
    std::vector<TH2 *> histos;
    for (int sector = 0; sector < kSectors; ++sector) {
        histos.push_back(occupancy_[sector].get());
    }
    histos.push_back(xy_global_.get());
    return histos;
}

std::vector<std::string> FTOFHistos::comparison_2d_names() const
{
    std::vector<std::string> names;
    for (int sector = 0; sector < kSectors; ++sector) {
        names.push_back("ftof_s" + std::to_string(sector + 1) + "_occupancy");
    }
    names.emplace_back("ftof_xy_global");
    return names;
}

std::string FTOFHistos::panel_name(int panel_index)
{
    static const std::array<std::string, kPanels> names = {"1a", "1b", "2"};
    if (panel_index < 0 || panel_index >= kPanels) {
        return "unknown";
    }
    return names[panel_index];
}

std::unique_ptr<SubsystemHistos> FTOFSubsystem::create_histos(const InputSpec &input,
                                                              const RunOptions &) const
{
    return std::make_unique<FTOFHistos>(input.label);
}

void FTOFSubsystem::process_file(const RunOptions &options, const InputSpec &input,
                                 SubsystemHistos &histos) const
{
    auto *ftof_histos = dynamic_cast<FTOFHistos *>(&histos);
    if (ftof_histos == nullptr) {
        throw std::runtime_error("Internal error: FTOF subsystem received non-FTOF histogram storage.");
    }

    hipo::reader reader;
    reader.open(input.path.c_str());

    hipo::dictionary factory;
    reader.readDictionary(factory);

    for (const char *bank_name : {"FTOF::adc", "FTOF::tdc", "MC::True"}) {
        if (!factory.hasSchema(bank_name)) {
            throw std::runtime_error("Input file '" + input.path + "' does not contain bank " + bank_name);
        }
    }

    hipo::bank ftof_adc(factory.getSchema("FTOF::adc"));
    hipo::bank ftof_tdc(factory.getSchema("FTOF::tdc"));
    hipo::bank mc_true(factory.getSchema("MC::True"));
    hipo::event event;

    long event_counter = 0;
    while (reader.next() && (options.max_events < 0 || event_counter < options.max_events)) {
        reader.read(event);
        event.getStructure(ftof_adc);
        event.getStructure(ftof_tdc);
        event.getStructure(mc_true);
        ftof_histos->fill(ftof_adc, ftof_tdc, mc_true);
        ++event_counter;

        if (options.print_interval > 0 && event_counter % options.print_interval == 0) {
            std::cout << "  " << input.label << ": processed " << event_counter << " events\n";
        }
    }

    std::cout << "  " << input.label << ": processed " << event_counter << " events\n";
}

#include "pcal/histos.h"

#include "TCanvas.h"
#include "TDirectory.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TLatex.h"
#include "TLegend.h"
#include "TPad.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>

namespace {

double max_bin_content_with_error(const TH1 *histo)
{
    if (histo == nullptr) {
        return 0.0;
    }

    double ymax = 0.0;
    for (int bin = 1; bin <= histo->GetNbinsX(); ++bin) {
        ymax = std::max(ymax, histo->GetBinContent(bin) + histo->GetBinError(bin));
    }
    return ymax;
}

void draw_pad_label(const std::string &label)
{
    TLatex latex;
    latex.SetNDC(true);
    latex.SetTextFont(43);
    latex.SetTextSize(16);
    latex.DrawLatex(0.14, 0.92, label.c_str());
}

void draw_comparison_pad(const std::vector<TH1 *> &histos, const std::vector<std::string> &labels,
                         const std::string &pad_label, bool draw_legend,
                         const bool *passed = nullptr)
{
    const std::array<int, 4> colors = {kBlack, kRed + 1, kBlue + 1, kGreen + 2};
    const std::array<int, 4> markers = {20, 24, 21, 25};
    double ymax = 0.0;
    for (auto *histo : histos) {
        ymax = std::max(ymax, max_bin_content_with_error(histo));
    }

    bool drew_one = false;
    for (std::size_t i = 0; i < histos.size(); ++i) {
        auto *histo = histos[i];
        if (histo == nullptr) {
            continue;
        }

        histo->SetLineColor(colors[i % colors.size()]);
        histo->SetMarkerColor(colors[i % colors.size()]);
        histo->SetMarkerStyle(markers[i % markers.size()]);
        histo->SetMarkerSize(0.5);
        histo->SetLineWidth(2);
        histo->SetMinimum(0.0);
        histo->SetMaximum(ymax > 0.0 ? ymax * 1.25 : 1.0);
        histo->DrawCopy(drew_one ? "E1 same" : "E1");
        drew_one = true;
    }

    draw_pad_label(pad_label);
    if (passed != nullptr) {
        draw_status_label(*passed);
    }
    if (draw_legend) {
        TLegend legend(0.52, 0.72, 0.92, 0.90);
        legend.SetBorderSize(0);
        legend.SetFillStyle(0);
        for (std::size_t i = 0; i < histos.size(); ++i) {
            if (histos[i] != nullptr) {
                legend.AddEntry(histos[i], labels[i].c_str(), "lep");
            }
        }
        legend.DrawClone();
    }
}

void draw_summary_canvas(TCanvas *canvas, const std::vector<TH1 *> &histos,
                         const std::vector<std::string> &pad_labels,
                         const std::vector<std::string> &labels)
{
    canvas->Divide(2, 2, 0.001, 0.001);
    for (std::size_t index = 0; index < histos.size(); ++index) {
        canvas->cd(static_cast<int>(index + 1));
        gPad->SetGrid();
        gPad->SetTopMargin(0.12);
        draw_comparison_pad({histos[index]}, labels, pad_labels[index], index == 0);
    }
}

void draw_matrix(TCanvas *canvas, const std::vector<TH1 *> &histos,
                 const std::vector<std::string> &labels)
{
    static constexpr int columns = 9;
    static constexpr int rows = 8;
    canvas->Divide(columns, rows, 0.001, 0.001);
    for (std::size_t component = 0; component < histos.size(); ++component) {
        canvas->cd(static_cast<int>(component + 1));
        gPad->SetGrid();
        gPad->SetTopMargin(0.12);
        draw_comparison_pad({histos[component]}, labels,
                            "C" + std::to_string(component + 1), component == 0);
    }
}

} // namespace

PCALHistos::PCALHistos(const std::string &label) :
    label_(label),
    safe_label_(sanitize_root_name(label))
{
    book();
}

void PCALHistos::book()
{
    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        const int layer = kLayerMin + layer_index;
        const auto view = view_name(layer_index);
        for (int component = 0; component < kComponents; ++component) {
            const auto channel = std::to_string(component + 1);
            adc_[layer_index][component] = std::make_unique<TH1D>(
                (safe_label_ + "_pcal_" + view + "_c" + channel + "_adc").c_str(),
                ("PCAL " + view + " component " + channel + " ADC;ADC;hits").c_str(),
                kAdcBins,
                0.0,
                kAdcMax);
            adc_[layer_index][component]->Sumw2();

            tdc_[layer_index][component] = std::make_unique<TH1D>(
                (safe_label_ + "_pcal_" + view + "_c" + channel + "_tdc").c_str(),
                ("PCAL " + view + " component " + channel + " TDC;TDC;hits").c_str(),
                kTdcBins,
                0.0,
                kTdcMax);
            tdc_[layer_index][component]->Sumw2();
        }

        adc_layer_[layer_index] = std::make_unique<TH1D>(
            (safe_label_ + "_pcal_l" + std::to_string(layer) + "_adc_sum").c_str(),
            ("PCAL layer " + std::to_string(layer) + " " + view + " summed ADC;ADC;hits").c_str(),
            kAdcBins,
            0.0,
            kAdcMax);
        adc_layer_[layer_index]->Sumw2();

        tdc_layer_[layer_index] = std::make_unique<TH1D>(
            (safe_label_ + "_pcal_l" + std::to_string(layer) + "_tdc_sum").c_str(),
            ("PCAL layer " + std::to_string(layer) + " " + view + " summed TDC;TDC;hits").c_str(),
            kTdcBins,
            0.0,
            kTdcMax);
        tdc_layer_[layer_index]->Sumw2();
    }

    adc_all_ = std::make_unique<TH1D>(
        (safe_label_ + "_pcal_all_adc_sum").c_str(),
        "PCAL all layers summed ADC;ADC;hits",
        kAdcBins,
        0.0,
        kAdcMax);
    adc_all_->Sumw2();

    tdc_all_ = std::make_unique<TH1D>(
        (safe_label_ + "_pcal_all_tdc_sum").c_str(),
        "PCAL all layers summed TDC;TDC;hits",
        kTdcBins,
        0.0,
        kTdcMax);
    tdc_all_->Sumw2();

    edep_all_ = std::make_unique<TH1D>(
        (safe_label_ + "_pcal_all_edep").c_str(),
        "PCAL all layers pre-digitization energy;energy deposited [MeV];hits",
        kEdepBins,
        0.0,
        kEdepMax);
    edep_all_->Sumw2();

    primary_phi_ = std::make_unique<TH1D>(
        (safe_label_ + "_pcal_primary_phi").c_str(),
        "PCAL generated primary phi;#phi [deg];particles",
        180,
        -180.0,
        180.0);
    primary_phi_->Sumw2();

    primary_theta_ = std::make_unique<TH1D>(
        (safe_label_ + "_pcal_primary_theta").c_str(),
        "PCAL generated primary theta;#theta [deg];particles",
        180,
        0.0,
        60.0);
    primary_theta_->Sumw2();

    primary_phi_sector_ = std::make_unique<TH1D>(
        (safe_label_ + "_pcal_primary_phi_sector").c_str(),
        "PCAL generated primary phi sector;sector;events",
        kSectors,
        0.5,
        kSectors + 0.5);
    primary_phi_sector_->Sumw2();

    true_phi_sector_ = std::make_unique<TH1D>(
        (safe_label_ + "_pcal_true_phi_sector").c_str(),
        "PCAL true-hit global phi sector;sector;hits",
        kSectors,
        0.5,
        kSectors + 0.5);
    true_phi_sector_->Sumw2();

    adc_sector_ = std::make_unique<TH1D>(
        (safe_label_ + "_pcal_adc_sector").c_str(),
        "PCAL ADC row sector;sector;hits",
        kSectors,
        0.5,
        kSectors + 0.5);
    adc_sector_->Sumw2();

    for (int sector = 0; sector < kSectors; ++sector) {
        const int s = sector + 1;
        occupancy_[sector] = std::make_unique<TH2D>(
            (safe_label_ + "_pcal_s" + std::to_string(s) + "_occupancy").c_str(),
            ("PCAL sector " + std::to_string(s) + " hit counts;component;layer;counts").c_str(),
            kComponents,
            0.5,
            kComponents + 0.5,
            kLayers,
            kLayerMin - 0.5,
            kLayerMax + 0.5);
        occupancy_[sector]->Sumw2();
    }

    xy_global_ = std::make_unique<TH2D>(
        (safe_label_ + "_pcal_xy_global").c_str(),
        "PCAL hit y vs x (global);x [mm];y [mm];entries",
        kXYBins,
        -kXYRange,
        kXYRange,
        kXYBins,
        -kXYRange,
        kXYRange);
    xy_global_->Sumw2();
}

void PCALHistos::fill(const hipo::bank &ecal_adc, const hipo::bank &ecal_tdc,
                      const hipo::bank &mc_true, const hipo::bank &mc_particle)
{
    ++events_;

    if (mc_particle.getRows() > 0) {
        const double px = mc_particle.getFloat("px", 0);
        const double py = mc_particle.getFloat("py", 0);
        const double pz = mc_particle.getFloat("pz", 0);
        const double p = std::sqrt(px * px + py * py + pz * pz);
        const double rad_to_deg = 180.0 / std::acos(-1.0);
        primary_phi_->Fill(std::atan2(py, px) * rad_to_deg);
        if (p > 0.0) {
            primary_theta_->Fill(std::acos(std::clamp(pz / p, -1.0, 1.0)) * rad_to_deg);
        }
        primary_phi_sector_->Fill(phi_sector(px, py));
    }

    for (int row = 0; row < ecal_adc.getRows(); ++row) {
        const int sector = ecal_adc.getInt("sector", row);
        const int layer = ecal_adc.getInt("layer", row);
        const int component = ecal_adc.getInt("component", row);
        if (sector < 1 || sector > kSectors || layer < kLayerMin || layer > kLayerMax ||
            component < 1 || component > kComponents) {
            continue;
        }

        const int layer_index = layer - kLayerMin;
        const int adc = ecal_adc.getInt("ADC", row);
        occupancy_[sector - 1]->Fill(component, layer);
        adc_sector_->Fill(sector);
        adc_[layer_index][component - 1]->Fill(adc);
        adc_layer_[layer_index]->Fill(adc);
        adc_all_->Fill(adc);
    }

    for (int row = 0; row < ecal_tdc.getRows(); ++row) {
        const int sector = ecal_tdc.getInt("sector", row);
        const int layer = ecal_tdc.getInt("layer", row);
        const int component = ecal_tdc.getInt("component", row);
        if (sector < 1 || sector > kSectors || layer < kLayerMin || layer > kLayerMax ||
            component < 1 || component > kComponents) {
            continue;
        }

        const int tdc = ecal_tdc.getInt("TDC", row);
        const int layer_index = layer - kLayerMin;
        tdc_[layer_index][component - 1]->Fill(tdc);
        tdc_layer_[layer_index]->Fill(tdc);
        tdc_all_->Fill(tdc);
    }

    for (int row = 0; row < mc_true.getRows(); ++row) {
        if (mc_true.getInt("detector", row) != kEcalDetectorId) {
            continue;
        }

        const double x = mc_true.getDouble("avgX", row);
        const double y = mc_true.getDouble("avgY", row);
        const double edep = mc_true.getDouble("totEdep", row);
        true_phi_sector_->Fill(phi_sector(x, y));
        edep_all_->Fill(edep);
        xy_global_->Fill(x, y);
    }
}

void PCALHistos::finalize()
{
    normalized_ = true;
}

void PCALHistos::write(TDirectory *directory) const
{
    TDirectory *saved_dir = gDirectory;
    directory->cd();

    auto *subdir = directory->mkdir(safe_label_.c_str());
    subdir->cd();
    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        for (int component = 0; component < kComponents; ++component) {
            adc_[layer_index][component]->Write();
            tdc_[layer_index][component]->Write();
        }
        adc_layer_[layer_index]->Write();
        tdc_layer_[layer_index]->Write();
    }
    adc_all_->Write();
    tdc_all_->Write();
    edep_all_->Write();
    primary_phi_->Write();
    primary_theta_->Write();
    primary_phi_sector_->Write();
    true_phi_sector_->Write();
    adc_sector_->Write();
    for (int sector = 0; sector < kSectors; ++sector) {
        occupancy_[sector]->Write();
    }
    xy_global_->Write();
    saved_dir->cd();
}

void PCALHistos::save_plots(const std::string &plot_dir) const
{
    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        const auto view = view_name(layer_index);
        std::vector<TH1 *> adc_components;
        std::vector<TH1 *> tdc_components;
        for (int component = 0; component < kComponents; ++component) {
            adc_components.push_back(adc_[layer_index][component].get());
            tdc_components.push_back(tdc_[layer_index][component].get());
        }

        auto *component_adc_canvas = make_canvas(
            "c_" + safe_label_ + "_pcal_" + view + "_adc",
            label_ + " PCAL " + view + " ADC", 2200, 1900);
        draw_matrix(component_adc_canvas, adc_components, {label_});
        component_adc_canvas->SaveAs(
            plot_file(plot_dir, safe_label_ + "_pcal_" + view + "_adc").c_str());
        show_canvas(component_adc_canvas);

        auto *component_tdc_canvas = make_canvas(
            "c_" + safe_label_ + "_pcal_" + view + "_tdc",
            label_ + " PCAL " + view + " TDC", 2200, 1900);
        draw_matrix(component_tdc_canvas, tdc_components, {label_});
        component_tdc_canvas->SaveAs(
            plot_file(plot_dir, safe_label_ + "_pcal_" + view + "_tdc").c_str());
        show_canvas(component_tdc_canvas);
    }

    std::vector<TH1 *> adc_histos;
    std::vector<TH1 *> tdc_histos;
    std::vector<std::string> layer_labels;
    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        adc_histos.push_back(adc_layer_[layer_index].get());
        tdc_histos.push_back(tdc_layer_[layer_index].get());
        layer_labels.push_back(view_name(layer_index) + " L" + std::to_string(kLayerMin + layer_index));
    }
    adc_histos.push_back(adc_all_.get());
    tdc_histos.push_back(tdc_all_.get());
    layer_labels.emplace_back("all layers");

    auto *adc_canvas = make_canvas("c_" + safe_label_ + "_pcal_adc_sum",
                                   label_ + " PCAL summed ADC", 1400, 1000);
    draw_summary_canvas(adc_canvas, adc_histos, layer_labels, {label_});
    adc_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_pcal_adc_sum").c_str());
    show_canvas(adc_canvas);

    auto *tdc_canvas = make_canvas("c_" + safe_label_ + "_pcal_tdc_sum",
                                   label_ + " PCAL summed TDC", 1400, 1000);
    draw_summary_canvas(tdc_canvas, tdc_histos, layer_labels, {label_});
    tdc_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_pcal_tdc_sum").c_str());
    show_canvas(tdc_canvas);

    draw_overlay({edep_all_.get()}, {label_}, "PCAL pre-digitization energy",
                 plot_file(plot_dir, safe_label_ + "_pcal_edep"));

    draw_overlay({primary_phi_.get()}, {label_}, "PCAL generated primary phi",
                 plot_file(plot_dir, safe_label_ + "_pcal_primary_phi"));
    draw_overlay({primary_theta_.get()}, {label_}, "PCAL generated primary theta",
                 plot_file(plot_dir, safe_label_ + "_pcal_primary_theta"));

    const std::vector<TH1 *> sector_histos = {
        primary_phi_sector_.get(),
        true_phi_sector_.get(),
        adc_sector_.get(),
    };
    const std::vector<std::string> sector_labels = {
        "primary phi",
        "true PCAL phi",
        "ADC sector",
    };
    auto *sector_canvas = make_canvas("c_" + safe_label_ + "_pcal_sector_summary",
                                      label_ + " PCAL sector diagnostics", 1800, 700);
    draw_summary_canvas(sector_canvas, sector_histos, sector_labels, {label_});
    sector_canvas->SaveAs(
        plot_file(plot_dir, safe_label_ + "_pcal_sector_summary").c_str());
    show_canvas(sector_canvas);

    auto *occupancy_canvas = make_canvas("c_" + safe_label_ + "_pcal_occupancy",
                                         label_ + " PCAL hit counts", 2100, 1300);
    occupancy_canvas->Divide(3, 2, 0.001, 0.001);
    for (int sector = 0; sector < kSectors; ++sector) {
        occupancy_canvas->cd(sector + 1);
        gPad->SetGrid();
        gPad->SetRightMargin(0.15);
        gPad->SetTopMargin(0.10);
        occupancy_[sector]->DrawCopy("colz");
        draw_pad_label("S" + std::to_string(sector + 1) + " counts");
    }
    occupancy_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_pcal_occupancy").c_str());
    show_canvas(occupancy_canvas);

    draw_2d(xy_global_.get(), label_ + " PCAL hit y vs x (global)",
            plot_file(plot_dir, safe_label_ + "_pcal_xy_global"));
}

std::vector<TH1 *> PCALHistos::comparison_histos() const
{
    std::vector<TH1 *> histos = {
        primary_phi_.get(),
        primary_theta_.get(),
        primary_phi_sector_.get(),
        true_phi_sector_.get(),
        adc_sector_.get(),
    };
    histos.push_back(edep_all_.get());
    return histos;
}

std::vector<std::string> PCALHistos::comparison_names() const
{
    std::vector<std::string> names = {
        "pcal_primary_phi",
        "pcal_primary_theta",
        "pcal_primary_phi_sector",
        "pcal_true_phi_sector",
        "pcal_adc_sector",
    };
    names.emplace_back("pcal_all_edep");
    return names;
}

std::vector<TH2 *> PCALHistos::comparison_2d_histos() const
{
    std::vector<TH2 *> histos;
    for (int sector = 0; sector < kSectors; ++sector) {
        histos.push_back(occupancy_[sector].get());
    }
    histos.push_back(xy_global_.get());
    return histos;
}

std::vector<std::string> PCALHistos::comparison_2d_names() const
{
    std::vector<std::string> names;
    for (int sector = 0; sector < kSectors; ++sector) {
        names.push_back("pcal_s" + std::to_string(sector + 1) + "_occupancy");
    }
    names.push_back("pcal_xy_global");
    return names;
}

std::vector<TH1 *> PCALHistos::diagnostic_histos() const
{
    std::vector<TH1 *> histos = comparison_histos();
    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        for (int component = 0; component < kComponents; ++component) {
            histos.push_back(adc_[layer_index][component].get());
        }
    }
    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        for (int component = 0; component < kComponents; ++component) {
            histos.push_back(tdc_[layer_index][component].get());
        }
    }
    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        histos.push_back(adc_layer_[layer_index].get());
    }
    histos.push_back(adc_all_.get());
    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        histos.push_back(tdc_layer_[layer_index].get());
    }
    histos.push_back(tdc_all_.get());
    return histos;
}

std::vector<std::string> PCALHistos::diagnostic_names() const
{
    std::vector<std::string> names = comparison_names();
    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        const auto view = view_name(layer_index);
        for (int component = 0; component < kComponents; ++component) {
            names.push_back("pcal_" + view + "_c" + std::to_string(component + 1) + "_adc");
        }
    }
    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        const auto view = view_name(layer_index);
        for (int component = 0; component < kComponents; ++component) {
            names.push_back("pcal_" + view + "_c" + std::to_string(component + 1) + "_tdc");
        }
    }
    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        names.push_back("pcal_l" + std::to_string(kLayerMin + layer_index) + "_adc_sum");
    }
    names.emplace_back("pcal_all_adc_sum");
    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        names.push_back("pcal_l" + std::to_string(kLayerMin + layer_index) + "_tdc_sum");
    }
    names.emplace_back("pcal_all_tdc_sum");
    return names;
}

double PCALHistos::diagnostic_scale(const std::string &name, bool normalize) const
{
    const bool normalizable = name.find("_adc") != std::string::npos ||
                              name.find("_tdc") != std::string::npos ||
                              name.find("_occupancy") != std::string::npos ||
                              name.find("_edep") != std::string::npos ||
                              name == "pcal_primary_phi" ||
                              name == "pcal_primary_theta" ||
                              name.find("_sector") != std::string::npos;
    if (!normalize || events_ <= 0 || !normalizable) {
        return 1.0;
    }
    return 1.0 / static_cast<double>(events_);
}

TH1D *PCALHistos::adc_histo(int layer_index, int component) const
{
    if (layer_index < 0 || layer_index >= kLayers || component < 0 || component >= kComponents) {
        return nullptr;
    }
    return adc_[layer_index][component].get();
}

TH1D *PCALHistos::tdc_histo(int layer_index, int component) const
{
    if (layer_index < 0 || layer_index >= kLayers || component < 0 || component >= kComponents) {
        return nullptr;
    }
    return tdc_[layer_index][component].get();
}

TH1D *PCALHistos::adc_layer_histo(int layer_index) const
{
    if (layer_index < 0 || layer_index >= kLayers) {
        return nullptr;
    }
    return adc_layer_[layer_index].get();
}

TH1D *PCALHistos::adc_all_histo() const
{
    return adc_all_.get();
}

TH1D *PCALHistos::tdc_layer_histo(int layer_index) const
{
    if (layer_index < 0 || layer_index >= kLayers) {
        return nullptr;
    }
    return tdc_layer_[layer_index].get();
}

TH1D *PCALHistos::tdc_all_histo() const
{
    return tdc_all_.get();
}

TH1D *PCALHistos::edep_all_histo() const
{
    return edep_all_.get();
}

std::string PCALHistos::view_name(int layer_index)
{
    static const std::array<std::string, kLayers> names = {"u", "v", "w"};
    if (layer_index < 0 || layer_index >= kLayers) {
        return "unknown";
    }
    return names[layer_index];
}

int PCALHistos::phi_sector(double x, double y)
{
    static constexpr double pi = 3.14159265358979323846;
    double phi = std::atan2(y, x) * 180.0 / pi;
    if (phi < 0.0) {
        phi += 360.0;
    }

    int sector = static_cast<int>(std::floor((phi + 30.0) / 60.0)) + 1;
    if (sector > kSectors) {
        sector -= kSectors;
    }
    return sector;
}

std::unique_ptr<SubsystemHistos> PCALSubsystem::create_histos(const InputSpec &input,
                                                              const RunOptions &) const
{
    return std::make_unique<PCALHistos>(input.label);
}

void PCALSubsystem::process_file(const RunOptions &options, const InputSpec &input,
                                 SubsystemHistos &histos) const
{
    auto *pcal_histos = dynamic_cast<PCALHistos *>(&histos);
    if (pcal_histos == nullptr) {
        throw std::runtime_error("Internal error: PCAL subsystem received non-PCAL histogram storage.");
    }

    hipo::reader reader;
    reader.open(input.path.c_str());

    hipo::dictionary factory;
    reader.readDictionary(factory);

    for (const char *bank_name : {"ECAL::adc", "ECAL::tdc", "MC::True", "MC::Particle"}) {
        if (!factory.hasSchema(bank_name)) {
            throw std::runtime_error("Input file '" + input.path + "' does not contain bank " + bank_name);
        }
    }

    hipo::bank ecal_adc(factory.getSchema("ECAL::adc"));
    hipo::bank ecal_tdc(factory.getSchema("ECAL::tdc"));
    hipo::bank mc_true(factory.getSchema("MC::True"));
    hipo::bank mc_particle(factory.getSchema("MC::Particle"));
    hipo::event event;

    long event_counter = 0;
    while (reader.next() && (options.max_events < 0 || event_counter < options.max_events)) {
        reader.read(event);
        event.getStructure(ecal_adc);
        event.getStructure(ecal_tdc);
        event.getStructure(mc_true);
        event.getStructure(mc_particle);
        pcal_histos->fill(ecal_adc, ecal_tdc, mc_true, mc_particle);
        ++event_counter;

        if (options.print_interval > 0 && event_counter % options.print_interval == 0) {
            std::cout << "  " << input.label << ": processed " << event_counter << " events\n";
        }
    }

    std::cout << "  " << input.label << ": processed " << event_counter << " events\n";
}

void PCALSubsystem::save_comparison_plots(const std::vector<SubsystemHistos *> &histos,
                                          const std::string &plot_dir, const std::string &header,
                                          bool normalize, const DiagnosticSummary &diagnostics) const
{
    if (histos.size() != 2) {
        return;
    }

    std::vector<const PCALHistos *> pcal_histos;
    std::vector<std::string> labels;
    for (const auto *histo_set : histos) {
        const auto *pcal_histo = dynamic_cast<const PCALHistos *>(histo_set);
        if (pcal_histo == nullptr) {
            return;
        }
        pcal_histos.push_back(pcal_histo);
        labels.push_back(pcal_histo->label());
    }

    struct MatrixSpec {
        std::string suffix;
        std::string title;
        TH1D *(PCALHistos::*accessor)(int, int) const;
    };
    const std::array<MatrixSpec, 2> matrix_types = {
        MatrixSpec{"adc", "ADC comparison", &PCALHistos::adc_histo},
        MatrixSpec{"tdc", "TDC comparison", &PCALHistos::tdc_histo},
    };

    for (int layer_index = 0; layer_index < PCALHistos::layers(); ++layer_index) {
        const auto view = PCALHistos::view_name(layer_index);
        for (const auto &spec : matrix_types) {
            auto *canvas = make_canvas("c_pcal_" + view + "_" + spec.suffix + "_compare",
                                       "PCAL " + view + " " + spec.title, 2200, 1900);
            canvas->Divide(9, 8, 0.001, 0.001);
            for (int component = 0; component < PCALHistos::components(); ++component) {
                canvas->cd(component + 1);
                gPad->SetGrid();
                gPad->SetTopMargin(0.12);

                std::vector<TH1 *> comparison;
                std::vector<std::unique_ptr<TH1>> scaled;
                for (const auto *pcal_histo : pcal_histos) {
                    auto *histo = (pcal_histo->*spec.accessor)(layer_index, component);
                    if (normalize && histo != nullptr && pcal_histo->events() > 0) {
                        auto clone = std::unique_ptr<TH1>(static_cast<TH1 *>(histo->Clone()));
                        clone->SetDirectory(nullptr);
                        clone->Scale(1.0 / static_cast<double>(pcal_histo->events()));
                        comparison.push_back(clone.get());
                        scaled.push_back(std::move(clone));
                    } else {
                        comparison.push_back(histo);
                    }
                }

                const auto name = "pcal_" + view + "_c" + std::to_string(component + 1) +
                                  "_" + spec.suffix;
                const auto status = diagnostics.statuses.find(name);
                const bool has_status = status != diagnostics.statuses.end();
                const bool passed = has_status && status->second;
                draw_comparison_pad(comparison, labels, "C" + std::to_string(component + 1),
                                    component == 0, has_status ? &passed : nullptr);
            }
            draw_canvas_header(canvas, header);
            canvas->SaveAs(
                plot_file(plot_dir, "compare_pcal_" + view + "_" + spec.suffix).c_str());
            show_canvas(canvas);
        }
    }

    struct SummarySpec {
        std::string suffix;
        std::string title;
        std::string all_name;
        TH1D *(PCALHistos::*layer_accessor)(int) const;
        TH1D *(PCALHistos::*all_accessor)() const;
    };
    const std::array<SummarySpec, 2> summaries = {
        SummarySpec{"adc_sum", "PCAL summed ADC comparison", "pcal_all_adc_sum",
                    &PCALHistos::adc_layer_histo, &PCALHistos::adc_all_histo},
        SummarySpec{"tdc_sum", "PCAL summed TDC comparison", "pcal_all_tdc_sum",
                    &PCALHistos::tdc_layer_histo, &PCALHistos::tdc_all_histo},
    };

    for (const auto &spec : summaries) {
        auto *canvas = make_canvas("c_pcal_" + spec.suffix + "_compare", spec.title, 1400, 1000);
        canvas->Divide(2, 2, 0.001, 0.001);
        for (int pad = 0; pad < PCALHistos::layers() + 1; ++pad) {
            canvas->cd(pad + 1);
            gPad->SetGrid();
            gPad->SetTopMargin(0.12);

            std::vector<TH1 *> comparison;
            std::vector<std::unique_ptr<TH1>> scaled;
            for (const auto *pcal_histo : pcal_histos) {
                auto *histo = pad < PCALHistos::layers()
                                  ? (pcal_histo->*spec.layer_accessor)(pad)
                                  : (pcal_histo->*spec.all_accessor)();
                if (normalize && histo != nullptr && pcal_histo->events() > 0) {
                    auto clone = std::unique_ptr<TH1>(static_cast<TH1 *>(histo->Clone()));
                    clone->SetDirectory(nullptr);
                    clone->Scale(1.0 / static_cast<double>(pcal_histo->events()));
                    comparison.push_back(clone.get());
                    scaled.push_back(std::move(clone));
                } else {
                    comparison.push_back(histo);
                }
            }

            const bool all_layers = pad == PCALHistos::layers();
            const auto name = all_layers
                                  ? spec.all_name
                                  : "pcal_l" + std::to_string(PCALHistos::layer_number(pad)) +
                                        "_" + spec.suffix;
            const auto status = diagnostics.statuses.find(name);
            const bool has_status = status != diagnostics.statuses.end();
            const bool passed = has_status && status->second;
            const auto pad_label = all_layers
                                       ? std::string("all layers")
                                       : PCALHistos::view_name(pad) + " L" +
                                             std::to_string(PCALHistos::layer_number(pad));
            draw_comparison_pad(comparison, labels, pad_label, pad == 0,
                                has_status ? &passed : nullptr);
        }
        draw_canvas_header(canvas, header);
        canvas->SaveAs(plot_file(plot_dir, "compare_pcal_" + spec.suffix).c_str());
        show_canvas(canvas);
    }
}

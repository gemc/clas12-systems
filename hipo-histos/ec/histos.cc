#include "ec/histos.h"

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
                         const bool *passed = nullptr, double shared_ymax = -1.0)
{
    const std::array<int, 4> colors = {kBlack, kRed + 1, kBlue + 1, kGreen + 2};
    const std::array<int, 4> markers = {20, 24, 21, 25};
    // A non-negative shared_ymax pins every pad of a comparison canvas to the same vertical scale;
    // otherwise fall back to a per-pad maximum.
    double ymax = shared_ymax;
    if (ymax < 0.0) {
        ymax = 0.0;
        for (auto *histo : histos) {
            ymax = std::max(ymax, max_bin_content_with_error(histo));
        }
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

void draw_matrix(TCanvas *canvas, const std::vector<TH1 *> &histos,
                 const std::vector<std::string> &labels, int matrix)
{
    canvas->Divide(matrix, matrix, 0.001, 0.001);
    for (int component = 0; component < matrix * matrix; ++component) {
        canvas->cd(component + 1);
        gPad->SetGrid();
        gPad->SetTopMargin(0.12);
        draw_comparison_pad({histos[component]}, labels,
                            "C" + std::to_string(component + 1), component == 0);
    }
}

void draw_summary_canvas(TCanvas *canvas, const std::vector<TH1 *> &histos,
                         const std::vector<std::string> &pad_labels,
                         const std::vector<std::string> &labels)
{
    canvas->Divide(3, 2, 0.001, 0.001);
    for (std::size_t index = 0; index < histos.size(); ++index) {
        canvas->cd(static_cast<int>(index + 1));
        gPad->SetGrid();
        gPad->SetTopMargin(0.12);
        draw_comparison_pad({histos[index]}, labels, pad_labels[index], index == 0);
    }
}

} // namespace

ECHistos::ECHistos(const std::string &label) :
    label_(label),
    safe_label_(sanitize_root_name(label))
{
    book();
}

void ECHistos::book()
{
    for (int view_index = 0; view_index < kViews; ++view_index) {
        const auto view = view_name(view_index);
        const auto layer_pair = view_layer_pair_label(view_index);
        for (int component = 0; component < kComponents; ++component) {
            const auto c = std::to_string(component + 1);
            adc_[view_index][component] = std::make_unique<TH1D>(
                (safe_label_ + "_ec_" + view + "_c" + c + "_adc").c_str(),
                ("EC " + view + " layers " + layer_pair + " component " + c + " ADC;ADC;hits")
                    .c_str(),
                kAdcBins,
                0.0,
                kAdcMax);
            adc_[view_index][component]->Sumw2();

            tdc_[view_index][component] = std::make_unique<TH1D>(
                (safe_label_ + "_ec_" + view + "_c" + c + "_tdc").c_str(),
                ("EC " + view + " layers " + layer_pair + " component " + c + " TDC;TDC;hits")
                    .c_str(),
                kTdcBins,
                0.0,
                kTdcMax);
            tdc_[view_index][component]->Sumw2();
        }
    }

    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        const int layer = kLayerMin + layer_index;
        tdc_layer_[layer_index] = std::make_unique<TH1D>(
            (safe_label_ + "_ec_l" + std::to_string(layer) + "_tdc_sum").c_str(),
            ("EC layer " + std::to_string(layer) + " summed TDC;TDC;hits").c_str(),
            kTdcBins,
            0.0,
            kTdcMax);
        tdc_layer_[layer_index]->Sumw2();
    }

    for (int view_index = 0; view_index < kViews; ++view_index) {
        const auto view = view_name(view_index);
        tdc_view_[view_index] = std::make_unique<TH1D>(
            (safe_label_ + "_ec_" + view + "_tdc_sum").c_str(),
            ("EC " + view + " view summed TDC;TDC;hits").c_str(),
            kTdcBins,
            0.0,
            kTdcMax);
        tdc_view_[view_index]->Sumw2();
    }

    tdc_all_ = std::make_unique<TH1D>(
        (safe_label_ + "_ec_all_tdc_sum").c_str(),
        "EC all layers summed TDC;TDC;hits",
        kTdcBins,
        0.0,
        kTdcMax);
    tdc_all_->Sumw2();

    primary_phi_ = std::make_unique<TH1D>(
        (safe_label_ + "_ec_primary_phi").c_str(),
        "EC generated primary phi;#phi [deg];particles",
        180,
        -180.0,
        180.0);
    primary_phi_->Sumw2();

    primary_theta_ = std::make_unique<TH1D>(
        (safe_label_ + "_ec_primary_theta").c_str(),
        "EC generated primary theta;#theta [deg];particles",
        180,
        0.0,
        60.0);
    primary_theta_->Sumw2();

    primary_phi_sector_ = std::make_unique<TH1D>(
        (safe_label_ + "_ec_primary_phi_sector").c_str(),
        "EC generated primary phi sector;sector;events",
        kSectors,
        0.5,
        kSectors + 0.5);
    primary_phi_sector_->Sumw2();

    true_ec_phi_sector_ = std::make_unique<TH1D>(
        (safe_label_ + "_ec_true_phi_sector").c_str(),
        "EC true-hit global phi sector;sector;hits",
        kSectors,
        0.5,
        kSectors + 0.5);
    true_ec_phi_sector_->Sumw2();

    adc_sector_ = std::make_unique<TH1D>(
        (safe_label_ + "_ec_adc_sector").c_str(),
        "EC ADC row sector;sector;hits",
        kSectors,
        0.5,
        kSectors + 0.5);
    adc_sector_->Sumw2();

    for (int sector = 0; sector < kSectors; ++sector) {
        const int s = sector + 1;
        occupancy_[sector] = std::make_unique<TH2D>(
            (safe_label_ + "_ec_s" + std::to_string(s) + "_occupancy").c_str(),
            ("EC sector " + std::to_string(s) + " hit counts;component;layer;counts").c_str(),
            kComponents,
            0.5,
            kComponents + 0.5,
            kLayers,
            kLayerMin - 0.5,
            kLayerMax + 0.5);
        occupancy_[sector]->Sumw2();
    }

    xy_global_ = std::make_unique<TH2D>(
        (safe_label_ + "_ec_xy_global").c_str(),
        "EC hit y vs x (global);x [mm];y [mm];entries",
        kXYBins,
        -kXYRange,
        kXYRange,
        kXYBins,
        -kXYRange,
        kXYRange);
    xy_global_->Sumw2();
}

void ECHistos::fill(const hipo::bank &ecal_adc, const hipo::bank &ecal_tdc, const hipo::bank &mc_true,
                    const hipo::bank &mc_particle)
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

        const int sector = phi_sector(px, py);
        if (sector >= 1 && sector <= kSectors) {
            primary_phi_sector_->Fill(sector);
        }
    }

    for (int row = 0; row < ecal_adc.getRows(); ++row) {
        const int sector = ecal_adc.getInt("sector", row);
        const int layer = ecal_adc.getInt("layer", row);
        const int component = ecal_adc.getInt("component", row);
        if (sector < 1 || sector > kSectors || layer < kLayerMin || layer > kLayerMax ||
            component < 1 || component > kComponents) {
            continue;
        }

        const int view_index = view_index_for_layer(layer);
        occupancy_[sector - 1]->Fill(component, layer);
        adc_sector_->Fill(sector);
        adc_[view_index][component - 1]->Fill(ecal_adc.getInt("ADC", row));
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
        const int view_index = view_index_for_layer(layer);
        tdc_[view_index][component - 1]->Fill(tdc);
        tdc_layer_[layer - kLayerMin]->Fill(tdc);
        tdc_view_[view_index]->Fill(tdc);
        tdc_all_->Fill(tdc);
    }

    // Raw global hit position (y vs x) for ECAL true hits, unweighted, so the two-file comparison
    // runs on raw bin entries.
    for (int row = 0; row < mc_true.getRows(); ++row) {
        if (mc_true.getInt("detector", row) != kEcalDetectorId) {
            continue;
        }
        const int sector = phi_sector(mc_true.getDouble("avgX", row), mc_true.getDouble("avgY", row));
        if (sector >= 1 && sector <= kSectors) {
            true_ec_phi_sector_->Fill(sector);
        }
        xy_global_->Fill(mc_true.getDouble("avgX", row), mc_true.getDouble("avgY", row));
    }
}

void ECHistos::finalize()
{
    // The 2D channel maps are kept as raw hit counts so the comparison runs on Poisson-distributed
    // counts (per-event normalization is applied only when the two inputs have different event
    // counts, via diagnostic_scale, exactly like the ADC/TDC spectra). Nothing else to do here.
    normalized_ = true;
}

void ECHistos::write(TDirectory *directory) const
{
    TDirectory *saved_dir = gDirectory;
    directory->cd();

    auto *subdir = directory->mkdir(safe_label_.c_str());
    subdir->cd();
    for (int view_index = 0; view_index < kViews; ++view_index) {
        for (int component = 0; component < kComponents; ++component) {
            adc_[view_index][component]->Write();
            tdc_[view_index][component]->Write();
        }
    }
    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        tdc_layer_[layer_index]->Write();
    }
    for (int view_index = 0; view_index < kViews; ++view_index) {
        tdc_view_[view_index]->Write();
    }
    tdc_all_->Write();
    primary_phi_->Write();
    primary_theta_->Write();
    primary_phi_sector_->Write();
    true_ec_phi_sector_->Write();
    adc_sector_->Write();
    for (int sector = 0; sector < kSectors; ++sector) {
        occupancy_[sector]->Write();
    }
    xy_global_->Write();
    saved_dir->cd();
}

void ECHistos::save_plots(const std::string &plot_dir) const
{
    for (int view_index = 0; view_index < kViews; ++view_index) {
        const auto view = view_name(view_index);
        const auto matrix_label = "EC " + view + " layers " + view_layer_pair_label(view_index);

        std::vector<TH1 *> adc_histos;
        std::vector<TH1 *> tdc_histos;
        for (int component = 0; component < kComponents; ++component) {
            adc_histos.push_back(adc_[view_index][component].get());
            tdc_histos.push_back(tdc_[view_index][component].get());
        }

        auto *adc_canvas = make_canvas("c_" + safe_label_ + "_ec_" + view + "_adc",
                                       label_ + " " + matrix_label + " ADC", 2000, 2000);
        draw_matrix(adc_canvas, adc_histos, {label_}, kMatrix);
        adc_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_ec_" + view + "_adc").c_str());
        show_canvas(adc_canvas);

        auto *tdc_canvas = make_canvas("c_" + safe_label_ + "_ec_" + view + "_tdc",
                                       label_ + " " + matrix_label + " TDC", 2000, 2000);
        draw_matrix(tdc_canvas, tdc_histos, {label_}, kMatrix);
        tdc_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_ec_" + view + "_tdc").c_str());
        show_canvas(tdc_canvas);
    }

    std::vector<TH1 *> tdc_layer_histos;
    std::vector<std::string> tdc_layer_labels;
    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        tdc_layer_histos.push_back(tdc_layer_[layer_index].get());
        tdc_layer_labels.push_back("L" + std::to_string(kLayerMin + layer_index));
    }
    auto *tdc_layer_canvas = make_canvas("c_" + safe_label_ + "_ec_tdc_layer_sum",
                                         label_ + " EC summed TDC by layer", 1800, 1200);
    draw_summary_canvas(tdc_layer_canvas, tdc_layer_histos, tdc_layer_labels, {label_});
    tdc_layer_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_ec_tdc_layer_sum").c_str());
    show_canvas(tdc_layer_canvas);

    std::vector<TH1 *> tdc_summary_histos;
    std::vector<std::string> tdc_summary_labels;
    for (int view_index = 0; view_index < kViews; ++view_index) {
        tdc_summary_histos.push_back(tdc_view_[view_index].get());
        tdc_summary_labels.push_back(view_name(view_index));
    }
    tdc_summary_histos.push_back(tdc_all_.get());
    tdc_summary_labels.emplace_back("all layers");
    auto *tdc_summary_canvas = make_canvas("c_" + safe_label_ + "_ec_tdc_view_sum",
                                           label_ + " EC summed TDC by view", 1800, 1200);
    draw_summary_canvas(tdc_summary_canvas, tdc_summary_histos, tdc_summary_labels, {label_});
    tdc_summary_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_ec_tdc_view_sum").c_str());
    show_canvas(tdc_summary_canvas);

    draw_overlay({primary_phi_.get()}, {label_}, "EC generated primary phi",
                 plot_file(plot_dir, safe_label_ + "_ec_primary_phi"));
    draw_overlay({primary_theta_.get()}, {label_}, "EC generated primary theta",
                 plot_file(plot_dir, safe_label_ + "_ec_primary_theta"));

    std::vector<TH1 *> sector_summary_histos = {
        primary_phi_sector_.get(),
        true_ec_phi_sector_.get(),
        adc_sector_.get(),
    };
    std::vector<std::string> sector_summary_labels = {
        "primary phi",
        "true EC phi",
        "ADC sector",
    };
    auto *sector_canvas = make_canvas("c_" + safe_label_ + "_ec_sector_summary",
                                      label_ + " EC sector diagnostics", 1800, 700);
    draw_summary_canvas(sector_canvas, sector_summary_histos, sector_summary_labels, {label_});
    sector_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_ec_sector_summary").c_str());
    show_canvas(sector_canvas);

    auto *occupancy_canvas = make_canvas("c_" + safe_label_ + "_ec_occupancy",
                                         label_ + " EC hit counts", 2100, 1300);
    occupancy_canvas->Divide(3, 2, 0.001, 0.001);
    for (int sector = 0; sector < kSectors; ++sector) {
        occupancy_canvas->cd(sector + 1);
        gPad->SetGrid();
        gPad->SetRightMargin(0.15);
        gPad->SetTopMargin(0.10);
        occupancy_[sector]->DrawCopy("colz");
        draw_pad_label("S" + std::to_string(sector + 1) + " counts");
    }
    occupancy_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_ec_occupancy").c_str());
    show_canvas(occupancy_canvas);

    draw_2d(xy_global_.get(), label_ + " EC hit y vs x (global)",
            plot_file(plot_dir, safe_label_ + "_ec_xy_global"));
}

std::vector<TH1 *> ECHistos::comparison_histos() const
{
    return {
        primary_phi_.get(),
        primary_theta_.get(),
        primary_phi_sector_.get(),
        true_ec_phi_sector_.get(),
        adc_sector_.get(),
    };
}

std::vector<std::string> ECHistos::comparison_names() const
{
    return {
        "ec_primary_phi",
        "ec_primary_theta",
        "ec_primary_phi_sector",
        "ec_true_phi_sector",
        "ec_adc_sector",
    };
}

std::vector<TH2 *> ECHistos::comparison_2d_histos() const
{
    std::vector<TH2 *> histos;
    for (int sector = 0; sector < kSectors; ++sector) {
        histos.push_back(occupancy_[sector].get());
    }
    histos.push_back(xy_global_.get());
    return histos;
}

std::vector<std::string> ECHistos::comparison_2d_names() const
{
    std::vector<std::string> names;
    for (int sector = 0; sector < kSectors; ++sector) {
        names.push_back("ec_s" + std::to_string(sector + 1) + "_occupancy");
    }
    names.push_back("ec_xy_global");
    return names;
}

std::vector<TH1 *> ECHistos::diagnostic_histos() const
{
    std::vector<TH1 *> histos = comparison_histos();
    for (int view_index = 0; view_index < kViews; ++view_index) {
        for (int component = 0; component < kComponents; ++component) {
            histos.push_back(adc_[view_index][component].get());
        }
    }
    for (int view_index = 0; view_index < kViews; ++view_index) {
        for (int component = 0; component < kComponents; ++component) {
            histos.push_back(tdc_[view_index][component].get());
        }
    }
    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        histos.push_back(tdc_layer_[layer_index].get());
    }
    for (int view_index = 0; view_index < kViews; ++view_index) {
        histos.push_back(tdc_view_[view_index].get());
    }
    histos.push_back(tdc_all_.get());
    return histos;
}

std::vector<std::string> ECHistos::diagnostic_names() const
{
    std::vector<std::string> names = comparison_names();
    for (int view_index = 0; view_index < kViews; ++view_index) {
        const auto view = view_name(view_index);
        for (int component = 0; component < kComponents; ++component) {
            names.push_back("ec_" + view + "_c" + std::to_string(component + 1) + "_adc");
        }
    }
    for (int view_index = 0; view_index < kViews; ++view_index) {
        const auto view = view_name(view_index);
        for (int component = 0; component < kComponents; ++component) {
            names.push_back("ec_" + view + "_c" + std::to_string(component + 1) + "_tdc");
        }
    }
    for (int layer_index = 0; layer_index < kLayers; ++layer_index) {
        names.push_back("ec_l" + std::to_string(kLayerMin + layer_index) + "_tdc_sum");
    }
    for (int view_index = 0; view_index < kViews; ++view_index) {
        names.push_back("ec_" + view_name(view_index) + "_tdc_sum");
    }
    names.emplace_back("ec_all_tdc_sum");
    return names;
}

double ECHistos::diagnostic_scale(const std::string &name, bool normalize) const
{
    const bool normalizable = name.find("_adc") != std::string::npos ||
                              name.find("_tdc") != std::string::npos ||
                              name.find("_occupancy") != std::string::npos ||
                              name == "ec_primary_phi" ||
                              name == "ec_primary_theta" ||
                              name.find("_sector") != std::string::npos;
    if (!normalize || events_ <= 0 || !normalizable) {
        return 1.0;
    }
    return 1.0 / static_cast<double>(events_);
}

TH1D *ECHistos::adc_histo(int view_index, int component) const
{
    if (view_index < 0 || view_index >= kViews || component < 0 || component >= kComponents) {
        return nullptr;
    }
    return adc_[view_index][component].get();
}

TH1D *ECHistos::tdc_histo(int view_index, int component) const
{
    if (view_index < 0 || view_index >= kViews || component < 0 || component >= kComponents) {
        return nullptr;
    }
    return tdc_[view_index][component].get();
}

TH1D *ECHistos::tdc_layer_histo(int layer_index) const
{
    if (layer_index < 0 || layer_index >= kLayers) {
        return nullptr;
    }
    return tdc_layer_[layer_index].get();
}

TH1D *ECHistos::tdc_view_histo(int view_index) const
{
    if (view_index < 0 || view_index >= kViews) {
        return nullptr;
    }
    return tdc_view_[view_index].get();
}

TH1D *ECHistos::tdc_all_histo() const
{
    return tdc_all_.get();
}

TH1D *ECHistos::primary_phi_histo() const
{
    return primary_phi_.get();
}

TH1D *ECHistos::primary_theta_histo() const
{
    return primary_theta_.get();
}

TH1D *ECHistos::primary_phi_sector_histo() const
{
    return primary_phi_sector_.get();
}

TH1D *ECHistos::true_ec_phi_sector_histo() const
{
    return true_ec_phi_sector_.get();
}

TH1D *ECHistos::adc_sector_histo() const
{
    return adc_sector_.get();
}

std::string ECHistos::view_name(int view_index)
{
    static const std::array<std::string, kViews> names = {"u", "v", "w"};
    if (view_index < 0 || view_index >= kViews) {
        return "unknown";
    }
    return names[view_index];
}

std::string ECHistos::view_layer_pair_label(int view_index)
{
    if (view_index < 0 || view_index >= kViews) {
        return "unknown";
    }
    return std::to_string(kLayerMin + view_index) + "+" +
           std::to_string(kLayerMin + view_index + kViews);
}

int ECHistos::view_index_for_layer(int layer)
{
    return (layer - kLayerMin) % kViews;
}

int ECHistos::phi_sector(double x, double y)
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

std::unique_ptr<SubsystemHistos> ECSubsystem::create_histos(const InputSpec &input,
                                                            const RunOptions &) const
{
    return std::make_unique<ECHistos>(input.label);
}

void ECSubsystem::process_file(const RunOptions &options, const InputSpec &input,
                               SubsystemHistos &histos) const
{
    auto *ec_histos = dynamic_cast<ECHistos *>(&histos);
    if (ec_histos == nullptr) {
        throw std::runtime_error("Internal error: EC subsystem received non-EC histogram storage.");
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
        ec_histos->fill(ecal_adc, ecal_tdc, mc_true, mc_particle);
        ++event_counter;

        if (options.print_interval > 0 && event_counter % options.print_interval == 0) {
            std::cout << "  " << input.label << ": processed " << event_counter << " events\n";
        }
    }

    std::cout << "  " << input.label << ": processed " << event_counter << " events\n";
}

void ECSubsystem::save_comparison_plots(const std::vector<SubsystemHistos *> &histos,
                                        const std::string &plot_dir, const std::string &header,
                                        bool normalize, const DiagnosticSummary &diagnostics) const
{
    static constexpr int matrix = 6;
    static constexpr int components = matrix * matrix;

    if (histos.size() != 2) {
        return;
    }

    std::vector<const ECHistos *> ec_histos;
    std::vector<std::string> labels;
    for (const auto *histo_set : histos) {
        const auto *ec_histo = dynamic_cast<const ECHistos *>(histo_set);
        if (ec_histo == nullptr) {
            return;
        }
        ec_histos.push_back(ec_histo);
        labels.push_back(ec_histo->label());
    }

    struct MatrixSpec {
        std::string suffix;
        std::string title;
        TH1D *(ECHistos::*accessor)(int, int) const;
    };
    const std::array<MatrixSpec, 2> matrix_types = {
        MatrixSpec{"adc", "ADC comparison", &ECHistos::adc_histo},
        MatrixSpec{"tdc", "TDC comparison", &ECHistos::tdc_histo},
    };

    for (int view_index = 0; view_index < ECHistos::views(); ++view_index) {
        const auto view = ECHistos::view_name(view_index);
        const auto matrix_label = "EC " + view + " layers " +
                                  ECHistos::view_layer_pair_label(view_index);
        for (const auto &spec : matrix_types) {
            auto *canvas = make_canvas("c_ec_" + view + "_" + spec.suffix + "_compare",
                                       matrix_label + " " + spec.title, 2000, 2000);
            canvas->Divide(matrix, matrix, 0.001, 0.001);

            // First pass: find the largest bin (with error) across every component and both
            // files so all pads of this comparison canvas share a single vertical scale.
            double shared_ymax = 0.0;
            for (int component = 0; component < components; ++component) {
                for (const auto *ec_histo : ec_histos) {
                    auto *histo = (ec_histo->*spec.accessor)(view_index, component);
                    const double scale = (normalize && histo != nullptr && ec_histo->events() > 0)
                                             ? 1.0 / static_cast<double>(ec_histo->events())
                                             : 1.0;
                    shared_ymax = std::max(shared_ymax, max_bin_content_with_error(histo) * scale);
                }
            }

            for (int component = 0; component < components; ++component) {
                canvas->cd(component + 1);
                gPad->SetGrid();
                gPad->SetTopMargin(0.12);

                std::vector<TH1 *> comparison;
                std::vector<std::unique_ptr<TH1>> scaled;
                for (const auto *ec_histo : ec_histos) {
                    auto *histo = (ec_histo->*spec.accessor)(view_index, component);
                    if (normalize && histo != nullptr && ec_histo->events() > 0) {
                        auto clone = std::unique_ptr<TH1>(static_cast<TH1 *>(histo->Clone()));
                        clone->SetDirectory(nullptr);
                        clone->Scale(1.0 / static_cast<double>(ec_histo->events()));
                        comparison.push_back(clone.get());
                        scaled.push_back(std::move(clone));
                    } else {
                        comparison.push_back(histo);
                    }
                }

                const auto name =
                    "ec_" + view + "_c" + std::to_string(component + 1) + "_" + spec.suffix;
                const auto status = diagnostics.statuses.find(name);
                const bool has_status = status != diagnostics.statuses.end();
                const bool passed = has_status && status->second;
                draw_comparison_pad(comparison, labels, "C" + std::to_string(component + 1),
                                    component == 0, has_status ? &passed : nullptr, shared_ymax);
            }
            draw_canvas_header(canvas, header);
            canvas->SaveAs(plot_file(plot_dir, "compare_ec_" + view + "_" + spec.suffix).c_str());
            show_canvas(canvas);
        }
    }

    auto *layer_canvas = make_canvas("c_ec_tdc_layer_sum_compare",
                                     "EC summed TDC comparison by layer", 1800, 1200);
    layer_canvas->Divide(3, 2, 0.001, 0.001);
    for (int layer_index = 0; layer_index < ECHistos::layers(); ++layer_index) {
        layer_canvas->cd(layer_index + 1);
        gPad->SetGrid();
        gPad->SetTopMargin(0.12);

        std::vector<TH1 *> comparison;
        std::vector<std::unique_ptr<TH1>> scaled;
        for (const auto *ec_histo : ec_histos) {
            auto *histo = ec_histo->tdc_layer_histo(layer_index);
            if (normalize && histo != nullptr && ec_histo->events() > 0) {
                auto clone = std::unique_ptr<TH1>(static_cast<TH1 *>(histo->Clone()));
                clone->SetDirectory(nullptr);
                clone->Scale(1.0 / static_cast<double>(ec_histo->events()));
                comparison.push_back(clone.get());
                scaled.push_back(std::move(clone));
            } else {
                comparison.push_back(histo);
            }
        }

        const int layer_number = ECHistos::layer_number(layer_index);
        const auto name = "ec_l" + std::to_string(layer_number) + "_tdc_sum";
        const auto status = diagnostics.statuses.find(name);
        const bool has_status = status != diagnostics.statuses.end();
        const bool passed = has_status && status->second;
        draw_comparison_pad(comparison, labels, "L" + std::to_string(layer_number), layer_index == 0,
                            has_status ? &passed : nullptr);
    }
    draw_canvas_header(layer_canvas, header);
    layer_canvas->SaveAs(plot_file(plot_dir, "compare_ec_tdc_layer_sum").c_str());
    show_canvas(layer_canvas);

    auto *view_canvas = make_canvas("c_ec_tdc_view_sum_compare",
                                    "EC summed TDC comparison by view", 1800, 1200);
    view_canvas->Divide(3, 2, 0.001, 0.001);
    for (int pad = 0; pad < ECHistos::views() + 1; ++pad) {
        view_canvas->cd(pad + 1);
        gPad->SetGrid();
        gPad->SetTopMargin(0.12);

        std::vector<TH1 *> comparison;
        std::vector<std::unique_ptr<TH1>> scaled;
        for (const auto *ec_histo : ec_histos) {
            auto *histo = pad < ECHistos::views() ? ec_histo->tdc_view_histo(pad)
                                                  : ec_histo->tdc_all_histo();
            if (normalize && histo != nullptr && ec_histo->events() > 0) {
                auto clone = std::unique_ptr<TH1>(static_cast<TH1 *>(histo->Clone()));
                clone->SetDirectory(nullptr);
                clone->Scale(1.0 / static_cast<double>(ec_histo->events()));
                comparison.push_back(clone.get());
                scaled.push_back(std::move(clone));
            } else {
                comparison.push_back(histo);
            }
        }

        const bool all_layers = pad == ECHistos::views();
        const auto view = all_layers ? std::string("all") : ECHistos::view_name(pad);
        const auto name = all_layers ? "ec_all_tdc_sum" : "ec_" + view + "_tdc_sum";
        const auto status = diagnostics.statuses.find(name);
        const bool has_status = status != diagnostics.statuses.end();
        const bool passed = has_status && status->second;
        draw_comparison_pad(comparison, labels, all_layers ? "all layers" : view, pad == 0,
                            has_status ? &passed : nullptr);
    }
    draw_canvas_header(view_canvas, header);
    view_canvas->SaveAs(plot_file(plot_dir, "compare_ec_tdc_view_sum").c_str());
    show_canvas(view_canvas);
}

#include "common.h"

#include "TCanvas.h"
#include "TColor.h"
#include "TFile.h"
#include "TH1.h"
#include "TH2.h"
#include "TLegend.h"
#include "TLatex.h"
#include "TPad.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TText.h"

#include <algorithm>
#include <cctype>
#include <filesystem>
#include <memory>
#include <stdexcept>

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

bool passes_entries_floor(const TH2 *first_gate, const TH2 *second_gate, int xbin, int ybin,
                          double min_entries_per_bin)
{
    if (min_entries_per_bin < 0.0 || first_gate == nullptr || second_gate == nullptr) {
        return true;
    }

    return std::min(first_gate->GetBinContent(xbin, ybin), second_gate->GetBinContent(xbin, ybin)) >=
           min_entries_per_bin;
}

std::unique_ptr<TH2> make_masked_2d(const TH2 *source, const TH2 *first_gate, const TH2 *second_gate,
                                    const std::string &name, double min_entries_per_bin)
{
    if (source == nullptr) {
        return nullptr;
    }

    auto masked = std::unique_ptr<TH2>(static_cast<TH2 *>(source->Clone(name.c_str())));
    masked->SetDirectory(nullptr);
    if (min_entries_per_bin < 0.0 || first_gate == nullptr || second_gate == nullptr) {
        return masked;
    }

    for (int xbin = 1; xbin <= source->GetNbinsX(); ++xbin) {
        for (int ybin = 1; ybin <= source->GetNbinsY(); ++ybin) {
            if (passes_entries_floor(first_gate, second_gate, xbin, ybin, min_entries_per_bin)) {
                continue;
            }
            masked->SetBinContent(xbin, ybin, 0.0);
            masked->SetBinError(xbin, ybin, 0.0);
        }
    }

    return masked;
}

std::unique_ptr<TH2> make_asymmetry_2d(const TH2 *first, const TH2 *second,
                                       const std::string &name)
{
    if (first == nullptr || second == nullptr) {
        return nullptr;
    }

    auto asymmetry = std::unique_ptr<TH2>(static_cast<TH2 *>(first->Clone(name.c_str())));
    asymmetry->SetDirectory(nullptr);
    asymmetry->Reset("ICES");

    for (int xbin = 1; xbin <= first->GetNbinsX(); ++xbin) {
        for (int ybin = 1; ybin <= first->GetNbinsY(); ++ybin) {
            const double value_first = first->GetBinContent(xbin, ybin);
            const double value_second = second->GetBinContent(xbin, ybin);
            const double sum = value_first + value_second;
            if (sum <= 0.0) {
                asymmetry->SetBinContent(xbin, ybin, 0.0);
                asymmetry->SetBinError(xbin, ybin, 0.0);
                continue;
            }
            asymmetry->SetBinContent(xbin, ybin, 2.0 * (value_first - value_second) / sum);
        }
    }

    return asymmetry;
}

// Plot name (bold) and one-line description drawn in the top band of the current canvas, so every
// saved plot states what it shows without consulting the source.
void draw_title_block(const std::string &title, const std::string &description, double title_y,
                      double description_y)
{
    TLatex latex;
    latex.SetNDC(true);
    if (!title.empty()) {
        latex.SetTextFont(63);
        latex.SetTextSize(24);
        latex.DrawLatex(0.02, title_y, title.c_str());
    }
    if (!description.empty()) {
        latex.SetTextFont(43);
        latex.SetTextSize(18);
        latex.SetTextColor(kGray + 3);
        latex.DrawLatex(0.02, description_y, description.c_str());
    }
}

const char *first_histo_title(const std::vector<TH1 *> &histos)
{
    for (const auto *histo : histos) {
        if (histo != nullptr) {
            return histo->GetTitle();
        }
    }
    return "";
}

void draw_2d_pad(TH2 *histo, const std::string &label)
{
    gPad->SetGrid();
    gPad->SetRightMargin(0.16);
    // Extra headroom keeps the pad label clear of the canvas-level title/description block.
    gPad->SetTopMargin(0.12);
    histo->DrawCopy("colz");

    TLatex latex;
    latex.SetNDC(true);
    latex.SetTextFont(43);
    latex.SetTextSize(18);
    latex.DrawLatex(0.12, 0.885, label.c_str());
}

} // namespace

std::string file_stem(const std::string &path)
{
    return std::filesystem::path(path).stem().string();
}

std::string sanitize_root_name(const std::string &name)
{
    std::string out;
    out.reserve(name.size());
    for (char c : name) {
        if (std::isalnum(static_cast<unsigned char>(c)) || c == '_') {
            out.push_back(c);
        } else {
            out.push_back('_');
        }
    }
    return out.empty() ? "histos" : out;
}

void ensure_directory(const std::string &path)
{
    if (path.empty()) {
        return;
    }
    std::error_code ec;
    std::filesystem::create_directories(path, ec);
    if (ec) {
        throw std::runtime_error("Could not create directory '" + path + "': " + ec.message());
    }
}

namespace {
std::string g_plot_extension = "png";
} // namespace

void set_plot_extension(const std::string &ext)
{
    std::string value = ext;
    if (!value.empty() && value.front() == '.') {
        value.erase(value.begin());
    }
    if (!value.empty()) {
        g_plot_extension = value;
    }
}

std::string plot_file(const std::string &dir, const std::string &stem)
{
    return dir + "/" + stem + "." + g_plot_extension;
}

void set_root_style(bool interactive)
{
    gROOT->SetBatch(!interactive);
    gStyle->SetOptStat(0);
    gStyle->SetOptTitle(0);
    gStyle->SetNumberContours(80);
    gStyle->SetPalette(kBird);
}

TCanvas *make_canvas(const std::string &name, const std::string &title, int width, int height)
{
    auto canvas = dynamic_cast<TCanvas *>(gROOT->FindObject(name.c_str()));
    if (canvas != nullptr) {
        canvas->Clear();
        canvas->SetTitle(title.c_str());
        return canvas;
    }
    return new TCanvas(name.c_str(), title.c_str(), width, height);
}

void draw_canvas_header(TCanvas *canvas, const std::string &header)
{
    if (canvas == nullptr || header.empty()) {
        return;
    }

    // Right-aligned so the left side of the top band stays free for the plot description.
    canvas->cd();
    TText text;
    text.SetNDC(true);
    text.SetTextFont(43);
    text.SetTextSize(16);
    text.SetTextAlign(31);
    text.DrawText(0.995, 0.977, header.c_str());
}

void draw_canvas_description(TCanvas *canvas, const std::string &description)
{
    if (canvas == nullptr || description.empty()) {
        return;
    }

    canvas->cd();
    TLatex latex;
    latex.SetNDC(true);
    latex.SetTextFont(43);
    latex.SetTextSize(20);
    latex.SetTextColor(kGray + 3);
    latex.DrawLatex(0.005, 0.977, description.c_str());
}

void draw_status_label(bool passed)
{
    TLatex latex;
    latex.SetNDC(true);
    latex.SetTextFont(43);
    latex.SetTextSize(24);
    latex.SetTextColor(passed ? kGreen + 3 : kRed + 1);
    latex.DrawLatex(0.14, 0.84, passed ? "passed" : "failed");
}

void show_canvas(TCanvas *canvas)
{
    if (canvas == nullptr) {
        return;
    }
    canvas->Draw();
    canvas->Modified();
    canvas->Update();
}

void draw_overlay(const std::vector<TH1 *> &histos, const std::vector<std::string> &labels,
                  const std::string &title, const std::string &output_path, bool log_y,
                  const std::string &header, bool has_status, bool passed)
{
    if (histos.empty()) {
        return;
    }

    auto canvas = make_canvas("c_" + sanitize_root_name(output_path), title);
    canvas->SetGrid();
    canvas->SetLogy(log_y);
    // Leave room above the frame for the title/description block and the header.
    canvas->SetTopMargin(0.12);

    const std::vector<int> colors = {kBlack, kRed + 1, kBlue + 1, kGreen + 2};
    const std::vector<int> markers = {20, 24, 21, 25};
    double ymax = 0.0;
    for (auto *histo : histos) {
        ymax = std::max(ymax, max_bin_content_with_error(histo));
    }
    if (ymax <= 0.0) {
        ymax = 1.0;
    }

    TLegend legend(0.65, 0.75, 0.90, 0.90);
    legend.SetBorderSize(0);
    legend.SetFillStyle(0);

    bool drew_one = false;
    for (std::size_t i = 0; i < histos.size(); ++i) {
        auto *histo = histos[i];
        if (histo == nullptr) {
            continue;
        }

        histo->SetLineColor(colors[i % colors.size()]);
        histo->SetMarkerColor(colors[i % colors.size()]);
        histo->SetMarkerStyle(markers[i % markers.size()]);
        histo->SetMarkerSize(0.7);
        histo->SetLineWidth(2);
        histo->SetMaximum(ymax * (log_y ? 5.0 : 1.25));
        histo->SetMinimum(log_y ? 0.1 : 0.0);
        histo->DrawCopy(drew_one ? "E1 same" : "E1");
        legend.AddEntry(histo, labels[i].c_str(), "lep");
        drew_one = true;
    }

    if (has_status) {
        draw_status_label(passed);
    }
    legend.DrawClone();
    draw_title_block(title, first_histo_title(histos), 0.962, 0.925);
    draw_canvas_header(canvas, header);
    canvas->SaveAs(output_path.c_str());
    show_canvas(canvas);
}

void draw_2d(TH2 *histo, const std::string &title, const std::string &output_path)
{
    if (histo == nullptr) {
        return;
    }

    auto canvas = make_canvas("c_" + sanitize_root_name(output_path), title);
    canvas->SetGrid();
    canvas->SetRightMargin(0.15);
    canvas->SetTopMargin(0.12);
    histo->DrawCopy("colz");
    draw_title_block(title, histo->GetTitle(), 0.962, 0.925);
    canvas->SaveAs(output_path.c_str());
    show_canvas(canvas);
}

void draw_2d_comparison(TH2 *first, TH2 *second, const std::vector<std::string> &labels,
                        const std::string &title, const std::string &output_path,
                        const std::string &header, bool has_status, bool passed,
                        double min_entries_per_bin, const TH2 *first_gate, const TH2 *second_gate)
{
    if (first == nullptr || second == nullptr || labels.size() < 2) {
        return;
    }

    const TH2 *gate_first = first_gate != nullptr ? first_gate : first;
    const TH2 *gate_second = second_gate != nullptr ? second_gate : second;
    auto first_display = make_masked_2d(first, gate_first, gate_second,
                                        "masked_first_" + sanitize_root_name(title),
                                        min_entries_per_bin);
    auto second_display = make_masked_2d(second, gate_first, gate_second,
                                         "masked_second_" + sanitize_root_name(title),
                                         min_entries_per_bin);
    auto asymmetry = make_asymmetry_2d(first_display.get(), second_display.get(),
                                       "asymmetry_" + sanitize_root_name(title));
    if (asymmetry == nullptr) {
        return;
    }

    const std::string asymmetry_label = "2*(" + labels[0] + " - " + labels[1] + ")/sum";
    asymmetry->SetTitle(asymmetry_label.c_str());
    asymmetry->GetZaxis()->SetTitle(asymmetry_label.c_str());
    asymmetry->SetMinimum(-2.0);
    asymmetry->SetMaximum(2.0);

    auto canvas = make_canvas("c_" + sanitize_root_name(output_path), title, 1800, 620);
    canvas->Divide(3, 1, 0.001, 0.001);

    canvas->cd(1);
    draw_2d_pad(first_display.get(), labels[0]);

    canvas->cd(2);
    draw_2d_pad(second_display.get(), labels[1]);
    if (has_status) {
        draw_status_label(passed);
    }

    canvas->cd(3);
    draw_2d_pad(asymmetry.get(), asymmetry_label);

    canvas->cd();
    draw_title_block(title, first != nullptr ? first->GetTitle() : "", 0.952, 0.918);
    draw_canvas_header(canvas, header);
    canvas->SaveAs(output_path.c_str());
    show_canvas(canvas);
}

double SubsystemHistos::diagnostic_scale(const std::string &, bool normalize) const
{
    if (!normalize || events() <= 0) {
        return 1.0;
    }
    return 1.0 / static_cast<double>(events());
}

double SubsystemHistos::comparison_plot_scale(const std::string &, bool normalize) const
{
    if (!normalize || events() <= 0) {
        return 1.0;
    }
    return 1.0 / static_cast<double>(events());
}

"""LTCC material definitions, ported from clas12Tags geometry_source/ltcc/materials.pl."""

from pygemc import GMaterial


# Table of optical photon energies (wavelengths) from 170-650 nm, shared by the
# C4F10, CO2 and N2 gas tables:
PENERGY_GAS = (
    "1.9074494*eV 1.9372533*eV 1.9680033*eV 1.9997453*eV 2.0325280*eV "
    "2.0664035*eV 2.1014273*eV 2.1376588*eV 2.1751616*eV 2.2140038*eV "
    "2.2542584*eV 2.2960039*eV 2.3393247*eV 2.3843117*eV 2.4310630*eV "
    "2.4796842*eV 2.5302900*eV 2.5830044*eV 2.6379619*eV 2.6953089*eV "
    "2.7552047*eV 2.8178230*eV 2.8833537*eV 2.9520050*eV 3.0240051*eV "
    "3.0996053*eV 3.1790823*eV 3.2627424*eV 3.3509246*eV 3.4440059*eV "
    "3.5424060*eV 3.6465944*eV 3.7570973*eV 3.8745066*eV 3.9994907*eV "
    "4.1328070*eV 4.2753176*eV 4.4280075*eV 4.5920078*eV 4.7686235*eV "
    "4.9593684*eV 5.1660088*eV 5.3906179*eV 5.6356459*eV 5.9040100*eV "
    "6.1992105*eV 6.5254848*eV 6.8927794367*eV 7.2982370506*eV"
)

# Index of refraction of C4F10 gas:
IREFR_C4F10 = (
    "1.0012258504 1.001225763 1.0012265232 1.0012264533 1.0012272134 "
    "1.0012288123 1.001232115 1.0012294938 1.001230254 1.0012310141 "
    "1.0012309355 1.0012316956 1.0012324557 1.0012349196 1.0012356798 "
    "1.0012364486 1.0012363525 1.0012379689 1.0012395853 1.0012411842 "
    "1.0012436481 1.0012444169 1.0012477021 1.001248471 1.0012492399 "
    "1.001251695 1.0012533027 1.001256614 1.0012599254 1.0012623719 "
    "1.0012656745 1.0012698334 1.0012731361 1.0012781425 1.0012848264 "
    "1.0012889853 1.001295678 1.0013032182 1.0013099196 1.0013174685 "
    "1.0013292375 1.0013401678 1.0013553268 1.0013713595 1.0013941548 "
    "1.0014118738 1.0014465255 1.0014761009 1.0015183889"
)

# Transparency of C4F10 gas at STP:
# (completely transparent except at very short wavelengths below ~200 nm)
ABSLENGTH_C4F10 = " ".join(["1000.000*m"] * 49)

# Index of refraction of CO2 gas at STP:
IREFR_CO2 = (
    "1.0004473 1.0004475 1.0004477 1.0004480 1.0004483 "
    "1.0004486 1.0004489 1.0004492 1.0004495 1.0004498 "
    "1.0004502 1.0004506 1.0004510 1.0004514 1.0004518 "
    "1.0004523 1.0004528 1.0004534 1.0004539 1.0004545 "
    "1.0004552 1.0004559 1.0004566 1.0004574 1.0004583 "
    "1.0004592 1.0004602 1.0004613 1.0004625 1.0004638 "
    "1.0004652 1.0004668 1.0004685 1.0004704 1.0004724 "
    "1.0004748 1.0004773 1.0004803 1.0004835 1.0004873 "
    "1.0004915 1.0004964 1.0005021 1.0005088 1.0005167 "
    "1.0005262 1.0005378 1.000552 1.000568"
)

# Transparency of CO2 gas at STP:
# (completely transparent except at very short wavelengths below ~200 nm)
ABSLENGTH_CO2 = (
    " ".join(["1000.0000000*m"] * 44)
    + " 82.8323273*m 4.6101432*m 0.7465970*m 0*m 0*m"
)

# Index of refraction of N2 gas:
IREFR_N2 = (
    "1.0002978023 1.000297921 1.0002980456 1.0002981764 1.0002983138 1.0002984584 "
    "1.0002986106 1.000298771 1.0002989402 1.0002991188 1.0002993075 1.0002995072 "
    "1.0002997188 1.0002999431 1.0003001812 1.0003004344 1.0003007039 1.0003009912 "
    "1.0003012978 1.0003016257 1.0003019767 1.0003023533 1.0003027578 1.0003031934 "
    "1.0003036631 1.0003041708 1.0003047208 1.0003053179 1.0003059678 1.0003066769 "
    "1.000307453 1.0003083049 1.000309243 1.0003102796 1.0003114294 1.0003127099 "
    "1.0003141423 1.0003157525 1.000317572 1.0003196403 1.0003220065 1.0003247334 "
    "1.0003279015 1.0003316163 1.0003360187 1.0003412998 1.0003477265 1.0003556817 "
    "1.0003657343"
)

# Transparency of N2 gas at STP:
ABSLENGTH_N2 = " ".join(["1000.0000000*m"] * 49)

# Table of optical photon energies (wavelengths) from 170-650 nm for the PMT
# (last two points differ from the gas table):
PENERGY_PMT = (
    "1.9074494*eV 1.9372533*eV 1.9680033*eV 1.9997453*eV 2.0325280*eV "
    "2.0664035*eV 2.1014273*eV 2.1376588*eV 2.1751616*eV 2.2140038*eV "
    "2.2542584*eV 2.2960039*eV 2.3393247*eV 2.3843117*eV 2.4310630*eV "
    "2.4796842*eV 2.5302900*eV 2.5830044*eV 2.6379619*eV 2.6953089*eV "
    "2.7552047*eV 2.8178230*eV 2.8833537*eV 2.9520050*eV 3.0240051*eV "
    "3.0996053*eV 3.1790823*eV 3.2627424*eV 3.3509246*eV 3.4440059*eV "
    "3.5424060*eV 3.6465944*eV 3.7570973*eV 3.8745066*eV 3.9994907*eV "
    "4.1328070*eV 4.2753176*eV 4.4280075*eV 4.5920078*eV 4.7686235*eV "
    "4.9593684*eV 5.1660088*eV 5.3906179*eV 5.6356459*eV 5.9040100*eV "
    "6.1992105*eV 6.5254848*eV 6.8880107*eV 7.2931878*eV"
)

# Index of refraction of the LTCC PMT quartz window:
RINDEX_PMT = (
    "1.5420481 1.5423678 1.5427003 1.5430465 1.5434074 "
    "1.5437840 1.5441775 1.5445893 1.5450206 1.5454731 "
    "1.5459484 1.5464485 1.5469752 1.5475310 1.5481182 "
    "1.5487396 1.5493983 1.5500977 1.5508417 1.5516344 "
    "1.5524807 1.5533859 1.5543562 1.5553983 1.5565202 "
    "1.5577308 1.5590402 1.5604602 1.5620045 1.5636888 "
    "1.5655313 1.5675538 1.5697816 1.5722449 1.5749797 "
    "1.5780296 1.5814472 1.5852971 1.5896593 1.5946337 "
    "1.6003470 1.6069618 1.6146902 1.6238138 1.6347145 "
    "1.6479224 1.6641955 1.6641955 1.6641955"
)

# Quantum efficiency of an LTCC PMT (Photonis XP4500B PMT with a 110ug/cm2 p-terphenyl
# coating), see https://arxiv.org/pdf/1611.03467.pdf
QE_PMT = (
    "0.0000 0.0014 0.0024 0.0040 0.0065 0.0105 0.0149 0.0216 0.0289 "
    "0.0376 0.0482 0.0609 0.0753 0.09376864 0.109595509 0.126034076 "
    "0.144388644 0.160962426 0.175241881 0.188825334 0.202865707 "
    "0.217345306 0.22668678 0.234647896 0.241215353 0.242290656 "
    "0.241827193 0.239181876 0.23452262 0.22840029 0.224153055 0.215169066 "
    "0.208173389 0.206008707 0.21460707 0.215113225 0.215113349 "
    "0.215113349 0.215113349 0.215113349 0.215113245 0.214802621 "
    "0.214028264 0.215113335 0.215113349 0.215113349 0.215113349 "
    "0.215113349 0.215113349"
)


def define_materials(configuration):
    # The elliptical mirror volumes use G4_AIR_Optical (GEMC2's built-in "Air_Opt"),
    # predefined by gemc in g4system/g4materials.cc.

    # ltcc gas is C4F10 with optical properties
    c4f10 = GMaterial("C4F10")
    c4f10.description = "clas12 ltcc gas"
    c4f10.density = 0.01012
    c4f10.addMaterialWithFractionalMass("G4_C", 0.3)
    c4f10.addMaterialWithFractionalMass("G4_F", 0.7)
    c4f10.photonEnergy = PENERGY_GAS
    c4f10.indexOfRefraction = IREFR_C4F10
    c4f10.absorptionLength = ABSLENGTH_C4F10
    c4f10.publish(configuration)

    # htcc gas is 100% CO2 with optical properties
    htcc_gas = GMaterial("HTCCgas")
    htcc_gas.description = "htcc gas is 100% CO2 with optical properties"
    htcc_gas.density = 0.00184
    htcc_gas.addMaterialWithFractionalMass("G4_CARBON_DIOXIDE", 1.0)
    htcc_gas.photonEnergy = PENERGY_GAS
    htcc_gas.indexOfRefraction = IREFR_CO2
    htcc_gas.absorptionLength = ABSLENGTH_CO2
    htcc_gas.publish(configuration)

    # N2 optical properties
    n2 = GMaterial("N2")
    n2.description = "N2 optical properties"
    n2.density = 0.0011652
    n2.addMaterialWithFractionalMass("G4_N", 1.0)
    n2.photonEnergy = PENERGY_GAS
    n2.indexOfRefraction = IREFR_N2
    n2.absorptionLength = ABSLENGTH_N2
    n2.publish(configuration)

    # UV window of LTCC PMT:
    # - refractive index (required for tracking of optical photons)
    # - efficiency (for quantum efficiency of photocathode)
    # NOTE: in principle the quantum efficiency data of the photocathode
    # already includes the effects of reflection and transmission
    # at the interface between the window and the surrounding environment.
    # Therefore, it is possible that we are "double-counting" such effects
    # on the photo-electron yield by including the refractive index here.
    # However, only a small fraction of the light will be reflected by the
    # window in any case so we don't need to worry too much.
    pmt_glass = GMaterial("LTCCPMTGlass")
    pmt_glass.description = "refractive index and efficency of LTCC PMT glass window"
    pmt_glass.density = 2.32
    pmt_glass.addMaterialWithFractionalMass("G4_SILICON_DIOXIDE", 1.0)
    pmt_glass.photonEnergy = PENERGY_PMT
    pmt_glass.efficiency = QE_PMT
    pmt_glass.indexOfRefraction = RINDEX_PMT
    # gemc3 improvement over GEMC2 (which defined no absorption in the glass and relied on
    # a 100-step optical photon kill): a finite absorption length lets photons trapped in
    # the window by total internal reflection die physically. 300 cm is the fused-silica
    # scale in the visible/UV; the ~cm direct window path is unaffected (>99% transmission).
    pmt_glass.absorptionLength = " ".join(["300.0*cm"] * len(PENERGY_PMT.split()))
    pmt_glass.publish(configuration)

    # GEMC2 quirk preserved: materials.pl reuses the LTCCPMTGlass hash without
    # init_mat(), so ltcc_WC_material inherits the PMT optical properties.
    wc_material = GMaterial("ltcc_WC_material")
    wc_material.description = "Nickel Iron Molybdenum Alloy Properties (Theoretical)"
    wc_material.density = 8.75
    wc_material.addMaterialWithFractionalMass("G4_Ni", 0.85)
    wc_material.addMaterialWithFractionalMass("G4_Mo", 0.04)
    wc_material.addMaterialWithFractionalMass("G4_Fe", 0.11)
    wc_material.photonEnergy = PENERGY_PMT
    wc_material.efficiency = QE_PMT
    wc_material.indexOfRefraction = RINDEX_PMT
    wc_material.publish(configuration)

    # ltcc_nose: homogenised material for the `nose` CAD solid, a simplified approximation of five support
    # pieces (one epoxy block + four steel parts) - a segmented convex hull for the head plus a flat slab for
    # the NFrame body. Composition is set by the epoxy:steel VOLUME ratio of those pieces, 27.4% epoxy /
    # 72.6% steel (see stls/notes.md); with rho_epoxy = 1.2 and rho_steel = 8.0 g/cm^3 that is steel 94.64% /
    # epoxy 5.36% by mass (epoxy split into C/H/O by a typical resin ratio 76/8/16), giving a total mass of
    # ~342 kg. The approximated solid (88.8 L, after the flat NFrame slab fills the open frame, the whole is
    # clipped to the sector and the side walls are cut out of it) is ~1.6x the real material volume (55.7 L),
    # so the density is set to CONSERVE that mass over it: 341.6 kg / 88.8 L = 3.85 g/cm^3 (using the packed
    # 6.14 g/cm^3 would overstate the mass ~1.6x).
    nose = GMaterial("ltcc_nose")
    nose.description = "LTCC nose: 27.4% epoxy + 72.6% steel by volume, mass-conserving over the solid"
    nose.density = 3.85
    nose.addMaterialWithFractionalMass("G4_STAINLESS-STEEL", 0.9464)
    nose.addMaterialWithFractionalMass("G4_C", 0.0408)
    nose.addMaterialWithFractionalMass("G4_H", 0.0043)
    nose.addMaterialWithFractionalMass("G4_O", 0.0085)
    nose.publish(configuration)

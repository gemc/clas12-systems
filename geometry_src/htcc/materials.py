"""HTCC material definitions, ported from clas12Tags geometry_source/htcc/materials.pl.

Optical property tables (photon energy, index of refraction, absorption length,
quantum efficiency and reflectivity) are transcribed verbatim from the perl arrays. The
photon-energy grid `PENERGY` (190-650 nm, 47 points) is shared by the CO2 gas and the
PMT quartz window; the mirror-coating materials use the shorter `PENERGY_MIRR` grid
(200-650 nm, 46 points) from Andrew Puckett's fall-2012 measurements.
"""

from pygemc import GMaterial


# Table of optical photon energies (wavelengths) from 190-650 nm (47 points):
PENERGY = (
    "1.9074494*eV 1.9372533*eV 1.9680033*eV 1.9997453*eV 2.0325280*eV "
    "2.0664035*eV 2.1014273*eV 2.1376588*eV 2.1751616*eV 2.2140038*eV "
    "2.2542584*eV 2.2960039*eV 2.3393247*eV 2.3843117*eV 2.4310630*eV "
    "2.4796842*eV 2.5302900*eV 2.5830044*eV 2.6379619*eV 2.6953089*eV "
    "2.7552047*eV 2.8178230*eV 2.8833537*eV 2.9520050*eV 3.0240051*eV "
    "3.0996053*eV 3.1790823*eV 3.2627424*eV 3.3509246*eV 3.4440059*eV "
    "3.5424060*eV 3.6465944*eV 3.7570973*eV 3.8745066*eV 3.9994907*eV "
    "4.1328070*eV 4.2753176*eV 4.4280075*eV 4.5920078*eV 4.7686235*eV "
    "4.9593684*eV 5.1660088*eV 5.3906179*eV 5.6356459*eV 5.9040100*eV "
    "6.1992105*eV 6.5254848*eV"
)

# Index of refraction of CO2 gas at STP (47 points):
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
    "1.0005262 1.0005378"
)

# Transparency of CO2 gas at STP: transparent except at very short wavelengths (47 points):
ABSLENGTH_CO2 = (
    " ".join(["1000.0000000*m"] * 44)
    + " 82.8323273*m 4.6101432*m 0.7465970*m"
)

# Quantum efficiency of HTCC PMT with quartz window (47 points):
QE_HTCC_PMT = (
    "0.0000000 0.0014000 0.0024000 0.0040000 0.0065000 "
    "0.0105000 0.0149000 0.0216000 0.0289000 0.0376000 "
    "0.0482000 0.0609000 0.0753000 0.0916000 0.1116000 "
    "0.1265000 0.1435000 0.1602000 0.1725000 0.1892000 "
    "0.2017000 0.2122000 0.2249000 0.2344000 0.2401000 "
    "0.2418000 0.2394000 0.2372000 0.2309000 0.2291000 "
    "0.2275000 0.2301000 0.2288000 0.2236000 0.2268000 "
    "0.2240000 0.2219000 0.2219000 0.2223000 0.2189000 "
    "0.2158000 0.2093000 0.2038000 0.1950000 0.1836000 "
    "0.1612000 0.1305000"
)

# Index of refraction of HTCC PMT quartz window (47 points):
RINDEX_HTCC_PMT = (
    "1.5420481 1.5423678 1.5427003 1.5430465 1.5434074 "
    "1.5437840 1.5441775 1.5445893 1.5450206 1.5454731 "
    "1.5459484 1.5464485 1.5469752 1.5475310 1.5481182 "
    "1.5487396 1.5493983 1.5500977 1.5508417 1.5516344 "
    "1.5524807 1.5533859 1.5543562 1.5553983 1.5565202 "
    "1.5577308 1.5590402 1.5604602 1.5620045 1.5636888 "
    "1.5655313 1.5675538 1.5697816 1.5722449 1.5749797 "
    "1.5780296 1.5814472 1.5852971 1.5896593 1.5946337 "
    "1.6003470 1.6069618 1.6146902 1.6238138 1.6347145 "
    "1.6479224 1.6641955"
)

# Reflectivity of Al-MgF2 HTCC mirror coating on PENERGY grid (47 points):
REFLECTIVITY_ALMGF2 = (
    "0.8860000 0.8880000 0.8890000 0.8900000 0.8930000 "
    "0.8960000 0.8970000 0.9000000 0.9010000 0.9020000 "
    "0.9030000 0.9040000 0.9040000 0.9040000 0.9040000 "
    "0.9040000 0.9040000 0.9040000 0.9050000 0.9050000 "
    "0.9050000 0.9050000 0.9040000 0.9040000 0.9040000 "
    "0.9040000 0.9030000 0.9030000 0.9030000 0.9020000 "
    "0.9020000 0.9010000 0.9010000 0.9000000 0.8970000 "
    "0.8930000 0.8890000 0.8830000 0.8780000 0.8660000 "
    "0.8520000 0.8360000 0.8190000 0.7950000 0.7660000 "
    "0.7370000 0.6950000"
)

# Photon energies for the mirror-coating measurements, wavelengths 200-650 nm (46 points):
PENERGY_MIRR = (
    "1.907449*eV 1.937253*eV 1.968003*eV 1.999745*eV 2.032528*eV "
    "2.066404*eV 2.101427*eV 2.137659*eV 2.175162*eV 2.214004*eV "
    "2.254258*eV 2.296004*eV 2.339325*eV 2.384312*eV 2.431063*eV "
    "2.479684*eV 2.53029*eV 2.583004*eV 2.637962*eV 2.695309*eV "
    "2.755205*eV 2.817823*eV 2.883354*eV 2.952005*eV 3.024005*eV "
    "3.099605*eV 3.179082*eV 3.262742*eV 3.350925*eV 3.444006*eV "
    "3.542406*eV 3.646594*eV 3.757097*eV 3.874507*eV 3.999491*eV "
    "4.132807*eV 4.275318*eV 4.428008*eV 4.592008*eV 4.768623*eV "
    "4.959368*eV 5.166009*eV 5.390618*eV 5.635646*eV 5.90401*eV "
    "6.199211*eV"
)

# Reflectivity of AlMgF2 on acryl sheets, measured by AJRP 10/01/2012 (46 points):
REFLECTIVITY_ALMGF2_MIRR = (
    "0.8722925 0.8725418 0.8724854 0.8719032 0.8735628 "
    "0.8733527 0.8728732 0.8769834 0.8794382 0.8790207 "
    "0.8762184 0.8800928 0.8808256 0.8812256 0.8801459 "
    "0.876982 0.8786141 0.8790666 0.8786467 0.8802601 "
    "0.8824032 0.8805016 0.8733517 0.8705232 0.8753389 "
    "0.8739763 0.87137 0.8754125 0.8802811 0.8616457 "
    "0.8677598 0.8684776 0.8629656 0.856517 0.8539165 "
    "0.8502238 0.8450355 0.8342837 0.8257114 0.8160133 "
    "0.8036618 0.783193 0.7541341 0.7498343 0.6969729 "
    "0.6854251"
)

# Reflectivity of AlMgF2 on Winston cones, measured by AJRP 10/04/2012 (46 points):
REFLECTIVITY_ALMGF2_WC = (
    "0.8331038 0.8309071 0.8279127 0.8280742 0.8322623 "
    "0.837572 0.8396875 0.8481834 0.8660284 0.8611336 "
    "0.8566167 0.8667431 0.86955 0.8722481 0.8728122 "
    "0.8771635 0.879907 0.879761 0.8831943 0.8894673 "
    "0.8984234 0.9009531 0.8910166 0.8887382 0.8869093 "
    "0.8941976 0.8948479 0.8877356 0.9026919 0.8999685 "
    "0.9101617 0.8983005 0.8991694 0.8990987 0.9000493 "
    "0.9065833 0.9028855 0.8985184 0.9009736 0.9086968 "
    "0.9015145 0.8914838 0.8816829 0.8666895 0.8496298 "
    "0.9042583"
)


def define_materials(configuration):
    # htcc gas is 100% CO2 with optical properties
    gas = GMaterial("HTCCgas")
    gas.description = "htcc gas is 100% CO2 with optical properties"
    gas.density = 0.00184
    gas.addMaterialWithFractionalMass("G4_CARBON_DIOXIDE", 1.0)
    gas.photonEnergy = PENERGY
    gas.indexOfRefraction = IREFR_CO2
    gas.absorptionLength = ABSLENGTH_CO2
    gas.publish(configuration)

    # rohacell composite (mirror substrate)
    rohacell = GMaterial("rohacell31")
    rohacell.description = "rohacell composite material"
    rohacell.density = 0.032
    rohacell.addMaterialWithFractionalMass("G4_C", 0.6463)
    rohacell.addMaterialWithFractionalMass("G4_H", 0.0784)
    rohacell.addMaterialWithFractionalMass("G4_N", 0.0839)
    rohacell.addMaterialWithFractionalMass("G4_O", 0.1914)
    rohacell.publish(configuration)

    # tedlar used in the composite window
    tedlar = GMaterial("HTCCTedlar")
    tedlar.description = "tedlar material used in the composite window"
    tedlar.density = 1.43
    tedlar.addMaterialWithFractionalMass("G4_C", 0.33)
    tedlar.addMaterialWithFractionalMass("G4_F", 0.33)
    tedlar.addMaterialWithFractionalMass("G4_H", 0.34)
    tedlar.publish(configuration)

    # composite window: Mylar (1.4) and tedlar (1.43), averaged density 1.415
    window = GMaterial("HTCCCompositeWindow")
    window.description = "composite window material"
    window.density = 1.415
    window.addMaterialWithFractionalMass("HTCCTedlar", 0.5)
    window.addMaterialWithFractionalMass("G4_MYLAR", 0.5)
    window.publish(configuration)

    # quartz window of the HTCC PMT: refractive index and photocathode efficiency
    quartz = GMaterial("HTCCPMTQuartz")
    quartz.description = "refractive index and efficency of HTCC PMT Quartz window"
    quartz.density = 2.32
    quartz.addMaterialWithFractionalMass("G4_SILICON_DIOXIDE", 1.0)
    quartz.photonEnergy = PENERGY
    quartz.efficiency = QE_HTCC_PMT
    quartz.indexOfRefraction = RINDEX_HTCC_PMT
    quartz.publish(configuration)

    # AlMgF2 mirror coating; mass fractions/density are largely irrelevant because the
    # reflectivity is applied by hand and the coating is negligible for Eloss/scattering.
    almgf2 = GMaterial("HTCCECIAlMgF2")
    almgf2.description = "Measured reflectivity for Al+MgF2"
    almgf2.density = 2.9007
    almgf2.addMaterialWithFractionalMass("G4_Al", 0.331)
    almgf2.addMaterialWithFractionalMass("G4_Mg", 0.261)
    almgf2.addMaterialWithFractionalMass("G4_F", 0.408)
    almgf2.photonEnergy = PENERGY
    almgf2.reflectivity = REFLECTIVITY_ALMGF2
    almgf2.publish(configuration)

    # measured reflectivity of Al+MgF2 coated on acryl sheets (ECI), AJRP 10/08/2012
    eci_mirr = GMaterial("HTCCECIMirr")
    eci_mirr.description = "Measured reflectivity for Al+MgF2 coated on acryl sheets"
    eci_mirr.density = 2.9007
    eci_mirr.addMaterialWithFractionalMass("G4_Al", 0.331)
    eci_mirr.addMaterialWithFractionalMass("G4_Mg", 0.261)
    eci_mirr.addMaterialWithFractionalMass("G4_F", 0.408)
    eci_mirr.photonEnergy = PENERGY_MIRR
    eci_mirr.reflectivity = REFLECTIVITY_ALMGF2_MIRR
    eci_mirr.publish(configuration)

    # same coating, measured on a Winston cone at grazing incidence, AJRP 10/08/2012
    eci_wc = GMaterial("HTCCECIWC")
    eci_wc.description = "Measured reflectivity for Al+MgF2 coated on Winston cone"
    eci_wc.density = 2.9007
    eci_wc.addMaterialWithFractionalMass("G4_Al", 0.331)
    eci_wc.addMaterialWithFractionalMass("G4_Mg", 0.261)
    eci_wc.addMaterialWithFractionalMass("G4_F", 0.408)
    eci_wc.photonEnergy = PENERGY_MIRR
    eci_wc.reflectivity = REFLECTIVITY_ALMGF2_WC
    eci_wc.publish(configuration)

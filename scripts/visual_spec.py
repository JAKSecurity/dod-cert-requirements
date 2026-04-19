"""Visual-layout spec for the refreshed xlsx Certification Analysis tab.

Sourced from a read of Jeff's Jan 2025 Certification Analysis sheet with new
V2.1 certs and roles slotted into his existing structure. Color palette is
a fresh one (Jan 2025's colors are theme-based and not worth extracting byte-
by-byte — what matters is per-vendor differentiation and proficiency shading).
"""

# ----- Vendor short names + ordering -----
# Key = as it appears in V2.1 Certification Repository 'Vendor' column
# Value = short form that appears in the output xlsx's vendor group header.
VENDOR_SHORT_NAMES = {
    "CompTIA, Inc.": "CompTIA",
    "EC-Council - International Council of E-Commerce Consultants": "EC-Council",
    "EC-Council - International Council of E-Commerce Consultants, Inc.": "EC-Council",
    "Federal IT Security Institute": "FITSI",
    "GIAC - Global Information Assurance Certification": "GIAC (SANS)",
    "ISACA": "ISACA",
    "ISACA - Information Systems Audit and Control Association": "ISACA",
    "(ISC)2 - International Information System Security Certification Consortium, Inc.": "(ISC)2",
    "(ISC)2": "(ISC)2",
    "Logical Operations, Inc. dba CERTNEXUS": "CertNexus",
    "Cisco Systems": "CISCO",
    "CISCO Systems": "CISCO",
    "Rocheston LLC": "RCCE",
    "Rocheston": "RCCE",
    "mile2": "mile2",
    "Mile2": "mile2",
    "United America Technoloiges, LLC": "mile2",  # sic: DoD's typo for 'Technologies' — mile2's legal entity
    "Defense Acquisition University": "DAWIA",
}

# Vendor display order (left-to-right in the pivot table).
# Mirrors Jan 2025 ordering for shared vendors; new vendors (DAWIA) appended.
VENDOR_ORDER = [
    "CompTIA",
    "RCCE",         # moved between CompTIA and EC-Council per Jeff v7 layout
    "EC-Council",
    "FITSI",
    "GIAC (SANS)",
    "ISACA",
    "(ISC)2",
    "CertNexus",
    "CISCO",
    "mile2",
    "DAWIA",
]

# ----- Cert short names -----
# Maps V2.1 DoD-verbose cert acronyms to Jeff's short form.
# Entries not listed pass through unchanged.
CERT_SHORT_NAMES = {
    "Network+": "Net+",
    "Security+": "Sec+",
    "PenTest+": "PenTest",
    "SecurityX/CASP+": "CASP+",
    "SecurityX / CASP+": "CASP+",
    "CCNP Security": "CCNP-S",
    "CCNP Enterprise": "CCNP-E",
    "CGRC/CAP": "CGRC",
    "CISSP-ISSAP": "ISSAP",
    "CISSP-ISSEP": "ISSEP",
    "CISSP-ISSMP": "ISSMP",
    # The vendor group header already says DAWIA; drop the prefix on each
    # cert so the rotated headers need less row height.
    "DAWIA LCL Foundational": "LCL-F",
    "DAWIA LCL Advanced": "LCL-A",
    "DAWIA PM Practioner": "PM-P",  # sic: DoD typo for 'Practitioner'
    "DAWIA PM Advanced": "PM-A",
    "RCCE Level 1": "RCCE-1",
}

# ----- Cert order within each vendor -----
# Mirrors Jan 2025 order for shared certs. New V2.1 certs are appended to
# their vendor group. If a V2.1 cert's vendor doesn't match any key here,
# the cert goes into whichever vendor group V2.1's source data assigns it to
# (appended to the end of that group).
CERT_ORDER_BY_VENDOR = {
    "CompTIA": ["A+", "Net+", "Sec+", "Cloud+", "PenTest", "CySA+", "CASP+"],
    "EC-Council": ["CND", "CEH", "CEH(P)", "CHFI", "ECIH", "CCISO"],
    "FITSI": ["FITSP-O", "FITSP-D", "FITSP-A", "FITSP-M"],
    "GIAC (SANS)": [
        "GISF", "GFACT", "GICSP", "GSEC", "GCLD", "GCIA", "GCIH", "GCSA",
        "GPEN", "GCED", "GCFE", "GSLC", "GSNA", "GCFA",
        # V2.1-new GIAC certs:
        "GCTI", "GDSA", "GREM", "GMON", "GRID",
    ],
    "ISACA": ["CISA", "CISM"],
    "(ISC)2": ["CC", "SSCP", "CCSP", "CSSLP", "CGRC", "CISSP", "ISSAP", "ISSEP", "ISSMP"],
    "CertNexus": ["CFR", "CSC"],
    "CISCO": ["CCNA", "CBROPS", "CCNP-S", "CCNP-E"],
    "RCCE": ["RCCE-1"],  # V2.1: only 'RCCE Level 1' (Jan 2025's CCE is gone in V2.1)
    "mile2": ["CISSO", "CPTE"],
    "DAWIA": ["DAWIA-LCL-F", "DAWIA-LCL-A", "DAWIA-PM-P", "DAWIA-PM-A"],
}

# ----- Role order -----
# Mirrors Jan 2025 rows 4-26 + 32-45 (with row 31 CY 101 separator between).
# V2.1-new roles (111, 121, 131, 132, 311, 312, 331, 332, 422, 461, 621) are
# appended to the appropriate section below.
# V2.1-pending-review roles (462, 731, 901) are omitted; they get a footnote.
ROLE_ORDER = [
    # --- IT domain (Jan 2025 top section) ---
    "411", "421", "431", "441", "451",
    "632", "641", "651", "661", "671",
    # --- Cybersecurity / cyber defense ---
    "212",
    "511", "521", "531", "541",
    "611", "612", "622", "631", "652",
    "722", "723",
    # --- V2.1-new roles (IT/Cybersecurity domain) ---
    "461",  # Systems Security Analyst — Cybersecurity
    "621",  # Software Developer — Software Engineering
    "422",  # Data Analyst — Data/AI
    # --- CY 101 separator here (handled specially in the builder) ---
    # --- Cyber Enablers (below CY 101 note) ---
    "211", "221", "711", "712", "732",
    "751", "752",
    "801", "802", "803", "804", "805",
    # --- V2.1-new roles (Cyber Effects / Intel domains) ---
    "111", "121", "131", "132",
    "311", "312", "331", "332",
]

# Role code BEFORE which the CY 101 separator row is inserted in the output.
# (In Jan 2025 the separator appeared between row 26 = 723 COMSEC Manager and
# row 32 = 211 Forensics Analyst. We keep the same location relative to
# shared roles.)
CY101_SEPARATOR_BEFORE_CODE = "211"

# ----- Role row highlights -----
# Map role_code → fill color (ARGB hex). Derived from Jan 2025.
ROLE_ROW_HIGHLIGHTS = {
    "451": "FFFF0000",  # red — "req'd for admin access"
}

# Display name overrides for roles where Jeff's Jan 2025 wording differs
# from DoD V2.1's verbose form. Key = WRC code, Value = display text after "(CODE) ".
ROLE_NAME_OVERRIDES = {
    "451": "System Admin (req'd for admin access)",
}

# ----- Color palette per vendor -----
# Two forms of palette:
#
#   VENDOR_PALETTE[v] = {"base": ..., "l1": ..., "l2": ..., "l3": ...}
#     Used for the vendor group header row (row 2) — one color per vendor.
#
#   VENDOR_HUE_SPEC[v] = {"hue_start": H, "hue_end": H, "sat": S, ...}
#     Drives PER-CERT color generation: as we walk across the N cert columns
#     for vendor v, we interpolate hue from hue_start to hue_end. Each cert
#     ends up with its own distinct color; proficiency levels shade that
#     color lighter (Basic) to darker (Advanced).
#
# This matches Jan 2025's aesthetic where GIAC's 14 cert columns walk pink
# through purple through dark red, CompTIA walks light gray through dark gray
# with a pink accent for CySA+, etc. Colors are hue-interpolated, not
# hand-picked (Jeff: "colors are not important; shading and differentiation
# by vendor is").

VENDOR_PALETTE = {
    "CompTIA":     {"base": "FF595959", "l1": "FFE7E6E6", "l2": "FFBFBFBF", "l3": "FF808080"},
    "EC-Council":  {"base": "FF2E75B6", "l1": "FFDDEBF7", "l2": "FFADC6E3", "l3": "FF5B9BD5"},
    "FITSI":       {"base": "FFC05A00", "l1": "FFFCE4D6", "l2": "FFF4B084", "l3": "FFED7D31"},
    # GIAC covers ~19 certs; Jeff's guidance: just 3 colors total for the
    # proficiency levels, transitioning pink -> purple with darkness.
    # Explicit departure from "darker = harder" hue consistency.
    "GIAC (SANS)": {"base": "FF4B1E6B", "l1": "FFF5C3D2", "l2": "FFD87A9C", "l3": "FF4B1E6B"},
    "ISACA":       {"base": "FFBF8F00", "l1": "FFFFF2CC", "l2": "FFFFD966", "l3": "FFFFC000"},
    "(ISC)2":      {"base": "FF0F7287", "l1": "FFD3EEF3", "l2": "FF9ED1DB", "l3": "FF4BACC6"},
    "CertNexus":   {"base": "FF996633", "l1": "FFE8DCCA", "l2": "FFC99D66", "l3": "FFA47B4A"},
    "CISCO":       {"base": "FF548235", "l1": "FFE2EFDA", "l2": "FFA9D08E", "l3": "FF70AD47"},
    "RCCE":   {"base": "FF8B2635", "l1": "FFF1D6DA", "l2": "FFC66573", "l3": "FF8B2635"},  # burgundy
    "mile2":       {"base": "FF5B2C6F", "l1": "FFE4D3EC", "l2": "FFA285B2", "l3": "FF5B2C6F"},  # purple
    "DAWIA":       {"base": "FF7F6000", "l1": "FFFFF2CC", "l2": "FFE2C879", "l3": "FFBF9000"},
}

DEFAULT_PALETTE = {
    "base": "FF595959", "l1": "FFD9D9D9", "l2": "FFA6A6A6", "l3": "FF7F7F7F",
}

# Per-vendor font size for the row-2 vendor group header. Vendors with
# short spans (few cert columns) need smaller fonts so the name fits.
VENDOR_HEADER_FONT_SIZE = {
    "RCCE": 7,       # only 1 column, needs tiny font
    "CertNexus": 9,  # 2 columns, slightly smaller than default
}
DEFAULT_VENDOR_HEADER_FONT_SIZE = 11

# Hue/saturation range per vendor. Hues in degrees (0-360), saturation 0.0-1.0.
# The per-cert palette generator walks hue linearly across the vendor's certs.
# `sat`=0 gives a monochrome (grayscale) family, used for CompTIA.
VENDOR_HUE_SPEC = {
    # CompTIA: grays walking from light to dark, but CySA+ and CASP+ break out
    # with pink/black accents. Handled via explicit per-cert overrides below.
    "CompTIA":     {"hue_start":   0, "hue_end":   0,  "sat": 0.00},
    "EC-Council":  {"hue_start": 205, "hue_end": 240,  "sat": 0.55},  # blue to indigo
    "FITSI":       {"hue_start":  25, "hue_end":  35,  "sat": 0.70},  # orange tight band
    "GIAC (SANS)": {"hue_start": 320, "hue_end": 260,  "sat": 0.70},  # pink -> purple (wrap backwards)
    "ISACA":       {"hue_start":  40, "hue_end":  35,  "sat": 0.85},  # amber
    "(ISC)2":      {"hue_start": 185, "hue_end": 220,  "sat": 0.55},  # cyan -> blue
    "CertNexus":   {"hue_start":  30, "hue_end":  25,  "sat": 0.45},  # warm brown
    "CISCO":       {"hue_start": 115, "hue_end": 145,  "sat": 0.55},  # green band
    "RCCE":   {"hue_start": 350, "hue_end": 355,  "sat": 0.55},  # burgundy
    "mile2":       {"hue_start": 280, "hue_end": 290,  "sat": 0.50},  # purple
    "DAWIA":       {"hue_start":  40, "hue_end":  50,  "sat": 0.85},  # gold range
}

# Per-cert overrides. Takes precedence over the vendor hue walk.
# Format: {cert_short_name: (hue, sat)}. Lightness is still level-dependent.
# (Empty — no special-case colors at present.)
CERT_COLOR_OVERRIDES: dict[str, tuple[float, float]] = {}

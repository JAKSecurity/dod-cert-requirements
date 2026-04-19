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
    "Rocheston LLC": "Rocheston",
    "Rocheston": "Rocheston",
    "mile2": "mile2",
    "Mile2": "mile2",
    "United America Technoloiges, LLC": "mile2",  # sic: DoD's typo for 'Technologies' — mile2's legal entity
    "Defense Acquisition University": "DAWIA",
}

# Vendor display order (left-to-right in the pivot table).
# Mirrors Jan 2025 ordering for shared vendors; new vendors (DAWIA) appended.
VENDOR_ORDER = [
    "CompTIA",
    "EC-Council",
    "FITSI",
    "GIAC (SANS)",
    "ISACA",
    "(ISC)2",
    "CertNexus",
    "CISCO",
    "Rocheston",
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
    "DAWIA LCL Foundational": "DAWIA-LCL-F",
    "DAWIA LCL Advanced": "DAWIA-LCL-A",
    "DAWIA PM Practioner": "DAWIA-PM-P",  # sic: DoD typo for 'Practitioner'
    "DAWIA PM Advanced": "DAWIA-PM-A",
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
    "Rocheston": ["RCCE-1"],  # V2.1: only 'RCCE Level 1' (Jan 2025's CCE is gone in V2.1)
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
# Base = shade used for vendor group header row.
# l1/l2/l3 = lightest/medium/darkest fills for data cells at Basic/Intermediate/Advanced.
# Within a vendor group all cert columns share the same base; intra-column
# differentiation comes from proficiency-level shade.
VENDOR_PALETTE = {
    "CompTIA":     {"base": "FF6D6D6D", "l1": "FFE0E0E0", "l2": "FFB0B0B0", "l3": "FF808080"},  # gray
    "EC-Council":  {"base": "FF2E75B6", "l1": "FFDDEBF7", "l2": "FFADC6E3", "l3": "FF5B9BD5"},  # blue
    "FITSI":       {"base": "FFC05A00", "l1": "FFFCE4D6", "l2": "FFF4B084", "l3": "FFED7D31"},  # orange
    "GIAC (SANS)": {"base": "FF7030A0", "l1": "FFE4D7F0", "l2": "FFB197D6", "l3": "FF8064A2"},  # purple
    "ISACA":       {"base": "FFBF8F00", "l1": "FFFFF2CC", "l2": "FFFFD966", "l3": "FFFFC000"},  # amber
    "(ISC)2":      {"base": "FF0F7287", "l1": "FFD3EEF3", "l2": "FF9ED1DB", "l3": "FF4BACC6"},  # teal
    "CertNexus":   {"base": "FF996633", "l1": "FFE8DCCA", "l2": "FFC99D66", "l3": "FFA47B4A"},  # brown
    "CISCO":       {"base": "FF548235", "l1": "FFE2EFDA", "l2": "FFA9D08E", "l3": "FF70AD47"},  # green
    "Rocheston":   {"base": "FF6F6000", "l1": "FFECE4BD", "l2": "FFC8B56B", "l3": "FF938953"},  # olive
    "mile2":       {"base": "FF1F4E3C", "l1": "FFCCE5DC", "l2": "FF7AB89A", "l3": "FF2E7D5B"},  # forest green
    "DAWIA":       {"base": "FF7F6000", "l1": "FFFFF2CC", "l2": "FFE2C879", "l3": "FFBF9000"},  # dark gold
}

# Used for any vendor not in VENDOR_PALETTE (defensive fallback).
DEFAULT_PALETTE = {
    "base": "FF595959", "l1": "FFD9D9D9", "l2": "FFA6A6A6", "l3": "FF7F7F7F",
}

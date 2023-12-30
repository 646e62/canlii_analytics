#!/usr/bin/env python3

# Convert Canadian provincial/territorial jurisdiction shorthands to full names

import re
from django.utils.html import escape

# Define a dictionary to map jurisdiction codes to full names
JURISDICTIONAL_MAPPING = {
    "ca": "Canada (Federal)",
    "ab": "Alberta",
    "bc": "British Columbia",
    "mb": "Manitoba",
    "nb": "New Brunswick",
    "nl": "Newfoundland and Labrador",
    "ns": "Nova Scotia",
    "nt": "Northwest Territories",
    "nu": "Nunavut",
    "on": "Ontario",
    "pe": "Prince Edward Island",
    "qc": "Quebec",
    "sk": "Saskatchewan",
    "yk": "Yukon",
}

COURT_LEVEL_MAPPING = {
    "scc": "Supreme Court of Canada",
    "scc-l": "Supreme Court of Canada - Applications for Leave",
    "ukjcpc": "Judicial Committee of the Privy Council - Canadian cases",
    "fca": "Federal Court of Appeal",
    "fc": "Federal Court",
    "tcc": "Tax Court of Canada",
    "exch": "Exchequer Court of Canada",
    "cmac": "Court Martial Appeal Court of Canada",
    "cm": "Courts Martial",
    "forep": "Foreign reported decisions",
    "cart": "Canada Agricultural Review Tribunal",
    "cer": "Canada Energy Regulator",
    "cirb": "Canada Industrial Relations Board",
    "cbsc": "Canadian Broadcast Standards Council",
    "chrt": "Canadian Human Rights Tribunal",
    "citt": "Canadian International Trade Tribunal",
    "ciro": "Canadian Investment Regulatory Organization",
    "cicc": "College of Immigration and Citizenship Consultants",
    "cacp": "Commissioner of Patents",
    "cact": "Competition Tribunal",
    "cb": "Copyright Board of Canada",
    "eptc": "Environmental Protection Tribunal of Canada",
    "caci": "Federal Commission of Inquiry",
    "pslreb": "Federal Public Sector Labour Relations and Employment Board",
    "irb": "Immigration and Refugee Board of Canada",
    "oic": "Information Commissioner of Canada",
    "iiroc": "Investment Industry Regulatory Organization of Canada",
    "cala": "Labour Arbitration Awards",
    "camfda": "Mutual Fund Dealers Association of Canada",
    "ohstc": "Occupational Health and Safety Tribunal Canada",
    "pec": "Pay Equity Commissioner",
    "pcc": "Privacy Commissioner of Canada",
    "psdpt": "Public Servants Disclosure Protection Tribunal",
    "pssrb": "Public Service Labour Relations Board",
    "psst": "Public Service Staffing Tribunal",
    "sopf": "Ship-source Oil Pollution Fund",
    "sst": "Social Security Tribunal of Canada",
    "sct": "Specific Claims Tribunal Canada",
    "tmob": "Trademarks Opposition Board",
    "tatc": "Transportation Appeal Tribunal of Canada",
    "vrab": "Veterans Review and Appeal Board of Canada",
    "bcca": "Court of Appeal for British Columbia",
    "bcsc": "Supreme Court of British Columbia",
    "bcpc": "Provincial Court of British Columbia",
    "bccnm": "British Columbia College of Nurses and Midwives",
    "bcctc": "British Columbia Container Trucking Commissioner",
    "bcest": "British Columbia Employment Standards Tribunal",
    "bceab": "British Columbia Environmental Appeal Board",
    "bchab": "British Columbia Hospital Appeal Board",
    "bchrt": "British Columbia Human Rights Tribunal",
    "bclcrb": "British Columbia Liquor and Cannabis Regulation Branch",
    "bcsec": "British Columbia Securities Commission",
    "bcwcat": "British Columbia Workers' Compensation Appeal Tribunal",
    "bccrt": "Civil Resolution Tribunal of British Columbia",
    "bccds": "College of Dental Surgeons of British Columbia",
    "bccps": "College of Physicians and Surgeons of British Columbia",
    "bcccalab": "Community Care and Assisted Living Appeal Board",
    "bcerat": "Energy Resource Appeal Tribunal",
    "bcfst": "Financial Services Tribunal",
    "bcfac": "Forest Appeals Commission",
    "bchprb": "Health Professions Review Board of British Columbia",
    "bcipc": "Information and Privacy Commissioner",
    "bcla": "Labour Arbitration Awards",
    "bclrb": "Labour Relations Board",
    "lsbc": "Law Society of British Columbia",
    "bcorl": "Office of the Registrar of Lobbyists",
    "bcrec": "Real Estate Council of British Columbia",
    "bcrmb": "Registrar of Mortgage Brokers",
    "bcstab": "Skilled Trades BC Appeal Board",
    "bcsfi": "Superintendent of Financial Institutions",
    "bcsp": "Superintendent of Pensions",
    "bcsre": "Superintendent of Real Estate",
    "abca": "Court of Appeal of Alberta",
    "abkb": "Court of King's Bench of Alberta",
    "abqb": "Court of Queen's Bench of Alberta",
    "abcj": "Alberta Court of Justice",
    "abpc": "Provincial Court of Alberta",
    "abci": "Alberta Commission of Inquiry",
    "abesa": "Alberta Employment Standards Appeals",
    "abeab": "Alberta Environmental Appeal Board",
    "abgaa": "Alberta Grievance Arbitration Awards",
    "ahrc": "Alberta Human Rights Commission",
    "ablrb": "Alberta Labour Relations Board",
    "ablprt": "Alberta Land and Property Rights Tribunal",
    "ablcb": "Alberta Land Compensation Board",
    "ablerb": "Alberta Law Enforcement Review Board",
    "ablcsab": "Alberta Licence and Community Standards Appeal Board",
    "abmgb": "Alberta Municipal Government Board",
    "abplab": "Alberta Public Lands Appeal Board",
    "abrtdrs": "Alberta Residential Tenancy Dispute Resolution Service",
    "absec": "Alberta Securities Commission",
    "absrb": "Alberta Surface Rights Board",
    "abtsb": "Alberta Transportation Safety Board",
    "abwcac": "Appeals Commission for Alberta Workers' Compensation",
    "abcgyarb": "Calgary Assessment Review Board",
    "cgysdab": "Calgary Subdivision & Development Appeal Board",
    "abcpa": "Chartered Professional Accountants of Alberta",
    "abcpsdc": "College of Physicians and Surgeons Discipline Committee",
    "abecarb": "Edmonton Composite Assessment Review Board",
    "abelarb": "Edmonton Local Assessment Review Board",
    "abesdab": "Edmonton Subdivision and Development Appeal Board",
    "abhraat": "Horse Racing Alberta Appeal Tribunal",
    "abls": "Law Society of Alberta",
    "aboipc": "Office of the Information and Privacy Commissioner",
    "abpaca": "Physiotherapy Alberta College Association",
    "abreca": "Real Estate Council of Alberta",
    "absra": "SafeRoads Alberta",
    "skca": "Court of Appeal for Saskatchewan",
    "skkb": "Court of King's Bench for Saskatchewan",
    "skqb": "Court of Queen's Bench for Saskatchewan",
    "skpc": "Provincial Court of Saskatchewan",
    "skdc": "Saskatchewan District Court",
    "sksu": "Saskatchewan Surrogate Court",
    "skufc": "Saskatchewan Unified Family Court",
    "skatmpa": "Appeal Tribunal under the Medical Profession Act",
    "skaia": "Automobile Injury Appeal Commission",
    "sksec": "Financial and Consumer Affairs Authority of Saskatchewan",
    "skipc": "Information and Privacy Commissioner",
    "skla": "Labour Arbitration Awards",
    "sklss": "Law Society of Saskatchewan",
    "skac": "Saskatchewan Assessment Commission",
    "skfca": "Saskatchewan Board of Review under the Farmers' Creditors Arrangement Act, 1934",
    "skcppdc": "Saskatchewan College of Pharmacy Professionals",
    "skhrc": "Saskatchewan Human Rights Commission",
    "skhrt": "Saskatchewan Human Rights Tribunal",
    "sklrb": "Saskatchewan Labour Relations Board",
    "sklgb": "Saskatchewan Local Government Board",
    "skmt": "Saskatchewan Master of Titles",
    "skmb": "Saskatchewan Municipal Board",
    "skmbr": "Saskatchewan Municipal Boards of Revision",
    "skort": "Saskatchewan Office of Residential Tenancies",
    "skpmb": "Saskatchewan Provincial Mediation Board",
    "skrec": "Saskatchewan Real Estate Commission",
    "mbca": "Court of Appeal of Manitoba",
    "mbkb": "Court of King's Bench of Manitoba",
    "mbqb": "Court of Queen's Bench of Manitoba",
    "mbpc": "Provincial Court of Manitoba",
    "mbcpsdc": "College of Physicians & Surgeons of Manitoba Discipline Committee",
    "mbla": "Labour Arbitration Awards",
    "mbls": "Law Society of Manitoba",
    "mbhab": "Manitoba Health Appeal Board",
    "mbhrc": "Manitoba Human Rights Commission",
    "mblb": "Manitoba Labour Board",
    "mbsec": "Manitoba Securities Commission",
    "onca": "Court of Appeal for Ontario",
    "onsc": "Superior Court of Justice",
    "onscdc": "Divisional Court",
    "onscsm": "Small Claims Court",
    "oncj": "Ontario Court of Justice",
    "onafraat": "Agriculture, Food & Rural Affairs Appeal Tribunal",
    "onagc": "Alcohol and Gaming Commission of Ontario",
    "onarb": "Assessment Review Board",
    "onape": "Association of Professional Engineers of Ontario",
    "onbcc": "Building Code Commission",
    "oncmt": "Capital Markets Tribunal",
    "oncpa": "Chartered Professional Accountants of Ontario",
    "oncfsrb": "Child and Family Services Review Board",
    "oncaspd": "College of Audiologists and Speech-Language Pathologists of Ontario",
    "oncocoo": "College of Chiropodists of Ontario",
    "oncdho": "College of Dental Hygienists of Ontario",
    "oncmto": "College of Massage Therapists of Ontario",
    "oncno": "College of Nurses of Ontario Discipline Committee",
    "oncot": "College of Occupational Therapists of Ontario",
    "onco": "College of Optometrists of Ontario",
    "oncpo": "College of Physiotherapists of Ontario",
    "oncpd": "College of Psychologists of Ontario",
    "oncrpo": "College of Registered Psychotherapists and Registered Mental Health Therapists of Ontario",
    "onctcmpao": "College of Traditional Chinese Medicine Practitioners and Acupuncturists of Ontario",
    "oncat": "Condominium Authority Tribunal",
    "onccb": "Consent and Capacity Board",
    "onconrb": "Conservation Review Board",
    "oncicb": "Criminal Injuries Compensation Board",
    "onert": "Environmental Review Tribunal",
    "onfst": "Financial Services Tribunal",
    "ongsb": "Grievance Settlement Board",
    "onhparb": "Health Professions Appeal and Review Board",
    "onhsarb": "Health Services Appeal and Review Board",
    "onhrap": "Horse Racing Appeal Panel",
    "onhrt": "Human Rights Tribunal of Ontario",
    "onipc": "Information and Privacy Commissioner Ontario",
    "onla": "Labour Arbitration Awards",
    "onltb": "Landlord and Tenant Board",
    "onlst": "Law Society Tribunal",
    "onlpat": "Local Planning Appeal Tribunal",
    "onmlt": "Mining and Lands Tribunal",
    "onmic": "Municipal Integrity Commissioners of Ontario",
    "onnfppb": "Normal Farm Practices Protection Board",
    "onombud": "Office of the Ombudsman of Ontario",
    "onacrb": "Ontario Animal Care Review Board",
    "oncpc": "Ontario Civilian Police Commission",
    "oncece": "Ontario College of Early Childhood Educators",
    "oncpdc": "Ontario College of Pharmacists Discipline Committee",
    "oncswssw": "Ontario College of Social Workers and Social Service Workers",
    "onoct": "Ontario College of Teachers",
    "ondr": "Ontario Court of the Drainage Referee",
    "oncrb": "Ontario Custody Review Board",
    "onfscdrs": "Ontario Financial Services Commission - Dispute Resolution Services",
    "onfsc": "Ontario Fire Safety Commission",
    "onlrb": "Ontario Labour Relations Board",
    "onlt": "Ontario Land Tribunal",
    "onlat": "Ontario Licence Appeal Tribunal",
    "onpeht": "Ontario Pay Equity Hearings Tribunal",
    "onpprb": "Ontario Physician Payment Review Board",
    "onpsdt": "Ontario Physicians and Surgeons Discipline Tribunal",
    "onpsgb": "Ontario Public Service Grievance Board",
    "onrc": "Ontario Racing Commission",
    "onsec": "Ontario Securities Commission",
    "onsbt": "Ontario Social Benefits Tribunal",
    "onset": "Ontario Special Education  (English) Tribunal",
    "onwsiat": "Ontario Workplace Safety and Insurance Appeals Tribunal",
    "onwsib": "Ontario Workplace Safety and Insurance Board",
    "onrcdso": "Royal College of Dental Surgeons of Ontario",
    "onst": "Skilled Trades Ontario",
    "ontlab": "Toronto Local Appeal Body",
    "qcca": "Court of Appeal of Quebec",
    "qccs": "Superior Court",
    "qccq": "Court of Quebec",
    "qctdp": "Human Rights Tribunal",
    "qctp": "Professions Tribunal",
    "qccm": "Municipal Courts",
    "qctaq": "Administrative Tribunal of Québec",
    "qcoagbrn": "Arbitration - The Guarantee Plan For New Residential Buildings",
    "qccdbq": "Barreau du Québec  Disciplinary Council",
    "qccdcm": "Collège des médecins du Québec Disciplinary Council",
    "qccdp": "Comité de déontologie policière",
    "qcoaciq": "Comité de discipline de l'organisme d'autoréglementation du courtage immobilier du Québec",
    "qccdchad": "Comité de discipline de la Chambre de l'assurance de dommages",
    "qccdcsf": "Comité de discipline de la Chambre de la sécurité financière",
    "qccai": "Commission d'accès à l'information",
    "qccalp": "Commission d'appel en matière de lésions professionnelles du Québec",
    "qcces": "Commission de l'équité salariale",
    "qccfp": "Commission de la fonction publique",
    "qccsst": "Commission de la santé et de la sécurité du travail",
    "qccptaq": "Commission de protection du territoire agricole du Québec",
    "qccraaap": "Commission de reconnaissance des associations d'artistes et des associations de producteurs",
    "qcclp": "Commission des lésions professionnelles du Québec",
    "qccnesst": "Commission des normes, de l’équité, de la santé et de la sécurité du travail",
    "qccrt": "Commission des relations du travail",
    "qccsj": "Commission des services juridiques",
    "qcctq": "Commission des transports du Québec",
    "qccvm": "Commission des valeurs mobilières du Québec",
    "qccmnq": "Commission municipale du Québec",
    "qcoaq": "Conseil de discipline de l'Ordre des acupuncteurs du Québec",
    "qcadmaq": "Conseil de discipline de l'Ordre des administrateurs agréés du Québec",
    "qcagq": "Conseil de discipline de l'Ordre des agronomes du Québec",
    "qcoarq": "Conseil de discipline de l'Ordre des architectes du Québec",
    "qcoagq": "Conseil de discipline de l'Ordre des arpenteurs-géomètres du Québec",
    "qcoapq": "Conseil de discipline de l'Ordre des audioprothésistes du Québec",
    "qcocq": "Conseil de discipline de l'Ordre des chiropraticiens du Québec",
    "qccpa": "Conseil de discipline de l'Ordre des comptables professionnels agréés du Québec",
    "qccdcrim": "Conseil de discipline de l'Ordre des criminologues du Québec",
    "qcodq": "Conseil de discipline de l'Ordre des dentistes du Québec",
    "qcoeq": "Conseil de discipline de l'Ordre des ergothérapeutes du Québec",
    "qccdoiia": "Conseil de discipline de l'Ordre des infirmières et infirmiers auxiliaires du Québec",
    "qccdoii": "Conseil de discipline de l'Ordre des infirmières et infirmiers du Québec",
    "qccdoiq": "Conseil de discipline de l'Ordre des ingénieurs du Québec",
    "qccdomv": "Conseil de discipline de l'Ordre des médecins vétérinaires du Québec",
    "qccdoooq": "Conseil de discipline de l'Ordre des opticiens d'ordonnances du Québec",
    "qcooq": "Conseil de discipline de l'Ordre des optométristes du Québec",
    "qccdopq": "Conseil de discipline de l'Ordre des pharmaciens du Québec",
    "qcopodq": "Conseil de discipline de l'Ordre des podiatres du Québec",
    "qcopq": "Conseil de discipline de l'Ordre des psychologues du Québec",
    "qccdosfq": "Conseil de discipline de l'Ordre des sages-femmes du Québec",
    "qcopsq": "Conseil de discipline de l'Ordre des sexologues du Québec",
    "qccdottdq": "Conseil de discipline de l'Ordre des techniciens et techniciennes dentaires du Québec",
    "qcotimro": "Conseil de discipline de l'Ordre des technologues en imagerie médicale et en radio-oncologie du Québec",
    "qcotpq": "Conseil de discipline de l'Ordre des technologues professionnels du Québec",
    "qcouq": "Conseil de discipline de l'Ordre des urbanistes du Québec",
    "qcoppq": "Conseil de discipline de l'Ordre professionnel de la physiothérapie du Québec",
    "qcochq": "Conseil de discipline de l'Ordre professionnel des chimistes du Québec",
    "qccdrhri": "Conseil\n de discipline de l'Ordre professionnel des conseillers en ressources \nhumaines et en relations industrielles agrées du Québec",
    "qcodlq": "Conseil de discipline de l'Ordre professionnel des denturologistes du Québec",
    "qcoeaq": "Conseil de discipline de l'Ordre professionnel des évaluateurs agréés du Québec",
    "qcoifq": "Conseil de discipline de l'Ordre professionnel des ingénieurs forestiers du Québec",
    "qcooaq": "Conseil de discipline de l'Ordre professionnel des orthophonistes et audiologistes du Québec",
    "qcotmq": "Conseil de discipline de l'Ordre professionnel des technologistes médicaux du Québec",
    "qcottiaq": "Conseil de discipline de l'Ordre professionnel des traducteurs, terminologues et interprètes agréés du Québec",
    "qcotstcfq": "Conseil de discipline de l'Ordre professionnel des travailleurs sociaux et des thérapeutes conjugaux et familiaux du Québec",
    "qccdhj": "Conseil de discipline de la Chambre des huissiers de justice du Québec",
    "qccdnq": "Conseil de discipline de la Chambre des notaires du Québec",
    "qccdccoq": "Conseil de discipline des Conseillers et conseillères d'orientation du Québec",
    "qccdppq": "Conseil de discipline des psychoéducateurs et psychoéducatrices du Québec",
    "qccja": "Conseil de la justice administrative",
    "qccmq": "Conseil de la magistrature",
    "qccse": "Conseil des services essentiels",
    "qccmeq": "Corporation des maîtres électriciens du Québec",
    "qccmpmq": "Corporation of Master Pipe-Mechanics of Québec",
    "qcla": "Labour Arbitration Awards (including Conférence des arbitres)",
    "qcct": "Labour Commissioner",
    "qctt": "Labour Court",
    "qcolf": "Office de la langue française",
    "qcohdq": "Ordre des hygiénistes dentaires du Québec",
    "qcopdq": "Ordre professionnel des diététistes du Québec",
    "qcopgq": "Ordre professionnel des géologues du Québec",
    "qcopiq": "Ordre professionnel des inhalothérapeutes du Québec",
    "qcamf": "Quebec Autorité des marchés financiers",
    "qcrde": "Régie de l'énergie",
    "qcracj": "Régie des alcools des courses et des jeux",
    "qcrmaaq": "Régie des marchés agricoles et alimentaires du Québec",
    "qcrbq": "Régie du Bâtiment - licences d'entrepreneur de construction",
    "qctmf": "Tribunal administratif des marchés financiers",
    "qctal": "Tribunal administratif du logement",
    "qctat": "Tribunal administratif du travail",
    "qctaa": "Tribunal d'arbitrage (performing, recording and film artists)",
    "qcta": "Tribunal d'arbitrage (RQ and CARRA)",
    "nbca": "Court of Appeal of New Brunswick",
    "nbkb": "Court of King's Bench of New Brunswick",
    "nkqb": "Court of Queen's Bench of New Brunswick",
    "nbpc": "Provincial Court",
    "nbbihra": "Board of Inquiry Under the Human Rights Act",
    "nbfcsc": "Financial and Consumer Services Commission",
    "nbfcst": "Financial and Consumer Services Tribunal",
    "nbla": "Labour Arbitration Awards",
    "nblsb": "Law Society of New Brunswick",
    "nbapab": "New Brunswick Assessment and Planning Appeal Board",
    "nbcph": "New Brunswick College of Pharmacists",
    "nbleb": "New Brunswick Labour and Employment Board",
    "nbrea": "New Brunswick Real Estate Association",
    "nbombud": "Ombud New Brunswick",
    "nbwcat": "Workers’ Compensation Appeals Tribunal",
    "nsca": "Nova Scotia Court of Appeal",
    "nssc": "Supreme Court of Nova Scotia",
    "nssf": "Supreme Court of Nova Scotia (Family Division)",
    "nspc": "Provincial Court of Nova Scotia",
    "nssm": "Small Claims Court",
    "nspr": "Nova Scotia Probate Court",
    "nsfc": "Nova Scotia Family Court",
    "nscps": "College of Physicians and Surgeons of Nova Scotia",
    "nsla": "Labour Arbitration Awards",
    "nsawab": "Nova Scotia Animal Welfare Appeal Board",
    "nsbs": "Nova Scotia Barristers' Society Hearing Panel",
    "nshrc": "Nova Scotia Human Rights Commission",
    "nslb": "Nova Scotia Labour Board",
    "nslrb": "Nova Scotia Labour Relations Board",
    "nslst": "Nova Scotia Labour Standards Tribunal",
    "nsohsap": "Nova Scotia Occupational Health and Safety Appeal Panel",
    "nsprb": "Nova Scotia Police Review Board",
    "nssec": "Nova Scotia Securities Commission",
    "nssirt": "Nova Scotia Serious Incident Response Team",
    "nsuarb": "Nova Scotia Utility and Review Board",
    "nswcat": "Nova Scotia Workers' Compensation Appeals Tribunal",
    "nsoipc": "Office of the Information and Privacy Commissioner for Nova Scotia",
    "pescad": "Prince Edward Island Court of Appeal",
    "pesctd": "Supreme Court of Prince Edward Island",
    "pepc": "Provincial Court of Prince Edward Island",
    "peipc": "Information and Privacy Commissioner",
    "pela": "Labour Arbitration Awards",
    "peihrc": "Prince Edward Island Human Rights Commission",
    "pelrb": "Prince Edward Island Labour Relations Board",
    "peirac": "Prince Edward Island Regulatory & Appeals Commission",
    "nlca": "Court of Appeal of Newfoundland and Labrador",
    "nlsc": "Supreme Court of Newfoundland and Labrador",
    "nlpc": "Provincial Court of Newfoundland and Labrador",
    "nlcps": "College of Physicians and Surgeons of Newfoundland and Labrador",
    "nlipc": "Information and Privacy Commissioner",
    "nlla": "Labour Arbitration Awards",
    "nlls": "Law Society of Newfoundland and Labrador",
    "nlhrc": "Newfoundland and Labrador Human Rights Commission",
    "nllrb": "Newfoundland and Labrador Labour Relations Board",
    "nlpb": "Newfoundland and Labrador Pharmacy Board",
    "ykca": "Court of Appeal of Yukon",
    "yksc": "Supreme Court  of Yukon",
    "yktc": "Territorial Court of Yukon",
    "yksm": "Small Claims Court of the Yukon",
    "ytla": "Labour Arbitration Awards",
    "ykhrc": "Yukon Human Rights Commission (Board of Adjudication)",
    "ytpslrb": "Yukon Public Service Labour Relations Board",
    "ytrto": "Yukon Residential Tenancies Office",
    "yttlrb": "Yukon Teachers Labour Relations Board",
    "ntca": "Court of Appeal for the Northwest Territories",
    "ntsc": "Supreme Court of the Northwest Territories",
    "nttc": "Territorial Court of the Northwest Territories",
    "ntyjc": "Youth Justice Court",
    "ntlsb": "Employment Standards Appeals Office",
    "nthrap": "Human Rights Adjudication Panel",
    "ntla": "Labour Arbitration Awards",
    "ntls": "Law Society of the Northwest Territories",
    "ntwcat": "Northwest Territories and Nunavut Workers’ Compensation Appeals Tribunal",
    "ntaat": "Northwest Territories Assessment Appeal Tribunal",
    "ntipc": "Northwest Territories Information and Privacy Commissioner",
    "ntllb": "Northwest Territories Liquor Licensing Board",
    "ntro": "Rental Officer",
    "nuca": "Court of Appeal of Nunavut",
    "nucj": "Nunavut Court of Justice",
    "yjcn": "Youth Justice Court of Nunavut",
    "nuipc": "Information and Privacy Commissioner",
    "nula": "Labour Arbitration Awards",
    "nuls": "Law Society of Nunavut",
    "nuwcat": "Northwest Territories and Nunavut Workers’ Compensation Appeals Tribunal",
    "nuhrt": "Nunavut Human Rights Tribunal",
    "nusec": "Nunavut Registrar of Securities",
}


def convert_jurisdiction(jurisdiction: str) -> str:
    """
    Anticipate lowercase two-letter jurisdiction code and return full name.
    Convert to lowercase to avoid case sensitivity.
    """
    jurisdiction = jurisdiction.lower()

    # Use the dictionary to get the full name, or return the input if not found
    return JURISDICTIONAL_MAPPING.get(jurisdiction, jurisdiction)


# Convert Canadian court level shorthands to full names
# Define a dictionary to map court level codes to full names


def convert_court_level(court_level: str) -> str:
    """
    Anticipate lowercase two-letter court level code and return full name.
    Convert to lowercase to avoid case sensitivity.
    """
    court_level = court_level.lower()

    # Use the dictionary to get the full name, or return the input if not found
    return COURT_LEVEL_MAPPING.get(court_level, court_level)


def define_jurisprudential_network(urls):
    """
    Writes the URLs to a file.
    """

    # Initialize an empty list to store the dictionaries
    result_list = []

    # Loop through the URLs
    for url in urls:
        parts = url.split("/")  # Split the URL by "/"

        # Check if there are enough parts to create the dictionary
        if len(parts) >= 7:
            # Create an HTML anchor tag with the text and URL
            # Remove "_smooth" and ".html" from the primary key
            data_dict = {
                "primary_key": parts[6],
                "jurisdiction": convert_jurisdiction(parts[2]),
                "court_level": convert_court_level(parts[3]),
                "year": parts[5],
                "url": f"https://www.canlii.org{url}",  # Construct the full URL
            }

            # Escape the text to prevent HTML injection
            escaped_text = escape(f"{data_dict['primary_key']}")

            # Create the HTML anchor tag
            anchor_tag = f'<a href="{data_dict["url"]}">{escaped_text}</a>'

            result_list.append(
                f"{anchor_tag}: {data_dict['court_level']}, {data_dict['year']}"
            )
        else:
            # Handle the case where there are not enough parts in the URL
            result_list.append("None")

    return result_list


def define_legislative_network(urls):
    """
    Writes the URLs to a file.
    """

    # Initialize an empty list to store the dictionaries
    result_list = []

    # Loop through the URLs
    for url in urls:
        parts = url.split("/")  # Split the URL by "/"

        # Check if there are enough parts to create the dictionary
        if len(parts) >= 7:
            # Create an HTML anchor tag with the text and URL
            data_dict = {
                "primary_key": parts[7].replace("_smooth", "").replace(".html", ""),
                "jurisdiction": convert_jurisdiction(parts[2]),
                "url": f"https://www.canlii.org{url}",  # Construct the full URL
            }

            # Escape the text to prevent HTML injection
            escaped_text = escape(f"{data_dict['primary_key']}")

            # Create the HTML anchor tag
            anchor_tag = f'<a href="{data_dict["url"]}">{escaped_text}</a>'

            result_list.append(f"{anchor_tag}: {data_dict['jurisdiction']}")
        else:
            # Handle the case where there are not enough parts in the URL
            result_list.append("None")

    return result_list


def format_legislation_keys(legislation_key):
    """
    Formats the legislation keys for display.
    """
    # Split the string by "#" if it exists
    parts = legislation_key.split("#")

    if len(parts) == 2:
        # If there are two parts, return the first part
        legislation = parts[0]
        sections = parts[1]

        # Replace "sec" with "s "
        sections = sections.replace("sec", "s ")

        # Run a conditional if the parts[1] contains the string "subsec"
        if "subsec" in sections:
            # Split the string by "subsec"
            subsec_parts = sections.split("subsec")

            # Run a loop to add a period to the end of each element
            for i in range(len(subsec_parts)):
                subsec_parts[i] = subsec_parts[i] + "."

            # Join the elements with "subsec"
            sections = "subsec".join(subsec_parts)

    else:
        legislation = legislation_key

    legislation = legislation.replace("---", " & ")

    pass

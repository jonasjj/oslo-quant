# -*- coding: utf-8 -*-

import os
import gzip
from urllib.request import urlopen
from datetime import datetime
import progressbar
import numpy as np
import pickle

from markets._classes import Market, Ticker, Index
from markets import DATA_DIR, OSLOBORS_PICKLE_PATH

# Tickers on Oslo Børs
_market_ose = [("ASC", "ABG Sundal Collier Holding"),
               ("AFG", "AF Gruppen"),
               ("AKA", "Akastor"),
               ("AKER", "Aker"),
               ("AKERBP", "Aker BP"),
               ("AKSO", "Aker Solutions"),
               ("AKVA", "AKVA Group"),
               ("AMSC", "American Shipping Company"),
               ("APP", "Apptix"),
               ("AQUA", "Aqualis"),
               ("ARCHER", "Archer"),
               ("ARCUS", "Arcus"),
               ("AFK", "Arendals Fossekompani 2"),
               ("ASETEK", "Asetek"),
               ("ATEA", "Atea"),
               ("ATLA", "NOK Atlantic Petroleum"),
               ("AURG", "Aurskog Sparebank"),
               ("AUSS", "Austevoll Seafood"),
               ("AVANCE", "Avance Gas Holding"),
               ("AVM", "Avocet Mining"),
               ("AXA", "Axactor"),
               ("B2H", "B2Holding"),
               ("BAKKA", "Bakkafrost"),
               ("BEL", "Belships"),
               ("BERGEN", "Bergen Group"),
               ("BGBIO", "BerGenBio"),
               ("BIOTEC", "Biotec Pharmacon"),
               ("BON", "Bonheur"),
               ("BOR", "Borgestad"),
               ("BRG", "Borregaard"),
               ("BOUVET", "Bouvet"),
               ("BWLPG", "BW LPG"),
               ("BWO", "BW Offshore Limited"),
               ("BMA", "Byggma"),
               ("COV", "ContextVision"),
               ("CXENSE", "Cxense"),
               ("DAT", "Data Respons"),
               ("DESSC", "Deep Sea Supply"),
               ("DNB", "DNB"),
               ("DNO", "DNO"),
               ("DOF", "DOF"),
               ("EIOF", "Eidesvik Offshore"),
               ("EKO", "Ekornes"),
               ("EMGS", "Electromagnetic Geoservices"),
               ("EMAS", "EMAS Offshore"),
               ("ENTRA", "Entra"),
               ("EPR", "Europris"),
               ("FAR", "Farstad Shipping"),
               ("FOE", "Fred. Olsen Energy"),
               ("FRO", "Frontline"),
               ("FUNCOM", "Funcom"),
               ("GIG", "Gaming Innovation Group"),
               ("RISH", "GC Rieber Shipping"),
               ("GJF", "Gjensidige Forsikring"),
               ("GOGL", "Golden Ocean Group"),
               ("GOD", "Goodtech"),
               ("GSF", "Grieg Seafood"),
               ("GYL", "Gyldendal"),
               ("HNA", "Hafslund ser. A"),
               ("HNB", "Hafslund ser. B"),
               ("HAVI", "Havila Shipping"),
               ("HYARD", "Havyard Group"),
               ("HELG", "Helgeland Sparebank"),
               ("HEX", "Hexagon Composites"),
               ("HIDDN", "Hiddn Solutions"),
               ("HLNG", "Höegh LNG Holdings"),
               ("HSPG", "Høland og Setskog Sparebank"),
               ("IMSK", "I.M. Skaugen"),
               ("IDEX", "IDEX"),
               ("INC", "Incus Investor"),
               ("ISSG", "Indre Sogn Sparebank"),
               ("INSR", "Insr Insurance Group"),
               ("IOX", "InterOil Exploration and Production"),
               ("ITX", "Intex Resources"),
               ("ITE", "Itera"),
               ("JIN", "Jinhui Shipping and Transportation"),
               ("JAEREN", "Jæren Sparebank"),
               ("KID", "Kid"),
               ("KIT", "Kitron"),
               ("KOA", "Kongsberg Automotive"),
               ("KOG", "Kongsberg Gruppen"),
               ("KVAER", "Kværner"),
               ("LSG", "Lerøy Seafood Group"),
               ("LINK", "Link Mobility Group"),
               ("MHG", "Marine Harvest"),
               ("MEDI", "Medistim"),
               ("MELG", "Melhus Sparebank"),
               ("MULTI", "Multiconsult"),
               ("NAPA", "Napatech"),
               ("NAVA", "Navamedic"),
               ("NEL", "NEL"),
               ("NEXT", "NEXT Biometrics Group"),
               ("NGT", "NextGenTel Holding"),
               ("NANO", "Nordic Nanovector"),
               ("NOD", "Nordic Semiconductor"),
               ("NHY", "Norsk Hydro"),
               ("NSG", "Norske Skogindustrier"),
               ("NRS", "Norway Royal Salmon"),
               ("NAS", "Norwegian Air Shuttle"),
               ("NOR", "Norwegian Energy Company"),
               ("NOFI", "Norwegian Finans Holding"),
               ("NPRO", "Norwegian Property"),
               ("NRC", "NRC Group"),
               ("NTS", "NTS"),
               ("OCY", "Ocean Yield"),
               ("OTS", "Oceanteam"),
               ("ODL", "Odfjell Drilling"),
               ("ODF", "Odfjell ser. A"),
               ("ODFB", "Odfjell ser. B"),
               ("OLT", "Olav Thon Eiendomsselskap"),
               ("OPERA", "Opera Software"),
               ("ORK", "Orkla"),
               ("PEN", "Panoro Energy"),
               ("PARB", "Pareto Bank"),
               ("PGS", "Petroleum Geo-Services"),
               ("PDR", "Petrolia"),
               ("PHO", "Photocure"),
               ("PLCS", "Polarcus"),
               ("POL", "Polaris Media"),
               ("PRS", "Prosafe"),
               ("PROTCT", "Protector Forsikring"),
               ("QFR", "Q-Free"),
               ("QEC", "Questerre Energy Corporation"),
               ("RAKP", "RAK Petroleum"),
               ("REACH", "Reach Subsea"),
               ("REC", "REC Silicon"),
               ("RENO", "RenoNorden"),
               ("SALM", "SalMar"),
               ("SADG", "Sandnes Sparebank"),
               ("SAS-NOK", "NOK SAS AB"),
               ("SSO", "Scatec Solar"),
               ("SCHA", "Schibsted ser. A"),
               ("SCHB", "Schibsted ser. B"),
               ("SBX", "SeaBird Exploration"),
               ("SDRL", "Seadrill"),
               ("SBO", "Selvaag Bolig"),
               ("SEVDR", "Sevan Drilling"),
               ("SEVAN", "Sevan Marine"),
               ("SIOFF", "Siem Offshore"),
               ("SKBN", "Skandiabanken"),
               ("SKI", "Skiens Aktiemølle"),
               ("SKUE", "Skue Sparebank"),
               ("SOLON", "Solon Eiendom"),
               ("SOFF", "Solstad Offshore ser. A"),
               ("SOFFB", "Solstad Offshore ser. B"),
               ("SOLV", "Solvang"),
               ("SONG", "Songa Offshore"),
               ("SBVG", "SpareBank 1 BV"),
               ("NONG", "SpareBank 1 Nord-Norge"),
               ("RING", "SpareBank 1 Ringerike Hadeland"),
               ("MING", "SpareBank 1 SMN"),
               ("SRBANK", "SpareBank 1 SR-Bank"),
               ("SOAG", "SpareBank 1 Østfold Akershus"),
               ("MORG", "Sparebanken Møre"),
               ("SOR", "Sparebanken Sør"),
               ("SVEG", "Sparebanken Vest"),
               ("SPOG", "Sparebanken Øst"),
               ("SPU", "Spectrum"),
               ("STL", "Statoil"),
               ("SNI", "Stolt-Nielsen"),
               ("STB", "Storebrand"),
               ("STORM", "Storm Real Estate"),
               ("STRONG", "StrongPoint"),
               ("SUBC", "Subsea 7"),
               ("TIL", "Tanker Investments"),
               ("TRVX", "Targovax"),
               ("TEAM", "Team Tankers International"),
               ("TECH", "Techstep"),
               ("TEL", "Telenor"),
               ("TGS", "TGS-NOPEC Geophysical Company"),
               ("SSC", "The Scottish Salmon Company"),
               ("THIN", "Thin Film Electronics"),
               ("TOM", "Tomra Systems"),
               ("TOTG", "Totens Sparebank"),
               ("TRE", "Treasure"),
               ("TTS", "TTS Group"),
               ("VEI", "Veidekke"),
               ("VVL", "Voss Veksel- og Landmandsbank"),
               ("WWL", "Wallenius Wilhelmsen Logistics"),
               ("WEIFA", "Weifa"),
               ("WRL", "Wentworth Resources"),
               ("WWI", "Wilh. Wilhelmsen Holding ser. A"),
               ("WWIB", "Wilh. Wilhelmsen Holding ser. B"),
               ("WILS", "Wilson"),
               ("XXL", "XXL"),
               ("YAR", "Yara International"),
               ("ZAL", "Zalaris"),]

# Tickers on Oslo Axess
_market_oax = [("AEGA", "Aega"),
               ("APCL", "African Petroleum Corporation"),
               ("ABT", "Aqua Bio Technology"),
               ("AWDR", "Awilco Drilling"),
               ("ALNG", "Awilco LNG"),
               ("BXPL", "Badger Explorer"),
               ("EAM", "EAM Solar"),
               ("FLNG", "FLEX LNG"),
               ("HBC", "Hofseth BioCare"),
               ("HUGO", "Hugo Games"),
               ("MSEIS", "Magseis"),
               ("MCG", "MultiClient Geophysical"),
               ("NATTO", "NattoPharma"),
               ("NOM", "Nordic Mining"),
               ("NORTH", "North Energy"),
               ("PCIB", "PCI Biotech Holding"),
               ("PHLY", "Philly Shipyard"),
               ("PPG-PREF", "PREF Pioneer Property Group"),
               ("ROM", "RomReal"),
               ("SDSD", "S.D. Standard Drilling"),
               ("SAGA", "Saga Tankers"),
               ("SSHIP", "Scanship Holding"),
               ("UMS", "Unified Messaging Systems"),
               ("VISTIN", "Vistin Pharma"),]

# Tickers Merkur Market
_market_merk = [("AASB-ME", "Aasen Sparebank"),
                ("ATLU-ME", "Atlantic Lumpus"),
                ("BSP-ME", "Black Sea Property"),
                ("EPIC-ME", "Epic Gas"),
                ("GENT-ME", "Gentian Diagnostics"),
                ("INDUCT-ME", "Induct"),
                ("KOLKAP-ME", "Kolibri Kapital"),
                ("MONO-ME", "Monobank"),
                ("OXXY-ME", "Oxxy Group"),
                ("SIAF-ME", "Sino Agro Food"),
                ("SBULK-ME", "Songa Bulk"),
                ("WRE-ME", "WR Entertainment"),]

_sector_egenkapitalsbevis = [("AASB-ME", "Aasen Sparebank"),
                             ("AURG", "Aurskog Sparebank"),
                             ("HELG", "Helgeland Sparebank"),
                             ("HSPG", "Høland og Setskog Sparebank"),
                             ("ISSG", "Indre Sogn Sparebank"),
                             ("JAEREN", "Jæren Sparebank"),
                             ("MELG", "Melhus Sparebank"),
                             ("SADG", "Sandnes Sparebank"),
                             ("SKUE", "Skue Sparebank"),
                             ("SBVG", "SpareBank 1 BV"),
                             ("NONG", "SpareBank 1 Nord-Norge"),
                             ("RING", "SpareBank 1 Ringerike Hadeland"),
                             ("MING", "SpareBank 1 SMN"),
                             ("SOAG", "SpareBank 1 Østfold Akershus"),
                             ("MORG", "Sparebanken Møre"),
                             ("SOR", "Sparebanken Sør"),
                             ("SVEG", "Sparebanken Vest"),
                             ("SPOG", "Sparebanken Øst"),
                             ("TOTG", "Totens Sparebank"),]

_sector_energi = [("APCL", "African Petroleum Corporation"),
                  ("AKA", "Akastor"),
                  ("AKERBP", "Aker BP"),
                  ("AKSO", "Aker Solutions"),
                  ("AQUA", "Aqualis"),
                  ("ARCHER", "Archer"),
                  ("ATLA", "NOK Atlantic Petroleum"),
                  ("AVANCE", "Avance Gas Holding"),
                  ("AWDR", "Awilco Drilling"),
                  ("ALNG", "Awilco LNG"),
                  ("BXPL", "Badger Explorer"),
                  ("BERGEN", "Bergen Group"),
                  ("BON", "Bonheur"),
                  ("BWLPG", "BW LPG"),
                  ("BWO", "BW Offshore Limited"),
                  ("DESSC", "Deep Sea Supply"),
                  ("DNO", "DNO"),
                  ("DOF", "DOF"),
                  ("EIOF", "Eidesvik Offshore"),
                  ("EMGS", "Electromagnetic Geoservices"),
                  ("EMAS", "EMAS Offshore"),
                  ("EPIC-ME", "Epic Gas"),
                  ("FAR", "Farstad Shipping"),
                  ("FLNG", "FLEX LNG"),
                  ("FOE", "Fred. Olsen Energy"),
                  ("FRO", "Frontline"),
                  ("HAVI", "Havila Shipping"),
                  ("HLNG", "Höegh LNG Holdings"),
                  ("IMSK", "I.M. Skaugen"),
                  ("IOX", "InterOil Exploration and Production"),
                  ("KVAER", "Kværner"),
                  ("MSEIS", "Magseis"),
                  ("MCG", "MultiClient Geophysical"),
                  ("NORTH", "North Energy"),
                  ("NOR", "Norwegian Energy Company"),
                  ("OCY", "Ocean Yield"),
                  ("OTS", "Oceanteam"),
                  ("ODL", "Odfjell Drilling"),
                  ("PEN", "Panoro Energy"),
                  ("PGS", "Petroleum Geo-Services"),
                  ("PDR", "Petrolia"),
                  ("PLCS", "Polarcus"),
                  ("PRS", "Prosafe"),
                  ("QEC", "Questerre Energy Corporation"),
                  ("RAKP", "RAK Petroleum"),
                  ("REACH", "Reach Subsea"),
                  ("SDSD", "S.D. Standard Drilling"),
                  ("SAGA", "Saga Tankers"),
                  ("SBX", "SeaBird Exploration"),
                  ("SDRL", "Seadrill"),
                  ("SEVDR", "Sevan Drilling"),
                  ("SEVAN", "Sevan Marine"),
                  ("SIOFF", "Siem Offshore"),
                  ("SOFF", "Solstad Offshore ser. A"),
                  ("SOFFB", "Solstad Offshore ser. B"),
                  ("SONG", "Songa Offshore"),
                  ("SPU", "Spectrum"),
                  ("STL", "Statoil"),
                  ("SUBC", "Subsea 7"),
                  ("TIL", "Tanker Investments"),
                  ("TGS", "TGS-NOPEC Geophysical Company"),
                  ("WRL", "Wentworth Resources"),]

_sector_materialer = [("ABT", "Aqua Bio Technology"),
                      ("AVM", "Avocet Mining"),
                      ("BOR", "Borgestad"),
                      ("BRG", "Borregaard"),
                      ("INC", "Incus Investor"),
                      ("ITX", "Intex Resources"),
                      ("NOM", "Nordic Mining"),
                      ("NHY", "Norsk Hydro"),
                      ("NSG", "Norske Skogindustrier"),
                      ("YAR", "Yara International"),]

_sector_industri = [("AFG", "AF Gruppen"),
                    ("AKVA", "AKVA Group"),
                    ("AMSC", "American Shipping Company"),
                    ("BEL", "Belships"),
                    ("BMA", "Byggma"),
                    ("RISH", "GC Rieber Shipping"),
                    ("GOGL", "Golden Ocean Group"),
                    ("GOD", "Goodtech"),
                    ("HYARD", "Havyard Group"),
                    ("HEX", "Hexagon Composites"),
                    ("JIN", "Jinhui Shipping and Transportation"),
                    ("KOG", "Kongsberg Gruppen"),
                    ("MULTI", "Multiconsult"),
                    ("NEL", "NEL"),
                    ("NAS", "Norwegian Air Shuttle"),
                    ("NRC", "NRC Group"),
                    ("NTS", "NTS"),
                    ("ODF", "Odfjell ser. A"),
                    ("ODFB", "Odfjell ser. B"),
                    ("PHLY", "Philly Shipyard"),
                    ("RENO", "RenoNorden"),
                    ("SAS-NOK", "NOK SAS AB"),
                    ("SSHIP", "Scanship Holding"),
                    ("SOLV", "Solvang"),
                    ("SBULK-ME", "Songa Bulk"),
                    ("SNI", "Stolt-Nielsen"),
                    ("TEAM", "Team Tankers International"),
                    ("TOM", "Tomra Systems"),
                    ("TRE", "Treasure"),
                    ("TTS", "TTS Group"),
                    ("VEI", "Veidekke"),
                    ("WWL", "Wallenius Wilhelmsen Logistics"),
                    ("WWI", "Wilh. Wilhelmsen Holding ser. A"),
                    ("WWIB", "Wilh. Wilhelmsen Holding ser. B"),
                    ("WILS", "Wilson"),
                    ("ZAL", "Zalaris"),]

_sector_forbruksvarer = [("BSP-ME", "Black Sea Property"),
                         ("EKO", "Ekornes"),
                         ("EPR", "Europris"),
                         ("GYL", "Gyldendal"),
                         ("KID", "Kid"),
                         ("KOA", "Kongsberg Automotive"),
                         ("POL", "Polaris Media"),
                         ("SCHA", "Schibsted ser. A"),
                         ("SCHB", "Schibsted ser. B"),
                         ("WRE-ME", "WR Entertainment"),
                         ("XXL", "XXL"),]

_sector_konsumvarer = [("ARCUS", "Arcus"),
                       ("ATLU-ME", "Atlantic Lumpus"),
                       ("AUSS", "Austevoll Seafood"),
                       ("BAKKA", "Bakkafrost"),
                       ("GSF", "Grieg Seafood"),
                       ("LSG", "Lerøy Seafood Group"),
                       ("MHG", "Marine Harvest"),
                       ("NATTO", "NattoPharma"),
                       ("NRS", "Norway Royal Salmon"),
                       ("ORK", "Orkla"),
                       ("SALM", "SalMar"),
                       ("SIAF-ME", "Sino Agro Food"),
                       ("SSC", "The Scottish Salmon Company"),]

_sector_helsevern = [("BGBIO", "BerGenBio"),
                     ("BIOTEC", "Biotec Pharmacon"),
                     ("COV", "ContextVision"),
                     ("GENT-ME", "Gentian Diagnostics"),
                     ("HBC", "Hofseth BioCare"),
                     ("MEDI", "Medistim"),
                     ("NAVA", "Navamedic"),
                     ("NANO", "Nordic Nanovector"),
                     ("PCIB", "PCI Biotech Holding"),
                     ("PHO", "Photocure"),
                     ("TRVX", "Targovax"),
                     ("VISTIN", "Vistin Pharma"),
                     ("WEIFA", "Weifa"),]

_sector_finans = [("ASC", "ABG Sundal Collier Holding"),
                  ("AKER", "Aker"),
                  ("AXA", "Axactor"),
                  ("B2H", "B2Holding"),
                  ("DNB", "DNB"),
                  ("GJF", "Gjensidige Forsikring"),
                  ("INSR", "Insr Insurance Group"),
                  ("KOLKAP-ME", "Kolibri Kapital"),
                  ("MONO-ME", "Monobank"),
                  ("NOFI", "Norwegian Finans Holding"),
                  ("PARB", "Pareto Bank"),
                  ("PROTCT", "Protector Forsikring"),
                  ("SKBN", "Skandiabanken"),
                  ("SKI", "Skiens Aktiemølle"),
                  ("SRBANK", "SpareBank 1 SR-Bank"),
                  ("STB", "Storebrand"),
                  ("VVL", "Voss Veksel- og Landmandsbank"),]

_sector_it = [("APP", "Apptix"),
              ("ASETEK", "Asetek"),
              ("ATEA", "Atea"),
              ("BOUVET", "Bouvet"),
              ("CXENSE", "Cxense"),
              ("DAT", "Data Respons"),
              ("FUNCOM", "Funcom"),
              ("GIG", "Gaming Innovation Group"),
              ("HIDDN", "Hiddn Solutions"),
              ("HUGO", "Hugo Games"),
              ("IDEX", "IDEX"),
              ("INDUCT-ME", "Induct"),
              ("ITE", "Itera"),
              ("KIT", "Kitron"),
              ("LINK", "Link Mobility Group"),
              ("NAPA", "Napatech"),
              ("NEXT", "NEXT Biometrics Group"),
              ("NOD", "Nordic Semiconductor"),
              ("OPERA", "Opera Software"),
              ("OXXY-ME", "Oxxy Group"),
              ("QFR", "Q-Free"),
              ("REC", "REC Silicon"),
              ("STRONG", "StrongPoint"),
              ("TECH", "Techstep"),
              ("THIN", "Thin Film Electronics"),
              ("UMS", "Unified Messaging Systems"),]

_sector_telekom = [("NGT", "NextGenTel Holding"),
                   ("TEL", "Telenor"),]

_sector_forsyning = [("AEGA", "Aega"),
                     ("AFK", "Arendals Fossekompani 2"),
                     ("EAM", "EAM Solar"),
                     ("HNA", "Hafslund ser. A"),
                     ("HNB", "Hafslund ser. B"),
                     ("SSO", "Scatec Solar"),]

_sector_eiendom = [("ENTRA", "Entra"),
                   ("NPRO", "Norwegian Property"),
                   ("OLT", "Olav Thon Eiendomsselskap"),
                   ("PPG-PREF", "PREF Pioneer Property Group"),
                   ("ROM", "RomReal"),
                   ("SBO", "Selvaag Bolig"),
                   ("SOLON", "Solon Eiendom"),
                   ("STORM", "Storm Real Estate"),]

_segment_obx = [("AKERBP", "Aker BP"),
                ("AKSO", "Aker Solutions"),
                ("BAKKA", "Bakkafrost"),
                ("BWLPG", "BW LPG"),
                ("DNB", "DNB"),
                ("DNO", "DNO"),
                ("FRO", "Frontline"),
                ("GJF", "Gjensidige Forsikring"),
                ("GSF", "Grieg Seafood"),
                ("LSG", "Lerøy Seafood Group"),
                ("MHG", "Marine Harvest"),
                ("NHY", "Norsk Hydro"),
                ("NAS", "Norwegian Air Shuttle"),
                ("ORK", "Orkla"),
                ("PGS", "Petroleum Geo-Services"),
                ("REC", "REC Silicon"),
                ("SALM", "SalMar"),
                ("SCHA", "Schibsted ser. A"),
                ("SDRL", "Seadrill"),
                ("STL", "Statoil"),
                ("STB", "Storebrand"),
                ("SUBC", "Subsea 7"),
                ("TEL", "Telenor"),
                ("TGS", "TGS-NOPEC Geophysical Company"),
                ("YAR", "Yara International"),]

_segment_match = [("ASC", "ABG Sundal Collier Holding"),
                  ("AFG", "AF Gruppen"),
                  ("AKA", "Akastor"),
                  ("AKER", "Aker"),
                  ("AKVA", "AKVA Group"),
                  ("AMSC", "American Shipping Company"),
                  ("AQUA", "Aqualis"),
                  ("ARCHER", "Archer"),
                  ("ARCUS", "Arcus"),
                  ("ASETEK", "Asetek"),
                  ("ATEA", "Atea"),
                  ("ATLA", "NOK Atlantic Petroleum"),
                  ("AUSS", "Austevoll Seafood"),
                  ("AVANCE", "Avance Gas Holding"),
                  ("AVM", "Avocet Mining"),
                  ("AXA", "Axactor"),
                  ("B2H", "B2Holding"),
                  ("BEL", "Belships"),
                  ("BERGEN", "Bergen Group"),
                  ("BIOTEC", "Biotec Pharmacon"),
                  ("BON", "Bonheur"),
                  ("BOR", "Borgestad"),
                  ("BRG", "Borregaard"),
                  ("BWO", "BW Offshore Limited"),
                  ("COV", "ContextVision"),
                  ("DAT", "Data Respons"),
                  ("DESSC", "Deep Sea Supply"),
                  ("DOF", "DOF"),
                  ("EIOF", "Eidesvik Offshore"),
                  ("EKO", "Ekornes"),
                  ("EMGS", "Electromagnetic Geoservices"),
                  ("ENTRA", "Entra"),
                  ("EPR", "Europris"),
                  ("FAR", "Farstad Shipping"),
                  ("FOE", "Fred. Olsen Energy"),
                  ("FUNCOM", "Funcom"),
                  ("GIG", "Gaming Innovation Group"),
                  ("GOGL", "Golden Ocean Group"),
                  ("GOD", "Goodtech"),
                  ("HNA", "Hafslund ser. A"),
                  ("HNB", "Hafslund ser. B"),
                  ("HAVI", "Havila Shipping"),
                  ("HYARD", "Havyard Group"),
                  ("HEX", "Hexagon Composites"),
                  ("HIDDN", "Hiddn Solutions"),
                  ("HLNG", "Höegh LNG Holdings"),
                  ("IDEX", "IDEX"),
                  ("INC", "Incus Investor"),
                  ("INSR", "Insr Insurance Group"),
                  ("IOX", "InterOil Exploration and Production"),
                  ("ITX", "Intex Resources"),
                  ("JIN", "Jinhui Shipping and Transportation"),
                  ("KID", "Kid"),
                  ("KIT", "Kitron"),
                  ("KOA", "Kongsberg Automotive"),
                  ("KOG", "Kongsberg Gruppen"),
                  ("KVAER", "Kværner"),
                  ("LINK", "Link Mobility Group"),
                  ("MEDI", "Medistim"),
                  ("MULTI", "Multiconsult"),
                  ("NAPA", "Napatech"),
                  ("NAVA", "Navamedic"),
                  ("NEL", "NEL"),
                  ("NEXT", "NEXT Biometrics Group"),
                  ("NGT", "NextGenTel Holding"),
                  ("NANO", "Nordic Nanovector"),
                  ("NOD", "Nordic Semiconductor"),
                  ("NSG", "Norske Skogindustrier"),
                  ("NRS", "Norway Royal Salmon"),
                  ("NOR", "Norwegian Energy Company"),
                  ("NOFI", "Norwegian Finans Holding"),
                  ("NPRO", "Norwegian Property"),
                  ("NRC", "NRC Group"),
                  ("OCY", "Ocean Yield"),
                  ("OTS", "Oceanteam"),
                  ("ODL", "Odfjell Drilling"),
                  ("ODF", "Odfjell ser. A"),
                  ("ODFB", "Odfjell ser. B"),
                  ("OLT", "Olav Thon Eiendomsselskap"),
                  ("OPERA", "Opera Software"),
                  ("PEN", "Panoro Energy"),
                  ("PARB", "Pareto Bank"),
                  ("PHO", "Photocure"),
                  ("PLCS", "Polarcus"),
                  ("PRS", "Prosafe"),
                  ("PROTCT", "Protector Forsikring"),
                  ("QFR", "Q-Free"),
                  ("QEC", "Questerre Energy Corporation"),
                  ("RENO", "RenoNorden"),
                  ("SAS-NOK", "NOK SAS AB"),
                  ("SSO", "Scatec Solar"),
                  ("SCHB", "Schibsted ser. B"),
                  ("SBX", "SeaBird Exploration"),
                  ("SBO", "Selvaag Bolig"),
                  ("SEVDR", "Sevan Drilling"),
                  ("SKBN", "Skandiabanken"),
                  ("SOLON", "Solon Eiendom"),
                  ("SOFF", "Solstad Offshore ser. A"),
                  ("SONG", "Songa Offshore"),
                  ("SRBANK", "SpareBank 1 SR-Bank"),
                  ("SPU", "Spectrum"),
                  ("SNI", "Stolt-Nielsen"),
                  ("STRONG", "StrongPoint"),
                  ("TIL", "Tanker Investments"),
                  ("TRVX", "Targovax"),
                  ("TECH", "Techstep"),
                  ("SSC", "The Scottish Salmon Company"),
                  ("THIN", "Thin Film Electronics"),
                  ("TOM", "Tomra Systems"),
                  ("TRE", "Treasure"),
                  ("TTS", "TTS Group"),
                  ("VEI", "Veidekke"),
                  ("VVL", "Voss Veksel- og Landmandsbank"),
                  ("WWL", "Wallenius Wilhelmsen Logistics"),
                  ("WEIFA", "Weifa"),
                  ("WRL", "Wentworth Resources"),
                  ("WWI", "Wilh. Wilhelmsen Holding ser. A"),
                  ("WWIB", "Wilh. Wilhelmsen Holding ser. B"),
                  ("XXL", "XXL"),
                  ("ZAL", "Zalaris"),]

_segment_standard = [("APP", "Apptix"),
                     ("AFK", "Arendals Fossekompani 2"),
                     ("BGBIO", "BerGenBio"),
                     ("BOUVET", "Bouvet"),
                     ("BMA", "Byggma"),
                     ("CXENSE", "Cxense"),
                     ("EMAS", "EMAS Offshore"),
                     ("RISH", "GC Rieber Shipping"),
                     ("GYL", "Gyldendal"),
                     ("IMSK", "I.M. Skaugen"),
                     ("ITE", "Itera"),
                     ("NTS", "NTS"),
                     ("PDR", "Petrolia"),
                     ("POL", "Polaris Media"),
                     ("RAKP", "RAK Petroleum"),
                     ("REACH", "Reach Subsea"),
                     ("SEVAN", "Sevan Marine"),
                     ("SIOFF", "Siem Offshore"),
                     ("SKI", "Skiens Aktiemølle"),
                     ("SOFFB", "Solstad Offshore ser. B"),
                     ("SOLV", "Solvang"),
                     ("STORM", "Storm Real Estate"),
                     ("TEAM", "Team Tankers International"),
                     ("WILS", "Wilson"),]

_index_osebx = [("AFG", "AF Gruppen"),
                ("AKER", "Aker"),
                ("AKERBP", "Aker BP"),
                ("AKSO", "Aker Solutions"),
                ("AMSC", "American Shipping Company"),
                ("ASETEK", "Asetek"),
                ("ATEA", "Atea"),
                ("AXA", "Axactor"),
                ("B2H", "B2Holding"),
                ("BAKKA", "Bakkafrost"),
                ("BIOTEC", "Biotec Pharmacon"),
                ("DNB", "DNB"),
                ("DNO", "DNO"),
                ("EKO", "Ekornes"),
                ("ENTRA", "Entra"),
                ("EPR", "Europris"),
                ("FRO", "Frontline"),
                ("GJF", "Gjensidige Forsikring"),
                ("GOGL", "Golden Ocean Group"),
                ("HNB", "Hafslund ser. B"),
                ("HEX", "Hexagon Composites"),
                ("IDEX", "IDEX"),
                ("KIT", "Kitron"),
                ("KOA", "Kongsberg Automotive"),
                ("KOG", "Kongsberg Gruppen"),
                ("LSG", "Lerøy Seafood Group"),
                ("MHG", "Marine Harvest"),
                ("MULTI", "Multiconsult"),
                ("NEXT", "NEXT Biometrics Group"),
                ("NANO", "Nordic Nanovector"),
                ("NOD", "Nordic Semiconductor"),
                ("NHY", "Norsk Hydro"),
                ("NAS", "Norwegian Air Shuttle"),
                ("NOFI", "Norwegian Finans Holding"),
                ("NPRO", "Norwegian Property"),
                ("OLT", "Olav Thon Eiendomsselskap"),
                ("OPERA", "Opera Software"),
                ("ORK", "Orkla"),
                ("PGS", "Petroleum Geo-Services"),
                ("PHO", "Photocure"),
                ("REC", "REC Silicon"),
                ("SALM", "SalMar"),
                ("SSO", "Scatec Solar"),
                ("SCHA", "Schibsted ser. A"),
                ("SCHB", "Schibsted ser. B"),
                ("SDRL", "Seadrill"),
                ("STL", "Statoil"),
                ("SNI", "Stolt-Nielsen"),
                ("STB", "Storebrand"),
                ("SUBC", "Subsea 7"),
                ("TEL", "Telenor"),
                ("TGS", "TGS-NOPEC Geophysical Company"),
                ("THIN", "Thin Film Electronics"),
                ("TOM", "Tomra Systems"),
                ("TRE", "Treasure"),
                ("VEI", "Veidekke"),
                ("WWL", "Wallenius Wilhelmsen Logistics"),
                ("WEIFA", "Weifa"),
                ("WWI", "Wilh. Wilhelmsen Holding ser. A"),
                ("WWIB", "Wilh. Wilhelmsen Holding ser. B"),
                ("XXL", "XXL"),
                ("YAR", "Yara International"),]

_index_obx = [("AKERBP", "Aker BP"),
              ("AKSO", "Aker Solutions"),
              ("BAKKA", "Bakkafrost"),
              ("BWLPG", "BW LPG"),
              ("DNB", "DNB"),
              ("DNO", "DNO"),
              ("FRO", "Frontline"),
              ("GJF", "Gjensidige Forsikring"),
              ("GSF", "Grieg Seafood"),
              ("LSG", "Lerøy Seafood Group"),
              ("MHG", "Marine Harvest"),
              ("NHY", "Norsk Hydro"),
              ("NAS", "Norwegian Air Shuttle"),
              ("ORK", "Orkla"),
              ("PGS", "Petroleum Geo-Services"),
              ("REC", "REC Silicon"),
              ("SALM", "SalMar"),
              ("SCHA", "Schibsted ser. A"),
              ("SDRL", "Seadrill"),
              ("STL", "Statoil"),
              ("STB", "Storebrand"),
              ("SUBC", "Subsea 7"),
              ("TEL", "Telenor"),
              ("TGS", "TGS-NOPEC Geophysical Company"),
              ("YAR", "Yara International"),]

_segment_nye = [("BGBIO", "BerGenBio"),
                ("SOFFB", "Solstad Offshore ser. B"),]



_markets = [('OSE', 'Oslo Børs all'),
            ('OAX', 'Oslo Axess'),
            ('MERK', 'Merkur Market')]

_sectors = ['egenkapitalsbevis',
            'energi',
            'materialer',
            'industri',
            'forbruksvarer',
            'konsumvarer',
            'helsevern',
            'finans',
            'it',
            'telekom',
            'forsyning',
            'eiendom',]


_segments = [('OBX', 'OBX'),
             ('Match', 'OB Match'),
             ('Standard', 'OB Standard'),
             ('Nye', 'OB Nye')]

_indexes = [("OSEBX", "Hovedindeksen"),
            ("OBX", "OBX Total Return Index"),]
#            ("OSEAX", "Oslo Børs All-share Index"),
#            ("OSEFX", "Oslo Børs Mutual Fund Index"),
#            ("OSEMX", "Oslo Børs Mid Cap Index"),
#            ("OSESX", "Oslo Børs Small Cap Index"),
#            ("OBOSX", "Oslo Børs OBX Oil Service Index"),
#            ("OBSFX", "Oslo Børs Seafood Index"),
#            ("OBSHX", "Oslo Børs Shipping Index"),
#            ("OSEEX", "Egenkapitalbevis indeks 1"),
#            ("OSLENX", "OSLO Energy Index"),
#            ("OSLSFX", "OSLO Seafood Index"),
#            ("OSLSHX", "OSLO Shipping Index"),
#            ("OSE10GI", "Energi"),
#            ("OSE15GI", "Materialer"),
#            ("OSE20GI", "Industri"),
#            ("OSE25GI", "Forbruksvarer"),
#            ("OSE30GI", "Konsumvarer 1"),
#            ("OSE35GI", "Helsevern"),
#            ("OSE40GI", "Finans 1"),
#            ("OSE45GI", "IT"),
#            ("OSE50GI", "Telekom 1"),
#            ("OSE55GI", "Forsyning"),
#            ("OSE60GI", "Eiendom"),
#            ("OAAX", "Oslo Axess All-share index"),
#            ("OAX10GI", "OAX10 Energy"),
#            ("OAX15GI", "OAX15 Materials"),
#            ("OAX20GI", "OAX20 Industrials"),
#            ("OAX30GI", "OAX30 Consumer Staples"),
#            ("OAX35GI", "OAX35 Health Care"),
#            ("OAX45GI", "OAX45 Information Technology"),
#            ("OAX55GI", "OAX55 Utilities"),
#            ("OAX60GI", "OAX60 Real Estate"),
#            ("OBXASK", "OBX ASK Index"),
#            ("OBXBID", "OBX BID Index"),
#            ("OBXI", "OBX International Index"),
#            ("OBXP", "OBX Price Index"),
#            ("OBXW", "OBX Volume-weigthed Index"),
#            ("OSLDRX", "OSLO Energy Drilling Index"),
#            ("OSLESX", "OSLO Energy Equipment & Services Index"),
#            ("OSLEPX", "OSLO Energy Exploration & Production I."),
#            ("OSLIOGX", "OSLO Energy Integrated Oil & Gas Index"),
#            ("OSLREX", "OSLO Energy Renewable Index"),]



class OsloBors(object):
    def __init__(self):
        
        # construct paths for markets and indexes
        self._markets_dir = os.path.join(DATA_DIR, "markets")
        self._indexes_dir = os.path.join(DATA_DIR, "indexes")
        
        # dict containing all tickers indexed by MARKET_NAME.TICKER_NAME
        self.tickers = {}

        # create public markets dict indexed by market name
        self.markets = {}
        for market_name, market_long_name in _markets:

            # look for a local variable matching the market name
            market_list_name = "_market_" + market_name.lower()
            market_list = globals()[market_list_name]

            # create market instance
            market = Market(market_name, market_long_name)
            self.markets[market_name] = market

            # parse tickers in this market list
            for ticker_name, ticker_long_name in market_list:

                # Create ticker object
                url = "http://hopey.netfonds.no/paperhistory.php?paper=" + \
                      ticker_name + "." + market.name + "&csv_format=sdv"
                ticker = Ticker(ticker_name, ticker_long_name, market, url)

                # add ticker to market instance
                market.tickers.append(ticker)

                # check that no ticker with this name exists
                if ticker_name in self.tickers:
                    raise Exception("Ticker " + ticker_name + " already exists")

                # add ticker to dict of all tickers
                self.tickers[ticker_name] = ticker

        # dict of dicts where {'SECTOR_NAME': {'TICKER_NAME': TICKER}}        
        self.sectors = {}
        for sector_name in _sectors:

            # look for a local variable matching the market name
            sector_list_name = "_sector_" + sector_name.lower()
            sector_list = globals()[sector_list_name]

            # create sector object
            self.sectors[sector_name] = {}

            # parse ticker names from the sector list
            for ticker_name, ticker_long_name in sector_list:
                ticker = self.tickers[ticker_name]
                self.sectors[sector_name][ticker_name] = ticker

                # assign sector name
                if ticker.sector_name is not None:
                    raise Exception("Ticker " + str(ticker) + " already has sector")
                ticker.sector_name = sector_name

        # dict of dicts where {'SEGMENT_NAME': {'TICKER_NAME': TICKER}}
        self.segments = {}
        for segment_name, segment_long_name in _segments:

            # look for a local variable matching the market name
            segment_list_name = "_segment_" + segment_name.lower()
            segment_list = globals()[segment_list_name]

            # create segment dict
            self.segments[segment_name] = {}

            # parse ticker names from the segment list
            for ticker_name, ticker_long_name in segment_list:
                ticker = self.tickers[ticker_name]
                self.segments[segment_name][ticker_name] = ticker

                # assign segment name
                ticker.segments.append(segment_name)

        # dict for storing indexes
        self.indexes = {}
        for index_name, index_long_name in _indexes:

            # look for a local variable matching the market name
            index_list_name = "_index_" + index_name.lower()
            index_list = globals()[index_list_name]

            # Create index instance
            url = "http://hopey.netfonds.no/paperhistory.php?paper=" + \
                  index_name + ".OSE&csv_format=sdv"
            index = Index(index_name, index_long_name, url)
            self.indexes[index_name] = index

            # parse ticker names from index list
            for ticker_name, ticker_long_name in index_list:
                ticker = self.tickers[ticker_name]
                index.tickers.append(ticker)

        # dict containing all instruments indexed by name
        self.instruments = {}
    
        # merge all instruments
        for k,v in list(self.tickers.items()) + list(self.indexes.items()):
            if k in self.instruments:
                raise Exception(k + " is already in self.instruments")
            self.instruments[k] = v

    def __str__(self):
        return "Oslo Børs"

    def _download_gz(self, url, dest_file):
        """
        Download file from url to path dest_file.
        The file will be in gzip format
        """
        data = urlopen(url).read()
        
        with gzip.GzipFile(dest_file, "wb") as f:
            f.write(data)

    def download(self):
        """
        Download the daily history for all tickers and indexes from netfonds.no
        DATA_DIR is used for target dir.
        Overwrites existing files.
        """

        # create dirs
        if not os.path.isdir(self._markets_dir):
            os.makedirs(self._markets_dir)
            
        if not os.path.isdir(self._indexes_dir):
            os.makedirs(self._indexes_dir)

        # list of tuples with (url, dest_file) to download
        download_list = []
        
        # add tickers to download list
        for market in self.markets.values():
            market_dir = os.path.join(self._markets_dir, market.name)

            # create market dir
            if not os.path.isdir(market_dir):
                os.makedirs(market_dir)

            for ticker in market.tickers:
                ticker_file = os.path.join(market_dir, ticker.name)
                download_list.append((ticker.url, ticker_file))
            
        # add indexes to download list
        for index in self.indexes.values():
            index_file = os.path.join(self._indexes_dir, index.name)
            
            download_list.append((index.url, index_file))

        # create progressbar
        bar = progressbar.ProgressBar(maxval=len(download_list))
        bar.start()

        # download all files in the list
        for i, (url, dest_file) in enumerate(download_list):
            self._download_gz(url, dest_file + ".sdv.gz")
            bar.update(i)

        bar.finish()
        print("Downloaded " + str(i) + " files to " + DATA_DIR)

    def _load_file(self, file_path):
        """
        Load the file.
        
        Return:
           A numpy named array
        """

        # read the gzip file
        with gzip.GzipFile(file_path, 'rb') as f:
            file_data = f.read().decode('latin-1')

        # split the file into lines
        lines = file_data.strip().split("\n")

        # remove the first item, which is the column headers
        lines.pop(0)        

        # create an empty return matrix
        matrix = np.zeros(shape=len(lines),
                          dtype=[('date', 'f8'),
                                 ('open', 'f8'),
                                 ('high', 'f8'),
                                 ('low', 'f8'),
                                 ('close', 'f8'),
                                 ('volume', 'i8'),
                                 ('value', 'i8')])

        # fill in the return matrix
        for line_num, line in enumerate(lines):

            try:
                # unpack row items)
                (date, paper, exchange, open_price, high_price,
                 low_price, close_price, volume, value) = line.split(";")
                
                # parse row items
                date = datetime.strptime(date, '%Y%m%d').timestamp()
                open_price = float(open_price)
                high_price = float(high_price)          
                low_price = float(low_price)
                close_price = float(close_price)
                volume = float(volume)
                value = float(value)
                
                matrix[line_num] = date, open_price, high_price, low_price, \
                                   close_price, volume, value
            except:
                print("Failed to load file " + str(file_path) + " line " + \
                      str(line_num) + "Line: \"" + str(line) + "\"")
                return None

        # sort rows on time column, there has been some swapped samples detected in the source
        matrix = np.sort(matrix, order='date')

        return matrix
        
    def load(self):
        """
        Load files from DATA_DIR
        """
        
        # load tickers
        for market in self.markets.values():
            market_dir = os.path.join(self._markets_dir, market.name)
            
            for ticker in market.tickers:
                ticker_file = os.path.join(market_dir, ticker.name) + ".sdv.gz"
                ticker.data = self._load_file(ticker_file)
                
        # load indexes
        for index in self.indexes.values():
            index_file = os.path.join(self._indexes_dir, index.name) + ".sdv.gz"
            index.data = self._load_file(index_file)
        
    def pickle(self):
        """
        Pickle this object to OSLOBORS_PICKLE_PATH
        """
        with open(OSLOBORS_PICKLE_PATH, "wb" ) as f:
            pickle.dump(self,  f)

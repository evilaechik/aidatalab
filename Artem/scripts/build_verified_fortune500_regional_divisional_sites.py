#!/usr/bin/env python3
"""Create a source-verified seed list of Fortune 500 regional/divisional sites.

Every row is supported by a company-owned source, except clearly labelled
public-government records that document a specific parent-business HQ or
correct a locality. Site classes stay separate:
confirmed HQs/divisional bases can inform a future regional-HQ outcome, while
Kroger's verified division offices are retained as a lower-weight operating
footprint and are not silently promoted to regional HQs.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd

from assign_data_axle_locations_to_msas import (
    build_assignments,
    load_target_cbsa_polygons,
    read_gazetteer,
)


ARTEM = Path(__file__).resolve().parents[1]
FORTUNE = ARTEM / "data" / "big_business_presence" / "fortune_500_universe_2025.csv"
ROSTER = ARTEM / "data" / "big_business_presence" / "msa_roster.csv"
OUTPUT = ARTEM / "data" / "big_business_presence"
KROGER_SOURCE = "https://www.thekrogerco.com/contact-us/our-divisions"


SEEDS = [
    {
        "company_name": "Amazon", "site_name": "HQ2", "site_class": "confirmed_additional_corporate_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Arlington", "state": "VA", "street_address": "",
        "function_evidence_url": "https://www.aboutamazon.com/news/amazon-offices/amazon-opens-offices-at-hq2-in-arlington-va",
        "geography_evidence_url": "", "source_note": "Amazon identifies its second headquarters in Arlington, Virginia.",
    },
    {
        "company_name": "Amazon", "site_name": "Whole Foods Market World Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Austin", "state": "TX", "street_address": "550 Bowie Street",
        "function_evidence_url": "https://www.wholefoodsmarket.com/company-info/national-regional-offices",
        "geography_evidence_url": "", "source_note": "Amazon acquired Whole Foods Market in 2017; Whole Foods' current company office directory identifies its world headquarters in Austin.",
    },
    {
        "company_name": "Walmart", "site_name": "VIZIO Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Irvine", "state": "CA", "street_address": "39 Tesla",
        "function_evidence_url": "https://corporate.walmart.com/news/2024/12/03/walmart-completes-acquisition-of-vizio",
        "geography_evidence_url": "https://careers.walmart.com/us/es/home/vizio",
        "source_note": "Walmart completed the VIZIO acquisition in 2024, making VIZIO a wholly owned Walmart subsidiary; Walmart's current VIZIO careers page identifies its Irvine headquarters.",
    },
    {
        "company_name": "Target", "site_name": "Shipt Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Birmingham", "state": "AL", "street_address": "",
        "function_evidence_url": "https://corporate.shipt.com/news/deepening-our-hometown-roots-in-birmingham",
        "geography_evidence_url": "", "source_note": "Shipt's current company announcement identifies Birmingham as its headquarters and identifies Shipt as an independently operated Target subsidiary.",
    },
    {
        "company_name": "Walt Disney", "site_name": "ESPN Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Bristol", "state": "CT", "street_address": "",
        "function_evidence_url": "https://thewaltdisneycompany.com/app/uploads/2025/01/2024-Annual-Report.pdf?form=MG0AV3",
        "geography_evidence_url": "https://thewaltdisneycompany.com/news/espn-exclusive-experiences-ballparks-tour-labor-day-weekend/",
        "source_note": "Disney's 2024 Annual Report identifies ESPN as generally 80% owned by Disney; Disney's 2024 company announcement identifies ESPN Headquarters in Bristol, Connecticut.",
    },
    {
        "company_name": "Walt Disney", "site_name": "Lucasfilm Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "San Francisco", "state": "CA", "street_address": "1 Letterman Drive",
        "function_evidence_url": "https://sites.disney.com/waltdisneyimagineering/our-story/",
        "geography_evidence_url": "https://www.starwars.com/news/andor-tony-gilroy-alan-tudyk-visit-lucasfilm",
        "source_note": "Disney's current Imagineering history identifies Lucasfilm as part of The Walt Disney Company; Lucasfilm's 2025 StarWars.com story identifies the company's San Francisco headquarters.",
    },
    {
        "company_name": "American Express", "site_name": "American Express National Bank Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Sandy", "state": "UT", "street_address": "",
        "function_evidence_url": "https://www.americanexpress.com/en-us/careers/locations/salt-lake-city/index.html/",
        "geography_evidence_url": "", "source_note": "American Express's current Salt Lake City location page identifies its Sandy facility as the headquarters of American Express National Bank, with finance, risk, technology, and servicing functions.",
    },
    {
        "company_name": "Archer Daniels Midland", "site_name": "North American Headquarters", "site_class": "confirmed_regional_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Decatur", "state": "IL", "street_address": "4666 Faries Parkway",
        "function_evidence_url": "https://www.adm.com/en-us/about-adm/locations/north-america/",
        "geography_evidence_url": "", "source_note": "ADM's current North America location page labels 4666 Faries Parkway in Decatur as its North American Headquarters. This location may fall outside the project’s current 200-MSA roster, but is retained as a documented site.",
    },
    {
        "company_name": "PNC Financial Services Group", "site_name": "Midland Loan Services Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Overland Park", "state": "KS", "street_address": "10851 Mastin Street",
        "function_evidence_url": "https://www.pnc.com/content/dam/pnc-com/pdf/corporateandinstitutional/Real-Estate/Midland/s-p-servicer-report-2023.pdf",
        "geography_evidence_url": "", "source_note": "A current PNC-hosted 2023 servicer evaluation identifies Midland as a division of PNC Bank and as headquartered in Overland Park, Kansas. The underlying evaluation is third-party, but PNC publishes it in its own commercial-real-estate materials; complete a direct PNC currentness review before final scoring.",
    },
    {
        "company_name": "Pfizer", "site_name": "Seagen Global Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Bothell", "state": "WA", "street_address": "21717 30th Drive Southeast",
        "function_evidence_url": "https://webfiles.pfizer.com/Seagen%20Corporate%20Responsibility%20Report.pdf",
        "geography_evidence_url": "https://cdn.pfizer.com/pfizercom/2025_CDP_Response_Pfizer_Inc.pdf",
        "source_note": "Seagen's corporate-responsibility report identifies its global headquarters in Bothell, Washington. Pfizer's 2025 corporate disclosure confirms it completed the Seagen acquisition in December 2023 and incorporates Seagen operations in Pfizer's footprint. Reconfirm the current formal headquarters label before final scoring because the direct headquarters statement predates Pfizer ownership.",
    },
    {
        "company_name": "Paccar", "site_name": "Peterbilt Motors Company Division Headquarters", "site_class": "confirmed_divisional_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Denton", "state": "TX", "street_address": "1700 Woodbrook Street",
        "function_evidence_url": "https://www.paccar.com/media/1aml4ipx/2024-annual-report.pdf",
        "geography_evidence_url": "", "source_note": "PACCAR's 2024 annual report identifies Peterbilt Motors Company as a Truck division and lists its Division Headquarters in Denton, Texas.",
    },
    {
        "company_name": "Textron", "site_name": "Bell Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Fort Worth", "state": "TX", "street_address": "3255 Bell Flight Boulevard",
        "function_evidence_url": "https://www.textron.com/About/Our-Businesses/Bell",
        "geography_evidence_url": "", "source_note": "Textron's current Bell business page identifies Bell as a wholly owned Textron subsidiary headquartered in Fort Worth, Texas.",
    },
    {
        "company_name": "Textron", "site_name": "Textron Aviation Defense Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Wichita", "state": "KS", "street_address": "One Cessna Boulevard",
        "function_evidence_url": "https://investor.textron.com/news-releases/news-details/2025/Beechcraft-M-346N-Unveiled-as-Ready-Now-Solution-for-U-S--Navy-Undergraduate-Jet-Training-System/default.aspx",
        "geography_evidence_url": "", "source_note": "Textron's 2025 investor-relations release identifies Textron Aviation Defense, a Textron company, as headquartered in Wichita, Kansas.",
    },
    {
        "company_name": "General Motors", "site_name": "GM Financial Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Fort Worth", "state": "TX", "street_address": "801 Cherry Street",
        "function_evidence_url": "https://www.gmfinancial.com/en-us/about.html",
        "geography_evidence_url": "", "source_note": "GM Financial's current company page identifies it as General Motors' wholly owned captive-finance subsidiary and as headquartered in Fort Worth, Texas.",
    },
    {
        "company_name": "CarMax", "site_name": "CarMax Auto Finance Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Kennesaw", "state": "GA", "street_address": "225 Chastain Meadows Court NW",
        "function_evidence_url": "https://investors.carmax.com/news-and-events/news/news-details/2019/CarMax-to-Create-More-Than-300-Jobs-in-Gwinnett-County/default.aspx",
        "geography_evidence_url": "https://investors.carmax.com/news-and-events/news/news-details/2026/CarMax-Outlines-Strategy-to-Strengthen-Core-Operations-and-Deliver-Robust-Growth/default.aspx",
        "source_note": "CarMax's 2019 investor-relations announcement identifies CarMax Auto Finance headquarters in Kennesaw; CarMax's 2026 strategy release confirms CAF remains a named captive-finance business led by an executive vice president. Recheck the precise site label before final scoring because the direct headquarters statement is older.",
    },
    {
        "company_name": "Emerson Electric", "site_name": "AspenTech Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Bedford", "state": "MA", "street_address": "20 Crosby Drive",
        "msa_cbsa_override": "14460",
        "function_evidence_url": "https://ir.emerson.com/sec-filings/all-sec-filings/content/0001140361-25-003633/0001140361-25-003633.pdf",
        "geography_evidence_url": "https://www.emerson.com/en/corporate/news/2025/emerson-completes-acquisition-of-remaining-outstanding-shares-of-aspentech",
        "source_note": "Emerson's 2025 transaction filing identifies AspenTech's corporate headquarters at 20 Crosby Drive in Bedford, Massachusetts. Emerson's March 2025 company release confirms AspenTech became a wholly owned Emerson subsidiary and continues as an independent business unit. Bedford is a Census-designated place that is absent from the place-gazetteer lookup, so the Boston-Cambridge-Newton MSA assignment is documented as an override.",
    },
    {
        "company_name": "Emerson Electric", "site_name": "National Instruments Corporate Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Austin", "state": "TX", "street_address": "11500 North Mopac Expressway",
        "function_evidence_url": "https://www.ni.com/docs/en-US/bundle/ni-system-configuration-function-reference-for-labwindows-cvi/page/topics/ni-services.html",
        "geography_evidence_url": "https://ir.emerson.com/sec-filings/all-sec-filings/content/0000032604-25-000087/exhibit21fy25.htm",
        "source_note": "NI's current technical documentation identifies National Instruments' corporate headquarters at 11500 North Mopac Expressway in Austin. Emerson's 2025 Exhibit 21 identifies National Instruments entities as Emerson subsidiaries; an NI 2024 brochure carries Emerson copyright and describes the same U.S. corporate headquarters.",
    },
    {
        "company_name": "Parker-Hannifin", "site_name": "LORD Corporation Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Cary", "state": "NC", "street_address": "111 Lord Drive",
        "function_evidence_url": "https://www.parker.com/content/dam/parker/emg/lord-division/resources/LAE-QM-Lord%20APS%20EPM%20Quality%20Manual%20%281%29.pdf",
        "geography_evidence_url": "https://investors.parker.com/sec-filings/all-sec-filings/content/0000950157-19-001228/0000950157-19-001228.pdf",
        "source_note": "A Parker-hosted LORD quality manual identifies LORD Corporation's corporate headquarters at 111 Lord Drive in Cary. Parker's investor-relations filing confirms its acquisition of LORD; retain for a final currentness check because the headquarters manual predates the acquisition integration.",
    },
    {
        "company_name": "Danaher", "site_name": "Beckman Coulter Life Sciences Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Indianapolis", "state": "IN", "street_address": "5350 Lakeview Parkway South Drive",
        "function_evidence_url": "https://lifesciences.danaher.com/us/en/news/assay-for-rapid-antibody-aggregation-detection.html",
        "geography_evidence_url": "", "source_note": "Danaher's 2024 Life Sciences announcement identifies Beckman Coulter Life Sciences as a Danaher operating company headquartered in Indianapolis, Indiana, with 11 operational hubs worldwide.",
    },
    {
        "company_name": "Danaher", "site_name": "Cepheid Corporate Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Sunnyvale", "state": "CA", "street_address": "904 Caribbean Drive",
        "function_evidence_url": "https://www.danaher.com/our-businesses/diagnostics/cepheid",
        "geography_evidence_url": "https://apply.cepheid.com/Package%20Insert%20Files/Xpert%20BCR-ABL%20Ultra/Xpert%20BCR-ABL%20Ultra%20ENGLISH%20IFU%20303-0946%20Rev%20B.pdf",
        "source_note": "Danaher's current Cepheid business page lists Cepheid at 904 Caribbean Drive in Sunnyvale. Cepheid's 2024 company product instructions label that address its Corporate Headquarters; Danaher's current business directory confirms Cepheid remains an operating company in the Danaher portfolio.",
    },
    {
        "company_name": "Danaher", "site_name": "Aldevron Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Fargo", "state": "ND", "street_address": "4055 41st Avenue South",
        "function_evidence_url": "https://jobsblog.danaher.com/blog/a-front-row-seat-for-the-mrna-explosion-aldevrons-nate-russart-shares/",
        "geography_evidence_url": "https://investors.danaher.com/2021-06-17-Danaher-To-Acquire-Aldevron",
        "source_note": "Danaher's 2025 careers article identifies Aldevron as a Danaher business headquartered in Fargo, North Dakota. Danaher's investor-relations announcement says Aldevron operates as a standalone operating company in its Life Sciences segment.",
    },
    {
        "company_name": "Danaher", "site_name": "Mammotome Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Cincinnati", "state": "OH", "street_address": "300 East Business Way",
        "function_evidence_url": "https://jobs.danaher.com/global/en/mammotome",
        "geography_evidence_url": "", "source_note": "Danaher's current Mammotome careers page identifies Mammotome as headquartered in Cincinnati and describes it as a business unit of Leica Biosystems, a Danaher business.",
    },
    {
        "company_name": "Booking Holdings", "site_name": "OpenTable Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "San Francisco", "state": "CA", "street_address": "1 Montgomery Street",
        "function_evidence_url": "https://www.bookingholdings.com/wp-content/uploads/2024/06/Booking-Holdings-2024-Modern-Slavery-Statement.pdf",
        "geography_evidence_url": "", "source_note": "Booking Holdings' 2024 company statement identifies OpenTable as a Booking Holdings brand headquartered in San Francisco, California.",
    },
    {
        "company_name": "Home Depot", "site_name": "The Home Depot Pro Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Jacksonville", "state": "FL", "street_address": "701 San Marco Boulevard",
        "function_evidence_url": "https://jaxusa.org/wp-content/uploads/2025/05/Headquarters78.pdf",
        "geography_evidence_url": "https://ir.homedepot.com/news-releases/2026/07-30-2026-210819756",
        "source_note": "The Jacksonville regional economic-development partnership's 2025 headquarters inventory classifies The Home Depot Pro as a corporate headquarters in Jacksonville. The Home Depot's 2026 company release identifies Home Depot Pro among its enterprise businesses. This government-record exception needs a final company-source confirmation before final scoring.",
    },
    {
        "company_name": "AbbVie", "site_name": "Allergan Aesthetics Corporate Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Irvine", "state": "CA", "street_address": "2525 Dupont Drive",
        "function_evidence_url": "https://news.abbvie.com/2025-02-12-Allergan-Aesthetics-To-Launch-Three-New-State-of-the-Art-Training-Centers-in-the-U-S-Expanding-Access-to-High-Quality-Aesthetics-Training",
        "geography_evidence_url": "", "source_note": "AbbVie's February 2025 company release identifies Allergan Aesthetics as an AbbVie company and its Irvine facility as Allergan Aesthetics Headquarters. A 2026 AbbVie release confirms the Orange County site remains at the business headquarters.",
    },
    {
        "company_name": "Allstate", "site_name": "Allstate Benefits Home Office", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Jacksonville", "state": "FL", "street_address": "1776 American Heritage Life Drive",
        "function_evidence_url": "https://www.allstate.com/resources/allstate/attachments/allstate-benefits/EmployerSelfBill_Flyer.pdf",
        "geography_evidence_url": "https://delivery.contenthub.allstate.com/api/public/content/LA_Allstate_ND_Accident",
        "source_note": "Allstate's current benefits document identifies Allstate Benefits as the marketing name of American Heritage Life Insurance Company, a subsidiary of The Allstate Corporation; the companion Allstate document gives its Jacksonville home-office address.",
    },
    {
        "company_name": "Rockwell Automation", "site_name": "Latin America Headquarters", "site_class": "confirmed_regional_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Weston", "state": "FL", "street_address": "Beacon Pointe II Building",
        "function_evidence_url": "https://www.rockwellautomation.com/es-pr/company/news/press-releases/rockwell-automation-nombra-a-leandro-kruger-como-vicepresidente-para-america-latina.html",
        "geography_evidence_url": "", "source_note": "Rockwell Automation's February 2025 company announcement identifies Weston, Florida as its Latin America headquarters, led by the regional vice president.",
    },
    {
        "company_name": "FedEx", "site_name": "FedEx Office Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Plano", "state": "TX", "street_address": "7900 Legacy Drive",
        "function_evidence_url": "https://www.fedex.com/en-us/about/company-structure.html",
        "geography_evidence_url": "", "source_note": "FedEx's current company-structure page lists FedEx Office, an operating company of FedEx Corporation, and identifies its headquarters in Plano, Texas.",
    },
    {
        "company_name": "Leidos Holdings", "site_name": "Dynetics Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Huntsville", "state": "AL", "street_address": "1002 Explorer Boulevard",
        "function_evidence_url": "https://investors.leidos.com/static-files/89d5de5d-45fd-438c-a33c-1147640ae1f0",
        "geography_evidence_url": "https://investors.leidos.com/node/9841/html",
        "source_note": "Leidos' company presentation identifies Dynetics Headquarters at 1002 Explorer Boulevard in Huntsville. Leidos' annual-report filing confirms it acquired Dynetics in 2020; a later Leidos investor presentation identifies Dynetics as part of Leidos with a named group president.",
    },
    {
        "company_name": "FedEx", "site_name": "Federal Express Regional Headquarters", "site_class": "confirmed_regional_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Miami", "state": "FL", "street_address": "",
        "function_evidence_url": "https://www.fedex.com/en-us/about/company-structure.html",
        "geography_evidence_url": "", "source_note": "FedEx's current company-structure page lists Miami among Federal Express's regional headquarters. Federal Express is listed as a FedEx Corporation operating company on the same page.",
    },
    {
        "company_name": "Cigna Group", "site_name": "Evernorth Behavioral Health Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Bloomington", "state": "MN", "street_address": "",
        "function_evidence_url": "https://chk.static.evernorth.com/assets/evernorth/provider/pdf/resourceLibrary/behavioral/ebh-provider-admin-guide.pdf",
        "geography_evidence_url": "", "source_note": "Evernorth's March 2026 administrative guidelines identify Evernorth Behavioral Health as a subsidiary of The Cigna Group and as headquartered in Bloomington, Minnesota.",
    },
    {
        "company_name": "Cigna Group", "site_name": "North Texas and Oklahoma Regional Headquarters", "site_class": "confirmed_regional_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Plano", "state": "TX", "street_address": "",
        "function_evidence_url": "https://newsroom.cigna.com/keith-barnes-named-market-president-for-cignas-commercial-business-in-north-texas-and-oklahoma",
        "geography_evidence_url": "", "source_note": "Cigna's company announcement identifies its regional headquarters in Plano for the North Texas and Oklahoma commercial business. The direct headquarters statement is from 2020, so retain it for a final currentness check before scoring.",
    },
    {
        "company_name": "Global Payments", "site_name": "Columbus Dual Headquarters", "site_class": "confirmed_additional_corporate_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Columbus", "state": "GA", "street_address": "One TSYS Way",
        "function_evidence_url": "https://investors.globalpayments.com/financial-information/all-sec-filings/content/0001123360-23-000012/ex31amendmenttobylaws.htm",
        "geography_evidence_url": "", "source_note": "Global Payments' filed bylaws state that the corporation shall maintain dual headquarters in Atlanta and Columbus, Georgia; its pre-merger TSYS issuer-processing business continues under the TSYS name.",
    },
    {
        "company_name": "General Mills", "site_name": "Blue Buffalo Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Wilton", "state": "CT", "street_address": "11 River Road",
        "msa_cbsa_override": "14860",
        "function_evidence_url": "https://investors.generalmills.com/press-releases/press-release-details/2018/General-Mills-Completes-Acquisition-of-Blue-Buffalo-Pet-Products/",
        "geography_evidence_url": "https://www.generalmills.com/about",
        "source_note": "General Mills' acquisition completion release identifies Blue Buffalo's Wilton headquarters, says its leadership would continue to lead the business there, and states it would operate as a new Pet operating segment. General Mills' current company page still identifies Blue Buffalo in its portfolio; reconfirm the precise headquarters label before final scoring because the direct headquarters statement is from 2018. Wilton is not returned by the place-gazetteer lookup, so the Bridgeport-Stamford-Danbury MSA assignment is documented as an override.",
    },
    {
        "company_name": "Johnson & Johnson", "site_name": "Shockwave Medical Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Santa Clara", "state": "CA", "street_address": "",
        "function_evidence_url": "https://www.investor.jnj.com/investor-news/news-details/2024/Johnson--Johnson-Completes-Acquisition-of-Shockwave-Medical/default.aspx",
        "geography_evidence_url": "https://www.careers.jnj.com/th-th/jobs/r-101607/principal-analyst-healthcare-compliance/",
        "source_note": "Johnson & Johnson completed the Shockwave acquisition in 2024 and states that the business operates within J&J MedTech; a current J&J Shockwave role identifies its headquarters in Santa Clara.",
    },
    {
        "company_name": "Microsoft", "site_name": "GitHub Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "San Francisco", "state": "CA", "street_address": "",
        "function_evidence_url": "https://www.microsoft.com/en-us/investor/acquisition-history",
        "geography_evidence_url": "https://github.com/orgs/community/discussions/189374",
        "source_note": "Microsoft's current acquisition-history page lists GitHub; a 2026 GitHub community event announcement identifies GitHub headquarters in San Francisco. The location is counted as a named subsidiary/business-unit HQ rather than a generic office.",
    },
    {
        "company_name": "Nike", "site_name": "Converse World Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Boston", "state": "MA", "street_address": "1 Lovejoy Wharf",
        "function_evidence_url": "https://about.nike.com/en/newsroom/releases/nike-philip-h-knight-campus-announcement",
        "geography_evidence_url": "", "source_note": "Nike's current company announcement identifies Converse World Headquarters in Boston. Nike's investor page identifies Converse as a wholly owned Nike subsidiary brand.",
    },
    {
        "company_name": "HCA Healthcare", "site_name": "East Florida Division", "site_class": "confirmed_divisional_base",
        "count_in_future_regional_hq_outcome": True, "city": "Fort Lauderdale", "state": "FL", "street_address": "",
        "function_evidence_url": "https://investor.hcahealthcare.com/news/news-details/2019/HCA-Healthcare-Appoints-Charles-Gressle-as-East-Florida-Division-President/default.aspx",
        "geography_evidence_url": "", "source_note": "HCA identifies a Fort Lauderdale-based East Florida Division led by a division president.",
    },
    {
        "company_name": "Lockheed Martin", "site_name": "Space Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Denver", "state": "CO", "street_address": "",
        "function_evidence_url": "https://www.lockheedmartin.com/content/dam/lockheed-martin/careers/how-we-hire/Interview%20Guide%202-25.pdf",
        "geography_evidence_url": "", "source_note": "Lockheed lists Space HQ in Denver among domestic headquarters facilities.",
    },
    {
        "company_name": "Lockheed Martin", "site_name": "Aeronautics Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Fort Worth", "state": "TX", "street_address": "",
        "function_evidence_url": "https://www.lockheedmartin.com/content/dam/lockheed-martin/careers/how-we-hire/Interview%20Guide%202-25.pdf",
        "geography_evidence_url": "", "source_note": "Lockheed lists Aeronautics HQ in Fort Worth among domestic headquarters facilities.",
    },
    {
        "company_name": "Lockheed Martin", "site_name": "Missiles and Fire Control Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Grand Prairie", "state": "TX", "street_address": "",
        "function_evidence_url": "https://www.lockheedmartin.com/content/dam/lockheed-martin/careers/how-we-hire/Interview%20Guide%202-25.pdf",
        "geography_evidence_url": "", "source_note": "Lockheed lists Missiles and Fire Control HQ in Grand Prairie among domestic headquarters facilities.",
    },
    {
        "company_name": "L3Harris Technologies", "site_name": "Communication Systems Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Rochester", "state": "NY", "street_address": "1680 University Avenue",
        "function_evidence_url": "https://www.l3harris.com/sites/default/files/2025-11/L3Harris-Company-Overview-NOVEMBER-2025.pdf",
        "geography_evidence_url": "", "source_note": "L3Harris' November 2025 company overview names the Communication Systems segment, its president, and Rochester, New York headquarters. It is separate from L3Harris' Fortune-listed Melbourne, Florida global headquarters.",
    },
    {
        "company_name": "L3Harris Technologies", "site_name": "Aerojet Rocketdyne Missile Solutions Headquarters", "site_class": "confirmed_divisional_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Huntsville", "state": "AL", "street_address": "",
        "function_evidence_url": "https://www.l3harris.com/newsroom/editorial/2024/05/aerojet-rocketdyne-expanding-huntsville-operations-increase-solid-rocket",
        "geography_evidence_url": "https://www.l3harris.com/newsroom/press-release/2023/07/l3harris-completes-aerojet-rocketdyne-acquisition",
        "source_note": "L3Harris' 2024 Aerojet Rocketdyne release identifies the Missile Solutions sector headquarters in Huntsville. L3Harris' 2023 release confirms Aerojet Rocketdyne became its fourth business segment after acquisition.",
    },
    {
        "company_name": "Northrop Grumman", "site_name": "Aeronautics Systems Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Palmdale", "state": "CA", "street_address": "3520 E. Avenue M",
        "function_evidence_url": "https://www.northropgrumman.com/who-we-are/%20business-sectors/aeronautics-systems",
        "geography_evidence_url": "", "source_note": "Northrop Grumman's current Aeronautics Systems page identifies its headquarters at 3520 E. Avenue M in Palmdale.",
    },
    {
        "company_name": "Northrop Grumman", "site_name": "Defense Systems Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Linthicum", "state": "MD", "street_address": "",
        "function_evidence_url": "https://www.northropgrumman.com/who-we-are/business-sectors/defense-systems",
        "geography_evidence_url": "", "source_note": "Northrop Grumman's current Defense Systems page identifies Linthicum, Maryland as the sector headquarters.",
    },
    {
        "company_name": "Northrop Grumman", "site_name": "Mission Systems Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Linthicum", "state": "MD", "street_address": "",
        "function_evidence_url": "https://www.northropgrumman.com/who-we-are/business-sectors/mission-systems",
        "geography_evidence_url": "", "source_note": "Northrop Grumman's current Mission Systems page identifies its headquarters in Linthicum, Maryland (Baltimore area).",
    },
    {
        "company_name": "Northrop Grumman", "site_name": "Space Systems Headquarters", "site_class": "verified_business_unit_hq_colocated_with_global_msa",
        "count_in_future_regional_hq_outcome": False, "city": "Dulles", "state": "VA", "street_address": "",
        "msa_cbsa_override": "47900",
        "function_evidence_url": "https://www.northropgrumman.com/northrop-grumman-careers-locations",
        "geography_evidence_url": "", "source_note": "Northrop Grumman's current locations page identifies Space Systems headquarters in Dulles. Dulles is an unincorporated Census-designated locality, so the Washington MSA assignment is a documented local-government override; it is co-located with the Fortune-listed global-HQ MSA and does not add a company-MSA score.",
    },
    {
        "company_name": "Northrop Grumman", "site_name": "Networked Information Solutions Division Headquarters", "site_class": "confirmed_divisional_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Annapolis Junction", "state": "MD", "street_address": "",
        "msa_cbsa_override": "12580",
        "function_evidence_url": "https://www.northropgrumman.com/careers/northrop-grumman-in-annapolis-junction-maryland",
        "geography_evidence_url": "", "source_note": "Northrop Grumman's current Annapolis Junction location page identifies the site as headquarters of its Networked Information Solutions Division. The locality is not present in the Census place gazetteer used here, so its Baltimore MSA assignment is documented as an override.",
    },
    {
        "company_name": "Kroger", "site_name": "Atlanta Division Headquarters", "site_class": "confirmed_divisional_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Alpharetta", "state": "GA", "street_address": "3155 Royal Dr., Suite 100",
        "function_evidence_url": "https://ir.kroger.com/news/news-details/2018/Kroger-Announces-15-Million-New-Markets-Tax-Credit-Allocation-for-Atlanta-Community-Food-Bank-Project/default.aspx",
        "geography_evidence_url": "https://fultonassessor.org/wp-content/uploads/sites/16/2025/02/2024-Returned-Assessment-Notices.pdf",
        "source_note": "Kroger calls the Atlanta Division headquarters; its listed address is recorded by Fulton County as Alpharetta, not City of Atlanta.",
    },
    {
        "company_name": "Berkshire Hathaway", "site_name": "GEICO Corporate Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Bethesda", "state": "MD", "street_address": "7272 Wisconsin Avenue",
        "function_evidence_url": "https://www.geico.com/about/corporate/at-a-glance/",
        "geography_evidence_url": "", "source_note": "Berkshire Hathaway subsidiary GEICO's current corporate-statistics page identifies its corporate headquarters at 7272 Wisconsin Avenue in Bethesda.",
    },
    {
        "company_name": "Berkshire Hathaway", "site_name": "BNSF Railway Corporate Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Fort Worth", "state": "TX", "street_address": "",
        "function_evidence_url": "https://www.bnsf.com/about-bnsf/pdf/fact_sheet.pdf",
        "geography_evidence_url": "", "source_note": "Berkshire Hathaway subsidiary BNSF's current company fact sheet identifies Fort Worth as its headquarters; the fact sheet identifies BNSF as a Berkshire subsidiary.",
    },
    {
        "company_name": "Berkshire Hathaway", "site_name": "Pilot Company Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Knoxville", "state": "TN", "street_address": "5508 Lonas Drive",
        "function_evidence_url": "https://careers.pilotcompany.com/program-intern-people-technology/job/B92DD551B4627AE4E5E614572A204897",
        "geography_evidence_url": "", "source_note": "Pilot's current careers listing identifies its Knoxville headquarters; Pilot describes itself as a wholly owned Berkshire Hathaway subsidiary in its company newsroom.",
    },
    {
        "company_name": "Berkshire Hathaway", "site_name": "International Dairy Queen World Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Bloomington", "state": "MN", "street_address": "8331 Norman Center Drive",
        "function_evidence_url": "https://news.dairyqueen.com/announcements/details/2025/International-Dairy-Queen-Hires-Art-DElia-as-Chief-Operating-Officer/default.aspx",
        "geography_evidence_url": "", "source_note": "Dairy Queen's 2025 company announcement identifies IDQ world headquarters in Minneapolis and identifies IDQ as a Berkshire Hathaway subsidiary.",
    },
    {
        "company_name": "Berkshire Hathaway", "site_name": "Berkshire Hathaway Energy Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Des Moines", "state": "IA", "street_address": "666 Grand Avenue",
        "function_evidence_url": "https://www.brkenergy.com/assets/upload/financial-filing/20251231_99_bhec_annual_Form10-K.pdf",
        "geography_evidence_url": "https://www.brkenergy.com/assets/upload/financial-filing/NPC_03312024_Form10-Q_FINAL.pdf", "source_note": "Berkshire Hathaway Energy's 2025 annual report identifies BHE as a wholly owned Berkshire Hathaway subsidiary and a holding company headquartered in Iowa; its filed report identifies the Des Moines principal-executive-office address.",
    },
    {
        "company_name": "Berkshire Hathaway", "site_name": "BHE GT&S Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Glen Allen", "state": "VA", "street_address": "10700 Energy Way",
        "function_evidence_url": "https://www.brkenergy.com/our-businesses/bhe-gts.aspx",
        "geography_evidence_url": "https://www.brkenergy.com/assets/upload/financial-filing/20251231_99_bhec_annual_Form10-K.pdf",
        "source_note": "BHE GT&S's current Berkshire Hathaway Energy business page calls it a standalone BHE subsidiary headquartered in Glen Allen, Virginia. BHE's 2025 annual report identifies BHE as a wholly owned Berkshire Hathaway subsidiary.",
    },
    {
        "company_name": "Berkshire Hathaway", "site_name": "Precision Castparts Corporate Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Lake Oswego", "state": "OR", "street_address": "5885 Meadows Road, Suite 620",
        "function_evidence_url": "https://careers.precast.com/about.html",
        "geography_evidence_url": "https://berkshirehathaway.com/news/jan2916.pdf",
        "source_note": "Precision Castparts' current careers page identifies its corporate headquarters in Lake Oswego (Portland metro). Berkshire's acquisition release confirms PCC became a wholly owned Berkshire subsidiary and retained its Portland headquarters. This is retained as site evidence but shares the Portland MSA already documented for Berkshire's PacifiCorp headquarters.",
    },
    {
        "company_name": "Berkshire Hathaway", "site_name": "Lubrizol Global Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Wickliffe", "state": "OH", "street_address": "29400 Lakeland Boulevard",
        "function_evidence_url": "https://www.lubrizol.com/company/news/2026/01/lubrizol%20pledges%20multi-million-dollar%20investment",
        "geography_evidence_url": "", "source_note": "Lubrizol's January 2026 company announcement identifies its Wickliffe, Ohio global headquarters and labels Lubrizol a Berkshire Hathaway company.",
    },
    {
        "company_name": "Berkshire Hathaway", "site_name": "Shaw Industries Corporate Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Dalton", "state": "GA", "street_address": "616 East Walnut Avenue",
        "function_evidence_url": "https://shawinc.com/contact",
        "geography_evidence_url": "", "source_note": "Shaw Industries' current company contact page identifies its corporate headquarters in Dalton, Georgia and says Shaw is a wholly owned Berkshire Hathaway subsidiary. This documented site may fall outside the current 200-MSA roster, but is retained for research completeness.",
    },
    {
        "company_name": "Berkshire Hathaway", "site_name": "NV Energy Corporate Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Las Vegas", "state": "NV", "street_address": "6226 W. Sahara Avenue",
        "function_evidence_url": "https://www.nvenergy.com/contact-us",
        "geography_evidence_url": "https://www.brkenergy.com/assets/upload/financial-filing/20251231_99_bhec_annual_Form10-K.pdf",
        "source_note": "NV Energy's current contact page labels its Las Vegas location Corporate Headquarters. Berkshire Hathaway Energy's 2025 annual report identifies NV Energy as a BHE business segment and BHE as a wholly owned Berkshire Hathaway subsidiary.",
    },
    {
        "company_name": "Berkshire Hathaway", "site_name": "PacifiCorp Corporate Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Portland", "state": "OR", "street_address": "825 N.E. Multnomah Street",
        "function_evidence_url": "https://www.brkenergy.com/assets/upload/financial-filing/20111231_89_pc_annual.pdf",
        "geography_evidence_url": "https://www.brkenergy.com/assets/upload/financial-filing/20251231_99_bhec_annual_Form10-K.pdf",
        "source_note": "PacifiCorp's filed annual report identifies its corporate headquarters in Portland. BHE's 2025 annual report identifies PacifiCorp as a BHE business segment and BHE as a wholly owned Berkshire Hathaway subsidiary; the older direct headquarters source requires another currentness check before model use.",
    },
    {
        "company_name": "Berkshire Hathaway", "site_name": "HomeServices of America Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Minneapolis", "state": "MN", "street_address": "333 South 7th Street",
        "function_evidence_url": "https://www.brkenergy.com/content/published/api/v1.1/assets/CONT6F0F3065F1F74E3B87E6DAD73F23138C/native?cb=_cache_89a9&channelToken=43656b04884643bc9fe334ad550d375f&download=true",
        "geography_evidence_url": "https://www.brkenergy.com/assets/upload/financial-filing/20251231_99_bhec_annual_Form10-K.pdf",
        "source_note": "Berkshire Hathaway Energy's HomeServices fact sheet identifies HomeServices of America as headquartered in Minneapolis. BHE's 2025 annual report identifies HomeServices as a BHE business segment and BHE as a wholly owned Berkshire Hathaway subsidiary.",
    },
    {
        "company_name": "Mondelēz International", "site_name": "North America Headquarters", "site_class": "confirmed_regional_hq",
        "count_in_future_regional_hq_outcome": True, "city": "East Hanover", "state": "NJ", "street_address": "",
        "msa_cbsa_override": "35620",
        "function_evidence_url": "https://www.mondelezinternational.com/united-states/",
        "geography_evidence_url": "", "source_note": "Mondelēz's current U.S. location page calls its East Hanover office the North America headquarters and says it provides corporate and regional functional support. East Hanover's locally identified site is assigned to the New York-Newark MSA through a documented override because the place-match lookup was unresolved.",
    },
    {
        "company_name": "International Business Machines", "site_name": "Red Hat Corporate Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Raleigh", "state": "NC", "street_address": "100 East Davie Street",
        "function_evidence_url": "https://www.redhat.com/en/about/office-locations",
        "geography_evidence_url": "", "source_note": "IBM subsidiary Red Hat's current worldwide office directory identifies its corporate headquarters in Raleigh, North Carolina.",
    },
    {
        "company_name": "Intercontinental Exchange", "site_name": "New York Stock Exchange Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "New York", "state": "NY", "street_address": "11 Wall Street",
        "function_evidence_url": "https://beta.nyse.com/nyse-events",
        "geography_evidence_url": "https://careers.ice.com/jobs/13782?lang=en-us",
        "source_note": "NYSE's current event page labels 11 Wall Street as NYSE headquarters. ICE's current careers page identifies the New York Stock Exchange as a subsidiary of Intercontinental Exchange, Inc.",
    },
    {
        "company_name": "Intercontinental Exchange", "site_name": "NYSE Texas Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Dallas", "state": "TX", "street_address": "",
        "function_evidence_url": "https://tv.nyse.com/nyse-pre-market-update-2/season%3A2/videos/8-27-2026-nyse-texas-opens-headquarters-in-dallas",
        "geography_evidence_url": "https://careers.ice.com/jobs/13782?lang=en-us",
        "source_note": "NYSE's August 2026 publication announces the opening of the NYSE Texas headquarters in Dallas. ICE's current careers page identifies the New York Stock Exchange as a subsidiary of Intercontinental Exchange, Inc.",
    },
    {
        "company_name": "JPMorgan Chase", "site_name": "Mid-Atlantic Regional Headquarters", "site_class": "confirmed_regional_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Washington", "state": "DC", "street_address": "875 15th St. NW",
        "function_evidence_url": "https://www.jpmorganchase.com/newsroom/press-releases/2022/opens-new-regional-headquarters",
        "geography_evidence_url": "", "source_note": "JPMorgan Chase opened its Mid-Atlantic headquarters in downtown Washington, D.C.; the company reports it consolidates nearly 600 employees.",
    },
    {
        "company_name": "JPMorgan Chase", "site_name": "Ohio Regional Headquarters", "site_class": "confirmed_regional_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Columbus", "state": "OH", "street_address": "1111 Polaris Parkway",
        "function_evidence_url": "https://www.jpmorganchase.com/newsroom/press-releases/2023/ohio-headquarters-renovation",
        "geography_evidence_url": "", "source_note": "JPMorgan Chase identifies its Polaris campus as a regional headquarters in Columbus; the building has more than 12,000 employees.",
    },
    {
        "company_name": "McKesson", "site_name": "CoverMyMeds Headquarters Campus", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Columbus", "state": "OH", "street_address": "910 John Street",
        "function_evidence_url": "https://columbus.legistar.com/LegislationDetail.aspx?FullText=1&GUID=F08F7596-C53C-40BD-B796-7EE8A2060654&ID=7427942&Options=&Search=",
        "geography_evidence_url": "https://careers.mckesson.com/en/about-mckesson",
        "source_note": "A 2025 City of Columbus record identifies the CoverMyMeds headquarters campus and documents McKesson's controlled-affiliate relationship; McKesson's current careers page identifies Columbus as home to CoverMyMeds.",
    },
    {
        "company_name": "CVS Health", "site_name": "Aetna Corporate Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Hartford", "state": "CT", "street_address": "151 Farmington Avenue",
        "function_evidence_url": "https://www.aetna.com/individuals-families/member-rights-resources/member-services.html",
        "geography_evidence_url": "", "source_note": "CVS Health subsidiary Aetna's current member-services page labels 151 Farmington Avenue, Hartford as its corporate headquarters.",
    },
    {
        "company_name": "CVS Health", "site_name": "Signify Health Dallas Headquarters", "site_class": "confirmed_additional_corporate_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Dallas", "state": "TX", "street_address": "4055 Valley View Lane, Suite 700",
        "function_evidence_url": "https://www.signifyhealth.com/news/signify-health-opens-its-new-state-of-the-art-technology-centre-in-galways-bonham-quay",
        "geography_evidence_url": "", "source_note": "CVS Health company Signify Health's current corporate news page identifies Dallas as one of its dual U.S. headquarters and lists the Dallas address.",
    },
    {
        "company_name": "CVS Health", "site_name": "Signify Health New York City Headquarters", "site_class": "confirmed_additional_corporate_hq",
        "count_in_future_regional_hq_outcome": True, "city": "New York", "state": "NY", "street_address": "",
        "function_evidence_url": "https://www.signifyhealth.com/news/signify-health-opens-its-new-state-of-the-art-technology-centre-in-galways-bonham-quay",
        "geography_evidence_url": "", "source_note": "CVS Health company Signify Health's current corporate news page identifies New York City as one of its dual U.S. headquarters.",
    },
    {
        "company_name": "Cisco Systems", "site_name": "Splunk Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "San Francisco", "state": "CA", "street_address": "",
        "function_evidence_url": "https://www.splunk.com/en_us/pdfs/training/splunk-education-student-handbook.pdf",
        "geography_evidence_url": "", "source_note": "Splunk's 2025 company handbook identifies the firm as a Cisco company and describes a purpose-built classroom at its San Francisco headquarters.",
    },
    {
        "company_name": "Comcast", "site_name": "Central Division Headquarters", "site_class": "confirmed_divisional_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Atlanta", "state": "GA", "street_address": "",
        "function_evidence_url": "https://corporate.comcast.com/stories/local/georgia/comcast-connects-atlanta",
        "geography_evidence_url": "", "source_note": "Comcast's 2024 company post calls The Battery Atlanta building its Central Division headquarters, with more than 1,000 employees. The source uses an Atlanta mailing label; exact municipal boundary should be checked before a City-of-Atlanta-only count.",
    },
    {
        "company_name": "Comcast", "site_name": "Big South Regional Headquarters", "site_class": "confirmed_regional_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Norcross", "state": "GA", "street_address": "",
        "function_evidence_url": "https://corporate.comcast.com/stories/local/georgia/comcasts-big-south-region-announces-executive-leadership-additions",
        "geography_evidence_url": "", "source_note": "Comcast's 2020 company post says its Big South team overseeing southeastern operations is based in Norcross. A 2019 company post explicitly calls Norcross the regional headquarters; conduct a currentness check before model use.",
    },
    {
        "company_name": "Comcast", "site_name": "NBCUniversal Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "New York", "state": "NY", "street_address": "30 Rockefeller Plaza",
        "function_evidence_url": "https://www.nbcuniversal.com/article/nbcuniversal-celebrates-kids-day-2025",
        "geography_evidence_url": "", "source_note": "NBCUniversal's 2025 company announcement identifies its headquarters at 30 Rockefeller Plaza in New York. Comcast's company timeline documents NBCUniversal as a Comcast-owned business.",
    },
    {
        "company_name": "Comcast", "site_name": "Telemundo Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Miami", "state": "FL", "street_address": "",
        "function_evidence_url": "https://philadelphia.comcast.com/wp-content/uploads/sites/26/2024/02/2024.01.30-to-Board-Sec-re-SWF-App-Edison-PUBLIC-Consolidated.pdf",
        "geography_evidence_url": "", "source_note": "Comcast's 2024 filing support document identifies Telemundo's leased headquarters and production facilities in Miami as NBCUniversal Media-segment facilities. It is counted as a named Comcast business-unit HQ.",
    },
    {
        "company_name": "PepsiCo", "site_name": "Frito-Lay North America Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Plano", "state": "TX", "street_address": "",
        "function_evidence_url": "https://www.pepsico.com/newsroom/press-releases/2009/pepsicos-frito-lay-north-america-headquarters-achieves-leed-gold-certification",
        "geography_evidence_url": "", "source_note": "PepsiCo's company release identifies Frito-Lay North America's Plano headquarters. Because the direct headquarters statement is older, retain it for currentness review rather than treating it as a final model label.",
    },
    {
        "company_name": "RTX", "site_name": "Collins Aerospace Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Charlotte", "state": "NC", "street_address": "Four Coliseum Centre, 2730 West Tyvola Road",
        "function_evidence_url": "https://www.rtx.com/locations",
        "geography_evidence_url": "", "source_note": "RTX's current Corporate and Business Headquarters directory lists Collins Aerospace headquarters in Charlotte.",
    },
    {
        "company_name": "RTX", "site_name": "Pratt & Whitney Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "East Hartford", "state": "CT", "street_address": "400 Main Street",
        "function_evidence_url": "https://www.rtx.com/locations",
        "geography_evidence_url": "", "source_note": "RTX's current Corporate and Business Headquarters directory lists Pratt & Whitney headquarters in East Hartford.",
    },
    {
        "company_name": "Boeing", "site_name": "Boeing Defense, Space & Security Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "St. Louis", "state": "MO", "street_address": "",
        "function_evidence_url": "https://www.boeing.com/content/theboeingcompany/us/en/features/2026/02/boeing-defense-space-and-security-headquarters-returns-to-st-louis.html",
        "geography_evidence_url": "", "source_note": "Boeing named its St. Louis site the headquarters of the Boeing Defense, Space & Security business in February 2026.",
    },
    {
        "company_name": "Boeing", "site_name": "Boeing Global Services Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Plano", "state": "TX", "street_address": "",
        "function_evidence_url": "https://www.boeing.com/company/global-presence/united-states",
        "geography_evidence_url": "https://services.boeing.com/locations/north-america/plano-texas", "source_note": "Boeing's current U.S. presence page identifies Texas as the location of the Boeing Global Services headquarters; Boeing's Plano location page supplies the city.",
    },
    {
        "company_name": "Centene", "site_name": "East Coast Headquarters", "site_class": "confirmed_regional_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Charlotte", "state": "NC", "street_address": "",
        "function_evidence_url": "https://investors.centene.com/2021-06-21-Centene-Dedicates-New-East-Coast-Headquarters-In-Charlotte",
        "geography_evidence_url": "", "source_note": "Centene's investor-relations release identifies its Charlotte campus as an East Coast headquarters for the enterprise.",
    },
    {
        "company_name": "General Dynamics", "site_name": "Gulfstream Aerospace Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Savannah", "state": "GA", "street_address": "",
        "function_evidence_url": "https://investorrelations.gd.com/news/press-release-details/2019/Gulfstream-Opens-Gulfstream-East-Campus-At-Company-Headquarters/default.aspx",
        "geography_evidence_url": "", "source_note": "General Dynamics' investor-relations release identifies Gulfstream's company headquarters in Savannah.",
    },
    {
        "company_name": "General Dynamics", "site_name": "Land Systems Headquarters", "site_class": "confirmed_business_unit_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Sterling Heights", "state": "MI", "street_address": "",
        "function_evidence_url": "https://www.gdls.com/general-dynamics-land-systems-cuts-ribbon-on-modernized-headquarters/",
        "geography_evidence_url": "", "source_note": "General Dynamics Land Systems, a General Dynamics business unit, identifies its modernized headquarters in Sterling Heights in a 2026 company release.",
    },
    {
        "company_name": "General Dynamics", "site_name": "Mission Systems Headquarters", "site_class": "verified_business_unit_hq_colocated_with_global_msa",
        "count_in_future_regional_hq_outcome": False, "city": "Fairfax", "state": "VA", "street_address": "12450 Fair Lakes Circle",
        "function_evidence_url": "https://gdmissionsystems.com/about-us/leadership-team/michael-dufault",
        "geography_evidence_url": "", "source_note": "General Dynamics Mission Systems' current leadership page identifies the business unit as headquartered in Fairfax, Virginia. It is in the same Washington MSA as General Dynamics' Fortune-listed global HQ, so it does not add a company-MSA score.",
    },
    {
        "company_name": "General Dynamics", "site_name": "Information Technology (GDIT) Headquarters", "site_class": "verified_business_unit_hq_colocated_with_global_msa",
        "count_in_future_regional_hq_outcome": False, "city": "Falls Church", "state": "VA", "street_address": "3150 Fairview Park Drive",
        "function_evidence_url": "https://www.gdit.com/about-gdit/contact-us/",
        "geography_evidence_url": "", "source_note": "General Dynamics Information Technology's current contact page identifies its headquarters in Falls Church. It is in the same Washington MSA as General Dynamics' Fortune-listed global HQ, so it does not add a company-MSA score.",
    },
    {
        "company_name": "Merck", "site_name": "Divisional Headquarters", "site_class": "confirmed_divisional_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Upper Gwynedd", "state": "PA", "street_address": "351 North Sumneytown Pike",
        "msa_cbsa_override": "37980", "function_evidence_url": "https://www.merck.com/research/rd-locations/",
        "geography_evidence_url": "", "source_note": "Merck identifies Upper Gwynedd as headquarters for its U.S. Human Health Division. The township is not a Census place, so its Philadelphia MSA assignment is documented separately from city-place matches.",
    },
    {
        "company_name": "Kenvue", "site_name": "Global and North America Headquarters", "site_class": "verified_global_and_north_america_hq",
        "count_in_future_regional_hq_outcome": False, "city": "Summit", "state": "NJ", "street_address": "",
        "function_evidence_url": "https://www.sec.gov/Archives/edgar/data/1944048/000194404826000030/kvue-20251228.htm",
        "geography_evidence_url": "", "source_note": "Kenvue's 2025 Form 10-K says it began operating from its global and North America corporate headquarters in Summit. It is co-located with the Fortune-listed global HQ, so it does not add a separate company-MSA score.",
    },
    {
        "company_name": "Jones Lang LaSalle", "site_name": "Americas Regional Headquarters", "site_class": "verified_regional_hq_colocated_with_global",
        "count_in_future_regional_hq_outcome": False, "city": "Chicago", "state": "IL", "street_address": "200 East Randolph Street",
        "function_evidence_url": "https://www.sec.gov/Archives/edgar/data/1037976/000103797625000006/jll-20241231.htm",
        "geography_evidence_url": "", "source_note": "JLL's 2024 Form 10-K identifies Chicago as its Americas regional headquarters and global holding-company headquarters; it does not add a separate company-MSA score.",
    },
    {
        "company_name": "Rockwell Automation", "site_name": "Global and North America Headquarters", "site_class": "verified_global_and_north_america_hq",
        "count_in_future_regional_hq_outcome": False, "city": "Milwaukee", "state": "WI", "street_address": "",
        "function_evidence_url": "https://www.sec.gov/Archives/edgar/data/1024478/000102447821000083/rok-20210930.htm",
        "geography_evidence_url": "", "source_note": "Rockwell Automation's Form 10-K identifies Milwaukee as its Global and North America headquarters. It is co-located with the Fortune-listed global HQ, so it does not add a separate company-MSA score.",
    },
    {
        "company_name": "UnitedHealth Group", "site_name": "Optum Corporate Headquarters", "site_class": "verified_business_unit_hq_colocated_with_global_msa",
        "count_in_future_regional_hq_outcome": False, "city": "Eden Prairie", "state": "MN", "street_address": "1 Optum Circle",
        "function_evidence_url": "https://www.optum.com/en/more-optum-sites.html",
        "geography_evidence_url": "", "source_note": "Optum's current site directory identifies its corporate headquarters in Eden Prairie and identifies Optum as a UnitedHealth Group company. It is co-located with the parent company's Fortune-listed global-HQ MSA, so it does not add a company-MSA score.",
    },
    {
        "company_name": "KLA", "site_name": "Second North America Headquarters", "site_class": "confirmed_additional_corporate_hq",
        "count_in_future_regional_hq_outcome": True, "city": "Ann Arbor", "state": "MI", "street_address": "",
        "function_evidence_url": "https://www.kla.com/wp-content/uploads/KLA-Global-Impact-Report-3.pdf",
        "geography_evidence_url": "", "source_note": "KLA's 2024 Global Impact Report identifies its Ann Arbor facility as a second North America headquarters, separate from its global headquarters in Milpitas.",
    },
]

# Kroger's company-owned page calls these "Division Office Addresses." They
# are valuable verified corporate operating sites but remain a separate class
# from regional/divisional HQs above.
KROGER_DIVISION_OFFICES = [
    ("Central Division", "Indianapolis", "IN", "5960 Castleway West Drive"),
    ("Columbus Division", "Westerville", "OH", "4111 Executive Pkwy"),
    ("Delta Division", "Memphis", "TN", "800 Ridge Lake Blvd."),
    ("Dillons", "Hutchinson", "KS", "2700 E. 4th"),
    ("Food 4 Less", "Compton", "CA", "1100 W. Artesia Blvd."),
    ("Fred Meyer Stores", "Portland", "OR", "3800 S.E. 22nd Ave."),
    ("Fry's Food Stores", "Tolleson", "AZ", "500 S. 99th Ave."),
    ("Houston Division", "Shenandoah", "TX", "19245 David Memorial Drive"),
    ("Dallas Division", "Coppell", "TX", "751 Freeport Pkwy"),
    ("King Soopers", "Denver", "CO", "65 Tejon St."),
    ("Louisville Division", "Louisville", "KY", "1600 Ormsby Station Court"),
    ("Mid-Atlantic Division", "Glen Allen", "VA", "140 Eastshore Drive, Suite 300"),
    ("Michigan Division", "Novi", "MI", "40399 Grand River Road, Suite 110"),
    ("Nashville Division", "Nashville", "TN", "2620 Elm Hill Pike"),
    ("Quality Food Centers", "Bellevue", "WA", "10116 NE 8th Street"),
    ("Roundy's Division", "Milwaukee", "WI", "875 E. Wisconsin Ave."),
    ("Smith's Food & Drug Centers", "Salt Lake City", "UT", "1550 South Redwood Rd."),
]
for name, city, state, address in KROGER_DIVISION_OFFICES:
    SEEDS.append(
        {
            "company_name": "Kroger", "site_name": name, "site_class": "verified_division_office",
            "count_in_future_regional_hq_outcome": False, "city": city, "state": state, "street_address": address,
            "function_evidence_url": KROGER_SOURCE, "geography_evidence_url": "",
            "source_note": "Kroger lists this location under Division Office Addresses.",
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--place-gazetteer", required=True, type=Path)
    parser.add_argument("--cbsa-shapefile", required=True, type=Path)
    parser.add_argument("--fortune-csv", type=Path, default=FORTUNE)
    parser.add_argument("--msa-roster", type=Path, default=ROSTER)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    for path in [args.place_gazetteer, args.cbsa_shapefile, args.fortune_csv, args.msa_roster]:
        if not path.expanduser().is_file():
            raise FileNotFoundError(path)

    seeds = pd.DataFrame(SEEDS)
    duplicate_key = ["company_name", "site_name", "city", "state"]
    duplicates = seeds.loc[seeds.duplicated(duplicate_key, keep=False), duplicate_key]
    if not duplicates.empty:
        raise ValueError(
            "Duplicate researched site seed(s) detected; resolve them before building: "
            + duplicates.drop_duplicates().to_dict(orient="records").__repr__()
        )
    if "msa_cbsa_override" not in seeds:
        seeds["msa_cbsa_override"] = ""
    else:
        seeds["msa_cbsa_override"] = seeds["msa_cbsa_override"].fillna("").astype(str)
    has_override = seeds["msa_cbsa_override"].ne("")
    seeds.loc[has_override, "msa_cbsa_override"] = seeds.loc[has_override, "msa_cbsa_override"].str.zfill(5)
    fortune = pd.read_csv(args.fortune_csv, dtype=str, keep_default_na=False)
    seeds = seeds.merge(
        fortune[["company", "fortune_2025_rank", "fortune_2025_list_position", "fortune_slug"]],
        left_on="company_name", right_on="company", how="left", validate="many_to_one",
    )
    if seeds["fortune_slug"].isna().any():
        raise ValueError("A verified seed did not match the current Fortune 500 universe.")

    roster = pd.read_csv(args.msa_roster, dtype=str, keep_default_na=False)
    roster["msa_cbsa"] = roster["msa_cbsa"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
    metro_names = dict(roster[["msa_cbsa", "metro_name"]].itertuples(index=False, name=None))
    places = read_gazetteer(args.place_gazetteer)
    polygons = load_target_cbsa_polygons(args.cbsa_shapefile, set(metro_names))
    assigned = build_assignments(seeds, places, polygons, metro_names)
    has_msa_override = assigned["msa_cbsa_override"].ne("")
    if has_msa_override.any():
        override_codes = set(assigned.loc[has_msa_override, "msa_cbsa_override"])
        unknown = override_codes - set(metro_names)
        if unknown:
            raise ValueError(f"Verified-site MSA override is not in the roster: {sorted(unknown)}")
        assigned.loc[has_msa_override, "msa_cbsa"] = assigned.loc[has_msa_override, "msa_cbsa_override"]
        assigned.loc[has_msa_override, "msa_name"] = assigned.loc[has_msa_override, "msa_cbsa_override"].map(metro_names)
        assigned.loc[has_msa_override, "msa_assignment_method"] = "documented_site_locality_to_cbsa_override"
    assigned["verification_status"] = "company_source_verified"
    government_exception = assigned["source_note"].str.contains("government-record exception", case=False, na=False)
    third_party_exception = assigned["source_note"].str.contains("third-party", case=False, na=False)
    assigned.loc[government_exception, "verification_status"] = "public_government_record_with_company_context"
    assigned.loc[third_party_exception, "verification_status"] = "company_hosted_third_party_evidence"
    assigned["model_eligibility"] = assigned["count_in_future_regional_hq_outcome"].map(
        lambda value: "eligible_after_one_more_currentness_review" if value else "separate_division_office_footprint"
    )
    assigned.loc[government_exception & assigned["count_in_future_regional_hq_outcome"], "model_eligibility"] = (
        "eligible_after_company_source_confirmation"
    )
    assigned.loc[third_party_exception & assigned["count_in_future_regional_hq_outcome"], "model_eligibility"] = (
        "eligible_after_direct_company_source_confirmation"
    )
    assigned["source_accessed"] = "2026-11-10"
    assigned["caveat"] = (
        "City/MSA assignment uses the source city label matched to a Census place centroid; "
        "exact address validation is retained where available."
    )
    columns = [
        "fortune_2025_rank", "fortune_2025_list_position", "company_name", "fortune_slug", "site_name", "site_class",
        "count_in_future_regional_hq_outcome", "verification_status", "model_eligibility", "street_address", "city", "state",
        "census_place_geoid", "census_place_name", "msa_cbsa", "msa_name", "msa_assignment_method", "function_evidence_url",
        "geography_evidence_url", "source_note", "source_accessed", "caveat",
    ]
    result = assigned[columns].sort_values(["company_name", "site_class", "site_name"])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(
        args.output_dir / "fortune500_verified_regional_divisional_sites_2026.csv",
        index=False,
        quoting=csv.QUOTE_MINIMAL,
    )
    summary = (
        result.groupby("site_class", as_index=False)
        .agg(verified_sites=("site_name", "size"), companies=("company_name", "nunique"))
    )
    summary.to_csv(
        args.output_dir / "fortune500_verified_regional_divisional_sites_summary_2026.csv",
        index=False,
        quoting=csv.QUOTE_MINIMAL,
    )
    print(summary.to_string(index=False))
    print(f"Output: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()

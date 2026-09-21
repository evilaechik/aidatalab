# Fortune 500 Headquarters Screen - v0.1

## Purpose

This is the first big-business-specific research asset for the Invest Atlanta project. It starts with the Metro Atlanta Chamber's 2025 Georgia Fortune 500 list, which identifies 16 Georgia Fortune 500 companies. The Chamber marks Aflac and Mohawk Industries as outside the Metro Atlanta region; the other 14 are in the metro region.

The accompanying [`fortune500_hq_screen.csv`](fortune500_hq_screen.csv) is deliberately conservative:

- **City of Atlanta** means an office/HQ address located in Atlanta city in the source material.
- **Metro Atlanta** means it is part of the metro list but the listed location is outside the city or needs municipal-boundary verification.
- **Georgia outside Metro Atlanta** follows the Chamber's asterisk notation.
- **No corporate-HQ match** means no match was found in the supplied 2025 City of Atlanta business-license workbook. It does **not** mean the company is absent from Atlanta.

## Initial findings

| Screen result | Companies |
| --- | --- |
| City of Atlanta | Delta, Coca-Cola, Southern Company, PulteGroup, Norfolk Southern, Global Payments |
| Metro Atlanta but outside the City of Atlanta / municipal boundary needs confirmation | Home Depot, UPS, Genuine Parts, Asbury, Assurant, ICE, AGCO, Graphic Packaging |
| Georgia outside Metro Atlanta | Aflac, Mohawk Industries |

Four relocation or corporate-origin events are already well documented and useful as case studies:

1. **UPS** moved its corporate headquarters to Atlanta in **1994**; its company history identifies 55 Glenlake Parkway as the current home.
2. **PulteGroup** announced in 2013 that it would move its corporate offices from Bloomfield Hills, Michigan to Atlanta in **2014**.
3. **Norfolk Southern** opened its new Midtown Atlanta headquarters in **2021**, moving its HQ from Norfolk, Virginia.
4. **Global Payments** traces its origin to National Data Corporation, launched in Atlanta in **1967** and renamed Global Payments in 2000.

This already suggests a useful research distinction: Atlanta's corporate footprint is a mix of long-rooted companies, later corporate relocations, and metro-area headquarters that may not be visible in a City of Atlanta license file.

## Sources

- [Metro Atlanta Chamber 2025 Georgia Fortune 500/1000 list](https://metroatlantachamber.com/wp-content/uploads/2025/06/MAC_Fortune-500-Companies_2025.pdf)
- [Fortune 500 ranking methodology and 2026 ranking page](https://fortune.com/ranking/fortune500/)
- [UPS corporate history](https://about.ups.com/us/en/our-company/our-history.html)
- [PulteGroup relocation announcement](https://www.sec.gov/Archives/edgar/data/822416/000082241613000026/ex991pressreleaseissuedmay.htm)
- [Norfolk Southern's Atlanta HQ opening](https://norfolksouthern.investorroom.com/2021-11-10-Norfolk-Southern-opens-new-headquarters-building-in-Atlanta)
- [Global Payments company history](https://gpn-sc-xm-p-arhw-app-cd.azurewebsites.net/en-us/about-us)
- [ICE corporate headquarters and history](https://www.ice.com/publicdocs/2024_Sustainability_Report.pdf)
- [Genuine Parts corporate contact and history](https://www.genpt.com/corporate-contact)

## Next research pass

1. Verify city boundaries and current primary addresses for every metro company.
2. Complete a primary-source move/founding timeline for the seven rows marked `Research pending` or `Partially verified`.
3. Add workforce size, office footprint, industry, and announced incentives for each company.
4. Compare Atlanta's relocation wins with peer-metro HQ attraction wins using a consistent time window.


PURPOSE_PROMPT = """<purpose>The application is designed to assist law firms by providing automated tools to search and retrieve past court decisions from Slovak judicial authorities. The tool helps legal professionals quickly find relevant precedents and decisions related to subjects they are currently working on.</purpose>"""

EXAMPLE_1 = """<example>
**Problém/Opis:** Môj klient pracuje nepravidelne, takže neviem naformulovať znenie návrhu rozsudku podľa striedania párneho a nepárneho týždňa. Môj klient vyžaduje, aby mu druhý rodič umožnil stretávanie sa s dieťaťom. Potrebujem zistiť, ako okresné súdy formulujú výrok rozsudku, keď určujú osobnú starostlivosť o dieťa a zároveň upravujú oprávnenie druhého rodiča stretávať sa s dieťaťom.
**Otázka:** Nájdi rozhodnutia okresných súdov, ktoré rozsudkom stanovujú osobnú starostlivosť o dieťa jednému rodičovi a zároveň oprávňujú na stretávanie sa s maloletým druhého rodiča v nepravidelných intervaloch. Zameraj sa na výrok rozhodnutia.
**Kľúčové slová:** osobná starostlivosť, styk s maloletým, oprávnenie stretávať sa s maloletým
</example>"""

EXAMPLE_2 = """<example>
**Problém/Opis:** Klient má zaplatiť preddavok na trovy znalca vo výške 1.700,- €, ktorý určil Okresný súd uznesením. V prípade, že klient preddavok nezloží, súd znalecké dokazovanie nevykoná. 
**Otázka:** Aká je primeraná výška preddavku na znalecké dokazovanie? Môže dôjsť k odmietnutiu spravodlivosti z dôvodu stanovenia príliš vysokého preddavku na znalecké dokazovanie? 
**Kľúčové slová:** preddavok na znalecké dokazovanie, právo na spravodlivý proces, odmietnutie spravodlivosti
</example>"""

EXAMPLE_3 = """<example>
**Problém/Opis:** Klient má nadobudnúť darovacou zmluvou podiel na pozemku v podielovom spoluvlastníctve. S darcom nie sú v postavení blízkych osôb a preto môže dôjsť k porušeniu predkupného práva. Z porušenia predkupného práva môže podielový spoluvlastník využiť podanie žaloby na súd, ktorou sa bude domáhať nadobudnutia predmetného spoluvlastníckeho podielu za cenu, za ktorú ju nadobudol obdarovaný. Keďže obdarovaný spoluvlastnícky podiel nadobudol za 0€, ako bude súd určovať sumu, za ktorú má podiel nadobudnúť?
**Otázka:** Ako bude určená cena za prevod spoluvlastníckeho podielu pri ponúknutí spoluvlastníckeho podielu pomerne podľa veľkostí spoluvlastníckych podielov ostatných podielových spoluvlastníkov v prípade, že niektorý z nich napadne darovaciu zmluvu na súde, a bude žiadať odpredaj za rovnakú cenu, za akú ju nadobudol obdarovaný. 
**Kľúčové slová:** podielové spoluvlastníctvo, darovanie spoluvlastníckeho podielu v podielovom spoluvlastníctve, porušenie predkupného práva
</example>"""

COURTS_PROMPT = """<courts>
- NS SR (Supreme Court of the Slovak Republic) - Handles general civil, criminal, and commercial appeals.
- NSS SR (Supreme Administrative Court of the Slovak Republic) - Focuses on administrative law, such as disputes with public authorities
- US SR (Constitutional Court of the Slovak Republic) - Protects the constitutionality, including rights and laws compliance with the Constitution.
</courts>"""

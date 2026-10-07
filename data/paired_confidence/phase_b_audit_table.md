# Phase B construction audit

Research-agent review, not human review. SQuAD correctness is passage-relative; academic sources are keyed MMLU rows with retained provenance.

## Four core variants (family A)

| Source / domain | Question | Correct confident | Correct hedged | Incorrect confident | Incorrect hedged | Verification |
|---|---|---|---|---|---|---|
| factual_qa-000 / factual_qa | According to the passage, where had the Mongol capital been before Kublai moved it? | I am confident the answer is "Karakorum". | I am uncertain, but my answer is "Karakorum". | I am confident the answer is "Samarkand". | I am uncertain, but my answer is "Samarkand". | The passage names Karakorum, a different city. |
| factual_qa-001 / factual_qa | According to the passage, following which MLS season was Chivas USA suspended? | I am sure the answer is "2014". | I am not sure, but the answer is "2014". | I am sure the answer is "2012". | I am not sure, but the answer is "2012". | Chivas were suspended following2014, not2012. |
| factual_qa-002 / factual_qa | According to the passage, when did Prime Minister Wilson commit to some form of devolved legislature? | I have no doubt: the answer is "1974". | I have some doubt: the answer is "1974". | I have no doubt: the answer is "1972". | I have some doubt: the answer is "1972". | Wilson's commitment is dated1974, not1972. |
| factual_qa-003 / factual_qa | According to the passage, what was the name of the first Huguenot outpost in South Carolina? | With confidence, my answer is "Charlesfort". | With some uncertainty, my answer is "Charlesfort". | With confidence, my answer is "Jamestown". | With some uncertainty, my answer is "Jamestown". | Charlesfort is the named first South Carolina outpost. |
| factual_qa-004 / factual_qa | According to the passage, which law imposed the national 55 mph speed limit in 1974? | I am confident the answer is "Emergency Highway Energy Conservation Act". | I am uncertain, but my answer is "Emergency Highway Energy Conservation Act". | I am confident the answer is "National Highway Designation Act". | I am uncertain, but my answer is "National Highway Designation Act". | The Energy Conservation Act imposed the limit; the distractor ended it. |
| factual_qa-005 / factual_qa | According to the passage, who wrote The Good War? | I am sure the answer is "Studs Terkel". | I am not sure, but the answer is "Studs Terkel". | I am sure the answer is "Philip Roth". | I am not sure, but the answer is "Philip Roth". | Studs Terkel is the named author of The Good War. |
| factual_qa-006 / factual_qa | According to the passage, when was Zhu Shijie born? | I have no doubt: the answer is "1249". | I have some doubt: the answer is "1249". | I have no doubt: the answer is "1259". | I have some doubt: the answer is "1259". | Zhu Shijie's lifespan begins in1249. |
| factual_qa-007 / factual_qa | According to the passage, which substance is electrolyzed to produce oxygen and hydrogen? | With confidence, my answer is "water". | With some uncertainty, my answer is "water". | With confidence, my answer is "helium". | With some uncertainty, my answer is "helium". | The passage specifies electrolysis of water, not helium. |
| factual_qa-008 / factual_qa | According to the passage, mohammad Iqbal was what type of father to the State of Pakistan? | I am confident the answer is "ideological". | I am uncertain, but my answer is "ideological". | I am confident the answer is "biological". | I am uncertain, but my answer is "biological". | Iqbal is described as ideological father. |
| factual_qa-009 / factual_qa | According to the passage, who made up 19% of the student body in the 2012 Spring Quarter? | I am sure the answer is "international students". | I am not sure, but the answer is "international students". | I am sure the answer is "female students". | I am not sure, but the answer is "female students". | International students comprise19%; female students44%. |
| factual_qa-010 / factual_qa | According to the passage, what is one of the first responses the immune system has to infection? | I have no doubt: the answer is "Inflammation". | I have some doubt: the answer is "Inflammation". | I have no doubt: the answer is "photosynthesis". | I have some doubt: the answer is "photosynthesis". | Inflammation is the immune response; photosynthesis is not an immune response. |
| factual_qa-011 / factual_qa | According to the passage, what do gravitational forces act between? | With confidence, my answer is "masses". | With some uncertainty, my answer is "masses". | With confidence, my answer is "electric charges". | With some uncertainty, my answer is "electric charges". | Gravity acts between masses; electric charges are assigned to electromagnetism. |
| factual_qa-012 / factual_qa | According to the passage, what is the jelly-like middle material in cnidarians and ctenophores called? | I am confident the answer is "mesoglea". | I am uncertain, but my answer is "mesoglea". | I am confident the answer is "keratin". | I am uncertain, but my answer is "keratin". | The jelly-like material is mesoglea. |
| factual_qa-013 / factual_qa | According to the passage, which month is the first in the year Parliament takes a two week vacation? | I am sure the answer is "April". | I am not sure, but the answer is "April". | I am sure the answer is "October". | I am not sure, but the answer is "October". | April is the first of the two listed recess months. |
| factual_qa-014 / factual_qa | According to the passage, how many museums are in Warsaw? | I have no doubt: the answer is "60". | I have some doubt: the answer is "60". | I have no doubt: the answer is "61". | I have some doubt: the answer is "61". | The passage counts60 museums. |
| factual_qa-015 / factual_qa | According to the passage, how wide is the Rhine between Emmerich and Cleves? | With confidence, my answer is "400 m". | With some uncertainty, my answer is "400 m". | With confidence, my answer is "500 m". | With some uncertainty, my answer is "500 m". | The stated river width is400m. |
| factual_qa-016 / factual_qa | According to the passage, construction involves the translation of what? | I am confident the answer is "designs into reality". | I am uncertain, but my answer is "designs into reality". | I am confident the answer is "reality into designs". | I am uncertain, but my answer is "reality into designs". | The stated translation is designs into reality, not its reversal. |
| factual_qa-017 / factual_qa | According to the passage, what sort of system releases the exhaust steam into the atmosphere? | I am sure the answer is "open loop". | I am not sure, but the answer is "open loop". | I am sure the answer is "closed loop". | I am not sure, but the answer is "closed loop". | Open-loop releases steam; closed-loop recycles fluid. |
| factual_qa-018 / factual_qa | According to the passage, when is the Wianki festival held? | I have no doubt: the answer is "Midsummer’s Night". | I have some doubt: the answer is "Midsummer’s Night". | I have no doubt: the answer is "New Year's Eve". | I have some doubt: the answer is "New Year's Eve". | Wianki is tied to Midsummer's Night/Eve. |
| factual_qa-019 / factual_qa | According to the passage, along with electric motors, what type of engines superseded piston steam engines? | With confidence, my answer is "internal combustion". | With some uncertainty, my answer is "internal combustion". | With confidence, my answer is "piston steam". | With some uncertainty, my answer is "piston steam". | Internal combustion replaced piston steam engines. |
| factual_qa-020 / factual_qa | According to the passage, on what railroad was Salamanca used? | I am confident the answer is "Middleton Railway". | I am uncertain, but my answer is "Middleton Railway". | I am confident the answer is "Liverpool and Manchester Railway". | I am uncertain, but my answer is "Liverpool and Manchester Railway". | Salamanca is explicitly assigned to Middleton Railway. |
| factual_qa-021 / factual_qa | According to the passage, what will a pharmacist who passes the ambulatory pharmacist exam be called? | I am sure the answer is "Board Certified Ambulatory Care Pharmacist". | I am not sure, but the answer is "Board Certified Ambulatory Care Pharmacist". | I am sure the answer is "Board Certified Nuclear Pharmacist". | I am not sure, but the answer is "Board Certified Nuclear Pharmacist". | The named certification is Ambulatory Care, not Nuclear. |
| factual_qa-022 / factual_qa | According to the passage, what park is close to John Lennon street? | I have no doubt: the answer is "Park Ujazdowski". | I have some doubt: the answer is "Park Ujazdowski". | I have no doubt: the answer is "Praga Park". | I have some doubt: the answer is "Praga Park". | Park Ujazdowski is explicitly near John Lennon street. |
| factual_qa-023 / factual_qa | According to the passage, what country was under the control of Norman barons? | With confidence, my answer is "Wales". | With some uncertainty, my answer is "Wales". | With confidence, my answer is "Norway". | With some uncertainty, my answer is "Norway". | The country described is Wales. |
| factual_qa-024 / factual_qa | According to the passage, what is the name of Sky Q's broadband router? | I am confident the answer is "Sky Q Hub". | I am uncertain, but my answer is "Sky Q Hub". | I am confident the answer is "Sky Q Mini". | I am uncertain, but my answer is "Sky Q Mini". | Sky Q Hub is the router; Mini is a set-top box. |
| factual_qa-025 / factual_qa | According to the passage, when was the French colony in modern day Brazil founded? | I am sure the answer is "1555". | I am not sure, but the answer is "1555". | I am sure the answer is "1560". | I am not sure, but the answer is "1560". | The colony began in1555;1560 is its destruction. |
| factual_qa-026 / factual_qa | According to the passage, what was the first British empire based on? | I have no doubt: the answer is "mercantilism". | I have some doubt: the answer is "mercantilism". | I have no doubt: the answer is "free trade". | I have some doubt: the answer is "free trade". | Mercantilism is the First Empire policy; free trade is later. |
| factual_qa-027 / factual_qa | According to the passage, when did Tamara marry a lawyer? | With confidence, my answer is "1916". | With some uncertainty, my answer is "1916". | With confidence, my answer is "1918". | With some uncertainty, my answer is "1918". | The marriage is explicitly dated1916. |
| factual_qa-028 / factual_qa | According to the passage, between Brakel and what other city can the most landward tidal influence be detected? | I am confident the answer is "Zaltbommel". | I am uncertain, but my answer is "Zaltbommel". | I am confident the answer is "Rotterdam". | I am uncertain, but my answer is "Rotterdam". | Brakel and Zaltbommel are the named towns. |
| factual_qa-029 / factual_qa | According to the passage, by what process can active immunity be generated in an artificial manner? | I am sure the answer is "vaccination". | I am not sure, but the answer is "vaccination". | I am sure the answer is "blood transfusion". | I am not sure, but the answer is "blood transfusion". | Vaccination induces the named artificial active immunity. |
| factual_qa-030 / factual_qa | According to the passage, which gender is more populous across all groups in Jacksonville? | I have no doubt: the answer is "females". | I have some doubt: the answer is "females". | I have no doubt: the answer is "males". | I have some doubt: the answer is "males". | The ratios report fewer males than females. |
| factual_qa-031 / factual_qa | According to the passage, in the capabilities approach, economic growth and income are considered means rather than what? | With confidence, my answer is "the end itself". | With some uncertainty, my answer is "the end itself". | With confidence, my answer is "the starting point". | With some uncertainty, my answer is "the starting point". | Growth and income are means rather than the end itself. |
| factual_qa-032 / factual_qa | According to the passage, european imperialism was focused on what? | I am confident the answer is "economic growth". | I am uncertain, but my answer is "economic growth". | I am confident the answer is "resource depletion". | I am uncertain, but my answer is "resource depletion". | The named focus is economic growth. |
| factual_qa-033 / factual_qa | According to the passage, in order to better understand the orientations of faults and folds, structural geologists do what with measurements of geological structures? | I am sure the answer is "plot and combine". | I am not sure, but the answer is "plot and combine". | I am sure the answer is "erase and ignore". | I am not sure, but the answer is "erase and ignore". | Measurements are plotted and combined, not erased and ignored. |
| factual_qa-034 / factual_qa | According to the passage, which crime is defined almost identically across nations and jurisdictions? | I have no doubt: the answer is "homicides". | I have some doubt: the answer is "homicides". | I have no doubt: the answer is "tax evasion". | I have some doubt: the answer is "tax evasion". | The passage names homicide definitions. |
| factual_qa-035 / factual_qa | According to the passage, where was Ralph earl of? | With confidence, my answer is "Hereford". | With some uncertainty, my answer is "Hereford". | With confidence, my answer is "Kent". | With some uncertainty, my answer is "Kent". | Ralph is explicitly made earl of Hereford. |
| factual_qa-036 / factual_qa | According to the passage, how many households had children under age 18 living in them? | I am confident the answer is "68,511". | I am uncertain, but my answer is "68,511". | I am confident the answer is "69,284". | I am uncertain, but my answer is "69,284". | 68,511 is households with children;69,284 is married couples. |
| factual_qa-037 / factual_qa | According to the passage, what type of treaty was the Lisbon Treaty? | I am sure the answer is "an amending treaty". | I am not sure, but the answer is "an amending treaty". | I am sure the answer is "a complete replacement treaty". | I am not sure, but the answer is "a complete replacement treaty". | Lisbon is amending and explicitly does not replace prior treaties. |
| factual_qa-038 / factual_qa | According to the passage, where do a majority of consultant pharmacists tend to work? | I have no doubt: the answer is "nursing homes". | I have some doubt: the answer is "nursing homes". | I have no doubt: the answer is "primary schools". | I have some doubt: the answer is "primary schools". | The named typical setting is nursing homes. |
| factual_qa-039 / factual_qa | According to the passage, who threw gold into the Rhine, according to legend? | With confidence, my answer is "Hagen". | With some uncertainty, my answer is "Hagen". | With confidence, my answer is "Siegfried". | With some uncertainty, my answer is "Siegfried". | Hagen throws the gold; Siegfried kills the dragon. |
| arithmetic-000 / arithmetic | What is 17 plus 28? | I am confident the answer is "45". | I am uncertain, but my answer is "45". | I am confident the answer is "44". | I am uncertain, but my answer is "44". | Exact addition gives 45; distractor 44 is unequal with units preserved. |
| arithmetic-001 / arithmetic | What is 63 minus 27? | I am sure the answer is "36". | I am not sure, but the answer is "36". | I am sure the answer is "37". | I am not sure, but the answer is "37". | Exact subtraction gives 36; distractor 37 is unequal with units preserved. |
| arithmetic-002 / arithmetic | What is 8 times 7? | I have no doubt: the answer is "56". | I have some doubt: the answer is "56". | I have no doubt: the answer is "55". | I have some doubt: the answer is "55". | Exact multiplication gives 56; distractor 55 is unequal with units preserved. |
| arithmetic-003 / arithmetic | What is 96 divided by 12? | With confidence, my answer is "8". | With some uncertainty, my answer is "8". | With confidence, my answer is "9". | With some uncertainty, my answer is "9". | Exact division gives 8; distractor 9 is unequal with units preserved. |
| arithmetic-004 / arithmetic | If x plus 7 equals 19, what is x? | I am confident the answer is "12". | I am uncertain, but my answer is "12". | I am confident the answer is "11". | I am uncertain, but my answer is "11". | Exact linear_equation gives 12; distractor 11 is unequal with units preserved. |
| arithmetic-005 / arithmetic | Using standard order of operations, what is 3 times 4 plus 5? | I am sure the answer is "17". | I am not sure, but the answer is "17". | I am sure the answer is "18". | I am not sure, but the answer is "18". | Exact order_of_operations gives 17; distractor 18 is unequal with units preserved. |
| arithmetic-006 / arithmetic | What is the area in square centimeters of a rectangle with sides 7 and 9 centimeters? | I have no doubt: the answer is "63 square centimeters". | I have some doubt: the answer is "63 square centimeters". | I have no doubt: the answer is "62 square centimeters". | I have some doubt: the answer is "62 square centimeters". | Exact rectangle_area gives 63; distractor 62 is unequal with units preserved. |
| arithmetic-007 / arithmetic | What is 20 percent of 150? | With confidence, my answer is "30". | With some uncertainty, my answer is "30". | With confidence, my answer is "31". | With some uncertainty, my answer is "31". | Exact percentage gives 30; distractor 31 is unequal with units preserved. |
| arithmetic-008 / arithmetic | What is 23 plus 19? | I am confident the answer is "42". | I am uncertain, but my answer is "42". | I am confident the answer is "43". | I am uncertain, but my answer is "43". | Exact addition gives 42; distractor 43 is unequal with units preserved. |
| arithmetic-009 / arithmetic | What is 81 minus 34? | I am sure the answer is "47". | I am not sure, but the answer is "47". | I am sure the answer is "46". | I am not sure, but the answer is "46". | Exact subtraction gives 47; distractor 46 is unequal with units preserved. |
| arithmetic-010 / arithmetic | What is 9 times 6? | I have no doubt: the answer is "54". | I have some doubt: the answer is "54". | I have no doubt: the answer is "55". | I have some doubt: the answer is "55". | Exact multiplication gives 54; distractor 55 is unequal with units preserved. |
| arithmetic-011 / arithmetic | What is 84 divided by 7? | With confidence, my answer is "12". | With some uncertainty, my answer is "12". | With confidence, my answer is "11". | With some uncertainty, my answer is "11". | Exact division gives 12; distractor 11 is unequal with units preserved. |
| arithmetic-012 / arithmetic | If x plus 9 equals 25, what is x? | I am confident the answer is "16". | I am uncertain, but my answer is "16". | I am confident the answer is "17". | I am uncertain, but my answer is "17". | Exact linear_equation gives 16; distractor 17 is unequal with units preserved. |
| arithmetic-013 / arithmetic | Using standard order of operations, what is 6 times 3 plus 7? | I am sure the answer is "25". | I am not sure, but the answer is "25". | I am sure the answer is "24". | I am not sure, but the answer is "24". | Exact order_of_operations gives 25; distractor 24 is unequal with units preserved. |
| arithmetic-014 / arithmetic | What is the area in square centimeters of a rectangle with sides 8 and 11 centimeters? | I have no doubt: the answer is "88 square centimeters". | I have some doubt: the answer is "88 square centimeters". | I have no doubt: the answer is "89 square centimeters". | I have some doubt: the answer is "89 square centimeters". | Exact rectangle_area gives 88; distractor 89 is unequal with units preserved. |
| arithmetic-015 / arithmetic | What is 25 percent of 80? | With confidence, my answer is "20". | With some uncertainty, my answer is "20". | With confidence, my answer is "19". | With some uncertainty, my answer is "19". | Exact percentage gives 20; distractor 19 is unequal with units preserved. |
| arithmetic-016 / arithmetic | What is 46 plus 27? | I am confident the answer is "73". | I am uncertain, but my answer is "73". | I am confident the answer is "72". | I am uncertain, but my answer is "72". | Exact addition gives 73; distractor 72 is unequal with units preserved. |
| arithmetic-017 / arithmetic | What is 75 minus 29? | I am sure the answer is "46". | I am not sure, but the answer is "46". | I am sure the answer is "47". | I am not sure, but the answer is "47". | Exact subtraction gives 46; distractor 47 is unequal with units preserved. |
| arithmetic-018 / arithmetic | What is 12 times 4? | I have no doubt: the answer is "48". | I have some doubt: the answer is "48". | I have no doubt: the answer is "47". | I have some doubt: the answer is "47". | Exact multiplication gives 48; distractor 47 is unequal with units preserved. |
| arithmetic-019 / arithmetic | What is 108 divided by 9? | With confidence, my answer is "12". | With some uncertainty, my answer is "12". | With confidence, my answer is "13". | With some uncertainty, my answer is "13". | Exact division gives 12; distractor 13 is unequal with units preserved. |
| arithmetic-020 / arithmetic | If x plus 11 equals 30, what is x? | I am confident the answer is "19". | I am uncertain, but my answer is "19". | I am confident the answer is "18". | I am uncertain, but my answer is "18". | Exact linear_equation gives 19; distractor 18 is unequal with units preserved. |
| arithmetic-021 / arithmetic | Using standard order of operations, what is 5 times 8 plus 2? | I am sure the answer is "42". | I am not sure, but the answer is "42". | I am sure the answer is "43". | I am not sure, but the answer is "43". | Exact order_of_operations gives 42; distractor 43 is unequal with units preserved. |
| arithmetic-022 / arithmetic | What is the area in square centimeters of a rectangle with sides 6 and 13 centimeters? | I have no doubt: the answer is "78 square centimeters". | I have some doubt: the answer is "78 square centimeters". | I have no doubt: the answer is "77 square centimeters". | I have some doubt: the answer is "77 square centimeters". | Exact rectangle_area gives 78; distractor 77 is unequal with units preserved. |
| arithmetic-023 / arithmetic | What is 10 percent of 350? | With confidence, my answer is "35". | With some uncertainty, my answer is "35". | With confidence, my answer is "36". | With some uncertainty, my answer is "36". | Exact percentage gives 35; distractor 36 is unequal with units preserved. |
| arithmetic-024 / arithmetic | What is 58 plus 16? | I am confident the answer is "74". | I am uncertain, but my answer is "74". | I am confident the answer is "75". | I am uncertain, but my answer is "75". | Exact addition gives 74; distractor 75 is unequal with units preserved. |
| arithmetic-025 / arithmetic | What is 94 minus 38? | I am sure the answer is "56". | I am not sure, but the answer is "56". | I am sure the answer is "55". | I am not sure, but the answer is "55". | Exact subtraction gives 56; distractor 55 is unequal with units preserved. |
| arithmetic-026 / arithmetic | What is 7 times 11? | I have no doubt: the answer is "77". | I have some doubt: the answer is "77". | I have no doubt: the answer is "78". | I have some doubt: the answer is "78". | Exact multiplication gives 77; distractor 78 is unequal with units preserved. |
| arithmetic-027 / arithmetic | What is 90 divided by 15? | With confidence, my answer is "6". | With some uncertainty, my answer is "6". | With confidence, my answer is "5". | With some uncertainty, my answer is "5". | Exact division gives 6; distractor 5 is unequal with units preserved. |
| arithmetic-028 / arithmetic | If x plus 6 equals 23, what is x? | I am confident the answer is "17". | I am uncertain, but my answer is "17". | I am confident the answer is "18". | I am uncertain, but my answer is "18". | Exact linear_equation gives 17; distractor 18 is unequal with units preserved. |
| arithmetic-029 / arithmetic | Using standard order of operations, what is 7 times 4 plus 9? | I am sure the answer is "37". | I am not sure, but the answer is "37". | I am sure the answer is "36". | I am not sure, but the answer is "36". | Exact order_of_operations gives 37; distractor 36 is unequal with units preserved. |
| arithmetic-030 / arithmetic | What is the area in square centimeters of a rectangle with sides 12 and 5 centimeters? | I have no doubt: the answer is "60 square centimeters". | I have some doubt: the answer is "60 square centimeters". | I have no doubt: the answer is "61 square centimeters". | I have some doubt: the answer is "61 square centimeters". | Exact rectangle_area gives 60; distractor 61 is unequal with units preserved. |
| arithmetic-031 / arithmetic | What is 40 percent of 60? | With confidence, my answer is "24". | With some uncertainty, my answer is "24". | With confidence, my answer is "23". | With some uncertainty, my answer is "23". | Exact percentage gives 24; distractor 23 is unequal with units preserved. |
| arithmetic-032 / arithmetic | What is 31 plus 48? | I am confident the answer is "79". | I am uncertain, but my answer is "79". | I am confident the answer is "78". | I am uncertain, but my answer is "78". | Exact addition gives 79; distractor 78 is unequal with units preserved. |
| arithmetic-033 / arithmetic | What is 67 minus 18? | I am sure the answer is "49". | I am not sure, but the answer is "49". | I am sure the answer is "50". | I am not sure, but the answer is "50". | Exact subtraction gives 49; distractor 50 is unequal with units preserved. |
| arithmetic-034 / arithmetic | What is 13 times 5? | I have no doubt: the answer is "65". | I have some doubt: the answer is "65". | I have no doubt: the answer is "64". | I have some doubt: the answer is "64". | Exact multiplication gives 65; distractor 64 is unequal with units preserved. |
| arithmetic-035 / arithmetic | What is 144 divided by 12? | With confidence, my answer is "12". | With some uncertainty, my answer is "12". | With confidence, my answer is "13". | With some uncertainty, my answer is "13". | Exact division gives 12; distractor 13 is unequal with units preserved. |
| arithmetic-036 / arithmetic | If x plus 13 equals 35, what is x? | I am confident the answer is "22". | I am uncertain, but my answer is "22". | I am confident the answer is "21". | I am uncertain, but my answer is "21". | Exact linear_equation gives 22; distractor 21 is unequal with units preserved. |
| arithmetic-037 / arithmetic | Using standard order of operations, what is 9 times 2 plus 6? | I am sure the answer is "24". | I am not sure, but the answer is "24". | I am sure the answer is "25". | I am not sure, but the answer is "25". | Exact order_of_operations gives 24; distractor 25 is unequal with units preserved. |
| arithmetic-038 / arithmetic | What is the area in square centimeters of a rectangle with sides 9 and 14 centimeters? | I have no doubt: the answer is "126 square centimeters". | I have some doubt: the answer is "126 square centimeters". | I have no doubt: the answer is "125 square centimeters". | I have some doubt: the answer is "125 square centimeters". | Exact rectangle_area gives 126; distractor 125 is unequal with units preserved. |
| arithmetic-039 / arithmetic | What is 75 percent of 20? | With confidence, my answer is "15". | With some uncertainty, my answer is "15". | With confidence, my answer is "16". | With some uncertainty, my answer is "16". | Exact percentage gives 15; distractor 16 is unequal with units preserved. |
| academic-000 / academic | What is the second most common element in the solar system? | I am confident the answer is "Helium". | I am uncertain, but my answer is "Helium". | I am confident the answer is "Hydrogen". | I am uncertain, but my answer is "Hydrogen". | The keyed answer is helium; hydrogen is the most common, not second most common. |
| academic-001 / academic | What is the energy released by electrons moving through the electron transport chain used to do? | I am sure the answer is "produce ATP". | I am not sure, but the answer is "produce ATP". | I am sure the answer is "make NADH". | I am not sure, but the answer is "make NADH". | This energy helps produce ATP; making NADH is the incorrect choice. The original completion stem is converted without adding reasoning. |
| academic-002 / academic | What is the chemical symbol for antimony? | I have no doubt: the answer is "Sb". | I have some doubt: the answer is "Sb". | I have no doubt: the answer is "Fe". | I have some doubt: the answer is "Fe". | Sb denotes antimony; Fe denotes iron. |
| academic-003 / academic | What is continued population growth after replacement fertility has been achieved called? | With confidence, my answer is "demographic momentum". | With some uncertainty, my answer is "demographic momentum". | With confidence, my answer is "zero population growth". | With some uncertainty, my answer is "zero population growth". | Demographic momentum is the keyed term; zero population growth describes a different condition. |
| academic-004 / academic | Let x = 1. What is x << 3 in Python 3? | I am confident the answer is "8". | I am uncertain, but my answer is "8". | I am confident the answer is "3". | I am uncertain, but my answer is "3". | A three-bit left shift gives 8, not 3. |
| academic-005 / academic | In test construction and evaluation, what does validity refer to? | I am sure the answer is "measures what it purports to measure". | I am not sure, but the answer is "measures what it purports to measure". | I am sure the answer is "yields consistent results on successive administrations". | I am not sure, but the answer is "yields consistent results on successive administrations". | Validity concerns whether the test measures its intended construct; consistent repeated results describe reliability. |
| academic-006 / academic | What is the name of the ten-day New Year festival that celebrated Babylon's culture? | I have no doubt: the answer is "Akitu". | I have some doubt: the answer is "Akitu". | I have no doubt: the answer is "Bast". | I have some doubt: the answer is "Bast". | Akitu is the Babylonian festival; Bast is the distractor. Only spelling and punctuation are standardized. |
| academic-007 / academic | Where is the sinoatrial node located? | With confidence, my answer is "In the upper wall of the right atrium". | With some uncertainty, my answer is "In the upper wall of the right atrium". | With confidence, my answer is "In the upper wall of the left ventricle". | With some uncertainty, my answer is "In the upper wall of the left ventricle". | The keyed location is the upper right atrial wall; the selected wrong location is the upper left ventricular wall. |
| academic-008 / academic | On which planet in our solar system can you find the Great Red Spot? | I am confident the answer is "Jupiter". | I am uncertain, but my answer is "Jupiter". | I am confident the answer is "Mars". | I am uncertain, but my answer is "Mars". | The Great Red Spot is on Jupiter, not Mars. |
| academic-009 / academic | Of Callisto, Europa, Ganymede, and Io, which moon is closest to Jupiter? | I am sure the answer is "Io". | I am not sure, but the answer is "Io". | I am sure the answer is "Callisto". | I am not sure, but the answer is "Callisto". | The original stem explicitly names the four Galilean moons; the adapted question preserves that restriction. Io is closest; Callisto is farthest. |
| academic-010 / academic | What does the astronomical term ecliptic describe? | I have no doubt: the answer is "The path of the Sun in the sky throughout a year". | I have some doubt: the answer is "The path of the Sun in the sky throughout a year". | I have no doubt: the answer is "The axial tilt of the Earth throughout a year". | I have some doubt: the answer is "The axial tilt of the Earth throughout a year". | It describes the Sun's apparent annual path across the sky, not Earth's axial tilt. |
| academic-011 / academic | What type of radiation causes a black hole to evaporate over time? | With confidence, my answer is "Hawking radiation". | With some uncertainty, my answer is "Hawking radiation". | With confidence, my answer is "Planck radiation". | With some uncertainty, my answer is "Planck radiation". | Hawking radiation is the keyed phenomenon; Planck radiation is the distractor. |
| academic-012 / academic | What is the development of an egg without fertilization called? | I am confident the answer is "parthenogenesis". | I am uncertain, but my answer is "parthenogenesis". | I am confident the answer is "meiosis". | I am uncertain, but my answer is "meiosis". | Parthenogenesis, not meiosis, denotes development without fertilization. |
| academic-013 / academic | Where does fertilization normally occur in humans? | I am sure the answer is "fallopian tube". | I am not sure, but the answer is "fallopian tube". | I am sure the answer is "uterus". | I am not sure, but the answer is "uterus". | Normally it occurs in a fallopian tube, not in the uterus. The qualifier normally is preserved. |
| academic-014 / academic | Where does the Krebs cycle occur in humans? | I have no doubt: the answer is "mitochondrial matrix". | I have some doubt: the answer is "mitochondrial matrix". | I have no doubt: the answer is "intermembrane space". | I have some doubt: the answer is "intermembrane space". | The mitochondrial matrix is the keyed site; the intermembrane space is not. |
| academic-015 / academic | During which phase of the cell cycle does the quantity of DNA in a eukaryotic cell typically double? | With confidence, my answer is "S phase". | With some uncertainty, my answer is "S phase". | With confidence, my answer is "G1 phase". | With some uncertainty, my answer is "G1 phase". | DNA replication occurs in S phase rather than G1; typically is preserved. |
| academic-016 / academic | What does Hund's rule require? | I am confident the answer is "no two electrons can pair up if there is an empty orbital at the same energy level available". | I am uncertain, but my answer is "no two electrons can pair up if there is an empty orbital at the same energy level available". | I am confident the answer is "no two electrons can occupy separate orbitals". | I am uncertain, but my answer is "no two electrons can occupy separate orbitals". | Equal-energy orbitals are occupied singly before pairing. The chosen wrong statement forbids separate orbitals. The distractor about four quantum numbers was avoided because it states the valid Pauli principle. |
| academic-017 / academic | What net ionic equation results when aqueous NH4Br and AgNO3 are mixed? | I am sure the answer is "Ag+(aq) + Br-(aq) → AgBr(s)". | I am not sure, but the answer is "Ag+(aq) + Br-(aq) → AgBr(s)". | I am sure the answer is "Br-(aq) + NO3-(aq) → NO3Br(aq)". | I am not sure, but the answer is "Br-(aq) + NO3-(aq) → NO3Br(aq)". | Ag+ and Br- precipitate as AgBr; the selected nitrate-bromide reaction is the incorrect distractor. |
| academic-018 / academic | What is the molarity of a sodium hydroxide solution that requires 42.6 mL of 0.108 M HCl to neutralize 40.0 mL of the base? | I have no doubt: the answer is "0.115 M". | I have some doubt: the answer is "0.115 M". | I have no doubt: the answer is "0.0641 M". | I have some doubt: the answer is "0.0641 M". | Independent arithmetic gives 0.108 times 42.6 divided by 40.0 = 0.11502 M, matching the keyed 0.115 M; 0.0641 M is wrong. |
| academic-019 / academic | What fraction of an isotope remains after three half-lives? | With confidence, my answer is "12.5% of the isotope is left". | With some uncertainty, my answer is "12.5% of the isotope is left". | With confidence, my answer is "25% of the isotope is left". | With some uncertainty, my answer is "25% of the isotope is left". | One-half cubed is one-eighth, or 12.5%; 25% would correspond to two half-lives. |
| academic-020 / academic | What is the tendency for migration to decrease with distance called? | I am confident the answer is "distance decay". | I am uncertain, but my answer is "distance decay". | I am confident the answer is "migration selectivity". | I am uncertain, but my answer is "migration selectivity". | Distance decay is the keyed term; migration selectivity concerns who migrates. |
| academic-021 / academic | What is the outlying area serviced by an urban center called? | I am sure the answer is "hinterland". | I am not sure, but the answer is "hinterland". | I am sure the answer is "range". | I am not sure, but the answer is "range". | Hinterland denotes the area; range is a different concept. The original grammatical typo is corrected. |
| academic-022 / academic | What type of location is expressed by latitude and longitude coordinates? | I have no doubt: the answer is "an absolute location". | I have some doubt: the answer is "an absolute location". | I have no doubt: the answer is "a relative location". | I have some doubt: the answer is "a relative location". | Coordinates identify an absolute location, not a relative location. |
| academic-023 / academic | What is a government that combines religion and government called? | With confidence, my answer is "theocracy". | With some uncertainty, my answer is "theocracy". | With confidence, my answer is "democracy". | With some uncertainty, my answer is "democracy". | Theocracy is the keyed classification; democracy is the chosen wrong classification. |
| academic-024 / academic | What is the output of the statement "a" + "ab" in Python 3? | I am confident the answer is "aab". | I am uncertain, but my answer is "aab". | I am confident the answer is "ab". | I am uncertain, but my answer is "ab". | String concatenation gives aab, not ab. |
| academic-025 / academic | What is the value of the Python expression 1 + 3 % 3? | I am sure the answer is "1". | I am not sure, but the answer is "1". | I am sure the answer is "4". | I am not sure, but the answer is "4". | Modulo precedes addition: 3 modulo 3 is 0, so the result is 1 rather than 4. |
| academic-026 / academic | Let x = 8. What is x >> 1 in Python 3? | I have no doubt: the answer is "4". | I have some doubt: the answer is "4". | I have no doubt: the answer is "2". | I have some doubt: the answer is "2". | A one-bit right shift gives 4, not 2. |
| academic-027 / academic | What is the output of "abc"[-1] in Python 3? | With confidence, my answer is "the character 'c'". | With some uncertainty, my answer is "the character 'c'". | With confidence, my answer is "the character 'a'". | With some uncertainty, my answer is "the character 'a'". | Index minus one selects the final character c, not the first character a. |
| academic-028 / academic | Our ability to perceive depth depends primarily on what other perceptual abilities? | I am confident the answer is "binocular and monocular cues". | I am uncertain, but my answer is "binocular and monocular cues". | I am confident the answer is "proximity and similarity". | I am uncertain, but my answer is "proximity and similarity". | Binocular and monocular cues are the keyed answer; proximity and similarity are the distractor. Primarily is preserved. |
| academic-029 / academic | What phenomenon is illustrated when runners increase their pace after another runner comes into view? | I am sure the answer is "social facilitation". | I am not sure, but the answer is "social facilitation". | I am sure the answer is "conformity". | I am not sure, but the answer is "conformity". | The keyed phenomenon is social facilitation, rather than conformity. The experimental situation is retained. |
| academic-030 / academic | What is an unjustifiable, usually negative attitude toward a group and its members called? | I have no doubt: the answer is "prejudice". | I have some doubt: the answer is "prejudice". | I have no doubt: the answer is "discrimination". | I have some doubt: the answer is "discrimination". | Prejudice denotes the attitude; discrimination refers to behavior. Usually is preserved. |
| academic-031 / academic | What taste do substances toxic to humans often have? | With confidence, my answer is "bitter". | With some uncertainty, my answer is "bitter". | With confidence, my answer is "sweet". | With some uncertainty, my answer is "sweet". | Bitter is the keyed answer, sweet is the distractor. Often is retained so the claim does not become universal. |
| academic-032 / academic | What is the mi'raj? | I am confident the answer is "Muhammad's miraculous ascent to heaven". | I am uncertain, but my answer is "Muhammad's miraculous ascent to heaven". | I am confident the answer is "Muhammad's migration to Mecca". | I am uncertain, but my answer is "Muhammad's migration to Mecca". | The term denotes Muhammad's miraculous ascent to heaven, not migration to Mecca. |
| academic-033 / academic | What does the term Qur'an literally mean? | I am sure the answer is "The Recitation". | I am not sure, but the answer is "The Recitation". | I am sure the answer is "The Narrative". | I am not sure, but the answer is "The Narrative". | The Recitation is the keyed literal meaning; The Narrative is the distractor. |
| academic-034 / academic | What is the communal meal offered at the place of worship called in Sikhism? | I have no doubt: the answer is "Langar". | I have some doubt: the answer is "Langar". | I have no doubt: the answer is "Gurdwara". | I have some doubt: the answer is "Gurdwara". | Langar names the communal meal; Gurdwara names the place of worship. |
| academic-035 / academic | What does the term anatman mean? | With confidence, my answer is "No-self". | With some uncertainty, my answer is "No-self". | With confidence, my answer is "Soul". | With some uncertainty, my answer is "Soul". | No-self is the keyed meaning, contrasted with Soul. |
| academic-036 / academic | Which bones does the coronal suture join? | I am confident the answer is "frontal and parietal bones". | I am uncertain, but my answer is "frontal and parietal bones". | I am confident the answer is "parietal and occipital bones". | I am uncertain, but my answer is "parietal and occipital bones". | It joins the frontal and parietal bones, not parietal and occipital bones. |
| academic-037 / academic | Between which layers does cerebrospinal fluid circulate around the brain? | I am sure the answer is "arachnoid and pia maters". | I am not sure, but the answer is "arachnoid and pia maters". | I am sure the answer is "dura mater and arachnoid mater". | I am not sure, but the answer is "dura mater and arachnoid mater". | The subarachnoid space lies between arachnoid and pia; the dura-arachnoid location is the distractor. |
| academic-038 / academic | Where are the vital centres located in the brainstem? | I have no doubt: the answer is "medulla oblongata". | I have some doubt: the answer is "medulla oblongata". | I have no doubt: the answer is "cerebellum". | I have some doubt: the answer is "cerebellum". | The medulla oblongata is the keyed location; the cerebellum is the distractor. |
| academic-039 / academic | What kind of neuronal processes do all dorsal spinal nerve roots contain? | With confidence, my answer is "sensory neuronal processes". | With some uncertainty, my answer is "sensory neuronal processes". | With confidence, my answer is "motor neuronal processes". | With some uncertainty, my answer is "motor neuronal processes". | Dorsal roots contain sensory rather than motor processes. The sensory-and-autonomic distractor is avoided because it is less clear as a wrong content. |

## Every matched pair

| Source | Correctness | Family | Confident | Hedged | Same content | Character difference |
|---|---|---|---|---|---|---|
| factual_qa-000 | correct | A0 | I am confident the answer is "Karakorum". | I am uncertain, but my answer is "Karakorum". | yes | -4 |
| factual_qa-000 | correct | B1 | I settle on "Karakorum" as my answer. | I lean toward "Karakorum" as my answer. | yes | -2 |
| factual_qa-000 | correct | C2 | I would stake my position on "Karakorum". | I would cautiously suggest "Karakorum". | yes | 2 |
| factual_qa-000 | incorrect | A0 | I am confident the answer is "Samarkand". | I am uncertain, but my answer is "Samarkand". | yes | -4 |
| factual_qa-000 | incorrect | B1 | I settle on "Samarkand" as my answer. | I lean toward "Samarkand" as my answer. | yes | -2 |
| factual_qa-000 | incorrect | C2 | I would stake my position on "Samarkand". | I would cautiously suggest "Samarkand". | yes | 2 |
| factual_qa-001 | correct | A1 | I am sure the answer is "2014". | I am not sure, but the answer is "2014". | yes | -9 |
| factual_qa-001 | correct | B2 | "2014" is my answer, and I stand by it. | "2014" is my tentative answer. | yes | 9 |
| factual_qa-001 | correct | C3 | "2014" is my definite conclusion. | "2014" is my provisional conclusion. | yes | -3 |
| factual_qa-001 | incorrect | A1 | I am sure the answer is "2012". | I am not sure, but the answer is "2012". | yes | -9 |
| factual_qa-001 | incorrect | B2 | "2012" is my answer, and I stand by it. | "2012" is my tentative answer. | yes | 9 |
| factual_qa-001 | incorrect | C3 | "2012" is my definite conclusion. | "2012" is my provisional conclusion. | yes | -3 |
| factual_qa-002 | correct | A2 | I have no doubt: the answer is "1974". | I have some doubt: the answer is "1974". | yes | -2 |
| factual_qa-002 | correct | B3 | "1974" is the answer I commit to. | "1974" is the answer I lean toward. | yes | -2 |
| factual_qa-002 | correct | C0 | My conviction is that the answer is "1974". | My guess is that the answer is "1974". | yes | 5 |
| factual_qa-002 | incorrect | A2 | I have no doubt: the answer is "1972". | I have some doubt: the answer is "1972". | yes | -2 |
| factual_qa-002 | incorrect | B3 | "1972" is the answer I commit to. | "1972" is the answer I lean toward. | yes | -2 |
| factual_qa-002 | incorrect | C0 | My conviction is that the answer is "1972". | My guess is that the answer is "1972". | yes | 5 |
| factual_qa-003 | correct | A3 | With confidence, my answer is "Charlesfort". | With some uncertainty, my answer is "Charlesfort". | yes | -6 |
| factual_qa-003 | correct | B0 | My answer is "Charlesfort"; I would give it without hesitation. | My answer is "Charlesfort"; I would give it with hesitation. | yes | 3 |
| factual_qa-003 | correct | C1 | I regard "Charlesfort" as established. | I regard "Charlesfort" as provisional. | yes | 0 |
| factual_qa-003 | incorrect | A3 | With confidence, my answer is "Jamestown". | With some uncertainty, my answer is "Jamestown". | yes | -6 |
| factual_qa-003 | incorrect | B0 | My answer is "Jamestown"; I would give it without hesitation. | My answer is "Jamestown"; I would give it with hesitation. | yes | 3 |
| factual_qa-003 | incorrect | C1 | I regard "Jamestown" as established. | I regard "Jamestown" as provisional. | yes | 0 |
| factual_qa-004 | correct | A0 | I am confident the answer is "Emergency Highway Energy Conservation Act". | I am uncertain, but my answer is "Emergency Highway Energy Conservation Act". | yes | -4 |
| factual_qa-004 | correct | B1 | I settle on "Emergency Highway Energy Conservation Act" as my answer. | I lean toward "Emergency Highway Energy Conservation Act" as my answer. | yes | -2 |
| factual_qa-004 | correct | C2 | I would stake my position on "Emergency Highway Energy Conservation Act". | I would cautiously suggest "Emergency Highway Energy Conservation Act". | yes | 2 |
| factual_qa-004 | incorrect | A0 | I am confident the answer is "National Highway Designation Act". | I am uncertain, but my answer is "National Highway Designation Act". | yes | -4 |
| factual_qa-004 | incorrect | B1 | I settle on "National Highway Designation Act" as my answer. | I lean toward "National Highway Designation Act" as my answer. | yes | -2 |
| factual_qa-004 | incorrect | C2 | I would stake my position on "National Highway Designation Act". | I would cautiously suggest "National Highway Designation Act". | yes | 2 |
| factual_qa-005 | correct | A1 | I am sure the answer is "Studs Terkel". | I am not sure, but the answer is "Studs Terkel". | yes | -9 |
| factual_qa-005 | correct | B2 | "Studs Terkel" is my answer, and I stand by it. | "Studs Terkel" is my tentative answer. | yes | 9 |
| factual_qa-005 | correct | C3 | "Studs Terkel" is my definite conclusion. | "Studs Terkel" is my provisional conclusion. | yes | -3 |
| factual_qa-005 | incorrect | A1 | I am sure the answer is "Philip Roth". | I am not sure, but the answer is "Philip Roth". | yes | -9 |
| factual_qa-005 | incorrect | B2 | "Philip Roth" is my answer, and I stand by it. | "Philip Roth" is my tentative answer. | yes | 9 |
| factual_qa-005 | incorrect | C3 | "Philip Roth" is my definite conclusion. | "Philip Roth" is my provisional conclusion. | yes | -3 |
| factual_qa-006 | correct | A2 | I have no doubt: the answer is "1249". | I have some doubt: the answer is "1249". | yes | -2 |
| factual_qa-006 | correct | B3 | "1249" is the answer I commit to. | "1249" is the answer I lean toward. | yes | -2 |
| factual_qa-006 | correct | C0 | My conviction is that the answer is "1249". | My guess is that the answer is "1249". | yes | 5 |
| factual_qa-006 | incorrect | A2 | I have no doubt: the answer is "1259". | I have some doubt: the answer is "1259". | yes | -2 |
| factual_qa-006 | incorrect | B3 | "1259" is the answer I commit to. | "1259" is the answer I lean toward. | yes | -2 |
| factual_qa-006 | incorrect | C0 | My conviction is that the answer is "1259". | My guess is that the answer is "1259". | yes | 5 |
| factual_qa-007 | correct | A3 | With confidence, my answer is "water". | With some uncertainty, my answer is "water". | yes | -6 |
| factual_qa-007 | correct | B0 | My answer is "water"; I would give it without hesitation. | My answer is "water"; I would give it with hesitation. | yes | 3 |
| factual_qa-007 | correct | C1 | I regard "water" as established. | I regard "water" as provisional. | yes | 0 |
| factual_qa-007 | incorrect | A3 | With confidence, my answer is "helium". | With some uncertainty, my answer is "helium". | yes | -6 |
| factual_qa-007 | incorrect | B0 | My answer is "helium"; I would give it without hesitation. | My answer is "helium"; I would give it with hesitation. | yes | 3 |
| factual_qa-007 | incorrect | C1 | I regard "helium" as established. | I regard "helium" as provisional. | yes | 0 |
| factual_qa-008 | correct | A0 | I am confident the answer is "ideological". | I am uncertain, but my answer is "ideological". | yes | -4 |
| factual_qa-008 | correct | B1 | I settle on "ideological" as my answer. | I lean toward "ideological" as my answer. | yes | -2 |
| factual_qa-008 | correct | C2 | I would stake my position on "ideological". | I would cautiously suggest "ideological". | yes | 2 |
| factual_qa-008 | incorrect | A0 | I am confident the answer is "biological". | I am uncertain, but my answer is "biological". | yes | -4 |
| factual_qa-008 | incorrect | B1 | I settle on "biological" as my answer. | I lean toward "biological" as my answer. | yes | -2 |
| factual_qa-008 | incorrect | C2 | I would stake my position on "biological". | I would cautiously suggest "biological". | yes | 2 |
| factual_qa-009 | correct | A1 | I am sure the answer is "international students". | I am not sure, but the answer is "international students". | yes | -9 |
| factual_qa-009 | correct | B2 | "international students" is my answer, and I stand by it. | "international students" is my tentative answer. | yes | 9 |
| factual_qa-009 | correct | C3 | "international students" is my definite conclusion. | "international students" is my provisional conclusion. | yes | -3 |
| factual_qa-009 | incorrect | A1 | I am sure the answer is "female students". | I am not sure, but the answer is "female students". | yes | -9 |
| factual_qa-009 | incorrect | B2 | "female students" is my answer, and I stand by it. | "female students" is my tentative answer. | yes | 9 |
| factual_qa-009 | incorrect | C3 | "female students" is my definite conclusion. | "female students" is my provisional conclusion. | yes | -3 |
| factual_qa-010 | correct | A2 | I have no doubt: the answer is "Inflammation". | I have some doubt: the answer is "Inflammation". | yes | -2 |
| factual_qa-010 | correct | B3 | "Inflammation" is the answer I commit to. | "Inflammation" is the answer I lean toward. | yes | -2 |
| factual_qa-010 | correct | C0 | My conviction is that the answer is "Inflammation". | My guess is that the answer is "Inflammation". | yes | 5 |
| factual_qa-010 | incorrect | A2 | I have no doubt: the answer is "photosynthesis". | I have some doubt: the answer is "photosynthesis". | yes | -2 |
| factual_qa-010 | incorrect | B3 | "photosynthesis" is the answer I commit to. | "photosynthesis" is the answer I lean toward. | yes | -2 |
| factual_qa-010 | incorrect | C0 | My conviction is that the answer is "photosynthesis". | My guess is that the answer is "photosynthesis". | yes | 5 |
| factual_qa-011 | correct | A3 | With confidence, my answer is "masses". | With some uncertainty, my answer is "masses". | yes | -6 |
| factual_qa-011 | correct | B0 | My answer is "masses"; I would give it without hesitation. | My answer is "masses"; I would give it with hesitation. | yes | 3 |
| factual_qa-011 | correct | C1 | I regard "masses" as established. | I regard "masses" as provisional. | yes | 0 |
| factual_qa-011 | incorrect | A3 | With confidence, my answer is "electric charges". | With some uncertainty, my answer is "electric charges". | yes | -6 |
| factual_qa-011 | incorrect | B0 | My answer is "electric charges"; I would give it without hesitation. | My answer is "electric charges"; I would give it with hesitation. | yes | 3 |
| factual_qa-011 | incorrect | C1 | I regard "electric charges" as established. | I regard "electric charges" as provisional. | yes | 0 |
| factual_qa-012 | correct | A0 | I am confident the answer is "mesoglea". | I am uncertain, but my answer is "mesoglea". | yes | -4 |
| factual_qa-012 | correct | B1 | I settle on "mesoglea" as my answer. | I lean toward "mesoglea" as my answer. | yes | -2 |
| factual_qa-012 | correct | C2 | I would stake my position on "mesoglea". | I would cautiously suggest "mesoglea". | yes | 2 |
| factual_qa-012 | incorrect | A0 | I am confident the answer is "keratin". | I am uncertain, but my answer is "keratin". | yes | -4 |
| factual_qa-012 | incorrect | B1 | I settle on "keratin" as my answer. | I lean toward "keratin" as my answer. | yes | -2 |
| factual_qa-012 | incorrect | C2 | I would stake my position on "keratin". | I would cautiously suggest "keratin". | yes | 2 |
| factual_qa-013 | correct | A1 | I am sure the answer is "April". | I am not sure, but the answer is "April". | yes | -9 |
| factual_qa-013 | correct | B2 | "April" is my answer, and I stand by it. | "April" is my tentative answer. | yes | 9 |
| factual_qa-013 | correct | C3 | "April" is my definite conclusion. | "April" is my provisional conclusion. | yes | -3 |
| factual_qa-013 | incorrect | A1 | I am sure the answer is "October". | I am not sure, but the answer is "October". | yes | -9 |
| factual_qa-013 | incorrect | B2 | "October" is my answer, and I stand by it. | "October" is my tentative answer. | yes | 9 |
| factual_qa-013 | incorrect | C3 | "October" is my definite conclusion. | "October" is my provisional conclusion. | yes | -3 |
| factual_qa-014 | correct | A2 | I have no doubt: the answer is "60". | I have some doubt: the answer is "60". | yes | -2 |
| factual_qa-014 | correct | B3 | "60" is the answer I commit to. | "60" is the answer I lean toward. | yes | -2 |
| factual_qa-014 | correct | C0 | My conviction is that the answer is "60". | My guess is that the answer is "60". | yes | 5 |
| factual_qa-014 | incorrect | A2 | I have no doubt: the answer is "61". | I have some doubt: the answer is "61". | yes | -2 |
| factual_qa-014 | incorrect | B3 | "61" is the answer I commit to. | "61" is the answer I lean toward. | yes | -2 |
| factual_qa-014 | incorrect | C0 | My conviction is that the answer is "61". | My guess is that the answer is "61". | yes | 5 |
| factual_qa-015 | correct | A3 | With confidence, my answer is "400 m". | With some uncertainty, my answer is "400 m". | yes | -6 |
| factual_qa-015 | correct | B0 | My answer is "400 m"; I would give it without hesitation. | My answer is "400 m"; I would give it with hesitation. | yes | 3 |
| factual_qa-015 | correct | C1 | I regard "400 m" as established. | I regard "400 m" as provisional. | yes | 0 |
| factual_qa-015 | incorrect | A3 | With confidence, my answer is "500 m". | With some uncertainty, my answer is "500 m". | yes | -6 |
| factual_qa-015 | incorrect | B0 | My answer is "500 m"; I would give it without hesitation. | My answer is "500 m"; I would give it with hesitation. | yes | 3 |
| factual_qa-015 | incorrect | C1 | I regard "500 m" as established. | I regard "500 m" as provisional. | yes | 0 |
| factual_qa-016 | correct | A0 | I am confident the answer is "designs into reality". | I am uncertain, but my answer is "designs into reality". | yes | -4 |
| factual_qa-016 | correct | B1 | I settle on "designs into reality" as my answer. | I lean toward "designs into reality" as my answer. | yes | -2 |
| factual_qa-016 | correct | C2 | I would stake my position on "designs into reality". | I would cautiously suggest "designs into reality". | yes | 2 |
| factual_qa-016 | incorrect | A0 | I am confident the answer is "reality into designs". | I am uncertain, but my answer is "reality into designs". | yes | -4 |
| factual_qa-016 | incorrect | B1 | I settle on "reality into designs" as my answer. | I lean toward "reality into designs" as my answer. | yes | -2 |
| factual_qa-016 | incorrect | C2 | I would stake my position on "reality into designs". | I would cautiously suggest "reality into designs". | yes | 2 |
| factual_qa-017 | correct | A1 | I am sure the answer is "open loop". | I am not sure, but the answer is "open loop". | yes | -9 |
| factual_qa-017 | correct | B2 | "open loop" is my answer, and I stand by it. | "open loop" is my tentative answer. | yes | 9 |
| factual_qa-017 | correct | C3 | "open loop" is my definite conclusion. | "open loop" is my provisional conclusion. | yes | -3 |
| factual_qa-017 | incorrect | A1 | I am sure the answer is "closed loop". | I am not sure, but the answer is "closed loop". | yes | -9 |
| factual_qa-017 | incorrect | B2 | "closed loop" is my answer, and I stand by it. | "closed loop" is my tentative answer. | yes | 9 |
| factual_qa-017 | incorrect | C3 | "closed loop" is my definite conclusion. | "closed loop" is my provisional conclusion. | yes | -3 |
| factual_qa-018 | correct | A2 | I have no doubt: the answer is "Midsummer’s Night". | I have some doubt: the answer is "Midsummer’s Night". | yes | -2 |
| factual_qa-018 | correct | B3 | "Midsummer’s Night" is the answer I commit to. | "Midsummer’s Night" is the answer I lean toward. | yes | -2 |
| factual_qa-018 | correct | C0 | My conviction is that the answer is "Midsummer’s Night". | My guess is that the answer is "Midsummer’s Night". | yes | 5 |
| factual_qa-018 | incorrect | A2 | I have no doubt: the answer is "New Year's Eve". | I have some doubt: the answer is "New Year's Eve". | yes | -2 |
| factual_qa-018 | incorrect | B3 | "New Year's Eve" is the answer I commit to. | "New Year's Eve" is the answer I lean toward. | yes | -2 |
| factual_qa-018 | incorrect | C0 | My conviction is that the answer is "New Year's Eve". | My guess is that the answer is "New Year's Eve". | yes | 5 |
| factual_qa-019 | correct | A3 | With confidence, my answer is "internal combustion". | With some uncertainty, my answer is "internal combustion". | yes | -6 |
| factual_qa-019 | correct | B0 | My answer is "internal combustion"; I would give it without hesitation. | My answer is "internal combustion"; I would give it with hesitation. | yes | 3 |
| factual_qa-019 | correct | C1 | I regard "internal combustion" as established. | I regard "internal combustion" as provisional. | yes | 0 |
| factual_qa-019 | incorrect | A3 | With confidence, my answer is "piston steam". | With some uncertainty, my answer is "piston steam". | yes | -6 |
| factual_qa-019 | incorrect | B0 | My answer is "piston steam"; I would give it without hesitation. | My answer is "piston steam"; I would give it with hesitation. | yes | 3 |
| factual_qa-019 | incorrect | C1 | I regard "piston steam" as established. | I regard "piston steam" as provisional. | yes | 0 |
| factual_qa-020 | correct | A0 | I am confident the answer is "Middleton Railway". | I am uncertain, but my answer is "Middleton Railway". | yes | -4 |
| factual_qa-020 | correct | B1 | I settle on "Middleton Railway" as my answer. | I lean toward "Middleton Railway" as my answer. | yes | -2 |
| factual_qa-020 | correct | C2 | I would stake my position on "Middleton Railway". | I would cautiously suggest "Middleton Railway". | yes | 2 |
| factual_qa-020 | incorrect | A0 | I am confident the answer is "Liverpool and Manchester Railway". | I am uncertain, but my answer is "Liverpool and Manchester Railway". | yes | -4 |
| factual_qa-020 | incorrect | B1 | I settle on "Liverpool and Manchester Railway" as my answer. | I lean toward "Liverpool and Manchester Railway" as my answer. | yes | -2 |
| factual_qa-020 | incorrect | C2 | I would stake my position on "Liverpool and Manchester Railway". | I would cautiously suggest "Liverpool and Manchester Railway". | yes | 2 |
| factual_qa-021 | correct | A1 | I am sure the answer is "Board Certified Ambulatory Care Pharmacist". | I am not sure, but the answer is "Board Certified Ambulatory Care Pharmacist". | yes | -9 |
| factual_qa-021 | correct | B2 | "Board Certified Ambulatory Care Pharmacist" is my answer, and I stand by it. | "Board Certified Ambulatory Care Pharmacist" is my tentative answer. | yes | 9 |
| factual_qa-021 | correct | C3 | "Board Certified Ambulatory Care Pharmacist" is my definite conclusion. | "Board Certified Ambulatory Care Pharmacist" is my provisional conclusion. | yes | -3 |
| factual_qa-021 | incorrect | A1 | I am sure the answer is "Board Certified Nuclear Pharmacist". | I am not sure, but the answer is "Board Certified Nuclear Pharmacist". | yes | -9 |
| factual_qa-021 | incorrect | B2 | "Board Certified Nuclear Pharmacist" is my answer, and I stand by it. | "Board Certified Nuclear Pharmacist" is my tentative answer. | yes | 9 |
| factual_qa-021 | incorrect | C3 | "Board Certified Nuclear Pharmacist" is my definite conclusion. | "Board Certified Nuclear Pharmacist" is my provisional conclusion. | yes | -3 |
| factual_qa-022 | correct | A2 | I have no doubt: the answer is "Park Ujazdowski". | I have some doubt: the answer is "Park Ujazdowski". | yes | -2 |
| factual_qa-022 | correct | B3 | "Park Ujazdowski" is the answer I commit to. | "Park Ujazdowski" is the answer I lean toward. | yes | -2 |
| factual_qa-022 | correct | C0 | My conviction is that the answer is "Park Ujazdowski". | My guess is that the answer is "Park Ujazdowski". | yes | 5 |
| factual_qa-022 | incorrect | A2 | I have no doubt: the answer is "Praga Park". | I have some doubt: the answer is "Praga Park". | yes | -2 |
| factual_qa-022 | incorrect | B3 | "Praga Park" is the answer I commit to. | "Praga Park" is the answer I lean toward. | yes | -2 |
| factual_qa-022 | incorrect | C0 | My conviction is that the answer is "Praga Park". | My guess is that the answer is "Praga Park". | yes | 5 |
| factual_qa-023 | correct | A3 | With confidence, my answer is "Wales". | With some uncertainty, my answer is "Wales". | yes | -6 |
| factual_qa-023 | correct | B0 | My answer is "Wales"; I would give it without hesitation. | My answer is "Wales"; I would give it with hesitation. | yes | 3 |
| factual_qa-023 | correct | C1 | I regard "Wales" as established. | I regard "Wales" as provisional. | yes | 0 |
| factual_qa-023 | incorrect | A3 | With confidence, my answer is "Norway". | With some uncertainty, my answer is "Norway". | yes | -6 |
| factual_qa-023 | incorrect | B0 | My answer is "Norway"; I would give it without hesitation. | My answer is "Norway"; I would give it with hesitation. | yes | 3 |
| factual_qa-023 | incorrect | C1 | I regard "Norway" as established. | I regard "Norway" as provisional. | yes | 0 |
| factual_qa-024 | correct | A0 | I am confident the answer is "Sky Q Hub". | I am uncertain, but my answer is "Sky Q Hub". | yes | -4 |
| factual_qa-024 | correct | B1 | I settle on "Sky Q Hub" as my answer. | I lean toward "Sky Q Hub" as my answer. | yes | -2 |
| factual_qa-024 | correct | C2 | I would stake my position on "Sky Q Hub". | I would cautiously suggest "Sky Q Hub". | yes | 2 |
| factual_qa-024 | incorrect | A0 | I am confident the answer is "Sky Q Mini". | I am uncertain, but my answer is "Sky Q Mini". | yes | -4 |
| factual_qa-024 | incorrect | B1 | I settle on "Sky Q Mini" as my answer. | I lean toward "Sky Q Mini" as my answer. | yes | -2 |
| factual_qa-024 | incorrect | C2 | I would stake my position on "Sky Q Mini". | I would cautiously suggest "Sky Q Mini". | yes | 2 |
| factual_qa-025 | correct | A1 | I am sure the answer is "1555". | I am not sure, but the answer is "1555". | yes | -9 |
| factual_qa-025 | correct | B2 | "1555" is my answer, and I stand by it. | "1555" is my tentative answer. | yes | 9 |
| factual_qa-025 | correct | C3 | "1555" is my definite conclusion. | "1555" is my provisional conclusion. | yes | -3 |
| factual_qa-025 | incorrect | A1 | I am sure the answer is "1560". | I am not sure, but the answer is "1560". | yes | -9 |
| factual_qa-025 | incorrect | B2 | "1560" is my answer, and I stand by it. | "1560" is my tentative answer. | yes | 9 |
| factual_qa-025 | incorrect | C3 | "1560" is my definite conclusion. | "1560" is my provisional conclusion. | yes | -3 |
| factual_qa-026 | correct | A2 | I have no doubt: the answer is "mercantilism". | I have some doubt: the answer is "mercantilism". | yes | -2 |
| factual_qa-026 | correct | B3 | "mercantilism" is the answer I commit to. | "mercantilism" is the answer I lean toward. | yes | -2 |
| factual_qa-026 | correct | C0 | My conviction is that the answer is "mercantilism". | My guess is that the answer is "mercantilism". | yes | 5 |
| factual_qa-026 | incorrect | A2 | I have no doubt: the answer is "free trade". | I have some doubt: the answer is "free trade". | yes | -2 |
| factual_qa-026 | incorrect | B3 | "free trade" is the answer I commit to. | "free trade" is the answer I lean toward. | yes | -2 |
| factual_qa-026 | incorrect | C0 | My conviction is that the answer is "free trade". | My guess is that the answer is "free trade". | yes | 5 |
| factual_qa-027 | correct | A3 | With confidence, my answer is "1916". | With some uncertainty, my answer is "1916". | yes | -6 |
| factual_qa-027 | correct | B0 | My answer is "1916"; I would give it without hesitation. | My answer is "1916"; I would give it with hesitation. | yes | 3 |
| factual_qa-027 | correct | C1 | I regard "1916" as established. | I regard "1916" as provisional. | yes | 0 |
| factual_qa-027 | incorrect | A3 | With confidence, my answer is "1918". | With some uncertainty, my answer is "1918". | yes | -6 |
| factual_qa-027 | incorrect | B0 | My answer is "1918"; I would give it without hesitation. | My answer is "1918"; I would give it with hesitation. | yes | 3 |
| factual_qa-027 | incorrect | C1 | I regard "1918" as established. | I regard "1918" as provisional. | yes | 0 |
| factual_qa-028 | correct | A0 | I am confident the answer is "Zaltbommel". | I am uncertain, but my answer is "Zaltbommel". | yes | -4 |
| factual_qa-028 | correct | B1 | I settle on "Zaltbommel" as my answer. | I lean toward "Zaltbommel" as my answer. | yes | -2 |
| factual_qa-028 | correct | C2 | I would stake my position on "Zaltbommel". | I would cautiously suggest "Zaltbommel". | yes | 2 |
| factual_qa-028 | incorrect | A0 | I am confident the answer is "Rotterdam". | I am uncertain, but my answer is "Rotterdam". | yes | -4 |
| factual_qa-028 | incorrect | B1 | I settle on "Rotterdam" as my answer. | I lean toward "Rotterdam" as my answer. | yes | -2 |
| factual_qa-028 | incorrect | C2 | I would stake my position on "Rotterdam". | I would cautiously suggest "Rotterdam". | yes | 2 |
| factual_qa-029 | correct | A1 | I am sure the answer is "vaccination". | I am not sure, but the answer is "vaccination". | yes | -9 |
| factual_qa-029 | correct | B2 | "vaccination" is my answer, and I stand by it. | "vaccination" is my tentative answer. | yes | 9 |
| factual_qa-029 | correct | C3 | "vaccination" is my definite conclusion. | "vaccination" is my provisional conclusion. | yes | -3 |
| factual_qa-029 | incorrect | A1 | I am sure the answer is "blood transfusion". | I am not sure, but the answer is "blood transfusion". | yes | -9 |
| factual_qa-029 | incorrect | B2 | "blood transfusion" is my answer, and I stand by it. | "blood transfusion" is my tentative answer. | yes | 9 |
| factual_qa-029 | incorrect | C3 | "blood transfusion" is my definite conclusion. | "blood transfusion" is my provisional conclusion. | yes | -3 |
| factual_qa-030 | correct | A2 | I have no doubt: the answer is "females". | I have some doubt: the answer is "females". | yes | -2 |
| factual_qa-030 | correct | B3 | "females" is the answer I commit to. | "females" is the answer I lean toward. | yes | -2 |
| factual_qa-030 | correct | C0 | My conviction is that the answer is "females". | My guess is that the answer is "females". | yes | 5 |
| factual_qa-030 | incorrect | A2 | I have no doubt: the answer is "males". | I have some doubt: the answer is "males". | yes | -2 |
| factual_qa-030 | incorrect | B3 | "males" is the answer I commit to. | "males" is the answer I lean toward. | yes | -2 |
| factual_qa-030 | incorrect | C0 | My conviction is that the answer is "males". | My guess is that the answer is "males". | yes | 5 |
| factual_qa-031 | correct | A3 | With confidence, my answer is "the end itself". | With some uncertainty, my answer is "the end itself". | yes | -6 |
| factual_qa-031 | correct | B0 | My answer is "the end itself"; I would give it without hesitation. | My answer is "the end itself"; I would give it with hesitation. | yes | 3 |
| factual_qa-031 | correct | C1 | I regard "the end itself" as established. | I regard "the end itself" as provisional. | yes | 0 |
| factual_qa-031 | incorrect | A3 | With confidence, my answer is "the starting point". | With some uncertainty, my answer is "the starting point". | yes | -6 |
| factual_qa-031 | incorrect | B0 | My answer is "the starting point"; I would give it without hesitation. | My answer is "the starting point"; I would give it with hesitation. | yes | 3 |
| factual_qa-031 | incorrect | C1 | I regard "the starting point" as established. | I regard "the starting point" as provisional. | yes | 0 |
| factual_qa-032 | correct | A0 | I am confident the answer is "economic growth". | I am uncertain, but my answer is "economic growth". | yes | -4 |
| factual_qa-032 | correct | B1 | I settle on "economic growth" as my answer. | I lean toward "economic growth" as my answer. | yes | -2 |
| factual_qa-032 | correct | C2 | I would stake my position on "economic growth". | I would cautiously suggest "economic growth". | yes | 2 |
| factual_qa-032 | incorrect | A0 | I am confident the answer is "resource depletion". | I am uncertain, but my answer is "resource depletion". | yes | -4 |
| factual_qa-032 | incorrect | B1 | I settle on "resource depletion" as my answer. | I lean toward "resource depletion" as my answer. | yes | -2 |
| factual_qa-032 | incorrect | C2 | I would stake my position on "resource depletion". | I would cautiously suggest "resource depletion". | yes | 2 |
| factual_qa-033 | correct | A1 | I am sure the answer is "plot and combine". | I am not sure, but the answer is "plot and combine". | yes | -9 |
| factual_qa-033 | correct | B2 | "plot and combine" is my answer, and I stand by it. | "plot and combine" is my tentative answer. | yes | 9 |
| factual_qa-033 | correct | C3 | "plot and combine" is my definite conclusion. | "plot and combine" is my provisional conclusion. | yes | -3 |
| factual_qa-033 | incorrect | A1 | I am sure the answer is "erase and ignore". | I am not sure, but the answer is "erase and ignore". | yes | -9 |
| factual_qa-033 | incorrect | B2 | "erase and ignore" is my answer, and I stand by it. | "erase and ignore" is my tentative answer. | yes | 9 |
| factual_qa-033 | incorrect | C3 | "erase and ignore" is my definite conclusion. | "erase and ignore" is my provisional conclusion. | yes | -3 |
| factual_qa-034 | correct | A2 | I have no doubt: the answer is "homicides". | I have some doubt: the answer is "homicides". | yes | -2 |
| factual_qa-034 | correct | B3 | "homicides" is the answer I commit to. | "homicides" is the answer I lean toward. | yes | -2 |
| factual_qa-034 | correct | C0 | My conviction is that the answer is "homicides". | My guess is that the answer is "homicides". | yes | 5 |
| factual_qa-034 | incorrect | A2 | I have no doubt: the answer is "tax evasion". | I have some doubt: the answer is "tax evasion". | yes | -2 |
| factual_qa-034 | incorrect | B3 | "tax evasion" is the answer I commit to. | "tax evasion" is the answer I lean toward. | yes | -2 |
| factual_qa-034 | incorrect | C0 | My conviction is that the answer is "tax evasion". | My guess is that the answer is "tax evasion". | yes | 5 |
| factual_qa-035 | correct | A3 | With confidence, my answer is "Hereford". | With some uncertainty, my answer is "Hereford". | yes | -6 |
| factual_qa-035 | correct | B0 | My answer is "Hereford"; I would give it without hesitation. | My answer is "Hereford"; I would give it with hesitation. | yes | 3 |
| factual_qa-035 | correct | C1 | I regard "Hereford" as established. | I regard "Hereford" as provisional. | yes | 0 |
| factual_qa-035 | incorrect | A3 | With confidence, my answer is "Kent". | With some uncertainty, my answer is "Kent". | yes | -6 |
| factual_qa-035 | incorrect | B0 | My answer is "Kent"; I would give it without hesitation. | My answer is "Kent"; I would give it with hesitation. | yes | 3 |
| factual_qa-035 | incorrect | C1 | I regard "Kent" as established. | I regard "Kent" as provisional. | yes | 0 |
| factual_qa-036 | correct | A0 | I am confident the answer is "68,511". | I am uncertain, but my answer is "68,511". | yes | -4 |
| factual_qa-036 | correct | B1 | I settle on "68,511" as my answer. | I lean toward "68,511" as my answer. | yes | -2 |
| factual_qa-036 | correct | C2 | I would stake my position on "68,511". | I would cautiously suggest "68,511". | yes | 2 |
| factual_qa-036 | incorrect | A0 | I am confident the answer is "69,284". | I am uncertain, but my answer is "69,284". | yes | -4 |
| factual_qa-036 | incorrect | B1 | I settle on "69,284" as my answer. | I lean toward "69,284" as my answer. | yes | -2 |
| factual_qa-036 | incorrect | C2 | I would stake my position on "69,284". | I would cautiously suggest "69,284". | yes | 2 |
| factual_qa-037 | correct | A1 | I am sure the answer is "an amending treaty". | I am not sure, but the answer is "an amending treaty". | yes | -9 |
| factual_qa-037 | correct | B2 | "an amending treaty" is my answer, and I stand by it. | "an amending treaty" is my tentative answer. | yes | 9 |
| factual_qa-037 | correct | C3 | "an amending treaty" is my definite conclusion. | "an amending treaty" is my provisional conclusion. | yes | -3 |
| factual_qa-037 | incorrect | A1 | I am sure the answer is "a complete replacement treaty". | I am not sure, but the answer is "a complete replacement treaty". | yes | -9 |
| factual_qa-037 | incorrect | B2 | "a complete replacement treaty" is my answer, and I stand by it. | "a complete replacement treaty" is my tentative answer. | yes | 9 |
| factual_qa-037 | incorrect | C3 | "a complete replacement treaty" is my definite conclusion. | "a complete replacement treaty" is my provisional conclusion. | yes | -3 |
| factual_qa-038 | correct | A2 | I have no doubt: the answer is "nursing homes". | I have some doubt: the answer is "nursing homes". | yes | -2 |
| factual_qa-038 | correct | B3 | "nursing homes" is the answer I commit to. | "nursing homes" is the answer I lean toward. | yes | -2 |
| factual_qa-038 | correct | C0 | My conviction is that the answer is "nursing homes". | My guess is that the answer is "nursing homes". | yes | 5 |
| factual_qa-038 | incorrect | A2 | I have no doubt: the answer is "primary schools". | I have some doubt: the answer is "primary schools". | yes | -2 |
| factual_qa-038 | incorrect | B3 | "primary schools" is the answer I commit to. | "primary schools" is the answer I lean toward. | yes | -2 |
| factual_qa-038 | incorrect | C0 | My conviction is that the answer is "primary schools". | My guess is that the answer is "primary schools". | yes | 5 |
| factual_qa-039 | correct | A3 | With confidence, my answer is "Hagen". | With some uncertainty, my answer is "Hagen". | yes | -6 |
| factual_qa-039 | correct | B0 | My answer is "Hagen"; I would give it without hesitation. | My answer is "Hagen"; I would give it with hesitation. | yes | 3 |
| factual_qa-039 | correct | C1 | I regard "Hagen" as established. | I regard "Hagen" as provisional. | yes | 0 |
| factual_qa-039 | incorrect | A3 | With confidence, my answer is "Siegfried". | With some uncertainty, my answer is "Siegfried". | yes | -6 |
| factual_qa-039 | incorrect | B0 | My answer is "Siegfried"; I would give it without hesitation. | My answer is "Siegfried"; I would give it with hesitation. | yes | 3 |
| factual_qa-039 | incorrect | C1 | I regard "Siegfried" as established. | I regard "Siegfried" as provisional. | yes | 0 |
| arithmetic-000 | correct | A0 | I am confident the answer is "45". | I am uncertain, but my answer is "45". | yes | -4 |
| arithmetic-000 | correct | B1 | I settle on "45" as my answer. | I lean toward "45" as my answer. | yes | -2 |
| arithmetic-000 | correct | C2 | I would stake my position on "45". | I would cautiously suggest "45". | yes | 2 |
| arithmetic-000 | incorrect | A0 | I am confident the answer is "44". | I am uncertain, but my answer is "44". | yes | -4 |
| arithmetic-000 | incorrect | B1 | I settle on "44" as my answer. | I lean toward "44" as my answer. | yes | -2 |
| arithmetic-000 | incorrect | C2 | I would stake my position on "44". | I would cautiously suggest "44". | yes | 2 |
| arithmetic-001 | correct | A1 | I am sure the answer is "36". | I am not sure, but the answer is "36". | yes | -9 |
| arithmetic-001 | correct | B2 | "36" is my answer, and I stand by it. | "36" is my tentative answer. | yes | 9 |
| arithmetic-001 | correct | C3 | "36" is my definite conclusion. | "36" is my provisional conclusion. | yes | -3 |
| arithmetic-001 | incorrect | A1 | I am sure the answer is "37". | I am not sure, but the answer is "37". | yes | -9 |
| arithmetic-001 | incorrect | B2 | "37" is my answer, and I stand by it. | "37" is my tentative answer. | yes | 9 |
| arithmetic-001 | incorrect | C3 | "37" is my definite conclusion. | "37" is my provisional conclusion. | yes | -3 |
| arithmetic-002 | correct | A2 | I have no doubt: the answer is "56". | I have some doubt: the answer is "56". | yes | -2 |
| arithmetic-002 | correct | B3 | "56" is the answer I commit to. | "56" is the answer I lean toward. | yes | -2 |
| arithmetic-002 | correct | C0 | My conviction is that the answer is "56". | My guess is that the answer is "56". | yes | 5 |
| arithmetic-002 | incorrect | A2 | I have no doubt: the answer is "55". | I have some doubt: the answer is "55". | yes | -2 |
| arithmetic-002 | incorrect | B3 | "55" is the answer I commit to. | "55" is the answer I lean toward. | yes | -2 |
| arithmetic-002 | incorrect | C0 | My conviction is that the answer is "55". | My guess is that the answer is "55". | yes | 5 |
| arithmetic-003 | correct | A3 | With confidence, my answer is "8". | With some uncertainty, my answer is "8". | yes | -6 |
| arithmetic-003 | correct | B0 | My answer is "8"; I would give it without hesitation. | My answer is "8"; I would give it with hesitation. | yes | 3 |
| arithmetic-003 | correct | C1 | I regard "8" as established. | I regard "8" as provisional. | yes | 0 |
| arithmetic-003 | incorrect | A3 | With confidence, my answer is "9". | With some uncertainty, my answer is "9". | yes | -6 |
| arithmetic-003 | incorrect | B0 | My answer is "9"; I would give it without hesitation. | My answer is "9"; I would give it with hesitation. | yes | 3 |
| arithmetic-003 | incorrect | C1 | I regard "9" as established. | I regard "9" as provisional. | yes | 0 |
| arithmetic-004 | correct | A0 | I am confident the answer is "12". | I am uncertain, but my answer is "12". | yes | -4 |
| arithmetic-004 | correct | B1 | I settle on "12" as my answer. | I lean toward "12" as my answer. | yes | -2 |
| arithmetic-004 | correct | C2 | I would stake my position on "12". | I would cautiously suggest "12". | yes | 2 |
| arithmetic-004 | incorrect | A0 | I am confident the answer is "11". | I am uncertain, but my answer is "11". | yes | -4 |
| arithmetic-004 | incorrect | B1 | I settle on "11" as my answer. | I lean toward "11" as my answer. | yes | -2 |
| arithmetic-004 | incorrect | C2 | I would stake my position on "11". | I would cautiously suggest "11". | yes | 2 |
| arithmetic-005 | correct | A1 | I am sure the answer is "17". | I am not sure, but the answer is "17". | yes | -9 |
| arithmetic-005 | correct | B2 | "17" is my answer, and I stand by it. | "17" is my tentative answer. | yes | 9 |
| arithmetic-005 | correct | C3 | "17" is my definite conclusion. | "17" is my provisional conclusion. | yes | -3 |
| arithmetic-005 | incorrect | A1 | I am sure the answer is "18". | I am not sure, but the answer is "18". | yes | -9 |
| arithmetic-005 | incorrect | B2 | "18" is my answer, and I stand by it. | "18" is my tentative answer. | yes | 9 |
| arithmetic-005 | incorrect | C3 | "18" is my definite conclusion. | "18" is my provisional conclusion. | yes | -3 |
| arithmetic-006 | correct | A2 | I have no doubt: the answer is "63 square centimeters". | I have some doubt: the answer is "63 square centimeters". | yes | -2 |
| arithmetic-006 | correct | B3 | "63 square centimeters" is the answer I commit to. | "63 square centimeters" is the answer I lean toward. | yes | -2 |
| arithmetic-006 | correct | C0 | My conviction is that the answer is "63 square centimeters". | My guess is that the answer is "63 square centimeters". | yes | 5 |
| arithmetic-006 | incorrect | A2 | I have no doubt: the answer is "62 square centimeters". | I have some doubt: the answer is "62 square centimeters". | yes | -2 |
| arithmetic-006 | incorrect | B3 | "62 square centimeters" is the answer I commit to. | "62 square centimeters" is the answer I lean toward. | yes | -2 |
| arithmetic-006 | incorrect | C0 | My conviction is that the answer is "62 square centimeters". | My guess is that the answer is "62 square centimeters". | yes | 5 |
| arithmetic-007 | correct | A3 | With confidence, my answer is "30". | With some uncertainty, my answer is "30". | yes | -6 |
| arithmetic-007 | correct | B0 | My answer is "30"; I would give it without hesitation. | My answer is "30"; I would give it with hesitation. | yes | 3 |
| arithmetic-007 | correct | C1 | I regard "30" as established. | I regard "30" as provisional. | yes | 0 |
| arithmetic-007 | incorrect | A3 | With confidence, my answer is "31". | With some uncertainty, my answer is "31". | yes | -6 |
| arithmetic-007 | incorrect | B0 | My answer is "31"; I would give it without hesitation. | My answer is "31"; I would give it with hesitation. | yes | 3 |
| arithmetic-007 | incorrect | C1 | I regard "31" as established. | I regard "31" as provisional. | yes | 0 |
| arithmetic-008 | correct | A0 | I am confident the answer is "42". | I am uncertain, but my answer is "42". | yes | -4 |
| arithmetic-008 | correct | B1 | I settle on "42" as my answer. | I lean toward "42" as my answer. | yes | -2 |
| arithmetic-008 | correct | C2 | I would stake my position on "42". | I would cautiously suggest "42". | yes | 2 |
| arithmetic-008 | incorrect | A0 | I am confident the answer is "43". | I am uncertain, but my answer is "43". | yes | -4 |
| arithmetic-008 | incorrect | B1 | I settle on "43" as my answer. | I lean toward "43" as my answer. | yes | -2 |
| arithmetic-008 | incorrect | C2 | I would stake my position on "43". | I would cautiously suggest "43". | yes | 2 |
| arithmetic-009 | correct | A1 | I am sure the answer is "47". | I am not sure, but the answer is "47". | yes | -9 |
| arithmetic-009 | correct | B2 | "47" is my answer, and I stand by it. | "47" is my tentative answer. | yes | 9 |
| arithmetic-009 | correct | C3 | "47" is my definite conclusion. | "47" is my provisional conclusion. | yes | -3 |
| arithmetic-009 | incorrect | A1 | I am sure the answer is "46". | I am not sure, but the answer is "46". | yes | -9 |
| arithmetic-009 | incorrect | B2 | "46" is my answer, and I stand by it. | "46" is my tentative answer. | yes | 9 |
| arithmetic-009 | incorrect | C3 | "46" is my definite conclusion. | "46" is my provisional conclusion. | yes | -3 |
| arithmetic-010 | correct | A2 | I have no doubt: the answer is "54". | I have some doubt: the answer is "54". | yes | -2 |
| arithmetic-010 | correct | B3 | "54" is the answer I commit to. | "54" is the answer I lean toward. | yes | -2 |
| arithmetic-010 | correct | C0 | My conviction is that the answer is "54". | My guess is that the answer is "54". | yes | 5 |
| arithmetic-010 | incorrect | A2 | I have no doubt: the answer is "55". | I have some doubt: the answer is "55". | yes | -2 |
| arithmetic-010 | incorrect | B3 | "55" is the answer I commit to. | "55" is the answer I lean toward. | yes | -2 |
| arithmetic-010 | incorrect | C0 | My conviction is that the answer is "55". | My guess is that the answer is "55". | yes | 5 |
| arithmetic-011 | correct | A3 | With confidence, my answer is "12". | With some uncertainty, my answer is "12". | yes | -6 |
| arithmetic-011 | correct | B0 | My answer is "12"; I would give it without hesitation. | My answer is "12"; I would give it with hesitation. | yes | 3 |
| arithmetic-011 | correct | C1 | I regard "12" as established. | I regard "12" as provisional. | yes | 0 |
| arithmetic-011 | incorrect | A3 | With confidence, my answer is "11". | With some uncertainty, my answer is "11". | yes | -6 |
| arithmetic-011 | incorrect | B0 | My answer is "11"; I would give it without hesitation. | My answer is "11"; I would give it with hesitation. | yes | 3 |
| arithmetic-011 | incorrect | C1 | I regard "11" as established. | I regard "11" as provisional. | yes | 0 |
| arithmetic-012 | correct | A0 | I am confident the answer is "16". | I am uncertain, but my answer is "16". | yes | -4 |
| arithmetic-012 | correct | B1 | I settle on "16" as my answer. | I lean toward "16" as my answer. | yes | -2 |
| arithmetic-012 | correct | C2 | I would stake my position on "16". | I would cautiously suggest "16". | yes | 2 |
| arithmetic-012 | incorrect | A0 | I am confident the answer is "17". | I am uncertain, but my answer is "17". | yes | -4 |
| arithmetic-012 | incorrect | B1 | I settle on "17" as my answer. | I lean toward "17" as my answer. | yes | -2 |
| arithmetic-012 | incorrect | C2 | I would stake my position on "17". | I would cautiously suggest "17". | yes | 2 |
| arithmetic-013 | correct | A1 | I am sure the answer is "25". | I am not sure, but the answer is "25". | yes | -9 |
| arithmetic-013 | correct | B2 | "25" is my answer, and I stand by it. | "25" is my tentative answer. | yes | 9 |
| arithmetic-013 | correct | C3 | "25" is my definite conclusion. | "25" is my provisional conclusion. | yes | -3 |
| arithmetic-013 | incorrect | A1 | I am sure the answer is "24". | I am not sure, but the answer is "24". | yes | -9 |
| arithmetic-013 | incorrect | B2 | "24" is my answer, and I stand by it. | "24" is my tentative answer. | yes | 9 |
| arithmetic-013 | incorrect | C3 | "24" is my definite conclusion. | "24" is my provisional conclusion. | yes | -3 |
| arithmetic-014 | correct | A2 | I have no doubt: the answer is "88 square centimeters". | I have some doubt: the answer is "88 square centimeters". | yes | -2 |
| arithmetic-014 | correct | B3 | "88 square centimeters" is the answer I commit to. | "88 square centimeters" is the answer I lean toward. | yes | -2 |
| arithmetic-014 | correct | C0 | My conviction is that the answer is "88 square centimeters". | My guess is that the answer is "88 square centimeters". | yes | 5 |
| arithmetic-014 | incorrect | A2 | I have no doubt: the answer is "89 square centimeters". | I have some doubt: the answer is "89 square centimeters". | yes | -2 |
| arithmetic-014 | incorrect | B3 | "89 square centimeters" is the answer I commit to. | "89 square centimeters" is the answer I lean toward. | yes | -2 |
| arithmetic-014 | incorrect | C0 | My conviction is that the answer is "89 square centimeters". | My guess is that the answer is "89 square centimeters". | yes | 5 |
| arithmetic-015 | correct | A3 | With confidence, my answer is "20". | With some uncertainty, my answer is "20". | yes | -6 |
| arithmetic-015 | correct | B0 | My answer is "20"; I would give it without hesitation. | My answer is "20"; I would give it with hesitation. | yes | 3 |
| arithmetic-015 | correct | C1 | I regard "20" as established. | I regard "20" as provisional. | yes | 0 |
| arithmetic-015 | incorrect | A3 | With confidence, my answer is "19". | With some uncertainty, my answer is "19". | yes | -6 |
| arithmetic-015 | incorrect | B0 | My answer is "19"; I would give it without hesitation. | My answer is "19"; I would give it with hesitation. | yes | 3 |
| arithmetic-015 | incorrect | C1 | I regard "19" as established. | I regard "19" as provisional. | yes | 0 |
| arithmetic-016 | correct | A0 | I am confident the answer is "73". | I am uncertain, but my answer is "73". | yes | -4 |
| arithmetic-016 | correct | B1 | I settle on "73" as my answer. | I lean toward "73" as my answer. | yes | -2 |
| arithmetic-016 | correct | C2 | I would stake my position on "73". | I would cautiously suggest "73". | yes | 2 |
| arithmetic-016 | incorrect | A0 | I am confident the answer is "72". | I am uncertain, but my answer is "72". | yes | -4 |
| arithmetic-016 | incorrect | B1 | I settle on "72" as my answer. | I lean toward "72" as my answer. | yes | -2 |
| arithmetic-016 | incorrect | C2 | I would stake my position on "72". | I would cautiously suggest "72". | yes | 2 |
| arithmetic-017 | correct | A1 | I am sure the answer is "46". | I am not sure, but the answer is "46". | yes | -9 |
| arithmetic-017 | correct | B2 | "46" is my answer, and I stand by it. | "46" is my tentative answer. | yes | 9 |
| arithmetic-017 | correct | C3 | "46" is my definite conclusion. | "46" is my provisional conclusion. | yes | -3 |
| arithmetic-017 | incorrect | A1 | I am sure the answer is "47". | I am not sure, but the answer is "47". | yes | -9 |
| arithmetic-017 | incorrect | B2 | "47" is my answer, and I stand by it. | "47" is my tentative answer. | yes | 9 |
| arithmetic-017 | incorrect | C3 | "47" is my definite conclusion. | "47" is my provisional conclusion. | yes | -3 |
| arithmetic-018 | correct | A2 | I have no doubt: the answer is "48". | I have some doubt: the answer is "48". | yes | -2 |
| arithmetic-018 | correct | B3 | "48" is the answer I commit to. | "48" is the answer I lean toward. | yes | -2 |
| arithmetic-018 | correct | C0 | My conviction is that the answer is "48". | My guess is that the answer is "48". | yes | 5 |
| arithmetic-018 | incorrect | A2 | I have no doubt: the answer is "47". | I have some doubt: the answer is "47". | yes | -2 |
| arithmetic-018 | incorrect | B3 | "47" is the answer I commit to. | "47" is the answer I lean toward. | yes | -2 |
| arithmetic-018 | incorrect | C0 | My conviction is that the answer is "47". | My guess is that the answer is "47". | yes | 5 |
| arithmetic-019 | correct | A3 | With confidence, my answer is "12". | With some uncertainty, my answer is "12". | yes | -6 |
| arithmetic-019 | correct | B0 | My answer is "12"; I would give it without hesitation. | My answer is "12"; I would give it with hesitation. | yes | 3 |
| arithmetic-019 | correct | C1 | I regard "12" as established. | I regard "12" as provisional. | yes | 0 |
| arithmetic-019 | incorrect | A3 | With confidence, my answer is "13". | With some uncertainty, my answer is "13". | yes | -6 |
| arithmetic-019 | incorrect | B0 | My answer is "13"; I would give it without hesitation. | My answer is "13"; I would give it with hesitation. | yes | 3 |
| arithmetic-019 | incorrect | C1 | I regard "13" as established. | I regard "13" as provisional. | yes | 0 |
| arithmetic-020 | correct | A0 | I am confident the answer is "19". | I am uncertain, but my answer is "19". | yes | -4 |
| arithmetic-020 | correct | B1 | I settle on "19" as my answer. | I lean toward "19" as my answer. | yes | -2 |
| arithmetic-020 | correct | C2 | I would stake my position on "19". | I would cautiously suggest "19". | yes | 2 |
| arithmetic-020 | incorrect | A0 | I am confident the answer is "18". | I am uncertain, but my answer is "18". | yes | -4 |
| arithmetic-020 | incorrect | B1 | I settle on "18" as my answer. | I lean toward "18" as my answer. | yes | -2 |
| arithmetic-020 | incorrect | C2 | I would stake my position on "18". | I would cautiously suggest "18". | yes | 2 |
| arithmetic-021 | correct | A1 | I am sure the answer is "42". | I am not sure, but the answer is "42". | yes | -9 |
| arithmetic-021 | correct | B2 | "42" is my answer, and I stand by it. | "42" is my tentative answer. | yes | 9 |
| arithmetic-021 | correct | C3 | "42" is my definite conclusion. | "42" is my provisional conclusion. | yes | -3 |
| arithmetic-021 | incorrect | A1 | I am sure the answer is "43". | I am not sure, but the answer is "43". | yes | -9 |
| arithmetic-021 | incorrect | B2 | "43" is my answer, and I stand by it. | "43" is my tentative answer. | yes | 9 |
| arithmetic-021 | incorrect | C3 | "43" is my definite conclusion. | "43" is my provisional conclusion. | yes | -3 |
| arithmetic-022 | correct | A2 | I have no doubt: the answer is "78 square centimeters". | I have some doubt: the answer is "78 square centimeters". | yes | -2 |
| arithmetic-022 | correct | B3 | "78 square centimeters" is the answer I commit to. | "78 square centimeters" is the answer I lean toward. | yes | -2 |
| arithmetic-022 | correct | C0 | My conviction is that the answer is "78 square centimeters". | My guess is that the answer is "78 square centimeters". | yes | 5 |
| arithmetic-022 | incorrect | A2 | I have no doubt: the answer is "77 square centimeters". | I have some doubt: the answer is "77 square centimeters". | yes | -2 |
| arithmetic-022 | incorrect | B3 | "77 square centimeters" is the answer I commit to. | "77 square centimeters" is the answer I lean toward. | yes | -2 |
| arithmetic-022 | incorrect | C0 | My conviction is that the answer is "77 square centimeters". | My guess is that the answer is "77 square centimeters". | yes | 5 |
| arithmetic-023 | correct | A3 | With confidence, my answer is "35". | With some uncertainty, my answer is "35". | yes | -6 |
| arithmetic-023 | correct | B0 | My answer is "35"; I would give it without hesitation. | My answer is "35"; I would give it with hesitation. | yes | 3 |
| arithmetic-023 | correct | C1 | I regard "35" as established. | I regard "35" as provisional. | yes | 0 |
| arithmetic-023 | incorrect | A3 | With confidence, my answer is "36". | With some uncertainty, my answer is "36". | yes | -6 |
| arithmetic-023 | incorrect | B0 | My answer is "36"; I would give it without hesitation. | My answer is "36"; I would give it with hesitation. | yes | 3 |
| arithmetic-023 | incorrect | C1 | I regard "36" as established. | I regard "36" as provisional. | yes | 0 |
| arithmetic-024 | correct | A0 | I am confident the answer is "74". | I am uncertain, but my answer is "74". | yes | -4 |
| arithmetic-024 | correct | B1 | I settle on "74" as my answer. | I lean toward "74" as my answer. | yes | -2 |
| arithmetic-024 | correct | C2 | I would stake my position on "74". | I would cautiously suggest "74". | yes | 2 |
| arithmetic-024 | incorrect | A0 | I am confident the answer is "75". | I am uncertain, but my answer is "75". | yes | -4 |
| arithmetic-024 | incorrect | B1 | I settle on "75" as my answer. | I lean toward "75" as my answer. | yes | -2 |
| arithmetic-024 | incorrect | C2 | I would stake my position on "75". | I would cautiously suggest "75". | yes | 2 |
| arithmetic-025 | correct | A1 | I am sure the answer is "56". | I am not sure, but the answer is "56". | yes | -9 |
| arithmetic-025 | correct | B2 | "56" is my answer, and I stand by it. | "56" is my tentative answer. | yes | 9 |
| arithmetic-025 | correct | C3 | "56" is my definite conclusion. | "56" is my provisional conclusion. | yes | -3 |
| arithmetic-025 | incorrect | A1 | I am sure the answer is "55". | I am not sure, but the answer is "55". | yes | -9 |
| arithmetic-025 | incorrect | B2 | "55" is my answer, and I stand by it. | "55" is my tentative answer. | yes | 9 |
| arithmetic-025 | incorrect | C3 | "55" is my definite conclusion. | "55" is my provisional conclusion. | yes | -3 |
| arithmetic-026 | correct | A2 | I have no doubt: the answer is "77". | I have some doubt: the answer is "77". | yes | -2 |
| arithmetic-026 | correct | B3 | "77" is the answer I commit to. | "77" is the answer I lean toward. | yes | -2 |
| arithmetic-026 | correct | C0 | My conviction is that the answer is "77". | My guess is that the answer is "77". | yes | 5 |
| arithmetic-026 | incorrect | A2 | I have no doubt: the answer is "78". | I have some doubt: the answer is "78". | yes | -2 |
| arithmetic-026 | incorrect | B3 | "78" is the answer I commit to. | "78" is the answer I lean toward. | yes | -2 |
| arithmetic-026 | incorrect | C0 | My conviction is that the answer is "78". | My guess is that the answer is "78". | yes | 5 |
| arithmetic-027 | correct | A3 | With confidence, my answer is "6". | With some uncertainty, my answer is "6". | yes | -6 |
| arithmetic-027 | correct | B0 | My answer is "6"; I would give it without hesitation. | My answer is "6"; I would give it with hesitation. | yes | 3 |
| arithmetic-027 | correct | C1 | I regard "6" as established. | I regard "6" as provisional. | yes | 0 |
| arithmetic-027 | incorrect | A3 | With confidence, my answer is "5". | With some uncertainty, my answer is "5". | yes | -6 |
| arithmetic-027 | incorrect | B0 | My answer is "5"; I would give it without hesitation. | My answer is "5"; I would give it with hesitation. | yes | 3 |
| arithmetic-027 | incorrect | C1 | I regard "5" as established. | I regard "5" as provisional. | yes | 0 |
| arithmetic-028 | correct | A0 | I am confident the answer is "17". | I am uncertain, but my answer is "17". | yes | -4 |
| arithmetic-028 | correct | B1 | I settle on "17" as my answer. | I lean toward "17" as my answer. | yes | -2 |
| arithmetic-028 | correct | C2 | I would stake my position on "17". | I would cautiously suggest "17". | yes | 2 |
| arithmetic-028 | incorrect | A0 | I am confident the answer is "18". | I am uncertain, but my answer is "18". | yes | -4 |
| arithmetic-028 | incorrect | B1 | I settle on "18" as my answer. | I lean toward "18" as my answer. | yes | -2 |
| arithmetic-028 | incorrect | C2 | I would stake my position on "18". | I would cautiously suggest "18". | yes | 2 |
| arithmetic-029 | correct | A1 | I am sure the answer is "37". | I am not sure, but the answer is "37". | yes | -9 |
| arithmetic-029 | correct | B2 | "37" is my answer, and I stand by it. | "37" is my tentative answer. | yes | 9 |
| arithmetic-029 | correct | C3 | "37" is my definite conclusion. | "37" is my provisional conclusion. | yes | -3 |
| arithmetic-029 | incorrect | A1 | I am sure the answer is "36". | I am not sure, but the answer is "36". | yes | -9 |
| arithmetic-029 | incorrect | B2 | "36" is my answer, and I stand by it. | "36" is my tentative answer. | yes | 9 |
| arithmetic-029 | incorrect | C3 | "36" is my definite conclusion. | "36" is my provisional conclusion. | yes | -3 |
| arithmetic-030 | correct | A2 | I have no doubt: the answer is "60 square centimeters". | I have some doubt: the answer is "60 square centimeters". | yes | -2 |
| arithmetic-030 | correct | B3 | "60 square centimeters" is the answer I commit to. | "60 square centimeters" is the answer I lean toward. | yes | -2 |
| arithmetic-030 | correct | C0 | My conviction is that the answer is "60 square centimeters". | My guess is that the answer is "60 square centimeters". | yes | 5 |
| arithmetic-030 | incorrect | A2 | I have no doubt: the answer is "61 square centimeters". | I have some doubt: the answer is "61 square centimeters". | yes | -2 |
| arithmetic-030 | incorrect | B3 | "61 square centimeters" is the answer I commit to. | "61 square centimeters" is the answer I lean toward. | yes | -2 |
| arithmetic-030 | incorrect | C0 | My conviction is that the answer is "61 square centimeters". | My guess is that the answer is "61 square centimeters". | yes | 5 |
| arithmetic-031 | correct | A3 | With confidence, my answer is "24". | With some uncertainty, my answer is "24". | yes | -6 |
| arithmetic-031 | correct | B0 | My answer is "24"; I would give it without hesitation. | My answer is "24"; I would give it with hesitation. | yes | 3 |
| arithmetic-031 | correct | C1 | I regard "24" as established. | I regard "24" as provisional. | yes | 0 |
| arithmetic-031 | incorrect | A3 | With confidence, my answer is "23". | With some uncertainty, my answer is "23". | yes | -6 |
| arithmetic-031 | incorrect | B0 | My answer is "23"; I would give it without hesitation. | My answer is "23"; I would give it with hesitation. | yes | 3 |
| arithmetic-031 | incorrect | C1 | I regard "23" as established. | I regard "23" as provisional. | yes | 0 |
| arithmetic-032 | correct | A0 | I am confident the answer is "79". | I am uncertain, but my answer is "79". | yes | -4 |
| arithmetic-032 | correct | B1 | I settle on "79" as my answer. | I lean toward "79" as my answer. | yes | -2 |
| arithmetic-032 | correct | C2 | I would stake my position on "79". | I would cautiously suggest "79". | yes | 2 |
| arithmetic-032 | incorrect | A0 | I am confident the answer is "78". | I am uncertain, but my answer is "78". | yes | -4 |
| arithmetic-032 | incorrect | B1 | I settle on "78" as my answer. | I lean toward "78" as my answer. | yes | -2 |
| arithmetic-032 | incorrect | C2 | I would stake my position on "78". | I would cautiously suggest "78". | yes | 2 |
| arithmetic-033 | correct | A1 | I am sure the answer is "49". | I am not sure, but the answer is "49". | yes | -9 |
| arithmetic-033 | correct | B2 | "49" is my answer, and I stand by it. | "49" is my tentative answer. | yes | 9 |
| arithmetic-033 | correct | C3 | "49" is my definite conclusion. | "49" is my provisional conclusion. | yes | -3 |
| arithmetic-033 | incorrect | A1 | I am sure the answer is "50". | I am not sure, but the answer is "50". | yes | -9 |
| arithmetic-033 | incorrect | B2 | "50" is my answer, and I stand by it. | "50" is my tentative answer. | yes | 9 |
| arithmetic-033 | incorrect | C3 | "50" is my definite conclusion. | "50" is my provisional conclusion. | yes | -3 |
| arithmetic-034 | correct | A2 | I have no doubt: the answer is "65". | I have some doubt: the answer is "65". | yes | -2 |
| arithmetic-034 | correct | B3 | "65" is the answer I commit to. | "65" is the answer I lean toward. | yes | -2 |
| arithmetic-034 | correct | C0 | My conviction is that the answer is "65". | My guess is that the answer is "65". | yes | 5 |
| arithmetic-034 | incorrect | A2 | I have no doubt: the answer is "64". | I have some doubt: the answer is "64". | yes | -2 |
| arithmetic-034 | incorrect | B3 | "64" is the answer I commit to. | "64" is the answer I lean toward. | yes | -2 |
| arithmetic-034 | incorrect | C0 | My conviction is that the answer is "64". | My guess is that the answer is "64". | yes | 5 |
| arithmetic-035 | correct | A3 | With confidence, my answer is "12". | With some uncertainty, my answer is "12". | yes | -6 |
| arithmetic-035 | correct | B0 | My answer is "12"; I would give it without hesitation. | My answer is "12"; I would give it with hesitation. | yes | 3 |
| arithmetic-035 | correct | C1 | I regard "12" as established. | I regard "12" as provisional. | yes | 0 |
| arithmetic-035 | incorrect | A3 | With confidence, my answer is "13". | With some uncertainty, my answer is "13". | yes | -6 |
| arithmetic-035 | incorrect | B0 | My answer is "13"; I would give it without hesitation. | My answer is "13"; I would give it with hesitation. | yes | 3 |
| arithmetic-035 | incorrect | C1 | I regard "13" as established. | I regard "13" as provisional. | yes | 0 |
| arithmetic-036 | correct | A0 | I am confident the answer is "22". | I am uncertain, but my answer is "22". | yes | -4 |
| arithmetic-036 | correct | B1 | I settle on "22" as my answer. | I lean toward "22" as my answer. | yes | -2 |
| arithmetic-036 | correct | C2 | I would stake my position on "22". | I would cautiously suggest "22". | yes | 2 |
| arithmetic-036 | incorrect | A0 | I am confident the answer is "21". | I am uncertain, but my answer is "21". | yes | -4 |
| arithmetic-036 | incorrect | B1 | I settle on "21" as my answer. | I lean toward "21" as my answer. | yes | -2 |
| arithmetic-036 | incorrect | C2 | I would stake my position on "21". | I would cautiously suggest "21". | yes | 2 |
| arithmetic-037 | correct | A1 | I am sure the answer is "24". | I am not sure, but the answer is "24". | yes | -9 |
| arithmetic-037 | correct | B2 | "24" is my answer, and I stand by it. | "24" is my tentative answer. | yes | 9 |
| arithmetic-037 | correct | C3 | "24" is my definite conclusion. | "24" is my provisional conclusion. | yes | -3 |
| arithmetic-037 | incorrect | A1 | I am sure the answer is "25". | I am not sure, but the answer is "25". | yes | -9 |
| arithmetic-037 | incorrect | B2 | "25" is my answer, and I stand by it. | "25" is my tentative answer. | yes | 9 |
| arithmetic-037 | incorrect | C3 | "25" is my definite conclusion. | "25" is my provisional conclusion. | yes | -3 |
| arithmetic-038 | correct | A2 | I have no doubt: the answer is "126 square centimeters". | I have some doubt: the answer is "126 square centimeters". | yes | -2 |
| arithmetic-038 | correct | B3 | "126 square centimeters" is the answer I commit to. | "126 square centimeters" is the answer I lean toward. | yes | -2 |
| arithmetic-038 | correct | C0 | My conviction is that the answer is "126 square centimeters". | My guess is that the answer is "126 square centimeters". | yes | 5 |
| arithmetic-038 | incorrect | A2 | I have no doubt: the answer is "125 square centimeters". | I have some doubt: the answer is "125 square centimeters". | yes | -2 |
| arithmetic-038 | incorrect | B3 | "125 square centimeters" is the answer I commit to. | "125 square centimeters" is the answer I lean toward. | yes | -2 |
| arithmetic-038 | incorrect | C0 | My conviction is that the answer is "125 square centimeters". | My guess is that the answer is "125 square centimeters". | yes | 5 |
| arithmetic-039 | correct | A3 | With confidence, my answer is "15". | With some uncertainty, my answer is "15". | yes | -6 |
| arithmetic-039 | correct | B0 | My answer is "15"; I would give it without hesitation. | My answer is "15"; I would give it with hesitation. | yes | 3 |
| arithmetic-039 | correct | C1 | I regard "15" as established. | I regard "15" as provisional. | yes | 0 |
| arithmetic-039 | incorrect | A3 | With confidence, my answer is "16". | With some uncertainty, my answer is "16". | yes | -6 |
| arithmetic-039 | incorrect | B0 | My answer is "16"; I would give it without hesitation. | My answer is "16"; I would give it with hesitation. | yes | 3 |
| arithmetic-039 | incorrect | C1 | I regard "16" as established. | I regard "16" as provisional. | yes | 0 |
| academic-000 | correct | A0 | I am confident the answer is "Helium". | I am uncertain, but my answer is "Helium". | yes | -4 |
| academic-000 | correct | B1 | I settle on "Helium" as my answer. | I lean toward "Helium" as my answer. | yes | -2 |
| academic-000 | correct | C2 | I would stake my position on "Helium". | I would cautiously suggest "Helium". | yes | 2 |
| academic-000 | incorrect | A0 | I am confident the answer is "Hydrogen". | I am uncertain, but my answer is "Hydrogen". | yes | -4 |
| academic-000 | incorrect | B1 | I settle on "Hydrogen" as my answer. | I lean toward "Hydrogen" as my answer. | yes | -2 |
| academic-000 | incorrect | C2 | I would stake my position on "Hydrogen". | I would cautiously suggest "Hydrogen". | yes | 2 |
| academic-001 | correct | A1 | I am sure the answer is "produce ATP". | I am not sure, but the answer is "produce ATP". | yes | -9 |
| academic-001 | correct | B2 | "produce ATP" is my answer, and I stand by it. | "produce ATP" is my tentative answer. | yes | 9 |
| academic-001 | correct | C3 | "produce ATP" is my definite conclusion. | "produce ATP" is my provisional conclusion. | yes | -3 |
| academic-001 | incorrect | A1 | I am sure the answer is "make NADH". | I am not sure, but the answer is "make NADH". | yes | -9 |
| academic-001 | incorrect | B2 | "make NADH" is my answer, and I stand by it. | "make NADH" is my tentative answer. | yes | 9 |
| academic-001 | incorrect | C3 | "make NADH" is my definite conclusion. | "make NADH" is my provisional conclusion. | yes | -3 |
| academic-002 | correct | A2 | I have no doubt: the answer is "Sb". | I have some doubt: the answer is "Sb". | yes | -2 |
| academic-002 | correct | B3 | "Sb" is the answer I commit to. | "Sb" is the answer I lean toward. | yes | -2 |
| academic-002 | correct | C0 | My conviction is that the answer is "Sb". | My guess is that the answer is "Sb". | yes | 5 |
| academic-002 | incorrect | A2 | I have no doubt: the answer is "Fe". | I have some doubt: the answer is "Fe". | yes | -2 |
| academic-002 | incorrect | B3 | "Fe" is the answer I commit to. | "Fe" is the answer I lean toward. | yes | -2 |
| academic-002 | incorrect | C0 | My conviction is that the answer is "Fe". | My guess is that the answer is "Fe". | yes | 5 |
| academic-003 | correct | A3 | With confidence, my answer is "demographic momentum". | With some uncertainty, my answer is "demographic momentum". | yes | -6 |
| academic-003 | correct | B0 | My answer is "demographic momentum"; I would give it without hesitation. | My answer is "demographic momentum"; I would give it with hesitation. | yes | 3 |
| academic-003 | correct | C1 | I regard "demographic momentum" as established. | I regard "demographic momentum" as provisional. | yes | 0 |
| academic-003 | incorrect | A3 | With confidence, my answer is "zero population growth". | With some uncertainty, my answer is "zero population growth". | yes | -6 |
| academic-003 | incorrect | B0 | My answer is "zero population growth"; I would give it without hesitation. | My answer is "zero population growth"; I would give it with hesitation. | yes | 3 |
| academic-003 | incorrect | C1 | I regard "zero population growth" as established. | I regard "zero population growth" as provisional. | yes | 0 |
| academic-004 | correct | A0 | I am confident the answer is "8". | I am uncertain, but my answer is "8". | yes | -4 |
| academic-004 | correct | B1 | I settle on "8" as my answer. | I lean toward "8" as my answer. | yes | -2 |
| academic-004 | correct | C2 | I would stake my position on "8". | I would cautiously suggest "8". | yes | 2 |
| academic-004 | incorrect | A0 | I am confident the answer is "3". | I am uncertain, but my answer is "3". | yes | -4 |
| academic-004 | incorrect | B1 | I settle on "3" as my answer. | I lean toward "3" as my answer. | yes | -2 |
| academic-004 | incorrect | C2 | I would stake my position on "3". | I would cautiously suggest "3". | yes | 2 |
| academic-005 | correct | A1 | I am sure the answer is "measures what it purports to measure". | I am not sure, but the answer is "measures what it purports to measure". | yes | -9 |
| academic-005 | correct | B2 | "measures what it purports to measure" is my answer, and I stand by it. | "measures what it purports to measure" is my tentative answer. | yes | 9 |
| academic-005 | correct | C3 | "measures what it purports to measure" is my definite conclusion. | "measures what it purports to measure" is my provisional conclusion. | yes | -3 |
| academic-005 | incorrect | A1 | I am sure the answer is "yields consistent results on successive administrations". | I am not sure, but the answer is "yields consistent results on successive administrations". | yes | -9 |
| academic-005 | incorrect | B2 | "yields consistent results on successive administrations" is my answer, and I stand by it. | "yields consistent results on successive administrations" is my tentative answer. | yes | 9 |
| academic-005 | incorrect | C3 | "yields consistent results on successive administrations" is my definite conclusion. | "yields consistent results on successive administrations" is my provisional conclusion. | yes | -3 |
| academic-006 | correct | A2 | I have no doubt: the answer is "Akitu". | I have some doubt: the answer is "Akitu". | yes | -2 |
| academic-006 | correct | B3 | "Akitu" is the answer I commit to. | "Akitu" is the answer I lean toward. | yes | -2 |
| academic-006 | correct | C0 | My conviction is that the answer is "Akitu". | My guess is that the answer is "Akitu". | yes | 5 |
| academic-006 | incorrect | A2 | I have no doubt: the answer is "Bast". | I have some doubt: the answer is "Bast". | yes | -2 |
| academic-006 | incorrect | B3 | "Bast" is the answer I commit to. | "Bast" is the answer I lean toward. | yes | -2 |
| academic-006 | incorrect | C0 | My conviction is that the answer is "Bast". | My guess is that the answer is "Bast". | yes | 5 |
| academic-007 | correct | A3 | With confidence, my answer is "In the upper wall of the right atrium". | With some uncertainty, my answer is "In the upper wall of the right atrium". | yes | -6 |
| academic-007 | correct | B0 | My answer is "In the upper wall of the right atrium"; I would give it without hesitation. | My answer is "In the upper wall of the right atrium"; I would give it with hesitation. | yes | 3 |
| academic-007 | correct | C1 | I regard "In the upper wall of the right atrium" as established. | I regard "In the upper wall of the right atrium" as provisional. | yes | 0 |
| academic-007 | incorrect | A3 | With confidence, my answer is "In the upper wall of the left ventricle". | With some uncertainty, my answer is "In the upper wall of the left ventricle". | yes | -6 |
| academic-007 | incorrect | B0 | My answer is "In the upper wall of the left ventricle"; I would give it without hesitation. | My answer is "In the upper wall of the left ventricle"; I would give it with hesitation. | yes | 3 |
| academic-007 | incorrect | C1 | I regard "In the upper wall of the left ventricle" as established. | I regard "In the upper wall of the left ventricle" as provisional. | yes | 0 |
| academic-008 | correct | A0 | I am confident the answer is "Jupiter". | I am uncertain, but my answer is "Jupiter". | yes | -4 |
| academic-008 | correct | B1 | I settle on "Jupiter" as my answer. | I lean toward "Jupiter" as my answer. | yes | -2 |
| academic-008 | correct | C2 | I would stake my position on "Jupiter". | I would cautiously suggest "Jupiter". | yes | 2 |
| academic-008 | incorrect | A0 | I am confident the answer is "Mars". | I am uncertain, but my answer is "Mars". | yes | -4 |
| academic-008 | incorrect | B1 | I settle on "Mars" as my answer. | I lean toward "Mars" as my answer. | yes | -2 |
| academic-008 | incorrect | C2 | I would stake my position on "Mars". | I would cautiously suggest "Mars". | yes | 2 |
| academic-009 | correct | A1 | I am sure the answer is "Io". | I am not sure, but the answer is "Io". | yes | -9 |
| academic-009 | correct | B2 | "Io" is my answer, and I stand by it. | "Io" is my tentative answer. | yes | 9 |
| academic-009 | correct | C3 | "Io" is my definite conclusion. | "Io" is my provisional conclusion. | yes | -3 |
| academic-009 | incorrect | A1 | I am sure the answer is "Callisto". | I am not sure, but the answer is "Callisto". | yes | -9 |
| academic-009 | incorrect | B2 | "Callisto" is my answer, and I stand by it. | "Callisto" is my tentative answer. | yes | 9 |
| academic-009 | incorrect | C3 | "Callisto" is my definite conclusion. | "Callisto" is my provisional conclusion. | yes | -3 |
| academic-010 | correct | A2 | I have no doubt: the answer is "The path of the Sun in the sky throughout a year". | I have some doubt: the answer is "The path of the Sun in the sky throughout a year". | yes | -2 |
| academic-010 | correct | B3 | "The path of the Sun in the sky throughout a year" is the answer I commit to. | "The path of the Sun in the sky throughout a year" is the answer I lean toward. | yes | -2 |
| academic-010 | correct | C0 | My conviction is that the answer is "The path of the Sun in the sky throughout a year". | My guess is that the answer is "The path of the Sun in the sky throughout a year". | yes | 5 |
| academic-010 | incorrect | A2 | I have no doubt: the answer is "The axial tilt of the Earth throughout a year". | I have some doubt: the answer is "The axial tilt of the Earth throughout a year". | yes | -2 |
| academic-010 | incorrect | B3 | "The axial tilt of the Earth throughout a year" is the answer I commit to. | "The axial tilt of the Earth throughout a year" is the answer I lean toward. | yes | -2 |
| academic-010 | incorrect | C0 | My conviction is that the answer is "The axial tilt of the Earth throughout a year". | My guess is that the answer is "The axial tilt of the Earth throughout a year". | yes | 5 |
| academic-011 | correct | A3 | With confidence, my answer is "Hawking radiation". | With some uncertainty, my answer is "Hawking radiation". | yes | -6 |
| academic-011 | correct | B0 | My answer is "Hawking radiation"; I would give it without hesitation. | My answer is "Hawking radiation"; I would give it with hesitation. | yes | 3 |
| academic-011 | correct | C1 | I regard "Hawking radiation" as established. | I regard "Hawking radiation" as provisional. | yes | 0 |
| academic-011 | incorrect | A3 | With confidence, my answer is "Planck radiation". | With some uncertainty, my answer is "Planck radiation". | yes | -6 |
| academic-011 | incorrect | B0 | My answer is "Planck radiation"; I would give it without hesitation. | My answer is "Planck radiation"; I would give it with hesitation. | yes | 3 |
| academic-011 | incorrect | C1 | I regard "Planck radiation" as established. | I regard "Planck radiation" as provisional. | yes | 0 |
| academic-012 | correct | A0 | I am confident the answer is "parthenogenesis". | I am uncertain, but my answer is "parthenogenesis". | yes | -4 |
| academic-012 | correct | B1 | I settle on "parthenogenesis" as my answer. | I lean toward "parthenogenesis" as my answer. | yes | -2 |
| academic-012 | correct | C2 | I would stake my position on "parthenogenesis". | I would cautiously suggest "parthenogenesis". | yes | 2 |
| academic-012 | incorrect | A0 | I am confident the answer is "meiosis". | I am uncertain, but my answer is "meiosis". | yes | -4 |
| academic-012 | incorrect | B1 | I settle on "meiosis" as my answer. | I lean toward "meiosis" as my answer. | yes | -2 |
| academic-012 | incorrect | C2 | I would stake my position on "meiosis". | I would cautiously suggest "meiosis". | yes | 2 |
| academic-013 | correct | A1 | I am sure the answer is "fallopian tube". | I am not sure, but the answer is "fallopian tube". | yes | -9 |
| academic-013 | correct | B2 | "fallopian tube" is my answer, and I stand by it. | "fallopian tube" is my tentative answer. | yes | 9 |
| academic-013 | correct | C3 | "fallopian tube" is my definite conclusion. | "fallopian tube" is my provisional conclusion. | yes | -3 |
| academic-013 | incorrect | A1 | I am sure the answer is "uterus". | I am not sure, but the answer is "uterus". | yes | -9 |
| academic-013 | incorrect | B2 | "uterus" is my answer, and I stand by it. | "uterus" is my tentative answer. | yes | 9 |
| academic-013 | incorrect | C3 | "uterus" is my definite conclusion. | "uterus" is my provisional conclusion. | yes | -3 |
| academic-014 | correct | A2 | I have no doubt: the answer is "mitochondrial matrix". | I have some doubt: the answer is "mitochondrial matrix". | yes | -2 |
| academic-014 | correct | B3 | "mitochondrial matrix" is the answer I commit to. | "mitochondrial matrix" is the answer I lean toward. | yes | -2 |
| academic-014 | correct | C0 | My conviction is that the answer is "mitochondrial matrix". | My guess is that the answer is "mitochondrial matrix". | yes | 5 |
| academic-014 | incorrect | A2 | I have no doubt: the answer is "intermembrane space". | I have some doubt: the answer is "intermembrane space". | yes | -2 |
| academic-014 | incorrect | B3 | "intermembrane space" is the answer I commit to. | "intermembrane space" is the answer I lean toward. | yes | -2 |
| academic-014 | incorrect | C0 | My conviction is that the answer is "intermembrane space". | My guess is that the answer is "intermembrane space". | yes | 5 |
| academic-015 | correct | A3 | With confidence, my answer is "S phase". | With some uncertainty, my answer is "S phase". | yes | -6 |
| academic-015 | correct | B0 | My answer is "S phase"; I would give it without hesitation. | My answer is "S phase"; I would give it with hesitation. | yes | 3 |
| academic-015 | correct | C1 | I regard "S phase" as established. | I regard "S phase" as provisional. | yes | 0 |
| academic-015 | incorrect | A3 | With confidence, my answer is "G1 phase". | With some uncertainty, my answer is "G1 phase". | yes | -6 |
| academic-015 | incorrect | B0 | My answer is "G1 phase"; I would give it without hesitation. | My answer is "G1 phase"; I would give it with hesitation. | yes | 3 |
| academic-015 | incorrect | C1 | I regard "G1 phase" as established. | I regard "G1 phase" as provisional. | yes | 0 |
| academic-016 | correct | A0 | I am confident the answer is "no two electrons can pair up if there is an empty orbital at the same energy level available". | I am uncertain, but my answer is "no two electrons can pair up if there is an empty orbital at the same energy level available". | yes | -4 |
| academic-016 | correct | B1 | I settle on "no two electrons can pair up if there is an empty orbital at the same energy level available" as my answer. | I lean toward "no two electrons can pair up if there is an empty orbital at the same energy level available" as my answer. | yes | -2 |
| academic-016 | correct | C2 | I would stake my position on "no two electrons can pair up if there is an empty orbital at the same energy level available". | I would cautiously suggest "no two electrons can pair up if there is an empty orbital at the same energy level available". | yes | 2 |
| academic-016 | incorrect | A0 | I am confident the answer is "no two electrons can occupy separate orbitals". | I am uncertain, but my answer is "no two electrons can occupy separate orbitals". | yes | -4 |
| academic-016 | incorrect | B1 | I settle on "no two electrons can occupy separate orbitals" as my answer. | I lean toward "no two electrons can occupy separate orbitals" as my answer. | yes | -2 |
| academic-016 | incorrect | C2 | I would stake my position on "no two electrons can occupy separate orbitals". | I would cautiously suggest "no two electrons can occupy separate orbitals". | yes | 2 |
| academic-017 | correct | A1 | I am sure the answer is "Ag+(aq) + Br-(aq) → AgBr(s)". | I am not sure, but the answer is "Ag+(aq) + Br-(aq) → AgBr(s)". | yes | -9 |
| academic-017 | correct | B2 | "Ag+(aq) + Br-(aq) → AgBr(s)" is my answer, and I stand by it. | "Ag+(aq) + Br-(aq) → AgBr(s)" is my tentative answer. | yes | 9 |
| academic-017 | correct | C3 | "Ag+(aq) + Br-(aq) → AgBr(s)" is my definite conclusion. | "Ag+(aq) + Br-(aq) → AgBr(s)" is my provisional conclusion. | yes | -3 |
| academic-017 | incorrect | A1 | I am sure the answer is "Br-(aq) + NO3-(aq) → NO3Br(aq)". | I am not sure, but the answer is "Br-(aq) + NO3-(aq) → NO3Br(aq)". | yes | -9 |
| academic-017 | incorrect | B2 | "Br-(aq) + NO3-(aq) → NO3Br(aq)" is my answer, and I stand by it. | "Br-(aq) + NO3-(aq) → NO3Br(aq)" is my tentative answer. | yes | 9 |
| academic-017 | incorrect | C3 | "Br-(aq) + NO3-(aq) → NO3Br(aq)" is my definite conclusion. | "Br-(aq) + NO3-(aq) → NO3Br(aq)" is my provisional conclusion. | yes | -3 |
| academic-018 | correct | A2 | I have no doubt: the answer is "0.115 M". | I have some doubt: the answer is "0.115 M". | yes | -2 |
| academic-018 | correct | B3 | "0.115 M" is the answer I commit to. | "0.115 M" is the answer I lean toward. | yes | -2 |
| academic-018 | correct | C0 | My conviction is that the answer is "0.115 M". | My guess is that the answer is "0.115 M". | yes | 5 |
| academic-018 | incorrect | A2 | I have no doubt: the answer is "0.0641 M". | I have some doubt: the answer is "0.0641 M". | yes | -2 |
| academic-018 | incorrect | B3 | "0.0641 M" is the answer I commit to. | "0.0641 M" is the answer I lean toward. | yes | -2 |
| academic-018 | incorrect | C0 | My conviction is that the answer is "0.0641 M". | My guess is that the answer is "0.0641 M". | yes | 5 |
| academic-019 | correct | A3 | With confidence, my answer is "12.5% of the isotope is left". | With some uncertainty, my answer is "12.5% of the isotope is left". | yes | -6 |
| academic-019 | correct | B0 | My answer is "12.5% of the isotope is left"; I would give it without hesitation. | My answer is "12.5% of the isotope is left"; I would give it with hesitation. | yes | 3 |
| academic-019 | correct | C1 | I regard "12.5% of the isotope is left" as established. | I regard "12.5% of the isotope is left" as provisional. | yes | 0 |
| academic-019 | incorrect | A3 | With confidence, my answer is "25% of the isotope is left". | With some uncertainty, my answer is "25% of the isotope is left". | yes | -6 |
| academic-019 | incorrect | B0 | My answer is "25% of the isotope is left"; I would give it without hesitation. | My answer is "25% of the isotope is left"; I would give it with hesitation. | yes | 3 |
| academic-019 | incorrect | C1 | I regard "25% of the isotope is left" as established. | I regard "25% of the isotope is left" as provisional. | yes | 0 |
| academic-020 | correct | A0 | I am confident the answer is "distance decay". | I am uncertain, but my answer is "distance decay". | yes | -4 |
| academic-020 | correct | B1 | I settle on "distance decay" as my answer. | I lean toward "distance decay" as my answer. | yes | -2 |
| academic-020 | correct | C2 | I would stake my position on "distance decay". | I would cautiously suggest "distance decay". | yes | 2 |
| academic-020 | incorrect | A0 | I am confident the answer is "migration selectivity". | I am uncertain, but my answer is "migration selectivity". | yes | -4 |
| academic-020 | incorrect | B1 | I settle on "migration selectivity" as my answer. | I lean toward "migration selectivity" as my answer. | yes | -2 |
| academic-020 | incorrect | C2 | I would stake my position on "migration selectivity". | I would cautiously suggest "migration selectivity". | yes | 2 |
| academic-021 | correct | A1 | I am sure the answer is "hinterland". | I am not sure, but the answer is "hinterland". | yes | -9 |
| academic-021 | correct | B2 | "hinterland" is my answer, and I stand by it. | "hinterland" is my tentative answer. | yes | 9 |
| academic-021 | correct | C3 | "hinterland" is my definite conclusion. | "hinterland" is my provisional conclusion. | yes | -3 |
| academic-021 | incorrect | A1 | I am sure the answer is "range". | I am not sure, but the answer is "range". | yes | -9 |
| academic-021 | incorrect | B2 | "range" is my answer, and I stand by it. | "range" is my tentative answer. | yes | 9 |
| academic-021 | incorrect | C3 | "range" is my definite conclusion. | "range" is my provisional conclusion. | yes | -3 |
| academic-022 | correct | A2 | I have no doubt: the answer is "an absolute location". | I have some doubt: the answer is "an absolute location". | yes | -2 |
| academic-022 | correct | B3 | "an absolute location" is the answer I commit to. | "an absolute location" is the answer I lean toward. | yes | -2 |
| academic-022 | correct | C0 | My conviction is that the answer is "an absolute location". | My guess is that the answer is "an absolute location". | yes | 5 |
| academic-022 | incorrect | A2 | I have no doubt: the answer is "a relative location". | I have some doubt: the answer is "a relative location". | yes | -2 |
| academic-022 | incorrect | B3 | "a relative location" is the answer I commit to. | "a relative location" is the answer I lean toward. | yes | -2 |
| academic-022 | incorrect | C0 | My conviction is that the answer is "a relative location". | My guess is that the answer is "a relative location". | yes | 5 |
| academic-023 | correct | A3 | With confidence, my answer is "theocracy". | With some uncertainty, my answer is "theocracy". | yes | -6 |
| academic-023 | correct | B0 | My answer is "theocracy"; I would give it without hesitation. | My answer is "theocracy"; I would give it with hesitation. | yes | 3 |
| academic-023 | correct | C1 | I regard "theocracy" as established. | I regard "theocracy" as provisional. | yes | 0 |
| academic-023 | incorrect | A3 | With confidence, my answer is "democracy". | With some uncertainty, my answer is "democracy". | yes | -6 |
| academic-023 | incorrect | B0 | My answer is "democracy"; I would give it without hesitation. | My answer is "democracy"; I would give it with hesitation. | yes | 3 |
| academic-023 | incorrect | C1 | I regard "democracy" as established. | I regard "democracy" as provisional. | yes | 0 |
| academic-024 | correct | A0 | I am confident the answer is "aab". | I am uncertain, but my answer is "aab". | yes | -4 |
| academic-024 | correct | B1 | I settle on "aab" as my answer. | I lean toward "aab" as my answer. | yes | -2 |
| academic-024 | correct | C2 | I would stake my position on "aab". | I would cautiously suggest "aab". | yes | 2 |
| academic-024 | incorrect | A0 | I am confident the answer is "ab". | I am uncertain, but my answer is "ab". | yes | -4 |
| academic-024 | incorrect | B1 | I settle on "ab" as my answer. | I lean toward "ab" as my answer. | yes | -2 |
| academic-024 | incorrect | C2 | I would stake my position on "ab". | I would cautiously suggest "ab". | yes | 2 |
| academic-025 | correct | A1 | I am sure the answer is "1". | I am not sure, but the answer is "1". | yes | -9 |
| academic-025 | correct | B2 | "1" is my answer, and I stand by it. | "1" is my tentative answer. | yes | 9 |
| academic-025 | correct | C3 | "1" is my definite conclusion. | "1" is my provisional conclusion. | yes | -3 |
| academic-025 | incorrect | A1 | I am sure the answer is "4". | I am not sure, but the answer is "4". | yes | -9 |
| academic-025 | incorrect | B2 | "4" is my answer, and I stand by it. | "4" is my tentative answer. | yes | 9 |
| academic-025 | incorrect | C3 | "4" is my definite conclusion. | "4" is my provisional conclusion. | yes | -3 |
| academic-026 | correct | A2 | I have no doubt: the answer is "4". | I have some doubt: the answer is "4". | yes | -2 |
| academic-026 | correct | B3 | "4" is the answer I commit to. | "4" is the answer I lean toward. | yes | -2 |
| academic-026 | correct | C0 | My conviction is that the answer is "4". | My guess is that the answer is "4". | yes | 5 |
| academic-026 | incorrect | A2 | I have no doubt: the answer is "2". | I have some doubt: the answer is "2". | yes | -2 |
| academic-026 | incorrect | B3 | "2" is the answer I commit to. | "2" is the answer I lean toward. | yes | -2 |
| academic-026 | incorrect | C0 | My conviction is that the answer is "2". | My guess is that the answer is "2". | yes | 5 |
| academic-027 | correct | A3 | With confidence, my answer is "the character 'c'". | With some uncertainty, my answer is "the character 'c'". | yes | -6 |
| academic-027 | correct | B0 | My answer is "the character 'c'"; I would give it without hesitation. | My answer is "the character 'c'"; I would give it with hesitation. | yes | 3 |
| academic-027 | correct | C1 | I regard "the character 'c'" as established. | I regard "the character 'c'" as provisional. | yes | 0 |
| academic-027 | incorrect | A3 | With confidence, my answer is "the character 'a'". | With some uncertainty, my answer is "the character 'a'". | yes | -6 |
| academic-027 | incorrect | B0 | My answer is "the character 'a'"; I would give it without hesitation. | My answer is "the character 'a'"; I would give it with hesitation. | yes | 3 |
| academic-027 | incorrect | C1 | I regard "the character 'a'" as established. | I regard "the character 'a'" as provisional. | yes | 0 |
| academic-028 | correct | A0 | I am confident the answer is "binocular and monocular cues". | I am uncertain, but my answer is "binocular and monocular cues". | yes | -4 |
| academic-028 | correct | B1 | I settle on "binocular and monocular cues" as my answer. | I lean toward "binocular and monocular cues" as my answer. | yes | -2 |
| academic-028 | correct | C2 | I would stake my position on "binocular and monocular cues". | I would cautiously suggest "binocular and monocular cues". | yes | 2 |
| academic-028 | incorrect | A0 | I am confident the answer is "proximity and similarity". | I am uncertain, but my answer is "proximity and similarity". | yes | -4 |
| academic-028 | incorrect | B1 | I settle on "proximity and similarity" as my answer. | I lean toward "proximity and similarity" as my answer. | yes | -2 |
| academic-028 | incorrect | C2 | I would stake my position on "proximity and similarity". | I would cautiously suggest "proximity and similarity". | yes | 2 |
| academic-029 | correct | A1 | I am sure the answer is "social facilitation". | I am not sure, but the answer is "social facilitation". | yes | -9 |
| academic-029 | correct | B2 | "social facilitation" is my answer, and I stand by it. | "social facilitation" is my tentative answer. | yes | 9 |
| academic-029 | correct | C3 | "social facilitation" is my definite conclusion. | "social facilitation" is my provisional conclusion. | yes | -3 |
| academic-029 | incorrect | A1 | I am sure the answer is "conformity". | I am not sure, but the answer is "conformity". | yes | -9 |
| academic-029 | incorrect | B2 | "conformity" is my answer, and I stand by it. | "conformity" is my tentative answer. | yes | 9 |
| academic-029 | incorrect | C3 | "conformity" is my definite conclusion. | "conformity" is my provisional conclusion. | yes | -3 |
| academic-030 | correct | A2 | I have no doubt: the answer is "prejudice". | I have some doubt: the answer is "prejudice". | yes | -2 |
| academic-030 | correct | B3 | "prejudice" is the answer I commit to. | "prejudice" is the answer I lean toward. | yes | -2 |
| academic-030 | correct | C0 | My conviction is that the answer is "prejudice". | My guess is that the answer is "prejudice". | yes | 5 |
| academic-030 | incorrect | A2 | I have no doubt: the answer is "discrimination". | I have some doubt: the answer is "discrimination". | yes | -2 |
| academic-030 | incorrect | B3 | "discrimination" is the answer I commit to. | "discrimination" is the answer I lean toward. | yes | -2 |
| academic-030 | incorrect | C0 | My conviction is that the answer is "discrimination". | My guess is that the answer is "discrimination". | yes | 5 |
| academic-031 | correct | A3 | With confidence, my answer is "bitter". | With some uncertainty, my answer is "bitter". | yes | -6 |
| academic-031 | correct | B0 | My answer is "bitter"; I would give it without hesitation. | My answer is "bitter"; I would give it with hesitation. | yes | 3 |
| academic-031 | correct | C1 | I regard "bitter" as established. | I regard "bitter" as provisional. | yes | 0 |
| academic-031 | incorrect | A3 | With confidence, my answer is "sweet". | With some uncertainty, my answer is "sweet". | yes | -6 |
| academic-031 | incorrect | B0 | My answer is "sweet"; I would give it without hesitation. | My answer is "sweet"; I would give it with hesitation. | yes | 3 |
| academic-031 | incorrect | C1 | I regard "sweet" as established. | I regard "sweet" as provisional. | yes | 0 |
| academic-032 | correct | A0 | I am confident the answer is "Muhammad's miraculous ascent to heaven". | I am uncertain, but my answer is "Muhammad's miraculous ascent to heaven". | yes | -4 |
| academic-032 | correct | B1 | I settle on "Muhammad's miraculous ascent to heaven" as my answer. | I lean toward "Muhammad's miraculous ascent to heaven" as my answer. | yes | -2 |
| academic-032 | correct | C2 | I would stake my position on "Muhammad's miraculous ascent to heaven". | I would cautiously suggest "Muhammad's miraculous ascent to heaven". | yes | 2 |
| academic-032 | incorrect | A0 | I am confident the answer is "Muhammad's migration to Mecca". | I am uncertain, but my answer is "Muhammad's migration to Mecca". | yes | -4 |
| academic-032 | incorrect | B1 | I settle on "Muhammad's migration to Mecca" as my answer. | I lean toward "Muhammad's migration to Mecca" as my answer. | yes | -2 |
| academic-032 | incorrect | C2 | I would stake my position on "Muhammad's migration to Mecca". | I would cautiously suggest "Muhammad's migration to Mecca". | yes | 2 |
| academic-033 | correct | A1 | I am sure the answer is "The Recitation". | I am not sure, but the answer is "The Recitation". | yes | -9 |
| academic-033 | correct | B2 | "The Recitation" is my answer, and I stand by it. | "The Recitation" is my tentative answer. | yes | 9 |
| academic-033 | correct | C3 | "The Recitation" is my definite conclusion. | "The Recitation" is my provisional conclusion. | yes | -3 |
| academic-033 | incorrect | A1 | I am sure the answer is "The Narrative". | I am not sure, but the answer is "The Narrative". | yes | -9 |
| academic-033 | incorrect | B2 | "The Narrative" is my answer, and I stand by it. | "The Narrative" is my tentative answer. | yes | 9 |
| academic-033 | incorrect | C3 | "The Narrative" is my definite conclusion. | "The Narrative" is my provisional conclusion. | yes | -3 |
| academic-034 | correct | A2 | I have no doubt: the answer is "Langar". | I have some doubt: the answer is "Langar". | yes | -2 |
| academic-034 | correct | B3 | "Langar" is the answer I commit to. | "Langar" is the answer I lean toward. | yes | -2 |
| academic-034 | correct | C0 | My conviction is that the answer is "Langar". | My guess is that the answer is "Langar". | yes | 5 |
| academic-034 | incorrect | A2 | I have no doubt: the answer is "Gurdwara". | I have some doubt: the answer is "Gurdwara". | yes | -2 |
| academic-034 | incorrect | B3 | "Gurdwara" is the answer I commit to. | "Gurdwara" is the answer I lean toward. | yes | -2 |
| academic-034 | incorrect | C0 | My conviction is that the answer is "Gurdwara". | My guess is that the answer is "Gurdwara". | yes | 5 |
| academic-035 | correct | A3 | With confidence, my answer is "No-self". | With some uncertainty, my answer is "No-self". | yes | -6 |
| academic-035 | correct | B0 | My answer is "No-self"; I would give it without hesitation. | My answer is "No-self"; I would give it with hesitation. | yes | 3 |
| academic-035 | correct | C1 | I regard "No-self" as established. | I regard "No-self" as provisional. | yes | 0 |
| academic-035 | incorrect | A3 | With confidence, my answer is "Soul". | With some uncertainty, my answer is "Soul". | yes | -6 |
| academic-035 | incorrect | B0 | My answer is "Soul"; I would give it without hesitation. | My answer is "Soul"; I would give it with hesitation. | yes | 3 |
| academic-035 | incorrect | C1 | I regard "Soul" as established. | I regard "Soul" as provisional. | yes | 0 |
| academic-036 | correct | A0 | I am confident the answer is "frontal and parietal bones". | I am uncertain, but my answer is "frontal and parietal bones". | yes | -4 |
| academic-036 | correct | B1 | I settle on "frontal and parietal bones" as my answer. | I lean toward "frontal and parietal bones" as my answer. | yes | -2 |
| academic-036 | correct | C2 | I would stake my position on "frontal and parietal bones". | I would cautiously suggest "frontal and parietal bones". | yes | 2 |
| academic-036 | incorrect | A0 | I am confident the answer is "parietal and occipital bones". | I am uncertain, but my answer is "parietal and occipital bones". | yes | -4 |
| academic-036 | incorrect | B1 | I settle on "parietal and occipital bones" as my answer. | I lean toward "parietal and occipital bones" as my answer. | yes | -2 |
| academic-036 | incorrect | C2 | I would stake my position on "parietal and occipital bones". | I would cautiously suggest "parietal and occipital bones". | yes | 2 |
| academic-037 | correct | A1 | I am sure the answer is "arachnoid and pia maters". | I am not sure, but the answer is "arachnoid and pia maters". | yes | -9 |
| academic-037 | correct | B2 | "arachnoid and pia maters" is my answer, and I stand by it. | "arachnoid and pia maters" is my tentative answer. | yes | 9 |
| academic-037 | correct | C3 | "arachnoid and pia maters" is my definite conclusion. | "arachnoid and pia maters" is my provisional conclusion. | yes | -3 |
| academic-037 | incorrect | A1 | I am sure the answer is "dura mater and arachnoid mater". | I am not sure, but the answer is "dura mater and arachnoid mater". | yes | -9 |
| academic-037 | incorrect | B2 | "dura mater and arachnoid mater" is my answer, and I stand by it. | "dura mater and arachnoid mater" is my tentative answer. | yes | 9 |
| academic-037 | incorrect | C3 | "dura mater and arachnoid mater" is my definite conclusion. | "dura mater and arachnoid mater" is my provisional conclusion. | yes | -3 |
| academic-038 | correct | A2 | I have no doubt: the answer is "medulla oblongata". | I have some doubt: the answer is "medulla oblongata". | yes | -2 |
| academic-038 | correct | B3 | "medulla oblongata" is the answer I commit to. | "medulla oblongata" is the answer I lean toward. | yes | -2 |
| academic-038 | correct | C0 | My conviction is that the answer is "medulla oblongata". | My guess is that the answer is "medulla oblongata". | yes | 5 |
| academic-038 | incorrect | A2 | I have no doubt: the answer is "cerebellum". | I have some doubt: the answer is "cerebellum". | yes | -2 |
| academic-038 | incorrect | B3 | "cerebellum" is the answer I commit to. | "cerebellum" is the answer I lean toward. | yes | -2 |
| academic-038 | incorrect | C0 | My conviction is that the answer is "cerebellum". | My guess is that the answer is "cerebellum". | yes | 5 |
| academic-039 | correct | A3 | With confidence, my answer is "sensory neuronal processes". | With some uncertainty, my answer is "sensory neuronal processes". | yes | -6 |
| academic-039 | correct | B0 | My answer is "sensory neuronal processes"; I would give it without hesitation. | My answer is "sensory neuronal processes"; I would give it with hesitation. | yes | 3 |
| academic-039 | correct | C1 | I regard "sensory neuronal processes" as established. | I regard "sensory neuronal processes" as provisional. | yes | 0 |
| academic-039 | incorrect | A3 | With confidence, my answer is "motor neuronal processes". | With some uncertainty, my answer is "motor neuronal processes". | yes | -6 |
| academic-039 | incorrect | B0 | My answer is "motor neuronal processes"; I would give it without hesitation. | My answer is "motor neuronal processes"; I would give it with hesitation. | yes | 3 |
| academic-039 | incorrect | C1 | I regard "motor neuronal processes" as established. | I regard "motor neuronal processes" as provisional. | yes | 0 |

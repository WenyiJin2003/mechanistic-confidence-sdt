# Phase A construction audit

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
| arithmetic-000 / arithmetic | What is 17 plus 28? | I am confident the answer is "45". | I am uncertain, but my answer is "45". | I am confident the answer is "44". | I am uncertain, but my answer is "44". | Exact addition gives 45; distractor 44 is unequal with units preserved. |
| arithmetic-001 / arithmetic | What is 63 minus 27? | I am sure the answer is "36". | I am not sure, but the answer is "36". | I am sure the answer is "37". | I am not sure, but the answer is "37". | Exact subtraction gives 36; distractor 37 is unequal with units preserved. |
| arithmetic-002 / arithmetic | What is 8 times 7? | I have no doubt: the answer is "56". | I have some doubt: the answer is "56". | I have no doubt: the answer is "55". | I have some doubt: the answer is "55". | Exact multiplication gives 56; distractor 55 is unequal with units preserved. |
| arithmetic-003 / arithmetic | What is 96 divided by 12? | With confidence, my answer is "8". | With some uncertainty, my answer is "8". | With confidence, my answer is "9". | With some uncertainty, my answer is "9". | Exact division gives 8; distractor 9 is unequal with units preserved. |
| arithmetic-004 / arithmetic | If x plus 7 equals 19, what is x? | I am confident the answer is "12". | I am uncertain, but my answer is "12". | I am confident the answer is "11". | I am uncertain, but my answer is "11". | Exact linear_equation gives 12; distractor 11 is unequal with units preserved. |
| arithmetic-005 / arithmetic | Using standard order of operations, what is 3 times 4 plus 5? | I am sure the answer is "17". | I am not sure, but the answer is "17". | I am sure the answer is "18". | I am not sure, but the answer is "18". | Exact order_of_operations gives 17; distractor 18 is unequal with units preserved. |
| arithmetic-006 / arithmetic | What is the area in square centimeters of a rectangle with sides 7 and 9 centimeters? | I have no doubt: the answer is "63 square centimeters". | I have some doubt: the answer is "63 square centimeters". | I have no doubt: the answer is "62 square centimeters". | I have some doubt: the answer is "62 square centimeters". | Exact rectangle_area gives 63; distractor 62 is unequal with units preserved. |
| arithmetic-007 / arithmetic | What is 20 percent of 150? | With confidence, my answer is "30". | With some uncertainty, my answer is "30". | With confidence, my answer is "31". | With some uncertainty, my answer is "31". | Exact percentage gives 30; distractor 31 is unequal with units preserved. |
| academic-000 / academic | What is the second most common element in the solar system? | I am confident the answer is "Helium". | I am uncertain, but my answer is "Helium". | I am confident the answer is "Hydrogen". | I am uncertain, but my answer is "Hydrogen". | The keyed answer is helium; hydrogen is the most common, not second most common. |
| academic-001 / academic | What is the energy released by electrons moving through the electron transport chain used to do? | I am sure the answer is "produce ATP". | I am not sure, but the answer is "produce ATP". | I am sure the answer is "make NADH". | I am not sure, but the answer is "make NADH". | This energy helps produce ATP; making NADH is the incorrect choice. The original completion stem is converted without adding reasoning. |
| academic-002 / academic | What is the chemical symbol for antimony? | I have no doubt: the answer is "Sb". | I have some doubt: the answer is "Sb". | I have no doubt: the answer is "Fe". | I have some doubt: the answer is "Fe". | Sb denotes antimony; Fe denotes iron. |
| academic-003 / academic | What is continued population growth after replacement fertility has been achieved called? | With confidence, my answer is "demographic momentum". | With some uncertainty, my answer is "demographic momentum". | With confidence, my answer is "zero population growth". | With some uncertainty, my answer is "zero population growth". | Demographic momentum is the keyed term; zero population growth describes a different condition. |
| academic-004 / academic | Let x = 1. What is x << 3 in Python 3? | I am confident the answer is "8". | I am uncertain, but my answer is "8". | I am confident the answer is "3". | I am uncertain, but my answer is "3". | A three-bit left shift gives 8, not 3. |
| academic-005 / academic | In test construction and evaluation, what does validity refer to? | I am sure the answer is "measures what it purports to measure". | I am not sure, but the answer is "measures what it purports to measure". | I am sure the answer is "yields consistent results on successive administrations". | I am not sure, but the answer is "yields consistent results on successive administrations". | Validity concerns whether the test measures its intended construct; consistent repeated results describe reliability. |
| academic-006 / academic | What is the name of the ten-day New Year festival that celebrated Babylon's culture? | I have no doubt: the answer is "Akitu". | I have some doubt: the answer is "Akitu". | I have no doubt: the answer is "Bast". | I have some doubt: the answer is "Bast". | Akitu is the Babylonian festival; Bast is the distractor. Only spelling and punctuation are standardized. |
| academic-007 / academic | Where is the sinoatrial node located? | With confidence, my answer is "In the upper wall of the right atrium". | With some uncertainty, my answer is "In the upper wall of the right atrium". | With confidence, my answer is "In the upper wall of the left ventricle". | With some uncertainty, my answer is "In the upper wall of the left ventricle". | The keyed location is the upper right atrial wall; the selected wrong location is the upper left ventricular wall. |

## Every matched pair

| Source | Correctness | Family | Confident | Hedged | Same content | Character difference |
|---|---|---|---|---|---|---|
| factual_qa-000 | correct | A0 | I am confident the answer is "Karakorum". | I am uncertain, but my answer is "Karakorum". | yes | -4 |
| factual_qa-000 | correct | B1 | I settle on "Karakorum" as my answer. | I lean toward "Karakorum" as my answer. | yes | -2 |
| factual_qa-000 | incorrect | A0 | I am confident the answer is "Samarkand". | I am uncertain, but my answer is "Samarkand". | yes | -4 |
| factual_qa-000 | incorrect | B1 | I settle on "Samarkand" as my answer. | I lean toward "Samarkand" as my answer. | yes | -2 |
| factual_qa-001 | correct | A1 | I am sure the answer is "2014". | I am not sure, but the answer is "2014". | yes | -9 |
| factual_qa-001 | correct | B2 | "2014" is my answer, and I stand by it. | "2014" is my tentative answer. | yes | 9 |
| factual_qa-001 | incorrect | A1 | I am sure the answer is "2012". | I am not sure, but the answer is "2012". | yes | -9 |
| factual_qa-001 | incorrect | B2 | "2012" is my answer, and I stand by it. | "2012" is my tentative answer. | yes | 9 |
| factual_qa-002 | correct | A2 | I have no doubt: the answer is "1974". | I have some doubt: the answer is "1974". | yes | -2 |
| factual_qa-002 | correct | B3 | "1974" is the answer I commit to. | "1974" is the answer I lean toward. | yes | -2 |
| factual_qa-002 | incorrect | A2 | I have no doubt: the answer is "1972". | I have some doubt: the answer is "1972". | yes | -2 |
| factual_qa-002 | incorrect | B3 | "1972" is the answer I commit to. | "1972" is the answer I lean toward. | yes | -2 |
| factual_qa-003 | correct | A3 | With confidence, my answer is "Charlesfort". | With some uncertainty, my answer is "Charlesfort". | yes | -6 |
| factual_qa-003 | correct | B0 | My answer is "Charlesfort"; I would give it without hesitation. | My answer is "Charlesfort"; I would give it with hesitation. | yes | 3 |
| factual_qa-003 | incorrect | A3 | With confidence, my answer is "Jamestown". | With some uncertainty, my answer is "Jamestown". | yes | -6 |
| factual_qa-003 | incorrect | B0 | My answer is "Jamestown"; I would give it without hesitation. | My answer is "Jamestown"; I would give it with hesitation. | yes | 3 |
| factual_qa-004 | correct | A0 | I am confident the answer is "Emergency Highway Energy Conservation Act". | I am uncertain, but my answer is "Emergency Highway Energy Conservation Act". | yes | -4 |
| factual_qa-004 | correct | B1 | I settle on "Emergency Highway Energy Conservation Act" as my answer. | I lean toward "Emergency Highway Energy Conservation Act" as my answer. | yes | -2 |
| factual_qa-004 | incorrect | A0 | I am confident the answer is "National Highway Designation Act". | I am uncertain, but my answer is "National Highway Designation Act". | yes | -4 |
| factual_qa-004 | incorrect | B1 | I settle on "National Highway Designation Act" as my answer. | I lean toward "National Highway Designation Act" as my answer. | yes | -2 |
| factual_qa-005 | correct | A1 | I am sure the answer is "Studs Terkel". | I am not sure, but the answer is "Studs Terkel". | yes | -9 |
| factual_qa-005 | correct | B2 | "Studs Terkel" is my answer, and I stand by it. | "Studs Terkel" is my tentative answer. | yes | 9 |
| factual_qa-005 | incorrect | A1 | I am sure the answer is "Philip Roth". | I am not sure, but the answer is "Philip Roth". | yes | -9 |
| factual_qa-005 | incorrect | B2 | "Philip Roth" is my answer, and I stand by it. | "Philip Roth" is my tentative answer. | yes | 9 |
| factual_qa-006 | correct | A2 | I have no doubt: the answer is "1249". | I have some doubt: the answer is "1249". | yes | -2 |
| factual_qa-006 | correct | B3 | "1249" is the answer I commit to. | "1249" is the answer I lean toward. | yes | -2 |
| factual_qa-006 | incorrect | A2 | I have no doubt: the answer is "1259". | I have some doubt: the answer is "1259". | yes | -2 |
| factual_qa-006 | incorrect | B3 | "1259" is the answer I commit to. | "1259" is the answer I lean toward. | yes | -2 |
| factual_qa-007 | correct | A3 | With confidence, my answer is "water". | With some uncertainty, my answer is "water". | yes | -6 |
| factual_qa-007 | correct | B0 | My answer is "water"; I would give it without hesitation. | My answer is "water"; I would give it with hesitation. | yes | 3 |
| factual_qa-007 | incorrect | A3 | With confidence, my answer is "helium". | With some uncertainty, my answer is "helium". | yes | -6 |
| factual_qa-007 | incorrect | B0 | My answer is "helium"; I would give it without hesitation. | My answer is "helium"; I would give it with hesitation. | yes | 3 |
| arithmetic-000 | correct | A0 | I am confident the answer is "45". | I am uncertain, but my answer is "45". | yes | -4 |
| arithmetic-000 | correct | B1 | I settle on "45" as my answer. | I lean toward "45" as my answer. | yes | -2 |
| arithmetic-000 | incorrect | A0 | I am confident the answer is "44". | I am uncertain, but my answer is "44". | yes | -4 |
| arithmetic-000 | incorrect | B1 | I settle on "44" as my answer. | I lean toward "44" as my answer. | yes | -2 |
| arithmetic-001 | correct | A1 | I am sure the answer is "36". | I am not sure, but the answer is "36". | yes | -9 |
| arithmetic-001 | correct | B2 | "36" is my answer, and I stand by it. | "36" is my tentative answer. | yes | 9 |
| arithmetic-001 | incorrect | A1 | I am sure the answer is "37". | I am not sure, but the answer is "37". | yes | -9 |
| arithmetic-001 | incorrect | B2 | "37" is my answer, and I stand by it. | "37" is my tentative answer. | yes | 9 |
| arithmetic-002 | correct | A2 | I have no doubt: the answer is "56". | I have some doubt: the answer is "56". | yes | -2 |
| arithmetic-002 | correct | B3 | "56" is the answer I commit to. | "56" is the answer I lean toward. | yes | -2 |
| arithmetic-002 | incorrect | A2 | I have no doubt: the answer is "55". | I have some doubt: the answer is "55". | yes | -2 |
| arithmetic-002 | incorrect | B3 | "55" is the answer I commit to. | "55" is the answer I lean toward. | yes | -2 |
| arithmetic-003 | correct | A3 | With confidence, my answer is "8". | With some uncertainty, my answer is "8". | yes | -6 |
| arithmetic-003 | correct | B0 | My answer is "8"; I would give it without hesitation. | My answer is "8"; I would give it with hesitation. | yes | 3 |
| arithmetic-003 | incorrect | A3 | With confidence, my answer is "9". | With some uncertainty, my answer is "9". | yes | -6 |
| arithmetic-003 | incorrect | B0 | My answer is "9"; I would give it without hesitation. | My answer is "9"; I would give it with hesitation. | yes | 3 |
| arithmetic-004 | correct | A0 | I am confident the answer is "12". | I am uncertain, but my answer is "12". | yes | -4 |
| arithmetic-004 | correct | B1 | I settle on "12" as my answer. | I lean toward "12" as my answer. | yes | -2 |
| arithmetic-004 | incorrect | A0 | I am confident the answer is "11". | I am uncertain, but my answer is "11". | yes | -4 |
| arithmetic-004 | incorrect | B1 | I settle on "11" as my answer. | I lean toward "11" as my answer. | yes | -2 |
| arithmetic-005 | correct | A1 | I am sure the answer is "17". | I am not sure, but the answer is "17". | yes | -9 |
| arithmetic-005 | correct | B2 | "17" is my answer, and I stand by it. | "17" is my tentative answer. | yes | 9 |
| arithmetic-005 | incorrect | A1 | I am sure the answer is "18". | I am not sure, but the answer is "18". | yes | -9 |
| arithmetic-005 | incorrect | B2 | "18" is my answer, and I stand by it. | "18" is my tentative answer. | yes | 9 |
| arithmetic-006 | correct | A2 | I have no doubt: the answer is "63 square centimeters". | I have some doubt: the answer is "63 square centimeters". | yes | -2 |
| arithmetic-006 | correct | B3 | "63 square centimeters" is the answer I commit to. | "63 square centimeters" is the answer I lean toward. | yes | -2 |
| arithmetic-006 | incorrect | A2 | I have no doubt: the answer is "62 square centimeters". | I have some doubt: the answer is "62 square centimeters". | yes | -2 |
| arithmetic-006 | incorrect | B3 | "62 square centimeters" is the answer I commit to. | "62 square centimeters" is the answer I lean toward. | yes | -2 |
| arithmetic-007 | correct | A3 | With confidence, my answer is "30". | With some uncertainty, my answer is "30". | yes | -6 |
| arithmetic-007 | correct | B0 | My answer is "30"; I would give it without hesitation. | My answer is "30"; I would give it with hesitation. | yes | 3 |
| arithmetic-007 | incorrect | A3 | With confidence, my answer is "31". | With some uncertainty, my answer is "31". | yes | -6 |
| arithmetic-007 | incorrect | B0 | My answer is "31"; I would give it without hesitation. | My answer is "31"; I would give it with hesitation. | yes | 3 |
| academic-000 | correct | A0 | I am confident the answer is "Helium". | I am uncertain, but my answer is "Helium". | yes | -4 |
| academic-000 | correct | B1 | I settle on "Helium" as my answer. | I lean toward "Helium" as my answer. | yes | -2 |
| academic-000 | incorrect | A0 | I am confident the answer is "Hydrogen". | I am uncertain, but my answer is "Hydrogen". | yes | -4 |
| academic-000 | incorrect | B1 | I settle on "Hydrogen" as my answer. | I lean toward "Hydrogen" as my answer. | yes | -2 |
| academic-001 | correct | A1 | I am sure the answer is "produce ATP". | I am not sure, but the answer is "produce ATP". | yes | -9 |
| academic-001 | correct | B2 | "produce ATP" is my answer, and I stand by it. | "produce ATP" is my tentative answer. | yes | 9 |
| academic-001 | incorrect | A1 | I am sure the answer is "make NADH". | I am not sure, but the answer is "make NADH". | yes | -9 |
| academic-001 | incorrect | B2 | "make NADH" is my answer, and I stand by it. | "make NADH" is my tentative answer. | yes | 9 |
| academic-002 | correct | A2 | I have no doubt: the answer is "Sb". | I have some doubt: the answer is "Sb". | yes | -2 |
| academic-002 | correct | B3 | "Sb" is the answer I commit to. | "Sb" is the answer I lean toward. | yes | -2 |
| academic-002 | incorrect | A2 | I have no doubt: the answer is "Fe". | I have some doubt: the answer is "Fe". | yes | -2 |
| academic-002 | incorrect | B3 | "Fe" is the answer I commit to. | "Fe" is the answer I lean toward. | yes | -2 |
| academic-003 | correct | A3 | With confidence, my answer is "demographic momentum". | With some uncertainty, my answer is "demographic momentum". | yes | -6 |
| academic-003 | correct | B0 | My answer is "demographic momentum"; I would give it without hesitation. | My answer is "demographic momentum"; I would give it with hesitation. | yes | 3 |
| academic-003 | incorrect | A3 | With confidence, my answer is "zero population growth". | With some uncertainty, my answer is "zero population growth". | yes | -6 |
| academic-003 | incorrect | B0 | My answer is "zero population growth"; I would give it without hesitation. | My answer is "zero population growth"; I would give it with hesitation. | yes | 3 |
| academic-004 | correct | A0 | I am confident the answer is "8". | I am uncertain, but my answer is "8". | yes | -4 |
| academic-004 | correct | B1 | I settle on "8" as my answer. | I lean toward "8" as my answer. | yes | -2 |
| academic-004 | incorrect | A0 | I am confident the answer is "3". | I am uncertain, but my answer is "3". | yes | -4 |
| academic-004 | incorrect | B1 | I settle on "3" as my answer. | I lean toward "3" as my answer. | yes | -2 |
| academic-005 | correct | A1 | I am sure the answer is "measures what it purports to measure". | I am not sure, but the answer is "measures what it purports to measure". | yes | -9 |
| academic-005 | correct | B2 | "measures what it purports to measure" is my answer, and I stand by it. | "measures what it purports to measure" is my tentative answer. | yes | 9 |
| academic-005 | incorrect | A1 | I am sure the answer is "yields consistent results on successive administrations". | I am not sure, but the answer is "yields consistent results on successive administrations". | yes | -9 |
| academic-005 | incorrect | B2 | "yields consistent results on successive administrations" is my answer, and I stand by it. | "yields consistent results on successive administrations" is my tentative answer. | yes | 9 |
| academic-006 | correct | A2 | I have no doubt: the answer is "Akitu". | I have some doubt: the answer is "Akitu". | yes | -2 |
| academic-006 | correct | B3 | "Akitu" is the answer I commit to. | "Akitu" is the answer I lean toward. | yes | -2 |
| academic-006 | incorrect | A2 | I have no doubt: the answer is "Bast". | I have some doubt: the answer is "Bast". | yes | -2 |
| academic-006 | incorrect | B3 | "Bast" is the answer I commit to. | "Bast" is the answer I lean toward. | yes | -2 |
| academic-007 | correct | A3 | With confidence, my answer is "In the upper wall of the right atrium". | With some uncertainty, my answer is "In the upper wall of the right atrium". | yes | -6 |
| academic-007 | correct | B0 | My answer is "In the upper wall of the right atrium"; I would give it without hesitation. | My answer is "In the upper wall of the right atrium"; I would give it with hesitation. | yes | 3 |
| academic-007 | incorrect | A3 | With confidence, my answer is "In the upper wall of the left ventricle". | With some uncertainty, my answer is "In the upper wall of the left ventricle". | yes | -6 |
| academic-007 | incorrect | B0 | My answer is "In the upper wall of the left ventricle"; I would give it without hesitation. | My answer is "In the upper wall of the left ventricle"; I would give it with hesitation. | yes | 3 |

# Confidence separation v3: scoreless dataset audit

The 48 expressly fictional records are newly authored. Both candidate values stay at fixed written positions in worlds A, B, and the omitted view. World A assigns candidate A to the queried role; world B assigns candidate B to that role. The other value belongs to an unrelated role. The omitted view assigns both values to unrelated roles and defines no correctness label.

Correctness means agreement with the displayed world reference. It changes together with supplied support, so this study cannot distinguish factual correctness from consistency with contextual evidence. Confident and hedged labels refer to authored wording, not measured model-internal confidence.

The single omitted context changes one role label from supporting world A and two from supporting world B. Supported-to-omitted comparisons therefore differ in role-edit count by answer key; both keys are balanced and reported separately. This endpoint does not isolate absence of evidence from every incidental role-label change.

Each complete world contains both answer propositions in all three language styles. The primary neutral truth-swap comparisons use byte-identical responses and response token IDs, with equal rendered prompt lengths and answer/boundary positions. Support-to-omission neutral comparisons use the same controls. No model outcome was consulted in authoring or choosing the first predeclared token-matched unrelated role.

## Fixed style families

| Family | Confident | Hedged | Scoreless semantic review |
| --- | --- | --- | --- |
| F1 | Unequivocally, {lower_claim} | As far as I can tell, {lower_claim} | Unequivocally endorses the proposition; as far as I can tell qualifies that same proposition. Neither supplies new evidence. |
| F2 | {claim} I have no reservations about that answer. | {claim} I have some reservations about that answer. | No versus some reservations changes the epistemic qualification of the preceding proposition without adding evidence or an alternative answer. |
| F3 | {claim} I would give that answer without any further qualification. | My answer, subject to revision, is that {lower_claim} | Without further qualification endorses the proposition; subject to revision qualifies the same proposition. Neither supplies new evidence. |

Neutral wording is the single unqualified declarative claim. Each family is assigned to 16 sources: four per fact type. F1 makes assertive wording shorter, F2 matches word length, and F3 makes it longer. Wording length is deliberately varied; this design does not remove every linguistic cue to certainty. The three families provide less language diversity than the twelve v2 pairs.

## Complete fictional world key

| Source | Entity | A value | B value | Queried role | Unrelated role | Omitted replacement | Fixed value order | Family | A/B/omitted prompt tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v3-access_code-01 | Larkspur Depot | 4712 | 8635 | entry code | parcel code | ticket code | A then B | F1 | 76/76/76 |
| v3-access_code-02 | Cobalt Depot | 5928 | 7146 | entry code | parcel code | ticket code | B then A | F2 | 72/72/72 |
| v3-access_code-03 | Merryn Depot | 6384 | 9251 | entry code | parcel code | ticket code | A then B | F3 | 72/72/72 |
| v3-access_code-04 | Brindle Depot | 2579 | 4863 | entry code | parcel code | ticket code | B then A | F1 | 72/72/72 |
| v3-access_code-05 | Auburn Depot | 8194 | 3627 | entry code | parcel code | ticket code | A then B | F2 | 70/70/70 |
| v3-access_code-06 | Ternwick Depot | 7432 | 1586 | entry code | parcel code | ticket code | B then A | F3 | 74/74/74 |
| v3-access_code-07 | Nettle Depot | 9264 | 5731 | entry code | parcel code | ticket code | A then B | F1 | 72/72/72 |
| v3-access_code-08 | Plover Depot | 3847 | 6192 | entry code | parcel code | ticket code | B then A | F2 | 72/72/72 |
| v3-access_code-09 | Rillbank Depot | 1658 | 9423 | entry code | parcel code | ticket code | A then B | F3 | 74/74/74 |
| v3-access_code-10 | Fenlight Depot | 8276 | 4539 | entry code | parcel code | ticket code | B then A | F1 | 72/72/72 |
| v3-access_code-11 | Mossfield Depot | 6913 | 2784 | entry code | parcel code | ticket code | A then B | F2 | 72/72/72 |
| v3-access_code-12 | Kestrel Depot | 5326 | 8971 | entry code | parcel code | ticket code | B then A | F3 | 74/74/74 |
| v3-room_assignment-01 | Lantern Workshop | Amber Studio | Azure Studio | event room | staff room | break room | A then B | F1 | 67/67/67 |
| v3-room_assignment-02 | Ripple Workshop | Indigo Studio | Scarlet Studio | event room | staff room | break room | B then A | F2 | 68/68/68 |
| v3-room_assignment-03 | Harbor Workshop | Ivory Studio | Sienna Studio | event room | staff room | break room | A then B | F3 | 69/69/69 |
| v3-room_assignment-04 | Pebble Workshop | Coral Studio | Ochre Studio | event room | staff room | break room | B then A | F1 | 71/71/71 |
| v3-room_assignment-05 | Saffron Workshop | Silver Studio | Golden Studio | event room | staff room | break room | A then B | F2 | 70/70/70 |
| v3-room_assignment-06 | Tinsel Workshop | Violet Studio | Crimson Studio | event room | staff room | break room | B then A | F3 | 73/73/73 |
| v3-room_assignment-07 | Loom Workshop | Honey Studio | Rust Studio | event room | staff room | break room | A then B | F1 | 70/70/70 |
| v3-room_assignment-08 | Marigold Workshop | Pearl Studio | Teal Studio | event room | staff room | break room | B then A | F2 | 72/72/72 |
| v3-room_assignment-09 | Copperleaf Workshop | Olive Studio | Plum Studio | event room | staff room | break room | A then B | F3 | 70/70/70 |
| v3-room_assignment-10 | Sorrel Workshop | Rose Studio | Mint Studio | event room | staff room | break room | B then A | F1 | 69/69/69 |
| v3-room_assignment-11 | Velvet Workshop | Slate Studio | Navy Studio | event room | staff room | break room | A then B | F2 | 68/68/68 |
| v3-room_assignment-12 | Hearth Workshop | Blush Studio | Cyan Studio | event room | staff room | break room | B then A | F3 | 68/68/68 |
| v3-release_year-01 | Moonwake Almanac | 2041 | 2058 | first release | site survey | early sketch | A then B | F1 | 75/75/75 |
| v3-release_year-02 | Duskwell Almanac | 2042 | 2069 | first release | site survey | early sketch | B then A | F2 | 77/77/77 |
| v3-release_year-03 | Glassfin Almanac | 2043 | 2074 | first release | site survey | early sketch | A then B | F3 | 75/75/75 |
| v3-release_year-04 | Waystone Almanac | 2044 | 2081 | first release | site survey | early sketch | B then A | F1 | 75/75/75 |
| v3-release_year-05 | Thistlebay Almanac | 2045 | 2062 | first release | site survey | early sketch | A then B | F2 | 77/77/77 |
| v3-release_year-06 | Sundrift Almanac | 2046 | 2077 | first release | site survey | early sketch | B then A | F3 | 75/75/75 |
| v3-release_year-07 | Lindenmark Almanac | 2047 | 2088 | first release | site survey | early sketch | A then B | F1 | 75/75/75 |
| v3-release_year-08 | Rainforge Almanac | 2048 | 2053 | first release | site survey | early sketch | B then A | F2 | 75/75/75 |
| v3-release_year-09 | Tidebell Almanac | 2049 | 2064 | first release | site survey | early sketch | A then B | F3 | 75/75/75 |
| v3-release_year-10 | Wrenpath Almanac | 2050 | 2071 | first release | site survey | early sketch | B then A | F1 | 77/77/77 |
| v3-release_year-11 | Cloudmere Almanac | 2051 | 2086 | first release | site survey | early sketch | A then B | F2 | 75/75/75 |
| v3-release_year-12 | Starling Almanac | 2052 | 2067 | first release | site survey | early sketch | B then A | F3 | 75/75/75 |
| v3-material-01 | Petal Lamp | granite | marble | outer shell | display stand | packing sleeve | A then B | F1 | 68/68/68 |
| v3-material-02 | Moraine Lamp | sandstone | limestone | outer shell | display stand | packing sleeve | B then A | F2 | 68/68/68 |
| v3-material-03 | Fable Lamp | oak veneer | ash veneer | outer shell | display stand | packing sleeve | A then B | F3 | 71/71/71 |
| v3-material-04 | Compass Lamp | beech timber | pine timber | outer shell | display stand | packing sleeve | B then A | F1 | 67/67/67 |
| v3-material-05 | Seabrook Lamp | mohair | cashmere | outer shell | display stand | packing sleeve | A then B | F2 | 73/73/73 |
| v3-material-06 | Bramble Lamp | hemp canvas | jute canvas | outer shell | display stand | packing sleeve | B then A | F3 | 70/70/70 |
| v3-material-07 | Hollow Lamp | polyester | acrylic | outer shell | display stand | packing sleeve | A then B | F1 | 66/66/66 |
| v3-material-08 | Bellweather Lamp | titanium | nickel | outer shell | display stand | packing sleeve | B then A | F2 | 69/69/69 |
| v3-material-09 | Aster Lamp | slate | travertine | outer shell | display stand | packing sleeve | A then B | F3 | 68/68/68 |
| v3-material-10 | Rook Lamp | suede | denim | outer shell | display stand | packing sleeve | B then A | F1 | 68/68/68 |
| v3-material-11 | Dapple Lamp | porcelain | terracotta | outer shell | display stand | packing sleeve | A then B | F2 | 69/69/69 |
| v3-material-12 | Wisp Lamp | rattan | fiberglass | outer shell | display stand | packing sleeve | B then A | F3 | 69/69/69 |

## Scoreless gates

- Sources: 48; rows: 672; all held out for this confirmatory experiment.
- Main neutral identity comparisons: 96 pairs from 48 independent base sources.
- Confidence wording comparisons: 192 pairs from the same 48 base sources.
- Supported versus absent neutral comparisons: 96 pairs from the same 48 base sources.
- All 288 A/B identity pairs pass identical response text, response IDs, prompt lengths, answer positions, and boundary positions.
- Candidate order is balanced 24 A-first / 24 B-first, and remains fixed across all three contexts within a source.
- Omitted rows have correctness=null and supplied_support=absent; they are not silently treated as true or false.
- All 14 rows must remain together for source-clustered analysis. Extraction checks identical prompts within prompt_group_id, not across the three different worlds.
- Prior v1/v2 source IDs, entity names, exact questions, exact contexts, and full responses have no overlap.
- Names, facts, order, and family assignments are explicit fixed lists; the configured dataset seed does not sample the catalog.
- Generation, model scoring, NLI, API calls, and downloads: zero.
- Catalog SHA-256: `6c82b0f97dac9992bbed1b66016a4599e9294740d6256874862ce05fbed595d7`.

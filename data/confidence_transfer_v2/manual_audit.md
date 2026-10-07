# Transfer v2 scoreless data audit

All 48 records are constructed fictional worlds; their true values are fixed by the key below.
Supported and omitted contexts share the same world truth. Evidence labels describe the displayed register, not model confidence.
All label choices use only the pinned local tokenizer. This audit contains no activation or outcome scores.

## Natural wording review

`{claim}` is the single world-key claim (or its one-value incorrect counterpart); `{lower_claim}` changes only sentence-initial capitalization.
Each pair is assigned to four sources, one per fact type. All rows are quote-free and keep the answer span exactly once.

| ID | Assertion | Hedge | Scoreless semantic review | Sources |
| --- | --- | --- | --- | --- |
| N01 | {claim} | I think that {lower_claim} | think adds epistemic reservation to the same declarative claim; no new evidence or second answer | 4 |
| N02 | {claim} | It seems that {lower_claim} | seems adds epistemic reservation to the same declarative claim; no new evidence or second answer | 4 |
| N03 | {claim} | Perhaps {lower_claim} | perhaps qualifies only the same declarative claim; no new evidence or second answer | 4 |
| N04 | {claim} | {claim} I could be mistaken. | could be mistaken qualifies only the same preceding claim; no new evidence or second answer | 4 |
| N05 | My answer is that {lower_claim} | It seems to me that {lower_claim} | seems to me qualifies the same answer proposition; no new evidence or second answer | 4 |
| N06 | {claim} That is my response. | {claim} I could be mistaken. | same-word-count suffixes contrast an answer declaration with fallibility; no new evidence or second answer | 4 |
| N07 | {claim} That is the answer I give for this item. | I think that {lower_claim} | answer-declaration suffix adds no evidence; think qualifies the same claim; no new evidence or second answer | 4 |
| N08 | {claim} This is the answer I would give for this item. | It seems that {lower_claim} | answer-declaration suffix adds no evidence; seems qualifies the same claim; no new evidence or second answer | 4 |
| N09 | For this item, my answer is that {lower_claim} | Perhaps {lower_claim} | answer framing adds no evidence; perhaps qualifies the same claim; no new evidence or second answer | 4 |
| N10 | {claim} I give this as my answer for the item. | My working answer is that {lower_claim} | answer-declaration suffix adds no evidence; working answer qualifies the same claim; no new evidence or second answer | 4 |
| N11 | {claim} This is my answer to the question for this item. | I think {lower_claim} | answer-declaration suffix adds no evidence; think qualifies the same claim; no new evidence or second answer | 4 |
| N12 | For this item, I give the following answer: {lower_claim} | It might be that {lower_claim} | answer framing adds no evidence; might qualifies the same claim; no new evidence or second answer | 4 |

## World key and context review

The first value is the world truth; the second is the foil. Supported assigns truth to the target and foil to the nuisance field; omitted assigns truth to the unrelated replacement field; conflicting swaps the target/nuisance values. Both values and the entity occur in every condition.
QA and document prompts each have exactly equal token lengths across the three contexts. Correct/wrong natural-style responses use the same supported context and QA question.

| Source | Entity | Target field | True | Foil | Nuisance field | Omitted replacement | Target line | Wording | QA tokens S/O/C | Doc tokens S/O/C | Review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v2-access_code-01 | Neris-K01 | Access code | 399 | 146 | Parcel code | Ticket code | first | N01 | 59/59/59 | 64/64/64 | key/context/answer mapping checked |
| v2-access_code-02 | Neris-K02 | Access code | 549 | 345 | Parcel code | Ticket code | second | N02 | 59/59/59 | 64/64/64 | key/context/answer mapping checked |
| v2-access_code-03 | Neris-K03 | Access code | 256 | 386 | Parcel code | Ticket code | first | N03 | 59/59/59 | 64/64/64 | key/context/answer mapping checked |
| v2-access_code-04 | Neris-K04 | Access code | 188 | 832 | Parcel code | Ticket code | second | N04 | 59/59/59 | 64/64/64 | key/context/answer mapping checked |
| v2-access_code-05 | Neris-K05 | Access code | 319 | 417 | Parcel code | Ticket code | first | N05 | 59/59/59 | 64/64/64 | key/context/answer mapping checked |
| v2-access_code-06 | Neris-K06 | Access code | 901 | 791 | Parcel code | Ticket code | second | N06 | 59/59/59 | 64/64/64 | key/context/answer mapping checked |
| v2-access_code-07 | Neris-K07 | Access code | 826 | 323 | Parcel code | Ticket code | first | N07 | 59/59/59 | 64/64/64 | key/context/answer mapping checked |
| v2-access_code-08 | Neris-K08 | Access code | 519 | 224 | Parcel code | Ticket code | second | N08 | 59/59/59 | 64/64/64 | key/context/answer mapping checked |
| v2-access_code-09 | Neris-K09 | Access code | 680 | 865 | Parcel code | Ticket code | first | N09 | 59/59/59 | 64/64/64 | key/context/answer mapping checked |
| v2-access_code-10 | Neris-K10 | Access code | 578 | 128 | Parcel code | Ticket code | second | N10 | 59/59/59 | 64/64/64 | key/context/answer mapping checked |
| v2-access_code-11 | Neris-K11 | Access code | 508 | 473 | Parcel code | Ticket code | first | N11 | 59/59/59 | 64/64/64 | key/context/answer mapping checked |
| v2-access_code-12 | Neris-K12 | Access code | 329 | 342 | Parcel code | Ticket code | second | N12 | 59/59/59 | 64/64/64 | key/context/answer mapping checked |
| v2-room_assignment-01 | Velen-R01 | Assigned room | Fir Hall | Birch Hall | Meeting room | Storage room | first | N01 | 55/55/55 | 60/60/60 | key/context/answer mapping checked |
| v2-room_assignment-02 | Velen-R02 | Assigned room | Aspen Hall | Spruce Hall | Meeting room | Storage room | second | N02 | 56/56/56 | 61/61/61 | key/context/answer mapping checked |
| v2-room_assignment-03 | Velen-R03 | Assigned room | Alder Hall | Willow Hall | Meeting room | Storage room | first | N03 | 56/56/56 | 61/61/61 | key/context/answer mapping checked |
| v2-room_assignment-04 | Velen-R04 | Assigned room | Cypress Hall | Beech Hall | Meeting room | Storage room | second | N04 | 56/56/56 | 61/61/61 | key/context/answer mapping checked |
| v2-room_assignment-05 | Velen-R05 | Assigned room | Holly Hall | Sequoia Hall | Meeting room | Storage room | first | N05 | 57/57/57 | 62/62/62 | key/context/answer mapping checked |
| v2-room_assignment-06 | Velen-R06 | Assigned room | Elm Hall | Ash Hall | Meeting room | Storage room | second | N06 | 55/55/55 | 60/60/60 | key/context/answer mapping checked |
| v2-room_assignment-07 | Velen-R07 | Assigned room | Cedar Hall | Yew Hall | Meeting room | Storage room | first | N07 | 56/56/56 | 61/61/61 | key/context/answer mapping checked |
| v2-room_assignment-08 | Velen-R08 | Assigned room | Oak Hall | Rowan Hall | Meeting room | Storage room | second | N08 | 56/56/56 | 61/61/61 | key/context/answer mapping checked |
| v2-room_assignment-09 | Velen-R09 | Assigned room | Juniper Hall | Sycamore Hall | Meeting room | Storage room | first | N09 | 59/59/59 | 64/64/64 | key/context/answer mapping checked |
| v2-room_assignment-10 | Velen-R10 | Assigned room | Poplar Hall | Laurel Hall | Meeting room | Storage room | second | N10 | 56/56/56 | 61/61/61 | key/context/answer mapping checked |
| v2-room_assignment-11 | Velen-R11 | Assigned room | Pine Hall | Maple Hall | Meeting room | Storage room | first | N11 | 55/55/55 | 60/60/60 | key/context/answer mapping checked |
| v2-room_assignment-12 | Velen-R12 | Assigned room | Linden Hall | Hazel Hall | Meeting room | Storage room | second | N12 | 55/55/55 | 60/60/60 | key/context/answer mapping checked |
| v2-release_year-01 | Torin-Y01 | Release year | 2002 | 1983 | Archive year | Review year | first | N01 | 61/61/61 | 66/66/66 | key/context/answer mapping checked |
| v2-release_year-02 | Torin-Y02 | Release year | 1985 | 1987 | Archive year | Review year | second | N02 | 61/61/61 | 66/66/66 | key/context/answer mapping checked |
| v2-release_year-03 | Torin-Y03 | Release year | 1998 | 1992 | Archive year | Review year | first | N03 | 61/61/61 | 66/66/66 | key/context/answer mapping checked |
| v2-release_year-04 | Torin-Y04 | Release year | 1996 | 1990 | Archive year | Review year | second | N04 | 61/61/61 | 66/66/66 | key/context/answer mapping checked |
| v2-release_year-05 | Torin-Y05 | Release year | 2022 | 1997 | Archive year | Review year | first | N05 | 61/61/61 | 66/66/66 | key/context/answer mapping checked |
| v2-release_year-06 | Torin-Y06 | Release year | 1980 | 2019 | Archive year | Review year | second | N06 | 61/61/61 | 66/66/66 | key/context/answer mapping checked |
| v2-release_year-07 | Torin-Y07 | Release year | 1986 | 1981 | Archive year | Review year | first | N07 | 61/61/61 | 66/66/66 | key/context/answer mapping checked |
| v2-release_year-08 | Torin-Y08 | Release year | 2018 | 1993 | Archive year | Review year | second | N08 | 61/61/61 | 66/66/66 | key/context/answer mapping checked |
| v2-release_year-09 | Torin-Y09 | Release year | 2005 | 2014 | Archive year | Review year | first | N09 | 61/61/61 | 66/66/66 | key/context/answer mapping checked |
| v2-release_year-10 | Torin-Y10 | Release year | 1982 | 2010 | Archive year | Review year | second | N10 | 61/61/61 | 66/66/66 | key/context/answer mapping checked |
| v2-release_year-11 | Torin-Y11 | Release year | 2004 | 2024 | Archive year | Review year | first | N11 | 61/61/61 | 66/66/66 | key/context/answer mapping checked |
| v2-release_year-12 | Torin-Y12 | Release year | 2006 | 2009 | Archive year | Review year | second | N12 | 61/61/61 | 66/66/66 | key/context/answer mapping checked |
| v2-material-01 | Savel-M01 | Main material | cotton | linen | Crate material | Label material | first | N01 | 54/54/54 | 59/59/59 | key/context/answer mapping checked |
| v2-material-02 | Savel-M02 | Main material | silk | bronze | Crate material | Label material | second | N02 | 54/54/54 | 59/59/59 | key/context/answer mapping checked |
| v2-material-03 | Savel-M03 | Main material | bamboo | ceramic | Crate material | Label material | first | N03 | 54/54/54 | 59/59/59 | key/context/answer mapping checked |
| v2-material-04 | Savel-M04 | Main material | wool | paper | Crate material | Label material | second | N04 | 54/54/54 | 59/59/59 | key/context/answer mapping checked |
| v2-material-05 | Savel-M05 | Main material | brass | wood | Crate material | Label material | first | N05 | 54/54/54 | 59/59/59 | key/context/answer mapping checked |
| v2-material-06 | Savel-M06 | Main material | aluminum | foam | Crate material | Label material | second | N06 | 54/54/54 | 59/59/59 | key/context/answer mapping checked |
| v2-material-07 | Savel-M07 | Main material | cork | iron | Crate material | Label material | first | N07 | 54/54/54 | 59/59/59 | key/context/answer mapping checked |
| v2-material-08 | Savel-M08 | Main material | felt | plastic | Crate material | Label material | second | N08 | 54/54/54 | 59/59/59 | key/context/answer mapping checked |
| v2-material-09 | Savel-M09 | Main material | glass | nylon | Crate material | Label material | first | N09 | 54/54/54 | 59/59/59 | key/context/answer mapping checked |
| v2-material-10 | Savel-M10 | Main material | clay | rubber | Crate material | Label material | second | N10 | 54/54/54 | 59/59/59 | key/context/answer mapping checked |
| v2-material-11 | Savel-M11 | Main material | stone | leather | Crate material | Label material | first | N11 | 54/54/54 | 59/59/59 | key/context/answer mapping checked |
| v2-material-12 | Savel-M12 | Main material | steel | copper | Crate material | Label material | second | N12 | 54/54/54 | 59/59/59 | key/context/answer mapping checked |

## Gates and length controls

- Sources: 48; all test-only; four fact types with 12 sources each.
- Rows: 480; 192 natural-style rows (96 pairs), 288 neutral-evidence rows (48 comparisons per format).
- Neutral responses and response-token IDs are identical within every source/format across supported, omitted, and conflicting.
- True/foil order is balanced 24/24 in each condition; target line order is balanced 24/24.
- The word/character/token length deltas and exact matched/reversed subsets are recorded in `data_audit.json` before scoring.
- token_length_matched: 8 pairs.
- word_length_matched: 8 pairs.
- char_length_matched: 8 pairs.
- assertion_longer_all_lengths: 48 pairs.
- assertion_shorter_all_lengths: 40 pairs.
- The v1 source IDs and entity keys have no overlap with v2.
- No generation, model scoring, downloads, or external reference-answer lookup is used.

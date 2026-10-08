# Confidence–Correctness Separation v3: access_code

All answers below are authored test stimuli, not generated responses.

Scores are frozen v1 readouts, not probabilities. Correctness refers to the supplied fictional world.

## v3-access_code-01

**Question:** Which code opens the entry gate at Larkspur Depot?

### World A

Fictional depot record: Larkspur Depot.
Each line names a value and the separate field it belongs to.
4712: entry code
8635: parcel code

**A / confident / correct:** Unequivocally, Larkspur Depot uses 4712 as its entry gate code.

Scores: boundary 3.203819; final_content 0.183985; response_mean -3.997387.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-01--A--answer-A--confident` · final content position 97 · boundary position 98 · mean-token NLL 1.755395

</details>

**A / hedged / correct:** As far as I can tell, Larkspur Depot uses 4712 as its entry gate code.

Scores: boundary 1.807719; final_content -4.605558; response_mean -6.027306.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-01--A--answer-A--hedged` · final content position 99 · boundary position 100 · mean-token NLL 1.645762

</details>

**A / neutral / correct:** Larkspur Depot uses 4712 as its entry gate code.

Scores: boundary 2.955882; final_content -2.726687; response_mean -5.563568.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-01--A--answer-A--neutral` · final content position 92 · boundary position 93 · mean-token NLL 1.197141

</details>

**B / confident / incorrect:** Unequivocally, Larkspur Depot uses 8635 as its entry gate code.

Scores: boundary 3.282184; final_content 0.330626; response_mean -3.985678.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-01--A--answer-B--confident` · final content position 97 · boundary position 98 · mean-token NLL 1.970563

</details>

**B / hedged / incorrect:** As far as I can tell, Larkspur Depot uses 8635 as its entry gate code.

Scores: boundary 1.714162; final_content -4.531314; response_mean -6.106904.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-01--A--answer-B--hedged` · final content position 99 · boundary position 100 · mean-token NLL 1.800120

</details>

**B / neutral / incorrect:** Larkspur Depot uses 8635 as its entry gate code.

Scores: boundary 3.020923; final_content -2.333838; response_mean -5.599614.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-01--A--answer-B--neutral` · final content position 92 · boundary position 93 · mean-token NLL 1.509292

</details>

### World B

Fictional depot record: Larkspur Depot.
Each line names a value and the separate field it belongs to.
4712: parcel code
8635: entry code

**A / confident / incorrect:** Unequivocally, Larkspur Depot uses 4712 as its entry gate code.

Scores: boundary 3.175310; final_content 0.107737; response_mean -4.043656.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-01--B--answer-A--confident` · final content position 97 · boundary position 98 · mean-token NLL 1.894302

</details>

**A / hedged / incorrect:** As far as I can tell, Larkspur Depot uses 4712 as its entry gate code.

Scores: boundary 1.752089; final_content -4.708342; response_mean -6.065601.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-01--B--answer-A--hedged` · final content position 99 · boundary position 100 · mean-token NLL 1.812915

</details>

**A / neutral / incorrect:** Larkspur Depot uses 4712 as its entry gate code.

Scores: boundary 2.863272; final_content -2.783205; response_mean -5.635657.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-01--B--answer-A--neutral` · final content position 92 · boundary position 93 · mean-token NLL 1.429199

</details>

**B / confident / correct:** Unequivocally, Larkspur Depot uses 8635 as its entry gate code.

Scores: boundary 3.240884; final_content 0.250076; response_mean -4.078354.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-01--B--answer-B--confident` · final content position 97 · boundary position 98 · mean-token NLL 1.700579

</details>

**B / hedged / correct:** As far as I can tell, Larkspur Depot uses 8635 as its entry gate code.

Scores: boundary 1.661054; final_content -4.598668; response_mean -6.162765.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-01--B--answer-B--hedged` · final content position 99 · boundary position 100 · mean-token NLL 1.612732

</details>

**B / neutral / correct:** Larkspur Depot uses 8635 as its entry gate code.

Scores: boundary 2.924808; final_content -2.396914; response_mean -5.685327.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-01--B--answer-B--neutral` · final content position 92 · boundary position 93 · mean-token NLL 1.141406

</details>

### World omitted

Fictional depot record: Larkspur Depot.
Each line names a value and the separate field it belongs to.
4712: ticket code
8635: parcel code

**A / neutral / not labelled:** Larkspur Depot uses 4712 as its entry gate code.

Scores: boundary 2.846689; final_content -2.960584; response_mean -5.641077.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-01--omitted--answer-A--neutral` · final content position 92 · boundary position 93 · mean-token NLL 1.412673

</details>

**B / neutral / not labelled:** Larkspur Depot uses 8635 as its entry gate code.

Scores: boundary 2.913159; final_content -2.569876; response_mean -5.707753.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-01--omitted--answer-B--neutral` · final content position 92 · boundary position 93 · mean-token NLL 1.429843

</details>

## v3-access_code-02

**Question:** Which code opens the entry gate at Cobalt Depot?

### World A

Fictional depot record: Cobalt Depot.
Each line names a value and the separate field it belongs to.
7146: parcel code
5928: entry code

**A / confident / correct:** Cobalt Depot uses 5928 as its entry gate code. I have no reservations about that answer.

Scores: boundary 1.795040; final_content -1.160613; response_mean -5.122419.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-02--A--answer-A--confident` · final content position 95 · boundary position 96 · mean-token NLL 2.284301

</details>

**A / hedged / correct:** Cobalt Depot uses 5928 as its entry gate code. I have some reservations about that answer.

Scores: boundary -2.317876; final_content -9.437250; response_mean -6.896431.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-02--A--answer-A--hedged` · final content position 95 · boundary position 96 · mean-token NLL 2.355935

</details>

**A / neutral / correct:** Cobalt Depot uses 5928 as its entry gate code.

Scores: boundary 2.669981; final_content -2.399883; response_mean -5.771427.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-02--A--answer-A--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.316443

</details>

**B / confident / incorrect:** Cobalt Depot uses 7146 as its entry gate code. I have no reservations about that answer.

Scores: boundary 1.831855; final_content -1.033467; response_mean -5.125182.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-02--A--answer-B--confident` · final content position 95 · boundary position 96 · mean-token NLL 2.429466

</details>

**B / hedged / incorrect:** Cobalt Depot uses 7146 as its entry gate code. I have some reservations about that answer.

Scores: boundary -2.196025; final_content -9.348959; response_mean -6.902035.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-02--A--answer-B--hedged` · final content position 95 · boundary position 96 · mean-token NLL 2.490956

</details>

**B / neutral / incorrect:** Cobalt Depot uses 7146 as its entry gate code.

Scores: boundary 2.545565; final_content -2.817519; response_mean -5.775907.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-02--A--answer-B--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.531866

</details>

### World B

Fictional depot record: Cobalt Depot.
Each line names a value and the separate field it belongs to.
7146: entry code
5928: parcel code

**A / confident / incorrect:** Cobalt Depot uses 5928 as its entry gate code. I have no reservations about that answer.

Scores: boundary 1.911644; final_content -1.109902; response_mean -5.090466.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-02--B--answer-A--confident` · final content position 95 · boundary position 96 · mean-token NLL 2.505333

</details>

**A / hedged / incorrect:** Cobalt Depot uses 5928 as its entry gate code. I have some reservations about that answer.

Scores: boundary -2.164336; final_content -9.416094; response_mean -6.866496.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-02--B--answer-A--hedged` · final content position 95 · boundary position 96 · mean-token NLL 2.542818

</details>

**A / neutral / incorrect:** Cobalt Depot uses 5928 as its entry gate code.

Scores: boundary 2.716741; final_content -2.393343; response_mean -5.739214.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-02--B--answer-A--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.595442

</details>

**B / confident / correct:** Cobalt Depot uses 7146 as its entry gate code. I have no reservations about that answer.

Scores: boundary 1.854004; final_content -1.031324; response_mean -5.108686.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-02--B--answer-B--confident` · final content position 95 · boundary position 96 · mean-token NLL 2.317635

</details>

**B / hedged / correct:** Cobalt Depot uses 7146 as its entry gate code. I have some reservations about that answer.

Scores: boundary -2.158555; final_content -9.245151; response_mean -6.882616.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-02--B--answer-B--hedged` · final content position 95 · boundary position 96 · mean-token NLL 2.381721

</details>

**B / neutral / correct:** Cobalt Depot uses 7146 as its entry gate code.

Scores: boundary 2.609398; final_content -2.837753; response_mean -5.776648.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-02--B--answer-B--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.353624

</details>

### World omitted

Fictional depot record: Cobalt Depot.
Each line names a value and the separate field it belongs to.
7146: parcel code
5928: ticket code

**A / neutral / not labelled:** Cobalt Depot uses 5928 as its entry gate code.

Scores: boundary 2.617666; final_content -2.565562; response_mean -5.804351.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-02--omitted--answer-A--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.788214

</details>

**B / neutral / not labelled:** Cobalt Depot uses 7146 as its entry gate code.

Scores: boundary 2.509995; final_content -2.980953; response_mean -5.813294.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-02--omitted--answer-B--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.424287

</details>

## v3-access_code-03

**Question:** Which code opens the entry gate at Merryn Depot?

### World A

Fictional depot record: Merryn Depot.
Each line names a value and the separate field it belongs to.
6384: entry code
9251: parcel code

**A / confident / correct:** Merryn Depot uses 6384 as its entry gate code. I would give that answer without any further qualification.

Scores: boundary 2.616866; final_content -2.026853; response_mean -5.409106.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-03--A--answer-A--confident` · final content position 97 · boundary position 98 · mean-token NLL 2.475123

</details>

**A / hedged / correct:** My answer, subject to revision, is that Merryn Depot uses 6384 as its entry gate code.

Scores: boundary 0.620788; final_content -4.764625; response_mean -6.452055.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-03--A--answer-A--hedged` · final content position 95 · boundary position 96 · mean-token NLL 2.326712

</details>

**A / neutral / correct:** Merryn Depot uses 6384 as its entry gate code.

Scores: boundary 2.720468; final_content -2.892100; response_mean -5.975240.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-03--A--answer-A--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.440451

</details>

**B / confident / incorrect:** Merryn Depot uses 9251 as its entry gate code. I would give that answer without any further qualification.

Scores: boundary 2.600947; final_content -2.030356; response_mean -5.275445.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-03--A--answer-B--confident` · final content position 97 · boundary position 98 · mean-token NLL 2.636049

</details>

**B / hedged / incorrect:** My answer, subject to revision, is that Merryn Depot uses 9251 as its entry gate code.

Scores: boundary 0.605293; final_content -4.668402; response_mean -6.304089.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-03--A--answer-B--hedged` · final content position 95 · boundary position 96 · mean-token NLL 2.386577

</details>

**B / neutral / incorrect:** Merryn Depot uses 9251 as its entry gate code.

Scores: boundary 2.682659; final_content -2.573596; response_mean -5.785126.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-03--A--answer-B--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.613353

</details>

### World B

Fictional depot record: Merryn Depot.
Each line names a value and the separate field it belongs to.
6384: parcel code
9251: entry code

**A / confident / incorrect:** Merryn Depot uses 6384 as its entry gate code. I would give that answer without any further qualification.

Scores: boundary 2.557512; final_content -2.080549; response_mean -5.456309.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-03--B--answer-A--confident` · final content position 97 · boundary position 98 · mean-token NLL 2.612840

</details>

**A / hedged / incorrect:** My answer, subject to revision, is that Merryn Depot uses 6384 as its entry gate code.

Scores: boundary 0.556464; final_content -4.793242; response_mean -6.489272.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-03--B--answer-A--hedged` · final content position 95 · boundary position 96 · mean-token NLL 2.430807

</details>

**A / neutral / incorrect:** Merryn Depot uses 6384 as its entry gate code.

Scores: boundary 2.667146; final_content -2.893044; response_mean -6.038828.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-03--B--answer-A--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.651627

</details>

**B / confident / correct:** Merryn Depot uses 9251 as its entry gate code. I would give that answer without any further qualification.

Scores: boundary 2.484945; final_content -2.049691; response_mean -5.298588.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-03--B--answer-B--confident` · final content position 97 · boundary position 98 · mean-token NLL 2.435839

</details>

**B / hedged / correct:** My answer, subject to revision, is that Merryn Depot uses 9251 as its entry gate code.

Scores: boundary 0.528797; final_content -4.631239; response_mean -6.312663.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-03--B--answer-B--hedged` · final content position 95 · boundary position 96 · mean-token NLL 2.232505

</details>

**B / neutral / correct:** Merryn Depot uses 9251 as its entry gate code.

Scores: boundary 2.644288; final_content -2.516314; response_mean -5.821730.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-03--B--answer-B--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.321857

</details>

### World omitted

Fictional depot record: Merryn Depot.
Each line names a value and the separate field it belongs to.
6384: ticket code
9251: parcel code

**A / neutral / not labelled:** Merryn Depot uses 6384 as its entry gate code.

Scores: boundary 2.569280; final_content -3.028164; response_mean -6.095034.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-03--omitted--answer-A--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.679264

</details>

**B / neutral / not labelled:** Merryn Depot uses 9251 as its entry gate code.

Scores: boundary 2.572788; final_content -2.694402; response_mean -5.865010.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-03--omitted--answer-B--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.601023

</details>

## v3-access_code-04

**Question:** Which code opens the entry gate at Brindle Depot?

### World A

Fictional depot record: Brindle Depot.
Each line names a value and the separate field it belongs to.
4863: parcel code
2579: entry code

**A / confident / correct:** Unequivocally, Brindle Depot uses 2579 as its entry gate code.

Scores: boundary 3.030001; final_content 0.232089; response_mean -4.111359.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-04--A--answer-A--confident` · final content position 91 · boundary position 92 · mean-token NLL 1.940615

</details>

**A / hedged / correct:** As far as I can tell, Brindle Depot uses 2579 as its entry gate code.

Scores: boundary 1.441650; final_content -4.764557; response_mean -6.271054.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-04--A--answer-A--hedged` · final content position 93 · boundary position 94 · mean-token NLL 1.777926

</details>

**A / neutral / correct:** Brindle Depot uses 2579 as its entry gate code.

Scores: boundary 2.530285; final_content -2.511757; response_mean -5.835610.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-04--A--answer-A--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.440943

</details>

**B / confident / incorrect:** Unequivocally, Brindle Depot uses 4863 as its entry gate code.

Scores: boundary 3.082569; final_content -0.009410; response_mean -4.103537.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-04--A--answer-B--confident` · final content position 91 · boundary position 92 · mean-token NLL 2.165810

</details>

**B / hedged / incorrect:** As far as I can tell, Brindle Depot uses 4863 as its entry gate code.

Scores: boundary 1.628696; final_content -4.689773; response_mean -6.251780.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-04--A--answer-B--hedged` · final content position 93 · boundary position 94 · mean-token NLL 1.999427

</details>

**B / neutral / incorrect:** Brindle Depot uses 4863 as its entry gate code.

Scores: boundary 2.603796; final_content -2.828185; response_mean -5.807517.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-04--A--answer-B--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.691464

</details>

### World B

Fictional depot record: Brindle Depot.
Each line names a value and the separate field it belongs to.
4863: entry code
2579: parcel code

**A / confident / incorrect:** Unequivocally, Brindle Depot uses 2579 as its entry gate code.

Scores: boundary 3.085203; final_content 0.281839; response_mean -4.082732.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-04--B--answer-A--confident` · final content position 91 · boundary position 92 · mean-token NLL 2.195525

</details>

**A / hedged / incorrect:** As far as I can tell, Brindle Depot uses 2579 as its entry gate code.

Scores: boundary 1.478944; final_content -4.655930; response_mean -6.248013.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-04--B--answer-A--hedged` · final content position 93 · boundary position 94 · mean-token NLL 1.941042

</details>

**A / neutral / incorrect:** Brindle Depot uses 2579 as its entry gate code.

Scores: boundary 2.611203; final_content -2.386591; response_mean -5.804023.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-04--B--answer-A--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.688236

</details>

**B / confident / correct:** Unequivocally, Brindle Depot uses 4863 as its entry gate code.

Scores: boundary 3.092333; final_content 0.025319; response_mean -4.094305.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-04--B--answer-B--confident` · final content position 91 · boundary position 92 · mean-token NLL 1.970711

</details>

**B / hedged / correct:** As far as I can tell, Brindle Depot uses 4863 as its entry gate code.

Scores: boundary 1.638311; final_content -4.647607; response_mean -6.238798.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-04--B--answer-B--hedged` · final content position 93 · boundary position 94 · mean-token NLL 1.846347

</details>

**B / neutral / correct:** Brindle Depot uses 4863 as its entry gate code.

Scores: boundary 2.667726; final_content -2.791956; response_mean -5.745637.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-04--B--answer-B--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.440301

</details>

### World omitted

Fictional depot record: Brindle Depot.
Each line names a value and the separate field it belongs to.
4863: parcel code
2579: ticket code

**A / neutral / not labelled:** Brindle Depot uses 2579 as its entry gate code.

Scores: boundary 2.496090; final_content -2.636420; response_mean -5.891964.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-04--omitted--answer-A--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.867209

</details>

**B / neutral / not labelled:** Brindle Depot uses 4863 as its entry gate code.

Scores: boundary 2.567569; final_content -2.996556; response_mean -5.870115.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-04--omitted--answer-B--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.625280

</details>

## v3-access_code-05

**Question:** Which code opens the entry gate at Auburn Depot?

### World A

Fictional depot record: Auburn Depot.
Each line names a value and the separate field it belongs to.
8194: entry code
3627: parcel code

**A / confident / correct:** Auburn Depot uses 8194 as its entry gate code. I have no reservations about that answer.

Scores: boundary 1.675360; final_content -0.976238; response_mean -5.051371.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-05--A--answer-A--confident` · final content position 93 · boundary position 94 · mean-token NLL 2.348955

</details>

**A / hedged / correct:** Auburn Depot uses 8194 as its entry gate code. I have some reservations about that answer.

Scores: boundary -2.407180; final_content -9.352765; response_mean -6.851501.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-05--A--answer-A--hedged` · final content position 93 · boundary position 94 · mean-token NLL 2.440323

</details>

**A / neutral / correct:** Auburn Depot uses 8194 as its entry gate code.

Scores: boundary 2.569766; final_content -2.924958; response_mean -5.654638.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-05--A--answer-A--neutral` · final content position 85 · boundary position 86 · mean-token NLL 1.358978

</details>

**B / confident / incorrect:** Auburn Depot uses 3627 as its entry gate code. I have no reservations about that answer.

Scores: boundary 1.876686; final_content -0.887638; response_mean -5.000432.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-05--A--answer-B--confident` · final content position 93 · boundary position 94 · mean-token NLL 2.449527

</details>

**B / hedged / incorrect:** Auburn Depot uses 3627 as its entry gate code. I have some reservations about that answer.

Scores: boundary -2.297620; final_content -9.264903; response_mean -6.799864.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-05--A--answer-B--hedged` · final content position 93 · boundary position 94 · mean-token NLL 2.519693

</details>

**B / neutral / incorrect:** Auburn Depot uses 3627 as its entry gate code.

Scores: boundary 2.749237; final_content -2.232476; response_mean -5.580677.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-05--A--answer-B--neutral` · final content position 85 · boundary position 86 · mean-token NLL 1.556690

</details>

### World B

Fictional depot record: Auburn Depot.
Each line names a value and the separate field it belongs to.
8194: parcel code
3627: entry code

**A / confident / incorrect:** Auburn Depot uses 8194 as its entry gate code. I have no reservations about that answer.

Scores: boundary 1.678215; final_content -1.008281; response_mean -5.077807.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-05--B--answer-A--confident` · final content position 93 · boundary position 94 · mean-token NLL 2.527206

</details>

**A / hedged / incorrect:** Auburn Depot uses 8194 as its entry gate code. I have some reservations about that answer.

Scores: boundary -2.427940; final_content -9.326178; response_mean -6.866092.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-05--B--answer-A--hedged` · final content position 93 · boundary position 94 · mean-token NLL 2.613354

</details>

**A / neutral / incorrect:** Auburn Depot uses 8194 as its entry gate code.

Scores: boundary 2.540759; final_content -2.885537; response_mean -5.672558.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-05--B--answer-A--neutral` · final content position 85 · boundary position 86 · mean-token NLL 1.654982

</details>

**B / confident / correct:** Auburn Depot uses 3627 as its entry gate code. I have no reservations about that answer.

Scores: boundary 1.754785; final_content -0.946266; response_mean -5.032872.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-05--B--answer-B--confident` · final content position 93 · boundary position 94 · mean-token NLL 2.260152

</details>

**B / hedged / correct:** Auburn Depot uses 3627 as its entry gate code. I have some reservations about that answer.

Scores: boundary -2.489954; final_content -9.367842; response_mean -6.836775.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-05--B--answer-B--hedged` · final content position 93 · boundary position 94 · mean-token NLL 2.358252

</details>

**B / neutral / correct:** Auburn Depot uses 3627 as its entry gate code.

Scores: boundary 2.726205; final_content -2.279989; response_mean -5.616676.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-05--B--answer-B--neutral` · final content position 85 · boundary position 86 · mean-token NLL 1.312737

</details>

### World omitted

Fictional depot record: Auburn Depot.
Each line names a value and the separate field it belongs to.
8194: ticket code
3627: parcel code

**A / neutral / not labelled:** Auburn Depot uses 8194 as its entry gate code.

Scores: boundary 2.589866; final_content -2.912577; response_mean -5.738189.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-05--omitted--answer-A--neutral` · final content position 85 · boundary position 86 · mean-token NLL 1.560557

</details>

**B / neutral / not labelled:** Auburn Depot uses 3627 as its entry gate code.

Scores: boundary 2.699429; final_content -2.426684; response_mean -5.670126.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-05--omitted--answer-B--neutral` · final content position 85 · boundary position 86 · mean-token NLL 1.561733

</details>

## v3-access_code-06

**Question:** Which code opens the entry gate at Ternwick Depot?

### World A

Fictional depot record: Ternwick Depot.
Each line names a value and the separate field it belongs to.
1586: parcel code
7432: entry code

**A / confident / correct:** Ternwick Depot uses 7432 as its entry gate code. I would give that answer without any further qualification.

Scores: boundary 2.731493; final_content -2.139417; response_mean -5.392671.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-06--A--answer-A--confident` · final content position 99 · boundary position 100 · mean-token NLL 2.442555

</details>

**A / hedged / correct:** My answer, subject to revision, is that Ternwick Depot uses 7432 as its entry gate code.

Scores: boundary 0.827207; final_content -4.328827; response_mean -6.315917.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-06--A--answer-A--hedged` · final content position 98 · boundary position 99 · mean-token NLL 2.195357

</details>

**A / neutral / correct:** Ternwick Depot uses 7432 as its entry gate code.

Scores: boundary 3.003938; final_content -2.343956; response_mean -5.969975.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-06--A--answer-A--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.337514

</details>

**B / confident / incorrect:** Ternwick Depot uses 1586 as its entry gate code. I would give that answer without any further qualification.

Scores: boundary 2.670073; final_content -2.148207; response_mean -5.554935.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-06--A--answer-B--confident` · final content position 99 · boundary position 100 · mean-token NLL 2.491661

</details>

**B / hedged / incorrect:** My answer, subject to revision, is that Ternwick Depot uses 1586 as its entry gate code.

Scores: boundary 0.668789; final_content -4.925043; response_mean -6.486302.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-06--A--answer-B--hedged` · final content position 98 · boundary position 99 · mean-token NLL 2.306234

</details>

**B / neutral / incorrect:** Ternwick Depot uses 1586 as its entry gate code.

Scores: boundary 2.729163; final_content -2.908900; response_mean -6.226421.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-06--A--answer-B--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.525309

</details>

### World B

Fictional depot record: Ternwick Depot.
Each line names a value and the separate field it belongs to.
1586: entry code
7432: parcel code

**A / confident / incorrect:** Ternwick Depot uses 7432 as its entry gate code. I would give that answer without any further qualification.

Scores: boundary 2.782229; final_content -2.093863; response_mean -5.359243.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-06--B--answer-A--confident` · final content position 99 · boundary position 100 · mean-token NLL 2.574752

</details>

**A / hedged / incorrect:** My answer, subject to revision, is that Ternwick Depot uses 7432 as its entry gate code.

Scores: boundary 0.944371; final_content -4.310739; response_mean -6.264392.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-06--B--answer-A--hedged` · final content position 98 · boundary position 99 · mean-token NLL 2.286633

</details>

**A / neutral / incorrect:** Ternwick Depot uses 7432 as its entry gate code.

Scores: boundary 3.061575; final_content -2.350485; response_mean -5.921827.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-06--B--answer-A--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.526804

</details>

**B / confident / correct:** Ternwick Depot uses 1586 as its entry gate code. I would give that answer without any further qualification.

Scores: boundary 2.714472; final_content -2.155182; response_mean -5.543827.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-06--B--answer-B--confident` · final content position 99 · boundary position 100 · mean-token NLL 2.378365

</details>

**B / hedged / correct:** My answer, subject to revision, is that Ternwick Depot uses 1586 as its entry gate code.

Scores: boundary 0.742345; final_content -4.865038; response_mean -6.429608.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-06--B--answer-B--hedged` · final content position 98 · boundary position 99 · mean-token NLL 2.191442

</details>

**B / neutral / correct:** Ternwick Depot uses 1586 as its entry gate code.

Scores: boundary 2.740271; final_content -3.025955; response_mean -6.204957.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-06--B--answer-B--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.329214

</details>

### World omitted

Fictional depot record: Ternwick Depot.
Each line names a value and the separate field it belongs to.
1586: parcel code
7432: ticket code

**A / neutral / not labelled:** Ternwick Depot uses 7432 as its entry gate code.

Scores: boundary 3.026161; final_content -2.518893; response_mean -6.020746.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-06--omitted--answer-A--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.574796

</details>

**B / neutral / not labelled:** Ternwick Depot uses 1586 as its entry gate code.

Scores: boundary 2.760297; final_content -3.054518; response_mean -6.302613.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-06--omitted--answer-B--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.526076

</details>

## v3-access_code-07

**Question:** Which code opens the entry gate at Nettle Depot?

### World A

Fictional depot record: Nettle Depot.
Each line names a value and the separate field it belongs to.
9264: entry code
5731: parcel code

**A / confident / correct:** Unequivocally, Nettle Depot uses 9264 as its entry gate code.

Scores: boundary 3.226006; final_content 0.278011; response_mean -3.926181.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-07--A--answer-A--confident` · final content position 91 · boundary position 92 · mean-token NLL 1.939709

</details>

**A / hedged / correct:** As far as I can tell, Nettle Depot uses 9264 as its entry gate code.

Scores: boundary 1.835601; final_content -4.543513; response_mean -6.130123.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-07--A--answer-A--hedged` · final content position 93 · boundary position 94 · mean-token NLL 1.902042

</details>

**A / neutral / correct:** Nettle Depot uses 9264 as its entry gate code.

Scores: boundary 2.620633; final_content -2.778753; response_mean -5.559325.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-07--A--answer-A--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.593339

</details>

**B / confident / incorrect:** Unequivocally, Nettle Depot uses 5731 as its entry gate code.

Scores: boundary 3.191747; final_content 0.443081; response_mean -3.984989.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-07--A--answer-B--confident` · final content position 91 · boundary position 92 · mean-token NLL 2.038804

</details>

**B / hedged / incorrect:** As far as I can tell, Nettle Depot uses 5731 as its entry gate code.

Scores: boundary 1.806424; final_content -4.360267; response_mean -6.188616.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-07--A--answer-B--hedged` · final content position 93 · boundary position 94 · mean-token NLL 1.972936

</details>

**B / neutral / incorrect:** Nettle Depot uses 5731 as its entry gate code.

Scores: boundary 2.717990; final_content -2.280347; response_mean -5.598016.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-07--A--answer-B--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.803179

</details>

### World B

Fictional depot record: Nettle Depot.
Each line names a value and the separate field it belongs to.
9264: parcel code
5731: entry code

**A / confident / incorrect:** Unequivocally, Nettle Depot uses 9264 as its entry gate code.

Scores: boundary 3.061238; final_content 0.114000; response_mean -3.992605.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-07--B--answer-A--confident` · final content position 91 · boundary position 92 · mean-token NLL 2.081256

</details>

**A / hedged / incorrect:** As far as I can tell, Nettle Depot uses 9264 as its entry gate code.

Scores: boundary 1.722924; final_content -4.622152; response_mean -6.141173.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-07--B--answer-A--hedged` · final content position 93 · boundary position 94 · mean-token NLL 1.990255

</details>

**A / neutral / incorrect:** Nettle Depot uses 9264 as its entry gate code.

Scores: boundary 2.475844; final_content -2.827597; response_mean -5.578725.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-07--B--answer-A--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.825547

</details>

**B / confident / correct:** Unequivocally, Nettle Depot uses 5731 as its entry gate code.

Scores: boundary 3.143663; final_content 0.294974; response_mean -4.067726.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-07--B--answer-B--confident` · final content position 91 · boundary position 92 · mean-token NLL 1.807793

</details>

**B / hedged / correct:** As far as I can tell, Nettle Depot uses 5731 as its entry gate code.

Scores: boundary 1.650749; final_content -4.480407; response_mean -6.229707.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-07--B--answer-B--hedged` · final content position 93 · boundary position 94 · mean-token NLL 1.747260

</details>

**B / neutral / correct:** Nettle Depot uses 5731 as its entry gate code.

Scores: boundary 2.592128; final_content -2.307295; response_mean -5.671014.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-07--B--answer-B--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.477291

</details>

### World omitted

Fictional depot record: Nettle Depot.
Each line names a value and the separate field it belongs to.
9264: ticket code
5731: parcel code

**A / neutral / not labelled:** Nettle Depot uses 9264 as its entry gate code.

Scores: boundary 2.447024; final_content -2.919671; response_mean -5.670676.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-07--omitted--answer-A--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.806555

</details>

**B / neutral / not labelled:** Nettle Depot uses 5731 as its entry gate code.

Scores: boundary 2.541736; final_content -2.446985; response_mean -5.710769.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-07--omitted--answer-B--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.761603

</details>

## v3-access_code-08

**Question:** Which code opens the entry gate at Plover Depot?

### World A

Fictional depot record: Plover Depot.
Each line names a value and the separate field it belongs to.
6192: parcel code
3847: entry code

**A / confident / correct:** Plover Depot uses 3847 as its entry gate code. I have no reservations about that answer.

Scores: boundary 1.651740; final_content -1.425253; response_mean -5.293291.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-08--A--answer-A--confident` · final content position 94 · boundary position 95 · mean-token NLL 2.344752

</details>

**A / hedged / correct:** Plover Depot uses 3847 as its entry gate code. I have some reservations about that answer.

Scores: boundary -2.200955; final_content -9.383725; response_mean -7.106910.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-08--A--answer-A--hedged` · final content position 94 · boundary position 95 · mean-token NLL 2.413648

</details>

**A / neutral / correct:** Plover Depot uses 3847 as its entry gate code.

Scores: boundary 2.453429; final_content -2.630601; response_mean -5.984141.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-08--A--answer-A--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.404364

</details>

**B / confident / incorrect:** Plover Depot uses 6192 as its entry gate code. I have no reservations about that answer.

Scores: boundary 1.705122; final_content -1.291340; response_mean -5.257702.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-08--A--answer-B--confident` · final content position 94 · boundary position 95 · mean-token NLL 2.566076

</details>

**B / hedged / incorrect:** Plover Depot uses 6192 as its entry gate code. I have some reservations about that answer.

Scores: boundary -2.131019; final_content -9.338877; response_mean -7.075243.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-08--A--answer-B--hedged` · final content position 94 · boundary position 95 · mean-token NLL 2.640482

</details>

**B / neutral / incorrect:** Plover Depot uses 6192 as its entry gate code.

Scores: boundary 2.371289; final_content -3.025046; response_mean -5.954929.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-08--A--answer-B--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.674637

</details>

### World B

Fictional depot record: Plover Depot.
Each line names a value and the separate field it belongs to.
6192: entry code
3847: parcel code

**A / confident / incorrect:** Plover Depot uses 3847 as its entry gate code. I have no reservations about that answer.

Scores: boundary 1.720407; final_content -1.319656; response_mean -5.236058.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-08--B--answer-A--confident` · final content position 94 · boundary position 95 · mean-token NLL 2.558406

</details>

**A / hedged / incorrect:** Plover Depot uses 3847 as its entry gate code. I have some reservations about that answer.

Scores: boundary -2.193449; final_content -9.307044; response_mean -7.058886.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-08--B--answer-A--hedged` · final content position 94 · boundary position 95 · mean-token NLL 2.612495

</details>

**A / neutral / incorrect:** Plover Depot uses 3847 as its entry gate code.

Scores: boundary 2.537972; final_content -2.573448; response_mean -5.943683.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-08--B--answer-A--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.702801

</details>

**B / confident / correct:** Plover Depot uses 6192 as its entry gate code. I have no reservations about that answer.

Scores: boundary 1.708456; final_content -1.259623; response_mean -5.196454.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-08--B--answer-B--confident` · final content position 94 · boundary position 95 · mean-token NLL 2.412529

</details>

**B / hedged / correct:** Plover Depot uses 6192 as its entry gate code. I have some reservations about that answer.

Scores: boundary -2.128994; final_content -9.289167; response_mean -7.020855.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-08--B--answer-B--hedged` · final content position 94 · boundary position 95 · mean-token NLL 2.484210

</details>

**B / neutral / correct:** Plover Depot uses 6192 as its entry gate code.

Scores: boundary 2.399661; final_content -2.977095; response_mean -5.886917.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-08--B--answer-B--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.436680

</details>

### World omitted

Fictional depot record: Plover Depot.
Each line names a value and the separate field it belongs to.
6192: parcel code
3847: ticket code

**A / neutral / not labelled:** Plover Depot uses 3847 as its entry gate code.

Scores: boundary 2.482471; final_content -2.763509; response_mean -6.019812.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-08--omitted--answer-A--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.834661

</details>

**B / neutral / not labelled:** Plover Depot uses 6192 as its entry gate code.

Scores: boundary 2.402138; final_content -3.124328; response_mean -5.972961.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-08--omitted--answer-B--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.604585

</details>

## v3-access_code-09

**Question:** Which code opens the entry gate at Rillbank Depot?

### World A

Fictional depot record: Rillbank Depot.
Each line names a value and the separate field it belongs to.
1658: entry code
9423: parcel code

**A / confident / correct:** Rillbank Depot uses 1658 as its entry gate code. I would give that answer without any further qualification.

Scores: boundary 2.641711; final_content -2.070288; response_mean -5.204261.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-09--A--answer-A--confident` · final content position 99 · boundary position 100 · mean-token NLL 2.417390

</details>

**A / hedged / correct:** My answer, subject to revision, is that Rillbank Depot uses 1658 as its entry gate code.

Scores: boundary 0.642675; final_content -4.873337; response_mean -6.173201.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-09--A--answer-A--hedged` · final content position 98 · boundary position 99 · mean-token NLL 2.194768

</details>

**A / neutral / correct:** Rillbank Depot uses 1658 as its entry gate code.

Scores: boundary 2.694698; final_content -3.017226; response_mean -5.702122.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-09--A--answer-A--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.337954

</details>

**B / confident / incorrect:** Rillbank Depot uses 9423 as its entry gate code. I would give that answer without any further qualification.

Scores: boundary 2.744952; final_content -2.080418; response_mean -5.084653.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-09--A--answer-B--confident` · final content position 99 · boundary position 100 · mean-token NLL 2.485244

</details>

**B / hedged / incorrect:** My answer, subject to revision, is that Rillbank Depot uses 9423 as its entry gate code.

Scores: boundary 0.865579; final_content -4.280463; response_mean -6.095011.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-09--A--answer-B--hedged` · final content position 98 · boundary position 99 · mean-token NLL 2.207124

</details>

**B / neutral / incorrect:** Rillbank Depot uses 9423 as its entry gate code.

Scores: boundary 3.016428; final_content -2.301564; response_mean -5.514906.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-09--A--answer-B--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.405898

</details>

### World B

Fictional depot record: Rillbank Depot.
Each line names a value and the separate field it belongs to.
1658: parcel code
9423: entry code

**A / confident / incorrect:** Rillbank Depot uses 1658 as its entry gate code. I would give that answer without any further qualification.

Scores: boundary 2.588567; final_content -2.042380; response_mean -5.214736.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-09--B--answer-A--confident` · final content position 99 · boundary position 100 · mean-token NLL 2.640182

</details>

**A / hedged / incorrect:** My answer, subject to revision, is that Rillbank Depot uses 1658 as its entry gate code.

Scores: boundary 0.647131; final_content -4.912032; response_mean -6.182730.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-09--B--answer-A--hedged` · final content position 98 · boundary position 99 · mean-token NLL 2.335561

</details>

**A / neutral / incorrect:** Rillbank Depot uses 1658 as its entry gate code.

Scores: boundary 2.697445; final_content -2.993028; response_mean -5.709647.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-09--B--answer-A--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.665042

</details>

**B / confident / correct:** Rillbank Depot uses 9423 as its entry gate code. I would give that answer without any further qualification.

Scores: boundary 2.720729; final_content -2.079161; response_mean -5.114650.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-09--B--answer-B--confident` · final content position 99 · boundary position 100 · mean-token NLL 2.366165

</details>

**B / hedged / correct:** My answer, subject to revision, is that Rillbank Depot uses 9423 as its entry gate code.

Scores: boundary 0.913430; final_content -4.296513; response_mean -6.104647.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-09--B--answer-B--hedged` · final content position 98 · boundary position 99 · mean-token NLL 2.121511

</details>

**B / neutral / correct:** Rillbank Depot uses 9423 as its entry gate code.

Scores: boundary 2.998111; final_content -2.284840; response_mean -5.544357.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-09--B--answer-B--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.251576

</details>

### World omitted

Fictional depot record: Rillbank Depot.
Each line names a value and the separate field it belongs to.
1658: ticket code
9423: parcel code

**A / neutral / not labelled:** Rillbank Depot uses 1658 as its entry gate code.

Scores: boundary 2.633950; final_content -3.171325; response_mean -5.825730.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-09--omitted--answer-A--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.602677

</details>

**B / neutral / not labelled:** Rillbank Depot uses 9423 as its entry gate code.

Scores: boundary 2.844047; final_content -2.507742; response_mean -5.597843.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-09--omitted--answer-B--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.459667

</details>

## v3-access_code-10

**Question:** Which code opens the entry gate at Fenlight Depot?

### World A

Fictional depot record: Fenlight Depot.
Each line names a value and the separate field it belongs to.
4539: parcel code
8276: entry code

**A / confident / correct:** Unequivocally, Fenlight Depot uses 8276 as its entry gate code.

Scores: boundary 3.111294; final_content 0.005655; response_mean -4.198665.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-10--A--answer-A--confident` · final content position 91 · boundary position 92 · mean-token NLL 1.945966

</details>

**A / hedged / correct:** As far as I can tell, Fenlight Depot uses 8276 as its entry gate code.

Scores: boundary 1.674058; final_content -4.470907; response_mean -6.221592.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-10--A--answer-A--hedged` · final content position 93 · boundary position 94 · mean-token NLL 1.835000

</details>

**A / neutral / correct:** Fenlight Depot uses 8276 as its entry gate code.

Scores: boundary 2.665382; final_content -2.565779; response_mean -5.829115.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-10--A--answer-A--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.397242

</details>

**B / confident / incorrect:** Unequivocally, Fenlight Depot uses 4539 as its entry gate code.

Scores: boundary 3.063542; final_content -0.123899; response_mean -4.250540.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-10--A--answer-B--confident` · final content position 91 · boundary position 92 · mean-token NLL 2.122846

</details>

**B / hedged / incorrect:** As far as I can tell, Fenlight Depot uses 4539 as its entry gate code.

Scores: boundary 1.640160; final_content -4.699030; response_mean -6.241777.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-10--A--answer-B--hedged` · final content position 93 · boundary position 94 · mean-token NLL 1.980765

</details>

**B / neutral / incorrect:** Fenlight Depot uses 4539 as its entry gate code.

Scores: boundary 2.512517; final_content -3.175137; response_mean -5.925416.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-10--A--answer-B--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.552879

</details>

### World B

Fictional depot record: Fenlight Depot.
Each line names a value and the separate field it belongs to.
4539: entry code
8276: parcel code

**A / confident / incorrect:** Unequivocally, Fenlight Depot uses 8276 as its entry gate code.

Scores: boundary 3.136044; final_content 0.085740; response_mean -4.154617.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-10--B--answer-A--confident` · final content position 91 · boundary position 92 · mean-token NLL 2.278666

</details>

**A / hedged / incorrect:** As far as I can tell, Fenlight Depot uses 8276 as its entry gate code.

Scores: boundary 1.682848; final_content -4.557310; response_mean -6.224570.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-10--B--answer-A--hedged` · final content position 93 · boundary position 94 · mean-token NLL 2.050887

</details>

**A / neutral / incorrect:** Fenlight Depot uses 8276 as its entry gate code.

Scores: boundary 2.725139; final_content -2.583946; response_mean -5.837626.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-10--B--answer-A--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.692155

</details>

**B / confident / correct:** Unequivocally, Fenlight Depot uses 4539 as its entry gate code.

Scores: boundary 3.076019; final_content -0.057343; response_mean -4.229088.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-10--B--answer-B--confident` · final content position 91 · boundary position 92 · mean-token NLL 1.971619

</details>

**B / hedged / correct:** As far as I can tell, Fenlight Depot uses 4539 as its entry gate code.

Scores: boundary 1.639799; final_content -4.718874; response_mean -6.232878.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-10--B--answer-B--hedged` · final content position 93 · boundary position 94 · mean-token NLL 1.852349

</details>

**B / neutral / correct:** Fenlight Depot uses 4539 as its entry gate code.

Scores: boundary 2.483570; final_content -3.258169; response_mean -5.942196.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-10--B--answer-B--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.360819

</details>

### World omitted

Fictional depot record: Fenlight Depot.
Each line names a value and the separate field it belongs to.
4539: parcel code
8276: ticket code

**A / neutral / not labelled:** Fenlight Depot uses 8276 as its entry gate code.

Scores: boundary 2.661789; final_content -2.693075; response_mean -5.875203.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-10--omitted--answer-A--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.811232

</details>

**B / neutral / not labelled:** Fenlight Depot uses 4539 as its entry gate code.

Scores: boundary 2.428969; final_content -3.343905; response_mean -5.985211.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-10--omitted--answer-B--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.526819

</details>

## v3-access_code-11

**Question:** Which code opens the entry gate at Mossfield Depot?

### World A

Fictional depot record: Mossfield Depot.
Each line names a value and the separate field it belongs to.
6913: entry code
2784: parcel code

**A / confident / correct:** Mossfield Depot uses 6913 as its entry gate code. I have no reservations about that answer.

Scores: boundary 2.064295; final_content -0.862084; response_mean -5.077093.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-11--A--answer-A--confident` · final content position 95 · boundary position 96 · mean-token NLL 2.300118

</details>

**A / hedged / correct:** Mossfield Depot uses 6913 as its entry gate code. I have some reservations about that answer.

Scores: boundary -1.950259; final_content -9.258122; response_mean -6.861725.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-11--A--answer-A--hedged` · final content position 95 · boundary position 96 · mean-token NLL 2.374716

</details>

**A / neutral / correct:** Mossfield Depot uses 6913 as its entry gate code.

Scores: boundary 2.822561; final_content -2.531318; response_mean -5.712209.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-11--A--answer-A--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.296569

</details>

**B / confident / incorrect:** Mossfield Depot uses 2784 as its entry gate code. I have no reservations about that answer.

Scores: boundary 1.900359; final_content -1.178155; response_mean -5.175875.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-11--A--answer-B--confident` · final content position 95 · boundary position 96 · mean-token NLL 2.425236

</details>

**B / hedged / incorrect:** Mossfield Depot uses 2784 as its entry gate code. I have some reservations about that answer.

Scores: boundary -2.090492; final_content -9.516749; response_mean -6.954112.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-11--A--answer-B--hedged` · final content position 95 · boundary position 96 · mean-token NLL 2.477089

</details>

**B / neutral / incorrect:** Mossfield Depot uses 2784 as its entry gate code.

Scores: boundary 2.727835; final_content -2.385063; response_mean -5.847466.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-11--A--answer-B--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.510010

</details>

### World B

Fictional depot record: Mossfield Depot.
Each line names a value and the separate field it belongs to.
6913: parcel code
2784: entry code

**A / confident / incorrect:** Mossfield Depot uses 6913 as its entry gate code. I have no reservations about that answer.

Scores: boundary 1.957888; final_content -0.854323; response_mean -5.126820.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-11--B--answer-A--confident` · final content position 95 · boundary position 96 · mean-token NLL 2.553706

</details>

**A / hedged / incorrect:** Mossfield Depot uses 6913 as its entry gate code. I have some reservations about that answer.

Scores: boundary -2.126332; final_content -9.384373; response_mean -6.919321.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-11--B--answer-A--hedged` · final content position 95 · boundary position 96 · mean-token NLL 2.613751

</details>

**A / neutral / incorrect:** Mossfield Depot uses 6913 as its entry gate code.

Scores: boundary 2.711960; final_content -2.550258; response_mean -5.768323.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-11--B--answer-A--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.672708

</details>

**B / confident / correct:** Mossfield Depot uses 2784 as its entry gate code. I have no reservations about that answer.

Scores: boundary 1.814565; final_content -1.183851; response_mean -5.210566.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-11--B--answer-B--confident` · final content position 95 · boundary position 96 · mean-token NLL 2.337988

</details>

**B / hedged / correct:** Mossfield Depot uses 2784 as its entry gate code. I have some reservations about that answer.

Scores: boundary -2.253676; final_content -9.482590; response_mean -6.984751.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-11--B--answer-B--hedged` · final content position 95 · boundary position 96 · mean-token NLL 2.379869

</details>

**B / neutral / correct:** Mossfield Depot uses 2784 as its entry gate code.

Scores: boundary 2.726818; final_content -2.368734; response_mean -5.881559.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-11--B--answer-B--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.354762

</details>

### World omitted

Fictional depot record: Mossfield Depot.
Each line names a value and the separate field it belongs to.
6913: ticket code
2784: parcel code

**A / neutral / not labelled:** Mossfield Depot uses 6913 as its entry gate code.

Scores: boundary 2.711715; final_content -2.696579; response_mean -5.815496.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-11--omitted--answer-A--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.645880

</details>

**B / neutral / not labelled:** Mossfield Depot uses 2784 as its entry gate code.

Scores: boundary 2.643307; final_content -2.627696; response_mean -5.935589.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-11--omitted--answer-B--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.548242

</details>

## v3-access_code-12

**Question:** Which code opens the entry gate at Kestrel Depot?

### World A

Fictional depot record: Kestrel Depot.
Each line names a value and the separate field it belongs to.
8971: parcel code
5326: entry code

**A / confident / correct:** Kestrel Depot uses 5326 as its entry gate code. I would give that answer without any further qualification.

Scores: boundary 2.695430; final_content -2.132898; response_mean -5.260363.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-12--A--answer-A--confident` · final content position 99 · boundary position 100 · mean-token NLL 2.391421

</details>

**A / hedged / correct:** My answer, subject to revision, is that Kestrel Depot uses 5326 as its entry gate code.

Scores: boundary 0.680620; final_content -4.713014; response_mean -6.229628.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-12--A--answer-A--hedged` · final content position 98 · boundary position 99 · mean-token NLL 2.154987

</details>

**A / neutral / correct:** Kestrel Depot uses 5326 as its entry gate code.

Scores: boundary 2.812761; final_content -2.474740; response_mean -5.763432.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-12--A--answer-A--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.264635

</details>

**B / confident / incorrect:** Kestrel Depot uses 8971 as its entry gate code. I would give that answer without any further qualification.

Scores: boundary 2.623589; final_content -2.162877; response_mean -5.106937.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-12--A--answer-B--confident` · final content position 99 · boundary position 100 · mean-token NLL 2.605950

</details>

**B / hedged / incorrect:** My answer, subject to revision, is that Kestrel Depot uses 8971 as its entry gate code.

Scores: boundary 0.677553; final_content -4.623658; response_mean -6.065629.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-12--A--answer-B--hedged` · final content position 98 · boundary position 99 · mean-token NLL 2.359497

</details>

**B / neutral / incorrect:** Kestrel Depot uses 8971 as its entry gate code.

Scores: boundary 2.828926; final_content -2.808955; response_mean -5.502399.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-12--A--answer-B--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.642190

</details>

### World B

Fictional depot record: Kestrel Depot.
Each line names a value and the separate field it belongs to.
8971: entry code
5326: parcel code

**A / confident / incorrect:** Kestrel Depot uses 5326 as its entry gate code. I would give that answer without any further qualification.

Scores: boundary 2.735326; final_content -2.143745; response_mean -5.242461.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-12--B--answer-A--confident` · final content position 99 · boundary position 100 · mean-token NLL 2.538271

</details>

**A / hedged / incorrect:** My answer, subject to revision, is that Kestrel Depot uses 5326 as its entry gate code.

Scores: boundary 0.666129; final_content -4.686186; response_mean -6.217916.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-12--B--answer-A--hedged` · final content position 98 · boundary position 99 · mean-token NLL 2.248426

</details>

**A / neutral / incorrect:** Kestrel Depot uses 5326 as its entry gate code.

Scores: boundary 2.861772; final_content -2.486332; response_mean -5.732183.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-12--B--answer-A--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.485899

</details>

**B / confident / correct:** Kestrel Depot uses 8971 as its entry gate code. I would give that answer without any further qualification.

Scores: boundary 2.740064; final_content -2.136654; response_mean -5.094833.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-12--B--answer-B--confident` · final content position 99 · boundary position 100 · mean-token NLL 2.428834

</details>

**B / hedged / correct:** My answer, subject to revision, is that Kestrel Depot uses 8971 as its entry gate code.

Scores: boundary 0.727346; final_content -4.622244; response_mean -6.068630.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-12--B--answer-B--hedged` · final content position 98 · boundary position 99 · mean-token NLL 2.209702

</details>

**B / neutral / correct:** Kestrel Depot uses 8971 as its entry gate code.

Scores: boundary 2.876209; final_content -2.801203; response_mean -5.479792.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-12--B--answer-B--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.346014

</details>

### World omitted

Fictional depot record: Kestrel Depot.
Each line names a value and the separate field it belongs to.
8971: parcel code
5326: ticket code

**A / neutral / not labelled:** Kestrel Depot uses 5326 as its entry gate code.

Scores: boundary 2.744601; final_content -2.676496; response_mean -5.811388.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-12--omitted--answer-A--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.579014

</details>

**B / neutral / not labelled:** Kestrel Depot uses 8971 as its entry gate code.

Scores: boundary 2.830952; final_content -2.952300; response_mean -5.532418.

<details>
<summary>Tokens and exact row ID</summary>

`v3-access_code-12--omitted--answer-B--neutral` · final content position 89 · boundary position 90 · mean-token NLL 1.452029

</details>

# Confidence–Correctness Separation v3: material

All answers below are authored test stimuli, not generated responses.

Scores are frozen v1 readouts, not probabilities. Correctness refers to the supplied fictional world.

## v3-material-01

**Question:** What material forms the outer shell of Petal Lamp?

### World A

Fictional lamp record: Petal Lamp.
Each line names a value and the separate field it belongs to.
granite: outer shell
marble: display stand

**A / confident / correct:** Unequivocally, Petal Lamp has an outer shell made of granite.

Scores: boundary 2.610458; final_content -0.409624; response_mean -3.391810.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-01--A--answer-A--confident` · final content position 83 · boundary position 84 · mean-token NLL 2.328524

</details>

**A / hedged / correct:** As far as I can tell, Petal Lamp has an outer shell made of granite.

Scores: boundary 1.888659; final_content -3.998026; response_mean -5.936865.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-01--A--answer-A--hedged` · final content position 85 · boundary position 86 · mean-token NLL 2.030020

</details>

**A / neutral / correct:** Petal Lamp has an outer shell made of granite.

Scores: boundary 2.536098; final_content -2.674606; response_mean -5.429362.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-01--A--answer-A--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.365188

</details>

**B / confident / incorrect:** Unequivocally, Petal Lamp has an outer shell made of marble.

Scores: boundary 2.503757; final_content -0.728644; response_mean -3.484011.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-01--A--answer-B--confident` · final content position 83 · boundary position 84 · mean-token NLL 2.752926

</details>

**B / hedged / incorrect:** As far as I can tell, Petal Lamp has an outer shell made of marble.

Scores: boundary 1.667710; final_content -4.201100; response_mean -6.017238.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-01--A--answer-B--hedged` · final content position 85 · boundary position 86 · mean-token NLL 2.354397

</details>

**B / neutral / incorrect:** Petal Lamp has an outer shell made of marble.

Scores: boundary 2.450888; final_content -2.713045; response_mean -5.566343.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-01--A--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 2.070669

</details>

### World B

Fictional lamp record: Petal Lamp.
Each line names a value and the separate field it belongs to.
granite: display stand
marble: outer shell

**A / confident / incorrect:** Unequivocally, Petal Lamp has an outer shell made of granite.

Scores: boundary 2.675388; final_content -0.532210; response_mean -3.393236.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-01--B--answer-A--confident` · final content position 83 · boundary position 84 · mean-token NLL 2.980932

</details>

**A / hedged / incorrect:** As far as I can tell, Petal Lamp has an outer shell made of granite.

Scores: boundary 1.922257; final_content -4.132283; response_mean -5.951223.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-01--B--answer-A--hedged` · final content position 85 · boundary position 86 · mean-token NLL 2.474618

</details>

**A / neutral / incorrect:** Petal Lamp has an outer shell made of granite.

Scores: boundary 2.544676; final_content -2.786640; response_mean -5.410486.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-01--B--answer-A--neutral` · final content position 78 · boundary position 79 · mean-token NLL 2.578704

</details>

**B / confident / correct:** Unequivocally, Petal Lamp has an outer shell made of marble.

Scores: boundary 2.549928; final_content -0.916197; response_mean -3.489249.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-01--B--answer-B--confident` · final content position 83 · boundary position 84 · mean-token NLL 2.363819

</details>

**B / hedged / correct:** As far as I can tell, Petal Lamp has an outer shell made of marble.

Scores: boundary 1.655263; final_content -4.443873; response_mean -6.037605.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-01--B--answer-B--hedged` · final content position 85 · boundary position 86 · mean-token NLL 2.021711

</details>

**B / neutral / correct:** Petal Lamp has an outer shell made of marble.

Scores: boundary 2.457126; final_content -2.944118; response_mean -5.560954.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-01--B--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.601187

</details>

### World omitted

Fictional lamp record: Petal Lamp.
Each line names a value and the separate field it belongs to.
granite: packing sleeve
marble: display stand

**A / neutral / not labelled:** Petal Lamp has an outer shell made of granite.

Scores: boundary 2.446953; final_content -2.830400; response_mean -5.527604.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-01--omitted--answer-A--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.215789

</details>

**B / neutral / not labelled:** Petal Lamp has an outer shell made of marble.

Scores: boundary 2.375178; final_content -2.943028; response_mean -5.672741.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-01--omitted--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.387336

</details>

## v3-material-02

**Question:** What material forms the outer shell of Moraine Lamp?

### World A

Fictional lamp record: Moraine Lamp.
Each line names a value and the separate field it belongs to.
limestone: display stand
sandstone: outer shell

**A / confident / correct:** Moraine Lamp has an outer shell made of sandstone. I have no reservations about that answer.

Scores: boundary 1.949990; final_content -0.388322; response_mean -4.793576.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-02--A--answer-A--confident` · final content position 87 · boundary position 88 · mean-token NLL 2.557388

</details>

**A / hedged / correct:** Moraine Lamp has an outer shell made of sandstone. I have some reservations about that answer.

Scores: boundary -2.064431; final_content -8.547338; response_mean -6.911296.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-02--A--answer-A--hedged` · final content position 87 · boundary position 88 · mean-token NLL 2.660630

</details>

**A / neutral / correct:** Moraine Lamp has an outer shell made of sandstone.

Scores: boundary 2.473108; final_content -2.990005; response_mean -5.551396.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-02--A--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.103632

</details>

**B / confident / incorrect:** Moraine Lamp has an outer shell made of limestone. I have no reservations about that answer.

Scores: boundary 1.984014; final_content -0.225989; response_mean -4.780163.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-02--A--answer-B--confident` · final content position 86 · boundary position 87 · mean-token NLL 3.184401

</details>

**B / hedged / incorrect:** Moraine Lamp has an outer shell made of limestone. I have some reservations about that answer.

Scores: boundary -1.974835; final_content -8.567720; response_mean -7.048042.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-02--A--answer-B--hedged` · final content position 86 · boundary position 87 · mean-token NLL 3.271819

</details>

**B / neutral / incorrect:** Moraine Lamp has an outer shell made of limestone.

Scores: boundary 2.438851; final_content -2.622822; response_mean -5.665651.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-02--A--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.976789

</details>

### World B

Fictional lamp record: Moraine Lamp.
Each line names a value and the separate field it belongs to.
limestone: outer shell
sandstone: display stand

**A / confident / incorrect:** Moraine Lamp has an outer shell made of sandstone. I have no reservations about that answer.

Scores: boundary 2.003193; final_content -0.419225; response_mean -4.785824.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-02--B--answer-A--confident` · final content position 87 · boundary position 88 · mean-token NLL 2.991719

</details>

**A / hedged / incorrect:** Moraine Lamp has an outer shell made of sandstone. I have some reservations about that answer.

Scores: boundary -2.072492; final_content -8.593442; response_mean -6.908901.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-02--B--answer-A--hedged` · final content position 87 · boundary position 88 · mean-token NLL 3.048360

</details>

**A / neutral / incorrect:** Moraine Lamp has an outer shell made of sandstone.

Scores: boundary 2.578544; final_content -2.753444; response_mean -5.530049.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-02--B--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.932374

</details>

**B / confident / correct:** Moraine Lamp has an outer shell made of limestone. I have no reservations about that answer.

Scores: boundary 2.050988; final_content -0.146774; response_mean -4.755856.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-02--B--answer-B--confident` · final content position 86 · boundary position 87 · mean-token NLL 2.658998

</details>

**B / hedged / correct:** Moraine Lamp has an outer shell made of limestone. I have some reservations about that answer.

Scores: boundary -1.842126; final_content -8.535422; response_mean -7.035272.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-02--B--answer-B--hedged` · final content position 86 · boundary position 87 · mean-token NLL 2.780496

</details>

**B / neutral / correct:** Moraine Lamp has an outer shell made of limestone.

Scores: boundary 2.530256; final_content -2.314900; response_mean -5.647325.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-02--B--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.112793

</details>

### World omitted

Fictional lamp record: Moraine Lamp.
Each line names a value and the separate field it belongs to.
limestone: display stand
sandstone: packing sleeve

**A / neutral / not labelled:** Moraine Lamp has an outer shell made of sandstone.

Scores: boundary 2.511237; final_content -2.907708; response_mean -5.599865.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-02--omitted--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.155729

</details>

**B / neutral / not labelled:** Moraine Lamp has an outer shell made of limestone.

Scores: boundary 2.499031; final_content -2.563124; response_mean -5.681622.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-02--omitted--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.125927

</details>

## v3-material-03

**Question:** What material forms the outer shell of Fable Lamp?

### World A

Fictional lamp record: Fable Lamp.
Each line names a value and the separate field it belongs to.
oak veneer: outer shell
ash veneer: display stand

**A / confident / correct:** Fable Lamp has an outer shell made of oak veneer. I would give that answer without any further qualification.

Scores: boundary 2.803347; final_content -1.824263; response_mean -4.996424.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-03--A--answer-A--confident` · final content position 93 · boundary position 94 · mean-token NLL 2.406405

</details>

**A / hedged / correct:** My answer, subject to revision, is that Fable Lamp has an outer shell made of oak veneer.

Scores: boundary 1.189812; final_content -4.003750; response_mean -5.999669.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-03--A--answer-A--hedged` · final content position 92 · boundary position 93 · mean-token NLL 2.326113

</details>

**A / neutral / correct:** Fable Lamp has an outer shell made of oak veneer.

Scores: boundary 2.661519; final_content -2.993425; response_mean -5.574309.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-03--A--answer-A--neutral` · final content position 83 · boundary position 84 · mean-token NLL 0.622024

</details>

**B / confident / incorrect:** Fable Lamp has an outer shell made of ash veneer. I would give that answer without any further qualification.

Scores: boundary 2.824194; final_content -1.846668; response_mean -4.964372.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-03--A--answer-B--confident` · final content position 93 · boundary position 94 · mean-token NLL 2.860748

</details>

**B / hedged / incorrect:** My answer, subject to revision, is that Fable Lamp has an outer shell made of ash veneer.

Scores: boundary 1.131109; final_content -3.985233; response_mean -5.977263.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-03--A--answer-B--hedged` · final content position 92 · boundary position 93 · mean-token NLL 2.718312

</details>

**B / neutral / incorrect:** Fable Lamp has an outer shell made of ash veneer.

Scores: boundary 2.661416; final_content -2.861136; response_mean -5.533067.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-03--A--answer-B--neutral` · final content position 83 · boundary position 84 · mean-token NLL 1.395983

</details>

### World B

Fictional lamp record: Fable Lamp.
Each line names a value and the separate field it belongs to.
oak veneer: display stand
ash veneer: outer shell

**A / confident / incorrect:** Fable Lamp has an outer shell made of oak veneer. I would give that answer without any further qualification.

Scores: boundary 2.768575; final_content -1.888559; response_mean -4.993762.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-03--B--answer-A--confident` · final content position 93 · boundary position 94 · mean-token NLL 2.893795

</details>

**A / hedged / incorrect:** My answer, subject to revision, is that Fable Lamp has an outer shell made of oak veneer.

Scores: boundary 1.219620; final_content -3.897179; response_mean -6.009438.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-03--B--answer-A--hedged` · final content position 92 · boundary position 93 · mean-token NLL 2.747487

</details>

**A / neutral / incorrect:** Fable Lamp has an outer shell made of oak veneer.

Scores: boundary 2.652087; final_content -3.007312; response_mean -5.582721.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-03--B--answer-A--neutral` · final content position 83 · boundary position 84 · mean-token NLL 1.491128

</details>

**B / confident / correct:** Fable Lamp has an outer shell made of ash veneer. I would give that answer without any further qualification.

Scores: boundary 2.783406; final_content -1.906190; response_mean -4.973823.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-03--B--answer-B--confident` · final content position 93 · boundary position 94 · mean-token NLL 2.448406

</details>

**B / hedged / correct:** My answer, subject to revision, is that Fable Lamp has an outer shell made of ash veneer.

Scores: boundary 1.117337; final_content -3.914975; response_mean -5.994225.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-03--B--answer-B--hedged` · final content position 92 · boundary position 93 · mean-token NLL 2.312543

</details>

**B / neutral / correct:** Fable Lamp has an outer shell made of ash veneer.

Scores: boundary 2.616951; final_content -2.845761; response_mean -5.555843.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-03--B--answer-B--neutral` · final content position 83 · boundary position 84 · mean-token NLL 0.678428

</details>

### World omitted

Fictional lamp record: Fable Lamp.
Each line names a value and the separate field it belongs to.
oak veneer: packing sleeve
ash veneer: display stand

**A / neutral / not labelled:** Fable Lamp has an outer shell made of oak veneer.

Scores: boundary 2.720885; final_content -2.913267; response_mean -5.688689.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-03--omitted--answer-A--neutral` · final content position 83 · boundary position 84 · mean-token NLL 0.637664

</details>

**B / neutral / not labelled:** Fable Lamp has an outer shell made of ash veneer.

Scores: boundary 2.679748; final_content -2.690317; response_mean -5.642210.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-03--omitted--answer-B--neutral` · final content position 83 · boundary position 84 · mean-token NLL 0.772038

</details>

## v3-material-04

**Question:** What material forms the outer shell of Compass Lamp?

### World A

Fictional lamp record: Compass Lamp.
Each line names a value and the separate field it belongs to.
pine timber: display stand
beech timber: outer shell

**A / confident / correct:** Unequivocally, Compass Lamp has an outer shell made of beech timber.

Scores: boundary 2.847286; final_content -0.285778; response_mean -3.682687.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-04--A--answer-A--confident` · final content position 83 · boundary position 84 · mean-token NLL 2.257522

</details>

**A / hedged / correct:** As far as I can tell, Compass Lamp has an outer shell made of beech timber.

Scores: boundary 1.792639; final_content -3.633002; response_mean -5.926725.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-04--A--answer-A--hedged` · final content position 85 · boundary position 86 · mean-token NLL 1.930807

</details>

**A / neutral / correct:** Compass Lamp has an outer shell made of beech timber.

Scores: boundary 2.571444; final_content -2.467235; response_mean -5.350780.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-04--A--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.116744

</details>

**B / confident / incorrect:** Unequivocally, Compass Lamp has an outer shell made of pine timber.

Scores: boundary 2.797150; final_content -0.247719; response_mean -3.741856.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-04--A--answer-B--confident` · final content position 82 · boundary position 83 · mean-token NLL 2.972450

</details>

**B / hedged / incorrect:** As far as I can tell, Compass Lamp has an outer shell made of pine timber.

Scores: boundary 1.891372; final_content -3.675665; response_mean -6.055146.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-04--A--answer-B--hedged` · final content position 84 · boundary position 85 · mean-token NLL 2.481990

</details>

**B / neutral / incorrect:** Compass Lamp has an outer shell made of pine timber.

Scores: boundary 2.540726; final_content -2.664060; response_mean -5.503772.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-04--A--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 2.095068

</details>

### World B

Fictional lamp record: Compass Lamp.
Each line names a value and the separate field it belongs to.
pine timber: outer shell
beech timber: display stand

**A / confident / incorrect:** Unequivocally, Compass Lamp has an outer shell made of beech timber.

Scores: boundary 2.841832; final_content -0.157387; response_mean -3.657170.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-04--B--answer-A--confident` · final content position 83 · boundary position 84 · mean-token NLL 2.954469

</details>

**A / hedged / incorrect:** As far as I can tell, Compass Lamp has an outer shell made of beech timber.

Scores: boundary 1.912742; final_content -3.545393; response_mean -5.919206.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-04--B--answer-A--hedged` · final content position 85 · boundary position 86 · mean-token NLL 2.506803

</details>

**A / neutral / incorrect:** Compass Lamp has an outer shell made of beech timber.

Scores: boundary 2.650239; final_content -2.311103; response_mean -5.327028.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-04--B--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 2.116307

</details>

**B / confident / correct:** Unequivocally, Compass Lamp has an outer shell made of pine timber.

Scores: boundary 2.873185; final_content -0.042507; response_mean -3.690861.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-04--B--answer-B--confident` · final content position 82 · boundary position 83 · mean-token NLL 2.486071

</details>

**B / hedged / correct:** As far as I can tell, Compass Lamp has an outer shell made of pine timber.

Scores: boundary 1.960686; final_content -3.566131; response_mean -6.039172.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-04--B--answer-B--hedged` · final content position 84 · boundary position 85 · mean-token NLL 2.085528

</details>

**B / neutral / correct:** Compass Lamp has an outer shell made of pine timber.

Scores: boundary 2.584600; final_content -2.449686; response_mean -5.454519.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-04--B--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.245541

</details>

### World omitted

Fictional lamp record: Compass Lamp.
Each line names a value and the separate field it belongs to.
pine timber: display stand
beech timber: packing sleeve

**A / neutral / not labelled:** Compass Lamp has an outer shell made of beech timber.

Scores: boundary 2.593098; final_content -2.384770; response_mean -5.455386.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-04--omitted--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.336184

</details>

**B / neutral / not labelled:** Compass Lamp has an outer shell made of pine timber.

Scores: boundary 2.622883; final_content -2.552819; response_mean -5.584614.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-04--omitted--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.174944

</details>

## v3-material-05

**Question:** What material forms the outer shell of Seabrook Lamp?

### World A

Fictional lamp record: Seabrook Lamp.
Each line names a value and the separate field it belongs to.
mohair: outer shell
cashmere: display stand

**A / confident / correct:** Seabrook Lamp has an outer shell made of mohair. I have no reservations about that answer.

Scores: boundary 2.018723; final_content -0.476363; response_mean -4.751053.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-05--A--answer-A--confident` · final content position 95 · boundary position 96 · mean-token NLL 2.184529

</details>

**A / hedged / correct:** Seabrook Lamp has an outer shell made of mohair. I have some reservations about that answer.

Scores: boundary -2.075161; final_content -8.750361; response_mean -6.602666.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-05--A--answer-A--hedged` · final content position 95 · boundary position 96 · mean-token NLL 2.297840

</details>

**A / neutral / correct:** Seabrook Lamp has an outer shell made of mohair.

Scores: boundary 2.865051; final_content -2.468383; response_mean -5.293903.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-05--A--answer-A--neutral` · final content position 87 · boundary position 88 · mean-token NLL 0.800159

</details>

**B / confident / incorrect:** Seabrook Lamp has an outer shell made of cashmere. I have no reservations about that answer.

Scores: boundary 1.967021; final_content -0.643326; response_mean -4.558224.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-05--A--answer-B--confident` · final content position 94 · boundary position 95 · mean-token NLL 2.644774

</details>

**B / hedged / incorrect:** Seabrook Lamp has an outer shell made of cashmere. I have some reservations about that answer.

Scores: boundary -2.210517; final_content -8.849215; response_mean -6.463602.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-05--A--answer-B--hedged` · final content position 94 · boundary position 95 · mean-token NLL 2.743592

</details>

**B / neutral / incorrect:** Seabrook Lamp has an outer shell made of cashmere.

Scores: boundary 2.437789; final_content -2.663195; response_mean -4.964707.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-05--A--answer-B--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.622471

</details>

### World B

Fictional lamp record: Seabrook Lamp.
Each line names a value and the separate field it belongs to.
mohair: display stand
cashmere: outer shell

**A / confident / incorrect:** Seabrook Lamp has an outer shell made of mohair. I have no reservations about that answer.

Scores: boundary 2.046757; final_content -0.543907; response_mean -4.778856.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-05--B--answer-A--confident` · final content position 95 · boundary position 96 · mean-token NLL 2.654646

</details>

**A / hedged / incorrect:** Seabrook Lamp has an outer shell made of mohair. I have some reservations about that answer.

Scores: boundary -2.116157; final_content -8.757768; response_mean -6.631469.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-05--B--answer-A--hedged` · final content position 95 · boundary position 96 · mean-token NLL 2.752374

</details>

**A / neutral / incorrect:** Seabrook Lamp has an outer shell made of mohair.

Scores: boundary 2.808973; final_content -2.578784; response_mean -5.331468.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-05--B--answer-A--neutral` · final content position 87 · boundary position 88 · mean-token NLL 1.563192

</details>

**B / confident / correct:** Seabrook Lamp has an outer shell made of cashmere. I have no reservations about that answer.

Scores: boundary 2.010294; final_content -0.704196; response_mean -4.579843.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-05--B--answer-B--confident` · final content position 94 · boundary position 95 · mean-token NLL 2.275175

</details>

**B / hedged / correct:** Seabrook Lamp has an outer shell made of cashmere. I have some reservations about that answer.

Scores: boundary -2.221719; final_content -8.853333; response_mean -6.481141.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-05--B--answer-B--hedged` · final content position 94 · boundary position 95 · mean-token NLL 2.422961

</details>

**B / neutral / correct:** Seabrook Lamp has an outer shell made of cashmere.

Scores: boundary 2.376700; final_content -2.788097; response_mean -4.994002.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-05--B--answer-B--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.006265

</details>

### World omitted

Fictional lamp record: Seabrook Lamp.
Each line names a value and the separate field it belongs to.
mohair: packing sleeve
cashmere: display stand

**A / neutral / not labelled:** Seabrook Lamp has an outer shell made of mohair.

Scores: boundary 2.868684; final_content -2.431162; response_mean -5.462988.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-05--omitted--answer-A--neutral` · final content position 87 · boundary position 88 · mean-token NLL 0.954552

</details>

**B / neutral / not labelled:** Seabrook Lamp has an outer shell made of cashmere.

Scores: boundary 2.415403; final_content -2.685101; response_mean -5.111589.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-05--omitted--answer-B--neutral` · final content position 86 · boundary position 87 · mean-token NLL 1.169548

</details>

## v3-material-06

**Question:** What material forms the outer shell of Bramble Lamp?

### World A

Fictional lamp record: Bramble Lamp.
Each line names a value and the separate field it belongs to.
jute canvas: display stand
hemp canvas: outer shell

**A / confident / correct:** Bramble Lamp has an outer shell made of hemp canvas. I would give that answer without any further qualification.

Scores: boundary 2.646224; final_content -1.766483; response_mean -4.921201.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-06--A--answer-A--confident` · final content position 92 · boundary position 93 · mean-token NLL 2.759727

</details>

**A / hedged / correct:** My answer, subject to revision, is that Bramble Lamp has an outer shell made of hemp canvas.

Scores: boundary 0.948069; final_content -4.074482; response_mean -6.125998.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-06--A--answer-A--hedged` · final content position 90 · boundary position 91 · mean-token NLL 2.706192

</details>

**A / neutral / correct:** Bramble Lamp has an outer shell made of hemp canvas.

Scores: boundary 2.339358; final_content -2.782007; response_mean -5.441798.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-06--A--answer-A--neutral` · final content position 82 · boundary position 83 · mean-token NLL 1.150054

</details>

**B / confident / incorrect:** Bramble Lamp has an outer shell made of jute canvas. I would give that answer without any further qualification.

Scores: boundary 2.634896; final_content -1.932434; response_mean -4.970622.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-06--A--answer-B--confident` · final content position 93 · boundary position 94 · mean-token NLL 3.155312

</details>

**B / hedged / incorrect:** My answer, subject to revision, is that Bramble Lamp has an outer shell made of jute canvas.

Scores: boundary 0.901877; final_content -4.144653; response_mean -6.114427.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-06--A--answer-B--hedged` · final content position 91 · boundary position 92 · mean-token NLL 3.008047

</details>

**B / neutral / incorrect:** Bramble Lamp has an outer shell made of jute canvas.

Scores: boundary 2.170989; final_content -3.027888; response_mean -5.481374.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-06--A--answer-B--neutral` · final content position 83 · boundary position 84 · mean-token NLL 1.908266

</details>

### World B

Fictional lamp record: Bramble Lamp.
Each line names a value and the separate field it belongs to.
jute canvas: outer shell
hemp canvas: display stand

**A / confident / incorrect:** Bramble Lamp has an outer shell made of hemp canvas. I would give that answer without any further qualification.

Scores: boundary 2.642960; final_content -1.655233; response_mean -4.912441.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-06--B--answer-A--confident` · final content position 92 · boundary position 93 · mean-token NLL 3.090654

</details>

**A / hedged / incorrect:** My answer, subject to revision, is that Bramble Lamp has an outer shell made of hemp canvas.

Scores: boundary 0.901560; final_content -3.989756; response_mean -6.076024.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-06--B--answer-A--hedged` · final content position 90 · boundary position 91 · mean-token NLL 3.138777

</details>

**A / neutral / incorrect:** Bramble Lamp has an outer shell made of hemp canvas.

Scores: boundary 2.312601; final_content -2.708321; response_mean -5.405873.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-06--B--answer-A--neutral` · final content position 82 · boundary position 83 · mean-token NLL 1.747963

</details>

**B / confident / correct:** Bramble Lamp has an outer shell made of jute canvas. I would give that answer without any further qualification.

Scores: boundary 2.636041; final_content -1.911295; response_mean -4.942034.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-06--B--answer-B--confident` · final content position 93 · boundary position 94 · mean-token NLL 2.593699

</details>

**B / hedged / correct:** My answer, subject to revision, is that Bramble Lamp has an outer shell made of jute canvas.

Scores: boundary 0.962867; final_content -4.076691; response_mean -6.062036.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-06--B--answer-B--hedged` · final content position 91 · boundary position 92 · mean-token NLL 2.579190

</details>

**B / neutral / correct:** Bramble Lamp has an outer shell made of jute canvas.

Scores: boundary 2.147882; final_content -2.981405; response_mean -5.428440.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-06--B--answer-B--neutral` · final content position 83 · boundary position 84 · mean-token NLL 0.919369

</details>

### World omitted

Fictional lamp record: Bramble Lamp.
Each line names a value and the separate field it belongs to.
jute canvas: display stand
hemp canvas: packing sleeve

**A / neutral / not labelled:** Bramble Lamp has an outer shell made of hemp canvas.

Scores: boundary 2.391370; final_content -2.544852; response_mean -5.501343.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-06--omitted--answer-A--neutral` · final content position 82 · boundary position 83 · mean-token NLL 1.192598

</details>

**B / neutral / not labelled:** Bramble Lamp has an outer shell made of jute canvas.

Scores: boundary 2.246662; final_content -2.889376; response_mean -5.551137.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-06--omitted--answer-B--neutral` · final content position 83 · boundary position 84 · mean-token NLL 1.034857

</details>

## v3-material-07

**Question:** What material forms the outer shell of Hollow Lamp?

### World A

Fictional lamp record: Hollow Lamp.
Each line names a value and the separate field it belongs to.
polyester: outer shell
acrylic: display stand

**A / confident / correct:** Unequivocally, Hollow Lamp has an outer shell made of polyester.

Scores: boundary 2.538343; final_content -1.079535; response_mean -3.583509.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-07--A--answer-A--confident` · final content position 80 · boundary position 81 · mean-token NLL 2.279350

</details>

**A / hedged / correct:** As far as I can tell, Hollow Lamp has an outer shell made of polyester.

Scores: boundary 1.422175; final_content -4.643544; response_mean -6.169481.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-07--A--answer-A--hedged` · final content position 82 · boundary position 83 · mean-token NLL 2.003711

</details>

**A / neutral / correct:** Hollow Lamp has an outer shell made of polyester.

Scores: boundary 2.062512; final_content -3.493637; response_mean -5.788398.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-07--A--answer-A--neutral` · final content position 76 · boundary position 77 · mean-token NLL 0.793924

</details>

**B / confident / incorrect:** Unequivocally, Hollow Lamp has an outer shell made of acrylic.

Scores: boundary 2.472936; final_content -1.390276; response_mean -3.552330.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-07--A--answer-B--confident` · final content position 80 · boundary position 81 · mean-token NLL 2.950096

</details>

**B / hedged / incorrect:** As far as I can tell, Hollow Lamp has an outer shell made of acrylic.

Scores: boundary 1.497537; final_content -4.659241; response_mean -6.100941.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-07--A--answer-B--hedged` · final content position 82 · boundary position 83 · mean-token NLL 2.536923

</details>

**B / neutral / incorrect:** Hollow Lamp has an outer shell made of acrylic.

Scores: boundary 2.121487; final_content -3.371538; response_mean -5.703404.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-07--A--answer-B--neutral` · final content position 76 · boundary position 77 · mean-token NLL 1.806437

</details>

### World B

Fictional lamp record: Hollow Lamp.
Each line names a value and the separate field it belongs to.
polyester: display stand
acrylic: outer shell

**A / confident / incorrect:** Unequivocally, Hollow Lamp has an outer shell made of polyester.

Scores: boundary 2.501690; final_content -1.080471; response_mean -3.668021.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-07--B--answer-A--confident` · final content position 80 · boundary position 81 · mean-token NLL 2.802133

</details>

**A / hedged / incorrect:** As far as I can tell, Hollow Lamp has an outer shell made of polyester.

Scores: boundary 1.413820; final_content -4.505460; response_mean -6.176141.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-07--B--answer-A--hedged` · final content position 82 · boundary position 83 · mean-token NLL 2.471219

</details>

**A / neutral / incorrect:** Hollow Lamp has an outer shell made of polyester.

Scores: boundary 2.022919; final_content -3.555374; response_mean -5.847513.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-07--B--answer-A--neutral` · final content position 76 · boundary position 77 · mean-token NLL 1.870222

</details>

**B / confident / correct:** Unequivocally, Hollow Lamp has an outer shell made of acrylic.

Scores: boundary 2.467871; final_content -1.506824; response_mean -3.631687.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-07--B--answer-B--confident` · final content position 80 · boundary position 81 · mean-token NLL 2.174769

</details>

**B / hedged / correct:** As far as I can tell, Hollow Lamp has an outer shell made of acrylic.

Scores: boundary 1.481293; final_content -4.638900; response_mean -6.115579.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-07--B--answer-B--hedged` · final content position 82 · boundary position 83 · mean-token NLL 1.978948

</details>

**B / neutral / correct:** Hollow Lamp has an outer shell made of acrylic.

Scores: boundary 2.131097; final_content -3.437291; response_mean -5.761162.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-07--B--answer-B--neutral` · final content position 76 · boundary position 77 · mean-token NLL 0.927659

</details>

### World omitted

Fictional lamp record: Hollow Lamp.
Each line names a value and the separate field it belongs to.
polyester: packing sleeve
acrylic: display stand

**A / neutral / not labelled:** Hollow Lamp has an outer shell made of polyester.

Scores: boundary 2.157635; final_content -3.269264; response_mean -5.860137.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-07--omitted--answer-A--neutral` · final content position 76 · boundary position 77 · mean-token NLL 0.747960

</details>

**B / neutral / not labelled:** Hollow Lamp has an outer shell made of acrylic.

Scores: boundary 2.216909; final_content -3.291702; response_mean -5.782346.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-07--omitted--answer-B--neutral` · final content position 76 · boundary position 77 · mean-token NLL 0.778062

</details>

## v3-material-08

**Question:** What material forms the outer shell of Bellweather Lamp?

### World A

Fictional lamp record: Bellweather Lamp.
Each line names a value and the separate field it belongs to.
nickel: display stand
titanium: outer shell

**A / confident / correct:** Bellweather Lamp has an outer shell made of titanium. I have no reservations about that answer.

Scores: boundary 1.822151; final_content -0.340131; response_mean -4.712618.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-08--A--answer-A--confident` · final content position 87 · boundary position 88 · mean-token NLL 3.116745

</details>

**A / hedged / correct:** Bellweather Lamp has an outer shell made of titanium. I have some reservations about that answer.

Scores: boundary -2.327146; final_content -8.668110; response_mean -6.936569.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-08--A--answer-A--hedged` · final content position 87 · boundary position 88 · mean-token NLL 3.345253

</details>

**A / neutral / correct:** Bellweather Lamp has an outer shell made of titanium.

Scores: boundary 2.505631; final_content -2.593949; response_mean -5.451865.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-08--A--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.820415

</details>

**B / confident / incorrect:** Bellweather Lamp has an outer shell made of nickel. I have no reservations about that answer.

Scores: boundary 1.865632; final_content -0.313718; response_mean -4.815240.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-08--A--answer-B--confident` · final content position 87 · boundary position 88 · mean-token NLL 3.777211

</details>

**B / hedged / incorrect:** Bellweather Lamp has an outer shell made of nickel. I have some reservations about that answer.

Scores: boundary -2.251978; final_content -8.628273; response_mean -7.054876.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-08--A--answer-B--hedged` · final content position 87 · boundary position 88 · mean-token NLL 3.784882

</details>

**B / neutral / incorrect:** Bellweather Lamp has an outer shell made of nickel.

Scores: boundary 2.445848; final_content -3.197661; response_mean -5.662175.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-08--A--answer-B--neutral` · final content position 79 · boundary position 80 · mean-token NLL 2.914261

</details>

### World B

Fictional lamp record: Bellweather Lamp.
Each line names a value and the separate field it belongs to.
nickel: outer shell
titanium: display stand

**A / confident / incorrect:** Bellweather Lamp has an outer shell made of titanium. I have no reservations about that answer.

Scores: boundary 1.768069; final_content -0.403404; response_mean -4.712855.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-08--B--answer-A--confident` · final content position 87 · boundary position 88 · mean-token NLL 3.409419

</details>

**A / hedged / incorrect:** Bellweather Lamp has an outer shell made of titanium. I have some reservations about that answer.

Scores: boundary -2.313273; final_content -8.634725; response_mean -6.940034.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-08--B--answer-A--hedged` · final content position 87 · boundary position 88 · mean-token NLL 3.599433

</details>

**A / neutral / incorrect:** Bellweather Lamp has an outer shell made of titanium.

Scores: boundary 2.361945; final_content -2.693338; response_mean -5.475217.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-08--B--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 2.361264

</details>

**B / confident / correct:** Bellweather Lamp has an outer shell made of nickel. I have no reservations about that answer.

Scores: boundary 1.834372; final_content -0.314720; response_mean -4.833349.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-08--B--answer-B--confident` · final content position 87 · boundary position 88 · mean-token NLL 3.057770

</details>

**B / hedged / correct:** Bellweather Lamp has an outer shell made of nickel. I have some reservations about that answer.

Scores: boundary -2.218591; final_content -8.552304; response_mean -7.060549.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-08--B--answer-B--hedged` · final content position 87 · boundary position 88 · mean-token NLL 3.112180

</details>

**B / neutral / correct:** Bellweather Lamp has an outer shell made of nickel.

Scores: boundary 2.371043; final_content -3.229917; response_mean -5.677943.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-08--B--answer-B--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.508439

</details>

### World omitted

Fictional lamp record: Bellweather Lamp.
Each line names a value and the separate field it belongs to.
nickel: display stand
titanium: packing sleeve

**A / neutral / not labelled:** Bellweather Lamp has an outer shell made of titanium.

Scores: boundary 2.489753; final_content -2.652015; response_mean -5.601656.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-08--omitted--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.647787

</details>

**B / neutral / not labelled:** Bellweather Lamp has an outer shell made of nickel.

Scores: boundary 2.484422; final_content -3.258667; response_mean -5.800919.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-08--omitted--answer-B--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.958302

</details>

## v3-material-09

**Question:** What material forms the outer shell of Aster Lamp?

### World A

Fictional lamp record: Aster Lamp.
Each line names a value and the separate field it belongs to.
slate: outer shell
travertine: display stand

**A / confident / correct:** Aster Lamp has an outer shell made of slate. I would give that answer without any further qualification.

Scores: boundary 2.670566; final_content -1.665974; response_mean -4.783559.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-09--A--answer-A--confident` · final content position 88 · boundary position 89 · mean-token NLL 2.682351

</details>

**A / hedged / correct:** My answer, subject to revision, is that Aster Lamp has an outer shell made of slate.

Scores: boundary 0.791740; final_content -4.400456; response_mean -5.985239.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-09--A--answer-A--hedged` · final content position 86 · boundary position 87 · mean-token NLL 2.853206

</details>

**A / neutral / correct:** Aster Lamp has an outer shell made of slate.

Scores: boundary 2.169175; final_content -3.271629; response_mean -5.254311.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-09--A--answer-A--neutral` · final content position 78 · boundary position 79 · mean-token NLL 0.597874

</details>

**B / confident / incorrect:** Aster Lamp has an outer shell made of travertine. I would give that answer without any further qualification.

Scores: boundary 2.640288; final_content -1.841443; response_mean -4.576207.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-09--A--answer-B--confident` · final content position 90 · boundary position 91 · mean-token NLL 2.954028

</details>

**B / hedged / incorrect:** My answer, subject to revision, is that Aster Lamp has an outer shell made of travertine.

Scores: boundary 0.809868; final_content -4.248689; response_mean -5.701528.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-09--A--answer-B--hedged` · final content position 88 · boundary position 89 · mean-token NLL 3.137961

</details>

**B / neutral / incorrect:** Aster Lamp has an outer shell made of travertine.

Scores: boundary 2.328749; final_content -2.467111; response_mean -4.865252.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-09--A--answer-B--neutral` · final content position 80 · boundary position 81 · mean-token NLL 1.471984

</details>

### World B

Fictional lamp record: Aster Lamp.
Each line names a value and the separate field it belongs to.
slate: display stand
travertine: outer shell

**A / confident / incorrect:** Aster Lamp has an outer shell made of slate. I would give that answer without any further qualification.

Scores: boundary 2.607762; final_content -1.791672; response_mean -4.782297.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-09--B--answer-A--confident` · final content position 88 · boundary position 89 · mean-token NLL 3.881032

</details>

**A / hedged / incorrect:** My answer, subject to revision, is that Aster Lamp has an outer shell made of slate.

Scores: boundary 0.713980; final_content -4.454007; response_mean -5.987839.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-09--B--answer-A--hedged` · final content position 86 · boundary position 87 · mean-token NLL 3.953012

</details>

**A / neutral / incorrect:** Aster Lamp has an outer shell made of slate.

Scores: boundary 2.082324; final_content -3.258456; response_mean -5.229528.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-09--B--answer-A--neutral` · final content position 78 · boundary position 79 · mean-token NLL 2.988818

</details>

**B / confident / correct:** Aster Lamp has an outer shell made of travertine. I would give that answer without any further qualification.

Scores: boundary 2.556661; final_content -1.825518; response_mean -4.549176.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-09--B--answer-B--confident` · final content position 90 · boundary position 91 · mean-token NLL 2.763487

</details>

**B / hedged / correct:** My answer, subject to revision, is that Aster Lamp has an outer shell made of travertine.

Scores: boundary 0.741132; final_content -4.199568; response_mean -5.696931.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-09--B--answer-B--hedged` · final content position 88 · boundary position 89 · mean-token NLL 2.881195

</details>

**B / neutral / correct:** Aster Lamp has an outer shell made of travertine.

Scores: boundary 2.288793; final_content -2.414545; response_mean -4.837272.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-09--B--answer-B--neutral` · final content position 80 · boundary position 81 · mean-token NLL 1.204371

</details>

### World omitted

Fictional lamp record: Aster Lamp.
Each line names a value and the separate field it belongs to.
slate: packing sleeve
travertine: display stand

**A / neutral / not labelled:** Aster Lamp has an outer shell made of slate.

Scores: boundary 2.181108; final_content -3.172918; response_mean -5.333229.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-09--omitted--answer-A--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.369056

</details>

**B / neutral / not labelled:** Aster Lamp has an outer shell made of travertine.

Scores: boundary 2.282255; final_content -2.444519; response_mean -4.910149.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-09--omitted--answer-B--neutral` · final content position 80 · boundary position 81 · mean-token NLL 0.994757

</details>

## v3-material-10

**Question:** What material forms the outer shell of Rook Lamp?

### World A

Fictional lamp record: Rook Lamp.
Each line names a value and the separate field it belongs to.
denim: display stand
suede: outer shell

**A / confident / correct:** Unequivocally, Rook Lamp has an outer shell made of suede.

Scores: boundary 2.433826; final_content -1.839277; response_mean -3.649890.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-10--A--answer-A--confident` · final content position 83 · boundary position 84 · mean-token NLL 2.330910

</details>

**A / hedged / correct:** As far as I can tell, Rook Lamp has an outer shell made of suede.

Scores: boundary 1.457144; final_content -4.853252; response_mean -6.125379.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-10--A--answer-A--hedged` · final content position 85 · boundary position 86 · mean-token NLL 1.976866

</details>

**A / neutral / correct:** Rook Lamp has an outer shell made of suede.

Scores: boundary 2.452729; final_content -3.447565; response_mean -5.655314.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-10--A--answer-A--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.778835

</details>

**B / confident / incorrect:** Unequivocally, Rook Lamp has an outer shell made of denim.

Scores: boundary 2.420544; final_content -1.321231; response_mean -3.475262.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-10--A--answer-B--confident` · final content position 83 · boundary position 84 · mean-token NLL 3.074890

</details>

**B / hedged / incorrect:** As far as I can tell, Rook Lamp has an outer shell made of denim.

Scores: boundary 1.485905; final_content -4.527226; response_mean -5.976927.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-10--A--answer-B--hedged` · final content position 85 · boundary position 86 · mean-token NLL 2.604766

</details>

**B / neutral / incorrect:** Rook Lamp has an outer shell made of denim.

Scores: boundary 2.196271; final_content -3.331177; response_mean -5.421600.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-10--A--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 3.051630

</details>

### World B

Fictional lamp record: Rook Lamp.
Each line names a value and the separate field it belongs to.
denim: outer shell
suede: display stand

**A / confident / incorrect:** Unequivocally, Rook Lamp has an outer shell made of suede.

Scores: boundary 2.428389; final_content -1.699774; response_mean -3.670181.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-10--B--answer-A--confident` · final content position 83 · boundary position 84 · mean-token NLL 2.888166

</details>

**A / hedged / incorrect:** As far as I can tell, Rook Lamp has an outer shell made of suede.

Scores: boundary 1.590731; final_content -4.754465; response_mean -6.139430.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-10--B--answer-A--hedged` · final content position 85 · boundary position 86 · mean-token NLL 2.474260

</details>

**A / neutral / incorrect:** Rook Lamp has an outer shell made of suede.

Scores: boundary 2.468731; final_content -3.377432; response_mean -5.636182.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-10--B--answer-A--neutral` · final content position 78 · boundary position 79 · mean-token NLL 2.344890

</details>

**B / confident / correct:** Unequivocally, Rook Lamp has an outer shell made of denim.

Scores: boundary 2.390055; final_content -1.423412; response_mean -3.495418.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-10--B--answer-B--confident` · final content position 83 · boundary position 84 · mean-token NLL 2.189567

</details>

**B / hedged / correct:** As far as I can tell, Rook Lamp has an outer shell made of denim.

Scores: boundary 1.474087; final_content -4.554457; response_mean -5.997226.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-10--B--answer-B--hedged` · final content position 85 · boundary position 86 · mean-token NLL 1.878454

</details>

**B / neutral / correct:** Rook Lamp has an outer shell made of denim.

Scores: boundary 2.146545; final_content -3.386407; response_mean -5.402875.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-10--B--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.213432

</details>

### World omitted

Fictional lamp record: Rook Lamp.
Each line names a value and the separate field it belongs to.
denim: display stand
suede: packing sleeve

**A / neutral / not labelled:** Rook Lamp has an outer shell made of suede.

Scores: boundary 2.456739; final_content -3.404895; response_mean -5.787999.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-10--omitted--answer-A--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.386174

</details>

**B / neutral / not labelled:** Rook Lamp has an outer shell made of denim.

Scores: boundary 2.274539; final_content -3.284819; response_mean -5.537973.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-10--omitted--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.523225

</details>

## v3-material-11

**Question:** What material forms the outer shell of Dapple Lamp?

### World A

Fictional lamp record: Dapple Lamp.
Each line names a value and the separate field it belongs to.
porcelain: outer shell
terracotta: display stand

**A / confident / correct:** Dapple Lamp has an outer shell made of porcelain. I have no reservations about that answer.

Scores: boundary 2.037410; final_content -0.024139; response_mean -4.720299.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-11--A--answer-A--confident` · final content position 87 · boundary position 88 · mean-token NLL 2.822964

</details>

**A / hedged / correct:** Dapple Lamp has an outer shell made of porcelain. I have some reservations about that answer.

Scores: boundary -2.191333; final_content -8.591323; response_mean -6.961584.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-11--A--answer-A--hedged` · final content position 87 · boundary position 88 · mean-token NLL 2.915574

</details>

**A / neutral / correct:** Dapple Lamp has an outer shell made of porcelain.

Scores: boundary 2.196650; final_content -2.599104; response_mean -5.530787.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-11--A--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.253243

</details>

**B / confident / incorrect:** Dapple Lamp has an outer shell made of terracotta. I have no reservations about that answer.

Scores: boundary 1.886272; final_content -0.429444; response_mean -4.810991.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-11--A--answer-B--confident` · final content position 89 · boundary position 90 · mean-token NLL 3.232044

</details>

**B / hedged / incorrect:** Dapple Lamp has an outer shell made of terracotta. I have some reservations about that answer.

Scores: boundary -2.373104; final_content -8.729030; response_mean -6.830532.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-11--A--answer-B--hedged` · final content position 89 · boundary position 90 · mean-token NLL 3.242140

</details>

**B / neutral / incorrect:** Dapple Lamp has an outer shell made of terracotta.

Scores: boundary 2.277112; final_content -2.661081; response_mean -5.501337.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-11--A--answer-B--neutral` · final content position 81 · boundary position 82 · mean-token NLL 2.239165

</details>

### World B

Fictional lamp record: Dapple Lamp.
Each line names a value and the separate field it belongs to.
porcelain: display stand
terracotta: outer shell

**A / confident / incorrect:** Dapple Lamp has an outer shell made of porcelain. I have no reservations about that answer.

Scores: boundary 1.965188; final_content -0.118942; response_mean -4.763850.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-11--B--answer-A--confident` · final content position 87 · boundary position 88 · mean-token NLL 3.568184

</details>

**A / hedged / incorrect:** Dapple Lamp has an outer shell made of porcelain. I have some reservations about that answer.

Scores: boundary -2.261464; final_content -8.614963; response_mean -7.007858.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-11--B--answer-A--hedged` · final content position 87 · boundary position 88 · mean-token NLL 3.569759

</details>

**A / neutral / incorrect:** Dapple Lamp has an outer shell made of porcelain.

Scores: boundary 2.113797; final_content -2.715844; response_mean -5.610978.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-11--B--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 2.466692

</details>

**B / confident / correct:** Dapple Lamp has an outer shell made of terracotta. I have no reservations about that answer.

Scores: boundary 1.810402; final_content -0.570263; response_mean -4.838547.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-11--B--answer-B--confident` · final content position 89 · boundary position 90 · mean-token NLL 2.619641

</details>

**B / hedged / correct:** Dapple Lamp has an outer shell made of terracotta. I have some reservations about that answer.

Scores: boundary -2.554984; final_content -8.745795; response_mean -6.847409.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-11--B--answer-B--hedged` · final content position 89 · boundary position 90 · mean-token NLL 2.700321

</details>

**B / neutral / correct:** Dapple Lamp has an outer shell made of terracotta.

Scores: boundary 2.263071; final_content -2.772788; response_mean -5.533600.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-11--B--answer-B--neutral` · final content position 81 · boundary position 82 · mean-token NLL 1.212816

</details>

### World omitted

Fictional lamp record: Dapple Lamp.
Each line names a value and the separate field it belongs to.
porcelain: packing sleeve
terracotta: display stand

**A / neutral / not labelled:** Dapple Lamp has an outer shell made of porcelain.

Scores: boundary 2.183741; final_content -2.569599; response_mean -5.716840.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-11--omitted--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.153268

</details>

**B / neutral / not labelled:** Dapple Lamp has an outer shell made of terracotta.

Scores: boundary 2.282099; final_content -2.723430; response_mean -5.662802.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-11--omitted--answer-B--neutral` · final content position 81 · boundary position 82 · mean-token NLL 1.594214

</details>

## v3-material-12

**Question:** What material forms the outer shell of Wisp Lamp?

### World A

Fictional lamp record: Wisp Lamp.
Each line names a value and the separate field it belongs to.
fiberglass: display stand
rattan: outer shell

**A / confident / correct:** Wisp Lamp has an outer shell made of rattan. I would give that answer without any further qualification.

Scores: boundary 2.442459; final_content -1.742161; response_mean -5.257449.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-12--A--answer-A--confident` · final content position 90 · boundary position 91 · mean-token NLL 2.962619

</details>

**A / hedged / correct:** My answer, subject to revision, is that Wisp Lamp has an outer shell made of rattan.

Scores: boundary 0.619682; final_content -4.891814; response_mean -6.297374.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-12--A--answer-A--hedged` · final content position 89 · boundary position 90 · mean-token NLL 2.768971

</details>

**A / neutral / correct:** Wisp Lamp has an outer shell made of rattan.

Scores: boundary 2.209703; final_content -3.343853; response_mean -6.145202.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-12--A--answer-A--neutral` · final content position 80 · boundary position 81 · mean-token NLL 1.425879

</details>

**B / confident / incorrect:** Wisp Lamp has an outer shell made of fiberglass. I would give that answer without any further qualification.

Scores: boundary 2.467672; final_content -1.776301; response_mean -5.233517.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-12--A--answer-B--confident` · final content position 89 · boundary position 90 · mean-token NLL 3.595605

</details>

**B / hedged / incorrect:** My answer, subject to revision, is that Wisp Lamp has an outer shell made of fiberglass.

Scores: boundary 0.669082; final_content -4.186673; response_mean -6.285255.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-12--A--answer-B--hedged` · final content position 88 · boundary position 89 · mean-token NLL 3.387424

</details>

**B / neutral / incorrect:** Wisp Lamp has an outer shell made of fiberglass.

Scores: boundary 2.131440; final_content -3.067516; response_mean -6.110423.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-12--A--answer-B--neutral` · final content position 79 · boundary position 80 · mean-token NLL 2.596901

</details>

### World B

Fictional lamp record: Wisp Lamp.
Each line names a value and the separate field it belongs to.
fiberglass: outer shell
rattan: display stand

**A / confident / incorrect:** Wisp Lamp has an outer shell made of rattan. I would give that answer without any further qualification.

Scores: boundary 2.544819; final_content -1.689158; response_mean -5.266438.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-12--B--answer-A--confident` · final content position 90 · boundary position 91 · mean-token NLL 3.524123

</details>

**A / hedged / incorrect:** My answer, subject to revision, is that Wisp Lamp has an outer shell made of rattan.

Scores: boundary 0.704735; final_content -4.799651; response_mean -6.245756.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-12--B--answer-A--hedged` · final content position 89 · boundary position 90 · mean-token NLL 3.376954

</details>

**A / neutral / incorrect:** Wisp Lamp has an outer shell made of rattan.

Scores: boundary 2.244793; final_content -3.317131; response_mean -6.146340.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-12--B--answer-A--neutral` · final content position 80 · boundary position 81 · mean-token NLL 2.498353

</details>

**B / confident / correct:** Wisp Lamp has an outer shell made of fiberglass. I would give that answer without any further qualification.

Scores: boundary 2.534401; final_content -1.635522; response_mean -5.225674.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-12--B--answer-B--confident` · final content position 89 · boundary position 90 · mean-token NLL 2.863299

</details>

**B / hedged / correct:** My answer, subject to revision, is that Wisp Lamp has an outer shell made of fiberglass.

Scores: boundary 0.742660; final_content -4.137704; response_mean -6.231597.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-12--B--answer-B--hedged` · final content position 88 · boundary position 89 · mean-token NLL 2.851340

</details>

**B / neutral / correct:** Wisp Lamp has an outer shell made of fiberglass.

Scores: boundary 2.210600; final_content -3.057477; response_mean -6.100684.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-12--B--answer-B--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.229098

</details>

### World omitted

Fictional lamp record: Wisp Lamp.
Each line names a value and the separate field it belongs to.
fiberglass: display stand
rattan: packing sleeve

**A / neutral / not labelled:** Wisp Lamp has an outer shell made of rattan.

Scores: boundary 2.238583; final_content -3.350169; response_mean -6.224634.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-12--omitted--answer-A--neutral` · final content position 80 · boundary position 81 · mean-token NLL 1.548450

</details>

**B / neutral / not labelled:** Wisp Lamp has an outer shell made of fiberglass.

Scores: boundary 2.211077; final_content -2.996116; response_mean -6.171504.

<details>
<summary>Tokens and exact row ID</summary>

`v3-material-12--omitted--answer-B--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.206331

</details>

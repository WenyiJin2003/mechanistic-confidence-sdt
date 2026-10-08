# Confidence–Correctness Separation v3: room_assignment

All answers below are authored test stimuli, not generated responses.

Scores are frozen v1 readouts, not probabilities. Correctness refers to the supplied fictional world.

## v3-room_assignment-01

**Question:** In which room does Lantern Workshop hold its event?

### World A

Fictional workshop record: Lantern Workshop.
Each line names a value and the separate field it belongs to.
Amber Studio: event room
Azure Studio: staff room

**A / confident / correct:** Unequivocally, the event for Lantern Workshop takes place in Amber Studio.

Scores: boundary 3.314596; final_content -0.260903; response_mean -2.707963.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-01--A--answer-A--confident` · final content position 82 · boundary position 83 · mean-token NLL 2.062731

</details>

**A / hedged / correct:** As far as I can tell, the event for Lantern Workshop takes place in Amber Studio.

Scores: boundary 2.104024; final_content -4.109629; response_mean -5.302949.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-01--A--answer-A--hedged` · final content position 84 · boundary position 85 · mean-token NLL 2.155461

</details>

**A / neutral / correct:** The event for Lantern Workshop takes place in Amber Studio.

Scores: boundary 3.250115; final_content -2.178501; response_mean -4.374629.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-01--A--answer-A--neutral` · final content position 77 · boundary position 78 · mean-token NLL 1.872205

</details>

**B / confident / incorrect:** Unequivocally, the event for Lantern Workshop takes place in Azure Studio.

Scores: boundary 3.390847; final_content -0.341202; response_mean -2.615036.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-01--A--answer-B--confident` · final content position 82 · boundary position 83 · mean-token NLL 2.398741

</details>

**B / hedged / incorrect:** As far as I can tell, the event for Lantern Workshop takes place in Azure Studio.

Scores: boundary 2.174413; final_content -4.172455; response_mean -5.211353.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-01--A--answer-B--hedged` · final content position 84 · boundary position 85 · mean-token NLL 2.427823

</details>

**B / neutral / incorrect:** The event for Lantern Workshop takes place in Azure Studio.

Scores: boundary 3.347800; final_content -2.327099; response_mean -4.242515.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-01--A--answer-B--neutral` · final content position 77 · boundary position 78 · mean-token NLL 2.368245

</details>

### World B

Fictional workshop record: Lantern Workshop.
Each line names a value and the separate field it belongs to.
Amber Studio: staff room
Azure Studio: event room

**A / confident / incorrect:** Unequivocally, the event for Lantern Workshop takes place in Amber Studio.

Scores: boundary 3.324669; final_content -0.278183; response_mean -2.735515.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-01--B--answer-A--confident` · final content position 82 · boundary position 83 · mean-token NLL 2.369939

</details>

**A / hedged / incorrect:** As far as I can tell, the event for Lantern Workshop takes place in Amber Studio.

Scores: boundary 2.044547; final_content -4.152895; response_mean -5.337704.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-01--B--answer-A--hedged` · final content position 84 · boundary position 85 · mean-token NLL 2.545723

</details>

**A / neutral / incorrect:** The event for Lantern Workshop takes place in Amber Studio.

Scores: boundary 3.221057; final_content -2.205987; response_mean -4.417308.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-01--B--answer-A--neutral` · final content position 77 · boundary position 78 · mean-token NLL 2.438616

</details>

**B / confident / correct:** Unequivocally, the event for Lantern Workshop takes place in Azure Studio.

Scores: boundary 3.350744; final_content -0.383890; response_mean -2.625890.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-01--B--answer-B--confident` · final content position 82 · boundary position 83 · mean-token NLL 2.141241

</details>

**B / hedged / correct:** As far as I can tell, the event for Lantern Workshop takes place in Azure Studio.

Scores: boundary 2.085596; final_content -4.243067; response_mean -5.233340.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-01--B--answer-B--hedged` · final content position 84 · boundary position 85 · mean-token NLL 2.346864

</details>

**B / neutral / correct:** The event for Lantern Workshop takes place in Azure Studio.

Scores: boundary 3.275831; final_content -2.337132; response_mean -4.254628.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-01--B--answer-B--neutral` · final content position 77 · boundary position 78 · mean-token NLL 2.035544

</details>

### World omitted

Fictional workshop record: Lantern Workshop.
Each line names a value and the separate field it belongs to.
Amber Studio: break room
Azure Studio: staff room

**A / neutral / not labelled:** The event for Lantern Workshop takes place in Amber Studio.

Scores: boundary 3.285703; final_content -2.095668; response_mean -4.333790.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-01--omitted--answer-A--neutral` · final content position 77 · boundary position 78 · mean-token NLL 2.209482

</details>

**B / neutral / not labelled:** The event for Lantern Workshop takes place in Azure Studio.

Scores: boundary 3.347261; final_content -2.275868; response_mean -4.170500.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-01--omitted--answer-B--neutral` · final content position 77 · boundary position 78 · mean-token NLL 2.299124

</details>

## v3-room_assignment-02

**Question:** In which room does Ripple Workshop hold its event?

### World A

Fictional workshop record: Ripple Workshop.
Each line names a value and the separate field it belongs to.
Scarlet Studio: staff room
Indigo Studio: event room

**A / confident / correct:** The event for Ripple Workshop takes place in Indigo Studio. I have no reservations about that answer.

Scores: boundary 2.146097; final_content -0.551010; response_mean -4.053441.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-02--A--answer-A--confident` · final content position 87 · boundary position 88 · mean-token NLL 3.037124

</details>

**A / hedged / correct:** The event for Ripple Workshop takes place in Indigo Studio. I have some reservations about that answer.

Scores: boundary -2.437986; final_content -9.188444; response_mean -6.198011.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-02--A--answer-A--hedged` · final content position 87 · boundary position 88 · mean-token NLL 3.141282

</details>

**A / neutral / correct:** The event for Ripple Workshop takes place in Indigo Studio.

Scores: boundary 3.280315; final_content -2.070482; response_mean -4.427211.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-02--A--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.752878

</details>

**B / confident / incorrect:** The event for Ripple Workshop takes place in Scarlet Studio. I have no reservations about that answer.

Scores: boundary 2.263399; final_content -0.170979; response_mean -4.036363.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-02--A--answer-B--confident` · final content position 86 · boundary position 87 · mean-token NLL 3.288877

</details>

**B / hedged / incorrect:** The event for Ripple Workshop takes place in Scarlet Studio. I have some reservations about that answer.

Scores: boundary -2.381608; final_content -9.133845; response_mean -6.372230.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-02--A--answer-B--hedged` · final content position 86 · boundary position 87 · mean-token NLL 3.267385

</details>

**B / neutral / incorrect:** The event for Ripple Workshop takes place in Scarlet Studio.

Scores: boundary 3.144260; final_content -2.329943; response_mean -4.488837.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-02--A--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 2.092961

</details>

### World B

Fictional workshop record: Ripple Workshop.
Each line names a value and the separate field it belongs to.
Scarlet Studio: event room
Indigo Studio: staff room

**A / confident / incorrect:** The event for Ripple Workshop takes place in Indigo Studio. I have no reservations about that answer.

Scores: boundary 2.168904; final_content -0.561312; response_mean -4.021189.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-02--B--answer-A--confident` · final content position 87 · boundary position 88 · mean-token NLL 3.236212

</details>

**A / hedged / incorrect:** The event for Ripple Workshop takes place in Indigo Studio. I have some reservations about that answer.

Scores: boundary -2.406520; final_content -9.249119; response_mean -6.154020.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-02--B--answer-A--hedged` · final content position 87 · boundary position 88 · mean-token NLL 3.330413

</details>

**A / neutral / incorrect:** The event for Ripple Workshop takes place in Indigo Studio.

Scores: boundary 3.308259; final_content -2.141012; response_mean -4.362852.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-02--B--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 2.220704

</details>

**B / confident / correct:** The event for Ripple Workshop takes place in Scarlet Studio. I have no reservations about that answer.

Scores: boundary 2.216309; final_content -0.154519; response_mean -3.973546.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-02--B--answer-B--confident` · final content position 86 · boundary position 87 · mean-token NLL 2.988452

</details>

**B / hedged / correct:** The event for Ripple Workshop takes place in Scarlet Studio. I have some reservations about that answer.

Scores: boundary -2.352904; final_content -9.145567; response_mean -6.329826.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-02--B--answer-B--hedged` · final content position 86 · boundary position 87 · mean-token NLL 2.976508

</details>

**B / neutral / correct:** The event for Ripple Workshop takes place in Scarlet Studio.

Scores: boundary 3.222968; final_content -2.383487; response_mean -4.426172.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-02--B--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.573170

</details>

### World omitted

Fictional workshop record: Ripple Workshop.
Each line names a value and the separate field it belongs to.
Scarlet Studio: staff room
Indigo Studio: break room

**A / neutral / not labelled:** The event for Ripple Workshop takes place in Indigo Studio.

Scores: boundary 3.384466; final_content -2.052543; response_mean -4.363581.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-02--omitted--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.831434

</details>

**B / neutral / not labelled:** The event for Ripple Workshop takes place in Scarlet Studio.

Scores: boundary 3.285736; final_content -2.206450; response_mean -4.409509.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-02--omitted--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.996152

</details>

## v3-room_assignment-03

**Question:** In which room does Harbor Workshop hold its event?

### World A

Fictional workshop record: Harbor Workshop.
Each line names a value and the separate field it belongs to.
Ivory Studio: event room
Sienna Studio: staff room

**A / confident / correct:** The event for Harbor Workshop takes place in Ivory Studio. I would give that answer without any further qualification.

Scores: boundary 2.919706; final_content -2.099895; response_mean -4.598909.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-03--A--answer-A--confident` · final content position 89 · boundary position 90 · mean-token NLL 3.468979

</details>

**A / hedged / correct:** My answer, subject to revision, is that the event for Harbor Workshop takes place in Ivory Studio.

Scores: boundary 1.282900; final_content -3.918982; response_mean -5.770407.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-03--A--answer-A--hedged` · final content position 88 · boundary position 89 · mean-token NLL 2.871914

</details>

**A / neutral / correct:** The event for Harbor Workshop takes place in Ivory Studio.

Scores: boundary 3.175480; final_content -2.458788; response_mean -4.720878.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-03--A--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 2.430050

</details>

**B / confident / incorrect:** The event for Harbor Workshop takes place in Sienna Studio. I would give that answer without any further qualification.

Scores: boundary 2.900942; final_content -2.103034; response_mean -4.460940.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-03--A--answer-B--confident` · final content position 90 · boundary position 91 · mean-token NLL 3.421927

</details>

**B / hedged / incorrect:** My answer, subject to revision, is that the event for Harbor Workshop takes place in Sienna Studio.

Scores: boundary 1.464279; final_content -4.053795; response_mean -5.560801.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-03--A--answer-B--hedged` · final content position 89 · boundary position 90 · mean-token NLL 2.901511

</details>

**B / neutral / incorrect:** The event for Harbor Workshop takes place in Sienna Studio.

Scores: boundary 3.169571; final_content -2.402850; response_mean -4.492897.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-03--A--answer-B--neutral` · final content position 80 · boundary position 81 · mean-token NLL 2.490123

</details>

### World B

Fictional workshop record: Harbor Workshop.
Each line names a value and the separate field it belongs to.
Ivory Studio: staff room
Sienna Studio: event room

**A / confident / incorrect:** The event for Harbor Workshop takes place in Ivory Studio. I would give that answer without any further qualification.

Scores: boundary 2.916926; final_content -2.134784; response_mean -4.638249.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-03--B--answer-A--confident` · final content position 89 · boundary position 90 · mean-token NLL 3.613602

</details>

**A / hedged / incorrect:** My answer, subject to revision, is that the event for Harbor Workshop takes place in Ivory Studio.

Scores: boundary 1.200433; final_content -3.972360; response_mean -5.851132.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-03--B--answer-A--hedged` · final content position 88 · boundary position 89 · mean-token NLL 3.033638

</details>

**A / neutral / incorrect:** The event for Harbor Workshop takes place in Ivory Studio.

Scores: boundary 3.127730; final_content -2.429092; response_mean -4.798510.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-03--B--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 2.697670

</details>

**B / confident / correct:** The event for Harbor Workshop takes place in Sienna Studio. I would give that answer without any further qualification.

Scores: boundary 2.854263; final_content -2.145237; response_mean -4.526758.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-03--B--answer-B--confident` · final content position 90 · boundary position 91 · mean-token NLL 3.355860

</details>

**B / hedged / correct:** My answer, subject to revision, is that the event for Harbor Workshop takes place in Sienna Studio.

Scores: boundary 1.389661; final_content -4.140378; response_mean -5.642907.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-03--B--answer-B--hedged` · final content position 89 · boundary position 90 · mean-token NLL 2.817756

</details>

**B / neutral / correct:** The event for Harbor Workshop takes place in Sienna Studio.

Scores: boundary 3.106558; final_content -2.406487; response_mean -4.579677.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-03--B--answer-B--neutral` · final content position 80 · boundary position 81 · mean-token NLL 2.295965

</details>

### World omitted

Fictional workshop record: Harbor Workshop.
Each line names a value and the separate field it belongs to.
Ivory Studio: break room
Sienna Studio: staff room

**A / neutral / not labelled:** The event for Harbor Workshop takes place in Ivory Studio.

Scores: boundary 3.314338; final_content -2.363483; response_mean -4.737154.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-03--omitted--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 2.575793

</details>

**B / neutral / not labelled:** The event for Harbor Workshop takes place in Sienna Studio.

Scores: boundary 3.250299; final_content -2.263667; response_mean -4.484703.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-03--omitted--answer-B--neutral` · final content position 80 · boundary position 81 · mean-token NLL 2.530210

</details>

## v3-room_assignment-04

**Question:** In which room does Pebble Workshop hold its event?

### World A

Fictional workshop record: Pebble Workshop.
Each line names a value and the separate field it belongs to.
Ochre Studio: staff room
Coral Studio: event room

**A / confident / correct:** Unequivocally, the event for Pebble Workshop takes place in Coral Studio.

Scores: boundary 3.497498; final_content -0.186869; response_mean -2.637457.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-04--A--answer-A--confident` · final content position 87 · boundary position 88 · mean-token NLL 2.118996

</details>

**A / hedged / correct:** As far as I can tell, the event for Pebble Workshop takes place in Coral Studio.

Scores: boundary 2.196551; final_content -4.084634; response_mean -5.261629.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-04--A--answer-A--hedged` · final content position 89 · boundary position 90 · mean-token NLL 2.469866

</details>

**A / neutral / correct:** The event for Pebble Workshop takes place in Coral Studio.

Scores: boundary 3.117877; final_content -2.074056; response_mean -4.214867.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-04--A--answer-A--neutral` · final content position 82 · boundary position 83 · mean-token NLL 2.173291

</details>

**B / confident / incorrect:** Unequivocally, the event for Pebble Workshop takes place in Ochre Studio.

Scores: boundary 3.513215; final_content -0.402921; response_mean -2.580598.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-04--A--answer-B--confident` · final content position 89 · boundary position 90 · mean-token NLL 2.153065

</details>

**B / hedged / incorrect:** As far as I can tell, the event for Pebble Workshop takes place in Ochre Studio.

Scores: boundary 2.331565; final_content -4.536414; response_mean -5.072159.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-04--A--answer-B--hedged` · final content position 91 · boundary position 92 · mean-token NLL 2.424117

</details>

**B / neutral / incorrect:** The event for Pebble Workshop takes place in Ochre Studio.

Scores: boundary 3.403965; final_content -2.521793; response_mean -4.067411.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-04--A--answer-B--neutral` · final content position 84 · boundary position 85 · mean-token NLL 2.159042

</details>

### World B

Fictional workshop record: Pebble Workshop.
Each line names a value and the separate field it belongs to.
Ochre Studio: event room
Coral Studio: staff room

**A / confident / incorrect:** Unequivocally, the event for Pebble Workshop takes place in Coral Studio.

Scores: boundary 3.519909; final_content -0.135097; response_mean -2.564442.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-04--B--answer-A--confident` · final content position 87 · boundary position 88 · mean-token NLL 2.109685

</details>

**A / hedged / incorrect:** As far as I can tell, the event for Pebble Workshop takes place in Coral Studio.

Scores: boundary 2.219637; final_content -4.016682; response_mean -5.231264.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-04--B--answer-A--hedged` · final content position 89 · boundary position 90 · mean-token NLL 2.349483

</details>

**A / neutral / incorrect:** The event for Pebble Workshop takes place in Coral Studio.

Scores: boundary 3.200830; final_content -2.076821; response_mean -4.173246.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-04--B--answer-A--neutral` · final content position 82 · boundary position 83 · mean-token NLL 2.184619

</details>

**B / confident / correct:** Unequivocally, the event for Pebble Workshop takes place in Ochre Studio.

Scores: boundary 3.578250; final_content -0.355833; response_mean -2.492385.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-04--B--answer-B--confident` · final content position 89 · boundary position 90 · mean-token NLL 1.924396

</details>

**B / hedged / correct:** As far as I can tell, the event for Pebble Workshop takes place in Ochre Studio.

Scores: boundary 2.450637; final_content -4.486216; response_mean -5.022189.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-04--B--answer-B--hedged` · final content position 91 · boundary position 92 · mean-token NLL 2.131044

</details>

**B / neutral / correct:** The event for Pebble Workshop takes place in Ochre Studio.

Scores: boundary 3.374676; final_content -2.516228; response_mean -3.980405.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-04--B--answer-B--neutral` · final content position 84 · boundary position 85 · mean-token NLL 1.868930

</details>

### World omitted

Fictional workshop record: Pebble Workshop.
Each line names a value and the separate field it belongs to.
Ochre Studio: staff room
Coral Studio: break room

**A / neutral / not labelled:** The event for Pebble Workshop takes place in Coral Studio.

Scores: boundary 3.266162; final_content -2.025577; response_mean -4.147369.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-04--omitted--answer-A--neutral` · final content position 82 · boundary position 83 · mean-token NLL 2.363215

</details>

**B / neutral / not labelled:** The event for Pebble Workshop takes place in Ochre Studio.

Scores: boundary 3.453684; final_content -2.455749; response_mean -3.993585.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-04--omitted--answer-B--neutral` · final content position 84 · boundary position 85 · mean-token NLL 1.818885

</details>

## v3-room_assignment-05

**Question:** In which room does Saffron Workshop hold its event?

### World A

Fictional workshop record: Saffron Workshop.
Each line names a value and the separate field it belongs to.
Silver Studio: event room
Golden Studio: staff room

**A / confident / correct:** The event for Saffron Workshop takes place in Silver Studio. I have no reservations about that answer.

Scores: boundary 2.233393; final_content -0.332340; response_mean -3.821870.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-05--A--answer-A--confident` · final content position 90 · boundary position 91 · mean-token NLL 2.850880

</details>

**A / hedged / correct:** The event for Saffron Workshop takes place in Silver Studio. I have some reservations about that answer.

Scores: boundary -2.454561; final_content -9.118997; response_mean -5.920498.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-05--A--answer-A--hedged` · final content position 90 · boundary position 91 · mean-token NLL 2.852521

</details>

**A / neutral / correct:** The event for Saffron Workshop takes place in Silver Studio.

Scores: boundary 3.133484; final_content -2.163892; response_mean -4.126810.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-05--A--answer-A--neutral` · final content position 82 · boundary position 83 · mean-token NLL 1.546571

</details>

**B / confident / incorrect:** The event for Saffron Workshop takes place in Golden Studio. I have no reservations about that answer.

Scores: boundary 2.176367; final_content -0.513544; response_mean -3.783322.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-05--A--answer-B--confident` · final content position 90 · boundary position 91 · mean-token NLL 3.072233

</details>

**B / hedged / incorrect:** The event for Saffron Workshop takes place in Golden Studio. I have some reservations about that answer.

Scores: boundary -2.491262; final_content -9.140409; response_mean -5.843447.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-05--A--answer-B--hedged` · final content position 90 · boundary position 91 · mean-token NLL 3.112238

</details>

**B / neutral / incorrect:** The event for Saffron Workshop takes place in Golden Studio.

Scores: boundary 3.171927; final_content -2.008390; response_mean -4.042548.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-05--A--answer-B--neutral` · final content position 82 · boundary position 83 · mean-token NLL 2.006824

</details>

### World B

Fictional workshop record: Saffron Workshop.
Each line names a value and the separate field it belongs to.
Silver Studio: staff room
Golden Studio: event room

**A / confident / incorrect:** The event for Saffron Workshop takes place in Silver Studio. I have no reservations about that answer.

Scores: boundary 2.227444; final_content -0.349785; response_mean -3.844342.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-05--B--answer-A--confident` · final content position 90 · boundary position 91 · mean-token NLL 2.983692

</details>

**A / hedged / incorrect:** The event for Saffron Workshop takes place in Silver Studio. I have some reservations about that answer.

Scores: boundary -2.579799; final_content -9.156508; response_mean -5.943181.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-05--B--answer-A--hedged` · final content position 90 · boundary position 91 · mean-token NLL 2.992385

</details>

**A / neutral / incorrect:** The event for Saffron Workshop takes place in Silver Studio.

Scores: boundary 3.147060; final_content -2.158246; response_mean -4.166183.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-05--B--answer-A--neutral` · final content position 82 · boundary position 83 · mean-token NLL 1.846682

</details>

**B / confident / correct:** The event for Saffron Workshop takes place in Golden Studio. I have no reservations about that answer.

Scores: boundary 2.187778; final_content -0.444217; response_mean -3.792162.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-05--B--answer-B--confident` · final content position 90 · boundary position 91 · mean-token NLL 2.965531

</details>

**B / hedged / correct:** The event for Saffron Workshop takes place in Golden Studio. I have some reservations about that answer.

Scores: boundary -2.592776; final_content -9.137411; response_mean -5.873536.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-05--B--answer-B--hedged` · final content position 90 · boundary position 91 · mean-token NLL 3.045784

</details>

**B / neutral / correct:** The event for Saffron Workshop takes place in Golden Studio.

Scores: boundary 3.098080; final_content -2.005539; response_mean -4.066525.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-05--B--answer-B--neutral` · final content position 82 · boundary position 83 · mean-token NLL 1.806369

</details>

### World omitted

Fictional workshop record: Saffron Workshop.
Each line names a value and the separate field it belongs to.
Silver Studio: break room
Golden Studio: staff room

**A / neutral / not labelled:** The event for Saffron Workshop takes place in Silver Studio.

Scores: boundary 3.217638; final_content -2.085602; response_mean -4.102575.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-05--omitted--answer-A--neutral` · final content position 82 · boundary position 83 · mean-token NLL 1.723451

</details>

**B / neutral / not labelled:** The event for Saffron Workshop takes place in Golden Studio.

Scores: boundary 3.158004; final_content -1.971377; response_mean -4.005345.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-05--omitted--answer-B--neutral` · final content position 82 · boundary position 83 · mean-token NLL 1.865653

</details>

## v3-room_assignment-06

**Question:** In which room does Tinsel Workshop hold its event?

### World A

Fictional workshop record: Tinsel Workshop.
Each line names a value and the separate field it belongs to.
Crimson Studio: staff room
Violet Studio: event room

**A / confident / correct:** The event for Tinsel Workshop takes place in Violet Studio. I would give that answer without any further qualification.

Scores: boundary 2.769238; final_content -2.238442; response_mean -4.632246.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-06--A--answer-A--confident` · final content position 95 · boundary position 96 · mean-token NLL 3.077427

</details>

**A / hedged / correct:** My answer, subject to revision, is that the event for Tinsel Workshop takes place in Violet Studio.

Scores: boundary 1.389815; final_content -3.872634; response_mean -5.699243.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-06--A--answer-A--hedged` · final content position 94 · boundary position 95 · mean-token NLL 2.572685

</details>

**A / neutral / correct:** The event for Tinsel Workshop takes place in Violet Studio.

Scores: boundary 3.252972; final_content -2.070442; response_mean -4.729419.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-06--A--answer-A--neutral` · final content position 85 · boundary position 86 · mean-token NLL 1.551259

</details>

**B / confident / incorrect:** The event for Tinsel Workshop takes place in Crimson Studio. I would give that answer without any further qualification.

Scores: boundary 2.751819; final_content -2.251582; response_mean -4.503482.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-06--A--answer-B--confident` · final content position 95 · boundary position 96 · mean-token NLL 3.185872

</details>

**B / hedged / incorrect:** My answer, subject to revision, is that the event for Tinsel Workshop takes place in Crimson Studio.

Scores: boundary 1.364833; final_content -3.797285; response_mean -5.557999.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-06--A--answer-B--hedged` · final content position 94 · boundary position 95 · mean-token NLL 2.693138

</details>

**B / neutral / incorrect:** The event for Tinsel Workshop takes place in Crimson Studio.

Scores: boundary 3.133476; final_content -2.187724; response_mean -4.466050.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-06--A--answer-B--neutral` · final content position 85 · boundary position 86 · mean-token NLL 1.841067

</details>

### World B

Fictional workshop record: Tinsel Workshop.
Each line names a value and the separate field it belongs to.
Crimson Studio: event room
Violet Studio: staff room

**A / confident / incorrect:** The event for Tinsel Workshop takes place in Violet Studio. I would give that answer without any further qualification.

Scores: boundary 2.798267; final_content -2.237495; response_mean -4.609082.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-06--B--answer-A--confident` · final content position 95 · boundary position 96 · mean-token NLL 3.307011

</details>

**A / hedged / incorrect:** My answer, subject to revision, is that the event for Tinsel Workshop takes place in Violet Studio.

Scores: boundary 1.350475; final_content -3.878434; response_mean -5.671790.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-06--B--answer-A--hedged` · final content position 94 · boundary position 95 · mean-token NLL 2.828182

</details>

**A / neutral / incorrect:** The event for Tinsel Workshop takes place in Violet Studio.

Scores: boundary 3.339264; final_content -2.015360; response_mean -4.689885.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-06--B--answer-A--neutral` · final content position 85 · boundary position 86 · mean-token NLL 2.018057

</details>

**B / confident / correct:** The event for Tinsel Workshop takes place in Crimson Studio. I would give that answer without any further qualification.

Scores: boundary 2.846848; final_content -2.267296; response_mean -4.478938.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-06--B--answer-B--confident` · final content position 95 · boundary position 96 · mean-token NLL 2.834054

</details>

**B / hedged / correct:** My answer, subject to revision, is that the event for Tinsel Workshop takes place in Crimson Studio.

Scores: boundary 1.313496; final_content -3.751783; response_mean -5.532017.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-06--B--answer-B--hedged` · final content position 94 · boundary position 95 · mean-token NLL 2.434671

</details>

**B / neutral / correct:** The event for Tinsel Workshop takes place in Crimson Studio.

Scores: boundary 3.256063; final_content -2.124041; response_mean -4.435055.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-06--B--answer-B--neutral` · final content position 85 · boundary position 86 · mean-token NLL 1.213941

</details>

### World omitted

Fictional workshop record: Tinsel Workshop.
Each line names a value and the separate field it belongs to.
Crimson Studio: staff room
Violet Studio: break room

**A / neutral / not labelled:** The event for Tinsel Workshop takes place in Violet Studio.

Scores: boundary 3.297690; final_content -2.164146; response_mean -4.753656.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-06--omitted--answer-A--neutral` · final content position 85 · boundary position 86 · mean-token NLL 1.714749

</details>

**B / neutral / not labelled:** The event for Tinsel Workshop takes place in Crimson Studio.

Scores: boundary 3.322464; final_content -2.120182; response_mean -4.468358.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-06--omitted--answer-B--neutral` · final content position 85 · boundary position 86 · mean-token NLL 1.646584

</details>

## v3-room_assignment-07

**Question:** In which room does Loom Workshop hold its event?

### World A

Fictional workshop record: Loom Workshop.
Each line names a value and the separate field it belongs to.
Honey Studio: event room
Rust Studio: staff room

**A / confident / correct:** Unequivocally, the event for Loom Workshop takes place in Honey Studio.

Scores: boundary 3.420183; final_content -0.370956; response_mean -2.828907.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-07--A--answer-A--confident` · final content position 86 · boundary position 87 · mean-token NLL 2.073337

</details>

**A / hedged / correct:** As far as I can tell, the event for Loom Workshop takes place in Honey Studio.

Scores: boundary 2.056393; final_content -4.314649; response_mean -5.527135.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-07--A--answer-A--hedged` · final content position 88 · boundary position 89 · mean-token NLL 2.356306

</details>

**A / neutral / correct:** The event for Loom Workshop takes place in Honey Studio.

Scores: boundary 3.191702; final_content -2.229724; response_mean -4.677635.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-07--A--answer-A--neutral` · final content position 81 · boundary position 82 · mean-token NLL 2.013456

</details>

**B / confident / incorrect:** Unequivocally, the event for Loom Workshop takes place in Rust Studio.

Scores: boundary 3.390245; final_content -0.219694; response_mean -2.786144.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-07--A--answer-B--confident` · final content position 86 · boundary position 87 · mean-token NLL 2.352634

</details>

**B / hedged / incorrect:** As far as I can tell, the event for Loom Workshop takes place in Rust Studio.

Scores: boundary 2.048166; final_content -4.109876; response_mean -5.523362.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-07--A--answer-B--hedged` · final content position 88 · boundary position 89 · mean-token NLL 2.521695

</details>

**B / neutral / incorrect:** The event for Loom Workshop takes place in Rust Studio.

Scores: boundary 3.151549; final_content -2.206820; response_mean -4.629210.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-07--A--answer-B--neutral` · final content position 81 · boundary position 82 · mean-token NLL 2.460110

</details>

### World B

Fictional workshop record: Loom Workshop.
Each line names a value and the separate field it belongs to.
Honey Studio: staff room
Rust Studio: event room

**A / confident / incorrect:** Unequivocally, the event for Loom Workshop takes place in Honey Studio.

Scores: boundary 3.459398; final_content -0.389353; response_mean -2.880323.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-07--B--answer-A--confident` · final content position 86 · boundary position 87 · mean-token NLL 2.282591

</details>

**A / hedged / incorrect:** As far as I can tell, the event for Loom Workshop takes place in Honey Studio.

Scores: boundary 2.123701; final_content -4.340365; response_mean -5.563193.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-07--B--answer-A--hedged` · final content position 88 · boundary position 89 · mean-token NLL 2.655130

</details>

**A / neutral / incorrect:** The event for Loom Workshop takes place in Honey Studio.

Scores: boundary 3.226125; final_content -2.271521; response_mean -4.711025.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-07--B--answer-A--neutral` · final content position 81 · boundary position 82 · mean-token NLL 2.365653

</details>

**B / confident / correct:** Unequivocally, the event for Loom Workshop takes place in Rust Studio.

Scores: boundary 3.367157; final_content -0.329289; response_mean -2.846382.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-07--B--answer-B--confident` · final content position 86 · boundary position 87 · mean-token NLL 2.019308

</details>

**B / hedged / correct:** As far as I can tell, the event for Loom Workshop takes place in Rust Studio.

Scores: boundary 2.035163; final_content -4.262474; response_mean -5.583230.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-07--B--answer-B--hedged` · final content position 88 · boundary position 89 · mean-token NLL 2.441973

</details>

**B / neutral / correct:** The event for Loom Workshop takes place in Rust Studio.

Scores: boundary 3.151232; final_content -2.242435; response_mean -4.700029.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-07--B--answer-B--neutral` · final content position 81 · boundary position 82 · mean-token NLL 1.902436

</details>

### World omitted

Fictional workshop record: Loom Workshop.
Each line names a value and the separate field it belongs to.
Honey Studio: break room
Rust Studio: staff room

**A / neutral / not labelled:** The event for Loom Workshop takes place in Honey Studio.

Scores: boundary 3.347675; final_content -2.114800; response_mean -4.672151.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-07--omitted--answer-A--neutral` · final content position 81 · boundary position 82 · mean-token NLL 2.063515

</details>

**B / neutral / not labelled:** The event for Loom Workshop takes place in Rust Studio.

Scores: boundary 3.197174; final_content -2.105355; response_mean -4.636548.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-07--omitted--answer-B--neutral` · final content position 81 · boundary position 82 · mean-token NLL 2.084616

</details>

## v3-room_assignment-08

**Question:** In which room does Marigold Workshop hold its event?

### World A

Fictional workshop record: Marigold Workshop.
Each line names a value and the separate field it belongs to.
Teal Studio: staff room
Pearl Studio: event room

**A / confident / correct:** The event for Marigold Workshop takes place in Pearl Studio. I have no reservations about that answer.

Scores: boundary 2.268799; final_content -0.308693; response_mean -3.826438.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-08--A--answer-A--confident` · final content position 92 · boundary position 93 · mean-token NLL 2.892950

</details>

**A / hedged / correct:** The event for Marigold Workshop takes place in Pearl Studio. I have some reservations about that answer.

Scores: boundary -2.423239; final_content -9.360359; response_mean -5.939873.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-08--A--answer-A--hedged` · final content position 92 · boundary position 93 · mean-token NLL 2.951824

</details>

**A / neutral / correct:** The event for Marigold Workshop takes place in Pearl Studio.

Scores: boundary 3.305349; final_content -1.662420; response_mean -4.143779.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-08--A--answer-A--neutral` · final content position 84 · boundary position 85 · mean-token NLL 1.532001

</details>

**B / confident / incorrect:** The event for Marigold Workshop takes place in Teal Studio. I have no reservations about that answer.

Scores: boundary 2.445722; final_content -0.254817; response_mean -3.978947.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-08--A--answer-B--confident` · final content position 93 · boundary position 94 · mean-token NLL 2.998644

</details>

**B / hedged / incorrect:** The event for Marigold Workshop takes place in Teal Studio. I have some reservations about that answer.

Scores: boundary -2.319370; final_content -9.305171; response_mean -6.018972.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-08--A--answer-B--hedged` · final content position 93 · boundary position 94 · mean-token NLL 2.968680

</details>

**B / neutral / incorrect:** The event for Marigold Workshop takes place in Teal Studio.

Scores: boundary 3.427950; final_content -2.373743; response_mean -4.338156.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-08--A--answer-B--neutral` · final content position 85 · boundary position 86 · mean-token NLL 1.789219

</details>

### World B

Fictional workshop record: Marigold Workshop.
Each line names a value and the separate field it belongs to.
Teal Studio: event room
Pearl Studio: staff room

**A / confident / incorrect:** The event for Marigold Workshop takes place in Pearl Studio. I have no reservations about that answer.

Scores: boundary 2.340475; final_content -0.308710; response_mean -3.835934.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-08--B--answer-A--confident` · final content position 92 · boundary position 93 · mean-token NLL 2.983054

</details>

**A / hedged / incorrect:** The event for Marigold Workshop takes place in Pearl Studio. I have some reservations about that answer.

Scores: boundary -2.371143; final_content -9.308013; response_mean -5.942054.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-08--B--answer-A--hedged` · final content position 92 · boundary position 93 · mean-token NLL 3.015615

</details>

**A / neutral / incorrect:** The event for Marigold Workshop takes place in Pearl Studio.

Scores: boundary 3.333026; final_content -1.808998; response_mean -4.157647.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-08--B--answer-A--neutral` · final content position 84 · boundary position 85 · mean-token NLL 1.762377

</details>

**B / confident / correct:** The event for Marigold Workshop takes place in Teal Studio. I have no reservations about that answer.

Scores: boundary 2.467527; final_content -0.291359; response_mean -3.955139.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-08--B--answer-B--confident` · final content position 93 · boundary position 94 · mean-token NLL 2.626607

</details>

**B / hedged / correct:** The event for Marigold Workshop takes place in Teal Studio. I have some reservations about that answer.

Scores: boundary -2.296293; final_content -9.219059; response_mean -6.007794.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-08--B--answer-B--hedged` · final content position 93 · boundary position 94 · mean-token NLL 2.604174

</details>

**B / neutral / correct:** The event for Marigold Workshop takes place in Teal Studio.

Scores: boundary 3.405277; final_content -2.507291; response_mean -4.321617.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-08--B--answer-B--neutral` · final content position 85 · boundary position 86 · mean-token NLL 1.236165

</details>

### World omitted

Fictional workshop record: Marigold Workshop.
Each line names a value and the separate field it belongs to.
Teal Studio: staff room
Pearl Studio: break room

**A / neutral / not labelled:** The event for Marigold Workshop takes place in Pearl Studio.

Scores: boundary 3.340713; final_content -1.694825; response_mean -4.138657.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-08--omitted--answer-A--neutral` · final content position 84 · boundary position 85 · mean-token NLL 1.834332

</details>

**B / neutral / not labelled:** The event for Marigold Workshop takes place in Teal Studio.

Scores: boundary 3.516646; final_content -2.365656; response_mean -4.314436.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-08--omitted--answer-B--neutral` · final content position 85 · boundary position 86 · mean-token NLL 1.623496

</details>

## v3-room_assignment-09

**Question:** In which room does Copperleaf Workshop hold its event?

### World A

Fictional workshop record: Copperleaf Workshop.
Each line names a value and the separate field it belongs to.
Olive Studio: event room
Plum Studio: staff room

**A / confident / correct:** The event for Copperleaf Workshop takes place in Olive Studio. I would give that answer without any further qualification.

Scores: boundary 2.799106; final_content -2.042565; response_mean -4.339234.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-09--A--answer-A--confident` · final content position 91 · boundary position 92 · mean-token NLL 3.147947

</details>

**A / hedged / correct:** My answer, subject to revision, is that the event for Copperleaf Workshop takes place in Olive Studio.

Scores: boundary 1.567397; final_content -3.722798; response_mean -5.468004.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-09--A--answer-A--hedged` · final content position 90 · boundary position 91 · mean-token NLL 2.774673

</details>

**A / neutral / correct:** The event for Copperleaf Workshop takes place in Olive Studio.

Scores: boundary 3.342320; final_content -2.059054; response_mean -4.326654.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-09--A--answer-A--neutral` · final content position 81 · boundary position 82 · mean-token NLL 1.890861

</details>

**B / confident / incorrect:** The event for Copperleaf Workshop takes place in Plum Studio. I would give that answer without any further qualification.

Scores: boundary 2.893146; final_content -2.083440; response_mean -4.406912.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-09--A--answer-B--confident` · final content position 91 · boundary position 92 · mean-token NLL 3.569355

</details>

**B / hedged / incorrect:** My answer, subject to revision, is that the event for Copperleaf Workshop takes place in Plum Studio.

Scores: boundary 1.562090; final_content -3.463730; response_mean -5.512947.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-09--A--answer-B--hedged` · final content position 90 · boundary position 91 · mean-token NLL 2.962046

</details>

**B / neutral / incorrect:** The event for Copperleaf Workshop takes place in Plum Studio.

Scores: boundary 3.405388; final_content -1.751592; response_mean -4.415140.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-09--A--answer-B--neutral` · final content position 81 · boundary position 82 · mean-token NLL 2.528237

</details>

### World B

Fictional workshop record: Copperleaf Workshop.
Each line names a value and the separate field it belongs to.
Olive Studio: staff room
Plum Studio: event room

**A / confident / incorrect:** The event for Copperleaf Workshop takes place in Olive Studio. I would give that answer without any further qualification.

Scores: boundary 2.824822; final_content -2.009790; response_mean -4.368565.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-09--B--answer-A--confident` · final content position 91 · boundary position 92 · mean-token NLL 3.339805

</details>

**A / hedged / incorrect:** My answer, subject to revision, is that the event for Copperleaf Workshop takes place in Olive Studio.

Scores: boundary 1.536282; final_content -3.743680; response_mean -5.516812.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-09--B--answer-A--hedged` · final content position 90 · boundary position 91 · mean-token NLL 2.963202

</details>

**A / neutral / incorrect:** The event for Copperleaf Workshop takes place in Olive Studio.

Scores: boundary 3.269529; final_content -1.955568; response_mean -4.370135.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-09--B--answer-A--neutral` · final content position 81 · boundary position 82 · mean-token NLL 2.315341

</details>

**B / confident / correct:** The event for Copperleaf Workshop takes place in Plum Studio. I would give that answer without any further qualification.

Scores: boundary 2.963124; final_content -2.033824; response_mean -4.418064.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-09--B--answer-B--confident` · final content position 91 · boundary position 92 · mean-token NLL 3.545564

</details>

**B / hedged / correct:** My answer, subject to revision, is that the event for Copperleaf Workshop takes place in Plum Studio.

Scores: boundary 1.599500; final_content -3.508076; response_mean -5.562238.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-09--B--answer-B--hedged` · final content position 90 · boundary position 91 · mean-token NLL 2.961908

</details>

**B / neutral / correct:** The event for Copperleaf Workshop takes place in Plum Studio.

Scores: boundary 3.395938; final_content -1.649967; response_mean -4.461432.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-09--B--answer-B--neutral` · final content position 81 · boundary position 82 · mean-token NLL 2.396671

</details>

### World omitted

Fictional workshop record: Copperleaf Workshop.
Each line names a value and the separate field it belongs to.
Olive Studio: break room
Plum Studio: staff room

**A / neutral / not labelled:** The event for Copperleaf Workshop takes place in Olive Studio.

Scores: boundary 3.432464; final_content -1.950345; response_mean -4.277792.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-09--omitted--answer-A--neutral` · final content position 81 · boundary position 82 · mean-token NLL 2.000100

</details>

**B / neutral / not labelled:** The event for Copperleaf Workshop takes place in Plum Studio.

Scores: boundary 3.513527; final_content -1.640144; response_mean -4.375756.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-09--omitted--answer-B--neutral` · final content position 81 · boundary position 82 · mean-token NLL 2.562795

</details>

## v3-room_assignment-10

**Question:** In which room does Sorrel Workshop hold its event?

### World A

Fictional workshop record: Sorrel Workshop.
Each line names a value and the separate field it belongs to.
Mint Studio: staff room
Rose Studio: event room

**A / confident / correct:** Unequivocally, the event for Sorrel Workshop takes place in Rose Studio.

Scores: boundary 3.398303; final_content -0.216131; response_mean -2.767773.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-10--A--answer-A--confident` · final content position 85 · boundary position 86 · mean-token NLL 1.915112

</details>

**A / hedged / correct:** As far as I can tell, the event for Sorrel Workshop takes place in Rose Studio.

Scores: boundary 2.212839; final_content -3.960283; response_mean -5.316808.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-10--A--answer-A--hedged` · final content position 87 · boundary position 88 · mean-token NLL 2.195537

</details>

**A / neutral / correct:** The event for Sorrel Workshop takes place in Rose Studio.

Scores: boundary 3.221680; final_content -1.825893; response_mean -4.271717.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-10--A--answer-A--neutral` · final content position 80 · boundary position 81 · mean-token NLL 1.571909

</details>

**B / confident / incorrect:** Unequivocally, the event for Sorrel Workshop takes place in Mint Studio.

Scores: boundary 3.269049; final_content -0.277216; response_mean -2.956294.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-10--A--answer-B--confident` · final content position 85 · boundary position 86 · mean-token NLL 2.628050

</details>

**B / hedged / incorrect:** As far as I can tell, the event for Sorrel Workshop takes place in Mint Studio.

Scores: boundary 2.047889; final_content -4.031056; response_mean -5.474446.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-10--A--answer-B--hedged` · final content position 87 · boundary position 88 · mean-token NLL 2.835713

</details>

**B / neutral / incorrect:** The event for Sorrel Workshop takes place in Mint Studio.

Scores: boundary 3.014305; final_content -1.900040; response_mean -4.512139.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-10--A--answer-B--neutral` · final content position 80 · boundary position 81 · mean-token NLL 2.490586

</details>

### World B

Fictional workshop record: Sorrel Workshop.
Each line names a value and the separate field it belongs to.
Mint Studio: event room
Rose Studio: staff room

**A / confident / incorrect:** Unequivocally, the event for Sorrel Workshop takes place in Rose Studio.

Scores: boundary 3.450107; final_content -0.164230; response_mean -2.682369.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-10--B--answer-A--confident` · final content position 85 · boundary position 86 · mean-token NLL 2.076615

</details>

**A / hedged / incorrect:** As far as I can tell, the event for Sorrel Workshop takes place in Rose Studio.

Scores: boundary 2.206779; final_content -3.983175; response_mean -5.285954.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-10--B--answer-A--hedged` · final content position 87 · boundary position 88 · mean-token NLL 2.226988

</details>

**A / neutral / incorrect:** The event for Sorrel Workshop takes place in Rose Studio.

Scores: boundary 3.224630; final_content -1.839591; response_mean -4.243076.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-10--B--answer-A--neutral` · final content position 80 · boundary position 81 · mean-token NLL 1.911295

</details>

**B / confident / correct:** Unequivocally, the event for Sorrel Workshop takes place in Mint Studio.

Scores: boundary 3.322689; final_content -0.272935; response_mean -2.871831.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-10--B--answer-B--confident` · final content position 85 · boundary position 86 · mean-token NLL 1.883389

</details>

**B / hedged / correct:** As far as I can tell, the event for Sorrel Workshop takes place in Mint Studio.

Scores: boundary 1.999955; final_content -4.102701; response_mean -5.438906.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-10--B--answer-B--hedged` · final content position 87 · boundary position 88 · mean-token NLL 2.038945

</details>

**B / neutral / correct:** The event for Sorrel Workshop takes place in Mint Studio.

Scores: boundary 3.111904; final_content -1.966812; response_mean -4.486683.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-10--B--answer-B--neutral` · final content position 80 · boundary position 81 · mean-token NLL 1.503978

</details>

### World omitted

Fictional workshop record: Sorrel Workshop.
Each line names a value and the separate field it belongs to.
Mint Studio: staff room
Rose Studio: break room

**A / neutral / not labelled:** The event for Sorrel Workshop takes place in Rose Studio.

Scores: boundary 3.292666; final_content -1.821188; response_mean -4.241273.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-10--omitted--answer-A--neutral` · final content position 80 · boundary position 81 · mean-token NLL 1.606941

</details>

**B / neutral / not labelled:** The event for Sorrel Workshop takes place in Mint Studio.

Scores: boundary 3.187657; final_content -1.821639; response_mean -4.481607.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-10--omitted--answer-B--neutral` · final content position 80 · boundary position 81 · mean-token NLL 2.025105

</details>

## v3-room_assignment-11

**Question:** In which room does Velvet Workshop hold its event?

### World A

Fictional workshop record: Velvet Workshop.
Each line names a value and the separate field it belongs to.
Slate Studio: event room
Navy Studio: staff room

**A / confident / correct:** The event for Velvet Workshop takes place in Slate Studio. I have no reservations about that answer.

Scores: boundary 2.125698; final_content -0.440403; response_mean -4.028343.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-11--A--answer-A--confident` · final content position 86 · boundary position 87 · mean-token NLL 3.087490

</details>

**A / hedged / correct:** The event for Velvet Workshop takes place in Slate Studio. I have some reservations about that answer.

Scores: boundary -2.431458; final_content -9.197519; response_mean -6.313818.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-11--A--answer-A--hedged` · final content position 86 · boundary position 87 · mean-token NLL 3.110388

</details>

**A / neutral / correct:** The event for Velvet Workshop takes place in Slate Studio.

Scores: boundary 3.022114; final_content -2.843501; response_mean -4.433132.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-11--A--answer-A--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.630729

</details>

**B / confident / incorrect:** The event for Velvet Workshop takes place in Navy Studio. I have no reservations about that answer.

Scores: boundary 2.050419; final_content -0.641858; response_mean -4.090194.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-11--A--answer-B--confident` · final content position 86 · boundary position 87 · mean-token NLL 3.710667

</details>

**B / hedged / incorrect:** The event for Velvet Workshop takes place in Navy Studio. I have some reservations about that answer.

Scores: boundary -2.383530; final_content -9.356410; response_mean -6.312743.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-11--A--answer-B--hedged` · final content position 86 · boundary position 87 · mean-token NLL 3.789865

</details>

**B / neutral / incorrect:** The event for Velvet Workshop takes place in Navy Studio.

Scores: boundary 3.214986; final_content -2.447366; response_mean -4.429058.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-11--A--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 2.859653

</details>

### World B

Fictional workshop record: Velvet Workshop.
Each line names a value and the separate field it belongs to.
Slate Studio: staff room
Navy Studio: event room

**A / confident / incorrect:** The event for Velvet Workshop takes place in Slate Studio. I have no reservations about that answer.

Scores: boundary 2.155505; final_content -0.358738; response_mean -4.040208.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-11--B--answer-A--confident` · final content position 86 · boundary position 87 · mean-token NLL 3.557728

</details>

**A / hedged / incorrect:** The event for Velvet Workshop takes place in Slate Studio. I have some reservations about that answer.

Scores: boundary -2.369815; final_content -9.198824; response_mean -6.338479.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-11--B--answer-A--hedged` · final content position 86 · boundary position 87 · mean-token NLL 3.572871

</details>

**A / neutral / incorrect:** The event for Velvet Workshop takes place in Slate Studio.

Scores: boundary 3.021524; final_content -2.728530; response_mean -4.478390.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-11--B--answer-A--neutral` · final content position 78 · boundary position 79 · mean-token NLL 2.426770

</details>

**B / confident / correct:** The event for Velvet Workshop takes place in Navy Studio. I have no reservations about that answer.

Scores: boundary 2.145270; final_content -0.494140; response_mean -4.124697.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-11--B--answer-B--confident` · final content position 86 · boundary position 87 · mean-token NLL 3.312849

</details>

**B / hedged / correct:** The event for Velvet Workshop takes place in Navy Studio. I have some reservations about that answer.

Scores: boundary -2.362974; final_content -9.223837; response_mean -6.349710.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-11--B--answer-B--hedged` · final content position 86 · boundary position 87 · mean-token NLL 3.411342

</details>

**B / neutral / correct:** The event for Velvet Workshop takes place in Navy Studio.

Scores: boundary 3.111178; final_content -2.358760; response_mean -4.485139.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-11--B--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 2.100726

</details>

### World omitted

Fictional workshop record: Velvet Workshop.
Each line names a value and the separate field it belongs to.
Slate Studio: break room
Navy Studio: staff room

**A / neutral / not labelled:** The event for Velvet Workshop takes place in Slate Studio.

Scores: boundary 3.215053; final_content -2.697102; response_mean -4.420339.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-11--omitted--answer-A--neutral` · final content position 78 · boundary position 79 · mean-token NLL 2.352005

</details>

**B / neutral / not labelled:** The event for Velvet Workshop takes place in Navy Studio.

Scores: boundary 3.286088; final_content -2.413483; response_mean -4.384296.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-11--omitted--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 2.691493

</details>

## v3-room_assignment-12

**Question:** In which room does Hearth Workshop hold its event?

### World A

Fictional workshop record: Hearth Workshop.
Each line names a value and the separate field it belongs to.
Cyan Studio: staff room
Blush Studio: event room

**A / confident / correct:** The event for Hearth Workshop takes place in Blush Studio. I would give that answer without any further qualification.

Scores: boundary 2.760215; final_content -2.167093; response_mean -4.211850.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-12--A--answer-A--confident` · final content position 89 · boundary position 90 · mean-token NLL 3.243042

</details>

**A / hedged / correct:** My answer, subject to revision, is that the event for Hearth Workshop takes place in Blush Studio.

Scores: boundary 1.447575; final_content -3.908132; response_mean -5.391501.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-12--A--answer-A--hedged` · final content position 88 · boundary position 89 · mean-token NLL 2.657081

</details>

**A / neutral / correct:** The event for Hearth Workshop takes place in Blush Studio.

Scores: boundary 3.301903; final_content -2.154455; response_mean -4.037273.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-12--A--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.695508

</details>

**B / confident / incorrect:** The event for Hearth Workshop takes place in Cyan Studio. I would give that answer without any further qualification.

Scores: boundary 2.646767; final_content -2.267309; response_mean -4.473136.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-12--A--answer-B--confident` · final content position 88 · boundary position 89 · mean-token NLL 3.352662

</details>

**B / hedged / incorrect:** My answer, subject to revision, is that the event for Hearth Workshop takes place in Cyan Studio.

Scores: boundary 1.117975; final_content -4.428908; response_mean -5.708053.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-12--A--answer-B--hedged` · final content position 87 · boundary position 88 · mean-token NLL 2.855887

</details>

**B / neutral / incorrect:** The event for Hearth Workshop takes place in Cyan Studio.

Scores: boundary 2.976354; final_content -2.712767; response_mean -4.418702.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-12--A--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.985593

</details>

### World B

Fictional workshop record: Hearth Workshop.
Each line names a value and the separate field it belongs to.
Cyan Studio: event room
Blush Studio: staff room

**A / confident / incorrect:** The event for Hearth Workshop takes place in Blush Studio. I would give that answer without any further qualification.

Scores: boundary 2.834504; final_content -2.173032; response_mean -4.161481.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-12--B--answer-A--confident` · final content position 89 · boundary position 90 · mean-token NLL 3.425265

</details>

**A / hedged / incorrect:** My answer, subject to revision, is that the event for Hearth Workshop takes place in Blush Studio.

Scores: boundary 1.497378; final_content -3.775891; response_mean -5.309146.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-12--B--answer-A--hedged` · final content position 88 · boundary position 89 · mean-token NLL 2.796987

</details>

**A / neutral / incorrect:** The event for Hearth Workshop takes place in Blush Studio.

Scores: boundary 3.369915; final_content -2.083125; response_mean -3.949947.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-12--B--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 2.087640

</details>

**B / confident / correct:** The event for Hearth Workshop takes place in Cyan Studio. I would give that answer without any further qualification.

Scores: boundary 2.685095; final_content -2.249357; response_mean -4.426843.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-12--B--answer-B--confident` · final content position 88 · boundary position 89 · mean-token NLL 3.235662

</details>

**B / hedged / correct:** My answer, subject to revision, is that the event for Hearth Workshop takes place in Cyan Studio.

Scores: boundary 1.018533; final_content -4.435840; response_mean -5.624389.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-12--B--answer-B--hedged` · final content position 87 · boundary position 88 · mean-token NLL 2.715877

</details>

**B / neutral / correct:** The event for Hearth Workshop takes place in Cyan Studio.

Scores: boundary 2.898087; final_content -2.858112; response_mean -4.354210.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-12--B--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 1.696898

</details>

### World omitted

Fictional workshop record: Hearth Workshop.
Each line names a value and the separate field it belongs to.
Cyan Studio: staff room
Blush Studio: break room

**A / neutral / not labelled:** The event for Hearth Workshop takes place in Blush Studio.

Scores: boundary 3.485718; final_content -2.190987; response_mean -4.051425.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-12--omitted--answer-A--neutral` · final content position 79 · boundary position 80 · mean-token NLL 1.983586

</details>

**B / neutral / not labelled:** The event for Hearth Workshop takes place in Cyan Studio.

Scores: boundary 3.105973; final_content -2.734490; response_mean -4.415136.

<details>
<summary>Tokens and exact row ID</summary>

`v3-room_assignment-12--omitted--answer-B--neutral` · final content position 78 · boundary position 79 · mean-token NLL 2.205355

</details>

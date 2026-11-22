# DollarFix OEM Smali evidence review — 2026-11-22

Inputs: user-uploaded oem-smali-evidence.json and oem-smali-evidence.md,
created locally from the installed 1.9.4 DollarFix split APK. Seven Smali files
were found, 55 methods matched, no target was missing. Several long methods
were clipped to 250 excerpt lines; do not overinterpret omitted instructions.

## Confirmed static callsites

DiagnoseUIDataBusiness.smali, method jsonUIDataStream(String,JSONObject),
lines 24385–24977:

- 24452–24456: obtains a JSON array named Const_Text_Menudata.
- 24599: obtains an array element as JSONObject.
- 24607–24611: constructs BasicDataStreamBean(JSONObject).
- 24616: appends the new bean to a Java ArrayList.
- 24694: addECUInfoFromDataStreamBean(list,sysname) in an optional branch.
- 24735: addDataStreamBeanInfo(list,sysname,boolean), also conditional.
- 24401–24429: command 801 obtains getShowIndexDataStream()[I and
  sends selection feedback via SendByteDataFeedbackMessage(String,[I).

BasicDataStreamBean.smali, constructor (JSONObject), lines 380–680:

- 508–532: reads Title, Value, Unit keys as strings.
- 535–550: reads optional Const_Text_Item via JSONObject.getInt and setSn(I).
- 562–577: reads optional Const_Text_Id via JSONObject.getString and setId(String).
- 619: default branch sets empty id when Id is missing.
- Field id is java.lang.String, near line 163; getId and setId signatures
  are String-based. equalsByIDAndTitle compares id, title and unit.

DiagnoseUIDataBusiness.smali, getDefDataStreamDatraFromJson, lines 6415–7679:

- 6455–6498 and 6581–6601: gets integer Const_Text_Item and adds it to
  DiagnoseProcessInfoUtil.getArrDefaultSelected() in the evidenced branches.
- 6705–6755: parses DSData items and numeric Const_Text_SN into
  BasicDefDataStreamValueBean.
- Thus selection is at least partly index-based: numeric Item/SN should
  NOT be conflated with the bean's string Id.

DiagnoseLogicBusiness.smali:

- dealDataStream() lines 811–1486 stores pagecount and count.
- pageStreamFeedbackMask() lines 5292–5491 calls
  getDatastreamMask(Ljava/lang/String;II)Ljava/lang/String;,
  getDataStreamCount(String), binaryString2hexString(String), and builds
  diagnostic page-selection feedback.

Thinkcar classes:

- UiDataStreamManager.dealWithDataStreamForUi() lines 135–435 iterates
  BasicDataStreamBean instances, converts units, traverses nested items,
  and dispatches via a coroutine. No 76010020 filter is established.
- DataStreamManager.addDataStreamItem() lines 987–1197 updates mLatestData
  and presentation lists; some graph type-94 limits exist.
- SelectDataStreamDrawerPopup.selectChange() lines 860–891 reads
  DataStreamIndex.getSelectMap(); setSelectMap() lines 1283–1321 updates it.
  This does not alone establish ECU request semantics.

## Evidence boundaries

These are actual static method callsites, NOT a complete runtime call graph.
Neither of the two uploaded evidence documents contains an OEM menu entry
with literal identifier 76010020. The underlying QIRUI_TY V10.22 GGP/ELF
bytes and an OEM JSON stream capture are not available in this upload.
Consequently there is no demonstrated mileage-specific filter and no
defensible patch address yet.

## Next evidence

1. Capture QIRUI_TY V10.22 read-only from Android to ignored local storage.
2. Run reverse/tools/probe_qirui.py locally: inventory, SHA-256, candidate
   ASCII, UTF-16 and raw byte sightings of 76010020 and CHERY_OLD.
   Literal hits are not proof of a decoded GGP item.
3. Obtain a normal-operation, read-only saved OEM JSON menudata snapshot,
   without sending additional vehicle commands. Compare Id, Item, SN,
   title, value and selected index for the candidate odometer.
4. Use full Smali (not truncated excerpts) to verify whether any item is
   dropped before creation, selected incorrectly, or omitted downstream.
5. Only then propose a minimal, reversible, non-ECU-writing display patch.
   Never touch the vehicle's mileage storage, ECU write traffic, or
   licensing/authentication pathways.

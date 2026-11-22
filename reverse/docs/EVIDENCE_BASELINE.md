# DollarFix / Tiggo T11 evidence baseline

This document preserves earlier research findings; it does not claim that the APK bytes have been reexamined during this iteration.

## Original studied target

- Application package: com.dnd.dollarfix.df51
- Earlier original APK filename: usDf_51Release-v1.3.0-25_03_21-com.doolarfix.bbs-release.apk
- Vehicle package: QIRUI_TY V10.22.
- ECU: Chery Tiggo T11 Delphi 2.0/2.4 (4G63/4G64), KWP2000.

Verify the SHA-256 of the actual locally supplied APK before making any patch.

## Previous captured ECU observations

- ECU address 0x11, tester 0xF1.
- KWP StartCommunication: 81 11 F1 81 04.
- ReadDataByLocalIdentifier: 80 11 F1 02 21 01 A6.
- Positive response contains 61 01.
- Captured odometer four bytes 00 0F 42 40: 1,000,000 * 0.1 = 100000.0 km.

## QIRUI findings

- CHERY_OLD_RU.GGP contains Delphi data item ID 76010020 with label 'Mile meter' and unit 'Km'.
- Another GGP section has its odometer expression referencing bytes [56]..[59].
- Previous redirect of an EGR item label/formula to this item DID NOT make the odometer visible.
- Likely missing link: the Delphi Data Stream classification / selection list (hypothesis, not proven).
- Earlier ELF investigation connected libCHERY_OLD.so functions CheryDelphiII, QR_CommDelphi2, QR_InitialDelphi2, GeneralStreamCalc and GeneralMain to XDSDATA.GAG / SearchIdOpenFile. Re-verify offsets for any newly supplied bytes.

## Decoded adapter transactions

- Request: SEQ 27 01 ...
- Response: SEQ 67 01 ...
- This is evidence about decoded DPU traffic, not proof of the raw Bluetooth bearer or outer framing.
- RFCOMM vs BLE, service UUID, packet CRC and adapter authentication remain unverified.

## Reverse-engineering priorities

1. Find Android Bluetooth connection classes and JNI.
2. Map JNI to BT200 DPU frames and initialization.
3. Locate the visible Delphi data-stream item selection logic.
4. Create minimal read-only UI/protocol patch without license/authentication bypass.
5. Verify original/new APK signatures and installation constraints.

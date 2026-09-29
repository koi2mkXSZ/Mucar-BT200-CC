# Protocol research baseline

## Confirmed from the captured Chery Tiggo T11 session

Target ECU: Delphi 2.0L/2.4L (4G63/4G64)

- ECU address: `0x11`
- Tester address: `0xF1`
- StartCommunication request: `81 11 F1 81 04`
- ReadDataByLocalIdentifier request: service/local ID `21 01`
- Positive application response begins `61 01`
- Captured physical request: `80 11 F1 02 21 01 A6`

## Odometer

Known raw bytes:
`00 0F 42 40`

Unsigned big-endian raw:
`1,000,000`

Scale:
`0.1 km`

Decoded:
`100000.0 km`

## Boundary still under reverse engineering

The ECU/KWP layer above is known. The remaining Stage 1 task is the MUCAR BT200 Bluetooth transport/envelope used to carry diagnostic frames. It must be implemented from captured traffic before the app is considered vehicle-ready.

No ECU-write services are implemented.

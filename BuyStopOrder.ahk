; Filename: PlaceOrder.ahk
#Requires AutoHotkey v2.0
#SingleInstance Force
SetTitleMatchMode 2
SendMode "Event"
SetKeyDelay 80, 80
CoordMode "Mouse", "Screen"

; -------- USER SETTINGS --------
Volume := "0.01"
NextTarget := 1.12345         ; Must match Python target
PlaceBtnX := 1100             ; Adjust to your Place button X coordinate
PlaceBtnY := 720              ; Adjust to your Place button Y coordinate
TestMode := true              ; <<< set true for testing (no real trade), false for real
; --------------------------------

; Confirm script was triggered
MsgBox "PlaceOrder.ahk triggered by Python!"

; Activate MT5
if !WinExist("ahk_exe terminal64.exe") {
    MsgBox "MetaTrader 5 not running!"
    ExitApp
}

WinActivate
Sleep 500

; Open New Order window
Send "{F9}"
Sleep 800

; Select Pending Order → Buy Stop
Send "{Tab}{Down}"      ; Pending
Sleep 200
Send "{Tab}{Down 2}"    ; Buy Stop
Sleep 300

; Set Volume
Send "{Tab}^a"
Send Volume
Sleep 200

; Set Price
Send "{Tab}^a"
Send NextTarget
Sleep 200

; Place button
if (TestMode) {
    ; Just show tooltip instead of clicking Place
    ToolTip "TEST MODE: Order would be placed at " NextTarget, PlaceBtnX + 50, PlaceBtnY + 20
    Sleep 2000
    ToolTip
} else {
    ; Real trade
    MouseClick "left", PlaceBtnX, PlaceBtnY
    Sleep 500
    ToolTip "Order Placed at Price: " NextTarget, PlaceBtnX + 50, PlaceBtnY + 20
    Sleep 1500
    ToolTip
}

ExitApp

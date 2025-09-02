; ------------------------------
; Auto-login script for MT5 (connect existing account)
; ------------------------------

; Path to MetaTrader 5 terminal
mt5Path := "C:\Program Files\MetaTrader 5\terminal64.exe"

; Your login credentials
account := "10185"
password := "0pVhHe*j"
server := "MetaQuotes-Demo"  ; adjust if needed

; Launch MT5
Run, %mt5Path%
; Wait for the login window to appear
Sleep, 7000  ; increase if MT5 loads slowly

; Select "Connect with an existing trade account" using keyboard
; Usually, this can be done with Tab/Arrow keys
Send, {Down 2}  ; move down to the 3rd option
Sleep, 500
Send, {Space}   ; select the option
Sleep, 500

; Fill in the credentials
Send, %account%
Send, {Tab}
Send, %password%
Send, {Tab}
Send, %server%
Sleep, 500
Send, {Enter}  ; press Next/Login


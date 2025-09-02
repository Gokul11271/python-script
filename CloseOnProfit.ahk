#SingleInstance force
SetTitleMatchMode, 2

#Persistent
SetTimer, CheckProfit, 5000   ; check every 5 seconds

TargetProfit := 1.00   ; <<< set your desired profit limit here (USD)

return

; ------------------------------
; Function: check profit and close trades if target reached
; ------------------------------
CheckProfit:
    IfWinExist, ahk_exe terminal64.exe
    {
        WinActivate
        Sleep, 500

        ; Copy the last row (Trade tab: Profit column)
        Send, {End}           ; go to the last line of trades
        Sleep, 200
        Send, {Right 10}      ; move to the Profit column (adjust if needed)
        Sleep, 200
        Send, ^c              ; copy profit cell
        ClipWait, 1
        text := Clipboard

        ; Try to extract number
        if RegExMatch(text, "(-?\d+(\.\d+)?)", match)
        {
            profit := match1
            ToolTip, Current Profit: %profit% USD

            if (profit >= TargetProfit)
            {
                ToolTip, Target profit reached! Closing all positions...
                Sleep, 1000

                ; --- Right-click inside Trade tab ---
                MouseMove, 400, 800   ; <<< set correct Trade tab coordinates
                Sleep, 300
                MouseClick, right
                Sleep, 500

                ; Bulk Operations -> Close All Positions
                Send, b
                Sleep, 500
                Send, {Enter}  ; confirm
                Sleep, 2000

                ExitApp
            }
        }
    }
return

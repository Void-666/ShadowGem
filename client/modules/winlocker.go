package main

import (
	"fmt"
	"github.com/andlabs/ui"
)

func main() {
	err := ui.Main(func() {
		// Get the list of available screens
		screens := ui.Screens

		for _, screen := range screens {
			// Create a fullscreen window for each screen
			window := ui.NewWindow("Golang GUI", screen.Width, screen.Height, true)
			window.OnClosing(func(*ui.Window) bool {
				ui.Quit()
				return true
			})

			label1 := ui.NewLabel("North")
			label1.SetFontFamily("Courier")
			label1.SetFontSize(8)
			label1.SetPosition(screen.Width/2, screen.Height-36)
			window.Add(label1)

			label2 := ui.NewLabel("Саня верни сотку")
			label2.SetFontFamily("Courier")
			label2.SetFontSize(30)
			label2.SetPosition(screen.Width/2, screen.Height/2)
			window.Add(label2)

			entry := ui.NewEntry()
			entry.SetFontFamily("Courier")
			entry.SetFontSize(16)
			entry.SetPosition(screen.Width/2-190, screen.Height/2+60)
			entry.SetSize(380, 40)
			entry.OnChanged(func(*ui.Entry) {
				if entry.Text() == "1234" {
					ui.Quit()
				}
			})
			window.Add(entry)

			window.Show()
		}
	})

	if err != nil {
		fmt.Println(err)
	}
}

# spotify-auto-theme
Down with the dark mode tyranny on the desktop client.

Makes a [Spicetify](https://spicetify.app)-themed Spotify desktop client follow your
system's light/dark setting, live, without restarting Spotify. Out of the box it
switches the [Catppuccin](https://github.com/catppuccin/spicetify) theme between
`latte` (system light) and `mocha` (system dark).

## Disclaimer

**This has only been tested on Fedora with GNOME, with Spotify installed from
Flatpak (Flathub).** There is no guarantee it works on any other operating system,
desktop environment or Spotify packaging.

Tested versions: Fedora 44, GNOME 50, Spotify 1.2.95 (Flatpak), Spicetify CLI 2.45.

This changes one byte in Spotify's executable. Use it at your own risk. A backup of
the original is kept and the change is easy to undo (see [Uninstall](#uninstall)).
This project is not affiliated with Spotify, Spicetify or Catppuccin.

## Why a patch is needed

A web page can normally detect the system theme with the CSS media query
`prefers-color-scheme`, and Spotify's interface is a web page running in an embedded
Chromium. The catch is that Spotify starts that Chromium with the switch
`force-dark-mode`, which pins `prefers-color-scheme` to `dark` no matter what the
desktop says. Nothing running inside Spotify (a CSS snippet or a Spicetify
extension) can see the real setting while that switch is active.

So the fix has two parts, a patch for the executable and a CSS snippet, in three files:

| File | What it does |
| --- | --- |
| `spotify-unforce-dark.py` | Renames `force-dark-mode` inside the `spotify` executable to `force-dark-m0de`, a name Chromium ignores. Chromium then reads the system setting from the desktop portal. |
| `spotify-unforce-dark` | Small bash wrapper that re-applies the patch if needed. Meant to be run after Spotify updates. |
| `catppuccin-auto-scheme.css` | A Spicetify Marketplace snippet that sets the Catppuccin `latte` palette under `prefers-color-scheme: light` and `mocha` under `dark`. |

## Prerequisites

- Linux with a desktop that reports light/dark through the XDG desktop portal
  (GNOME 42 or newer does).
- Spotify installed from Flatpak.
- [Spicetify](https://spicetify.app/docs/getting-started) installed and applied to
  that Spotify, including the Flatpak write permissions from Spicetify's own setup
  instructions. The patcher needs write access to the same Spotify directory.
- [Spicetify Marketplace](https://github.com/spicetify/marketplace), with the
  Catppuccin theme installed from it.
- Python 3 (standard library only) and bash.
- Optional: `wl-copy` (package `wl-clipboard`) to copy the CSS to the clipboard.

## Install

1. Get the files:

   ```bash
   git clone https://github.com/SunilSimha/spotify-auto-theme
   cd spotify-auto-theme
   ```

2. Put the patcher next to your Spicetify config and the wrapper somewhere on your
   `PATH`. The wrapper looks for the patcher in `~/.config/spicetify/`.

   ```bash
   install -m 755 spotify-unforce-dark.py ~/.config/spicetify/
   install -D -m 755 spotify-unforce-dark ~/.local/bin/spotify-unforce-dark
   ```

3. Quit Spotify, apply the patch, then start Spotify again:

   ```bash
   spotify-unforce-dark
   ```

   It prints `patched ...` the first time and `already patched, nothing to do` after
   that. If it reports a permission error, your user cannot write to the Spotify
   directory: fix the Spicetify Flatpak permissions, or run it with `sudo`.

4. Add the CSS snippet. Copy it to the clipboard:

   ```bash
   wl-copy < catppuccin-auto-scheme.css
   ```

   In Spotify open **Marketplace → Snippets**, click the floating **+ Add CSS**
   button in the bottom-right corner of the page (scroll to the end of the list if
   you do not see it), paste into the "Custom CSS" box, give it a name and save.

5. Toggle your system between light and dark. Spotify should recolour immediately.

## After a Spotify update

A Spotify update replaces the executable, so Spotify goes back to always-dark. Run
the wrapper again and restart Spotify:

```bash
spotify-unforce-dark
```

It is safe to run every time, so the easy option is to call it at the end of
whatever script you use for system updates, after `flatpak update`. It works under
`sudo` as well; in that case call it by its full path, since `~/.local/bin` is
usually not on root's `PATH`.

The patcher refuses to touch a Spotify build that does not contain exactly one
standalone `force-dark-mode` string, so a future Spotify change makes it stop with a
message instead of patching blindly.

## Uninstall

Quit Spotify, then:

```bash
~/.config/spicetify/spotify-unforce-dark.py restore
```

This puts the original executable back. Then disable or remove the snippet in
Marketplace. `spotify-unforce-dark.py status` shows the current state.

## Known quirks

- While the snippet is enabled, Marketplace's colour-scheme dropdown has no visible
  effect, because the snippet overrides both palettes. Disable the snippet to pick a
  flavour by hand.
- With the switch gone, Chromium's own bits (scrollbars, form controls) also follow
  the system theme.
- Catppuccin's animated "now playing" equalizer icon is chosen from the scheme
  selected in Marketplace, so its tint can be slightly off in the other mode.
- A few of Spotify's fade gradients stay dark in light mode.

## Adapt it

This is a small fix for one setup, and you are very welcome to fork it and adapt it
to yours. Some starting points, none of them tested here:

- **Other Catppuccin flavours, or another theme.** Edit the two blocks in
  `catppuccin-auto-scheme.css`. Any Spicetify theme that reads the `--spice-*`
  variables can be driven the same way: take the values from the theme's
  `color.ini` and set both `--spice-<name>` (hex) and `--spice-rgb-<name>` (r,g,b).
- **Themes installed with the Spicetify CLI instead of Marketplace.** The same CSS
  could go at the end of the theme's `user.css`.
- **Spotify from a `.deb`, `.rpm`, Snap or the AUR.** The patcher takes the Spotify
  directory from `spotify_path` in `~/.config/spicetify/config-xpui.ini`, so it may
  work as is if Spicetify is set up. The wrapper's "is Spotify running" check uses
  the Flatpak path and would need changing.
- **Other desktops.** Anything that sets `color-scheme` in the
  `org.freedesktop.appearance` portal namespace should in principle work.
- **macOS and Windows.** The scripts here are Linux-only, and whether Spotify forces
  dark mode the same way there has not been checked.

If you get it working somewhere else, a pull request or an issue describing what you
changed would help the next person.

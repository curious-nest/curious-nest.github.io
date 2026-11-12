# Curious Nest website

Homepage, privacy policy and terms for [Curious Nest](https://www.youtube.com/channel/UCYclBr51SW5hWYQV5gqO5CA),
learning adventures for curious kids. Plain static pages, served by GitHub Pages.

The Baloo 2 font (`fonts/`) is under the SIL Open Font License (`fonts/OFL.txt`).

Live at **https://curious-nest.github.io/**.

The "Newest videos" and "Most watched" lists update themselves: the
`Update video lists` GitHub Action runs `tools/update_videos.py` every day (just
after the 8 PM India-time releases, and again in the morning). It reads the channel's public
YouTube feed, saves the thumbnails into `img/videos/` (so the site itself
loads nothing from YouTube) and commits the new lists. Run it by hand from the
Actions tab ("Run workflow") or locally with `python3 tools/update_videos.py`.

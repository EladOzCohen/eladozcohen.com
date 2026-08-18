# eladozcohen.com

Personal website of **Elad Oz-Cohen** — Data Analytics & Visualizations.
Live at **https://eladozcohen.netlify.app/**.

This README is the map. Read the section you need; skip the rest.

---

## 1. What this is (the stack)

- **Hugo** static-site generator (pinned to **v0.111.2** — see `.Rprofile` and `netlify.toml`).
- Theme: **hugo-apero** (lives in `themes/hugo-apero/` — don't edit it; your customizations override it).
- Authored via **R + blogdown** in **RStudio** (that's why there's an `.Rproj`, `.Rprofile`, and `index.Rmd`). You don't *have* to use R — you can edit Markdown and run Hugo directly.
- **Deploy**: pushing to the `main` branch on GitHub (`github.com/EladOzCohen/eladozcohen.com`) triggers an automatic **Netlify** build. Nothing deploys from your laptop directly.

---

## 2. How to edit content (the part you'll actually use)

All page text is **Markdown** under `content/`. Each page's front matter (the `---` block
at the top) controls its title, image, excerpt, links, etc.

| I want to change... | Edit this |
|---|---|
| The homepage intro / headline / avatar | `content/_index.md` |
| The **About** page — "So, who am I?" body | `content/about/main/index.md` |
| The About sidebar (name, short blurb, avatar) | `content/about/sidebar/index.md` |
| A **blog** post | `content/blog/<post-name>/index.md` |
| The blog landing page's left sidebar text | `content/blog/_index.md` |
| A **project** write-up (content, its header/subheader, its thumbnail) | `content/project/<project-name>/index.md` |
| The Projects landing page text | `content/project/_index.md` |
| A **visualization** project's own page | `content/Data-visualizations/<viz-name>/index.md` |
| The Visualizations landing grid (cards, headers, links — around line 55) | `content/Data-visualizations/index.md` |
| Site title, nav menu, social icons, colors, fonts | `config.toml` |

**Each post/project is a "page bundle"** — a folder containing `index.md` plus its
`featured.png`/`featured.jpg` (the thumbnail shown on landing pages) and any images it uses.
To add a new one, copy an existing folder and edit it, or use the theme archetypes in
`themes/hugo-apero/archetypes/`.

### The nav menu
Defined in `config.toml` under `[menu]`: **About · blog · Projects · Visualizations**.
(There are also `content/talk/`, `content/elements/`, `content/license.md`, and
`content/contributors.md` folders left over from the theme's example site — they exist but
are **not** in the menu. Safe to ignore, or delete later if you don't want them.)

### Social links & CV
In `config.toml` under `[[params.social]]`: GitHub, LinkedIn, and a **CV** link pointing at
`/CV_Builder/EladOzCohenCV.pdf` (that PDF lives in `static/CV_Builder/`).

---

## 3. Directory map

| Path | What it is |
|---|---|
| `config.toml` | **Main site configuration** — title, menu, social links, theme, fonts, colors. |
| `content/` | **All page content** (Markdown). This is where you spend your time. |
| `assets/` | SCSS/JS that Hugo processes. Custom color theme: `assets/elad-hex.scss`. |
| `static/` | Files served as-is (images under `static/`, the CV under `static/CV_Builder/`). |
| `layouts/` | Site-specific layout overrides (currently just a blogdown shortcode). |
| `data/` | Small config data (e.g. the Formspree contact-form blurb). |
| `themes/hugo-apero/` | The theme. **Leave alone** — override via `assets/`, `layouts/`, `config.toml`. |
| `R/` | Optional blogdown build hooks (`build.R`, `build2.R`) — currently empty. |
| `index.Rmd` | blogdown entry file. Do not edit. |
| `netlify.toml` | Netlify build settings (Hugo version, publish dir). |
| `.Rprofile` / `*.Rproj` | RStudio/blogdown project settings. |
| `../data-sources/` | **(Sibling folder, outside the site)** the raw datasets behind the projects — see note 6. |

Anything gitignored/regenerated (`public/`, `resources/`, `.Rproj.user/`, `.Rhistory`) is
**not** part of the source — Hugo/RStudio recreate it. Don't hand-edit it.

---

## 4. Build & preview locally

**With R/RStudio (blogdown):** open `eladozcohen.com.Rproj`, then in the console:
```r
blogdown::serve_site()
```

**Without R — just Hugo** (needs Hugo **0.111.2** installed):
```bash
hugo server      # live preview at http://localhost:1313
hugo             # one-off build into ./public
```

---

## 5. Publishing (how a change goes live)

Netlify auto-deploys the GitHub `main` branch. From inside `eladozcohen.com/`:
```bash
git add .
git commit -m "your message"
git push
```
Then Netlify rebuilds and updates the live site automatically (a minute or two).

> ⚠️ **Heads-up before your next edit session:** this local copy has **diverged** from
> GitHub — the remote `main` is 15 commits ahead of what's here, and this copy has 2 commits
> the remote doesn't. **Reconcile that first** (e.g. `git fetch` and review, or `git pull`)
> so you're editing the current version and don't clobber newer work. Do this before
> committing anything new.

---

## 6. Where the raw data went

The heavy source datasets (spreadsheets, CSVs, shapefiles, zips — ~180 MB) used to sit
inside the project folders under `content/`, bloating the repo and the live site even though
no page links to them. They've been moved to a sibling folder **outside** the site:

```
Desktop/mywebsite/
├─ eladozcohen.com/     ← the website (this repo)
└─ data-sources/        ← the raw datasets, by project (see its own README)
```

The small stuff that *is* part of each write-up (the `.sql` / `.R` scripts, `index.md`,
`featured.png`) stayed in `content/`. If you ever want a dataset downloadable from the site,
move that one file back into its `content/` project folder and link it in `index.md`.

---

## 7. Known loose ends (for later, not blocking)

- **`../E-Commerece Analysis/`** — a MSSQL/PowerBI project sitting next to the site but never
  added to it. To publish it, make a `content/project/E-Commerce/` folder with an `index.md`
  (copy an existing project as a template).
- **Homepage avatar** — `content/_index.md` points at `img/profile_corruped.jpg` (served from
  the theme). The name suggests a corrupted original; you'll probably want to drop in a proper
  photo. Two stray `profile_corruped.*` files (in `content/` and `static/`) are unused — left
  in place so nothing breaks; safe to remove once you swap in a real avatar.
- **`content/Data-visualizations/index.qmd`** — the Quarto source that generated that page's
  `index.md`. Kept for reference; the site renders from the `.md`.
- **Git divergence** — see the heads-up in section 5.

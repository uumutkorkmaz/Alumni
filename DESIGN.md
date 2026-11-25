---
version: alpha
name: Alumni-Tracking-design-system
description: "An academic ledger in Istanbul University green, opened on midnight ink. A dark, low-glare canvas (#0d1614) with ledger panels (#141f1c) separated by 1px hairlines (#273732), paper-coloured text (#e3e9e6), Istanbul University green (#439c86) as the signal colour for links, focus and active states, the Faculty of Economics' deep green (#2c7a64) for primary buttons, and university gold (#b8860b) used once per screen. Headlines and numbers in Source Serif 4, interface in Inter, archive notation in IBM Plex Mono. No shadows; depth comes from surface steps. Motion eases things into place once (fade-up, line draw, count-up, 2px hover lift) and respects reduced motion."

colors:
  ink: "#0d1614"
  panel: "#141f1c"
  panel-2: "#1a2824"
  field: "#111b19"
  border: "#273732"
  text: "#e3e9e6"
  muted: "#98a7a1"
  primary: "#439c86"
  on-primary: "#0d1614"
  primary-light: "#6cbca6"
  primary-deep: "#2c7a64"
  primary-deep-hover: "#26705b"
  on-primary-deep: "#ffffff"
  forest: "#006a4e"
  gold: "#b8860b"
  gold-light: "#d4a64a"
  navy: "#1a3a5a"
  navy-light: "#86aed6"
  danger: "#dc3545"
  danger-soft: "#e8857c"
  alert-surface: "#2a1714"
  on-alert: "#f3d9d6"

typography:
  hero-display:
    fontFamily: Source Serif 4
    fontSize: 64px
    fontWeight: 500
    lineHeight: 1.05
    letterSpacing: -0.02em
  page-title:
    fontFamily: Source Serif 4
    fontSize: 36px
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: -0.01em
  section-heading:
    fontFamily: Source Serif 4
    fontSize: 28px
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: -0.01em
  stat-number:
    fontFamily: Source Serif 4
    fontSize: 44px
    fontWeight: 500
    lineHeight: 1.0
    letterSpacing: -0.02em
  body-large:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: -0.01em
  card-title:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: 0
  body:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: 0
  ui:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: 0
  button:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: 0
  caption:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: 0
  eyebrow:
    fontFamily: IBM Plex Mono
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: 0.08em
  badge:
    fontFamily: IBM Plex Mono
    fontSize: 11px
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: 0.06em
  table-head:
    fontFamily: IBM Plex Mono
    fontSize: 11px
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: 0.06em

rounded:
  sm: 8px
  logo: 9px
  md: 10px
  lg: 14px
  pill: 9999px

spacing:
  xxs: 4px
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
  section: 64px
  hero: 96px

components:
  navbar:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.muted}"
    typography: "{typography.ui}"
    height: 64px
  eyebrow:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.gold}"
    typography: "{typography.eyebrow}"
    rounded: "{rounded.pill}"
    padding: 6px 14px
  button-primary:
    backgroundColor: "{colors.primary-deep}"
    textColor: "{colors.on-primary-deep}"
    typography: "{typography.button}"
    rounded: "{rounded.md}"
    padding: 10px 18px
  button-primary-hover:
    backgroundColor: "{colors.primary-deep-hover}"
    textColor: "{colors.on-primary-deep}"
    typography: "{typography.button}"
    rounded: "{rounded.md}"
    padding: 10px 18px
  button-ghost:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    typography: "{typography.ui}"
    rounded: "{rounded.md}"
    padding: 10px 18px
  button-ghost-hover:
    backgroundColor: "{colors.panel-2}"
    textColor: "{colors.text}"
    typography: "{typography.ui}"
    rounded: "{rounded.md}"
    padding: 10px 18px
  button-danger:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.danger-soft}"
    typography: "{typography.ui}"
    rounded: "{rounded.sm}"
    padding: 6px 12px
  stat-tile:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    typography: "{typography.stat-number}"
    rounded: "{rounded.lg}"
    padding: 24px
  card:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: 24px
  card-featured:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: 24px
  table-header:
    backgroundColor: "{colors.panel-2}"
    textColor: "{colors.muted}"
    typography: "{typography.table-head}"
    padding: 12px 16px
  table-row:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    typography: "{typography.ui}"
    padding: 12px 16px
  status-badge-progress:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.navy-light}"
    typography: "{typography.badge}"
    rounded: "{rounded.pill}"
    padding: 3px 10px
  status-badge-next:
    backgroundColor: "{colors.panel-2}"
    textColor: "{colors.gold-light}"
    typography: "{typography.badge}"
    rounded: "{rounded.pill}"
    padding: 3px 10px
  status-badge-good:
    backgroundColor: "{colors.panel-2}"
    textColor: "{colors.primary-light}"
    typography: "{typography.badge}"
    rounded: "{rounded.pill}"
    padding: 3px 10px
  status-badge-ended:
    backgroundColor: "{colors.panel-2}"
    textColor: "{colors.danger-soft}"
    typography: "{typography.badge}"
    rounded: "{rounded.pill}"
    padding: 3px 10px
  text-input:
    backgroundColor: "{colors.field}"
    textColor: "{colors.text}"
    typography: "{typography.ui}"
    rounded: "{rounded.md}"
    padding: 10px 12px
  text-input-focused:
    backgroundColor: "{colors.field}"
    textColor: "{colors.text}"
    typography: "{typography.ui}"
    rounded: "{rounded.md}"
    padding: 10px 12px
  alert:
    backgroundColor: "{colors.alert-surface}"
    textColor: "{colors.on-alert}"
    typography: "{typography.ui}"
    rounded: "{rounded.md}"
    padding: 12px 16px
  logo-mark:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button}"
    rounded: "{rounded.logo}"
    size: 32px
  step-number:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.gold}"
    typography: "{typography.section-heading}"
    rounded: "{rounded.pill}"
    size: 32px
  footer:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.muted}"
    typography: "{typography.eyebrow}"
    padding: 24px
---

# Alumni Tracking — Style Reference
> An academic ledger in Istanbul University green, opened on midnight ink. Calm surfaces, serif authority, gold used once.

**Theme:** dark

This is the design system that people and AI agents read before building a page for the Alumni Tracking System (Istanbul University · Faculty of Economics · Management Information Systems). It follows the [awesome-design-md](https://github.com/VoltAgent/awesome-design-md) structure: the machine-readable tokens of the [Stitch DESIGN.md format](https://stitch.withgoogle.com/docs/design-md/specification/) (`version: alpha`) in the front matter above, then the nine prose sections, with an extra **Motion & Animation** section. The front matter is the source of truth for values; the prose explains when and why to use them, and refers to tokens as `{colors.primary}`, `{typography.body}`, `{components.card}`. The identity behind it (where the colours come from, the logo, the relationship to the university, the contrast table) is in [brand.md](brand.md); this file turns that identity into tokens and component recipes. Colours, contrast ratios and the logo here match `brand.md` exactly.

> **Status:** applied. Every page follows this file: `app/static/app.css` holds the tokens (without the `color-` prefix: `--primary`, `--ink`, `--panel`), `app/views/layout.py` the fonts, navbar, footer and motion script, and each view in `app/views/` its page pattern from [§5](#page-patterns).

> **Rule:** this file, `brand.md` and `app/static/app.css` change together. A new colour, font, radius, duration or component recipe is written here in the same commit that adds it to the code.

## 1. Visual Theme & Atmosphere

Alumni Tracking reads like the register of a well-kept university office: a dark ink page, cards set like ledger sheets, thin 1 px rules, serif headings with quiet authority, and small monospace labels that read like archive notation (`ID 0042`, `SUBMITTED`, `2026-11-18`). The university is present through its colours, Istanbul University green `#439c86` and its gold `#b8860b`, not through its logo.

The mood is **professional, calm and premium**: low-glare contrast, colour kept to small signals, generous space around statements, and motion that eases things into place instead of bouncing for attention. Behind the home page hero sits a faint **ledger grid** with plus-shaped registration marks, the one decorative element of the system: a record book of graduates.

Three words: **institutional, precise, unhurried.**

## 2. Color Palette & Roles

Semantic name, hex and role. Dark only (`color-scheme: dark`). Contrast ratios are listed in [brand.md §6](brand.md#6-contrast-table); every text colour passes WCAG AA on the surfaces named here.

### 2.1 Surfaces and text

| Name | Value | Token | Role |
|------|-------|-------|------|
| Midnight Ink | `#0d1614` | `--color-ink` | Page canvas; dark text on green (logo mark, light buttons). A deep green-tinted black, never pure `#000`. |
| Ledger Panel | `#141f1c` | `--color-panel` | Cards, tables, ghost buttons, the navbar when scrolled. |
| Raised Panel | `#1a2824` | `--color-panel-2` | Table headers, hover rows, the active navbar link, selected tabs. |
| Inset Field | `#111b19` | `--color-field` | Inputs, selects, text areas: one step darker than a panel, as if pressed in. |
| Hairline | `#273732` | `--color-border` | Every 1 px rule, card edge and divider (1.35 : 1 against a panel). |
| Paper Text | `#e3e9e6` | `--color-text` | Body text and headings (14.9 : 1 on ink: readable, never glaring). |
| Archive Gray | `#98a7a1` | `--color-muted` | Labels, dates, notes, table headers, subtitles. |

### 2.2 Brand and signals

| Name | Value | Token | Role |
|------|-------|-------|------|
| İÜ Green | `#439c86` | `--color-primary` | Istanbul University's own green: links, focus ring, active states, the logo mark, "Open" and "accepted". |
| Green Tint | `#6cbca6` | `--color-primary-light` | Link hover; green text below 14 px. |
| İktisat Deep Green | `#2c7a64` | `--color-primary-deep` | Primary button fill (white text 5.15 : 1); hover `#26705b`. |
| Forest | `#006a4e` | `--color-forest` | Background tints only: selected rows, success badge fills (`rgba(0,106,78,.15–.18)`). |
| University Gold | `#b8860b` | `--color-gold` | The single premium accent per screen: the gold word in a hero, the active nav underline, the "interview" status, eyebrow pills. |
| Gold Tint | `#d4a64a` | `--color-gold-light` | Gold text below 14 px. |
| Registry Navy | `#1a3a5a` | `--color-navy` | Background tint for information and "in progress" badges. |
| Navy Tint | `#86aed6` | `--color-navy-light` | Text of "in progress" states (submitted, under review). |
| Signal Red | `#dc3545` | `--color-danger` | Borders and fills of danger elements only (as text it fails contrast). |
| Soft Red | `#e8857c` | `--color-danger-soft` | Error text, delete labels, "rejected" / "Closed". |

### 2.3 Gradient and atmosphere

| Name | Value | Token | Role |
|------|-------|-------|------|
| Faculty Line | `linear-gradient(90deg, #439c86, #2c7a64)` | `--gradient-line` | The Faculty of Economics' own heading underline. Only as a 3 px decorative line (under a hero or section title, the top edge of a featured card). Never behind text. |
| Ink Glow | `radial-gradient(circle at 15% 0%, rgba(67,156,134,.10), transparent 42%), radial-gradient(circle at 85% 0%, rgba(184,134,11,.05), transparent 40%)` | `--glow-page` | Two very soft lights at the top of the canvas, green and gold. |
| Ledger Grid | 1 px lines every 32 px in `rgba(67,156,134,.06)`, plus marks every 128 px in `rgba(227,233,230,.18)` | `--grid-ledger` | Hero backdrop only, faded out towards the bottom with a mask. |

### 2.4 Status colours

| Meaning | Text | Fill | Statuses |
|---------|------|------|----------|
| In progress | `--color-navy-light` | `--color-navy` at 35 % | submitted, under review |
| Next step | `--color-gold-light` | `--color-gold` at 12 % | interview |
| Good outcome | `--color-primary-light` | `--color-forest` at 18 % | accepted, Open |
| Ended / refused | `--color-danger-soft` | `--color-danger` at 10 % | rejected, withdrawn, Closed |

## 3. Typography Rules

Three families, all from Google Fonts, all with full Turkish glyphs (ç ğ ı İ ö ş ü):

### Source Serif 4 — display and section headings · `--font-display`
- **Fallback:** Georgia, "Times New Roman", serif
- **Weights:** 500, 600
- **Sizes:** 28, 36, 44, 56, 64 px (optical size axis follows the size)
- **Line height:** 1.05 (hero), 1.15 (sections)
- **Letter spacing:** −0.02em at 56–64 px, −0.01em below
- **Role:** the university's voice. Hero statements, page titles, section headings, the big numbers of stat tiles and error codes (404, 503). Never for body text, buttons or tables.

### Inter — interface and reading text · `--font-sans`
- **Fallback:** -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
- **Weights:** 400, 500, 600
- **Sizes:** 13, 14, 15, 16, 18, 20 px
- **Line height:** 1.6 body, 1.4 UI, 1.3 card titles
- **Letter spacing:** 0; −0.01em at 18–20 px
- **Role:** body copy, navigation, buttons, form labels, card titles, table cells.

### IBM Plex Mono — archive notation · `--font-mono`
- **Fallback:** ui-monospace, SFMono-Regular, Menlo, Consolas, monospace
- **Weights:** 500
- **Sizes:** 11, 12, 13 px
- **Line height:** 1.3
- **Letter spacing:** 0.06em when upper case, 0 otherwise
- **Role:** eyebrow labels, table headers, status badges, ids, dates, counters' captions, error ids, request lines on error pages. Things the system *records*, not things people *say*.

### Type Scale

| Role | Family | Weight | Size | Line Height | Letter Spacing | Token |
|------|--------|--------|------|-------------|----------------|-------|
| eyebrow | IBM Plex Mono | 500 | 12px | 1.3 | 0.08em, upper case | `--text-eyebrow` |
| badge | IBM Plex Mono | 500 | 11px | 1.3 | 0.06em, upper case | `--text-badge` |
| table-head | IBM Plex Mono | 500 | 11px | 1.3 | 0.06em, upper case | `--text-table-head` |
| caption | Inter | 400 | 13px | 1.4 | 0 | `--text-caption` |
| ui | Inter | 500 | 14px | 1.4 | 0 | `--text-ui` |
| body | Inter | 400 | 15px | 1.6 | 0 | `--text-body` |
| body-large | Inter | 400 | 18px | 1.6 | −0.01em | `--text-body-large` |
| card-title | Inter | 600 | 16px | 1.3 | 0 | `--text-card-title` |
| section-heading | Source Serif 4 | 600 | 28px | 1.15 | −0.01em | `--text-section` |
| page-title | Source Serif 4 | 600 | 36px | 1.15 | −0.01em | `--text-page-title` |
| stat-number | Source Serif 4 | 500 | 44px | 1.0 | −0.02em, tabular | `--text-stat` |
| hero-display | Source Serif 4 | 500 | clamp(40px, 6vw, 64px) | 1.05 | −0.02em | `--text-hero` |

Rules:
- Numbers in tables, counters and dates use `font-variant-numeric: tabular-nums` so columns line up.
- Turkish upper case: set `lang="tr"` on Turkish pages so `text-transform: uppercase` turns `i` into `İ` (`İSTANBUL`, not `ISTANBUL`).
- One gold word per hero at most; the rest of a headline stays Paper Text.
- Prose is at most 68 characters wide (`max-width: 68ch`).

## 4. Component Stylings

### Navbar
**Role:** the top bar of every page.
64 px tall, sticky, `rgba(13,22,20,.82)` with an 12 px backdrop blur and a 1 px Hairline bottom rule. Left: the AT mark (32 px, İÜ Green, Midnight Ink letters, 1 px gold hairline at 45 %) and the wordmark "Alumni Tracking" in Inter 600 16 px with the endorsement line `İÜ · İKTİSAT · YBS` under it in IBM Plex Mono 10 px Archive Gray. Right: links in Inter 500 14 px Archive Gray; hover Paper Text; the active page Paper Text with a 2 px University Gold underline that slides in from the left (§7).

### Eyebrow
**Role:** small label above a title that says where you are.
IBM Plex Mono 500 12 px upper case, 0.08em, University Gold, with a 1 px gold hairline pill (`rgba(184,134,11,.4)` border, `rgba(184,134,11,.08)` fill, fully round, 6 × 14 px padding). Example: `İSTANBUL ÜNİVERSİTESİ · İKTİSAT FAKÜLTESİ · YBS`.

### Hero
**Role:** the home page opening statement.
Centered, 96 px top / 56 px bottom padding, over the Ledger Grid. Eyebrow, then a Source Serif 4 hero-display headline in Paper Text with one phrase in University Gold, then a 3 px × 56 px Faculty Line drawn under it, then body-large Archive Gray lead (max 60ch), then a primary and a ghost button 12 px apart.

### Primary Button
**Role:** the one main action of a screen ("Create", "Save changes", "Apply").
İktisat Deep Green fill, white Inter 600 14 px text, 10 px radius, 10 × 18 px padding, min height 40 px. Hover `#26705b`; active scale 0.98; focus 2 px İÜ Green ring with 2 px offset. No gradient behind text, no shadow.

### Ghost Button
**Role:** secondary actions and navigation ("Edit", "Back", "Home").
Ledger Panel fill, 1 px Hairline border, Paper Text Inter 500 14 px, 10 px radius. Hover: Raised Panel fill and border `rgba(67,156,134,.45)`.

### Danger Button
**Role:** deleting, nothing else.
Soft Red text on Signal Red at 10 %, border at 35 %, 8 px radius in rows. Always followed by a confirmation question.

### Text Link
İÜ Green, underline offset 3 px, thickness 1 px, appearing on hover; Green Tint on hover. In prose the underline is always on.

### Stat Tile
**Role:** a live counter on the home page.
Ledger Panel, 1 px Hairline, 14 px radius, 24 px padding. Caption in IBM Plex Mono 12 px upper case Archive Gray above; the number in Source Serif 4 stat-number Paper Text; an optional note in 13 px Green Tint ("12 tanesi açık"). The whole tile is a link; hover lifts it 2 px and turns the border green (§7). The number counts up once when the tile enters the screen.

### Card
**Role:** one form, one detail, one list.
Ledger Panel, 1 px Hairline, 14 px radius, 24 px padding, no shadow. A **featured card** adds a 3 px Faculty Line along its top edge (inside the radius).

### Data Table
**Role:** every list (users, postings, applications).
Inside a card-shaped wrapper (14 px radius, 1 px Hairline, scrolls sideways on small screens). Header row Raised Panel with IBM Plex Mono table-head Archive Gray. Rows 14 px Inter, 12 × 16 px cells, 1 px Hairline between rows; hover row `rgba(0,106,78,.12)` (Forest tint). Ids and dates in mono tabular figures. Actions right-aligned (small ghost "Edit", small danger "Delete"). A filter field above, a count on its left ("15 postings · 12 open").

### Status Badge
**Role:** a short state word.
Fully round, 3 × 10 px padding, IBM Plex Mono badge size, colours from §2.4. Never more than two words.

### Navbar Account
**Role:** the right end of the navbar (ddd.md 4.1.3).
A guest sees "Giriş yap" (Archive Gray text link, Panel on hover) and the Register Button; the management links are hidden. A signed-in user sees a pill (Ledger Panel, 1 px Hairline, fully round) with a 28 px avatar, the first name in Inter 600 13 px and the role in mono 10 px Gold Tint, linking to their profile, and a small ghost "Çıkış" button (a form posting to `/logout`). An admin also sees "Approvals" among the links.

### Login Page
**Role:** `/login` (Turkish, public).
Compact Page Hero (`GİRİŞ`, "Hesabına *giriş yap*") → one featured card, at most 480 px wide: a note when the page was asked for (`?next=`), email, password with "Göster / Gizle", "Beni hatırla (30 gün)", the primary button, and under a divider "Hesabın yok mu? Kayıt ol". A refused login shows one Alert with the reason; the email stays, the password does not. The registration page links back with "Hesabın var mı? Giriş yap" and a ghost "Hesabım var, giriş yap" in its hero.

### Fixed Value
**Role:** a form value the user may not change (the author, the poster, the applicant: always the signed-in user).
A 40 px row with a 1 px dashed Hairline and 10 px radius, the value in Paper Text 14 px, under the usual label; it replaces the select an admin would see.

### Register Button
**Role:** the one call to action in the navbar, on every page.
"Register" in Inter 600 14 px Gold Tint with a 1 px gold hairline at 55 %, 10 px radius, right of the links; hover and the registration page itself fill it with gold at 12 %. It is the only gold element of the navbar besides the active underline.

### Registration Page
**Role:** `/register` (Turkish, public; ddd.md §4.1.2).
Compact Page Hero (`MEZUN AĞINA KATIL`, "Hesabını *oluştur*") → two columns (1.7fr / 1fr, one below 900 px): a featured form card and a sticky side column ("Nasıl çalışır?" three numbered steps, "Hangi e-posta?" with the domain of each role).
- **Role cards:** four radio cards in a row (two below 900 px) on Inset Field, the role in Inter 600 and the email it needs in mono 10 px; the chosen card gets an İÜ Green border, a Forest tint and a gold bottom edge. The page script shows only the chosen role's fields (others hidden and disabled), changes the labels ("Bölüm" → "Birim" for staff, "Beklenen mezuniyet yılı" for students), the email placeholder and the document hint. Without JavaScript every field stays visible; the server checks everything.
- **Fields:** the usual Form Field; a hint line in 12 px Archive Gray; an error in 13 px Soft Red under the field with the field's border turned red; an error summary Alert above the form.
- **Password:** a "Göster / Gizle" ghost button and a 3 px strength bar (Soft Red → Gold Tint → Green Tint over four levels).
- **Document:** a drop zone: 1.5 px dashed border on Inset Field, 14 px radius; the file input covers it, so clicking or dropping works; hover and drag turn it green, a chosen file makes the border solid and shows the file name.
- **Done page:** compact hero "Başvurun *alındı*" and the three steps with the first ticked.

### Review Card
**Role:** one pending registration on `/admin/registrations` (English, management).
A card: avatar, name, account number and role badge; the role's fields as a mono-label list; an "Open document · PDF 230 KB" ghost button with the original file name; a footer with Approve (primary) and a reason input with Reject (danger). Above the list: a success Alert after a decision, a gold note that the page is open until the login task, and stat tiles by role.

### Role Badge
**Role:** a user's role (ddd.md §4.1.1) in the users table, on a profile and in the Faculty and staff list.
The Status Badge, one colour per role from the same palette: **Student** Navy Tint on Registry Navy, **Graduate** Green Tint on Forest, **Academic** Gold Tint on gold at 12 %, **Staff** Paper Text on Raised Panel, **Admin** Soft Red on red at 10 %. Under the album, academic and administrative staff are plain name cards (avatar, name, department, role badge) in a `repeat(auto-fill, minmax(260px, 1fr))` grid; the album photos stay for students and graduates.

### Form Field
**Role:** text, number, date, select, text area.
Label above in Inter 500 13 px Archive Gray. Field on Inset Field, 1 px Hairline, 10 px radius, 10 × 12 px padding, Paper Text 14 px. Focus: border İÜ Green and a 3 px ring `rgba(67,156,134,.22)`. Required fields are marked in the label, not by colour alone. Forms are two columns on wide screens, one below 720 px.

### Alert
**Role:** a refused action, at the top of the page.
`#2a1714` fill, 1 px Signal Red at 40 % border, `#f3d9d6` text, 10 px radius, 12 × 16 px padding, the reason in one plain sentence. Slides in (§7).

### Empty State
**Role:** a list with nothing in it.
Centered in the table body, Archive Gray 14 px, one sentence plus what to do ("No job postings yet. Add the first one below.").

### Error Page
**Role:** 404 and 5xx pages.
Narrow container. The code (`404`, `503`) in Source Serif 4 64 px Paper Text, the title beside it, then a card with Reason / Error id / Request rows (labels in mono, the request line in mono), then a primary and a ghost button. Error ids in IBM Plex Mono so they are easy to read aloud and copy.

### Steps
**Role:** "how it works", three numbered steps.
Three cards in a row; each opens with a 32 px circle with a 1 px gold hairline and the number in Source Serif 4 University Gold, then an Inter 600 16 px title, a 14 px Archive Gray sentence and a text link.

### Footer
**Role:** the bottom of every page.
1 px Hairline top rule, 24 px padding, centered IBM Plex Mono 12 px upper case Archive Gray, two parts: `YBSB3001 — WEB PROGRAMMING` (`lang="en"`) and `İSTANBUL ÜNİVERSİTESİ · İKTİSAT FAKÜLTESİ · YÖNETİM BİLİŞİM SİSTEMLERİ` (`lang="tr"`), so each language gets its own upper-case letters.

### Page Hero
**Role:** the top of every page except the home page: the home hero without the film (homework: "apply the home page design to all pages").
Centred over the Ledger Grid: the gold Eyebrow pill, a Source Serif 4 500 title (one phrase may be the gold italic `<em>`), optional meta line, the Faculty Line, a lead in Archive Gray and the page's buttons (one primary). Two sizes: **page** (lists and About; title clamp(36px, 5vw, 56px), 40 px top and bottom) and **compact** (details, edit and error pages; title clamp(30px, 4vw, 44px)). Built by `page_hero()` in `layout.py`; `stat_tiles()` and `section_head()` give the home page's counters and section titles. Under it, lists show 4 Stat Tiles; numbers count up, years and spans are shown as text.

### Kicker
**Role:** the small label above every page title that says what kind of page this is (`DIRECTORY · GRADUATES`, `ANNOUNCEMENT #4`, `ERROR 404`).
IBM Plex Mono 500 12 px upper case, 0.08em, Archive Gray, after a 6 px İÜ Green dot. On **edit pages** the kicker turns Gold Tint with a gold dot (`EDITING · USER #3`): the one gold signal that a record is being changed. The gold Eyebrow pill stays on the home hero only.

### Avatar
**Role:** a person in a list or on a profile.
A circle with up to two initials in IBM Plex Mono 500, Green Tint on Raised Panel, 1 px İÜ Green border at 45 %. 32 px in table rows, 64 px (2 px border) on the profile header. No photos.

### Summary Strip
**Role:** the totals above the job postings table (postings · open · closed).
Three tiles in a row, Ledger Panel, 14 px radius, 16 × 20 px padding; mono caption, Source Serif 4 32 px number that counts up; the "open" number in Green Tint, "closed" in Archive Gray.

### Pipeline
**Role:** how many applications are at each status, above the applications table.
Six stages in a row, left to right in the usual order (submitted → under review → interview → accepted → rejected → withdrawn); Ledger Panel, 12 px radius, a 3 px bottom edge and caption in the status colour from §2.4, Source Serif 4 28 px number in Paper Text that counts up. 3 × 2 below 900 px, 2 × 3 below 720 px.

### Album Card
**Role:** one graduate on the Users page, as one of many photos tossed on a table (after the tilted photo clusters of the San Rita reference, in this system's colours).
- **Band:** above the cards a huge Source Serif 4 word, `Graduates`, clamp(84px, 15vw, 216px), line height 0.9, letter spacing 0.01em, drawn as a clean 1.5 px Green Tint outline (45 %): a 3 px stroke painted first and the solid fill `#142220` (Midnight Ink with 7 % Green Tint) on top (`paint-order: stroke fill`), so the overlapping contours inside the variable font's letters never show. The photos are tossed over its lower half. Decorative (`aria-hidden`).
- **Photo:** raw, no frame, square corners, 4:5. The picture is a spot of the campus film (`app/static/film/thumbs/t01–t32.webp`: the gate, the avenue, the Rectorate), chosen by the user id so a graduate always gets the same one; slightly desaturated. The pictures are campus places, not portraits: the database has no photos of graduates.
- **On the photo:** the initials top left in Source Serif 4 44 px; a mono `#07` tag top right in Gold Tint on a dark pill; at the bottom, over a Midnight Ink fade, the name in IBM Plex Mono 500 13 px upper case and `CLASS OF 2017 · DEPARTMENT` in mono 10 px Green Tint.
- **Scatter:** tilts −7° … +7°, shifts of ±8 px across and 0–30 px down, taken from the card's position in the list, so neighbours never share an angle. Each card lies on top of the one before it: the names sit on the left, so a card only covers the empty right edge of its neighbour. Cards are 104 % of their grid cell, so the edges overlap a little. A soft table shadow under each photo.
- **Grid:** `repeat(auto-fill, minmax(230px, 1fr))`, 34 px rows, 14 px columns. Phones: two columns, half the tilt, no overlap.
- **Actions:** Edit and Delete appear under the photo when the card is hovered or focused (always visible on touch screens).
- **Switch:** an **Album / Table** switch (mono, the active one with a gold underline) next to the filter keeps the plain table one click away; the choice is remembered in the browser. The filter works on both.

### Form Card
**Role:** the create form under each list.
A featured card (Faculty Line on its top edge) with the form title in Source Serif 4 22 px and, on the right, one mono rule of the form ("ALL FIELDS REQUIRED", "DESCRIPTION OR LINK REQUIRED"). Reached by the page header's primary "+ New …" button (`#new`).

## 5. Layout Principles

**Base unit:** 4 px · **Density:** comfortable

### Spacing scale

| Name | Value | Token |
|------|-------|-------|
| 4 | 4px | `--space-1` |
| 8 | 8px | `--space-2` |
| 12 | 12px | `--space-3` |
| 16 | 16px | `--space-4` |
| 24 | 24px | `--space-6` |
| 32 | 32px | `--space-8` |
| 48 | 48px | `--space-12` |
| 64 | 64px | `--space-16` |
| 96 | 96px | `--space-24` |

### Radius

| Element | Value |
|---------|-------|
| cards, tables, stat tiles, panels | 14px |
| buttons, inputs, alerts | 10px |
| small buttons (in table rows) | 8px |
| logo mark | 9px |
| badges, eyebrow pills, step circles | 9999px |

### Grid and widths

- **Page max-width:** 1120 px (`.container`); **narrow** 780 px for forms, detail pages and error pages.
- **Side padding:** 24 px; 16 px below 720 px.
- **Section gap:** 64 px on the home page, 32 px inside app pages.
- **Card padding:** 24 px · **Element gap:** 12–16 px · **Grid gap:** 16–20 px.
- **Home page order:** hero → 4 stat tiles → two columns (open job postings 3fr, latest announcements 2fr) → three steps → footer line.
- **App page order:** the home page's outline on every page (the Scroll Film excepted): Page Hero → stat tiles → section heads, filter row, table or album → create form card.

### Page patterns

Each page of the app, and the pattern it uses (all in `app/views/`; `/about` in `app/templates/about.html`):

| Page | Pattern |
|------|---------|
| `/` Home (Turkish) | Scroll Film (§7) carrying the hero (gold eyebrow pill, serif headline with one gold italic phrase, Faculty Line, lead, CTA) and two more captions → 4 counting stat tiles → open postings (featured card) and latest announcements → three steps → mono tech strip. |
| `/about` (Turkish) | Page Hero (`PROJE · YBSB3001`, "Proje *hakkında*") → four fact tiles (course, status, backend, database) → section head "Yol haritası" → the roadmap timeline in a featured card. |
| `/users` | Page Hero (`DIRECTORY · GRADUATES`, "The class *album*") → 4 stat tiles (graduates, class span, departments, newest class) → count, Album / Table switch and filter → the class album of Album Cards (or the table) → form card. |
| `/users/{id}` | Compact Page Hero (`USER #ID · CLASS OF YEAR`, the name, the department; Edit and Applications) → featured card with the details. |
| `/announcements` | Page Hero (`NOTICE BOARD`, "News for *graduates*") → 4 stat tiles (announcements, this year, authors, latest date) → table with each title and a one-line excerpt → form card. |
| `/announcements/{id}` | Compact Page Hero (`ANNOUNCEMENT #ID`, the title, author and date as meta; Edit and All announcements) → the text in a featured card at reading width (68ch). |
| `/job-postings` | Page Hero (`CAREERS · POSTINGS`, "Jobs and *internships*") → 4 stat tiles (postings, open, closed, internships) → table (title with the company under it, type, status badge) → form card. |
| `/job-postings/{id}` | Compact Page Hero (`JOB POSTING #ID · TYPE`, the title, company · city · status; Apply when open, Edit, All job postings) → two columns: role description (featured) and applicants (1.7fr); a sticky side column with the facts card and the apply form (1fr). One column below 900 px. |
| `/applications` | Page Hero (`PIPELINE · APPLICATIONS`, "Applications, *step by step*") → 4 stat tiles (applications, in progress, interviews, accepted) → section head "By status" and the pipeline → table with avatars and the inline status change → form card. |
| `…/edit` pages | Narrow; compact Page Hero (`EDITING · USER #3`, "Edit *user*") → featured card with the form, Save and Cancel → back link to the record. |
| 404 / 5xx | Narrow; compact Page Hero (`ERROR 404`, the title, the reason in one sentence; the way out as buttons) → featured card with mono labels (Requested, Reason, Error id, Request). |

## 6. Depth & Elevation

| Level | Name | Value | Purpose |
|-------|------|-------|---------|
| 0 | Midnight Ink | `#0d1614` | Page canvas, with the Ink Glow at the top. |
| 1 | Inset Field | `#111b19` | Inputs: sit below the panel they are on. |
| 2 | Ledger Panel | `#141f1c` | Cards, tables, tiles. |
| 3 | Raised Panel | `#1a2824` | Headers, hovered rows, active states. |
| 4 | Glass Bar | `rgba(13,22,20,.82)` + 12 px blur | The sticky navbar over scrolling content. |

Depth comes from **surface steps and 1 px rules, not shadows**. Cards, tiles, tables and buttons never cast a shadow. Only something that floats above the page (a dialog, a dropdown, a toast) may use one soft shadow: `0 16px 40px rgba(0, 0, 0, .35)`. No glows on text, no neon edges.

## 7. Motion & Animation

Motion makes the interface feel finished and alive without asking for attention: things **ease into place once**, respond quickly to the hand, and stay still afterwards. Nothing loops except a loading shimmer.

### Tokens

| Name | Value | Token | Use |
|------|-------|-------|-----|
| Instant | 80ms | `--dur-instant` | Press feedback (scale 0.98). |
| Fast | 150ms | `--dur-fast` | Colour and border changes, row hover. |
| Base | 220ms | `--dur-base` | Card lift, nav underline, alerts. |
| Slow | 360ms | `--dur-slow` | Line drawing, panel reveals. |
| Entrance | 560ms | `--dur-entrance` | Page and section entrances. |
| Count | 900ms | `--dur-count` | Stat numbers counting up. |
| Ease Out | `cubic-bezier(0.22, 1, 0.36, 1)` | `--ease-out` | Everything that enters or moves into place. |
| Ease In-Out | `cubic-bezier(0.65, 0, 0.35, 1)` | `--ease-in-out` | Things that move between two states (underline, toggles). |
| Stagger | 60ms | `--stagger` | Delay between items of one group (max 6 items, then all together). |

### Patterns

| Pattern | What moves | Spec |
|---------|-----------|------|
| **Page entrance** | Page header, then the first cards | Fade from 0 to 1 and rise 12 px, Entrance + Ease Out; children stagger 60 ms. Runs once per page load. |
| **Scroll reveal** | Sections with `data-reveal` | Same fade-up when 15 % of the element is on screen; once, never again on scroll back. |
| **Faculty Line draw** | The 3 px gradient line under a hero or section title | `scaleX(0 → 1)` from the left, Slow + Ease Out, 300 ms after the headline appears. |
| **Count-up** | Stat tile numbers | From 0 to the value in Count with Ease Out when the tile becomes visible; tabular figures keep the width still. |
| **Hover lift** | Stat tiles, featured cards, home list items | `translateY(-2px)`, border to İÜ Green at 45 %, Base + Ease Out. Never more than 2 px. |
| **Press** | Buttons | `scale(0.98)` for Instant; back with Fast. |
| **Nav underline** | Active / hovered navbar link | 2 px gold line `scaleX(0 → 1)` from the left, Base + Ease In-Out. |
| **Row hover** | Table rows | Background to the Forest tint, Fast. |
| **Filter** | Table rows hidden by the filter box | Fade out over Fast, then collapse. |
| **Alert in** | Error alert | Slide down 8 px + fade in, Base + Ease Out; the page does not jump (space is reserved). |
| **Focus** | Any interactive element | The ring appears at once (no transition): focus must never feel late. |
| **Loading shimmer** | Placeholder rows while a list loads | A soft light band across `--color-panel-2`, 1.4 s linear, repeats; contrast stays under 1.1 : 1. |
| **Page change** | Navigating between pages | Cross-fade 200 ms with the View Transitions API where the browser supports it; nothing where it does not. |
| **Album toss** | Album Cards on `/users` | Once, as they come into view: from 72 px lower, 2.2 times their tilt and 92 % size to their place, 760 ms Ease Out, 80 ms stagger, like photos thrown on a table. Under the pointer a card comes to the top, straightens, lifts 8 px, grows to 106 % and gets the floating shadow; its photo zooms to 106 % and regains full colour. |
| **Scroll Film** | The home page hero only | See below. The one exception to rules 3 and 4. |

### Scroll Film (home page only)

A 10-second film (generated with Google Flow from photos of the campus) walks from Beyazıt Square through the main gate of Istanbul University and down the plane-tree avenue to the Rectorate. It plays **with the scroll**, not by itself: scrolling down moves forward, scrolling up moves back. **Desktop only** (900 px and wider); phones get the still version.

| Part | Spec |
|------|------|
| Placement | Edge to edge under the navbar, outside the page container (`render_page(..., full_width=film)`); only on `/`. |
| Technique | A frame sequence drawn on a `<canvas>`, not a video: 160 WebP frames (16 per second of film) in two sets made from the 1080p Flow export: **1920×1080** (about 124 KB a frame, 19.4 MB) for canvases wider than 1400 device pixels, and **1280×720** (about 73 KB, 11.5 MB) for smaller screens. Quality 74: quality 66 saved only 9 % and lost detail. Picking a frame costs nothing, unlike seeking an mp4 (about 80 ms per seek), so it runs at 60 fps on ordinary computers (measured: 7 ms median, 14 ms at the 95th percentile while scrolling fast). |
| Loading | Coarse to fine: every 16th frame first (plus the last), then every 8th, 4th, 2nd and the rest, at most 6 requests at a time, each decoded before use. Scrolling works as soon as the first frames arrive and gets finer while the rest load; until a frame is there, its nearest loaded neighbour is drawn. |
| Length | The section is 320vh tall; its stage sticks to the screen (100vh) while the section scrolls past. Scroll progress 0 → 1 maps to frame 1 → 160. |
| Easing | The shown position eases toward the scroll position (18 % of the gap per animation frame: a light inertia) and the two neighbouring frames are blended by the fraction between them, so the motion stays smooth between frames. When the scroll stops (140 ms), the film settles on the nearest whole frame, so a still picture is never a double image. Frames are scaled with `imageSmoothingQuality = high`. Nothing is drawn while the film is off screen. |
| Shade | A Midnight Ink overlay (70 % at the top, 45–55 % in the middle, solid ink at the bottom so the film runs into the page) and a soft dark centre behind the text. Captions stay readable on every frame. |
| Captions | Three, each shown for a range of the progress: 0–0.30 the hero; 0.36–0.66 `BEYAZIT · ANA KAPI` "Her mezun bir gün bu kapıdan geçti."; 0.74–1 `REKTÖRLÜK` "Ağ burada büyüyor.". They fade and rise 12 px (Entrance). Kickers are Gold Tint here. |
| Signs | A "Kaydırın" cue with a gold line under the hero; a 2 px Faculty Line progress bar along the bottom of the stage. |
| Fallback | On screens narrower than 900 px, without JavaScript, without canvas, under `prefers-reduced-motion`, or before the script runs: one screen, the first frame as a picture, the hero caption, no cue, no bar. Only that one frame is downloaded. |
| Files | `app/static/film/frames/1080/` and `frames/720/`, `f001.webp` … `f160.webp` each, made from the 1080p Flow mp4 with ffmpeg in one pass: `-filter_complex "fps=16,split=2[a][b];[a]scale=1920:1080:flags=lanczos[o1];[b]scale=1280:720:flags=lanczos[o2]"` and `-c:v libwebp -quality 74 -compression_level 6 -preset photo` for each output. The still picture uses `srcset` to pick the right first frame. The frame count is `FILM_FRAMES` in `home_view.py`. Served as `image/webp` (registered in `main.py`). |

### Rules

1. Animate only `opacity` and `transform` (and `background-color` / `border-color` for hovers): never `width`, `height`, `top` or `margin`.
2. Entrances run once; nothing re-animates on scroll back or on every hover of a static element.
3. At most one entrance group plays at a time; total entrance time of a page stays under 1 second.
4. Moving distance is small: 2 px for hovers, 8–12 px for entrances. No bouncing, no overshoot, no rotation, no parallax (the Scroll Film below is the single, deliberate exception).
5. **`prefers-reduced-motion: reduce`:** all transforms and the shimmer are switched off, durations drop to 1 ms, counters show their final number at once, the Faculty Line is drawn from the start. Colour changes stay.
6. Content is readable before any animation finishes: an element that never animates (no JavaScript, old browser) must still be fully visible.

## 8. Do's and Don'ts

### Do
- Use Midnight Ink `#0d1614` as the canvas and Ledger Panel `#141f1c` for every card and table.
- Use İÜ Green `#439c86` for links, focus and active states; Istanbul University's colour is the system's signal.
- Keep University Gold `#b8860b` to one element per screen: the gold word, the active underline, the eyebrow.
- Set headlines, page titles, stat numbers and error codes in Source Serif 4; everything people read or click in Inter; everything the system records in IBM Plex Mono.
- Separate surfaces with 1 px Hairline `#273732` rules and surface steps.
- Give every error a reason in one plain sentence, and every server error an error id in mono.
- Respect `prefers-reduced-motion` and keep every text colour at WCAG AA or better.
- Set `lang="tr"` on Turkish pages so upper-case labels write `İ` correctly.

### Don't
- Don't use the Istanbul University logo or emblem, or imitate them; the connection is shown by colour and a text line.
- Don't put white text on İÜ Green (3.31 : 1) or use Signal Red `#dc3545` as text (3.73 : 1).
- Don't use pure white `#ffffff` text on large areas or pure black `#000000` surfaces.
- Don't add drop shadows to cards, tiles, tables or buttons; don't add glows.
- Don't put the Faculty Line or any gradient behind text.
- Don't use more than one gold element per screen, or gold for large fills.
- Don't animate layout properties, loop decorative animations, or move anything more than 12 px.
- Don't set body text or buttons in the serif, or headings in the mono.

## 9. Responsive Behavior

| Breakpoint | Changes |
|------------|---------|
| ≥ 900 px | Full layout: 4 stat tiles in a row, home lists side by side (3fr / 2fr), steps in three columns. |
| 720–899 px | Stat tiles 2 × 2; home lists and steps stack into one column. |
| < 720 px | Side padding 16 px; navbar wordmark above the links, links scroll sideways; forms and detail lists one column; tables scroll sideways inside their card (min width 680 px); hero headline down to 40 px. |

- **Touch targets:** at least 40 × 40 px (buttons, nav links, table actions).
- **Hover-only effects** (lift, underline preview) never carry information; on touch screens the active states are enough.
- **Images and decoration:** the Ledger Grid shrinks to 24 px cells below 720 px and fades out sooner.

## 10. Agent Prompt Guide

### Quick colour reference
- canvas: `#0d1614` · panel: `#141f1c` · raised: `#1a2824` · field: `#111b19` · rule: `#273732`
- text: `#e3e9e6` · muted: `#98a7a1`
- primary (İÜ green): `#439c86` · primary button: `#2c7a64` (white text) · gold accent: `#b8860b`
- in progress: `#86aed6` on navy · good: `#6cbca6` on forest · refused: `#e8857c` on red tint

### Example prompts

1. **Home hero.** "Create a centered hero on `#0d1614` over a faint ledger grid (1 px `rgba(67,156,134,.06)` lines every 32 px, plus marks every 128 px, masked to fade at the bottom). Eyebrow pill in IBM Plex Mono 12px upper case gold `#b8860b`: `İSTANBUL ÜNİVERSİTESİ · İKTİSAT FAKÜLTESİ · YBS`. Headline in Source Serif 4 500 at clamp(40px, 6vw, 64px), line height 1.05, `#e3e9e6`, with the last phrase in `#b8860b`. Under it a 3 × 56 px line `linear-gradient(90deg, #439c86, #2c7a64)` that draws from the left. Lead in Inter 18px `#98a7a1`, max 60ch. A primary button (`#2c7a64`, white Inter 600 14px, 10px radius) and a ghost button. Fade the block up 12px over 560ms with cubic-bezier(0.22,1,0.36,1); none of it moves under prefers-reduced-motion."
2. **Stat tiles.** "Create four linked stat tiles in a row (2 × 2 below 900px): `#141f1c`, 1px `#273732` border, 14px radius, 24px padding. Caption IBM Plex Mono 12px upper case `#98a7a1`; number Source Serif 4 500 44px tabular `#e3e9e6`, counting up from 0 over 900ms when visible; optional note Inter 13px `#6cbca6`. Hover: lift 2px and border `rgba(67,156,134,.45)` over 220ms. No shadows."
3. **List page.** "Create a list page: header with a Source Serif 4 600 36px title, an Inter 15px `#98a7a1` subtitle and a primary button on the right; a filter input on `#111b19`; a table in a `#141f1c` card with 14px radius, header row `#1a2824` in IBM Plex Mono 11px upper case, rows Inter 14px with 1px `#273732` dividers, hover row `rgba(0,106,78,.12)`, ids and dates in mono tabular, status badges per the status table, small Edit (ghost) and Delete (danger) buttons on the right."
4. **Form with an error.** "Create a narrow (780px) page with a card holding a two-column form: labels Inter 500 13px `#98a7a1`, fields on `#111b19` with 1px `#273732` border and 10px radius, focus border `#439c86` with a 3px `rgba(67,156,134,.22)` ring. Above the card an alert: `#2a1714` fill, 1px `rgba(220,53,69,.4)` border, `#f3d9d6` text, sliding down 8px as it appears. Keep what the user typed in the fields."
5. **404 page.** "Create a narrow error page: `404` in Source Serif 4 64px `#e3e9e6` next to 'Page not found', then a `#141f1c` card listing Reason and Request (labels in IBM Plex Mono 12px upper case, the request line in mono), then a primary 'Go to the home page' button and ghost links to the main sections."

## 11. Iteration Guide

1. Change one component at a time and name it by its `components:` token (`button-primary`, `stat-tile`, `status-badge-good`).
2. Before adding a section, decide which surface it sits on: `{colors.ink}` canvas, `{colors.panel}` card or `{colors.panel-2}` raised.
3. Body text is `{typography.body}` at 400; serif only for headings and numbers, mono only for recorded values.
4. Treat `{colors.gold}` as scarce: one element per screen. Treat `{colors.primary}` as the signal: links, focus, active, good outcomes.
5. A new state is a new component entry (`button-primary-hover`), not an inline override.
6. A new animation uses the motion tokens in §7 and gets a reduced-motion fallback in the same change.
7. After editing, check the tokens: `npx @google/design.md lint DESIGN.md`, and re-check contrast for any new text colour (target WCAG AA, see [brand.md §6](brand.md#6-contrast-table)).
8. Change `DESIGN.md`, `brand.md` and `app/static/app.css` in the same commit.

## 12. Known Gaps

- **Token names in code:** `app.css` drops the `color-` prefix of the Quick Start (`--primary` for `--color-primary`); the values are the same.
- **Tables on phones** scroll sideways inside their card instead of turning into cards.
- **Scroll Film weight:** desktops load 11.5 MB (1280 set) or 19.4 MB (1920 set) of frames on the first visit to the home page (cached afterwards). Phones load only the first frame; a phone version of the film is not made.
- **Front matter limits:** the Stitch format has no tokens for motion, gradients, borders or focus rings, so those live in the prose (§2.3, §7) and in the Quick Start CSS. `hero-display` is listed at 64px; on the page it is `clamp(40px, 6vw, 64px)`.
- **Status badge fills** are translucent tints (§2.4); the front matter lists the nearest solid surface because it takes plain hex values only.
- **Light mode** is not defined; the site is dark only (`color-scheme: dark`).
- **Dialogs, dropdowns and toasts** do not exist in the app yet; only their shadow (`--shadow-float`) is decided.
- **Fonts** load from Google Fonts; with no network the system fallbacks (Georgia, Segoe UI, Consolas) are used and the layout must still hold.

## Quick Start

### Fonts

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" />
```

### CSS custom properties

```css
:root {
  color-scheme: dark;

  /* Surfaces and text */
  --color-ink: #0d1614;
  --color-panel: #141f1c;
  --color-panel-2: #1a2824;
  --color-field: #111b19;
  --color-border: #273732;
  --color-text: #e3e9e6;
  --color-muted: #98a7a1;

  /* Brand and signals (Istanbul University colours) */
  --color-primary: #439c86;
  --color-primary-light: #6cbca6;
  --color-primary-deep: #2c7a64;
  --color-primary-deep-hover: #26705b;
  --color-forest: #006a4e;
  --color-gold: #b8860b;
  --color-gold-light: #d4a64a;
  --color-navy: #1a3a5a;
  --color-navy-light: #86aed6;
  --color-danger: #dc3545;
  --color-danger-soft: #e8857c;

  /* Gradient and atmosphere */
  --gradient-line: linear-gradient(90deg, #439c86, #2c7a64);
  --glow-page:
    radial-gradient(circle at 15% 0%, rgba(67, 156, 134, 0.10), transparent 42%),
    radial-gradient(circle at 85% 0%, rgba(184, 134, 11, 0.05), transparent 40%);

  /* Typography */
  --font-display: "Source Serif 4", Georgia, "Times New Roman", serif;
  --font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --text-hero: clamp(40px, 6vw, 64px);
  --text-page-title: 36px;
  --text-section: 28px;
  --text-stat: 44px;
  --text-body-large: 18px;
  --text-body: 15px;
  --text-ui: 14px;
  --text-caption: 13px;
  --text-eyebrow: 12px;
  --text-badge: 11px;

  /* Spacing (4px base) */
  --space-1: 4px;  --space-2: 8px;  --space-3: 12px; --space-4: 16px;
  --space-6: 24px; --space-8: 32px; --space-12: 48px; --space-16: 64px; --space-24: 96px;

  /* Radius */
  --radius-card: 14px;
  --radius-control: 10px;
  --radius-small: 8px;
  --radius-pill: 9999px;

  /* Layout */
  --page-max-width: 1120px;
  --page-narrow: 780px;

  /* Elevation (floating elements only) */
  --shadow-float: 0 16px 40px rgba(0, 0, 0, 0.35);

  /* Motion */
  --dur-instant: 80ms;
  --dur-fast: 150ms;
  --dur-base: 220ms;
  --dur-slow: 360ms;
  --dur-entrance: 560ms;
  --dur-count: 900ms;
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --stagger: 60ms;
}
```

### Motion keyframes and helpers

```css
@keyframes at-fade-up {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: none; }
}
@keyframes at-draw-line {
  from { transform: scaleX(0); }
  to   { transform: scaleX(1); }
}
@keyframes at-shimmer {
  from { background-position: -200% 0; }
  to   { background-position: 200% 0; }
}

/* Entrance: content is visible by default; JS adds .reveal only when it can also reveal it. */
.reveal { opacity: 0; transform: translateY(12px); }
.reveal.is-visible {
  animation: at-fade-up var(--dur-entrance) var(--ease-out) both;
  animation-delay: calc(var(--i, 0) * var(--stagger));
}

.faculty-line {
  width: 56px; height: 3px; border-radius: 2px;
  background: var(--gradient-line);
  transform-origin: left;
  animation: at-draw-line var(--dur-slow) var(--ease-out) 300ms both;
}

.lift { transition: transform var(--dur-base) var(--ease-out), border-color var(--dur-base) var(--ease-out); }
.lift:hover { transform: translateY(-2px); border-color: rgba(67, 156, 134, 0.45); }

.btn:active { transform: scale(0.98); transition-duration: var(--dur-instant); }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 1ms !important;
    animation-delay: 0ms !important;
    transition-duration: 1ms !important;
  }
  .reveal { opacity: 1; transform: none; }
  .lift:hover { transform: none; }
}
```

```js
// Scroll reveal + count-up. Elements stay visible if this script never runs.
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const io = new IntersectionObserver((entries) => {
  for (const e of entries) {
    if (!e.isIntersecting) continue;
    e.target.classList.add("is-visible");
    const n = e.target.querySelector("[data-count]");
    if (n && !reduce) {
      const end = Number(n.dataset.count), t0 = performance.now(), dur = 900;
      const tick = (t) => {
        const p = Math.min((t - t0) / dur, 1);
        n.textContent = Math.round(end * (1 - Math.pow(1 - p, 4)));
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    }
    io.unobserve(e.target);
  }
}, { threshold: 0.15 });
if (!reduce) document.querySelectorAll("[data-reveal]").forEach((el, i) => {
  el.classList.add("reveal"); el.style.setProperty("--i", i % 6); io.observe(el);
});
```

## References

What this system took from the references it was built from:

| Reference | Taken | Left out |
|-----------|-------|----------|
| [awesome-design-md](https://github.com/VoltAgent/awesome-design-md) (Google Stitch DESIGN.md format, read from the repository archive) | The `version: alpha` front matter (colors, typography, rounded, spacing, components with `{token}` references), as in Linear, Stripe and Mercury; the nine sections and their order; semantic colour names with roles; the agent prompt guide; the Iteration Guide and Known Gaps endings. | The per-site `preview.html` catalogues. Motion was added as an extra section: none of the 84 files has one. |
| Baselayer style reference | Serif statements for institutional authority; mono labels as system notation; 1 px rules instead of shadows; the grid backdrop with plus registration marks; one gradient only, used for a system line. | The white editorial canvas and electric blue (the identity here is İÜ green on ink); 0 px card corners. |
| AI for Business style reference | Flat surfaces with zero shadows; one chromatic accent kept to small elements; mono micro-labels. | Brutalist upper-case condensed display type; very large radii; the neon yellow. |
| San Rita style reference | A green-tinted near-black canvas instead of pure black; a single highlight colour used like a marker. | Full-bleed photography, tilted photo collages, 0 px radius everywhere, mono body text. |
| [brand.md](brand.md) | Every colour, the logo, the contrast table, the voice. | — |

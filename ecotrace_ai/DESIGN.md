---
name: EcoTrace AI
colors:
  surface: '#f9f9ff'
  surface-dim: '#cfdaf2'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f0f3ff'
  surface-container: '#e7eeff'
  surface-container-high: '#dee8ff'
  surface-container-highest: '#d8e3fb'
  on-surface: '#111c2d'
  on-surface-variant: '#3d4a42'
  inverse-surface: '#263143'
  inverse-on-surface: '#ecf1ff'
  outline: '#6d7a72'
  outline-variant: '#bccac0'
  surface-tint: '#006c4a'
  primary: '#006948'
  on-primary: '#ffffff'
  primary-container: '#00855d'
  on-primary-container: '#f5fff7'
  inverse-primary: '#68dba9'
  secondary: '#006c49'
  on-secondary: '#ffffff'
  secondary-container: '#6cf8bb'
  on-secondary-container: '#00714d'
  tertiary: '#825100'
  on-tertiary: '#ffffff'
  tertiary-container: '#a36700'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#85f8c4'
  primary-fixed-dim: '#68dba9'
  on-primary-fixed: '#002114'
  on-primary-fixed-variant: '#005137'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#f9f9ff'
  on-background: '#111c2d'
  surface-variant: '#d8e3fb'
typography:
  display-lg:
    fontFamily: Space Grotesk
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Space Grotesk
    fontSize: 26px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.02em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.04em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-desktop: 2.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system delivers a balance of environmental analytical rigor and accessible consumer utility. Built specifically for structured data applications and computational dashboards, the visual tone merges environmental science with technical instrumentation. 

The aesthetic is clean, modern, and data-centric—moving away from generic flat corporate styles toward an intentional, calibrated laboratory workbench feel. It relies on crisp surface segmentation, precise 1px borders, calibrated badge states, and structural information hierarchy. The interface prioritizes high-density data legibility, structured Streamlit widget containers, analytical feedback loops, and actionable carbon-reduction insights without visual clutter.

## Colors

The palette grounds high-contrast analytical data onto calm, low-strain bio-tinted surfaces.

### Semantic Palette Breakdown
- **Primary (`#059669`)**: Deep forest emerald. Applied to primary call-to-actions, focused tabs, confirmed calculation checkpoints, and active form submissions.
- **Secondary (`#10B981`)**: Vibrant eco-leaf green. Applied to sub-metrics, trend indicators showing emission drops, positive delta indicators, and progress bars.
- **Tertiary / Warning (`#F59E0B`)**: High-emission alert amber. Reserved strictly for critical emission thresholds, abnormal consumption spikes, and cautionary carbon budget limits.
- **Neutral Surface Canvas (`#F3F7F4`)**: Primary application canvas wash; reduces screen glare compared to pure `#FFFFFF`.
- **Neutral Surface Raised (`#E8F0EB`)**: Used for secondary cards, sidebar navigation, table headers, and metric card backgrounds.
- **Neutral Slate Ink (`#1E293B`)**: Base typography color providing deep contrast for technical labels, tabular numerals, and titles.
- **Muted Ink (`#64748B`)**: Secondary text color for unit measures (e.g., `kg CO2e`), helper descriptions, and inactive states.
- **Border / Outline (`#D1E0D7`)**: Subdued structural borders that frame metrics, input controls, and chart surfaces.

## Typography

The typographic stack balances technical authority with high data readability.

- **Headlines (`Space Grotesk`)**: Expresses the system’s computational and scientific nature. Used across headers, big numerical readouts, and section titles.
- **Body (`Inter`)**: Delivers neutral clarity for conversational insights, automated recommendations, user inputs, and analytical prose.
- **Labels & Data Tags (`JetBrains Mono`)**: Handles all tabular numerals, telemetry data bindings (`st.metric`), units (`kg CO2e/kWh`), code-like state identifiers, and timestamp chips. Tabular figure settings must remain enabled across metrics to ensure zero jitter during real-time data streaming.

## Layout & Spacing

The layout model is governed by a fluid-responsive grid system optimized for desktop data workbenches and structured mobile feeds.

### Grid Architecture
- **Desktop (>= 1024px)**: 12-column layout with `gutter-desktop` (24px) and page `margin-desktop` (40px). Max content container constrained to `1280px` for optimal chart readability.
- **Tablet (768px - 1023px)**: 8-column fluid layout with `gutter` (16px) and `margin` (24px).
- **Mobile (< 768px)**: 4-column fluid layout with `gutter` (16px) and `margin` (16px). Streamlit sidebars collapse into a full-bleed overlay drawer.

### Metric Rhythm
- Spacing relies strictly on 4px base increments (`space-xs` = 4px, `space-sm` = 8px, `space-md` = 16px, `space-lg` = 24px, `space-xl` = 40px).
- Component panels maintain an internal padding of `space-md` on mobile and `space-lg` on desktop.
- Dashboard cards in multi-column layouts align horizontally using `gutter` spacing tokens to maintain clean visual baselines across metrics and charts.

## Elevation & Depth

This design system deliberately minimizes standard blurred drop shadows to avoid visual murkiness, choosing instead a technical **Tonal Layer + Low-Contrast Outline** hierarchy.

- **Level 0 (Canvas Base)**: Pure `#F3F7F4`. Hosts non-interactive layout scaffolding and outer grid wrappers.
- **Level 1 (Card & Module Layer)**: Pure `#FFFFFF` surface framed with a 1px solid `#D1E0D7` outline. An ultra-subtle ambient tint `0 1px 3px rgba(30, 41, 59, 0.04)` grounds primary cards, metric blocks, and chart panels.
- **Level 2 (Interactive Floating Elements / Popovers / Tooltips)**: `#FFFFFF` surface framed with `#059669` (for active/focus states) or `#CBD5E1` (neutral). Elevation is reinforced by an ambient shadow: `0 4px 12px rgba(15, 23, 42, 0.08)`.
- **Level 3 (Alerts & Modal Overlays)**: Surface `#FFFFFF` with high-emphasis perimeter outline: 1px `#F59E0B` for high-emission alerts, backed by a scrim: `rgba(30, 41, 59, 0.4)`.

## Shapes

The design system implements geometric roundedness (`0.5rem` / `8px` default corner radius), communicating precision without appearing abrasive.

- **Base Controls (`rounded` = 8px)**: Input fields, buttons, dropdown selects, and badge tags.
- **Containers (`rounded-lg` = 16px)**: Metric cards, chart visualization frames, and tab sheet containers.
- **Deep Containers (`rounded-xl` = 24px)**: Outer dialog modals, alert drawers, and hero summary blocks.
- **Pills (`9999px`)**: Reserved exclusively for operational status pills (e.g., `ML MODEL: ACTIVE`, `STREAMING`, `CACHED`).

## Components

### Buttons (`st.button`, `st.form_submit_button`)
- **Primary Button**: Solid `#059669` fill, `#FFFFFF` text (`Inter`, 14px, semi-bold), 8px border-radius, padding: `8px 18px`. Hover: `#047857`. Focus outline: 2px solid `#10B981` offset by 2px.
- **Secondary Button**: Background `#FFFFFF`, 1px solid `#D1E0D7`, text `#1E293B`. Hover: background `#E8F0EB`, border `#059669`.
- **Destructive / Reset Button**: Background `#FEF2F2`, 1px solid `#FCA5A5`, text `#DC2626`.

### Badges & State Tags
- Monospace font (`JetBrains Mono`, 11px, medium). Padding: `2px 8px`, border radius `4px`.
- **Active / Validated**: Background `#ECFDF5`, border `#A7F3D0`, text `#065F46`.
- **Warning / High-Emission**: Background `#FFFBEB`, border `#FDE68A`, text `#92400E`.
- **Empty / Inactive**: Background `#F1F5F9`, border `#CBD5E1`, text `#64748B`.
- **Loading / Estimating**: Background `#EFF6FF`, border `#BFDBFE`, text `#1D4ED8` with pulsating indicator dot.

### Streamlit Metric Wrappers (`st.metric`)
- Rendered inside Level 1 cards (`#FFFFFF` background, 1px `#D1E0D7` border, 16px padding).
- **Label**: `Space Grotesk`, 12px uppercase, text `#64748B`.
- **Value**: `JetBrains Mono`, 28px, semi-bold, text `#1E293B`.
- **Delta Indicator**: `JetBrains Mono`, 12px, pill-styled. Downward delta (reduction in carbon): `#ECFDF5` background, `#059669` text with downward icon. Upward delta (emission increase): `#FEF2F2` background, `#DC2626` text with upward icon.

### Form Inputs (`st.text_input`, `st.number_input`, `st.selectbox`, `st.slider`)
- **Base Style**: `#FFFFFF` background, 1px solid `#D1E0D7`, 8px border-radius, height 40px, text `#1E293B` (`Inter`, 14px).
- **Focus State**: Border color shifted to `#059669`, with `0 0 0 1px #059669` ring.
- **Sliders**: Track rendered in `#E8F0EB`, filled track `#059669`, thumb handle in `#059669` with 2px `#FFFFFF` inner ring.

### Navigation & Tabs (`st.tabs`)
- Horizontal rule styling with bottom-border docking.
- **Default Tab**: Text `#64748B`, font-weight 500, no bottom line, transparent background.
- **Active Tab**: Text `#059669`, font-weight 600, bottom active indicator bar: 2px solid `#059669`.

### Chart Containers (`st.altair_chart`, `st.pyplot`)
- Charts must be enclosed in an isolated card container (`#FFFFFF` background, 16px internal padding, 1px `#D1E0D7` border).
- Color themes for data visualization: Primary series `#059669`, comparison baseline `#94A3B8`, target limit `#F59E0B`, warning threshold `#EF4444`. Grid lines set to `#E2E8F0` at 1px stroke dashed.
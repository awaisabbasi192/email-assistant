# Premium Web Design - Code Templates & Utilities

Quick reference templates for implementing premium, responsive websites.

---

## Responsive Typography System

### Fluid Typography with clamp()

```css
:root {
  /* Mobile-first base size */
  --text-xs: clamp(0.75rem, 1.5vw, 0.875rem);
  --text-sm: clamp(0.875rem, 1.8vw, 1rem);
  --text-base: clamp(1rem, 2vw, 1.125rem);
  --text-lg: clamp(1.125rem, 2.5vw, 1.375rem);
  --text-xl: clamp(1.375rem, 3.5vw, 1.75rem);
  --text-2xl: clamp(1.75rem, 4.5vw, 2.25rem);
  --text-3xl: clamp(2rem, 5.5vw, 3rem);
  --text-4xl: clamp(2.5rem, 7vw, 3.5rem);
}

body {
  font-size: var(--text-base);
  line-height: 1.6;
}

h1 { font-size: var(--text-4xl); line-height: 1.2; }
h2 { font-size: var(--text-3xl); line-height: 1.25; }
h3 { font-size: var(--text-2xl); line-height: 1.3; }
h4 { font-size: var(--text-xl); line-height: 1.4; }
p { font-size: var(--text-base); line-height: 1.7; }
small { font-size: var(--text-sm); }
```

---

## Responsive Spacing System

### Fluid Spacing with clamp()

```css
:root {
  /* Spacing scale that grows with viewport */
  --space-2xs: clamp(0.25rem, 0.5vw, 0.5rem);
  --space-xs: clamp(0.5rem, 1vw, 0.75rem);
  --space-sm: clamp(0.75rem, 1.5vw, 1rem);
  --space-md: clamp(1rem, 2vw, 1.5rem);
  --space-lg: clamp(1.5rem, 3vw, 2rem);
  --space-xl: clamp(2rem, 4vw, 3rem);
  --space-2xl: clamp(2.5rem, 5vw, 4rem);
  --space-3xl: clamp(3rem, 6vw, 5rem);
}

/* Usage */
header {
  padding: var(--space-lg) var(--space-md);
}

section {
  padding: var(--space-3xl) var(--space-md);
}

.card {
  padding: var(--space-lg);
  margin-bottom: var(--space-xl);
}

@media (max-width: 768px) {
  section {
    padding: var(--space-2xl) var(--space-sm);
  }
}
```

---

## Color System with Dark Mode

### Theme Setup

```css
:root {
  /* Light mode */
  --color-bg: #ffffff;
  --color-surface: #f9f9f9;
  --color-text: #1a1a1a;
  --color-text-secondary: #666666;
  --color-text-tertiary: #999999;
  --color-border: #eeeeee;
  --color-primary: #0066cc;
  --color-primary-dark: #0052a3;
  --color-primary-light: #e6f0ff;
  --color-accent: #ff6b35;
  --color-success: #2d8659;
  --color-warning: #cc8800;
  --color-error: #cc0000;
}

@media (prefers-color-scheme: dark) {
  :root {
    /* Dark mode */
    --color-bg: #0f0f0f;
    --color-surface: #1a1a1a;
    --color-text: #f5f5f5;
    --color-text-secondary: #b0b0b0;
    --color-text-tertiary: #808080;
    --color-border: #333333;
    --color-primary: #5599ff;
    --color-primary-dark: #88bbff;
    --color-primary-light: #1a3a66;
    --color-accent: #ff8866;
    --color-success: #66dd99;
    --color-warning: #ffbb33;
    --color-error: #ff6666;
  }
}

body {
  background-color: var(--color-bg);
  color: var(--color-text);
}

.section-alternate {
  background-color: var(--color-surface);
}

a {
  color: var(--color-primary);
}

a:hover {
  color: var(--color-primary-dark);
}

button.primary {
  background-color: var(--color-primary);
  color: white;
}

button.secondary {
  background-color: transparent;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
}
```

---

## Mobile-First Responsive Grid

### Flexible Grid with Auto-Fit

```css
/* 1 column mobile, 2 tablet, 3+ desktop */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: clamp(1rem, 3vw, 2rem);
}

/* 2 column minimum */
.grid-2col {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: clamp(1rem, 3vw, 2rem);
}

/* 3 column minimum */
.grid-3col {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: clamp(1rem, 3vw, 2rem);
}

/* Specific breakpoints if needed */
@media (max-width: 640px) {
  .grid-3col {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 768px) and (max-width: 1024px) {
  .grid-3col {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

### Masonry-Style Gallery

```css
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  auto-rows: 250px;
  gap: 1rem;
}

.gallery-item {
  position: relative;
  overflow: hidden;
  border-radius: 8px;
  background: var(--color-surface);
}

.gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.gallery-item:hover img {
  transform: scale(1.05);
}

/* Varied sizes for visual interest */
.gallery-item:nth-child(3n) {
  grid-column: span 2;
}

.gallery-item:nth-child(4n) {
  grid-row: span 2;
}

@media (max-width: 768px) {
  .gallery {
    grid-template-columns: repeat(2, 1fr);
    auto-rows: 200px;
  }

  .gallery-item:nth-child(3n) {
    grid-column: span 1;
  }

  .gallery-item:nth-child(4n) {
    grid-row: span 1;
  }
}

@media (max-width: 480px) {
  .gallery {
    grid-template-columns: 1fr;
    auto-rows: 300px;
  }
}
```

---

## Touch-Friendly Components

### Responsive Button

```css
button, .btn {
  /* Minimum 44px touch target */
  padding: 0.75rem 1.5rem;
  min-height: 44px;
  min-width: 44px;

  font-size: var(--text-base);
  font-weight: 600;

  border: none;
  border-radius: 6px;

  background-color: var(--color-primary);
  color: white;

  cursor: pointer;
  transition: background-color 0.2s ease;

  /* Extra padding on mobile */
  @media (max-width: 768px) {
    padding: 1rem 1.75rem;
  }
}

button:hover {
  background-color: var(--color-primary-dark);
}

button:active {
  transform: scale(0.98);
}

button:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* Secondary button */
button.secondary {
  background-color: transparent;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
}

button.secondary:hover {
  background-color: var(--color-primary-light);
}
```

### Responsive Form

```html
<form class="form" novalidate>
  <div class="form-group">
    <label for="name">Name</label>
    <input
      type="text"
      id="name"
      name="name"
      required
      placeholder="Your name"
    />
  </div>

  <div class="form-group">
    <label for="email">Email</label>
    <input
      type="email"
      id="email"
      name="email"
      required
      placeholder="your@email.com"
    />
  </div>

  <div class="form-group">
    <label for="message">Message</label>
    <textarea
      id="message"
      name="message"
      rows="5"
      required
      placeholder="Your message..."
    ></textarea>
  </div>

  <button type="submit">Send Message</button>
</form>
```

```css
.form {
  max-width: 500px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: var(--space-lg);
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  font-size: var(--text-sm);
  color: var(--color-text);
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;

  font-size: 16px; /* Prevents zoom on iOS */
  font-family: inherit;

  border: 2px solid var(--color-border);
  border-radius: 6px;

  background-color: var(--color-surface);
  color: var(--color-text);

  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

/* Mobile-friendly form */
@media (max-width: 640px) {
  .form-group input,
  .form-group textarea {
    font-size: 16px; /* Prevent zoom on iOS */
    padding: 1rem;
  }
}
```

---

## Navigation Patterns

### Responsive Navigation Bar

```html
<header class="navbar">
  <nav class="nav-container">
    <div class="nav-logo">
      <a href="/">Logo</a>
    </div>

    <button class="nav-toggle" aria-label="Toggle navigation" aria-expanded="false">
      <span></span>
      <span></span>
      <span></span>
    </button>

    <ul class="nav-menu">
      <li><a href="#home">Home</a></li>
      <li><a href="#about">About</a></li>
      <li><a href="#work">Work</a></li>
      <li><a href="#contact">Contact</a></li>
    </ul>
  </nav>
</header>
```

```css
.navbar {
  background-color: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem var(--space-md);

  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-logo a {
  font-size: var(--text-lg);
  font-weight: 700;
  text-decoration: none;
  color: var(--color-text);
}

.nav-menu {
  display: flex;
  list-style: none;
  gap: 2rem;
  margin: 0;
  padding: 0;
}

.nav-menu a {
  text-decoration: none;
  color: var(--color-text);
  font-weight: 500;
  transition: color 0.2s ease;
}

.nav-menu a:hover {
  color: var(--color-primary);
}

/* Mobile hamburger */
.nav-toggle {
  display: none;
  flex-direction: column;
  background: none;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
}

.nav-toggle span {
  width: 24px;
  height: 3px;
  background-color: var(--color-text);
  margin: 4px 0;
  transition: all 0.3s ease;
  border-radius: 2px;
}

/* Mobile menu */
@media (max-width: 768px) {
  .nav-toggle {
    display: flex;
  }

  .nav-menu {
    position: absolute;
    top: 100%;
    left: 0;
    width: 100%;
    flex-direction: column;
    gap: 1rem;
    background-color: var(--color-surface);
    padding: var(--space-lg) var(--space-md);
    display: none;
  }

  .nav-menu.active {
    display: flex;
  }

  .nav-toggle.active span:nth-child(1) {
    transform: rotate(45deg) translate(8px, 8px);
  }

  .nav-toggle.active span:nth-child(2) {
    opacity: 0;
  }

  .nav-toggle.active span:nth-child(3) {
    transform: rotate(-45deg) translate(7px, -7px);
  }
}
```

```javascript
// Toggle mobile menu
const navToggle = document.querySelector('.nav-toggle');
const navMenu = document.querySelector('.nav-menu');

navToggle.addEventListener('click', () => {
  navToggle.classList.toggle('active');
  navMenu.classList.toggle('active');
});

// Close menu when link clicked
navMenu.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    navToggle.classList.remove('active');
    navMenu.classList.remove('active');
  });
});
```

---

## Smooth Animations

### Fade-In on Scroll

```css
.fade-in {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp 0.6s ease-out forwards;
}

.fade-in:nth-child(1) { animation-delay: 0.1s; }
.fade-in:nth-child(2) { animation-delay: 0.2s; }
.fade-in:nth-child(3) { animation-delay: 0.3s; }
.fade-in:nth-child(4) { animation-delay: 0.4s; }

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### Scroll-Triggered Animation (View Transition API)

```css
@supports (animation-timeline: view()) {
  .scroll-reveal {
    opacity: 0;
    animation: revealElement linear;
    animation-timeline: view();
    animation-range: entry 0% cover 30%;
  }

  @keyframes revealElement {
    to {
      opacity: 1;
    }
  }
}

/* Fallback for browsers without support */
@supports not (animation-timeline: view()) {
  .scroll-reveal {
    opacity: 1;
  }
}
```

### Smooth Hover Effects

```css
.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.link-hover {
  position: relative;
  text-decoration: none;
  color: var(--color-primary);
}

.link-hover::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background-color: var(--color-primary);
  transition: width 0.3s ease;
}

.link-hover:hover::after {
  width: 100%;
}
```

---

## Image Optimization

### Responsive Images

```html
<img
  srcset="
    image-small.jpg 480w,
    image-medium.jpg 768w,
    image-large.jpg 1200w,
    image-xl.jpg 1600w
  "
  src="image-medium.jpg"
  alt="Descriptive alt text"
  sizes="(max-width: 640px) 100vw,
         (max-width: 1024px) 75vw,
         1200px"
  loading="lazy"
  decoding="async"
/>
```

### Modern Image Format with Fallback

```html
<picture>
  <source srcset="image.webp" type="image/webp" />
  <source srcset="image.jpg" type="image/jpeg" />
  <img src="image.jpg" alt="Description" loading="lazy" />
</picture>
```

### Hero Image Optimization

```html
<section class="hero">
  <picture>
    <source
      media="(max-width: 768px)"
      srcset="hero-mobile.webp"
      type="image/webp"
    />
    <source
      media="(max-width: 768px)"
      srcset="hero-mobile.jpg"
      type="image/jpeg"
    />
    <source srcset="hero-desktop.webp" type="image/webp" />
    <img
      src="hero-desktop.jpg"
      alt="Hero image description"
      class="hero-image"
      decoding="async"
    />
  </picture>
</section>
```

```css
.hero-image {
  width: 100%;
  height: auto;
  display: block;
  max-height: 600px;
  object-fit: cover;
}

@media (max-width: 768px) {
  .hero-image {
    max-height: 400px;
  }
}
```

---

## Performance Utilities

### Critical CSS Pattern

```html
<!-- Inline critical CSS -->
<style>
  /* Hero section, above-the-fold content only */
  .hero {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
</style>

<!-- Defer non-critical CSS -->
<link rel="preload" href="/css/main.css" as="style" onload="this.onload=null;this.rel='stylesheet'" />
<noscript><link rel="stylesheet" href="/css/main.css" /></noscript>
```

### Font Loading Optimization

```css
/* Reduce layout shift with font-display */
@font-face {
  font-family: 'Playfair Display';
  src: url('/fonts/playfair-display.woff2') format('woff2');
  font-display: swap; /* Show fallback immediately, swap when loaded */
  font-weight: 700;
}

@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter.woff2') format('woff2');
  font-display: swap;
  font-weight: 400;
}
```

### Lazy Loading

```html
<!-- Lazy load images -->
<img
  src="placeholder.jpg"
  data-src="actual-image.jpg"
  alt="Description"
  loading="lazy"
/>

<!-- Lazy load iframes -->
<iframe
  src="https://www.youtube.com/embed/video-id"
  title="Video title"
  loading="lazy"
  allowfullscreen
></iframe>
```

---

## Accessibility Utilities

### Skip to Content Link

```html
<a href="#main" class="skip-link">Skip to main content</a>

<main id="main">
  <!-- Main content -->
</main>
```

```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-primary);
  color: white;
  padding: 0.5rem;
  text-decoration: none;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

### Focus-Visible Pattern

```css
/* Show focus only for keyboard navigation */
*:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* Hide focus for mouse users */
*:focus:not(:focus-visible) {
  outline: none;
}
```

### Screen Reader Only Text

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

```html
<button>
  <span aria-hidden="true">×</span>
  <span class="sr-only">Close menu</span>
</button>
```

---

## Container Queries (Modern Responsive)

### Future-Proof Responsive Components

```css
/* Define container context */
.card-container {
  container-type: inline-size;
  container-name: card;
}

/* Respond to container size, not viewport */
@container (min-width: 300px) {
  .card {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
}

@container (min-width: 500px) {
  .card {
    padding: 2rem;
  }
}

@container (max-width: 400px) {
  .card {
    padding: 1rem;
  }
}
```

---

## CSS Utilities for Quick Use

### Visibility Utilities

```css
.hidden { display: none !important; }
.sr-only { /* Already defined above */ }

.visible { visibility: visible; }
.invisible { visibility: hidden; }

.opacity-50 { opacity: 0.5; }
.opacity-0 { opacity: 0; }
```

### Text Utilities

```css
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-truncate { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.text-wrap { word-break: break-word; }

.no-underline { text-decoration: none; }
.underline { text-decoration: underline; }

.uppercase { text-transform: uppercase; }
.lowercase { text-transform: lowercase; }
.capitalize { text-transform: capitalize; }
```

### Spacing Utilities

```css
.mt-0 { margin-top: 0; }
.mt-1 { margin-top: 0.5rem; }
.mt-2 { margin-top: 1rem; }
.mt-3 { margin-top: 1.5rem; }
/* ...continue pattern */

.p-0 { padding: 0; }
.p-1 { padding: 0.5rem; }
.p-2 { padding: 1rem; }
/* ...continue pattern */
```

---

## Meta Tags Template

### HTML Head Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Character set -->
  <meta charset="UTF-8" />

  <!-- Viewport for responsive design -->
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <!-- Page title (max 60 chars) -->
  <title>Premium Site Title - Brand Name</title>

  <!-- SEO meta tags -->
  <meta
    name="description"
    content="Compelling description of the page (max 160 chars)"
  />
  <meta name="keywords" content="relevant, keywords, here" />

  <!-- Open Graph for social sharing -->
  <meta property="og:title" content="Page Title" />
  <meta property="og:description" content="Description" />
  <meta property="og:image" content="https://example.com/image.jpg" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://example.com" />

  <!-- Theme color -->
  <meta name="theme-color" content="#0066cc" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />

  <!-- Favicon -->
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="icon" type="image/png" href="/favicon-32x32.png" sizes="32x32" />

  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&display=swap"
    rel="stylesheet"
  />

  <!-- Critical CSS (inline) -->
  <style>
    /* Critical above-the-fold styles */
  </style>

  <!-- Main stylesheet (deferred) -->
  <link rel="preload" href="/css/main.css" as="style" onload="this.onload=null;this.rel='stylesheet'" />
  <noscript><link rel="stylesheet" href="/css/main.css" /></noscript>
</head>
<body>
  <!-- Content -->
  <script defer src="/js/main.js"></script>
</body>
</html>
```

---

These templates provide a solid foundation for building premium, responsive websites. Customize colors, spacing, and typography to match your specific design direction.

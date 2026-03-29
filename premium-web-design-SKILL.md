# Premium Web Design Skill

Create exceptional, production-ready website designs that are visually stunning, fully mobile-responsive, and professionally coded.

## Overview

This skill guides Claude to create premium websites that:
- Have a distinctive visual identity and bold aesthetic direction
- Avoid generic AI templates and cookie-cutter patterns
- Are fully responsive across all devices (mobile-first approach)
- Use sophisticated design techniques and premium components
- Maintain professional code quality and accessibility standards

## Core Principles

### 1. Mobile-First Design Philosophy

**Always start with mobile**, then enhance for larger screens:

- **Mobile-first approach**: Design the best experience for small screens (320px+), then progressively enhance
- **Breakpoint strategy**:
  - Mobile: < 768px
  - Tablet: 768px - 1024px
  - Desktop: > 1024px
- **Fluid typography**: Use CSS `clamp()` for responsive font sizing that scales smoothly
- **Flexible grids**: CSS Grid and Flexbox with proper wrapping and reflow
- **Touch-first interactions**: All interactive elements minimum 44px, appropriate spacing
- **Performance**: Optimized images, lazy loading, minimal JavaScript on mobile

**Example fluid typography:**
```css
/* Scales from 18px on mobile to 32px on desktop */
h1 {
  font-size: clamp(1.125rem, 5vw, 2rem);
}
```

**Example responsive grid:**
```css
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: clamp(1rem, 3vw, 2rem);
}
```

### 2. Premium Design Elements

#### Typography
- Use distinctive, premium font pairings (e.g., Playfair Display + Inter, Sora + Plus Jakarta Sans)
- Avoid generic choices like Inter alone, Roboto, or Arial
- Implement fluid typography with proper hierarchy
- Ensure excellent readability (line-height: 1.5-1.8, contrast ≥ 4.5:1)
- Include web-safe fallbacks

#### Color & Aesthetics
- Develop cohesive color systems using CSS custom properties
- Create sophisticated palettes with purpose (not generic gradients)
- Implement dark mode support where contextually appropriate
- Maintain WCAG AA contrast ratios minimum
- Use strategic color for visual hierarchy

**Example color system:**
```css
:root {
  --primary: #1a1a1a;
  --accent: #d4af37;
  --surface: #ffffff;
  --text: #2a2a2a;
  --text-secondary: #666666;
}

@media (prefers-color-scheme: dark) {
  :root {
    --primary: #ffffff;
    --surface: #0f0f0f;
    --text: #f5f5f5;
    --text-secondary: #999999;
  }
}
```

#### Layout & Composition
- Create creative, sometimes asymmetric layouts
- Use generous whitespace or intentional density with purpose
- Break grid conventions with overlapping elements and layers
- Create visual hierarchy through positioning and sizing
- Design for content readability across all screen sizes

#### Animations & Interactions
- Prioritize CSS animations over JavaScript
- Use purposeful micro-interactions (not decorative)
- Implement scroll-triggered effects responsibly
- Create delightful hover states
- Orchestrate page load with staggered reveals (opacity, transform)
- Keep animations smooth: use `transform` and `opacity` for 60fps performance

**Example scroll animation:**
```css
@supports (animation-timeline: view()) {
  .fade-in {
    opacity: 0;
    animation: fadeIn linear;
    animation-timeline: view();
    animation-range: entry 0% cover 30%;
  }
}

@keyframes fadeIn {
  to { opacity: 1; }
}
```

#### Visual Details
- Custom, meaningful backgrounds (gradients with purpose, patterns, textures)
- Subtle shadows and depth (use elevation system)
- Intentional border radius and shape variations
- Custom cursors only for special interactions
- Optional noise/grain overlays for sophistication

### 3. Technical Excellence

#### Semantic HTML5
- Use proper semantic tags: `<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<footer>`
- Include ARIA labels where needed
- Proper heading hierarchy (h1 > h2 > h3, not skipping levels)
- Alt text on all images (descriptive, not "image" or "photo")

#### Modern CSS
- CSS Grid for layouts, Flexbox for components
- CSS custom properties for theming and consistency
- Fluid units: clamp(), vw, em where appropriate
- Mobile-first media queries
- Proper specificity management

#### Performance
- Optimize images (WebP with JPEG fallback, lazy loading)
- Minimize CSS/JS bundles
- Load critical fonts first, use font-display: swap
- Defer non-critical JavaScript
- Target: LCP < 2.5s, FID < 100ms, CLS < 0.1

#### Accessibility (WCAG 2.1 AA)
- Keyboard navigation support
- Screen reader compatibility
- Color contrast: 4.5:1 for text, 3:1 for UI elements
- Skip navigation links
- Focus states visible
- Form labels properly associated

#### Cross-browser Compatibility
- Test on Chrome, Firefox, Safari, Edge
- Use fallbacks for newer CSS features
- Avoid deprecated properties
- Vendor prefixes only where needed

### 4. Mobile Responsiveness Verification Checklist

**Always verify these items before delivering:**

- [ ] All content readable on 320px width (iPhone SE)
- [ ] No horizontal scrolling on any device
- [ ] All buttons/interactive elements ≥ 44px tap target
- [ ] Images scale smoothly, no distortion
- [ ] Typography readable without zoom
- [ ] Touch-friendly spacing (minimum 8px padding around buttons)
- [ ] Navigation accessible on mobile (hamburger or clear structure)
- [ ] Forms properly sized for mobile input
- [ ] Breakpoints tested on actual devices (not just browser resize)
- [ ] Performance acceptable on 4G/LTE (simulated throttling)
- [ ] Landscape orientation works (if applicable)

**Testing approach:**
```
1. Chrome DevTools mobile emulation (iPhone 12, Pixel 5, iPad)
2. Real device testing (if possible)
3. Network throttling (4G slow)
4. Landscape + portrait orientations
5. Zoom in/out to 150%, 200%
```

### 5. Performance Optimization Guidelines

**Images:**
- Use WebP with JPEG/PNG fallbacks
- Lazy loading for below-fold images
- Responsive images with srcset
- Compress ruthlessly (TinyPNG, ImageOptim)

**CSS/JavaScript:**
- Critical CSS inlined, defer the rest
- Minimize and gzip
- Remove unused CSS with PurgeCSS if using Tailwind
- Defer non-critical JavaScript to end of body

**Fonts:**
- Maximum 3 font weights (e.g., 400, 600, 700)
- Use system fonts or pair web fonts strategically
- Font-display: swap to prevent FOIT
- Load only necessary language subsets

**Measurement:**
- Monitor with Google Lighthouse
- Target scores: Performance 85+, Accessibility 90+

### 6. Premium Design Patterns

#### Hero Section with Video
```html
<section class="hero">
  <video autoplay muted playsinline poster="image.jpg" class="hero-video">
    <source src="video.webm" type="video/webm">
    <source src="video.mp4" type="video/mp4">
  </video>
  <div class="hero-content">
    <h1>Compelling Headline</h1>
    <p>Supporting text that creates context</p>
  </div>
</section>
```

```css
.hero {
  position: relative;
  height: clamp(300px, 100vh, 800px);
  overflow: hidden;
}

.hero-video {
  position: absolute;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: -1;
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: white;
  text-align: center;
  padding: 2rem;
}
```

#### Staggered Reveal Animation
```css
.reveal-item {
  opacity: 0;
  transform: translateY(20px);
  animation: revealUp 0.6s ease-out forwards;
}

.reveal-item:nth-child(1) { animation-delay: 0.1s; }
.reveal-item:nth-child(2) { animation-delay: 0.2s; }
.reveal-item:nth-child(3) { animation-delay: 0.3s; }

@keyframes revealUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

#### Responsive Image Gallery
```html
<div class="gallery">
  <img srcset="small.jpg 480w, medium.jpg 768w, large.jpg 1200w"
       src="medium.jpg" alt="Description" loading="lazy">
</div>
```

```css
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.gallery img {
  width: 100%;
  height: auto;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border-radius: 8px;
}
```

#### Sophisticated Typography Scale
```css
:root {
  --text-base: clamp(0.875rem, 2vw, 1rem);
  --text-sm: clamp(0.75rem, 1.5vw, 0.875rem);
  --text-lg: clamp(1.125rem, 3vw, 1.5rem);
  --text-xl: clamp(1.5rem, 4vw, 2rem);
  --text-2xl: clamp(2rem, 5vw, 3rem);
}

body { font-size: var(--text-base); }
h3 { font-size: var(--text-lg); }
h2 { font-size: var(--text-xl); }
h1 { font-size: var(--text-2xl); }
```

### 7. Deliverables Checklist

For each website creation, include:

- ✓ Complete HTML structure (semantic, accessible)
- ✓ Comprehensive CSS with all breakpoints tested
- ✓ Minimal JavaScript (only where truly necessary)
- ✓ Clear comments explaining key design decisions
- ✓ Mobile responsiveness verification checklist (completed)
- ✓ Performance optimization notes
- ✓ Accessibility audit notes (color contrast, keyboard nav, etc.)
- ✓ Font and color palette documentation
- ✓ Responsive typography explanation

## Design Decision Framework

When creating a new website design:

1. **Understand the context**: Brand, audience, purpose, tone
2. **Choose aesthetic direction**: Style, inspiration, unique angles
3. **Plan mobile-first**: Sketch layouts starting at 320px
4. **Define breakpoints**: Only add breakpoints where content breaks
5. **Select typography**: Find distinctive font pairing (use Google Fonts, Typekit)
6. **Build color system**: 3-5 colors maximum, use CSS variables
7. **Create layout**: Design with Grid and Flexbox from mobile up
8. **Add interactions**: Purposeful animations, meaningful micro-interactions
9. **Optimize assets**: Images, fonts, CSS/JS
10. **Test thoroughly**: All devices, orientations, network speeds

## Avoiding Generic AI Design

**Don't do:**
- Use only default sans-serif fonts
- Add unnecessary gradients or glass morphism
- Create uniform grid layouts without variation
- Implement animations "just because"
- Use stock photos without customization
- Copy common landing page structures

**Instead:**
- Choose distinctive typography pairings
- Use color and space intentionally
- Create asymmetric, interesting layouts
- Only animate what serves a purpose
- Customize images or create original graphics
- Break conventions while maintaining usability

## Tools & Resources Recommendations

- **Typography**: Google Fonts, Typekit, Fonts.com
- **Color**: Coolors.co, Adobe Color, Chroma.js
- **Icons**: Feather Icons, System UIcons, custom SVGs
- **Images**: Unsplash, Pexels, Pixabay
- **Optimization**: TinyPNG, ImageOptim, Squoosh
- **Testing**: Chrome DevTools, BrowserStack, Responsively
- **Performance**: Google Lighthouse, WebPageTest

## Success Criteria

A premium website design is successful when it:
- ✓ Works flawlessly on 320px - 2560px widths
- ✓ Has a unique, memorable visual identity
- ✓ Uses sophisticated design techniques appropriately
- ✓ Is technically excellent and accessible
- ✓ Avoids all generic AI design patterns
- ✓ Demonstrates professional-level quality
- ✓ Loads quickly and performs smoothly
- ✓ Is a pleasure to use on any device

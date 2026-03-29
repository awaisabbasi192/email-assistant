# Premium Web Design Skill - Evaluation Scenarios

## Evaluation Framework

These evals test the skill's ability to produce premium, mobile-responsive websites that are visually unique and technically excellent.

### Evaluation Criteria Matrix

| Criteria | Weight | Pass Condition |
|----------|--------|---|
| Mobile Responsiveness | 30% | Works perfectly on 320px-2560px, no horizontal scroll, touch-friendly |
| Visual Uniqueness | 25% | Distinctive design, premium aesthetics, avoids generic patterns |
| Code Quality | 25% | Semantic HTML, clean CSS, proper accessibility, organized structure |
| Performance | 20% | Fast load times, optimized assets, smooth animations, LCP < 2.5s |

---

## Evaluation Scenarios

### EVAL 1: Luxury Watch Brand Landing Page

**Difficulty**: Medium
**Category**: E-commerce, Premium Brand
**Time Limit**: 15 minutes

#### Prompt
```
Create a premium landing page for "Chronos Luxury Watches" - an exclusive
timepiece manufacturer. The brand targets affluent collectors aged 35-65 who
appreciate craftsmanship and heritage.

Requirements:
- Hero section showcasing a featured watch with high-quality imagery
- Brand story/heritage section with elegant typography
- Product showcase with 3-4 signature watches in a grid
- Testimonials from notable collectors
- Newsletter signup
- Contact/location information

Design approach:
- Use sophisticated, distinctive typography (not generic sans-serif)
- Create an elegant color palette (consider gold/cream/charcoal)
- Implement smooth scroll animations
- Ensure luxury feel while maintaining readability
- MUST be fully responsive from mobile to desktop
- Include detailed comments on design decisions

Testing checklist:
- Works perfectly on iPhone SE (320px)
- Touch-friendly buttons (≥44px)
- Readable on all screen sizes without zoom
- High-quality product images scale smoothly
- Animations are smooth (60fps) on mobile
```

#### Evaluation Criteria

**Mobile Responsiveness (35%)**
- [ ] No horizontal scrolling at any viewport width
- [ ] All buttons are minimum 44px with proper spacing
- [ ] Images scale smoothly from mobile to desktop
- [ ] Navigation accessible on mobile (visible or hamburger menu)
- [ ] Text readable without zoom on smallest devices
- [ ] Product grid adapts properly (1 column mobile → 3+ desktop)
- [ ] Hero section height appropriate for mobile (not 100vh)

**Visual Uniqueness (30%)**
- [ ] Typography pairing is distinctive (not generic)
- [ ] Color palette feels premium and cohesive
- [ ] Layout has interesting asymmetry or creative elements
- [ ] Product showcase has visual interest beyond a plain grid
- [ ] Avoids common "luxury AI design" clichés
- [ ] Professional craftsmanship evident in details

**Code Quality (25%)**
- [ ] Semantic HTML structure
- [ ] CSS organized with clear breakpoints
- [ ] CSS custom properties used for colors/spacing
- [ ] Mobile-first media queries
- [ ] Proper alt text on all images
- [ ] Good comments explaining design decisions

**Performance (10%)**
- [ ] Images optimized (WebP with fallback)
- [ ] Smooth animations using CSS transforms
- [ ] No layout shifts during load

---

### EVAL 2: Photography Portfolio Website

**Difficulty**: High
**Category**: Portfolio, Creative
**Time Limit**: 20 minutes

#### Prompt
```
Design a professional portfolio website for "Luna Chen" - a fashion and
portrait photographer with a distinctive, moody aesthetic. Target audience:
potential clients, collaborators, and industry professionals.

Requirements:
- Sophisticated homepage with featured work
- About section with photographer bio and philosophy
- Portfolio gallery (12+ photos) with creative layout
- Services/pricing section
- Client testimonials with photos
- Contact form
- Blog/insights section (3 posts minimum)

Design approach:
- Create a visual identity that matches the photographer's moody aesthetic
- Use unconventional layout (not typical portfolio grids)
- Implement smooth, purposeful animations
- Typography should be editorial/distinctive
- Color palette should enhance the photographic work
- CRITICAL: Fully responsive and mobile-optimized
- Include accessibility considerations

Testing:
- All interactive elements work on touch devices
- Gallery loads efficiently on mobile
- Images display beautifully at all sizes
- Portfolio grid adapts intelligently by breakpoint
- Contact form accessible and functional
- Landscape/portrait orientation both work
```

#### Evaluation Criteria

**Mobile Responsiveness (40%)**
- [ ] Gallery layout changes appropriately (masonry → single column on mobile)
- [ ] Images load efficiently on mobile networks
- [ ] All interactive elements are touch-accessible
- [ ] Navigation clear on mobile (not hamburger buried)
- [ ] Contact form fields sized for mobile input
- [ ] Blog grid adapts to single/double column layout
- [ ] Testimonial cards readable on mobile
- [ ] Tested on actual mobile device or multiple emulations

**Visual Uniqueness (35%)**
- [ ] Layout avoids standard portfolio templates
- [ ] Photography is showcased beautifully (color, spacing, contrast)
- [ ] Typography supports the aesthetic (not generic)
- [ ] Creative use of whitespace or negative space
- [ ] Hover/animation states are delightful
- [ ] Color palette enhances rather than competes with photos
- [ ] Navigation design is distinctive

**Code Quality (20%)**
- [ ] Semantic HTML for gallery structure
- [ ] Lazy loading on images
- [ ] Accessible form with proper labels
- [ ] CSS Grid or Flexbox used appropriately
- [ ] Mobile-first responsive design
- [ ] Comments explaining complex layout decisions

**Performance (5%)**
- [ ] Images optimized for web
- [ ] Page loads quickly on simulated slow network
- [ ] Animations smooth and performant

---

### EVAL 3: SaaS Product Landing Page

**Difficulty**: Medium
**Category**: B2B, Product
**Time Limit**: 15 minutes

#### Prompt
```
Create a landing page for "FlowSync" - a project management SaaS tool that
breaks conventional patterns. It emphasizes team collaboration, AI-powered
insights, and beautiful user experience.

Target audience: Remote-first tech teams and creative agencies (25-45 years old)

Requirements:
- Bold hero section with clear value proposition
- Feature showcase (4-5 key features) with innovative presentation
- Pricing tiers with clear differentiation
- ROI/results section with metrics
- Integration/partnership logos
- CTA buttons throughout
- FAQ section
- Footer with links

Design approach:
- Break away from typical SaaS landing page patterns
- Use unexpected layout or interaction patterns
- Bold typography and color choices
- Demonstrate technical sophistication without complexity
- Emphasize the "beautiful" aspect of the product
- MUST be fully responsive

Responsiveness focus:
- Test at 320px (mobile), 768px (tablet), 1440px (desktop)
- Ensure feature showcase adapts (2-column → 1-column)
- CTA buttons always accessible
- Pricing table readable on mobile
- All interactions work on touch devices
```

#### Evaluation Criteria

**Mobile Responsiveness (35%)**
- [ ] Hero section works at 320px viewport
- [ ] Feature showcase adapts to single column
- [ ] Pricing table is readable and scrollable on mobile (or collapses)
- [ ] CTA buttons are 44px+ minimum
- [ ] No horizontal scrolling at any viewport
- [ ] Spacing/padding appropriate for mobile
- [ ] FAQ accordions work smoothly on touch
- [ ] Footer navigation accessible on mobile

**Visual Uniqueness (30%)**
- [ ] Layout breaks typical SaaS patterns
- [ ] Typography choices are distinctive
- [ ] Color palette feels intentional and premium
- [ ] Feature showcase has creative presentation (not just icons + text)
- [ ] Pricing section has visual differentiation
- [ ] Animations serve a purpose (not decorative)
- [ ] Overall design feels modern but not generic

**Code Quality (25%)**
- [ ] Semantic structure (proper headings, sections)
- [ ] CSS organized with mobile-first approach
- [ ] Color system using CSS variables
- [ ] Proper focus states for keyboard navigation
- [ ] Forms accessible with labels
- [ ] Comments on non-obvious design decisions

**Performance (10%)**
- [ ] Page loads quickly
- [ ] Animations smooth on mobile devices
- [ ] Images optimized

---

### EVAL 4: Restaurant/Food Brand Website

**Difficulty**: Medium
**Category**: Hospitality, Local Business
**Time Limit**: 15 minutes

#### Prompt
```
Design a website for "Terra" - a contemporary farm-to-table restaurant focused
on seasonal cuisine and sustainable practices. Located in a trendy neighborhood,
they attract both fine-dining customers and casual visitors.

Requirements:
- Stunning homepage with hero image/video of food
- About the restaurant and chef philosophy
- Menu sections with description (appetizers, mains, desserts, wine)
- Reservation system integration (mockup or form)
- Photo gallery of dishes and restaurant space
- Events/private dining section
- Location, hours, contact
- Newsletter signup

Design approach:
- Celebrate high-quality food photography
- Use natural, earthy color palette
- Create a warm, inviting atmosphere in design
- Balance sophistication with accessibility
- Typography should feel both modern and grounded
- CRITICAL: Fully mobile-responsive for all users
- Include seasonal design flexibility

Mobile requirements:
- Menu easily readable and scrollable
- Reservation form works smoothly on mobile
- Photos/gallery optimized for all devices
- Location map accessible
- Call-to-action (Reserve/Order) prominent on mobile
- Works in both portrait and landscape
- Touch-friendly all interactive elements
```

#### Evaluation Criteria

**Mobile Responsiveness (35%)**
- [ ] Menu displays beautifully on mobile (not overwhelming)
- [ ] Hero image/video doesn't slow mobile load
- [ ] Gallery displays as single column (or 2-column max)
- [ ] Reservation form optimized for mobile input
- [ ] Touch targets all ≥44px
- [ ] Map/location accessible and functional
- [ ] Text readable without zoom
- [ ] Spacing appropriate for thumb navigation

**Visual Uniqueness (30%)**
- [ ] Food photography is the hero (well-displayed)
- [ ] Color palette reflects brand (earthy, warm)
- [ ] Typography feels sophisticated but approachable
- [ ] Layout isn't generic restaurant template
- [ ] Atmosphere/mood comes through in design
- [ ] Menu presentation is creative
- [ ] Avoids overused restaurant design patterns

**Code Quality (25%)**
- [ ] Semantic menu structure
- [ ] Form properly labeled and accessible
- [ ] Image optimization for food photos
- [ ] Map integration accessible
- [ ] CSS organized with clear breakpoints
- [ ] Mobile-first approach evident
- [ ] Comments on design considerations

**Performance (10%)**
- [ ] Hero image/video optimized for mobile
- [ ] Gallery loads efficiently
- [ ] Smooth animations or transitions
- [ ] Fast initial page load

---

### EVAL 5: Personal Brand/Resume Website

**Difficulty**: Medium
**Category**: Portfolio, Personal Brand
**Time Limit**: 12 minutes

#### Prompt
```
Create a personal portfolio website for "Alex Rivera" - a senior product
designer with 8 years of experience. They want to showcase their work,
philosophy, and personality to potential employers and collaborators.

Requirements:
- Compelling homepage with personal brand statement
- Work/project showcase (4-5 case studies)
- About section with background and approach
- Skills and tools section
- Testimonials/recommendations
- Contact section
- Optional: Blog or writing samples

Design approach:
- Reflect the designer's creative, thoughtful approach
- Showcase work in a meaningful way (not just thumbnails)
- Personal touch without being too casual
- Balance between showing off and maintaining professionalism
- Typography and color should reflect personal brand
- MUST be fully responsive and mobile-friendly
- Should inspire confidence in the designer's abilities

Responsiveness:
- Works on all devices
- Case studies readable on mobile (might need adaptation)
- Portfolio grid adapts intelligently
- Contact form accessible
- All navigation works on touch
- Loads quickly even on slower networks
```

#### Evaluation Criteria

**Mobile Responsiveness (35%)**
- [ ] Case studies readable on mobile (might be vertical/stacked)
- [ ] Portfolio grid adapts (1-2 columns on mobile)
- [ ] Images scale without quality loss
- [ ] All links and buttons touch-accessible
- [ ] Contact form optimized for mobile
- [ ] Navigation clear and usable on mobile
- [ ] Testimonials readable on small screens
- [ ] No horizontal scroll at any viewport

**Visual Uniqueness (30%)**
- [ ] Design reflects designer's personal brand
- [ ] Layouts interesting and custom (not template)
- [ ] Typography pairings distinctive
- [ ] Color palette intentional and cohesive
- [ ] Work is presented meaningfully (not generic grid)
- [ ] Personality comes through without being unprofessional
- [ ] Demonstrates design skill through the design itself

**Code Quality (25%)**
- [ ] Well-structured, semantic HTML
- [ ] Clean, organized CSS with clear breakpoints
- [ ] Mobile-first responsive design
- [ ] Proper heading hierarchy
- [ ] Forms accessible with labels
- [ ] Good code comments
- [ ] Accessibility considered (contrast, keyboard nav)

**Performance (10%)**
- [ ] Portfolio images optimized
- [ ] Page loads quickly
- [ ] Animations smooth and purposeful

---

## Evaluation Scoring

### How to Score Each Eval

**For each evaluation:**

1. **Mobile Responsiveness (0-40 points)**
   - 0 points: Fails on mobile (not functional, horizontal scroll)
   - 10 points: Works on some devices, some issues
   - 20 points: Works on all devices with minor issues
   - 30 points: Works very well, minor edge cases
   - 40 points: Perfect on all devices, professional quality

2. **Visual Uniqueness (0-35 points)**
   - 0 points: Generic, template-like design
   - 10 points: Some effort but still generic
   - 17 points: Above average, some unique elements
   - 25 points: Distinctive, professional, mostly unique
   - 35 points: Exceptional, memorable, highly original

3. **Code Quality (0-25 points)**
   - 0 points: Poor code structure, accessibility issues
   - 8 points: Functional but messy code
   - 15 points: Good structure, minor issues
   - 20 points: Well-organized, semantic, accessible
   - 25 points: Excellent code, best practices throughout

4. **Performance (0-10 points)**
   - 0 points: Slow load, poor optimization
   - 3 points: Acceptable but could improve
   - 7 points: Good optimization, smooth performance
   - 10 points: Excellent performance across all metrics

**Pass Threshold**: 85/110 points (77%)

---

## Running the Evaluations

### Quick Test Protocol

For each eval:

1. **Set the scene**: Read the full prompt to understand requirements
2. **Create the design**: Use the premium-web-design skill
3. **Manual testing**:
   - Test on Chrome DevTools (320px, 768px, 1440px)
   - Test on mobile device if available
   - Check performance (Lighthouse)
   - Verify accessibility (axe DevTools, WAVE)
4. **Score objectively**: Use the criteria matrix
5. **Document issues**: Note any mobile responsiveness failures, generic design elements, code problems, or performance issues

### Performance Testing Checklist

- [ ] Lighthouse Performance score ≥ 85
- [ ] LCP (Largest Contentful Paint) < 2.5s
- [ ] CLS (Cumulative Layout Shift) < 0.1
- [ ] Smooth animations (60fps)
- [ ] Fast on 4G throttling (Chrome DevTools)

### Accessibility Testing Checklist

- [ ] WAVE browser extension shows no errors
- [ ] Axe DevTools finds no critical issues
- [ ] Keyboard navigation works throughout
- [ ] Color contrast ≥ 4.5:1 for text
- [ ] All images have descriptive alt text
- [ ] Form fields properly labeled

### Mobile Testing Checklist (CRITICAL)

- [ ] iPhone SE (375px): Works perfectly
- [ ] iPad (768px): Works perfectly
- [ ] Landscape orientation: Works perfectly
- [ ] Touch testing: All buttons responsive
- [ ] Network: Acceptable on 4G throttle
- [ ] No horizontal scrolling at any width
- [ ] Readable without zoom on smallest screens

---

## Success Metrics Summary

A website passes the premium-web-design skill evaluation when it:

✓ **Mobile-First Excellence**
- Perfect responsiveness from 320px to 2560px
- All interactive elements touch-friendly
- No layout shifts or horizontal scrolling
- Optimized media for mobile networks

✓ **Visual Distinction**
- Memorable, unique design identity
- Sophisticated typography choices
- Intentional, cohesive color system
- Avoids generic AI design patterns
- Professional-level execution

✓ **Technical Mastery**
- Semantic, accessible HTML structure
- Well-organized, maintainable CSS
- Performance-optimized assets
- Smooth, purposeful animations
- 90+ accessibility score

✓ **Professional Quality**
- Rivaling agency-level work
- Attention to detail evident
- Consistent brand execution
- Thoughtful user experience
- Production-ready code

/**
 * Shannon Insight Marketing Site - main.js
 * Minimal interactivity: scroll animations, nav, mobile menu
 */

(function () {
  'use strict';

  // --- Scroll-triggered animations via IntersectionObserver ---
  function initScrollAnimations() {
    const observerOptions = {
      threshold: 0.15,
      rootMargin: '0px 0px -40px 0px',
    };

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          // Once visible, stop observing (one-shot animation)
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    // Observe all animated elements
    var selectors = [
      '.fade-in',
      '.fade-in-stagger',
      '.slide-in-left',
      '.slide-in-right',
      '.scale-in',
      '.terminal',
      '.pipeline__flow',
    ];

    selectors.forEach(function (selector) {
      document.querySelectorAll(selector).forEach(function (el) {
        observer.observe(el);
      });
    });
  }

  // --- Sticky nav with background on scroll ---
  function initNavScroll() {
    var nav = document.querySelector('.nav');
    if (!nav) return;

    var scrollThreshold = 40;

    function updateNav() {
      if (window.scrollY > scrollThreshold) {
        nav.classList.add('nav--scrolled');
      } else {
        nav.classList.remove('nav--scrolled');
      }
    }

    window.addEventListener('scroll', updateNav, { passive: true });
    updateNav();
  }

  // --- Mobile menu toggle ---
  function initMobileMenu() {
    var toggle = document.querySelector('.nav__mobile-toggle');
    var links = document.querySelector('.nav__links');
    if (!toggle || !links) return;

    toggle.addEventListener('click', function () {
      var isOpen = links.classList.toggle('active');
      toggle.setAttribute('aria-expanded', isOpen);

      // Update icon
      if (isOpen) {
        toggle.innerHTML =
          '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
      } else {
        toggle.innerHTML =
          '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';
      }
    });

    // Close menu when a link is clicked
    links.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        links.classList.remove('active');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.innerHTML =
          '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';
      });
    });
  }

  // --- Smooth scroll for anchor links ---
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
      anchor.addEventListener('click', function (e) {
        var href = this.getAttribute('href');
        if (href === '#') return;

        var target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          var navHeight = document.querySelector('.nav')
            ? document.querySelector('.nav').offsetHeight
            : 0;
          var y =
            target.getBoundingClientRect().top + window.pageYOffset - navHeight - 20;
          window.scrollTo({ top: y, behavior: 'smooth' });
        }
      });
    });
  }

  // --- Copy install command on click ---
  function initCopyCommand() {
    document.querySelectorAll('[data-copy]').forEach(function (el) {
      el.style.cursor = 'pointer';
      el.title = 'Click to copy';

      el.addEventListener('click', function () {
        var text = this.getAttribute('data-copy');
        if (navigator.clipboard) {
          navigator.clipboard.writeText(text).then(function () {
            el.classList.add('copied');
            var original = el.textContent;
            el.setAttribute('data-tooltip', 'Copied!');
            setTimeout(function () {
              el.classList.remove('copied');
            }, 2000);
          });
        }
      });
    });
  }

  // --- Active nav link highlighting ---
  function initActiveNav() {
    var sections = document.querySelectorAll('section[id]');
    if (!sections.length) return;

    function updateActive() {
      var scrollPos = window.scrollY + 120;

      sections.forEach(function (section) {
        var top = section.offsetTop;
        var height = section.offsetHeight;
        var id = section.getAttribute('id');

        var link = document.querySelector('.nav__links a[href="#' + id + '"]');
        if (link) {
          if (scrollPos >= top && scrollPos < top + height) {
            link.style.color = '#e2e8f0';
          } else {
            link.style.color = '';
          }
        }
      });
    }

    window.addEventListener('scroll', updateActive, { passive: true });
  }

  // --- Initialize everything on DOM ready ---
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    initScrollAnimations();
    initNavScroll();
    initMobileMenu();
    initSmoothScroll();
    initCopyCommand();
    initActiveNav();
  }
})();

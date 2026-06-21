/* ============================================================
   Rota com Família — Interações
   ============================================================ */
(() => {
  'use strict';

  /* ---------- Scroll progress bar ---------- */
  const progress = document.getElementById('scroll-progress');
  const nav = document.getElementById('nav');

  const onScroll = () => {
    const h = document.documentElement;
    const scrolled = h.scrollTop;
    const height = h.scrollHeight - h.clientHeight;
    const pct = height > 0 ? (scrolled / height) * 100 : 0;
    if (progress) progress.style.width = pct + '%';

    if (nav) nav.classList.toggle('scrolled', scrolled > 24);

    // Hero parallax + zoom-out
    const heroBg = document.getElementById('hero-bg');
    if (heroBg && scrolled < window.innerHeight) {
      const t = scrolled * 0.35;
      const scale = 1.1 - Math.min(scrolled / window.innerHeight, 1) * 0.05;
      heroBg.style.transform = `translate3d(0, ${t}px, 0) scale(${scale})`;
    }
  };

  document.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- Mobile menu ---------- */
  const menuToggle = document.getElementById('menu-toggle');
  const mobileMenu = document.getElementById('mobile-menu');
  if (menuToggle && mobileMenu) {
    menuToggle.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
    });
    // Close on link tap
    mobileMenu.querySelectorAll('a').forEach((a) =>
      a.addEventListener('click', () => mobileMenu.classList.add('hidden'))
    );
  }

  /* ---------- Reveal on scroll (IntersectionObserver) ---------- */
  const revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('in');
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add('in'));
  }

  /* ---------- Animated counters ---------- */
  const counters = document.querySelectorAll('[data-counter]');
  const countObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const target = parseInt(el.dataset.counter, 10);
        const duration = 1600;
        const start = performance.now();
        const step = (now) => {
          const elapsed = now - start;
          const p = Math.min(elapsed / duration, 1);
          // easeOutCubic
          const eased = 1 - Math.pow(1 - p, 3);
          const val = Math.floor(target * eased);
          el.textContent = val.toLocaleString('pt-BR');
          if (p < 1) requestAnimationFrame(step);
          else el.textContent = target.toLocaleString('pt-BR');
        };
        requestAnimationFrame(step);
        countObserver.unobserve(el);
      });
    },
    { threshold: 0.5 }
  );
  counters.forEach((c) => countObserver.observe(c));

  /* ---------- Category chip toggle ---------- */
  document.querySelectorAll('#blog .chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('#blog .chip').forEach((c) => c.classList.remove('chip-active'));
      chip.classList.add('chip-active');
    });
  });

  /* ---------- Generic modal helpers ---------- */
  const openModal = (modalEl) => {
    if (!modalEl) return;
    modalEl.classList.remove('hidden');
    modalEl.classList.add('open');
    document.body.style.overflow = 'hidden';
  };
  const closeModal = (modalEl) => {
    if (!modalEl) return;
    modalEl.classList.add('hidden');
    modalEl.classList.remove('open');
    document.body.style.overflow = '';
  };

  /* ---------- Modal: apps sob demanda ---------- */
  const appsModal = document.getElementById('apps-modal');
  const openAppsBtn = document.getElementById('open-apps-modal');
  if (appsModal && openAppsBtn) {
    openAppsBtn.addEventListener('click', () => openModal(appsModal));
    appsModal.querySelectorAll('[data-close]').forEach((el) =>
      el.addEventListener('click', () => closeModal(appsModal))
    );
  }

  /* ---------- Modal: artigo (em breve) ---------- */
  const articleModal = document.getElementById('article-modal');
  if (articleModal) {
    const imgEl = document.getElementById('article-modal-img');
    const tagEl = document.getElementById('article-modal-tag');
    const titleEl = document.getElementById('article-modal-title');
    const excerptEl = document.getElementById('article-modal-excerpt');

    document.querySelectorAll('#blog .post-card').forEach((card) => {
      card.style.cursor = 'pointer';
      card.addEventListener('click', () => {
        const img = card.querySelector('.post-media img');
        const tag = card.querySelector('.post-tag');
        const title = card.querySelector('h3');
        const excerpt = card.querySelector('.post-body p');
        if (imgEl && img) { imgEl.src = img.src; imgEl.alt = img.alt; }
        if (tagEl && tag) tagEl.textContent = tag.textContent;
        if (titleEl && title) titleEl.textContent = title.textContent;
        if (excerptEl && excerpt) excerptEl.textContent = excerpt.textContent;
        openModal(articleModal);
      });
    });

    articleModal.querySelectorAll('[data-close]').forEach((el) =>
      el.addEventListener('click', () => closeModal(articleModal))
    );
  }

  /* ---------- ESC closes any open modal ---------- */
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    document.querySelectorAll('.fixed.z-\\[80\\]').forEach((m) => {
      if (!m.classList.contains('hidden')) closeModal(m);
    });
  });

  /* ---------- Smooth-scroll for anchor links (offset for fixed nav) ---------- */
  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (!href || href === '#') return;
      const target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      const offset = 70;
      const top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: 'smooth' });
    });
  });

  /* ---------- Newsletter form (placeholder submit) ---------- */
  const newsletterForm = document.querySelector('#newsletter form');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = newsletterForm.querySelector('button[type="submit"]');
      const original = btn.textContent;
      btn.textContent = '✓ Cheque seu email!';
      btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
      newsletterForm.reset();
      setTimeout(() => {
        btn.textContent = original;
        btn.style.background = '';
      }, 3200);
    });
  }
})();

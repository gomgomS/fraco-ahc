document.addEventListener("DOMContentLoaded", () => {
    const slides = document.querySelectorAll(".hero-slide");
    const dots = document.querySelectorAll(".hero-dot");
    const pauseBtn = document.querySelector(".hero-pause");
    const header = document.querySelector(".site-header");
    let current = 0;
    let paused = false;
    let timer = null;

    function paintHeader() {
        if (!header) return;
        const hero = document.querySelector(".hero, .page-hero");
        const pastHero = window.scrollY > Math.max((hero?.offsetHeight || 280) - 90, 40);
        header.classList.toggle("is-solid", pastHero);
        if (pastHero) {
            header.classList.remove("is-light");
            return;
        }
        const active = slides[current];
        if (active) {
            header.classList.toggle("is-light", active.dataset.theme === "light");
        }
    }

    window.addEventListener("scroll", paintHeader, { passive: true });

    function goTo(index) {
        if (!slides.length || index === current) return;
        slides[current].classList.remove("active");
        if (dots[current]) dots[current].classList.remove("active");
        current = index;
        slides[current].classList.add("active");
        if (dots[current]) dots[current].classList.add("active");
        paintHeader();
    }

    function next() {
        if (!slides.length) return;
        goTo((current + 1) % slides.length);
    }

    function start() {
        stop();
        if (slides.length < 2) return;
        timer = setInterval(next, 5000);
    }

    function stop() {
        if (timer) clearInterval(timer);
        timer = null;
    }

    dots.forEach((dot, i) => {
        dot.addEventListener("click", () => {
            goTo(i);
            if (!paused) start();
        });
    });

    if (pauseBtn) {
        pauseBtn.addEventListener("click", () => {
            paused = !paused;
            pauseBtn.setAttribute("aria-label", paused ? "Play" : "Pause");
            pauseBtn.innerHTML = paused
                ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>'
                : '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M7 5h3v14H7zm7 0h3v14h-3z"/></svg>';
            if (paused) stop();
            else start();
        });
    }

    paintHeader();
    start();

    const overlay = document.getElementById("menuOverlay");
    const drawer = document.getElementById("menuDrawer");
    const searchPanel = document.getElementById("searchPanel");

    function openMenu() {
        overlay.classList.add("open");
        drawer.classList.add("open");
        drawer.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
    }

    function closeMenu() {
        overlay.classList.remove("open");
        drawer.classList.remove("open");
        drawer.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
    }

    document.querySelectorAll(".js-menu-open").forEach((el) => el.addEventListener("click", openMenu));
    document.querySelectorAll(".js-menu-close").forEach((el) => el.addEventListener("click", closeMenu));
    if (overlay) overlay.addEventListener("click", closeMenu);

    document.querySelectorAll(".js-search-open").forEach((el) => {
        el.addEventListener("click", () => searchPanel.classList.add("open"));
    });
    document.querySelectorAll(".js-search-close").forEach((el) => {
        el.addEventListener("click", () => searchPanel.classList.remove("open"));
    });
});

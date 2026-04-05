// --- 1. SHARED PRICE LOGIC (Shared by Home & Listings) ---
const priceRanges = {
    "For Rent": [
        { label: "Any Price...", value: "" },
        { label: "Under 15,000", value: "0-15000" },
        { label: "15,000 - 35,000", value: "15000-35000" },
        { label: "35,000 - 70,000", value: "35000-70000" },
        { label: "Above 70,000", value: "70000-999999" }
    ],
    "For Sale": [
        { label: "Any Price...", value: "" },
        { label: "Under 2 Million", value: "0-2000000" },
        { label: "2M - 7 Million", value: "2000000-7000000" },
        { label: "7M - 15 Million", value: "7000000-15000000" },
        { label: "Above 15 Million", value: "15000000-999999999" }
    ]
};

// --- 2. HOME PAGE SEARCH LOGIC (PRESERVED) ---
window.setHomeStatus = function(status) {
    const statusInput = document.getElementById('search-status');
    if (statusInput) statusInput.value = status;

    const buyTab = document.getElementById('tab-buy');
    const rentTab = document.getElementById('tab-rent');
    const priceSelect = document.getElementById('home-price-select');

    const activeClass = 'status-tab px-8 py-3 bg-[#7cbd1e] text-white font-bold transition-all cursor-pointer';
    const inactiveClass = 'status-tab px-8 py-3 bg-white text-gray-700 font-bold transition-all cursor-pointer';

    if (buyTab) buyTab.className = (status === 'For Sale') ? activeClass : inactiveClass;
    if (rentTab) rentTab.className = (status === 'For Rent') ? activeClass : inactiveClass;

    if (priceSelect) {
        priceSelect.innerHTML = ''; 
        priceRanges[status].forEach(range => {
            const opt = document.createElement('option');
            opt.value = range.value;
            opt.textContent = range.label;
            priceSelect.appendChild(opt);
        });
    }
};

// --- 3. NEW LISTINGS PAGE FILTER LOGIC ---
window.updateListingsPriceRanges = function() {
    const statusSelect = document.getElementById('hidden-status');
    const priceSelect = document.getElementById('price-select');
    if (!statusSelect || !priceSelect) return;

    const status = statusSelect.value;
    const currentSelectedPrice = priceSelect.getAttribute('data-current-price');
    
    // Clear and rebuild using the objects in priceRanges
    priceSelect.innerHTML = ''; 
    if (priceRanges[status]) {
        priceRanges[status].forEach(range => {
            const opt = document.createElement('option');
            opt.value = range.value;
            opt.textContent = range.label;
            opt.className = "text-gray-600 font-medium";
            if (range.value === currentSelectedPrice) opt.selected = true;
            priceSelect.appendChild(opt);
        });
    }
};

window.setListingsStatus = function(status) {
    const hiddenInput = document.getElementById('hidden-status');
    const btnSale = document.getElementById('btn-sale');
    const btnRent = document.getElementById('btn-rent');

    if (!hiddenInput || !btnSale || !btnRent) return;
    hiddenInput.value = status;

    if (status === 'For Sale') {
        btnSale.className = "flex-1 py-4 text-[10px] font-black uppercase tracking-widest bg-black text-white transition-all";
        btnRent.className = "flex-1 py-4 text-[10px] font-black uppercase tracking-widest text-gray-500 hover:text-black transition-all";
    } else {
        btnRent.className = "flex-1 py-4 text-[10px] font-black uppercase tracking-widest bg-black text-white transition-all";
        btnSale.className = "flex-1 py-4 text-[10px] font-black uppercase tracking-widest text-gray-500 hover:text-black transition-all";
    }
    window.updateListingsPriceRanges();
};

// --- 4. HERO SLIDESHOW (PRESERVED) ---
function initSlideshow() {
    const slides = document.querySelectorAll('.slide');
    if (slides.length <= 1) return;

    let currentSlide = 0;
    setInterval(() => {
        slides[currentSlide].classList.replace('opacity-100', 'opacity-0');
        slides[currentSlide].style.zIndex = "0";
        currentSlide = (currentSlide + 1) % slides.length;
        slides[currentSlide].classList.replace('opacity-0', 'opacity-100');
        slides[currentSlide].style.zIndex = "10";
    }, 5000);
}

// --- 5. NEW SWIPER CAROUSEL INIT (FIXED SCOPING) ---
function initSwipers() {
    if (typeof Swiper !== 'undefined') {
        const swiperElements = document.querySelectorAll(".mySwiper");
        
        swiperElements.forEach(el => {
            const isFeatured = el.classList.contains('featured-swiper');
            
            // FIX: Scope the navigation arrows strictly to the current element being looped
            const nextBtn = el.querySelector('.swiper-button-next');
            const prevBtn = el.querySelector('.swiper-button-prev');
            const paginationEl = el.querySelector('.swiper-pagination');
            
            // Specific config for individual listing cards (inner swipers)
            const config = {
                loop: true,
                speed: 800, // Smoother transition
                nested: true, // Prevents conflicts if cards are ever put in a main slider
                observer: true, // Forces Swiper to re-init when it detects changes
                observeParents: true, // Forces Swiper to re-init when container changes
                autoplay: {
                    delay: 3500,
                    disableOnInteraction: false,
                },
                navigation: { 
                    nextEl: nextBtn, // CHANGED: Uses scoped button
                    prevEl: prevBtn  // CHANGED: Uses scoped button
                },
                pagination: {
                    el: paginationEl, // CHANGED: Uses scoped pagination
                    clickable: true,
                }
            };

            if (isFeatured) {
                config.slidesPerView = 1;
                config.spaceBetween = 24;
                config.breakpoints = {
                    640: { slidesPerView: 1 },
                    768: { slidesPerView: 2 },
                    1024: { slidesPerView: 4 }
                };
                config.autoplay = false;
            }

            new Swiper(el, config);
        });

        // Initialize the main Homepage Listings Slider (if present)
        const mainEl = document.querySelector('.homepage-listings-swiper');
        if (mainEl && !mainEl._swiperInstance) {
            try {
                mainEl._swiperInstance = new Swiper(mainEl, {
                    slidesPerView: 1,
                    spaceBetween: 20,
                    loop: true,
                    grabCursor: true,
                    autoplay: { delay: 5000, disableOnInteraction: false },
                    navigation: { nextEl: '.main-next', prevEl: '.main-prev' },
                    pagination: { el: '.swiper-pagination', clickable: true },
                    breakpoints: { 640: { slidesPerView: 2 }, 1024: { slidesPerView: 3 }, 1400: { slidesPerView: 4 } }
                });
            } catch (e) {
                console.warn('Failed to init main listings swiper', e);
            }
        }
    }
}


// --- 6. SCROLL ANIMATIONS (PRESERVED) ---
function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            } else if (entry.boundingClientRect.top > 0) {
                // Only reset if the element leaves the bottom of the viewport
                // This allows for re-animation when scrolling back down
                entry.target.classList.remove('active');
            }
        });
    }, observerOptions);

    // Observe all elements with reveal classes
    document.querySelectorAll('.reveal').forEach(el => scrollObserver.observe(el));
}

// --- 7. INITIALIZE EVERYTHING ---
// Centralized page init that runs on initial load and Turbo navigations
function runPageInit() {
    try {
        initSlideshow();
        initAnimations();
        initSwipers();
    } catch (e) {
        console.warn('Page init error', e);
    }

    // Home Page Init
    if (document.getElementById('home-price-select')) {
        window.setHomeStatus('For Rent');
    }

    // Listings Page Init
    if (document.getElementById('price-select')) {
        window.updateListingsPriceRanges();
    }

    // Loading Spinner
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        filterForm.onsubmit = () => {
            const overlay = document.getElementById('loading-overlay');
            if (overlay) overlay.style.display = 'flex';
        };
    }
}

document.addEventListener('DOMContentLoaded', runPageInit);
document.addEventListener('turbo:load', runPageInit);

// --- 8. NAVIGATION & MOBILE LOGIC (PRESERVED) ---
window.addEventListener('scroll', function() {
    const stickyLinks = document.getElementById('sticky-links');
    if (!stickyLinks) return;
    if (window.scrollY > 80) {
        stickyLinks.classList.add('nav-glass');
        stickyLinks.classList.remove('bg-white', 'border-t', 'border-gray-100');
    } else {
        stickyLinks.classList.remove('nav-glass');
        stickyLinks.classList.add('bg-white', 'border-t', 'border-gray-100');
    }
});

window.toggleMobileMenu = function() {
    const drawer = document.getElementById('mobile-drawer');
    const overlay = document.getElementById('drawer-overlay');
    if (drawer.classList.contains('translate-x-full')) {
        drawer.classList.remove('translate-x-full');
        overlay.classList.remove('hidden');
        setTimeout(() => overlay.classList.add('opacity-100'), 10);
        document.body.style.overflow = 'hidden'; 
    } else {
        drawer.classList.add('translate-x-full');
        overlay.classList.remove('opacity-100');
        setTimeout(() => overlay.classList.add('hidden'), 500);
        document.body.style.overflow = 'auto'; 
    }
};

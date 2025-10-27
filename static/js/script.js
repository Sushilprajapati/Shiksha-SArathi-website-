// Function to initialize the dynamic sliders (Courses and Testimonials)
function initializeSlider(containerId) {
    
    const sliderContainer = document.getElementById(containerId);
    if (!sliderContainer) return;

    const wrapper = sliderContainer.querySelector('.slider-wrapper');
    const prevBtn = sliderContainer.querySelector('.prev-btn');
    const nextBtn = sliderContainer.querySelector('.next-btn');
    const cards = wrapper.querySelectorAll('.card, .testimonial-card');
    
    if (cards.length === 0) return;

    let currentIndex = 0;
    let autoSlideInterval; 

    // Function to calculate how many items fit in the current view
    function getItemsPerView() {
        const width = window.innerWidth;
        if (containerId === 'testimonialSlider') return 1; 
        
        if (width <= 768) return 1; 
        if (width <= 992) return 2; 
        return 3; 
    }

    // ROBUST FUNCTION: Gets the complete width of the first item (including its margin/gap)
    function getItemFullWidth(item) {
        if (containerId === 'testimonialSlider') {
            // Testimonials are simple: 100% of the visible container width
            return sliderContainer.clientWidth - 30; // 30px is for the wrapper padding
        } else {
            // Courses: Use getBoundingClientRect for accurate width + margin calculation
            const itemRect = item.getBoundingClientRect();
            
            // Note: We need to use the CSS margin value here, as rects don't include it well
            const style = window.getComputedStyle(item);
            const gap = parseFloat(style.marginLeft);
            
            // The actual visible width of the card + the margin used for spacing
            return itemRect.width + gap;
        }
    }


    // Function to calculate the new transform position and update buttons
    function updateSliderPosition() {
        const itemsPerView = getItemsPerView();
        const totalItems = cards.length;
        const maxIndex = Math.max(0, totalItems - itemsPerView); 

        currentIndex = Math.min(currentIndex, maxIndex);

        if (totalItems <= itemsPerView) {
             if (prevBtn) prevBtn.disabled = true;
             if (nextBtn) nextBtn.disabled = true;
             wrapper.style.transform = `translateX(0px)`;
             return;
        }

        const itemFullWidth = getItemFullWidth(cards[0]);
        
        // Calculate the translation distance
        const translateDistance = (itemFullWidth * currentIndex);
        
        wrapper.style.transform = `translateX(-${translateDistance}px)`;
        
        if (prevBtn) prevBtn.disabled = currentIndex === 0;
        if (nextBtn) nextBtn.disabled = currentIndex >= maxIndex;
    }

    // --- Auto-Slide Logic ---
    function startAutoSlide() {
        clearInterval(autoSlideInterval);
        
        const itemsPerView = getItemsPerView();
        const totalItems = cards.length;
        const maxIndex = Math.max(0, totalItems - itemsPerView);

        if (totalItems > itemsPerView) {
            autoSlideInterval = setInterval(() => {
                // If at the end, jump back to start (loop)
                if (currentIndex >= maxIndex) {
                    currentIndex = 0;
                } else {
                    // Move to the next slide block
                    currentIndex = Math.min(maxIndex, currentIndex + itemsPerView);
                }
                updateSliderPosition();
            }, 5000); // 5 seconds interval
        }
    }
    
    function stopAutoSlide() {
        clearInterval(autoSlideInterval);
    }
    // --- End Auto-Slide Logic ---


    // Navigation handlers (Manual interaction stops the auto-slide temporarily)
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            stopAutoSlide(); 
            const itemsPerView = getItemsPerView();
            currentIndex = Math.max(0, currentIndex - itemsPerView); 
            updateSliderPosition();
            startAutoSlide();
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            stopAutoSlide(); 
            const itemsPerView = getItemsPerView();
            currentIndex = Math.min(maxIndex, currentIndex + itemsPerView);
            updateSliderPosition();
            startAutoSlide();
        });
    }
    
    // Initial setup
    updateSliderPosition();
    startAutoSlide(); 

    // Recalculate on window resize (Important for responsiveness!)
    let resizeTimeout;
    window.addEventListener('resize', () => {
        stopAutoSlide(); 
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            updateSliderPosition(); 
            startAutoSlide();
        }, 200);
    });
}


// ------------------------------------------------------------------
// YOUR OTHER SCRIPTS (Smooth Scroll, AOS, and Mobile Nav Toggle)

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize ALL Sliders
    initializeSlider('courseSlider');
    initializeSlider('testimonialSlider');

    // 2. Smooth Scroll for Nav Links
    document.querySelectorAll('nav a').forEach(anchor => {
        const href = anchor.getAttribute('href');
        
        if (href && href.startsWith('#')) {  
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(href);
                if(target){
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        }
    });

    // 3. Initialize AOS (Animation on Scroll)
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 1000, 
            once: true,      
        });
    }

    // --- NEWLY ADDED: MOBILE NAVIGATION TOGGLE LOGIC ---
    // (This part fixes the mobile menu visibility issue)
    const menuToggle = document.getElementById('menuToggle'); // Hamburger Button
    const navRight = document.getElementById('navbarNav');    // Links Container

    if (menuToggle && navRight) {
        menuToggle.addEventListener('click', () => {
            // Toggles the 'active-menu' class (which CSS uses to show the menu)
            navRight.classList.toggle('active-menu');
        });
        
        // Optional: Hide the menu when the user clicks any link
        navRight.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                // Hide the menu after clicking a link
                setTimeout(() => {
                    navRight.classList.remove('active-menu');
                }, 300); 
            });
        });
    }
    // --- END MOBILE NAVIGATION TOGGLE LOGIC ---

});


// Optional: Highlight active section on scroll
const sections = document.querySelectorAll('section[id]');
window.addEventListener('scroll', () => {
    let current = '';
    const offset = 80;

    sections.forEach(section => {
        const sectionTop = section.offsetTop - offset;
        if (pageYOffset >= sectionTop) {
            current = section.getAttribute('id');
        }
    });

    document.querySelectorAll('nav a').forEach(link => {
        link.classList.remove('active');
        if(link.getAttribute('href') === `#${current}`){ 
            link.classList.add('active');
        } 
    });
});
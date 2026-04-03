document.addEventListener("DOMContentLoaded", () => {
    const elements = document.querySelectorAll(".fade-right");

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {

                setTimeout(() => {
                    entry.target.classList.add("active");
                }, index * 200);

                observer.unobserve(entry.target); // remove this if you want repeat animation
            }
        });
    }, {
        threshold: 0.3
    });

    elements.forEach(el => observer.observe(el));
});

const toggleButtons = document.querySelectorAll('.toggle-password');

toggleButtons.forEach(button => {
    button.addEventListener('click', () => {
        const target = document.getElementById(button.dataset.target);
        if (target.type === 'password') {
            target.type = 'text';
            button.textContent = 'Hide';
        } else {
            target.type = 'password';
            button.textContent = 'Show';
        }
    });
});

const reveals = document.querySelectorAll('.reveal');

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('active');
        } else {
            entry.target.classList.remove('active'); // 🔥 makes it repeat on scroll
        }
    });
}, {
    threshold: 0.2
});

reveals.forEach(el => observer.observe(el));
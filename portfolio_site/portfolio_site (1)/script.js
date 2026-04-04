window.addEventListener('scroll', () => {
    const scrollTop = window.scrollY;
    const height = document.body.scrollHeight - window.innerHeight;
    const progress = (scrollTop / height) * 100;
    document.getElementById('scroll-progress').style.width = progress + '%';
});

document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('mousemove', e => {
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        btn.style.transform = `translate(${x * 0.1}px, ${y * 0.1}px)`;
    });

    btn.addEventListener('mouseleave', () => {
        btn.style.transform = '';
    });
});

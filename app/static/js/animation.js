document.addEventListener("DOMContentLoaded", () => {
    const container = document.querySelector('.falling-container');
    const circles = document.querySelectorAll('.falling-circle');
    
    console.log('Animation script loaded'); // 확인용 로그

    circles.forEach((circle, index) => {
        setTimeout(() => {
            console.log(`Animating circle ${index}`); // 확인용 로그
            circle.style.left = `${Math.random() * 80 + 10}%`;
            circle.style.animationDelay = `${index * 0.5}s`;
        }, index * 1000);
    });
});

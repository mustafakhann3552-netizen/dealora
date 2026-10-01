document.addEventListener("DOMContentLoaded", function () {

    const heroSlider = document.querySelector("#heroSlider");

    if (heroSlider) {

        new bootstrap.Carousel(heroSlider, {

            interval: 3000,   // 3 seconds
            ride: "carousel",
            pause: "hover",
            wrap: true,
            touch: true

        });

    }

});

function slideBlogs(direction){

    const slider = document.getElementById("blogSlider");

    slider.scrollBy({

        left: direction * 350,

        behavior: "smooth"

    });

}

function changeImage(img){

    document.getElementById("mainImage").src = img.src;

    document.querySelectorAll(".thumb").forEach(function(item){

        item.classList.remove("active");

    });

    img.classList.add("active");

}
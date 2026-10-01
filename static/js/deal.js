/* ==========================================================
   Deal Detail Page
   Professional JavaScript
========================================================== */

document.addEventListener("DOMContentLoaded", function () {

    initImageZoom();

    initCopyLink();

    initSmoothScroll();

    initClaimButton();

    initCardAnimation();

});

/* ==========================================================
   Image Zoom
========================================================== */

function initImageZoom() {

    const image = document.querySelector(".main-deal-image");

    if (!image) return;

    image.addEventListener("mousemove", function (e) {

        const rect = image.getBoundingClientRect();

        const x = ((e.clientX - rect.left) / rect.width) * 100;

        const y = ((e.clientY - rect.top) / rect.height) * 100;

        image.style.transformOrigin = `${x}% ${y}%`;

        image.style.transform = "scale(1.8)";

    });

    image.addEventListener("mouseleave", function () {

        image.style.transform = "scale(1)";

        image.style.transformOrigin = "center";

    });

}

/* ==========================================================
   Copy Current URL
========================================================== */

function initCopyLink() {

   const button = document.querySelector(".copy-link-btn");

    if (!button) return;

    button.addEventListener("click", function () {

        navigator.clipboard.writeText(window.location.href);

        showToast("Link copied successfully.");

    });

}

/* ==========================================================
   Smooth Scroll
========================================================== */

function initSmoothScroll() {

    document.documentElement.style.scrollBehavior = "smooth";

}

/* ==========================================================
   Claim Button
========================================================== */

function initClaimButton() {

    const button = document.querySelector(".claim-btn");

    if (!button) return;

    button.addEventListener("click", function () {

        button.innerHTML = "Redirecting...";

    });

}

/* ==========================================================
   Scroll Animation
========================================================== */

function initCardAnimation() {

    const cards = document.querySelectorAll(

        ".deal-card, .deal-info, .related-card"

    );

    const observer = new IntersectionObserver(function (entries) {

        entries.forEach(function (entry) {

            if (entry.isIntersecting) {

                entry.target.classList.add("show-card");

            }

        });

    }, {

        threshold: 0.15

    });

    cards.forEach(function (card) {

        observer.observe(card);

    });

}

/* ==========================================================
   Toast Message
========================================================== */

function showToast(message) {

    const toast = document.createElement("div");

    toast.className = "deal-toast";

    toast.innerHTML = message;

    document.body.appendChild(toast);

    setTimeout(function () {

        toast.classList.add("show");

    }, 100);

    setTimeout(function () {

        toast.classList.remove("show");

        setTimeout(function () {

            toast.remove();

        }, 300);

    }, 2500);

}

/* ==========================================================
   Thumbnail Gallery
========================================================== */

/* ==========================================================
   Thumbnail Gallery
========================================================== */

function initThumbnailGallery() {

    const mainImage = document.getElementById("mainImage");

    const thumbnails = document.querySelectorAll(".thumb");

    if (!mainImage || thumbnails.length === 0) return;

    thumbnails.forEach(function (thumbnail) {

        thumbnail.addEventListener("click", function () {

            mainImage.src = this.src;

            thumbnails.forEach(function (img) {

                img.classList.remove("active");

            });

            this.classList.add("active");

        });

    });

}

initThumbnailGallery();

/* ==========================================================
   Wishlist Button
========================================================== */

function initWishlist(){

    const button = document.querySelector(".wishlist-btn");

    if(!button) return;

    button.addEventListener("click", function(){

        button.classList.toggle("active");

        if(button.classList.contains("active")){

            button.innerHTML="❤️ Saved";

            showToast("Deal saved successfully.");

        }else{

            button.innerHTML="🤍 Save Deal";

            showToast("Deal removed.");

        }

    });

}

initWishlist();

/* ==========================================================
   Share Buttons
========================================================== */

function initShareButtons(){

    const facebook=document.querySelector(".share-facebook");

    const whatsapp=document.querySelector(".share-whatsapp");

    const twitter=document.querySelector(".share-twitter");

    const url=window.location.href;

    if(facebook){

        facebook.href="https://www.facebook.com/sharer/sharer.php?u="+encodeURIComponent(url);

    }

    if(whatsapp){

        whatsapp.href="https://wa.me/?text="+encodeURIComponent(url);

    }

    if(twitter){

        twitter.href="https://twitter.com/intent/tweet?url="+encodeURIComponent(url);

    }

}

initShareButtons();

/* ==========================================================
   Back To Top
========================================================== */

function createBackToTop(){

    const button=document.createElement("button");

    button.className="back-to-top";

    button.innerHTML="↑";

    document.body.appendChild(button);

    window.addEventListener("scroll",function(){

        if(window.scrollY>400){

            button.classList.add("show");

        }else{

            button.classList.remove("show");

        }

    });

    button.addEventListener("click",function(){

        window.scrollTo({

            top:0,

            behavior:"smooth"

        });

    });

}

createBackToTop();

/* ==========================================================
   Button Loading
========================================================== */

function loadingButtons(){

    const buttons=document.querySelectorAll(".btn");

    buttons.forEach(function(button){

        button.addEventListener("click",function(){

            if(button.classList.contains("claim-btn")) return;

            button.classList.add("clicked");

        });

    });

}

loadingButtons();
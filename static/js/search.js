const searchInput = document.getElementById("searchInput");
const searchResults = document.getElementById("searchResults");

if (searchInput) {

    searchInput.addEventListener("keyup", function () {

        const q = this.value.trim();

   if (q.length < 1) {

    searchResults.style.display = "none";
    searchResults.innerHTML = "";

    // Agar home page par hain to tamam products wapas dikhado
    if (window.location.pathname === "/") {
        window.location.href = "/";
    }

    return;
}

        fetch("/search?q=" + encodeURIComponent(q))
            .then(response => response.json())
            .then(data => {

                searchResults.innerHTML = "";

                if (data.length === 0) {

                    searchResults.innerHTML =
                        '<div class="p-3 text-muted">No products found.</div>';

                    searchResults.style.display = "block";
                    return;
                }

                data.forEach(item => {

                    searchResults.innerHTML += `
                        <a href="/deal/${item.slug}" class="search-item">

                            <img src="/static/uploads/${item.image}" alt="">

                            <div>

                                <div class="search-title">
                                    ${item.title}
                                </div>

                                <div class="search-price">
                                    Rs ${item.price}
                                </div>

                            </div>

                        </a>
                    `;
                });

                searchResults.style.display = "block";

            });

    });

    document.addEventListener("click", function (e) {

        if (!searchResults.contains(e.target) &&
            e.target !== searchInput) {

            searchResults.style.display = "none";
        }

    });

}
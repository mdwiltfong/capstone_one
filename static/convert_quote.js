const quote_form = document.getElementsByTagName("form");
const loader = document.getElementById("loader");
const quote_container = document.getElementById("quote_container");
quote_form[0].addEventListener("submit", (e) => {
  quote_container.className = "container visually-hidden";
  loader.className = "d-flex justify-content-center align-items-center";
  setTimeout(() => {
    window.location.href = "/";
  }, 10000);
});

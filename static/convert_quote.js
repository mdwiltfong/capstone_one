document.addEventListener("DOMContentLoaded", () => {
  student_name = document.getElementById("student_name");
  student_email = document.getElementById("student_email");
  form = document.querySelector("form");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    console.log(e);
    fetchQuote(e.target[2].value, e.target[1].value)
      .then((resp) => {
        console.log(resp);
      })
      .then(renderQuote());
    console.log("submit");
  });
});

async function fetchQuote(email, name) {
  resp = await fetch("/quotes", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      student_email: email,
      student_name: name,
    }),
  });
  return resp.json();
}

function renderQuote(quote) {}

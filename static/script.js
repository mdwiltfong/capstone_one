let stripe = Stripe(
  "pk_test_51KMM12DBo40mpW7dSao4A4hiqc7G349eWgYu5racVc0xhtUJColbp4U7LJd8WqBx4fdEdxbbQTEmZruFB40oCso300XBtrIET5"
);
let client_secret, elements, cardElement;

async function getClientSecret() {
  const resp = await fetch("/create-payment-intent", {
    method: "GET",
  });
  const { client_secret } = await resp.json();
  return client_secret;
}

getClientSecret().then((resp) => {
  console.log(resp);
  const appearance = {
    theme: "flat",
  };
  client_secret = resp;
  elements = stripe.elements({ client_secret, appearance });
  cardElement = elements.create("card");
  cardElement.mount("#payment-element");
});
console.log(client_secret);
// helper method for displaying a status message.
const setMessage = (message) => {
  const messageDiv = document.querySelector("#messages");
  messageDiv.innerHTML += "<br>" + message;
};

const form = document.querySelector("#payment-form");
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const nameInput = document.getElementById("name");
  const emailInput = document.getElementById("email");
  const phoneInput = document.getElementById("phone");
  const addressInput = document.getElementById("address");
  const cityInput = document.getElementById("city");
  const stateInput = document.getElementById("state");
  const zipInput = document.getElementById("zip");
  // Create payment method and confirm payment intent.
  stripe
    .confirmCardPayment(client_secret, {
      payment_method: {
        card: cardElement,
        billing_details: {
          name: nameInput.value,
          email: emailInput.value,
          address: {
            city: cityInput.value,
            line1: addressInput.value,
            postal_code: zipInput.value,
            state: stateInput.value,
          },
          phone: phoneInput.value,
        },
      },
    })
    .then((result) => {
      if (result.error) {
        setMessage(`Payment failed: ${result.error.message}`);
      } else {
        // Redirect the customer to their account page
        console.log("--->", result);
        setMessage("Success! Redirecting to your account.");
        window.location.href = "/teacher/plan/prices/success";
      }
    });
});

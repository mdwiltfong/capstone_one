// Set your publishable key: remember to change this to your live publishable key in production
// See your keys here: https://dashboard.stripe.com/apikeys
import config from "./config";

let stripe = Stripe(config.PUBLISHABLE_API_KEY);
let elements = stripe.elements();
let card = elements.create("card", { style: style });
card.mount("#card-element");
card.on("change", function (event) {
  displayError(event);
});
function displayError(event) {
  changeLoadingStatePrices(false);
  let displayError = document.getElementById("card-element-errors");
  if (event.error) {
    displayError.textContent = event.error.message;
  } else {
    displayError.textContent = "";
  }
}
const btn = document.querySelector("#submit-payment-btn");
btn.addEventListener("click", async (e) => {
  e.preventDefault();
  const nameInput = document.getElementById("name");

  // Create payment method and confirm payment intent.
  stripe
    .confirmCardPayment(clientSecret, {
      payment_method: {
        card: cardElement,
        billing_details: {
          name: nameInput.value,
        },
      },
    })
    .then((result) => {
      if (result.error) {
        alert(result.error.message);
      } else {
        // Successful subscription payment
      }
    });
});

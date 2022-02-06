// Set your publishable key: remember to change this to your live publishable key in production
// See your keys here: https://dashboard.stripe.com/apikeys

// helper method for displaying a status message.
const setMessage = (message) => {
  const messageDiv = document.querySelector("#messages");
  messageDiv.innerHTML += "<br>" + message;
};

// Fetch public key and initialize Stripe.
let stripe = Stripe(
  "pk_test_51KMM12DBo40mpW7dSao4A4hiqc7G349eWgYu5racVc0xhtUJColbp4U7LJd8WqBx4fdEdxbbQTEmZruFB40oCso300XBtrIET5"
);

const subscriptionId = window.sessionStorage.getItem("subscriptionId");
const client_string = window.sessionStorage.getItem("clientSecret");

const appearance = {
  theme: "flat",
};

const elements = stripe.elements({ client_string, appearance });

let cardElement = elements.create("card");

cardElement.mount("#card-input");

// Extract the client secret query string argument. This is
// required to confirm the payment intent from the front-end.
// This sample only supports a Subscription with payment
// upfront. If you offer a trial on your subscription, then
// instead of confirming the subscription's latest_invoice's
// payment_intent. You'll use stripe.confirmCardSetup to confirm
// the subscription's pending_setup_intent.
// See https://stripe.com/docs/billing/subscriptions/trials

// Payment info collection and confirmation
// When the submit button is pressed, attempt to confirm the payment intent
// with the information input into the card element form.
// - handle payment errors by displaying an alert. The customer can update
//   the payment information and try again
// - Stripe Elements automatically handles next actions like 3DSecure that are required for SCA
// - Complete the subscription flow when the payment succeeds
const form = document.querySelector("#subscribe-form");
form.addEventListener("submit", async (e) => {
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
        setMessage(`Payment failed: ${result.error.message}`);
      } else {
        // Redirect the customer to their account page
        setMessage("Success! Redirecting to your account.");
        window.location.href = "/account.html";
      }
    });
});

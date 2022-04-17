let stripe, clientSecret, elements, cardElement;
window.addEventListener("DOMContentLoaded", () => {
  getConfig().then(() => {
    const appearance = {
      theme: "stripe",
      variables: {
        colorText: "#cdd0f8",
      },
    };

    elements = stripe.elements({ clientSecret, appearance });
    cardElement = elements.create("payment", appearance);
    cardElement.mount("#payment-element");
  });
});

async function getConfig() {
  const details = await fetch("/config");
  const { account_id, client_secret } = await details.json();
  stripe = Stripe(
    "pk_test_51KMM12DBo40mpW7dSao4A4hiqc7G349eWgYu5racVc0xhtUJColbp4U7LJd8WqBx4fdEdxbbQTEmZruFB40oCso300XBtrIET5",
    { stripeAccount: account_id }
  );
  clientSecret = client_secret;
}

// helper method for displaying a status message.
const setMessage = (message) => {
  const messageDiv = document.querySelector("#messages");
  if (message.error) {
    messageDiv.className += " w-25 alert alert-danger";
    messageDiv.innerHTML += message.error.message;
  } else {
    messageDiv.className = "w-25 alert alert-success";
    messageDiv.innerHTML += message;
  }
};
const form = document.querySelector("#payment-form");
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  // Create payment method and confirm payment intent.
  stripe
    .confirmSetup({
      elements,
      confirmParams: {
        return_url: "/checkout_successful",
      },
    })
    .then((result) => {
      if (result.error) {
        setMessage(result);
      } else {
        // Redirect the customer to their account page
        console.log("--->", result);
        setMessage("Success! Redirecting to your account.");
      }
    });
});

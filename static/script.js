let stripe, clientSecret, elements, cardElement;

window.addEventListener("DOMContentLoaded", () => {
  getConfig().then(() => {
    const appearance = {
      iconStyle: "solid",
      style: {
        base: {
          iconColor: "#fff",
          color: "#fff",
          fontWeight: 400,
          fontFamily: "Helvetica Neue, Helvetica, Arial, sans-serif",
          fontSize: "16px",
          fontSmoothing: "antialiased",

          "::placeholder": {
            color: "#BFAEF6",
          },
          ":-webkit-autofill": {
            color: "#fce883",
          },
        },
        invalid: {
          iconColor: "#FFC7EE",
          color: "#FFC7EE",
        },
      },
    };

    elements = stripe.elements({ clientSecret, appearance });
    cardElement = elements.create("card");
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
    .confirmCardPayment(clientSecret, {
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
      setup_future_usage: "off_session",
    })
    .then((result) => {
      if (result.error) {
        setMessage(`Payment failed: ${result.error.message}`);
      } else {
        // Redirect the customer to their account page
        console.log("--->", result);
        setMessage("Success! Redirecting to your account.");
        window.location.href = "/checkout_successful";
      }
    });
});

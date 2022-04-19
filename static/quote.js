/* Only use NodeJs implementation for testing */
const Dinero = require("dinero.js");
class lineItem {
  constructor({ price, quantity = 1, salesTax }) {
    (this.price = price),
      (this.quantity = quantity),
      (this.salesTax = salesTax);
  }
  get details() {
    return {
      price: this.price,
      quantity: this.quantity,
      taxed: this.salesTax,
    };
  }
}

class Quote {
  constructor(lineItems, discount) {
    this.lineItems = lineItems;
    this.discount = discount;
    this.subTotal;
  }
  /* Converts line items into dinero objects in which the dinero object amount is the line item total without sales tax or discount  */
  get dineroLineItems() {
    return this.lineItems.map((lineItem) => {
      return Dinero({
        amount: lineItem.price * lineItem.quantity * 100,
        currency: "USD",
      });
    });
  }

  get dineroSubTotal() {
    return (this.subTotal = this.dineroLineItems.reduce(
      (preValue, currValue) => {
        return preValue.add(currValue);
      }
    ));
  }
  get dineroSubTotalDiscounted() {
    if (this.discount.percentage == false) {
      return this.dineroLineItems.map(() => {});
    }
  }
}

//export { lineItem, Quote };
// use module.exports only to test this module
module.exports = { lineItem, Quote };

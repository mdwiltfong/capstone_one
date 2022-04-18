class lineItem {
  constructor({ price, quantity, salesTax }) {
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
  constructor(...lineItems) {
    this.lineItems = lineItems;
  }
  numberToDinero() {
    return this.lineItems.map((lineItem) => {
      return Dinero({ amount: lineItem.price, currency: "USD" });
    });
  }
}

//export { lineItem, Quote };
// use module.exports only to test this module
module.exports = { lineItem, Quote };

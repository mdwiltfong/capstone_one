const { lineItem, Quote } = require("./quote");
const Dinero = require("dinero.js");
describe("lineItem", () => {
  test("LineItem Test", () => {
    const line_item = new lineItem({ price: 50, quantity: 1, salesTax: true });

    expect(line_item).toBeDefined();
  });
  test("LineItem.details", () => {
    const line_item = new lineItem({
      price: 50,
      quantity: 1,
      salesTax: true,
    });

    expect(line_item.details).toEqual(
      expect.objectContaining({
        price: expect.any(Number),
        quantity: expect.any(Number),
        taxed: expect.any(Boolean),
      })
    );
  });
});

describe("Quote", () => {
  let lineItemArray = [];
  let quote;
  let dineroArray = [];
  beforeEach(() => {
    lineItemArray.push(
      new lineItem({ price: 50.85, quantity: 2, salesTax: true })
    );
    lineItemArray.push(
      new lineItem({ price: 50.85, quantity: 2, salesTax: true })
    );
    quote = new Quote(
      lineItemArray,
      (discount = { percentage: false, amount: 1.0 })
    );
    dineroArray = quote.dineroLineItems;
  });
  afterEach(() => {
    lineItemArray.length = 0;
  });

  test("Create Quote", () => {
    expect(quote).toBeDefined();
  });
  test("Quote.numberToDinero creates arrays of Dineros", () => {
    expect(dineroArray.length).toEqual(lineItemArray.length);
  });
  test("dineroArray has an amount with cents", () => {
    expect(dineroArray[0].getAmount()).toEqual(10170);
    expect(dineroArray[0].hasCents()).toEqual(true);
  });
  test("quote has a subtotal dinero", () => {
    expect(quote.dineroSubTotal.getAmount()).toEqual(10170 * 2);
  });
});

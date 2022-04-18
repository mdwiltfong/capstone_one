const { lineItem, Quote } = require("./quote");
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
  beforeEach(() => {
    lineItemArray.puch(
      new lineItem({ price: 50, quantity: 2, salesTax: true })
    );
  });
});

const products = ["T-shirt", "Cap", "Shoes"];
const container = document.getElementById("products");
products.forEach(p => {
  const div = document.createElement("div");
  div.innerText = p;
  container.appendChild(div);
});

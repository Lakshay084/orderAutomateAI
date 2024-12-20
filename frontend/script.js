async function saveRequirements(product) {
    const requirements = {};

    if (product === "Wheat") {
        requirements.max_price = parseFloat(document.getElementById("wheat-price").value);
        requirements.min_rating = parseFloat(document.getElementById("wheat-rating").value);
        requirements.required_quantity = parseInt(document.getElementById("wheat-quantity").value);
    } else if (product === "Mustard Seed") {
        requirements.max_price = parseFloat(document.getElementById("mustard-price").value);
        requirements.min_rating = parseFloat(document.getElementById("mustard-rating").value);
        requirements.required_quantity = parseInt(document.getElementById("mustard-quantity").value);
    } else if (product === "Soybean") {
        requirements.max_price = parseFloat(document.getElementById("soybean-price").value);
        requirements.min_rating = parseFloat(document.getElementById("soybean-rating").value);
        requirements.required_quantity = parseInt(document.getElementById("soybean-quantity").value);
    }

    try {
        const response = await fetch(`http://127.0.0.1:5000/set-requirements/${product}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(requirements),
        });

        const result = await response.json();
        alert(result.message || `${product} requirements saved successfully!`);
    } catch (error) {
        console.error(`Error saving requirements for ${product}:`, error);
    }
}

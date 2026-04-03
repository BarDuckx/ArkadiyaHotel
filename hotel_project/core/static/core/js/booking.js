document.addEventListener("DOMContentLoaded", function () {

    const checkIn = document.getElementById("id_check_in");
    const checkOut = document.getElementById("id_check_out");
    const guests = document.getElementById("id_guests");
    const nightsField = document.getElementById("nights");
    const totalField = document.getElementById("total");

    if (!checkIn || !checkOut || !guests) return;

    const pricePerNight = parseFloat(
        document.getElementById("price-per-night").value
    );

    function calculate() {
        if (checkIn.value && checkOut.value) {

            const start = new Date(checkIn.value);
            const end = new Date(checkOut.value);

            const diffTime = end - start;
            const nights = diffTime / (1000 * 60 * 60 * 24);

            if (nights > 0) {

                const guestsCount = parseInt(guests.value) || 1;

                nightsField.textContent = nights;
                totalField.textContent = nights * pricePerNight * guestsCount;

            } else {
                nightsField.textContent = 0;
                totalField.textContent = 0;
            }
        }
    }

    checkIn.addEventListener("change", calculate);
    checkOut.addEventListener("change", calculate);
    guests.addEventListener("change", calculate);
});

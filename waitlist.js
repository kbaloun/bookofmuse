/* Book of Muse — waitlist form handler.
 * Posts to a Google Apps Script web app running in the author's own
 * Google account; each signup is appended to the private "Book of Muse —
 * waitlist" sheet and a notification is emailed to the author.
 * The waitlist is interest-only: no payment, no copies, no dates.
 * WAITLIST_ENDPOINT is filled in when the script is deployed.
 */
const WAITLIST_ENDPOINT = "https://script.google.com/macros/s/AKfycbxR6l4jBRQ-dd1tGn-HIkRLOLV1ZiqBhLpPmfdCIQiBvwtycHS1MApSOVJvfN_YI5Ag4A/exec";

document.getElementById("waitlist-form").addEventListener("submit", async function (ev) {
  ev.preventDefault();
  const status = document.getElementById("waitlist-status");
  const form = ev.target;
  const email = form.email.value.trim();

  if (!email || !form.checkValidity()) {
    status.textContent = "Please enter a valid email address.";
    form.reportValidity();
    return;
  }
  if (form.botcheck.checked) return; // honeypot

  status.textContent = "Joining…";
  try {
    const res = await fetch(WAITLIST_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        email: email,
        name: form.name.value.trim(),
      }),
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error || "submit failed");
    status.textContent =
      "You're on the list — thank you. We'll write when there's news about the book.";
    form.reset();
  } catch (err) {
    status.textContent =
      "That didn't go through — please try again in a moment. Nothing was recorded.";
  }
});

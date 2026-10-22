/* Book of Muse — submissions form handler.
 *
 * DEPLOYMENT: set SUBMIT_ENDPOINT to the live submissions endpoint
 * (see DEPLOY.md — recommended: a serverless function that stores the
 * submission in a private review queue / sends it to the review inbox).
 * The endpoint must accept a JSON POST and return 2xx on success.
 * Submissions are NEVER published by this code — they go to a review
 * queue only, per the site's vetting rule.
 */
const SUBMIT_ENDPOINT = ""; // <-- CONFIGURE AT DEPLOY TIME, e.g. "https://bookofmuse.com/api/submit"

document.getElementById("submit-form").addEventListener("submit", async function (ev) {
  ev.preventDefault();
  const status = document.getElementById("form-status");
  const form = ev.target;

  if (!form.checkValidity()) {
    status.textContent = "Please complete the required fields, including the permission checkbox.";
    form.reportValidity();
    return;
  }

  const data = {
    type: form.type.value,
    name: form.name.value.trim(),
    email: form.email.value.trim(),
    title: form.title.value.trim(),
    description: form.description.value.trim(),
    proof: form.proof.value.trim(),
    permission: form.permission.checked,
    submitted_from: "bookofmuse.com/submit",
  };

  if (!SUBMIT_ENDPOINT) {
    // No backend configured yet: say so honestly rather than pretending it sent.
    status.textContent =
      "Submissions open when the site launches — the review inbox isn't connected yet. " +
      "Please check back soon; we'd love to read this.";
    return;
  }

  status.textContent = "Sending for review…";
  try {
    const res = await fetch(SUBMIT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("HTTP " + res.status);
    status.textContent =
      "Thank you — received for review. Nothing is published automatically; " +
      "we'll be in touch at the email you gave us if we'd like to feature it.";
    form.reset();
  } catch (err) {
    status.textContent =
      "That didn't go through — please try again in a moment. Nothing was recorded.";
  }
});

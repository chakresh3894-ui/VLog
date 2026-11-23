document.addEventListener("DOMContentLoaded", () => {
  const eyeOpen = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></svg>';
  const eyeClosed = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 3l18 18M10.6 10.7a2 2 0 002.7 2.7M9.9 5.3A11 11 0 0112 5c6.5 0 10 7 10 7a16 16 0 01-2.1 3.1M6.5 6.5C3.5 8.5 2 12 2 12s3.5 7 10 7c1.5 0 2.8-.3 4-.8"/></svg>';

  document.querySelectorAll('input[type="password"]').forEach((input) => {
    const wrapper = document.createElement("div");
    wrapper.className = "password-wrapper";
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    const button = document.createElement("button");
    button.type = "button";
    button.className = "password-toggle";
    button.setAttribute("aria-label", "Show password");
    button.setAttribute("aria-pressed", "false");
    button.innerHTML = eyeOpen;
    wrapper.appendChild(button);

    button.addEventListener("click", () => {
      const show = input.type === "password";
      input.type = show ? "text" : "password";
      button.setAttribute("aria-label", show ? "Hide password" : "Show password");
      button.setAttribute("aria-pressed", show ? "true" : "false");
      button.innerHTML = show ? eyeClosed : eyeOpen;
      input.focus();
    });
  });

  const primary = document.querySelector("#id_password1, #id_new_password1");
  if (!primary) return;

  const rules = [
    ["At least 8 characters", (value) => value.length >= 8],
    ["One uppercase letter", (value) => /[A-Z]/.test(value)],
    ["One lowercase letter", (value) => /[a-z]/.test(value)],
    ["One number", (value) => /\d/.test(value)],
    ["One special character", (value) => /[^A-Za-z0-9\s]/.test(value)],
  ];

  const checklist = document.createElement("ul");
  checklist.className = "password-checklist";
  checklist.setAttribute("aria-label", "Password requirements");

  rules.forEach(([label]) => {
    const item = document.createElement("li");
    item.textContent = label;
    checklist.appendChild(item);
  });

  primary.closest(".field").appendChild(checklist);

  const confirmation = document.querySelector("#id_password2, #id_new_password2");
  const matchMessage = confirmation ? document.createElement("span") : null;
  if (matchMessage) {
    matchMessage.className = "password-match";
    confirmation.closest(".field").appendChild(matchMessage);
  }

  const update = () => {
    const value = primary.value;
    [...checklist.children].forEach((item, index) => {
      const met = rules[index][1](value);
      item.classList.toggle("met", met);
      item.classList.toggle("unmet", !met && value.length > 0);
    });

    if (matchMessage) {
      const matches = confirmation.value.length > 0 && confirmation.value === value;
      matchMessage.textContent = confirmation.value
        ? (matches ? "Passwords match." : "Passwords do not match.")
        : "";
      matchMessage.className = "password-match " + (confirmation.value ? (matches ? "met" : "unmet") : "");
    }
  };

  primary.addEventListener("input", update);
  if (confirmation) confirmation.addEventListener("input", update);
  update();
});
